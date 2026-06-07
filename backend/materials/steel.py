from backend.materials.base_material import BaseMaterial

class Steel(BaseMaterial):
    def __init__(self, name="Structural Steel Grade 250", density=7850.0, compressive_strength=250.0, tensile_strength=250.0, failure_mode="Plastic Yielding"):
        super().__init__(name, "Steel", density, compressive_strength, tensile_strength, failure_mode)

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        base_eval = super().evaluate_damage(pressure, impulse, thresholds, curves)
        level = base_eval["damage_level"]
        mode = base_eval["controlling_mode"]
        
        minor_p = thresholds.get("minor_pressure") or 150.0
        minor_i = thresholds.get("minor_impulse") or 400.0
        mod_p = thresholds.get("moderate_pressure") or 800.0
        mod_i = thresholds.get("moderate_impulse") or 1200.0
        sev_p = thresholds.get("severe_pressure") or 3500.0
        sev_i = thresholds.get("severe_impulse") or 3000.0
        fail_p = thresholds.get("failure_pressure") or 5000.0
        fail_i = thresholds.get("failure_impulse") or 4000.0
        
        # Choose control parameter
        if mode == "Pressure":
            param, t_min, t_mod, t_sev, t_fail = pressure, minor_p, mod_p, sev_p, fail_p
        else:
            param, t_min, t_mod, t_sev, t_fail = impulse, minor_i, mod_i, sev_i, fail_i
            
        # Steel states: Elastic, Yield, Membrane, Tearing
        if level == "Safe":
            state = "Elastic"
            score = min(0.24, 0.25 * (param / t_min if t_min else 0.0))
        elif level == "Minor":
            state = "Yield"
            denom = (t_mod - t_min) if t_mod > t_min else t_min
            score = 0.25 + 0.25 * ((param - t_min) / denom)
        elif level == "Moderate":
            state = "Membrane"
            denom = (t_sev - t_mod) if t_sev > t_mod else t_mod
            score = 0.50 + 0.25 * ((param - t_mod) / denom)
        else: # Severe or Failure
            state = "Tearing"
            score = min(1.0, 0.75 + 0.25 * ((param - t_sev) / (t_fail - t_sev if t_fail > t_sev else t_sev)))
            
        score = round(min(1.0, max(0.0, score)), 2)
        
        base_eval.update({
            "damage_state": state,
            "severity_score": score,
            "damage_mechanism": "Ductile membrane stretching and boundary tear" if state in ["Membrane", "Tearing"] else "Elastic/plastic flexural deformation",
            "confidence_level": "High",
            "source_reference": "UFC 3-340-02",
            "response_model_version": "v1.0 (Progressive)"
        })
        
        return base_eval
