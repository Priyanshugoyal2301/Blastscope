from backend.materials.base_material import BaseMaterial
import math

class Glass(BaseMaterial):
    def __init__(self, name="Glass 6mm Monolithic", density=2500.0, compressive_strength=250.0, tensile_strength=45.0, failure_mode="Brittle Shards"):
        super().__init__(name, "Glass", density, compressive_strength, tensile_strength, failure_mode)

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        base_eval = super().evaluate_damage(pressure, impulse, thresholds, curves)
        
        minor_p = thresholds.get("minor_pressure") or 15.0
        minor_i = thresholds.get("minor_impulse") or 100.0
        
        # Calculate demand-to-capacity ratio for Minor threshold
        di_minor = max(pressure / minor_p, impulse / minor_i)
        
        # Calculate breakage probability (Pb) based on glazing type (Monolithic vs Laminated)
        is_laminated = "laminated" in self.name.lower()
        if is_laminated:
            # Laminated glass has PVB, tougher response
            pb = 1.0 - math.exp(-0.693 * (di_minor ** 1.8))
            mechanism = "Laminated glass PVB interlayer tearing"
            source = "Blast Glazing Design and Assessment Criteria"
            confidence = "High"
        else:
            # Monolithic annealed glass
            pb = 1.0 - math.exp(-0.693 * (di_minor ** 2.5))
            mechanism = "Monolithic annealed glass tensile fracture"
            source = "ISO 16933:2007"
            confidence = "High"
            
        pb = min(1.0, max(0.0, pb))
        pb_rounded = round(pb, 2)
        
        # Override hazard state
        if pb_rounded < 0.05:
            damage_state = "Glazing Safe"
        elif pb_rounded < 0.50:
            damage_state = "Low Hazard"
        else:
            damage_state = "High Hazard"
            
        base_eval.update({
            "damage_state": damage_state,
            "severity_score": pb_rounded,
            "damage_mechanism": mechanism,
            "confidence_level": confidence,
            "source_reference": source,
            "response_model_version": "v1.0 (Progressive)"
        })
        
        return base_eval
