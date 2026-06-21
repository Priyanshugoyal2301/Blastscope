from backend.materials import MATERIAL_CLASS_MAP, Glass, Masonry, ReinforcedConcrete, Steel, UHPC

class DamageEngine:
    @staticmethod
    def assess_material(profile_name: str, family: str, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        """
        Instantiates appropriate material class and runs progressive response/curve assessment.
        """
        material_class = MATERIAL_CLASS_MAP.get(profile_name)
        if not material_class:
            if family == "Glass":
                material_class = Glass
            elif family == "Masonry":
                material_class = Masonry
            elif family == "Concrete" and "UHPC" in profile_name:
                material_class = UHPC
            elif family == "Concrete":
                material_class = ReinforcedConcrete
            elif family == "Steel":
                material_class = Steel
            else:
                material_class = ReinforcedConcrete
                
        mat_inst = material_class(name=profile_name)
        return mat_inst.evaluate_damage(pressure, impulse, thresholds, curves=curves)

    @classmethod
    def assess_batch(cls, blast_results: dict, profiles_data: list) -> list:
        """
        Evaluate damage across multiple material profiles.
        
        Args:
            blast_results (dict): Output from the blast calculator (incident/reflected pressure/impulse)
            profiles_data (list): List of dicts, each containing profile details and thresholds.
            
        Returns:
            list: Assessments records matching schema output.
        """
        import math
        assessments = []
        
        # Read optional parameters from blast_results or defaults
        angle = float(blast_results.get("angle_of_incidence", 0.0))
        angle_rad = math.radians(angle)
        
        # Default facade dimensions for clearing calculations
        H = 3.0  # m
        W = 4.0  # m
        S = min(H, W / 2.0)  # clearing distance = 2.0 m
        P0 = 101.325  # ambient pressure (kPa)
        
        for prof in profiles_data:
            # Facade elements experience Reflected overpressure loading, others experience Incident
            is_facade = prof["family"] in ["Glass", "Masonry"]
            
            if is_facade:
                P_incident = blast_results["incident_pressure"]
                P_reflected = blast_results["reflected_pressure"]
                I_incident = blast_results["positive_impulse"]
                I_reflected = blast_results.get("reflected_impulse", I_incident)
                
                # 1. Adjust for angle of incidence (obliquity)
                cos2 = (math.cos(angle_rad)) ** 2
                P_adj = P_incident + (P_reflected - P_incident) * cos2
                I_adj = I_incident + (I_reflected - I_incident) * cos2
                
                # 2. Adjust for clearing effects
                c0 = 0.340  # speed of sound (m/ms)
                term = 1.0 + (6.0 * P_incident) / (7.0 * P0)
                U_shock = c0 * math.sqrt(max(0.1, term))
                
                t_c = (3.0 * S) / U_shock if U_shock > 0 else 9999.0
                t_d = blast_results.get("positive_duration", 10.0)
                
                Q_so = blast_results.get("dynamic_pressure", 0.0)
                P_stag = P_incident + Q_so  # stagnation pressure Cd = 1.0
                
                if t_c < t_d:
                    I_cleared = P_adj * (t_c / 2.0) + P_stag * ((t_d - t_c) / 2.0)
                    I_actual = min(I_adj, I_cleared)
                else:
                    I_actual = I_adj
                
                P_actual = P_adj
            else:
                P_actual = blast_results["incident_pressure"]
                I_actual = blast_results["positive_impulse"]
            
            thresholds = {
                "minor_pressure": prof.get("minor_pressure"),
                "minor_impulse": prof.get("minor_impulse"),
                "moderate_pressure": prof.get("moderate_pressure"),
                "moderate_impulse": prof.get("moderate_impulse"),
                "severe_pressure": prof.get("severe_pressure"),
                "severe_impulse": prof.get("severe_impulse"),
                "failure_pressure": prof.get("failure_pressure"),
                "failure_impulse": prof.get("failure_impulse"),
            }
            
            evaluation = cls.assess_material(
                profile_name=prof["profile_name"],
                family=prof["family"],
                pressure=P_actual,
                impulse=I_actual,
                thresholds=thresholds,
                curves=prof.get("curves")
            )
            
            assessments.append({
                "profile_id": prof["id"],
                "profile_name": prof["profile_name"],
                "family": prof["family"],
                "failure_category": prof.get("failure_category", "Unknown"),
                "damage_level": evaluation["damage_level"],
                "damage_state": evaluation.get("damage_state", evaluation["damage_level"]),
                "severity_score": evaluation.get("severity_score", 0.0),
                "pressure_ratio": evaluation["pressure_ratio"],
                "impulse_ratio": evaluation["impulse_ratio"],
                "damage_index": evaluation["damage_index"],
                "controlling_mode": evaluation["controlling_mode"],
                "damage_mechanism": evaluation.get("damage_mechanism", prof.get("damage_mechanism", "Failure")),
                "assessment_reason": evaluation["reason"],
                "confidence_level": evaluation.get("confidence_level", prof.get("confidence_level", "High")),
                "source_reference": evaluation.get("source_reference", "UFC 3-340-02"),
                "response_model_version": evaluation.get("response_model_version", "v1.0 (Progressive)")
            })
            
        return assessments
