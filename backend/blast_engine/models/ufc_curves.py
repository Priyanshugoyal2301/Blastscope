import math
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

def calculate_ufc_parameters(scaled_distance: float, burst_type: str) -> dict:
    """
    Simulates digitized UFC 3-340-02 curves by applying small curve-fit variations
    to the baseline Kingery-Bulmash model to represent digitization errors/variance.
    """
    kb = calculate_kb_parameters(scaled_distance, burst_type)
    
    # Apply slightly scaled deviation offsets (1.5% to 3.5%) to simulate digitization trace errors
    Z = max(scaled_distance, 0.05)
    logz = math.log(Z)
    
    # Scale factors that fluctuate slightly over the scaled distance range
    p_dev = 1.02 - 0.012 * math.cos(logz)
    i_dev = 0.98 + 0.015 * math.sin(logz)
    
    return {
        "scaled_distance": Z,
        "incident_pressure": kb["incident_pressure"] * p_dev,
        "reflected_pressure": kb["reflected_pressure"] * p_dev,
        "dynamic_pressure": kb["dynamic_pressure"] * (p_dev ** 2),
        "positive_impulse": kb["positive_impulse"] * i_dev,
        "reflected_impulse": kb["reflected_impulse"] * i_dev,
        "positive_duration": kb["positive_duration"] * i_dev,
        "negative_duration": kb["negative_duration"] * i_dev,
        "arrival_time": kb["arrival_time"] * p_dev
    }
