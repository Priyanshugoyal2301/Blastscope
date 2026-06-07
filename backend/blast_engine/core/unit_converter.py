# Unit Conversion Engine

CONVERSION_FACTORS = {
    # PRESSURE (Base unit: kPa)
    "kPa": 1.0,
    "MPa": 1000.0,
    "psi": 6.89475729,
    "bar": 100.0,
    "atm": 101.325,
    
    # DISTANCE (Base unit: m)
    "m": 1.0,
    "ft": 0.3048,
    "in": 0.0254,
    
    # MASS / WEIGHT (Base unit: kg)
    "kg": 1.0,
    "lb": 0.45359237,
    
    # IMPULSE (Base unit: kPa-ms)
    "kPa-ms": 1.0,
    "psi-ms": 6.89475729,
}

def convert(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts a value between specified units.
    
    Args:
        value (float): The value to convert.
        from_unit (str): The symbol of the source unit (e.g. 'psi').
        to_unit (str): The symbol of the target unit (e.g. 'kPa').
        
    Returns:
        float: The converted value.
    """
    if from_unit == to_unit:
        return value
        
    if from_unit not in CONVERSION_FACTORS or to_unit not in CONVERSION_FACTORS:
        raise ValueError(f"Unsupported conversion from '{from_unit}' to '{to_unit}'")
        
    # Convert to base unit first, then to target unit
    value_in_base = value * CONVERSION_FACTORS[from_unit]
    converted_value = value_in_base / CONVERSION_FACTORS[to_unit]
    
    return converted_value
