"""
dataset_certification.py
========================

Generates the qualified machine-learning training dataset blast_certified_dataset.csv
and the accompanying metadata file blast_certified_metadata.json using log-uniform
sampling of Z (0.05 - 40.0) and W (0.1 - 10000.0 kg).
"""

import os
import sys
import csv
import json
import random
import math

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

def main():
    print("=" * 80)
    print("BlastScope Dataset Certification Runner")
    print("=" * 80)
    
    # Set seed for reproducibility
    random.seed(42)
    
    total_samples = 100000
    print(f"Generating {total_samples} certified samples...")
    
    csv_path = "backend/validation/blast_certified_dataset.csv"
    json_path = "backend/validation/blast_certified_metadata.json"
    
    headers = [
        "sample_id", "burst_type", "charge_weight_kg", "standoff_distance_m",
        "scaled_distance_m_kg13", "incident_pressure_kPa", "reflected_pressure_kPa",
        "dynamic_pressure_kPa", "incident_impulse_scaled_kPa_ms",
        "reflected_impulse_scaled_kPa_ms", "positive_duration_scaled_ms",
        "negative_duration_scaled_ms", "arrival_time_scaled_ms",
        "shock_front_velocity_m_s", "particle_velocity_m_s", "decay_parameter"
    ]
    
    # Generate log-uniform samples
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(total_samples):
            sample_id = i + 1
            burst_type = "Surface" if random.random() < 0.5 else "Free Air"
            
            # W log-uniform in [0.1, 10000.0]
            log_w = random.uniform(math.log10(0.1), math.log10(10000.0))
            W = 10.0 ** log_w
            
            # Z log-uniform in [0.05, 40.0]
            log_z = random.uniform(math.log10(0.05), math.log10(40.0))
            Z = 10.0 ** log_z
            
            # R = Z * W^(1/3)
            R = Z * (W ** (1.0 / 3.0))
            
            # Compute parameters
            res = calculate_kb_parameters(Z, burst_type)
            
            writer.writerow([
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
            
            if (i + 1) % 20000 == 0:
                print(f"  Generated {i + 1} / {total_samples} samples...")
                
    print(f"CSV dataset generated successfully at: {csv_path}")
    
    # Save the JSON metadata file detailing every field record
    metadata = {
        "dataset_info": {
            "dataset_name": "BlastScope Certified Forward Physics Dataset",
            "description": "Certified blast parameter dataset for surrogate-model training, generated via log-uniform sampling of scaled distance Z and charge weight W.",
            "total_samples": total_samples,
            "applicable_range": {
                "scaled_distance_Z": "0.05 to 40.0 m/kg^(1/3)",
                "charge_weight_W": "0.1 to 10000.0 kg"
            }
        },
        "environmental_constants": {
            "ambient_pressure_kPa": 101.325,
            "speed_of_sound_m_s": 340.292
        },
        "fields": {
            "sample_id": {
                "equation": "N/A",
                "source_document": "N/A",
                "page": "N/A",
                "table": "N/A",
                "units": "dimensionless",
                "validity_range": "1 to 100000"
            },
            "burst_type": {
                "equation": "N/A",
                "source_document": "N/A",
                "page": "N/A",
                "table": "N/A",
                "units": "categorical",
                "validity_range": "Surface, Free Air"
            },
            "charge_weight_kg": {
                "equation": "N/A",
                "source_document": "N/A",
                "page": "N/A",
                "table": "N/A",
                "units": "kg",
                "validity_range": "0.1 to 10000.0"
            },
            "standoff_distance_m": {
                "equation": "R = Z * W^(1/3)",
                "source_document": "UFC 3-340-02",
                "page": "Chapter 2",
                "table": "N/A",
                "units": "m",
                "validity_range": "Dependent on W and Z"
            },
            "scaled_distance_m_kg13": {
                "equation": "Z = R / W^(1/3)",
                "source_document": "UFC 3-340-02",
                "page": "Chapter 2",
                "table": "N/A",
                "units": "m/kg^(1/3)",
                "validity_range": "0.05 to 40.0"
            },
            "incident_pressure_kPa": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwep-brl [Free Air]",
                "units": "kPa",
                "validity_range": "Z >= 0.20 [Surface], Z >= 0.0587 [Free Air]"
            },
            "reflected_pressure_kPa": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwep-pref [Free Air]",
                "units": "kPa",
                "validity_range": "Z >= 0.06 [Surface], Z >= 0.0587 [Free Air]"
            },
            "dynamic_pressure_kPa": {
                "equation": "Q = 2.5 * Pso^2 / (7 * P0 + Pso)",
                "source_document": "UFC 3-340-02",
                "page": "Eq. 2-4",
                "table": "N/A",
                "units": "kPa",
                "validity_range": "Derived from incident_pressure"
            },
            "incident_impulse_scaled_kPa_ms": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwep-ximps [Free Air]",
                "units": "kPa-ms/kg^(1/3)",
                "validity_range": "Z >= 0.20 [Surface], Z >= 0.0587 [Free Air]"
            },
            "reflected_impulse_scaled_kPa_ms": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwep-ximpr [Free Air]",
                "units": "kPa-ms/kg^(1/3)",
                "validity_range": "Z >= 0.06 [Surface], Z >= 0.0587 [Free Air]"
            },
            "positive_duration_scaled_ms": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwepjtdur [Free Air]",
                "units": "ms/kg^(1/3)",
                "validity_range": "Z >= 0.20 [Surface], Z >= 0.0587 [Free Air]"
            },
            "negative_duration_scaled_ms": {
                "equation": "td- = td * (1 + 1/b)",
                "source_document": "UFC 3-340-02 / Standard Physics",
                "page": "Chapter 2",
                "table": "N/A",
                "units": "ms/kg^(1/3)",
                "validity_range": "Derived from positive_duration and decay_parameter"
            },
            "arrival_time_scaled_ms": {
                "equation": "Y = exp(A + B*ln(Z) + ...) [Surface], Y = 10^(sum(C_i * u^i)) [Free Air]",
                "source_document": "Swisdak (1994) [Surface], ARL-TR-1310 [Free Air]",
                "page": "Page 12 [Surface], Appendix A [Free Air]",
                "table": "Table 1 [Surface], conwep-tarr [Free Air]",
                "units": "ms/kg^(1/3)",
                "validity_range": "Z >= 0.06 [Surface], Z >= 0.0587 [Free Air]"
            },
            "shock_front_velocity_m_s": {
                "equation": "U = C0 * sqrt(1 + 6 * Pso / (7 * P0))",
                "source_document": "UFC 3-340-02",
                "page": "Eq. 2-2",
                "table": "N/A",
                "units": "m/s",
                "validity_range": "Derived from incident_pressure"
            },
            "particle_velocity_m_s": {
                "equation": "up = 5 * C0 * Pso / (7 * P0 * sqrt(1 + 6 * Pso / (7 * P0)))",
                "source_document": "UFC 3-340-02",
                "page": "Eq. 2-3",
                "table": "N/A",
                "units": "m/s",
                "validity_range": "Derived from incident_pressure"
            },
            "decay_parameter": {
                "equation": "is / (Pso * td) = (b - 1 + e^-b) / b^2",
                "source_document": "UFC 3-340-02 / Standard Physics",
                "page": "Chapter 2",
                "table": "N/A",
                "units": "dimensionless",
                "validity_range": "Numerical solver output"
            }
        }
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"JSON metadata generated successfully at: {json_path}")
    
    # Copy both files to the absolute artifacts directory
    artifacts_dir = r"C:\Users\Priyanshu Goyal\.gemini\antigravity-ide\brain\2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c"
    import shutil
    shutil.copy2(csv_path, os.path.join(artifacts_dir, "blast_certified_dataset.csv"))
    shutil.copy2(json_path, os.path.join(artifacts_dir, "blast_certified_metadata.json"))
    print(f"Certified files copied to artifacts folder.")


if __name__ == "__main__":
    main()
