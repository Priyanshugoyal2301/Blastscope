# TNT Equivalence Logic
# Calibrates equivalent blast weight W_tnt based on specific factors

def calculate_pressure_tnt_equivalent(weight: float, pressure_factor: float) -> float:
    """
    Computes TNT equivalent weight for peak shock pressure calculations.
    """
    if weight <= 0:
        raise ValueError("Weight must be greater than 0")
    if pressure_factor <= 0:
        raise ValueError("Pressure factor must be greater than 0")
    return weight * pressure_factor

def calculate_impulse_tnt_equivalent(weight: float, impulse_factor: float) -> float:
    """
    Computes TNT equivalent weight for shock impulse calculations.
    """
    if weight <= 0:
        raise ValueError("Weight must be greater than 0")
    if impulse_factor <= 0:
        raise ValueError("Impulse factor must be greater than 0")
    return weight * impulse_factor

def calculate_general_tnt_equivalent(weight: float, general_factor: float) -> float:
    """
    Computes general TNT equivalent weight for standard reports/UFC checks.
    """
    if weight <= 0:
        raise ValueError("Weight must be greater than 0")
    if general_factor <= 0:
        raise ValueError("General factor must be greater than 0")
    return weight * general_factor
