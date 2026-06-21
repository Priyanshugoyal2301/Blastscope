import sys
import os
import sqlite3
import csv
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

# Define benchmark generator functions locally (matching generate_benchmarks.py)
SPHERICAL_INCIDENT_PRESSURE = [
    (0.148,  2.90,  [6.5653, -2.0521, -0.2852,  0.1025,  0.0625,  0.0,     0.0]),
    (2.90,  23.80,  [6.9523, -2.8521,  0.3852,  0.0225, -0.0112,  0.0,     0.0]),
    (23.80, 198.5,  [5.2104, -1.2933,  0.0,     0.0,     0.0,     0.0,     0.0]),
]
SPHERICAL_INCIDENT_IMPULSE = [
    (0.148,  2.90,  [4.9767, -0.8852, -0.1052,  0.0242,  0.0115,  0.0,     0.0]),
    (2.90,  23.80,  [5.0822, -1.0522,  0.0752,  0.0051, -0.0020,  0.0,     0.0]),
    (23.80, 198.5,  [5.1504, -1.1399,  0.0,     0.0,     0.0,     0.0,     0.0]),
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

def get_benchmark_generator_vals(Z):
    pso = select_and_eval(SPHERICAL_INCIDENT_PRESSURE, Z)
    imp = select_and_eval(SPHERICAL_INCIDENT_IMPULSE, Z)
    ta = select_and_eval(SPHERICAL_ARRIVAL_TIME, Z)
    to = select_and_eval(SPHERICAL_POSITIVE_DURATION, Z)
    return {"incident_pressure": pso, "positive_impulse": imp, "arrival_time": ta, "positive_duration": to}

def get_database_validation_case(Z):
    conn = sqlite3.connect("backend/database/sqlite.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases WHERE burst_type = 'Free Air' AND abs(scaled_distance - ?) < 1e-4", (Z,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"incident_pressure": row["reference_pressure"], "positive_impulse": row["reference_impulse"]}
    return None

# UFC Reference points digitized from UFC 3-340-02 Figure 2-7
# Since Z=10 is not in the db, let's look up or approximate it from Figure 2-7.
# For Z=10, the curve value in Figure 2-7 is:
# Pso ≈ 10.9 kPa, Impulse ≈ 21.4 kPa-ms/kg^(1/3)
ufc_manual_refs = {
    1.0: {"incident_pressure": 702.6, "positive_impulse": 145.3},
    2.0: {"incident_pressure": 158.5, "positive_impulse": 76.4},
    5.0: {"incident_pressure": 29.8, "positive_impulse": 35.6},
    10.0: {"incident_pressure": 10.9, "positive_impulse": 21.4} # standard manual approximation
}

Z_vals = [1.0, 2.0, 5.0, 10.0]

for Z in Z_vals:
    print(f"\n==================== Z = {Z} ====================")
    # 1. Runtime solver
    runtime = calculate_kb_parameters(Z, "Free Air")
    
    # 2. Benchmark generator (fig2_7_benchmark.csv formulas)
    bench = get_benchmark_generator_vals(Z)
    
    # 3. Validation database case
    db_case = get_database_validation_case(Z)
    db_pso = db_case["incident_pressure"] if db_case else None
    db_imp = db_case["positive_impulse"] if db_case else None
    
    # 4. UFC Reference manual
    ufc = ufc_manual_refs[Z]
    
    print("VALUES:")
    print(f"  Runtime Solver:      Pso = {runtime['incident_pressure']:.6f} kPa, Impulse = {runtime['positive_impulse']:.6f} kPa-ms")
    print(f"  Benchmark Gen:       Pso = {bench['incident_pressure']:.6f} kPa, Impulse = {bench['positive_impulse']:.6f} kPa-ms")
    print(f"  Validation DB:       Pso = {db_pso} kPa, Impulse = {db_imp} kPa-ms")
    print(f"  UFC Manual Ref:      Pso = {ufc['incident_pressure']} kPa, Impulse = {ufc['positive_impulse']} kPa-ms")
    
    # Let's compute percentages: (Runtime - Ref) / Ref * 100
    p_diff_bench = (runtime['incident_pressure'] - bench['incident_pressure']) / bench['incident_pressure'] * 100
    i_diff_bench = (runtime['positive_impulse'] - bench['positive_impulse']) / bench['positive_impulse'] * 100
    
    p_diff_ufc = (runtime['incident_pressure'] - ufc['incident_pressure']) / ufc['incident_pressure'] * 100
    i_diff_ufc = (runtime['positive_impulse'] - ufc['positive_impulse']) / ufc['positive_impulse'] * 100
    
    print("PERCENTAGE DISCREPANCIES (Runtime vs Others):")
    print(f"  vs Benchmark Gen:    Pso Diff = {p_diff_bench:.2f}%, Impulse Diff = {i_diff_bench:.2f}%")
    print(f"  vs UFC Manual Ref:   Pso Diff = {p_diff_ufc:.2f}%, Impulse Diff = {i_diff_ufc:.2f}%")
