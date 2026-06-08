import sys
import json
import traceback
import math
from backend.database.db_manager import DatabaseManager
from backend.blast_engine.services.blast_calculator import BlastCalculatorService
from backend.blast_engine.core.unit_converter import convert
from backend.assessment.damage_engine import DamageEngine
from backend.validation.scenario_validator import validate_scenario_params, ValidationError
from backend.studies.sweep_engine import SweepEngine
from backend.studies.material_ranker import MaterialRanker
from backend.studies.batch_runner import BatchRunner, export_sweep_to_csv

class StdioServer:
    def __init__(self):
        # Database initialized with force_rebuild=True during dev restart
        self.db = DatabaseManager(force_rebuild=False)

    def run(self):
        """Event loop reading JSON messages from stdin and replying on stdout."""
        sys.stderr.write("BLASTSCOPE_PYTHON_BACKEND_READY\n")
        sys.stderr.flush()

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break # EOF
                
                request = json.loads(line.strip())
                req_id = request.get("id")
                channel = request.get("channel")
                payload = request.get("payload", {})
                
                response_payload = self.route(channel, payload)
                
                response = {
                    "id": req_id,
                    "success": True,
                    "response": response_payload
                }
                
            except json.JSONDecodeError:
                response = {
                    "success": False,
                    "error": "Invalid JSON format"
                }
            except ValidationError as e:
                response = {
                    "id": req_id if 'req_id' in locals() else None,
                    "success": False,
                    "error": str(e),
                    "type": "ValidationError"
                }
            except Exception as e:
                response = {
                    "id": req_id if 'req_id' in locals() else None,
                    "success": False,
                    "error": f"Internal Error: {str(e)}",
                    "traceback": traceback.format_exc()
                }
                
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
    def _fetch_study_data(self, conn, explosive_id: int, profile_ids: list) -> tuple:
        """
        Shared helper: fetch explosive dict and enriched profiles_data list (with curves)
        needed by all studies IPC channels.

        Returns:
            (explosive: dict, profiles_data: list)
        """
        cursor = conn.cursor()

        # Fetch explosive
        cursor.execute("SELECT * FROM explosives WHERE id = ?", (explosive_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Explosive id={explosive_id} not found")
        explosive = dict(row)

        # Fetch profiles + thresholds + curves
        profiles_data = []
        for pid in profile_ids:
            cursor.execute("""
                SELECT mp.*, mp.name AS profile_name
                FROM material_profiles mp
                WHERE mp.id = ?
            """, (pid,))
            prof_row = cursor.fetchone()
            if not prof_row:
                continue
            prof = dict(prof_row)

            # Load response curves for this profile
            cursor.execute("""
                SELECT damage_state, curve_type, pressure_asymptote,
                       impulse_asymptote, curve_constant, equation_text,
                       source_reference, confidence_level
                FROM material_response_curves
                WHERE profile_id = ?
            """, (pid,))
            prof["curves"] = [dict(r) for r in cursor.fetchall()]
            profiles_data.append(prof)

        return explosive, profiles_data

    def route(self, channel: str, payload: dict):
        """Routes the Electron IPC channel to database queries or calculations."""
        conn = self.db.get_connection()
        try:
            if channel == "scenarios:list":
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.*, e.name as explosive_name, e.pressure_equivalency, 
                           e.impulse_equivalency, e.general_equivalency 
                    FROM scenarios s
                    JOIN explosives e ON s.explosive_id = e.id
                    ORDER BY s.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "scenarios:save":
                cursor = conn.cursor()
                weight = float(payload.get("chargeWeight", 0))
                distance = float(payload.get("distance", 0))
                burst_type = payload.get("burstType", "Free Air")
                validate_scenario_params(weight, distance, burst_type)

                with conn:
                    # Save scenario parameters
                    cursor.execute("""
                        INSERT OR REPLACE INTO scenarios 
                        (id, name, explosive_id, charge_weight, distance, burst_type, unit_system) 
                        VALUES (:id, :name, :explosiveId, :chargeWeight, :distance, :burstType, :unitSystem)
                    """, {
                        "id": payload.get("id"),
                        "name": payload.get("name"),
                        "explosiveId": payload.get("explosiveId"),
                        "chargeWeight": weight,
                        "distance": distance,
                        "burstType": burst_type,
                        "unitSystem": payload.get("unitSystem", "Metric")
                    })
                    scenario_id = cursor.lastrowid if payload.get("id") is None else payload.get("id")
                    
                    # Fetch explosive equivalency factors
                    cursor.execute("""
                        SELECT pressure_equivalency, impulse_equivalency, general_equivalency 
                        FROM explosives WHERE id = ?
                    """, (payload.get("explosiveId"),))
                    exp_factors = cursor.fetchone()

                    # Perform environmental calculation using dual pressure-impulse factors
                    calc_res = BlastCalculatorService.calculate_environment(
                        charge_weight=weight,
                        distance=distance,
                        burst_type=burst_type,
                        pressure_factor=exp_factors["pressure_equivalency"],
                        impulse_factor=exp_factors["impulse_equivalency"],
                        general_factor=exp_factors["general_equivalency"]
                    )

                    # Save calculations to results cache table
                    cursor.execute("SELECT id FROM model_versions WHERE model_name = ?", (calc_res["model_used"],))
                    mv_row = cursor.fetchone()
                    mv_id = mv_row["id"] if mv_row else None

                    cursor.execute("""
                        INSERT OR REPLACE INTO scenario_results 
                        (scenario_id, model_version_id, scaled_distance, incident_pressure, 
                         reflected_pressure, dynamic_pressure, positive_impulse, positive_duration, 
                         negative_duration, arrival_time) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        scenario_id,
                        mv_id,
                        calc_res["scaled_distance"],
                        calc_res["incident_pressure"],
                        calc_res["reflected_pressure"],
                        calc_res["dynamic_pressure"],
                        calc_res["positive_impulse"],
                        calc_res["positive_duration"],
                        calc_res["negative_duration"],
                        calc_res["arrival_time"]
                    ))
                    result_id = cursor.lastrowid

                    # Fetch curves
                    cursor.execute("SELECT * FROM material_response_curves")
                    curves_rows = [dict(row) for row in cursor.fetchall()]
                    curves_by_profile = {}
                    for c_row in curves_rows:
                        pid = c_row["profile_id"]
                        if pid not in curves_by_profile:
                            curves_by_profile[pid] = []
                        curves_by_profile[pid].append(c_row)

                    # Batch assess all materials and store assessments
                    cursor.execute("""
                        SELECT mp.*, t.minor_pressure, t.minor_impulse, t.moderate_pressure, t.moderate_impulse,
                               t.severe_pressure, t.severe_impulse, t.failure_pressure, t.failure_impulse, m.family
                        FROM material_profiles mp
                        JOIN materials m ON mp.material_id = m.id
                        LEFT JOIN thresholds t ON mp.id = t.profile_id
                    """)
                    profiles = []
                    for row in cursor.fetchall():
                        d_row = dict(row)
                        d_row["curves"] = curves_by_profile.get(d_row["id"], [])
                        profiles.append(d_row)
                    assessments = DamageEngine.assess_batch(calc_res, profiles)

                    for assess in assessments:
                        cursor.execute("""
                            INSERT OR REPLACE INTO material_assessments
                            (scenario_result_id, profile_id, damage_level, damage_state, severity_score, 
                             pressure_ratio, impulse_ratio, damage_index, controlling_mode, damage_mechanism, 
                             assessment_reason, confidence_level, source_reference, response_model_version)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            result_id,
                            assess["profile_id"],
                            assess["damage_level"],
                            assess["damage_state"],
                            assess["severity_score"],
                            assess["pressure_ratio"],
                            assess["impulse_ratio"],
                            assess["damage_index"],
                            assess["controlling_mode"],
                            assess["damage_mechanism"],
                            assess["assessment_reason"],
                            assess["confidence_level"],
                            assess["source_reference"],
                            assess["response_model_version"]
                        ))

                return {"scenarioId": scenario_id, "resultId": result_id, "assessments": assessments}

            elif channel == "validation:runSweep":
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM validation_cases")
                cases = [dict(row) for row in cursor.fetchall()]
                
                with conn:
                    for case in cases:
                        # Perform calculation using Kingery-Bulmash (Swisdak 1994)
                        # Reference is TNT (equivalence = 1.0)
                        calc = BlastCalculatorService.calculate_environment(
                            charge_weight=case["charge_weight"],
                            distance=case["distance"],
                            burst_type=case["burst_type"],
                            pressure_factor=1.0,
                            impulse_factor=1.0,
                            general_factor=1.0,
                            model="Kingery-Bulmash"
                        )
                        
                        p_calc = calc["incident_pressure"]
                        i_calc = calc["positive_impulse"]
                        
                        p_abs = abs(p_calc - case["reference_pressure"])
                        p_rel = (p_abs / case["reference_pressure"]) * 100.0
                        
                        i_abs = abs(i_calc - case["reference_impulse"])
                        i_rel = (i_abs / case["reference_impulse"]) * 100.0
                        
                        cursor.execute("""
                            UPDATE validation_cases
                            SET calculated_pressure = ?, calculated_impulse = ?,
                                pressure_abs_error = ?, pressure_rel_error = ?,
                                impulse_abs_error = ?, impulse_rel_error = ?
                            WHERE id = ?
                        """, (p_calc, i_calc, p_abs, p_rel, i_abs, i_rel, case["id"]))
                
                cursor.execute("SELECT * FROM validation_cases")
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "validation:getSummary":
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM validation_cases WHERE pressure_rel_error IS NOT NULL")
                rows = [dict(row) for row in cursor.fetchall()]
                
                # Group by ground_truth_class
                by_class = {}
                for r in rows:
                    gtc = r["ground_truth_class"]
                    if gtc not in by_class:
                        by_class[gtc] = []
                    by_class[gtc].append(r)
                
                def compute_metrics(group_name, cases):
                    errs_p = [c["pressure_rel_error"] for c in cases if c["pressure_rel_error"] is not None]
                    errs_i = [c["impulse_rel_error"] for c in cases if c["impulse_rel_error"] is not None]
                    
                    if not errs_p:
                        return None
                        
                    avg_p = sum(errs_p) / len(errs_p)
                    max_p = max(errs_p)
                    rmse_p = math.sqrt(sum(x**2 for x in errs_p) / len(errs_p))
                    sorted_p = sorted(errs_p)
                    p95_p = sorted_p[min(len(sorted_p) - 1, max(0, int(math.ceil(0.95 * len(sorted_p)) - 1)))]
                    
                    avg_i = sum(errs_i) / len(errs_i)
                    max_i = max(errs_i)
                    rmse_i = math.sqrt(sum(x**2 for x in errs_i) / len(errs_i))
                    sorted_i = sorted(errs_i)
                    p95_i = sorted_i[min(len(sorted_i) - 1, max(0, int(math.ceil(0.95 * len(sorted_i)) - 1)))]
                    
                    return {
                        "ground_truth_class": group_name,
                        "total_cases": len(cases),
                        "avg_pressure_error": avg_p,
                        "rmse_pressure_error": rmse_p,
                        "max_pressure_error": max_p,
                        "p95_pressure_error": p95_p,
                        "avg_impulse_error": avg_i,
                        "rmse_impulse_error": rmse_i,
                        "max_impulse_error": max_i,
                        "p95_impulse_error": p95_i
                    }
                
                summary = []
                for gtc, cases in by_class.items():
                    metrics = compute_metrics(gtc, cases)
                    if metrics:
                        summary.append(metrics)
                        
                # Overall total
                if rows:
                    overall = compute_metrics("OVERALL TOTAL", rows)
                    if overall:
                        summary.append(overall)
                
                return summary


            elif channel == "scenarios:saveNote":
                cursor = conn.cursor()
                with conn:
                    cursor.execute("""
                        INSERT INTO notes (scenario_id, note) VALUES (?, ?)
                    """, (payload.get("scenarioId"), payload.get("note")))
                return {"id": cursor.lastrowid, "scenarioId": payload.get("scenarioId"), "note": payload.get("note")}

            elif channel == "scenarios:listNotes":
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE scenario_id = ? ORDER BY created_at DESC", (payload.get("scenarioId"),))
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "explosives:list":
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM explosives")
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "materials:listProfiles":
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mp.*, m.family, 
                           t.minor_pressure, t.minor_impulse, 
                           t.moderate_pressure, t.moderate_impulse, 
                           t.severe_pressure, t.severe_impulse, 
                           t.failure_pressure, t.failure_impulse,
                           s.title as source_title, s.year as source_year, t.confidence_level,
                           t.failure_description, t.threshold_source_type, t.applicability_notes
                    FROM material_profiles mp
                    JOIN materials m ON mp.material_id = m.id
                    LEFT JOIN thresholds t ON mp.id = t.profile_id
                    LEFT JOIN sources s ON t.source_id = s.id
                """)
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "blast:calculateEnvironment":
                weight = float(payload.get("chargeWeight", 0))
                distance = float(payload.get("distance", 0))
                burst_type = payload.get("burstType", "Free Air")
                model = payload.get("model", "Kingery-Bulmash")
                
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT pressure_equivalency, impulse_equivalency, general_equivalency 
                    FROM explosives WHERE id = ?
                """, (payload.get("explosiveId"),))
                row = cursor.fetchone()
                
                press_f = row["pressure_equivalency"] if row else 1.0
                imp_f = row["impulse_equivalency"] if row else 1.0
                gen_f = row["general_equivalency"] if row else 1.0

                calc_res = BlastCalculatorService.calculate_environment(
                    charge_weight=weight,
                    distance=distance,
                    burst_type=burst_type,
                    pressure_factor=press_f,
                    impulse_factor=imp_f,
                    general_factor=gen_f,
                    model=model
                )
                return calc_res

            elif channel == "material:assessBatch":
                results = payload.get("results")
                profile_ids = payload.get("profileIds", [])
                
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM material_response_curves")
                curves_rows = [dict(row) for row in cursor.fetchall()]
                curves_by_profile = {}
                for c_row in curves_rows:
                    pid = c_row["profile_id"]
                    if pid not in curves_by_profile:
                        curves_by_profile[pid] = []
                    curves_by_profile[pid].append(c_row)

                if profile_ids:
                    placeholders = ",".join("?" for _ in profile_ids)
                    cursor.execute(f"""
                        SELECT mp.*, t.minor_pressure, t.minor_impulse, t.moderate_pressure, t.moderate_impulse,
                               t.severe_pressure, t.severe_impulse, t.failure_pressure, t.failure_impulse, m.family,
                               t.failure_description, t.threshold_source_type, t.applicability_notes
                        FROM material_profiles mp
                        JOIN materials m ON mp.material_id = m.id
                        LEFT JOIN thresholds t ON mp.id = t.profile_id
                        WHERE mp.id IN ({placeholders})
                    """, profile_ids)
                else:
                    cursor.execute("""
                        SELECT mp.*, t.minor_pressure, t.minor_impulse, t.moderate_pressure, t.moderate_impulse,
                               t.severe_pressure, t.severe_impulse, t.failure_pressure, t.failure_impulse, m.family,
                               t.failure_description, t.threshold_source_type, t.applicability_notes
                        FROM material_profiles mp
                        JOIN materials m ON mp.material_id = m.id
                        LEFT JOIN thresholds t ON mp.id = t.profile_id
                    """)
                profiles = []
                for row in cursor.fetchall():
                    d_row = dict(row)
                    d_row["curves"] = curves_by_profile.get(d_row["id"], [])
                    profiles.append(d_row)
                return DamageEngine.assess_batch(results, profiles)

            elif channel == "materials:getPIEnvelopes":
                profile_id = payload.get("profileId")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, s.title as source_title
                    FROM material_response_curves c
                    LEFT JOIN sources s ON c.source_id = s.id
                    WHERE c.profile_id = ?
                """, (profile_id,))
                rows = cursor.fetchall()
                
                envelopes = []
                for row in rows:
                    p0 = row["pressure_asymptote"]
                    i0 = row["impulse_asymptote"]
                    kc = row["curve_constant"]
                    damage_state = row["damage_state"]
                    curve_type = row["curve_type"]
                    conf = row["confidence_level"]
                    source = row["source_title"] or "UFC 3-340-02"
                    
                    points = []
                    if curve_type == "Hyperbolic" and p0 and i0 and kc:
                        start_val = 1.1 * i0 if i0 > 0 else 1.0
                        end_val = max(start_val * 100, 20000.0)
                        
                        log_start = math.log10(start_val)
                        log_end = math.log10(end_val)
                        step = (log_end - log_start) / 299
                        
                        for idx in range(300):
                            imp = 10 ** (log_start + idx * step)
                            denom = (imp - i0)
                            if abs(denom) < 1e-5:
                                denom = 1e-5
                            press = p0 + kc / denom
                            points.append({"impulse": imp, "pressure": press})
                            
                    envelopes.append({
                        "damage_state": damage_state,
                        "curve_type": curve_type,
                        "pressure_asymptote": p0,
                        "impulse_asymptote": i0,
                        "curve_constant": kc,
                        "confidence_level": conf,
                        "source_reference": source,
                        "equation_text": row["equation_text"],
                        "points": points
                    })
                return envelopes

            elif channel == "research:parametricSweep":
                base_scenario_id = payload.get("baseScenarioId")
                variable = payload.get("variableName")
                min_val = float(payload.get("minValue"))
                max_val = float(payload.get("maxValue"))
                step = float(payload.get("stepValue"))
                model = payload.get("model", "Kingery-Bulmash")

                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.*, e.pressure_equivalency, e.impulse_equivalency, e.general_equivalency 
                    FROM scenarios s 
                    JOIN explosives e ON s.explosive_id = e.id 
                    WHERE s.id = ?
                """, (base_scenario_id,))
                base = cursor.fetchone()
                if not base:
                    raise ValidationError("Base scenario not found")
                
                points = []
                current = min_val
                
                while current <= max_val:
                    weight = current if variable == "chargeWeight" else base["charge_weight"]
                    distance = current if variable == "distance" else base["distance"]
                    
                    calc_res = BlastCalculatorService.calculate_environment(
                        charge_weight=weight,
                        distance=distance,
                        burst_type=base["burst_type"],
                        pressure_factor=base["pressure_equivalency"],
                        impulse_factor=base["impulse_equivalency"],
                        general_factor=base["general_equivalency"],
                        model=model
                    )
                    calc_res["sweep_variable"] = current
                    points.append(calc_res)
                    current += step
                    
                return points

            elif channel == "research:compareScenarios":
                scenario_ids = payload.get("scenarioIds", [])
                if not scenario_ids:
                    return []
                
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in scenario_ids)
                cursor.execute(f"""
                    SELECT s.*, e.pressure_equivalency, e.impulse_equivalency, e.general_equivalency, e.name as explosive_name
                    FROM scenarios s
                    JOIN explosives e ON s.explosive_id = e.id
                    WHERE s.id IN ({placeholders})
                """, scenario_ids)
                scenarios = cursor.fetchall()
                
                comparison = []
                for s in scenarios:
                    curve = []
                    for d in range(1, 101, 2):
                        calc_res = BlastCalculatorService.calculate_environment(
                            charge_weight=s["charge_weight"],
                            distance=d,
                            burst_type=s["burst_type"],
                            pressure_factor=s["pressure_equivalency"],
                            impulse_factor=s["impulse_equivalency"],
                            general_factor=s["general_equivalency"]
                        )
                        curve.append({
                            "distance": d,
                            "incident_pressure": calc_res["incident_pressure"],
                            "reflected_pressure": calc_res["reflected_pressure"],
                            "positive_impulse": calc_res["positive_impulse"]
                        })
                    comparison.append({
                        "scenarioId": s["id"],
                        "scenarioName": s["name"],
                        "chargeWeight": s["charge_weight"],
                        "explosiveName": s["explosive_name"],
                        "burstType": s["burst_type"],
                        "curve": curve
                    })
                return comparison

            elif channel == "units:list":
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM unit_definitions")
                return [dict(row) for row in cursor.fetchall()]

            elif channel == "units:convert":
                value = float(payload.get("value", 0))
                from_unit = payload.get("from")
                to_unit = payload.get("to")
                return {"value": convert(value, from_unit, to_unit)}

            elif channel == "ufc:search":
                query = payload.get("query", "").strip()
                cursor = conn.cursor()
                if query:
                    cursor.execute("""
                        SELECT * FROM ufc_references 
                        WHERE figure_number LIKE ? OR title LIKE ? OR keywords LIKE ? OR category LIKE ?
                    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
                else:
                    cursor.execute("SELECT * FROM ufc_references")
                return [dict(row) for row in cursor.fetchall()]

            # ----------------------------------------------------------------
            # studies:distanceSweep
            # Payload: {explosive_id, charge_kg, distances_m[], profile_ids[], burst_type?}
            # ----------------------------------------------------------------
            elif channel == "studies:distanceSweep":
                explosive_id = payload["explosive_id"]
                charge_kg    = float(payload["charge_kg"])
                distances_m  = [float(d) for d in payload["distances_m"]]
                profile_ids  = payload["profile_ids"]
                burst_type   = payload.get("burst_type", "Surface")

                explosive, profiles_data = self._fetch_study_data(conn, explosive_id, profile_ids)
                return SweepEngine.distance_sweep(explosive, charge_kg, distances_m, profiles_data, burst_type)

            # ----------------------------------------------------------------
            # studies:chargeSweep
            # Payload: {explosive_id, charges_kg[], distance_m, profile_ids[], burst_type?}
            # ----------------------------------------------------------------
            elif channel == "studies:chargeSweep":
                explosive_id = payload["explosive_id"]
                charges_kg   = [float(c) for c in payload["charges_kg"]]
                distance_m   = float(payload["distance_m"])
                profile_ids  = payload["profile_ids"]
                burst_type   = payload.get("burst_type", "Surface")

                explosive, profiles_data = self._fetch_study_data(conn, explosive_id, profile_ids)
                return SweepEngine.charge_sweep(explosive, charges_kg, distance_m, profiles_data, burst_type)

            # ----------------------------------------------------------------
            # studies:explosiveComparison
            # Payload: {explosive_ids[], charge_kg, distances_m[], profile_ids[], burst_type?}
            # ----------------------------------------------------------------
            elif channel == "studies:explosiveComparison":
                explosive_ids = payload["explosive_ids"]
                charge_kg     = float(payload["charge_kg"])
                distances_m   = [float(d) for d in payload["distances_m"]]
                profile_ids   = payload["profile_ids"]
                burst_type    = payload.get("burst_type", "Surface")

                cursor = conn.cursor()
                explosives = []
                for eid in explosive_ids:
                    cursor.execute("SELECT * FROM explosives WHERE id = ?", (eid,))
                    row = cursor.fetchone()
                    if row:
                        explosives.append(dict(row))

                _, profiles_data = self._fetch_study_data(conn, explosive_ids[0], profile_ids)
                return SweepEngine.explosive_comparison(explosives, charge_kg, distances_m, profiles_data, burst_type)

            # ----------------------------------------------------------------
            # studies:runGrid
            # Payload: {explosive_id, charges_kg[], distances_m[], profile_ids[], burst_type?}
            # ----------------------------------------------------------------
            elif channel == "studies:runGrid":
                explosive_id = payload["explosive_id"]
                charges_kg   = [float(c) for c in payload["charges_kg"]]
                distances_m  = [float(d) for d in payload["distances_m"]]
                profile_ids  = payload["profile_ids"]
                burst_type   = payload.get("burst_type", "Surface")

                explosive, profiles_data = self._fetch_study_data(conn, explosive_id, profile_ids)
                result = BatchRunner.run_grid(explosive, charges_kg, distances_m, profiles_data, burst_type)
                return result

            # ----------------------------------------------------------------
            # studies:exportCSV
            # Payload: {sweep_points[], save_path?}
            # ----------------------------------------------------------------
            elif channel == "studies:exportCSV":
                sweep_points = payload["sweep_points"]
                save_path    = payload.get("save_path")  # None → fallback to Documents
                written_path = export_sweep_to_csv(sweep_points, save_path)
                return {"path": written_path, "n_rows": len(sweep_points)}

            else:
                raise ValueError(f"Unknown channel: {channel}")
        finally:
            conn.close()

if __name__ == "__main__":
    server = StdioServer()
    server.run()
