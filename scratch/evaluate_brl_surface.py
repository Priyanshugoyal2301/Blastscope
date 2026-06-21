import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.blast_engine.models.brl_tr_2555_solver import calculate_brl_parameters_metric

Z_vals = [1.0, 2.0, 5.0, 10.0]

for Z in Z_vals:
    print(f"\n==================== Z_metric = {Z} ====================")
    free_air = calculate_brl_parameters_metric(Z, "Free Air")
    surface = calculate_brl_parameters_metric(Z, "Surface")
    
    print(f"Free Air Burst: Pso = {free_air['incident_pressure']:.4f} kPa, Impulse = {free_air['positive_impulse']:.4f} kPa-ms")
    print(f"Surface Burst:  Pso = {surface['incident_pressure']:.4f} kPa, Impulse = {surface['positive_impulse']:.4f} kPa-ms")
