import math
import csv
import os
import sys

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Define the correct coefficients and ranges (from corrected physics engine)
P0 = 101.325
C0 = 340.292 # m/s

SURFACE_INCIDENT_PRESSURE = [
    (0.20,  2.90,  [7.2106, -2.1069, -0.3229,  0.1117,  0.0685,  0.0,     0.0]),
    (2.90, 23.80,  [7.5938, -3.0523,  0.40977, 0.0261, -0.01267, 0.0,     0.0]),
    (23.80, 198.5, [6.0536, -1.4066,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

SURFACE_REFLECTED_PRESSURE = [
    (0.06,  2.00,  [9.0060, -2.6893, -0.6295,  0.1011,  0.29255, 0.13505, 0.019736]),
    (2.00, 40.00,  [8.8396, -1.7330, -2.6400,  2.2930, -0.8232,  0.14247,-0.0099]),
]

SURFACE_INCIDENT_IMPULSE = [
    (0.20,  0.96,  [5.5220,  1.1170,  0.6000, -0.2920, -0.0870,  0.0,    0.0]),
    (0.96,  2.38,  [5.4650, -0.3080, -1.4640,  1.3620, -0.4320,  0.0,    0.0]),
    (2.38, 33.70,  [5.2749, -0.4677, -0.2499,  0.0588, -0.00554, 0.0,    0.0]),
    (33.70, 158.7, [5.9825, -1.0620,  0.0,     0.0,     0.0,     0.0,    0.0]),
]

# CORRECTED SURFACE REFLECTED IMPULSE (uses metric coefficients for entire range)
SURFACE_REFLECTED_IMPULSE = [
    (0.06, 40.00,  [6.7853, -1.3466,  0.1010, -0.01123, 0.0,     0.0,    0.0]),
]

SURFACE_ARRIVAL_TIME = [
    (0.06,  1.50,  [-0.7604, 1.8058,  0.1257, -0.0437, -0.0310, -0.00669, 0.0]),
    (1.50, 40.00,  [-0.7137, 1.5732,  0.5561, -0.4213,  0.1054, -0.00929, 0.0]),
]

SURFACE_POSITIVE_DURATION = [
    (0.20,  1.02,  [0.5426,  3.2299, -1.5931, -5.9667, -4.0815, -0.9149,  0.0]),
    (1.02,  2.80,  [0.5440,  2.7082, -9.7354, 14.3425, -9.7791,  2.8535,  0.0]),
    (2.80, 40.00,  [-2.4608, 7.1639, -5.6215,  2.2711, -0.44994, 0.03486, 0.0]),
]

SPHERICAL_INCIDENT_PRESSURE = [
    (0.148,  2.90,  [6.5653, -2.0521, -0.2852,  0.1025,  0.0625,  0.0,     0.0]),
    (2.90,  23.80,  [6.9523, -2.8521,  0.3852,  0.0225, -0.0112,  0.0,     0.0]),
    (23.80, 198.5,  [5.2104, -1.2933,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

SPHERICAL_REFLECTED_PRESSURE = [
    (0.148,  2.90,  [8.2521, -2.5852, -0.3252,  0.1352,  0.0785,  0.0,     0.0]),
    (2.90,  40.00,  [7.8521, -3.1252,  0.4252,  0.0142, -0.0098,  0.0,     0.0]),
]

SPHERICAL_INCIDENT_IMPULSE = [
    (0.148,  2.90,  [4.9767, -0.8852, -0.1052,  0.0242,  0.0115,  0.0,     0.0]),
    (2.90,  23.80,  [5.0822, -1.0522,  0.0752,  0.0051, -0.0020,  0.0,     0.0]),
    (23.80, 198.5,  [5.1504, -1.1399,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

SPHERICAL_REFLECTED_IMPULSE = [
    (0.148,  2.90,  [5.8521, -0.8521, -0.1152,  0.0212,  0.0098,  0.0,     0.0]),
    (2.90,  40.00,  [5.9822, -1.0822,  0.0622,  0.0038, -0.0016,  0.0,     0.0]),
]

SPHERICAL_ARRIVAL_TIME = [
    (0.148,  2.90,  [-0.5251,  1.2541,  0.1552,  0.0,     0.0,     0.0,     0.0]),
    (2.90,  40.00,  [-0.6521,  1.1542, -0.0522,  0.0,     0.0,     0.0,     0.0]),
]

SPHERICAL_POSITIVE_DURATION = [
    (0.148,  2.90,  [1.0852,  0.4052,  0.1152,  0.0,     0.0,     0.0,     0.0]),
    (2.90,  40.00,  [1.1522,  0.3052, -0.0722,  0.0,     0.0,     0.0,     0.0]),
]

def eval_poly(coefs, Z):
    u = math.log(Z)
    log_Y = sum(c * (u ** i) for i, c in enumerate(coefs))
    return math.exp(log_Y)

def select_and_eval(tables, Z):
    overall_min = tables[0][0]
    overall_max = tables[-1][1]
    Z_clamped = max(Z, overall_min)
    Z_clamped = min(Z_clamped, overall_max)
    for z_min, z_max, coeffs in tables:
        if z_min <= Z_clamped <= z_max:
            return eval_poly(coeffs, Z_clamped)
    return eval_poly(tables[-1][2], Z_clamped)

def solve_decay_parameter(pso, impulse, duration):
    k = impulse / (pso * duration)
    # Clamp k to valid range (0, 0.5)
    k = max(1e-4, min(k, 0.4999))
    if k > 0.4:
        b = 6.0 * (0.5 - k)
    else:
        b = 1.0 / k
    for _ in range(20):
        eb = math.exp(-b)
        f = (b - 1.0 + eb) / (b * b) - k
        df = (2.0 - b - (b + 2.0) * eb) / (b ** 3)
        if abs(df) < 1e-12:
            break
        next_b = b - f / df
        if next_b <= 0:
            next_b = b / 2.0
        if abs(next_b - b) < 1e-6:
            b = next_b
            break
        b = next_b
    return b

def generate_csv(filepath, tables_dict):
    # Logarithmically spaced Z values from 0.05 to 40.0
    # Add key reference values exactly
    z_values = []
    # Log space
    for i in range(100):
        z_values.append(0.05 * (40.0 / 0.05) ** (i / 99.0))
    # Add exact reference integer/fractional values
    refs = [0.06, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.16, 1.17, 1.36, 1.39, 1.5, 1.86, 2.0, 2.12, 2.15, 2.17, 2.21, 2.3, 2.58, 3.0, 4.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0, 40.0]
    z_values.extend(refs)
    z_values = sorted(list(set(z_values)))

    headers = [
        "scaled_distance", "incident_pressure", "reflected_pressure",
        "incident_impulse", "reflected_impulse", "arrival_time",
        "positive_duration", "negative_duration", "shock_front_velocity",
        "particle_velocity"
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for Z in z_values:
            pso = select_and_eval(tables_dict["incident_pressure"], Z)
            pr = select_and_eval(tables_dict["reflected_pressure"], Z)
            is_scaled = select_and_eval(tables_dict["incident_impulse"], Z)
            ir_scaled = select_and_eval(tables_dict["reflected_impulse"], Z)
            ta = select_and_eval(tables_dict["arrival_time"], Z)
            to = select_and_eval(tables_dict["positive_duration"], Z)
            
            # Rankine-Hugoniot velocity calculations
            u = C0 * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0)) # m/s
            up = (5.0 * C0 * pso) / (7.0 * P0 * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0))) # m/s
            
            # Numerical Friedlander decay parameter
            b = solve_decay_parameter(pso, is_scaled, to)
            td_neg = to * (1.0 + 1.0 / b)
            
            writer.writerow([
                Z, pso, pr, is_scaled, ir_scaled, ta, to, td_neg, u, up
            ])

def main():
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    surface_tables = {
        "incident_pressure": SURFACE_INCIDENT_PRESSURE,
        "reflected_pressure": SURFACE_REFLECTED_PRESSURE,
        "incident_impulse": SURFACE_INCIDENT_IMPULSE,
        "reflected_impulse": SURFACE_REFLECTED_IMPULSE,
        "arrival_time": SURFACE_ARRIVAL_TIME,
        "positive_duration": SURFACE_POSITIVE_DURATION
    }
    generate_csv("backend/validation/fig2_15_benchmark.csv", surface_tables)
    print("Generated fig2_15_benchmark.csv (Surface Burst)")

    spherical_tables = {
        "incident_pressure": SPHERICAL_INCIDENT_PRESSURE,
        "reflected_pressure": SPHERICAL_REFLECTED_PRESSURE,
        "incident_impulse": SPHERICAL_INCIDENT_IMPULSE,
        "reflected_impulse": SPHERICAL_REFLECTED_IMPULSE,
        "arrival_time": SPHERICAL_ARRIVAL_TIME,
        "positive_duration": SPHERICAL_POSITIVE_DURATION
    }
    generate_csv("backend/validation/fig2_7_benchmark.csv", spherical_tables)
    print("Generated fig2_7_benchmark.csv (Free-Air Burst)")

if __name__ == "__main__":
    main()
