from backend.materials.base_material import BaseMaterial

class HumanInjury(BaseMaterial):
    def __init__(self, name="Human Vulnerability", density=1000.0, compressive_strength=0.0, tensile_strength=0.0, failure_mode="Blast Injury"):
        super().__init__(name, "Human", density, compressive_strength, tensile_strength, failure_mode)

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        base_eval = super().evaluate_damage(pressure, impulse, thresholds, curves)
        level = base_eval["damage_level"]
        mode = base_eval["controlling_mode"]
        
        minor_p = thresholds.get("minor_pressure") or 34.0
        minor_i = thresholds.get("minor_impulse") or 80.0
        mod_p = thresholds.get("moderate_pressure") or 100.0
        mod_i = thresholds.get("moderate_impulse") or 180.0
        sev_p = thresholds.get("severe_pressure") or 240.0
        sev_i = thresholds.get("severe_impulse") or 380.0
        fail_p = thresholds.get("failure_pressure") or 340.0
        fail_i = thresholds.get("failure_impulse") or 600.0
        
        # Choose control parameter
        if mode == "Pressure":
            param, t_min, t_mod, t_sev, t_fail = pressure, minor_p, mod_p, sev_p, fail_p
        else:
            param, t_min, t_mod, t_sev, t_fail = impulse, minor_i, mod_i, sev_i, fail_i
            
        # Interpolate severity score
        if level == "Safe":
            state = "Healthy"
            score = min(0.19, 0.20 * (param / t_min if t_min else 0.0))
        elif level == "Minor":
            state = "Eardrum Rupture"
            denom = (t_mod - t_min) if t_mod > t_min else t_min
            score = 0.20 + 0.20 * ((param - t_min) / denom)
        elif level == "Moderate":
            state = "Severe Eardrum Rupture"
            denom = (t_sev - t_mod) if t_sev > t_mod else t_mod
            score = 0.40 + 0.20 * ((param - t_mod) / denom)
        elif level == "Severe":
            state = "Lung Damage"
            denom = (t_fail - t_sev) if t_fail > t_sev else t_sev
            score = 0.60 + 0.20 * ((param - t_sev) / denom)
        else: # Failure
            state = "Lethality"
            score = min(1.0, 0.80 + 0.20 * ((param - t_fail) / t_fail if t_fail else 0.0))
            
        score = round(min(1.0, max(0.0, score)), 2)
        
        base_eval.update({
            "damage_state": state,
            "severity_score": score,
            "damage_mechanism": "Primary blast overpressure trauma" if state in ["Lung Damage", "Lethality"] else "Acoustic trauma & dynamic displacement",
            "confidence_level": "Medium",
            "source_reference": "Glasstone & Dolan (1977) / UFC 3-340-02",
            "response_model_version": "v1.0 (Progressive)"
        })
        
        return base_eval
