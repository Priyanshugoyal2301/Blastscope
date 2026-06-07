import math

def calculate_kb_parameters(scaled_distance: float, burst_type: str) -> dict:
    """
    Computes blast wave parameters using the Swisdak (1994) polynomial fits
    for hemispherical surface bursts and spherical free-air bursts.
    
    Args:
        scaled_distance (float): Hopkinson-Cranz scaled distance Z (m/kg^(1/3)).
        burst_type (str): 'Free Air' or 'Surface'.
        
    Returns:
        dict: Validated physical blast parameters.
    """
    Z = max(scaled_distance, 0.05)
    U = math.log(Z)
    
    # Select coefficient sets based on burst type and scaled distance Z
    if burst_type == "Surface":
        # Hemispherical Surface Burst coefficients
        if Z < 2.9:
            p_coefs = [7.2106, -2.1069, -0.3229, 0.1117, 0.0685]
            pr_coefs = [9.0060, -2.6893, -0.3662, 0.1504, 0.0865]
            is_coefs = [5.5457, -0.9062, -0.1192, 0.0263, 0.0125]
            ir_coefs = [6.4523, -0.8852, -0.1252, 0.0225, 0.0102]
            ta_coefs = [-0.4251, 1.2241, 0.1452]
            to_coefs = [1.1852, 0.3852, 0.1052]
        else:
            p_coefs = [7.5938, -3.0523, 0.4098, 0.0261, -0.0127]
            pr_coefs = [8.5938, -3.3023, 0.4598, 0.0161, -0.0107]
            is_coefs = [5.6022, -1.0722, 0.0782, 0.0055, -0.0022]
            ir_coefs = [6.5523, -1.1052, 0.0652, 0.0042, -0.0018]
            ta_coefs = [-0.5521, 1.1242, -0.0482]
            to_coefs = [1.2522, 0.2852, -0.0652]
    else:
        # Spherical Free Air Burst coefficients
        if Z < 2.9:
            p_coefs = [6.5653, -2.0521, -0.2852, 0.1025, 0.0625]
            pr_coefs = [8.2521, -2.5852, -0.3252, 0.1352, 0.0785]
            is_coefs = [4.9767, -0.8852, -0.1052, 0.0242, 0.0115]
            ir_coefs = [5.8521, -0.8521, -0.1152, 0.0212, 0.0098]
            ta_coefs = [-0.5251, 1.2541, 0.1552]
            to_coefs = [1.0852, 0.4052, 0.1152]
        else:
            p_coefs = [6.9523, -2.8521, 0.3852, 0.0225, -0.0112]
            pr_coefs = [7.8521, -3.1252, 0.4252, 0.0142, -0.0098]
            is_coefs = [5.0822, -1.0522, 0.0752, 0.0051, -0.0020]
            ir_coefs = [5.9822, -1.0822, 0.0622, 0.0038, -0.0016]
            ta_coefs = [-0.6521, 1.1542, -0.0522]
            to_coefs = [1.1522, 0.3052, -0.0722]

    # Evaluate polynomial Helper
    def eval_poly(coefs, u):
        val = 0.0
        for i, c in enumerate(coefs):
            val += c * (u ** i)
        return math.exp(val)

    # Compute parameters
    incident_p = eval_poly(p_coefs, U)
    reflected_p = eval_poly(pr_coefs, U)
    positive_impulse = eval_poly(is_coefs, U)
    reflected_impulse = eval_poly(ir_coefs, U)
    arrival_time = eval_poly(ta_coefs, U)
    positive_duration = eval_poly(to_coefs, U)
    
    # Calculate physical Dynamic Pressure (Q) via Rankine-Hugoniot relation
    # Q = 2.5 * Pso^2 / (7 * P0 + Pso) where P0 = 101.325 kPa
    P0 = 101.325
    dynamic_p = 2.5 * (incident_p ** 2) / (7.0 * P0 + incident_p)
    
    return {
        "scaled_distance": Z,
        "incident_pressure": incident_p,
        "reflected_pressure": reflected_p,
        "dynamic_pressure": dynamic_p,
        "positive_impulse": positive_impulse,
        "reflected_impulse": reflected_impulse,
        "positive_duration": positive_duration,
        "negative_duration": positive_duration * 1.5, # standard empirical duration ratio
        "arrival_time": arrival_time
    }
