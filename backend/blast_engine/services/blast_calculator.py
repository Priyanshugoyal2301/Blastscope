"""
Blast Calculator Service
========================

Coordinates blast environment calculations using the Kingery-Bulmash
(Swisdak 1994) model with dual pressure/impulse TNT equivalency scaling.

Architecture Note:
    The dual TNT equivalency approach (separate pressure and impulse
    scaling factors) is a pragmatic engineering approximation. The
    original KB/Swisdak model assumes a single TNT equivalent weight.
    Splitting into pressure/impulse equivalents enables non-TNT explosive
    calculations but introduces systematic error that grows with charge
    weight and scaled distance, particularly for non-TNT explosives.
    For rigorous analysis of non-TNT explosives at extreme conditions,
    full JWL EOS or hydrocode simulations should be used.
"""

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
        
        Uses Swisdak (1994) simplified Kingery-Bulmash polynomials with
        verified coefficients (DTIC ADA526744) for hemispherical surface bursts,
        and the ground reflection equivalence for free-air bursts (UFC 3-340-02).

        Reflected pressure is computed via BOTH:
        1. KB polynomial fit (primary, for UFC figure comparison)
        2. Rankine-Hugoniot relation (secondary, theoretical cross-check)
        The primary (KB polynomial) value is used in the output.
        
        Args:
            charge_weight (float): Explosive weight (kg).
            distance (float): Standoff distance (m).
            burst_type (str): 'Free Air', 'Air', or 'Surface'.
            pressure_factor (float): Pressure TNT equivalency factor.
            impulse_factor (float): Impulse TNT equivalency factor.
            general_factor (float): General TNT equivalency factor (defaults to pressure_factor).
            model (str): 'Kingery-Bulmash' or 'Digitized UFC'.
            
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
        # Peak pressures are governed by Z_p (pressure-equivalenced scaled distance)
        # Impulse parameters are governed by Z_i (impulse-equivalenced scaled distance)
        if model == "Digitized UFC":
            kb_p = calculate_ufc_parameters(Z_p, burst_type)
            kb_i = calculate_ufc_parameters(Z_i, burst_type)
            model_name = "Digitized UFC"
            version = "v2.0"  # Updated with authentic Swisdak coefficients
        else:
            kb_p = calculate_kb_parameters(Z_p, burst_type)
            kb_i = calculate_kb_parameters(Z_i, burst_type)
            model_name = "Kingery-Bulmash"
            version = "v2.0"  # Updated with authentic Swisdak coefficients
            
        # Calculate scaling factors based on Hopkinson-Cranz scaling laws
        # Impulse and time scale as W^{1/3}
        w_p_factor = W_p ** (1.0 / 3.0) if W_p > 0 else 1.0
        w_i_factor = W_i ** (1.0 / 3.0) if W_i > 0 else 1.0

        incident_p = kb_p["incident_pressure"]
        
        # Primary reflected pressure: from KB polynomial fit
        # This is what matches the UFC Figure 2-15 curves
        reflected_p_kb = kb_p["reflected_pressure"]
        
        # Secondary reflected pressure: Rankine-Hugoniot theoretical
        # Pr = 2*Pso * (7*P0 + 4*Pso) / (7*P0 + Pso)
        # This is the exact oblique reflection formula for normal incidence
        P0 = 101.325  # kPa (standard atmospheric pressure)
        reflected_p_rh = 2.0 * incident_p * ((7.0 * P0 + 4.0 * incident_p) / (7.0 * P0 + incident_p))

        # Use KB polynomial reflected pressure as primary
        # (matches UFC figures; Rankine-Hugoniot available for comparison)
        reflected_p = reflected_p_kb

        # Combine parameters
        results = {
            "scaled_distance": Z_g,  # General scaled distance
            "incident_pressure": incident_p,
            "reflected_pressure": reflected_p,
            "reflected_pressure_rankine_hugoniot": reflected_p_rh,  # Cross-check value
            "dynamic_pressure": kb_p["dynamic_pressure"],
            "positive_impulse": kb_i["positive_impulse"] * w_i_factor,
            "reflected_impulse": kb_i["reflected_impulse"] * w_i_factor,
            "positive_duration": kb_i["positive_duration"] * w_i_factor,
            "negative_duration": kb_i["negative_duration"] * w_i_factor,
            "arrival_time": kb_p["arrival_time"] * w_p_factor,
            "shock_front_velocity": kb_p["shock_front_velocity"],
            "particle_velocity": kb_p["particle_velocity"],
            "decay_parameter": kb_i["decay_parameter"],
            
            # Scaled parameters (per kg^{1/3}) for validation comparison
            "incident_pressure_scaled": incident_p,
            "reflected_pressure_scaled": reflected_p_kb,
            "dynamic_pressure_scaled": kb_p["dynamic_pressure"],
            "positive_impulse_scaled": kb_i["positive_impulse"],
            "reflected_impulse_scaled": kb_i["reflected_impulse"],
            "positive_duration_scaled": kb_i["positive_duration"],
            "negative_duration_scaled": kb_i["negative_duration"],
            "arrival_time_scaled": kb_p["arrival_time"],
            "shock_front_velocity_scaled": kb_p["shock_front_velocity"],
            "particle_velocity_scaled": kb_p["particle_velocity"],
            
            "model_used": model_name,
            "model_version": version
        }
            
        return results
