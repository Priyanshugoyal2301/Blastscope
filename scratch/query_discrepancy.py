import sys
import os
import sqlite3
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

Z_vals = [1.0, 2.0, 5.0, 10.0]

print("--- RUNTIME SOLVER VALUES ---")
for Z in Z_vals:
    res = calculate_kb_parameters(Z, "Free Air")
    print(f"Z = {Z}: Pso = {res['incident_pressure']:.6f}, impulse = {res['positive_impulse']:.6f}, duration = {res['positive_duration']:.6f}, arrival = {res['arrival_time']:.6f}")

print("\n--- fig2_7_benchmark.csv (approximate metric curve) ---")
if os.path.exists("backend/validation/fig2_7_benchmark.csv"):
    with open("backend/validation/fig2_7_benchmark.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            z_val = float(row["scaled_distance"])
            # Match close to 1.0, 2.0, 5.0, 10.0
            for target in Z_vals:
                if abs(z_val - target) < 1e-4:
                    print(f"Z = {z_val}: Pso = {row['incident_pressure']}, impulse = {row['incident_impulse']}, duration = {row['positive_duration']}, arrival = {row['arrival_time']}")
else:
    print("fig2_7_benchmark.csv not found")

print("\n--- free_air_reference.csv (authentic ARL-TR-1310/CONWEP curve) ---")
if os.path.exists("backend/validation/free_air_reference.csv"):
    with open("backend/validation/free_air_reference.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            z_val = float(row["scaled_distance"])
            for target in Z_vals:
                if abs(z_val - target) < 1e-4:
                    print(f"Z = {z_val}: Pso = {row['incident_pressure']}, impulse = {row['incident_impulse']}, duration = {row['positive_duration']}, arrival = {row['arrival_time']}")
else:
    print("free_air_reference.csv not found")

print("\n--- DATABASE validation_cases TABLE ---")
if os.path.exists("backend/database/sqlite.db"):
    conn = sqlite3.connect("backend/database/sqlite.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases WHERE burst_type = 'Free Air'")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Z = {row['scaled_distance']}: Pso = {row['reference_pressure']}, impulse = {row['reference_impulse']}, source = {row['validation_source']}, page = {row['validation_page']}")
    conn.close()
else:
    print("sqlite.db not found")
