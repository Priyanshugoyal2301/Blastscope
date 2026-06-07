from backend.blast_engine.core.scaled_distance import (
    calculate_pressure_scaled_distance,
    calculate_impulse_scaled_distance,
    calculate_scaled_distance
)
from backend.blast_engine.core.tnt_equivalence import (
    calculate_pressure_tnt_equivalent,
    calculate_impulse_tnt_equivalent,
    calculate_general_tnt_equivalent
)
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters
from backend.blast_engine.models.ufc_curves import calculate_ufc_parameters

class BlastCalculatorService:
    @staticmethod
    def calculate_environment(charge_weight: float, distance: float, burst_type: str, 
                              pressure_factor: float, impulse_factor: float, general_factor: float = None,
                              model: str = "Kingery-Bulmash") -> dict:
        """
        Coordinates the blast environment calculation using dual pressure/impulse scaling.
        
        Args:
            charge_weight (float): Explosive weight.
            distance (float): Standoff distance (m).
            burst_type (str): Free Air, Air, Surface.
            pressure_factor (float): Pressure conversion factor.
            impulse_factor (float): Impulse conversion factor.
            general_factor (float): General conversion factor.
            model (str): 'Kingery-Bulmash' or 'Digitized UFC'
            
        Returns:
            dict: Complete blast parameters package.
        """
        gen_factor = general_factor if general_factor is not None else pressure_factor
        
        # 1. Calculate TNT equivalent weights
        W_p = calculate_pressure_tnt_equivalent(charge_weight, pressure_factor)
        W_i = calculate_impulse_tnt_equivalent(charge_weight, impulse_factor)
        W_g = calculate_general_tnt_equivalent(charge_weight, gen_factor)
        
        # 2. Calculate scaled distances
        Z_p = calculate_pressure_scaled_distance(distance, W_p)
        Z_i = calculate_impulse_scaled_distance(distance, W_i)
        Z_g = calculate_scaled_distance(distance, W_g)
        
        # 3. Calculate parameters using appropriate scaled distance
        # Peak pressures are governed by Z_p
        # Impulse parameters are governed by Z_i
        if model == "Digitized UFC":
            kb_p = calculate_ufc_parameters(Z_p, burst_type)
            kb_i = calculate_ufc_parameters(Z_i, burst_type)
            model_name = "Digitized UFC"
            version = "v1.0"
        else:
            kb_p = calculate_kb_parameters(Z_p, burst_type)
            kb_i = calculate_kb_parameters(Z_i, burst_type)
            model_name = "Kingery-Bulmash"
            version = "v1.0"
            
        # Combine parameters
        results = {
            "scaled_distance": Z_g, # Return general scaled distance
            "incident_pressure": kb_p["incident_pressure"],
            "reflected_pressure": kb_p["reflected_pressure"],
            "dynamic_pressure": kb_p["dynamic_pressure"],
            "positive_impulse": kb_i["positive_impulse"],
            # Time components are typically linked to distance / duration scales (Z_p or Z_i, standard is Z_p/Z_i range)
            "positive_duration": kb_i["positive_duration"],
            "negative_duration": kb_i["negative_duration"],
            "arrival_time": kb_p["arrival_time"],
            "model_used": model_name,
            "model_version": version
        }
            
        return results
