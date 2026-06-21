"""
generate_reference_benchmarks.py
================================

Generates independent (non-circular) benchmark CSV files for Surface and Free-Air bursts
using direct evaluations of the published coefficients:
  - Surface Burst: Swisdak (1994) Table 1 simplified polynomials.
  - Free-Air Burst: BRL-TR-2555 / CONWEP (1984) high-order imperial polynomials (ARL-TR-1310).

Saves outputs to backend/validation/surface_reference.csv and backend/validation/free_air_reference.csv.
"""

import math
import csv
import os

# ===========================================================================
#  SWISDAK (1994) COEFFICIENTS - SURFACE BURST (Metric)
# ===========================================================================
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

# ===========================================================================
#  BRL-TR-2555 / CONWEP COEFFICIENTS - FREE AIR (Imperial)
# ===========================================================================
CPSO_FREE_AIR = [
    1.77284970457, -1.69012801396, 0.00804973591951, 0.336743114941,
    -0.00516226351334, -0.0809228619888, -0.00478507266747, 0.00793030472242,
    0.0007684469735, 0.0, 0.0, 0.0
]

CFREE_PREF = [
    2.39106134946, -2.21400538997, 0.035119031446, 0.657599992109,
    0.0141818951887, -0.243076636231, -0.0158699803158, 0.0492741184234,
    0.00227639644004, -0.00397126276058
]

CFREE_TARR = [
    -0.0423733936826, 1.36456871214, -0.0570035692784, -0.182832224796,
    0.0118851436014, 0.0432648687627, -0.0007997367834, -0.00436073555033
]

CFREE_XIMPR = [
    1.60579280091, -0.903118886091, 0.101771877942, -0.0242139751146
]

CFREE_XIMPS_1 = [
    1.43534136453, -0.443749377691, 0.168825414684, 0.0348138030308, -0.010435192824
]
CFREE_XIMPS_2 = [
    0.599008468099, -0.40463292088, -0.0142721946082, 0.00912366316617,
    -0.0006750681404, -0.00800863718901, 0.00314819515931, 0.00152044783382,
    -0.0007470265899
]

CFREE_TDUR_1 = [
    -0.801052722864, 0.164953518069, 0.127788499497, 0.00291430135946,
    0.00187957449227, 0.0173413962543, 0.00269739758043, -0.00361976502798,
    -0.00100926577934
]
CFREE_TDUR_2 = [
    0.115874238335, -0.0297944268969, 0.0306329542941, 0.018340557407,
    -0.0173964666286, -0.00106321963576, 0.0056206003128, 0.0001618217499,
    -0.0006860188944
]
CFREE_TDUR_3 = [
    0.50659210403, 0.0967031995552, -0.00801302059667, 0.00482705779732,
    0.00187587272287, -0.00246738509321, -0.000841116668, 0.0006193291052
]

# Conversions
Z_CONV = (1.0 / 0.3048) / ((1.0 / 0.45359237) ** (1.0 / 3.0))
PSI_TO_KPA = 6.89475729
TIME_SCALED_CONV = (0.45359237) ** (-1.0 / 3.0)
IMPULSE_SCALED_CONV = PSI_TO_KPA * TIME_SCALED_CONV


def eval_poly_swisdak(coeffs, Z):
    u = math.log(Z)
    log_Y = sum(c * (u ** i) for i, c in enumerate(coeffs))
    return math.exp(log_Y)


def select_and_eval_swisdak(tables, Z):
    overall_min = tables[0][0]
    overall_max = tables[-1][1]
    Z_clamped = max(Z, overall_min)
    Z_clamped = min(Z_clamped, overall_max)
    for z_min, z_max, coeffs in tables:
        if z_min <= Z_clamped <= z_max:
            return eval_poly_swisdak(coeffs, Z_clamped)
    return eval_poly_swisdak(tables[-1][2], Z_clamped)


def eval_poly_horner(coeffs, u):
    val = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        val = val * u + c
    return val


def solve_decay_conwep(pso, impulse, duration):
    if impulse <= 0.0 or pso <= 0.0 or duration <= 0.0:
        return 0.0
    ptoi = pso * duration / impulse
    if ptoi <= 1.0:
        return 0.0
    a = ptoi - 1.0
    for _ in range(100):
        try:
            ea = math.exp(-a)
        except OverflowError:
            ea = 0.0
        fa = a * a - ptoi * (a + ea - 1.0)
        fpa = 2.0 * a - ptoi * (1.0 - ea)
        if abs(fpa) < 1e-12:
            break
        a_next = a - fa / fpa
        if abs(a_next - a) < 1e-7:
            a = a_next
            break
        a = a_next
    return max(0.0, a)


def main():
    validation_dir = "backend/validation"
    os.makedirs(validation_dir, exist_ok=True)
    
    # Z range values to evaluate
    z_values = []
    # Log spaced
    for i in range(100):
        z_values.append(0.05 * (40.0 / 0.05) ** (i / 99.0))
    # Standard integer/fractional check points
    checkpoints = [0.06, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.16, 1.17, 1.36, 1.39, 1.5, 1.86, 2.0, 2.12, 2.15, 2.17, 2.21, 2.3, 2.58, 3.0, 4.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0, 40.0]
    z_values.extend(checkpoints)
    z_values = sorted(list(set(z_values)))
    
    # 1. Surface burst benchmark generation (Swisdak Table 1 simplified metric)
    surface_path = os.path.join(validation_dir, "surface_reference.csv")
    with open(surface_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scaled_distance", "incident_pressure", "reflected_pressure",
            "incident_impulse", "reflected_impulse", "arrival_time",
            "positive_duration", "dynamic_pressure", "shock_front_velocity",
            "particle_velocity", "decay_parameter", "negative_duration",
            "source", "page", "table", "figure", "digitization_method"
        ])
        for Z in z_values:
            if Z < 0.06:
                continue
            
            pso = select_and_eval_swisdak(SURFACE_INCIDENT_PRESSURE, Z)
            pr = select_and_eval_swisdak(SURFACE_REFLECTED_PRESSURE, Z)
            is_scaled = select_and_eval_swisdak(SURFACE_INCIDENT_IMPULSE, Z)
            ir_scaled = select_and_eval_swisdak(SURFACE_REFLECTED_IMPULSE, Z)
            ta = select_and_eval_swisdak(SURFACE_ARRIVAL_TIME, Z)
            to = select_and_eval_swisdak(SURFACE_POSITIVE_DURATION, Z)
            
            # Rankine-Hugoniot
            P0 = 101.325
            C0 = 340.292
            q = 2.5 * (pso ** 2) / (7.0 * P0 + pso) if pso > 0 else 0.0
            u = C0 * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0)) if pso > 0 else C0
            up = (5.0 * C0 * pso) / (7.0 * P0 * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0))) if pso > 0 else 0.0
            
            # Decay solver
            b = solve_decay_conwep(pso, is_scaled, to) if pso > 0 else 0.0
            td_neg = to * (1.0 + 1.0 / b) if b > 0 else to * 1.5
            
            writer.writerow([
                Z, pso, pr, is_scaled, ir_scaled, ta, to, q, u, up, b, td_neg,
                "Swisdak (1994)", "DTIC ADA526744 Page 12", "Table 1", "N/A", "Direct Polynomial Evaluation"
            ])
            
    # 2. Free Air burst benchmark generation (BRL-TR-2555 / CONWEP high-order imperial)
    free_air_path = os.path.join(validation_dir, "free_air_reference.csv")
    with open(free_air_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "scaled_distance", "incident_pressure", "reflected_pressure",
            "incident_impulse", "reflected_impulse", "arrival_time",
            "positive_duration", "dynamic_pressure", "shock_front_velocity",
            "particle_velocity", "decay_parameter", "negative_duration",
            "source", "page", "table", "figure", "digitization_method"
        ])
        for Z in z_values:
            # Air burst curves valid for Z_imp >= 0.148 (which corresponds to Z_metric = 0.0587)
            if Z < 0.0587:
                continue
            
            # Convert to imperial Z
            Z_imp = Z * Z_CONV
            zlog = math.log10(Z_imp)
            
            # Pso
            u_pso = -0.756579301809 + 1.35034249993 * zlog
            pso_imp = 10.0 ** eval_poly_horner(CPSO_FREE_AIR, u_pso)
            
            # Pr
            u_pr = -0.756579301809 + 1.35034249993 * zlog
            pr_imp = 10.0 ** eval_poly_horner(CFREE_PREF, u_pr)
            
            # Arrival Time ta
            u_ta = -0.80501734056 + 1.37407043777 * zlog
            ta_imp = 10.0 ** eval_poly_horner(CFREE_TARR, u_ta)
            
            # Reflected Impulse ir
            u_ir = -0.757659920369 + 1.37882996018 * zlog
            ir_imp = 10.0 ** eval_poly_horner(CFREE_XIMPR, u_ir)
            
            # Incident Impulse is
            if zlog < 0.30103:
                u_is = 1.04504877747 + 3.24299066475 * zlog
                coeffs_is = CFREE_XIMPS_1
            else:
                u_is = -2.67912519532 + 2.30629231803 * zlog
                coeffs_is = CFREE_XIMPS_2
            is_imp = 10.0 ** eval_poly_horner(coeffs_is, u_is)
            
            # Duration to
            if zlog < -0.34:
                to_log = -0.824
            elif zlog < 0.350248:
                u_to = 0.209440059933 + 5.11588554305 * zlog
                to_log = eval_poly_horner(CFREE_TDUR_1, u_to)
            elif zlog < 0.7596678:
                u_to = -5.06778493835 + 9.2996288611 * zlog
                to_log = eval_poly_horner(CFREE_TDUR_2, u_to)
            else:
                u_to = -4.39590184126 + 3.1524725264 * zlog
                to_log = eval_poly_horner(CFREE_TDUR_3, u_to)
            to_imp = 10.0 ** to_log
            
            # Adjust duration and solve decay
            zlo = 0.37
            if Z_imp >= zlo:
                if (pso_imp * to_imp / is_imp <= 2.5) or (pr_imp * to_imp / ir_imp <= 2.5):
                    to_imp = 2.5 * max(is_imp / pso_imp, ir_imp / pr_imp)
                a = solve_decay_conwep(pso_imp, is_imp, to_imp)
            else:
                if (pso_imp * to_imp / is_imp <= 2.0) or (pr_imp * to_imp / ir_imp <= 2.0):
                    to_imp = 2.0 * max(is_imp / pso_imp, ir_imp / pr_imp)
                a = 0.0
            
            # Derived parameters (Rankine-Hugoniot)
            q_imp = 2.5 * (pso_imp ** 2) / (7.0 * 14.696 + pso_imp)
            u_imp = 1116.0 * math.sqrt(1.0 + 6.0 * pso_imp / (7.0 * 14.696))
            up_imp = (5.0 * 1116.0 * pso_imp) / (7.0 * 14.696 * math.sqrt(1.0 + 6.0 * pso_imp / (7.0 * 14.696)))
            td_neg_imp = to_imp * (1.0 + 1.0 / a) if a > 0 else to_imp * 1.5
            
            # Convert to Metric
            pso_metric = pso_imp * PSI_TO_KPA
            pr_metric = pr_imp * PSI_TO_KPA
            is_metric = is_imp * IMPULSE_SCALED_CONV
            ir_metric = ir_imp * IMPULSE_SCALED_CONV
            ta_metric = ta_imp * TIME_SCALED_CONV
            to_metric = to_imp * TIME_SCALED_CONV
            q_metric = q_imp * PSI_TO_KPA
            u_metric = u_imp * 0.3048
            up_metric = up_imp * 0.3048
            td_neg_metric = td_neg_imp * TIME_SCALED_CONV
            
            writer.writerow([
                Z, pso_metric, pr_metric, is_metric, ir_metric, ta_metric, to_metric,
                q_metric, u_metric, up_metric, a, td_neg_metric,
                "ARL-TR-1310 / BRL-TR-02555", "Appendix A", "conwep-brl / conwep-pref", "UFC Figure 2-7", "Direct Polynomial Evaluation"
            ])
            
    print("Independent references generated successfully:")
    print(f"  {surface_path}")
    print(f"  {free_air_path}")


if __name__ == "__main__":
    main()
