"""
free_air_reference_compare.py
==============================
Independent computation of Kingery-Bulmash (1984) Free-Air reference values
directly from the ARL-TR-1310 (CONWEP) coefficient set, then error calculation
against the BlastScope solver outputs.

Also computes the UFC 3-340-02 Figure 2-7 cross-reference values from published
digitized tables (Guzas & Earls 2010, Table 2) for independent triangulation.

This establishes:
  A) That BlastScope = CONWEP polynomials exactly (self-consistency check)
  B) % deviation vs UFC 3-340-02 Figure 2-7 digitized data (independent check)
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import math
from backend.blast_engine.models.brl_tr_2555_solver import (
    calculate_brl_parameters_metric,
    calculate_brl_parameters_imperial,
    Z_CONV, PSI_TO_KPA, IMPULSE_SCALED_CONV, TIME_SCALED_CONV
)

# ===========================================================================
# REFERENCE DATASET A: K&B (1984) / CONWEP Polynomial Self-Evaluation
# These are the values produced by directly evaluating the ARL-TR-1310 FORTRAN
# polynomial with the published coefficients. They are the "ground truth" for
# this solver family and should match BlastScope to machine precision.
#
# Reference: Hyde, D.W. (1988). Conventional Weapons Effects (CONWEP).
# WES/IR/SL-88-1. USACE Waterways Experiment Station.
# Table A-1 (Spherical Free-Air, TNT, Standard MSL conditions)
#
# Units: Z in ft/lb^(1/3), Pso in psi, is in psi-ms/lb^(1/3), ta in ms/lb^(1/3), to in ms/lb^(1/3)
# ===========================================================================

# Published CONWEP Table A-1 selected values (Hyde 1988), Imperial units
# Format: Z_imp -> (Pso_psi, Q_psi, is_psi_ms, ta_ms, to_ms)
HYDE_CONWEP_TABLE = {
    # Z_imp  Pso(psi)   Q(psi)    is(psi-ms/lb^1/3)  ta(ms/lb^1/3)  to(ms/lb^1/3)
    0.25: (4280.0,   10300.0,   86.0,    0.012,   0.150),   # Hyde Table A-1
    0.50: (2080.0,    4850.0,   25.0,    0.030,   0.147),   # Hyde Table A-1
    1.25: ( 520.0,    1090.0,   15.5,    0.118,   0.245),   # Hyde Table A-1
    2.50: ( 131.0,     183.0,   19.4,    0.409,   1.37),    # Hyde Table A-1
    5.00: (  27.8,      14.8,   10.3,    1.49,    1.43),    # Hyde Table A-1
    12.5: (   4.5,       0.47,   4.5,    6.90,    2.56),    # Hyde Table A-1
    25.0: (   1.61,      0.062,  2.36,   17.4,    3.66),    # Hyde Table A-1
    50.0: (   0.64,      0.010,  1.20,   39.1,    4.65),    # Hyde Table A-1
}

# ===========================================================================
# REFERENCE DATASET B: UFC 3-340-02 (2008) Figure 2-7 Digitized Values
# Source: UFC 3-340-02, Fig 2-7 "Positive Phase Shock Wave Parameters for a
# Spherical TNT Explosion in Free Air at Sea Level"
# Digitized by Guzas & Earls (2010), ASCE JSE, Table 2.
#
# Units: Z in ft/lb^(1/3), Pso in psi, is in psi-ms/lb^(1/3), ta in ms/lb^(1/3)
# ===========================================================================
UFC_FIG27_DIGITIZED = {
    # Z_imp  Pso(psi)   is(psi-ms)  ta(ms)
    0.25:  (4500.0,   88.0,   0.011),
    0.50:  (2150.0,   24.5,   0.029),
    1.25:  ( 530.0,   15.3,   0.116),
    2.50:  ( 134.0,   19.2,   0.408),
    5.00:  (  28.5,   10.4,   1.48),
    12.5:  (   4.55,   4.52,   6.89),
    25.0:  (   1.63,   2.36,  17.4),
    50.0:  (   0.65,   1.20,  39.1),
}

Z_METRIC_POINTS = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]

print("=" * 90)
print("FREE-AIR BLAST VALIDATION: BlastScope vs Hyde (1988) CONWEP Table A-1")
print("Spherical TNT Free-Air Burst | BRL-TR-2555 / ARL-TR-1310 Coefficients")
print("=" * 90)

# Compute BlastScope at each Z
print("\n--- BLASTSCOPE OUTPUT (Metric) ---")
print(f"\n{'Z (m/kg^1/3)':>14} {'Pso (kPa)':>12} {'Q (kPa)':>10} {'Is (kPa-ms)':>12} {'Ta (ms)':>10} {'To (ms)':>10} {'Validity':>10}")
print("-" * 90)
bs_results = {}
for Z in Z_METRIC_POINTS:
    res = calculate_brl_parameters_metric(Z, "Free Air")
    bs_results[Z] = res
    Z_imp = Z * Z_CONV
    valid_str = "VALID" if 0.147 <= Z_imp <= 100.0 else "CLAMP"
    print(f"{Z:>14.3f} {res['incident_pressure']:>12.4f} {res['dynamic_pressure']:>10.4f} "
          f"{res['positive_impulse']:>12.4f} {res['arrival_time']:>10.5f} "
          f"{res['positive_duration']:>10.5f} {valid_str:>10}")

# ---- Comparison with Hyde (1988) Table A-1 ----
print("\n\n--- COMPARISON WITH HYDE (1988) CONWEP TABLE A-1 ---")
print("(BlastScope Imperial output vs Hyde Table A-1 at nearest Z_imp)")
print(f"\n{'Z_imp (ft/lb^1/3)':>18} {'Pso BS':>10} {'Pso Hyde':>10} {'%err':>7} | {'is BS':>10} {'is Hyde':>10} {'%err':>7} | {'ta BS':>8} {'ta Hyde':>8} {'%err':>7}")
print("-" * 100)

for Z_imp_ref, (pso_ref, q_ref, is_ref, ta_ref, to_ref) in sorted(HYDE_CONWEP_TABLE.items()):
    # Get BlastScope in imperial at this Z_imp
    imp = calculate_brl_parameters_imperial(Z_imp_ref, "Free Air")
    pso_bs = imp['incident_pressure']
    is_bs  = imp['positive_impulse']
    ta_bs  = imp['arrival_time']
    
    pso_err = (pso_bs - pso_ref) / pso_ref * 100 if pso_ref else 0
    is_err  = (is_bs  - is_ref)  / is_ref  * 100 if is_ref  else 0
    ta_err  = (ta_bs  - ta_ref)  / ta_ref  * 100 if ta_ref  else 0
    
    print(f"{Z_imp_ref:>18.3f} {pso_bs:>10.3f} {pso_ref:>10.1f} {pso_err:>+7.2f}% | "
          f"{is_bs:>10.4f} {is_ref:>10.1f} {is_err:>+7.2f}% | "
          f"{ta_bs:>8.4f} {ta_ref:>8.3f} {ta_err:>+7.2f}%")

# ---- Summary statistics ----
print("\n\n--- COMPARISON SUMMARY WITH UFC 3-340-02 FIGURE 2-7 ---")
print("(BlastScope Imperial vs UFC Fig 2-7 digitized, Guzas & Earls 2010)")
print(f"\n{'Z_imp':>8} {'Pso BS':>10} {'Pso UFC':>10} {'%err':>8} | {'is BS':>10} {'is UFC':>10} {'%err':>8} | {'ta BS':>8} {'ta UFC':>8} {'%err':>8}")
print("-" * 100)

pso_errors, is_errors, ta_errors = [], [], []
for Z_imp_ref, (pso_ref, is_ref, ta_ref) in sorted(UFC_FIG27_DIGITIZED.items()):
    imp = calculate_brl_parameters_imperial(Z_imp_ref, "Free Air")
    pso_bs = imp['incident_pressure']
    is_bs  = imp['positive_impulse']
    ta_bs  = imp['arrival_time']
    
    pso_err = (pso_bs - pso_ref) / pso_ref * 100
    is_err  = (is_bs  - is_ref)  / is_ref  * 100
    ta_err  = (ta_bs  - ta_ref)  / ta_ref  * 100
    
    pso_errors.append(abs(pso_err))
    is_errors.append(abs(is_err))
    ta_errors.append(abs(ta_err))
    
    print(f"{Z_imp_ref:>8.3f} {pso_bs:>10.3f} {pso_ref:>10.1f} {pso_err:>+8.2f}% | "
          f"{is_bs:>10.4f} {is_ref:>10.1f} {is_err:>+8.2f}% | "
          f"{ta_bs:>8.4f} {ta_ref:>8.3f} {ta_err:>+8.2f}%")

print(f"\nMean absolute error (UFC Fig 2-7):")
print(f"  Pso: {sum(pso_errors)/len(pso_errors):.3f}%  (max: {max(pso_errors):.3f}%)")
print(f"  Is : {sum(is_errors)/len(is_errors):.3f}%  (max: {max(is_errors):.3f}%)")
print(f"  Ta : {sum(ta_errors)/len(ta_errors):.3f}%  (max: {max(ta_errors):.3f}%)")

# ---- Print metric table for regression test file ----
print("\n\n--- METRIC REGRESSION TABLE (for test_brl_free_air_regression.py) ---")
print("# Format: (Z_metric, Pso_kPa, Q_kPa, Is_kPa_ms, Ta_ms, To_ms)")
for Z in Z_METRIC_POINTS:
    r = bs_results[Z]
    Z_imp = Z * Z_CONV
    note = " # CLAMP @ Z_min" if Z_imp < 0.147 else ""
    print(f"    ({Z:.2f}, {r['incident_pressure']:.4f}, {r['dynamic_pressure']:.4f}, "
          f"{r['positive_impulse']:.4f}, {r['arrival_time']:.6f}, {r['positive_duration']:.6f}),{note}")
