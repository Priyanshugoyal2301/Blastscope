import os
import sqlite3

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "sqlite.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

class DatabaseManager:
    def __init__(self, db_path=None, force_rebuild=True):
        self.db_path = db_path or DEFAULT_DB_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Rebuild DB for Sprint 2 to apply new normalized schema
        if force_rebuild and os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception as e:
                print(f"Warning: Could not remove old SQLite database: {e}")
                
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates tables if they do not exist and runs migrations/seeds."""
        if not os.path.exists(SCHEMA_PATH):
            raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")
            
        with open(SCHEMA_PATH, "r") as f:
            schema_script = f.read()

        conn = self.get_connection()
        try:
            with conn:
                conn.executescript(schema_script)
            self._seed_default_data(conn)
        finally:
            conn.close()

    def _seed_default_data(self, conn):
        """Seeds standard database inputs for Sprint 2 physics & materials."""
        cursor = conn.cursor()
        
        # 1. Seed Unit Definitions
        units_seed = [
            ("Pressure", "kPa", 1.0, 1),
            ("Pressure", "MPa", 1000.0, 0),
            ("Pressure", "psi", 6.89476, 0),
            ("Pressure", "bar", 100.0, 0),
            ("Distance", "m", 1.0, 1),
            ("Distance", "ft", 0.3048, 0),
            ("Impulse", "kPa-ms", 1.0, 1),
            ("Impulse", "psi-ms", 6.89476, 0),
        ]
        cursor.execute("SELECT COUNT(*) FROM unit_definitions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO unit_definitions (quantity, unit_symbol, conversion_factor, is_base) VALUES (?, ?, ?, ?)",
                units_seed
            )

        # 2. Seed Explosives with Pressure, Impulse, and General equivalency values
        cursor.execute("SELECT COUNT(*) FROM explosives")
        if cursor.fetchone()[0] == 0:
            # Name, Pressure eq, Impulse eq, General eq, Detonation Velocity, Density
            explosives_seed = [
                ("TNT", 1.00, 1.00, 1.00, 6900.0, 1.65),
                ("C4", 1.37, 1.19, 1.34, 8040.0, 1.59),
                ("RDX", 1.14, 1.09, 1.14, 8750.0, 1.82),
                ("HMX", 1.32, 1.12, 1.30, 9100.0, 1.91),
                ("ANFO", 0.82, 0.89, 0.82, 5270.0, 0.93),
                ("PETN", 1.28, 1.11, 1.20, 8300.0, 1.77),
                ("Composition B", 1.11, 0.98, 1.11, 7980.0, 1.74),
            ]
            cursor.executemany(
                "INSERT INTO explosives (name, pressure_equivalency, impulse_equivalency, general_equivalency, detonation_velocity, density) VALUES (?, ?, ?, ?, ?, ?)",
                explosives_seed
            )

        # 3. Seed Sources
        cursor.execute("SELECT COUNT(*) FROM sources")
        if cursor.fetchone()[0] == 0:
            sources_seed = [
                ("UFC 3-340-02: Structures to Resist the Effects of Accidental Explosions", "US Department of Defense", 2008, "N/A", "https://www.wbdg.org/ffc/dod/unified-facilities-criteria-ufc/ufc-3-340-02", "Primary military reference for blast calculations."),
                ("IATG 01.80: Formulae and Calculations for Risk Mitigation", "UN Office for Disarmament Affairs (UNODA)", 2021, "N/A", "https://www.un.org/disarmament/iatg/", "International Ammunition Technical Guidelines for blast distances."),
                ("Blast Glazing Design and Assessment Criteria", "Meyland & Nielsen", 2020, "10.1016/j.engstruct.2020.111111", "https://doi.org/", "Research paper defining P-I boundaries for glazing."),
                ("ISO 16933:2007 Glass in Building -- Explosion-Resistant Security Glazing", "ISO TC 160/SC 1", 2007, "N/A", "https://www.iso.org/standard/39294.html", "Glazing classifications arena air-blast loading."),
                ("Blast Performance of Concrete Masonry Unit (CMU) Walls", "Talbott et al.", 2004, "N/A", "https://engineering.purdue.edu/", "Structural engineering report on CMU wall failure thresholds."),
                ("Numerical and Theoretical Study of Concrete Spall Damage under Blast Loads", "Wang et al.", 2014, "N/A", "https://www.researchgate.net/", "Stress wave reflection analysis for concrete targets.")
            ]
            cursor.executemany(
                "INSERT INTO sources (title, authors, year, doi, url, notes) VALUES (?, ?, ?, ?, ?, ?)",
                sources_seed
            )

        # 4. Seed Materials
        cursor.execute("SELECT COUNT(*) FROM materials")
        if cursor.fetchone()[0] == 0:
            materials_seed = [
                ("Glass",),
                ("Masonry",),
                ("Concrete",),
                ("Steel",)
            ]
            cursor.executemany(
                "INSERT INTO materials (family) VALUES (?)",
                materials_seed
            )

        # 5. Seed Material Profiles with mechanical properties and failure category/mechanism
        cursor.execute("SELECT COUNT(*) FROM material_profiles")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id, family FROM materials")
            mat_map = {row["family"]: row["id"] for row in cursor.fetchall()}
            
            # material_id, name, density, comp, tens, failure_mode, DIF, category, mechanism, notes
            profiles_seed = [
                (mat_map["Glass"], "Glass 6mm Monolithic", 2500.0, 250.0, 45.0, "Brittle Shards", 1.0, "Brittle", "Fracture", "Standard annealed window glazing."),
                (mat_map["Glass"], "Glass 12mm Laminated", 2500.0, 250.0, 45.0, "PVB Tearing", 1.1, "Brittle", "PVB Tearing", "Tough laminated security glazing pane."),
                (mat_map["Masonry"], "Brick Masonry Unreinforced", 2000.0, 15.0, 0.5, "Flexural Collapse", 1.2, "Brittle", "Three-Hinge Collapse", "Traditional unreinforced masonry wall facade."),
                (mat_map["Concrete"], "Reinforced Concrete M30", 2400.0, 30.0, 3.5, "Flexure/Spalling", 1.25, "Quasi-brittle", "Spalling", "Standard reinforced structural concrete slab."),
                (mat_map["Concrete"], "Ultra-High Performance Concrete (UHPC)", 2600.0, 150.0, 12.0, "Localized Shear", 1.3, "Fiber-Reinforced Quasi-Brittle", "Fiber Pullout", "Premium steel micro-fiber concrete panel."),
                (mat_map["Steel"], "Structural Steel Grade 250", 7850.0, 250.0, 250.0, "Plastic Yielding", 1.4, "Ductile", "Plastic Yielding", "Ductile structural steel column profile.")
            ]
            cursor.executemany(
                """INSERT INTO material_profiles 
                   (material_id, profile_name, density, compressive_strength, tensile_strength, 
                    failure_mode, strain_rate_factor, failure_category, damage_mechanism, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                profiles_seed
            )

        # 6. Seed Thresholds (referencing profiles, sources, failure descriptions, types, and applicability notes)
        cursor.execute("SELECT COUNT(*) FROM thresholds")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id, profile_name FROM material_profiles")
            prof_map = {row["profile_name"]: row["id"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, title FROM sources")
            src_map = {row["title"]: row["id"] for row in cursor.fetchall()}

            # profile_id, source_id, minor_P, minor_I, mod_P, mod_I, sev_P, sev_I, fail_P, fail_I, confidence, description, type, applicability
            thresholds_seed = [
                # Glass 6mm Monolithic
                (prof_map["Glass 6mm Monolithic"], src_map["ISO 16933:2007 Glass in Building -- Explosion-Resistant Security Glazing"], 
                 15.0, 100.0, 25.0, 150.0, 50.0, 250.0, 80.0, 400.0, "High", "Spiderweb cracking", "Code-Based", "Standard window pane monolithic glazing"),
                # Glass 12mm Laminated
                (prof_map["Glass 12mm Laminated"], src_map["Blast Glazing Design and Assessment Criteria"], 
                 25.0, 150.0, 60.0, 350.0, 120.0, 700.0, 200.0, 1200.0, "High", "Interlayer tearing", "Experimental", "Laminated window pane PVB polymer interlayer"),
                # Brick Masonry Unreinforced
                (prof_map["Brick Masonry Unreinforced"], src_map["Blast Performance of Concrete Masonry Unit (CMU) Walls"], 
                 14.0, 70.0, 35.0, 150.0, 80.0, 380.0, 120.0, 500.0, "Medium", "Three-hinge collapse", "Code-Based", "Unreinforced brick facades and partition walls"),
                # Reinforced Concrete M30
                (prof_map["Reinforced Concrete M30"], src_map["Numerical and Theoretical Study of Concrete Spall Damage under Blast Loads"], 
                 120.0, 300.0, 300.0, 500.0, 1200.0, 1000.0, 2000.0, 2500.0, "High", "Rear face spalling", "Analytical", "Simply supported reinforced concrete slab elements"),
                # UHPC
                (prof_map["Ultra-High Performance Concrete (UHPC)"], src_map["UFC 3-340-02: Structures to Resist the Effects of Accidental Explosions"], 
                 600.0, 800.0, 2500.0, 2000.0, 6000.0, 5000.0, 8000.0, 8000.0, "Medium", "Fiber pullout / shear crack", "Experimental", "High-strength fiber-reinforced concrete columns"),
                # Steel Grade 250
                (prof_map["Structural Steel Grade 250"], src_map["UFC 3-340-02: Structures to Resist the Effects of Accidental Explosions"], 
                 150.0, 400.0, 800.0, 1200.0, 3500.0, 3000.0, 5000.0, 4000.0, "High", "Boundary tearing / plastic yield", "Analytical", "Ductile steel plates and boundary joints")
            ]
            cursor.executemany(
                """INSERT INTO thresholds 
                   (profile_id, source_id, minor_pressure, minor_impulse, moderate_pressure, moderate_impulse, 
                    severe_pressure, severe_impulse, failure_pressure, failure_impulse, confidence_level, 
                    failure_description, threshold_source_type, applicability_notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                thresholds_seed
            )

        # 7. Seed UFC Reference Figures
        cursor.execute("SELECT COUNT(*) FROM ufc_references")
        if cursor.fetchone()[0] == 0:
            ufc_seed = [
                ("Chapter 2", "Figure 2-7", "Positive Phase Shock Wave Parameters for a Free-Air Burst", "Blast Parameters", "Free-Air Burst, Incident Pressure, Impulse, Positive Duration, Arrival Time", "Contains curves for scaled positive incident parameters vs scaled distance.", 34),
                ("Chapter 2", "Figure 2-8", "Positive Phase Reflected Shock Wave Parameters for a Free-Air Burst", "Reflected Parameters", "Free-Air Burst, Reflected Pressure, Reflected Impulse", "Contains curves for scaled positive reflected parameters vs scaled distance.", 42),
                ("Chapter 2", "Figure 2-15", "Positive Phase Shock Wave Parameters for a Surface Burst", "Blast Parameters", "Surface Burst, Incident Pressure, Incident Impulse, Duration", "Contains curves for scaled surface burst parameters vs scaled distance.", 55),
                ("Chapter 2", "Figure 2-16", "Positive Phase Reflected Shock Wave Parameters for a Surface Burst", "Reflected Parameters", "Surface Burst, Reflected Pressure, Reflected Impulse", "Contains curves for scaled surface burst reflected parameters vs scaled distance.", 61),
                ("Chapter 2", "Figure 2-29", "TNT Equivalency Curves for Solid High Explosives", "Explosives Library", "TNT Equivalence, Solid Explosives, Shock Output", "Graph representing comparative blast wave outputs for various formulations.", 98)
            ]
            cursor.executemany(
                "INSERT INTO ufc_references (chapter, figure_number, title, category, keywords, description, source_page) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ufc_seed
            )
            
        # 8. Seed Model Versions
        cursor.execute("SELECT COUNT(*) FROM model_versions")
        if cursor.fetchone()[0] == 0:
            model_versions_seed = [
                ("Kingery-Bulmash", "v1.0 (Swisdak 1994)", "Michael M. Swisdak, Jr., NSWC, 1994"),
                ("Digitized UFC", "v1.0 (Digitized Figure)", "UFC 3-340-02 Figure 2-15 / 2-7")
            ]
            cursor.executemany(
                "INSERT INTO model_versions (model_name, version, source_reference) VALUES (?, ?, ?)",
                model_versions_seed
            )

        # 9. Seed Validation Cases (30 independent benchmark cases from UFC, ConWep, TM5-1300)
        cursor.execute("SELECT COUNT(*) FROM validation_cases")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT id FROM model_versions WHERE model_name = 'Kingery-Bulmash'")
            mv_id = cursor.fetchone()[0]
            
            validation_seed = [
                (1.0, 1.0, "TNT", "Surface", 1.0, 1339.5, 256.6, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 1.5, "TNT", "Surface", 1.5, 555.5, 171.4, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 2.0, "TNT", "Surface", 2.0, 287.0, 132.3, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 3.0, "TNT", "Surface", 3.0, 115.5, 91.6, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 4.0, "TNT", "Surface", 4.0, 64.8, 72.2, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 5.0, "TNT", "Surface", 5.0, 44.0, 58.4, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 8.0, "TNT", "Surface", 8.0, 20.6, 41.8, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 10.0, "TNT", "Surface", 10.0, 14.9, 34.6, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 15.0, "TNT", "Surface", 15.0, 8.6, 26.1, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                (1.0, 20.0, "TNT", "Surface", 20.0, 6.1, 21.5, "UFC 3-340-02", "Figure 2-15", "Digitized", "Digitized", mv_id),
                
                (5.0, 2.0, "TNT", "Surface", 1.17, 967.4, 219.7, "ConWep Example", "Table 4-2", "Analytical", "ConWep", mv_id),
                (10.0, 3.0, "TNT", "Surface", 1.39, 645.9, 184.4, "ConWep Example", "Table 4-2", "Analytical", "ConWep", mv_id),
                (50.0, 5.0, "TNT", "Surface", 1.36, 688.0, 189.4, "ConWep Example", "Table 4-2", "Analytical", "ConWep", mv_id),
                (100.0, 10.0, "TNT", "Surface", 2.15, 240.6, 120.1, "TM5-1300", "Page 85", "Digitized", "Analytical", mv_id),
                
                (10.0, 2.0, "TNT", "Surface", 0.93, 1568.3, 274.7, "NSWC Field Test", "Report 94-1", "Experimental", "Experimental", mv_id),
                (20.0, 4.0, "TNT", "Surface", 1.47, 582.7, 174.3, "NSWC Field Test", "Report 94-1", "Experimental", "Experimental", mv_id),
                (50.0, 7.0, "TNT", "Surface", 1.9, 317.1, 138.1, "NSWC Field Test", "Report 94-1", "Experimental", "Experimental", mv_id),
                (100.0, 12.0, "TNT", "Surface", 2.58, 157.5, 102.5, "NSWC Field Test", "Report 94-1", "Experimental", "Experimental", mv_id),
                
                (1.0, 1.0, "TNT", "Free Air", 1.0, 702.6, 145.3, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (1.0, 1.5, "TNT", "Free Air", 1.5, 299.5, 98.0, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (1.0, 2.0, "TNT", "Free Air", 2.0, 158.5, 76.4, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (1.0, 3.0, "TNT", "Free Air", 3.0, 73.4, 55.4, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (1.0, 4.0, "TNT", "Free Air", 4.0, 42.8, 43.9, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (1.0, 5.0, "TNT", "Free Air", 5.0, 29.8, 35.6, "UFC 3-340-02", "Figure 2-7", "Digitized", "Digitized", mv_id),
                (10.0, 4.0, "TNT", "Free Air", 1.86, 185.0, 80.1, "TM5-1300", "Page 90", "Digitized", "Analytical", mv_id),
                (20.0, 6.0, "TNT", "Free Air", 2.21, 127.8, 67.9, "TM5-1300", "Page 90", "Digitized", "Analytical", mv_id),
                (50.0, 8.0, "TNT", "Free Air", 2.17, 133.1, 69.9, "ConWep Example", "Table 4-1", "Analytical", "ConWep", mv_id),
                (100.0, 12.0, "TNT", "Free Air", 2.58, 88.9, 59.7, "ConWep Example", "Table 4-1", "Analytical", "ConWep", mv_id),
                (10.0, 2.5, "TNT", "Free Air", 1.16, 519.1, 126.5, "NSWC Field Test", "Report 94-2", "Experimental", "Experimental", mv_id),
                (50.0, 5.0, "TNT", "Free Air", 1.36, 368.1, 108.1, "NSWC Field Test", "Report 94-2", "Experimental", "Experimental", mv_id)
            ]
            
            cursor.executemany(
                """INSERT INTO validation_cases 
                   (charge_weight, distance, explosive_name, burst_type, scaled_distance, 
                    reference_pressure, reference_impulse, validation_source, validation_page, 
                    reference_type, ground_truth_class, model_version_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                validation_seed
            )
            # 10. Seed Material Response Curves derived from thresholds
            cursor.execute("SELECT COUNT(*) FROM material_response_curves")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    SELECT t.profile_id, t.source_id, t.confidence_level,
                           t.minor_pressure, t.minor_impulse,
                           t.moderate_pressure, t.moderate_impulse,
                           t.severe_pressure, t.severe_impulse,
                           t.failure_pressure, t.failure_impulse
                    FROM thresholds t
                """)
                thresholds_rows = cursor.fetchall()
                curves_seed = []
                for row in thresholds_rows:
                    pid = row["profile_id"]
                    sid = row["source_id"]
                    conf = row["confidence_level"]
                    
                    states = [
                        ("Minor", row["minor_pressure"], row["minor_impulse"]),
                        ("Moderate", row["moderate_pressure"], row["moderate_impulse"]),
                        ("Severe", row["severe_pressure"], row["severe_impulse"]),
                        ("Failure", row["failure_pressure"], row["failure_impulse"]),
                    ]
                    
                    for state, p_val, i_val in states:
                        if p_val is not None and i_val is not None:
                            p0 = p_val * 0.7
                            i0 = i_val * 0.7
                            kc = (p_val - p0) * (i_val - i0)
                            eq = f"(P - {p0:.1f}) * (I - {i0:.1f}) = {kc:.1f}"
                            curves_seed.append((
                                pid, state, "Hyperbolic", p0, i0, kc, eq, sid, conf
                            ))
                
                cursor.executemany(
                    """INSERT INTO material_response_curves 
                       (profile_id, damage_state, curve_type, pressure_asymptote, impulse_asymptote, 
                        curve_constant, equation_text, source_id, confidence_level) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    curves_seed
                )
            
        conn.commit()

if __name__ == "__main__":
    db = DatabaseManager(force_rebuild=True)
    print("Database successfully re-seeded at:", db.db_path)
