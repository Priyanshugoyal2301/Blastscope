"""
physics_certification.py
========================

Validates the BlastScope forward blast solver against independent benchmarks.
Asserts that implementation reproduction error is strictly < 0.01% mean relative error.
"""

import os
import sys
import csv
import math

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

def run_verification(filepath, burst_type):
    print(f"\nEvaluating {burst_type} Burst against {os.path.basename(filepath)}...")
    
    if not os.path.exists(filepath):
        print(f"Error: reference file not found: {filepath}")
        return False
        
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        
    parameters = [
        ("incident_pressure", "incident_pressure"),
        ("reflected_pressure", "reflected_pressure"),
        ("positive_impulse", "incident_impulse"),
        ("reflected_impulse", "reflected_impulse"),
        ("arrival_time", "arrival_time"),
        ("positive_duration", "positive_duration"),
        ("dynamic_pressure", "dynamic_pressure"),
        ("shock_front_velocity", "shock_front_velocity"),
        ("particle_velocity", "particle_velocity"),
        ("decay_parameter", "decay_parameter"),
        ("negative_duration", "negative_duration"),
    ]
    
    stats = {key: [] for key, _ in parameters}
    
    for row in rows:
        Z = float(row["scaled_distance"])
        res = calculate_kb_parameters(Z, burst_type)
        
        for key, ref_col in parameters:
            ref_val = float(row[ref_col])
            calc_val = res[key]
            
            # Avoid division by zero
            if ref_val == 0.0:
                err = 0.0 if calc_val == 0.0 else 100.0
            else:
                err = (abs(calc_val - ref_val) / ref_val) * 100.0
                
            stats[key].append(err)
            
    print(f"{'Parameter':<25} | {'Mean Err %':<12} | {'Max Err %':<12} | {'RMSE %':<12} | {'Status':<8}")
    print("-" * 75)
    
    all_passed = True
    for key, _ in parameters:
        errors = stats[key]
        n = len(errors)
        if n == 0:
            continue
        mean_err = sum(errors) / n
        max_err = max(errors)
        rmse_err = math.sqrt(sum(e**2 for e in errors) / n)
        
        # Target: Mean Error < 0.01% (0.0001 fraction), Max Error < 0.05%
        # Let's allow slightly higher tolerance for secondary numerical estimates (like decay and negative duration)
        # where numerical solver convergence might introduce tiny noise, but keep it very tight.
        limit_mean = 0.01
        limit_max = 0.05
        
        status = "PASS"
        if mean_err >= limit_mean or max_err >= limit_max:
            status = "FAIL"
            all_passed = False
            
        print(f"{key:<25} | {mean_err:10.6f}% | {max_err:10.6f}% | {rmse_err:10.6f}% | {status}")
        
    return all_passed

def main():
    print("=" * 80)
    print("BlastScope Physics Engine Certification & Validation Runner")
    print("=" * 80)
    
    surface_csv = "backend/validation/surface_reference.csv"
    free_air_csv = "backend/validation/free_air_reference.csv"
    
    surface_ok = run_verification(surface_csv, "Surface")
    free_air_ok = run_verification(free_air_csv, "Free Air")
    
    print("\n" + "=" * 80)
    print("Verification Summary:")
    print(f"  Surface Burst Status:  {'PASSED' if surface_ok else 'FAILED'}")
    print(f"  Free-Air Burst Status: {'PASSED' if free_air_ok else 'FAILED'}")
    print("=" * 80)
    
    if surface_ok and free_air_ok:
        print("Certification Status: SUCCESS")
        sys.exit(0)
    else:
        print("Certification Status: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
