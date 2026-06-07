from backend.materials.base_material import BaseMaterial

class Masonry(BaseMaterial):
    def __init__(self, name="Brick Masonry Unreinforced", density=2000.0, compressive_strength=15.0, tensile_strength=0.5, failure_mode="Flexural Collapse"):
        super().__init__(name, "Masonry", density, compressive_strength, tensile_strength, failure_mode)

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        base_eval = super().evaluate_damage(pressure, impulse, thresholds, curves)
        level = base_eval["damage_level"]
        mode = base_eval["controlling_mode"]
        
        minor_p = thresholds.get("minor_pressure") or 14.0
        minor_i = thresholds.get("minor_impulse") or 70.0
        mod_p = thresholds.get("moderate_pressure") or 35.0
        mod_i = thresholds.get("moderate_impulse") or 150.0
        sev_p = thresholds.get("severe_pressure") or 80.0
        sev_i = thresholds.get("severe_impulse") or 380.0
        fail_p = thresholds.get("failure_pressure") or 120.0
        fail_i = thresholds.get("failure_impulse") or 500.0
        
        if mode == "Pressure":
            param, t_min, t_mod, t_sev, t_fail = pressure, minor_p, mod_p, sev_p, fail_p
        else:
            param, t_min, t_mod, t_sev, t_fail = impulse, minor_i, mod_i, sev_i, fail_i
            
        # Masonry states: Elastic, Cracking, Yielding, Three-Hinge Collapse
        if level == "Safe":
            state = "Elastic"
            score = min(0.24, 0.25 * (param / t_min if t_min else 0.0))
        elif level == "Minor":
            state = "Cracking"
            denom = (t_mod - t_min) if t_mod > t_min else t_min
            score = 0.25 + 0.25 * ((param - t_min) / denom)
        elif level == "Moderate":
            state = "Yielding"
            denom = (t_sev - t_mod) if t_sev > t_mod else t_mod
            score = 0.50 + 0.25 * ((param - t_mod) / denom)
        else: # Severe or Failure
            state = "Three-Hinge Collapse"
            score = min(1.0, 0.75 + 0.25 * ((param - t_sev) / (t_fail - t_sev if t_fail > t_sev else t_sev)))
            
        score = round(min(1.0, max(0.0, score)), 2)
        
        base_eval.update({
            "damage_state": state,
            "severity_score": score,
            "damage_mechanism": "Structural instability and masonry unit shedding" if state == "Three-Hinge Collapse" else "Mortar joint shear/cracking",
            "confidence_level": "Medium",
            "source_reference": "Blast Performance of Concrete Masonry Unit (CMU) Walls",
            "response_model_version": "v1.0 (Progressive)"
        })
        
        return base_eval
