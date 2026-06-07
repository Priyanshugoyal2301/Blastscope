# Charts Data Generator (Python side helper)

def generate_curve_points(start_val: float, end_val: float, step: float, calculation_func) -> list:
    """
    Utility to run a function over a sweep range and collect output points for plotting.
    
    Args:
        start_val (float): Sweep minimum.
        end_val (float): Sweep maximum.
        step (float): Sweep step increment.
        calculation_func (callable): Function taking the swept variable and returning metrics.
        
    Returns:
        list: Collection of dict points.
    """
    points = []
    current = start_val
    while current <= end_val:
        try:
            res = calculation_func(current)
            res["x_value"] = current
            points.append(res)
        except Exception:
            pass
        current += step
    return points
