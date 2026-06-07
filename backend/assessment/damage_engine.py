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
        assessments = []
        
        for prof in profiles_data:
            # Facade elements experience Reflected overpressure loading, others experience Incident
            is_facade = prof["family"] in ["Glass", "Masonry"]
            P_actual = blast_results["reflected_pressure"] if is_facade else blast_results["incident_pressure"]
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
