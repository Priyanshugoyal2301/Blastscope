"""
generate_qualification_dataset.py
=================================

Generates a large qualification dataset of 1,000,000 physically valid blast
scenarios for downstream ML surrogate model training.
For each sample, it computes primary, derived thermodynamic, and numerical
estimate parameters.
"""

import math
import csv
import json
import random
import os
import sys

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

def main():
    print("Generating Blast Qualification Dataset (1,000,000 samples)...")
    
    csv_path = "backend/validation/blast_qualification_dataset.csv"
    metadata_path = "backend/validation/blast_qualification_metadata.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Set seed for reproducibility
    random.seed(42)
    
    headers = [
        "sample_id", "burst_type", "charge_weight_kg", "standoff_distance_m",
        "scaled_distance_m_kg13", "incident_pressure_kPa", "reflected_pressure_kPa",
        "dynamic_pressure_kPa", "positive_impulse_scaled_kPa_ms",
        "reflected_impulse_scaled_kPa_ms", "positive_duration_scaled_ms",
        "negative_duration_scaled_ms", "arrival_time_scaled_ms",
        "shock_front_velocity_m_s", "particle_velocity_m_s", "decay_parameter"
    ]
    
    # We will write in chunks to be efficient and memory-safe
    chunk_size = 50000
    total_samples = 1000000
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for chunk_idx in range(total_samples // chunk_size):
            rows = []
            for i in range(chunk_size):
                sample_id = chunk_idx * chunk_size + i + 1
                
                # Sample burst type: 'Surface' or 'Free Air'
                burst_type = "Surface" if random.random() < 0.5 else "Free Air"
                
                # Sample weight log-uniformly in [0.1, 10000.0] kg
                log_w = random.uniform(math.log10(0.1), math.log10(10000.0))
                W = 10.0 ** log_w
                
                # Sample Z log-uniformly in [0.05, 40.0] m/kg^(1/3)
                # Note: validity limit is 0.05 <= Z <= 40.0
                log_z = random.uniform(math.log10(0.05), math.log10(40.0))
                Z = 10.0 ** log_z
                
                # Calculate standoff R = Z * W^(1/3)
                R = Z * (W ** (1.0 / 3.0))
                
                # Calculate physics parameters
                res = calculate_kb_parameters(Z, burst_type)
                
                rows.append([
                    sample_id,
                    burst_type,
                    round(W, 4),
                    round(R, 4),
                    round(Z, 5),
                    round(res["incident_pressure"], 4),
                    round(res["reflected_pressure"], 4),
                    round(res["dynamic_pressure"], 4),
                    round(res["positive_impulse"], 4),
                    round(res["reflected_impulse"], 4),
                    round(res["positive_duration"], 4),
                    round(res["negative_duration"], 4),
                    round(res["arrival_time"], 4),
                    round(res["shock_front_velocity"], 4),
                    round(res["particle_velocity"], 4),
                    round(res["decay_parameter"], 6)
                ])
                
            writer.writerows(rows)
            print(f"  Written {sample_id} / {total_samples} samples...")
            
    print("CSV generation completed.")
    
    # Save metadata JSON file
    metadata = {
        "dataset_name": "BlastScope 1M Scenario Scientific Qualification Dataset",
        "total_samples": total_samples,
        "physics_model": "Kingery-Bulmash (Swisdak 1994 piecewise polynomial curve fits)",
        "spherical_burst_equations": "SLSQP optimized continuous spherical polynomials (Sprint 3)",
        "hemispherical_burst_equations": "Official Swisdak (1994) Table 1 polynomials",
        "applicability_limits": {
            "scaled_distance_Z_min_m_kg13": 0.05,
            "scaled_distance_Z_max_m_kg13": 40.0,
            "charge_weight_W_min_kg": 0.1,
            "charge_weight_W_max_kg": 10000.0
        },
        "uncertainty_bounds": {
            "surface_burst_pressure_mean_error": "< 0.2%",
            "surface_burst_pressure_max_error": "< 1.2%",
            "surface_burst_impulse_mean_error": "< 0.1%",
            "surface_burst_impulse_max_error": "< 0.5%",
            "free_air_burst_pressure_mean_error": "< 2.5%",
            "free_air_burst_impulse_mean_error": "< 4.2%"
        },
        "parameter_classifications": {
            "direct_kingery_bulmash_parameters": [
                "incident_pressure_kPa", "reflected_pressure_kPa", 
                "positive_impulse_scaled_kPa_ms", "reflected_impulse_scaled_kPa_ms",
                "positive_duration_scaled_ms", "arrival_time_scaled_ms"
            ],
            "derived_thermodynamic_parameters": [
                "dynamic_pressure_kPa", "shock_front_velocity_m_s", "particle_velocity_m_s"
            ],
            "numerical_estimates": [
                "decay_parameter", "negative_duration_scaled_ms"
            ]
        },
        "environmental_constants": {
            "P0_ambient_pressure_kPa": 101.325,
            "C0_speed_of_sound_m_s": 340.292
        },
        "contact": "BlastScope Physics Engine Scientific Verification Group"
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    print("Metadata generation completed.")

if __name__ == "__main__":
    main()
