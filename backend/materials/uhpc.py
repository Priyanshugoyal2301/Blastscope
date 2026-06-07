from backend.materials.base_material import BaseMaterial

class UHPC(BaseMaterial):
    def __init__(self, name="Ultra-High Performance Concrete (UHPC)", density=2600.0, compressive_strength=150.0, tensile_strength=12.0, failure_mode="Localized Shear"):
        super().__init__(name, "Concrete", density, compressive_strength, tensile_strength, failure_mode)

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        base_eval = super().evaluate_damage(pressure, impulse, thresholds, curves)
        level = base_eval["damage_level"]
        mode = base_eval["controlling_mode"]
        
        minor_p = thresholds.get("minor_pressure") or 600.0
        minor_i = thresholds.get("minor_impulse") or 800.0
        mod_p = thresholds.get("moderate_pressure") or 2500.0
        mod_i = thresholds.get("moderate_impulse") or 2000.0
        sev_p = thresholds.get("severe_pressure") or 6000.0
        sev_i = thresholds.get("severe_impulse") or 5000.0
        fail_p = thresholds.get("failure_pressure") or 8000.0
        fail_i = thresholds.get("failure_impulse") or 8000.0
        
        if mode == "Pressure":
            param, t_min, t_mod, t_sev, t_fail = pressure, minor_p, mod_p, sev_p, fail_p
        else:
            param, t_min, t_mod, t_sev, t_fail = impulse, minor_i, mod_i, sev_i, fail_i
            
        # UHPC states: Elastic, Micro-cracking, Fiber Activation, Fiber Pullout, Localized Shear Failure
        if level == "Safe":
            state = "Elastic"
            score = min(0.19, 0.20 * (param / t_min if t_min else 0.0))
        elif level == "Minor":
            state = "Micro-cracking"
            denom = (t_mod - t_min) if t_mod > t_min else t_min
            score = 0.20 + 0.20 * ((param - t_min) / denom)
        elif level == "Moderate":
            state = "Fiber Activation"
            denom = (t_sev - t_mod) if t_sev > t_mod else t_mod
            score = 0.40 + 0.20 * ((param - t_mod) / denom)
        elif level == "Severe":
            state = "Fiber Pullout"
            denom = (t_fail - t_sev) if t_fail > t_sev else t_sev
            score = 0.60 + 0.20 * ((param - t_sev) / denom)
        else: # Failure
            state = "Localized Shear Failure"
            score = min(1.0, 0.80 + 0.20 * ((param - t_fail) / t_fail if t_fail else 0.0))
            
        score = round(min(1.0, max(0.0, score)), 2)
        
        base_eval.update({
            "damage_state": state,
            "severity_score": score,
            "damage_mechanism": "Frictional bond pullout and dynamic punching shear" if state in ["Fiber Pullout", "Localized Shear Failure"] else "Tensile fiber activation",
            "confidence_level": "Medium",
            "source_reference": "UFC 3-340-02",
            "response_model_version": "v1.0 (Progressive)"
        })
        
        return base_eval
