"""
independent_surface_reproduction_test.py
========================================
Performs a direct mathematical validation of BlastScope's Surface solver against
an independent, fresh implementation of Swisdak (1994) Table 1 equations.
"""

import math
import sys
import os

# Ensure backend package can be imported
sys.path.insert(0, r"c:\project\drdo\code")

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

# ===========================================================================
# INDEPENDENT REFERENCE IMPLEMENTATION OF SWISDAK (1994) TABLE 1
# ===========================================================================

# Incident Peak Overpressure Pso (kPa)
REF_SURFACE_INCIDENT_PRESSURE = [
    (0.20,  2.90,  [7.2106, -2.1069, -0.3229,  0.1117,  0.0685,  0.0,     0.0]),
    (2.90, 23.80,  [7.5938, -3.0523,  0.40977, 0.0261, -0.01267, 0.0,     0.0]),
    (23.80, 198.5, [6.0536, -1.4066,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

# Reflected Peak Pressure Pr (kPa)
REF_SURFACE_REFLECTED_PRESSURE = [
    (0.06,  2.00,  [9.0060, -2.6893, -0.6295,  0.1011,  0.29255, 0.13505, 0.019736]),
    (2.00, 40.00,  [8.8396, -1.7330, -2.6400,  2.2930, -0.8232,  0.14247,-0.0099]),
]

# Incident Impulse is/W^{1/3} (kPa·ms/kg^{1/3})
REF_SURFACE_INCIDENT_IMPULSE = [
    (0.20,  0.96,  [5.5220,  1.1170,  0.6000, -0.2920, -0.0870,  0.0,    0.0]),
    (0.96,  2.38,  [5.4650, -0.3080, -1.4640,  1.3620, -0.4320,  0.0,    0.0]),
    (2.38, 33.70,  [5.2749, -0.4677, -0.2499,  0.0588, -0.00554, 0.0,    0.0]),
    (33.70, 158.7, [5.9825, -1.0620,  0.0,     0.0,     0.0,     0.0,    0.0]),
]

# Reflected Impulse ir/W^{1/3} (kPa·ms/kg^{1/3})
REF_SURFACE_REFLECTED_IMPULSE = [
    (0.06, 40.00,  [6.7853, -1.3466,  0.1010, -0.01123, 0.0,     0.0,    0.0]),
]

# Arrival Time ta/W^{1/3} (ms/kg^{1/3})
REF_SURFACE_ARRIVAL_TIME = [
    (0.06,  1.50,  [-0.7604, 1.8058,  0.1257, -0.0437, -0.0310, -0.00669, 0.0]),
    (1.50, 40.00,  [-0.7137, 1.5732,  0.5561, -0.4213,  0.1054, -0.00929, 0.0]),
]

# Positive Phase Duration to/W^{1/3} (ms/kg^{1/3})
REF_SURFACE_POSITIVE_DURATION = [
    (0.20,  1.02,  [0.5426,  3.2299, -1.5931, -5.9667, -4.0815, -0.9149,  0.0]),
    (1.02,  2.80,  [0.5440,  2.7082, -9.7354, 14.3425, -9.7791,  2.8535,  0.0]),
    (2.80, 40.00,  [-2.4608, 7.1639, -5.6215,  2.2711, -0.44994, 0.03486, 0.0]),
]

def eval_swisdak_poly_ref(coeffs, Z):
    U = math.log(Z)
    log_Y = 0.0
    for i, c in enumerate(coeffs):
        log_Y += c * (U ** i)
    return math.exp(log_Y)

def select_and_eval_ref(tables, Z):
    overall_min = tables[0][0]
    overall_max = tables[-1][1]
    Z_clamped = max(Z, overall_min)
    Z_clamped = min(Z_clamped, overall_max)
    
    for z_min, z_max, coeffs in tables:
        if z_min <= Z_clamped <= z_max:
            return eval_swisdak_poly_ref(coeffs, Z_clamped)
            
    return eval_swisdak_poly_ref(tables[-1][2], Z_clamped)

def reference_surface(Z):
    return {
        "incident_pressure": select_and_eval_ref(REF_SURFACE_INCIDENT_PRESSURE, Z),
        "reflected_pressure": select_and_eval_ref(REF_SURFACE_REFLECTED_PRESSURE, Z),
        "positive_impulse": select_and_eval_ref(REF_SURFACE_INCIDENT_IMPULSE, Z),
        "reflected_impulse": select_and_eval_ref(REF_SURFACE_REFLECTED_IMPULSE, Z),
        "arrival_time": select_and_eval_ref(REF_SURFACE_ARRIVAL_TIME, Z),
        "positive_duration": select_and_eval_ref(REF_SURFACE_POSITIVE_DURATION, Z),
    }

# ===========================================================================
# EVALUATION SWEEP
# ===========================================================================

def main():
    print("=" * 80)
    print("Swisdak (1994) Surface Table 1 Independent Verification Sweep")
    print("=" * 80)
    
    # 5,000 log-spaced Z values from 0.06 to 40.0 m/kg^(1/3)
    num_points = 5000
    z_min = 0.06
    z_max = 40.0
    
    z_values = [z_min * (z_max / z_min) ** (i / (num_points - 1)) for i in range(num_points)]
    
    parameters = [
        "incident_pressure", "reflected_pressure", "positive_impulse",
        "reflected_impulse", "arrival_time", "positive_duration"
    ]
    
    errors = {param: [] for param in parameters}
    
    for Z in z_values:
        ref = reference_surface(Z)
        calc = calculate_kb_parameters(Z, "Surface")
        
        for param in parameters:
            ref_val = ref[param]
            calc_val = calc[param]
            
            if ref_val == 0.0:
                err = 0.0 if calc_val == 0.0 else 100.0
            else:
                err = (abs(calc_val - ref_val) / ref_val) * 100.0
            errors[param].append(err)
            
    print(f"{'Parameter':<25} | {'Mean Error %':<12} | {'Max Error %':<12} | {'RMSE %':<12}")
    print("-" * 75)
    
    all_passed = True
    for param in parameters:
        err_list = errors[param]
        mean_err = sum(err_list) / len(err_list)
        max_err = max(err_list)
        rmse_err = math.sqrt(sum(e**2 for e in err_list) / len(err_list))
        print(f"{param:<25} | {mean_err:10.8f}% | {max_err:10.8f}% | {rmse_err:10.8f}%")
        
        if mean_err >= 0.01 or max_err >= 0.01:
            all_passed = False
            
    print("=" * 80)
    if all_passed:
        print("VERIFICATION STATUS: PASSED (All errors < 0.01%)")
    else:
        print("VERIFICATION STATUS: FAILED")
    print("=" * 80)

if __name__ == "__main__":
    main()
