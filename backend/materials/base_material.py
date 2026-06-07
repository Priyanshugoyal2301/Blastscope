from abc import ABC

class BaseMaterial(ABC):
    """
    Abstract Base Class for all BlastScope materials.
    Provides a standardized interface for material property extraction
    and structural damage assessment methods.
    """
    def __init__(self, name: str, family: str, density: float, compressive_strength: float, tensile_strength: float, failure_mode: str):
        self.name = name
        self.family = family
        self.density = density  # kg/m³
        self.compressive_strength = compressive_strength  # MPa
        self.tensile_strength = tensile_strength  # MPa
        self.failure_mode = failure_mode

    def get_summary(self) -> dict:
        return {
            "name": self.name,
            "family": self.family,
            "density": self.density,
            "compressive_strength": self.compressive_strength,
            "tensile_strength": self.tensile_strength,
            "failure_mode": self.failure_mode
        }

    def evaluate_damage(self, pressure: float, impulse: float, thresholds: dict, curves: list = None) -> dict:
        """
        Evaluate damage level based on physical blast parameters and structural thresholds
        using the unified Pressure-Impulse Damage Index (DI).
        
        Args:
            pressure (float): Actual blast incident/reflected pressure in kPa.
            impulse (float): Actual blast positive phase impulse in kPa-ms.
            thresholds (dict): Threshold limits for Minor, Moderate, Severe, and Failure.
            curves (list, optional): List of response curves containing asymptotes and Kc constants.
            
        Returns:
            dict: Containing "damage_index", "damage_level", "controlling_mode", "reason", etc.
        """
        minor_p = thresholds.get("minor_pressure") or 10.0
        minor_i = thresholds.get("minor_impulse") or 50.0
        mod_p = thresholds.get("moderate_pressure")
        mod_i = thresholds.get("moderate_impulse")
        sev_p = thresholds.get("severe_pressure")
        sev_i = thresholds.get("severe_impulse")
        fail_p = thresholds.get("failure_pressure")
        fail_i = thresholds.get("failure_impulse")
        
        # Fallback to defaults if not provided
        pressure_ratio = pressure / minor_p if minor_p else 0.0
        impulse_ratio = impulse / minor_i if minor_i else 0.0
        
        damage_index = max(pressure_ratio, impulse_ratio)
        controlling_mode = "Pressure" if pressure_ratio >= impulse_ratio else "Impulse"
        
        # Evaluate damage level using curves if available
        if curves:
            # Sort curves by damage_state severity
            rank = {'Safe': 0, 'Minor': 1, 'Moderate': 2, 'Severe': 3, 'Failure': 4}
            exceeded = ['Safe']
            
            for curve in curves:
                p0 = curve.get("pressure_asymptote")
                i0 = curve.get("impulse_asymptote")
                kc = curve.get("curve_constant")
                state = curve.get("damage_state")
                
                if p0 is not None and i0 is not None and kc is not None:
                    # Check if actual point exceeds this hyperbolic curve
                    if impulse > i0 and pressure > p0:
                        if pressure >= p0 + kc / (impulse - i0):
                            exceeded.append(state)
            
            # Find the highest rank exceeded
            level = max(exceeded, key=lambda x: rank.get(x, 0))
        else:
            # Fallback to rectangular/orthogonal thresholds
            if mod_p is not None:
                if fail_p and fail_i and pressure >= fail_p and impulse >= fail_i:
                    level = "Failure"
                elif sev_p and sev_i and pressure >= sev_p and impulse >= sev_i:
                    level = "Severe"
                elif mod_p and mod_i and pressure >= mod_p and impulse >= mod_i:
                    level = "Moderate"
                elif minor_p and minor_i and pressure >= minor_p and impulse >= minor_i:
                    level = "Minor"
                else:
                    level = "Safe"
            else:
                # If only minor thresholds are provided, fall back to Sprint 2 DI scale
                if damage_index < 1.0:
                    level = "Safe"
                elif damage_index < 2.0:
                    level = "Minor"
                elif damage_index < 4.0:
                    level = "Moderate"
                else:
                    level = "Severe"
            
        reason = f"Damage Index {damage_index:.2f} governed by {controlling_mode} (P-ratio: {pressure_ratio:.2f}, I-ratio: {impulse_ratio:.2f})."
        
        return {
            "damage_index": damage_index,
            "damage_level": level,
            "controlling_mode": controlling_mode,
            "pressure_ratio": pressure_ratio,
            "impulse_ratio": impulse_ratio,
            "reason": reason
        }
