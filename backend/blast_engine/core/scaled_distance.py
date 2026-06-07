# Hopkinson-Cranz Blast Standoff Scaling
# Z = R / W^(1/3)

def calculate_scaled_distance(distance: float, weight: float) -> float:
    """
    Computes scaled distance using Hopkinson-Cranz scaling.
    
    Args:
        distance (float): Standoff distance (m).
        weight (float): TNT equivalent weight (kg).
        
    Returns:
        float: Stained distance Z in m/kg^(1/3)
    """
    if weight <= 0:
        raise ValueError("Equivalent weight must be greater than 0 kg.")
    if distance < 0:
        raise ValueError("Standoff distance cannot be negative.")
        
    return distance / (weight ** (1.0 / 3.0))

def calculate_pressure_scaled_distance(distance: float, pressure_equivalent_weight: float) -> float:
    """
    Computes pressure scaled distance Z_p.
    """
    return calculate_scaled_distance(distance, pressure_equivalent_weight)

def calculate_impulse_scaled_distance(distance: float, impulse_equivalent_weight: float) -> float:
    """
    Computes impulse scaled distance Z_i.
    """
    return calculate_scaled_distance(distance, impulse_equivalent_weight)
