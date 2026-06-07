class ValidationError(Exception):
    pass

def validate_scenario_params(charge_weight: float, distance: float, burst_type: str) -> None:
    """
    Validates scenario inputs before calculations.
    
    Args:
        charge_weight (float): Mass of explosive.
        distance (float): Standoff distance.
        burst_type (str): Type of explosion burst.
        
    Raises:
        ValidationError: If any parameter is physically or semantically invalid.
    """
    if charge_weight <= 0:
        raise ValidationError("Charge weight must be strictly greater than 0 kg.")
        
    if distance < 0.1:
        raise ValidationError("Distance must be at least 0.1 meters to avoid extreme near-field singularities.")
        
    valid_bursts = ["Free Air", "Air", "Surface"]
    if burst_type not in valid_bursts:
        raise ValidationError(f"Invalid burst type '{burst_type}'. Must be one of {valid_bursts}.")
