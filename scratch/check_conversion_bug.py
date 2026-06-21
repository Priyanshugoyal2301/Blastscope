import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.blast_engine.models.brl_tr_2555_solver import calculate_brl_parameters_imperial

# We want to see what the BRL solver outputs in Imperial units at Z_english = 1, 2, 5, 10,
# and then convert those outputs to Metric using standard conversions.
PSI_TO_KPA = 6.89475729
TIME_SCALED_CONV = (0.45359237) ** (-1.0 / 3.0)
IMPULSE_SCALED_CONV = PSI_TO_KPA * TIME_SCALED_CONV

Z_vals = [1.0, 2.0, 5.0, 10.0]

print("--- CONWEP IMPERIAL EVALUATION AT Z_english = Z_metric (No Z_CONV scaling) ---")
for Z in Z_vals:
    imp = calculate_brl_parameters_imperial(Z, "Free Air")
    pso_metric = imp["incident_pressure"] * PSI_TO_KPA
    is_metric = imp["positive_impulse"] * IMPULSE_SCALED_CONV
    ta_metric = imp["arrival_time"] * TIME_SCALED_CONV
    to_metric = imp["positive_duration"] * TIME_SCALED_CONV
    
    print(f"Z_eng = {Z}: Pso = {pso_metric:.4f} kPa, Impulse = {is_metric:.4f} kPa-ms, ta = {ta_metric:.4f} ms, to = {to_metric:.4f} ms")
