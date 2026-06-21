"""
Kingery-Bulmash Blast Parameter Calculator
==========================================

Implements the Swisdak (1994) simplified polynomial curve fits for
hemispherical TNT surface bursts, based on the original Kingery & Bulmash
(1984) compilation (ARBRL-TR-02555).

Delegates Spherical Free-Air bursts to the authentic reference-grade
BRL-TR-2555 / ConWep solver.

Validity Bounds — Swisdak (1994) Hemispherical Surface Burst
------------------------------------------------------------
The following minimum scaled distances apply per Table 1 of Swisdak (1994):
  Pso (Incident Pressure)     : Z_min = 0.20 m/kg^(1/3)
  is  (Incident Impulse)      : Z_min = 0.20 m/kg^(1/3)
  to  (Positive Duration)     : Z_min = 0.20 m/kg^(1/3)
  Pr  (Reflected Pressure)    : Z_min = 0.06 m/kg^(1/3)
  ir  (Reflected Impulse)     : Z_min = 0.06 m/kg^(1/3)
  ta  (Arrival Time)          : Z_min = 0.06 m/kg^(1/3)

Requesting a value below these bounds will emit a warning to stderr and
return the value evaluated at the lower validity bound (clamped).
"""

import math
import sys
import warnings
from typing import List, Tuple
from backend.blast_engine.models.brl_tr_2555_solver import calculate_brl_parameters_metric


# ===========================================================================
#  VALIDITY BOUNDS — Swisdak (1994) Table 1 Minimum Scaled Distances (Metric)
# ===========================================================================
SURFACE_VALIDITY_BOUNDS = {
    # Parameter name       : (z_min, z_max)
    "incident_pressure":    (0.20, 198.5),
    "incident_impulse":     (0.20, 158.7),
    "positive_duration":    (0.20,  40.0),
    "reflected_pressure":   (0.06,  40.0),
    "reflected_impulse":    (0.06,  40.0),
    "arrival_time":         (0.06,  40.0),
}


# ===========================================================================
#  SWISDAK (1994) COEFFICIENT TABLES — HEMISPHERICAL SURFACE BURST (Metric)
#  Source: DTIC ADA526744, Table 1 (Metric coefficients)
# ===========================================================================

# Incident Peak Overpressure Pso (kPa)
SURFACE_INCIDENT_PRESSURE = [
    (0.20,  2.90,  [7.2106, -2.1069, -0.3229,  0.1117,  0.0685,  0.0,     0.0]),
    (2.90, 23.80,  [7.5938, -3.0523,  0.40977, 0.0261, -0.01267, 0.0,     0.0]),
    (23.80, 198.5, [6.0536, -1.4066,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

# Reflected Peak Pressure Pr (kPa)
SURFACE_REFLECTED_PRESSURE = [
    (0.06,  2.00,  [9.0060, -2.6893, -0.6295,  0.1011,  0.29255, 0.13505, 0.019736]),
    (2.00, 40.00,  [8.8396, -1.7330, -2.6400,  2.2930, -0.8232,  0.14247,-0.0099]),
]

# Incident Impulse is/W^{1/3} (kPa·ms/kg^{1/3})
SURFACE_INCIDENT_IMPULSE = [
    (0.20,  0.96,  [5.5220,  1.1170,  0.6000, -0.2920, -0.0870,  0.0,    0.0]),
    (0.96,  2.38,  [5.4650, -0.3080, -1.4640,  1.3620, -0.4320,  0.0,    0.0]),
    (2.38, 33.70,  [5.2749, -0.4677, -0.2499,  0.0588, -0.00554, 0.0,    0.0]),
    (33.70, 158.7, [5.9825, -1.0620,  0.0,     0.0,     0.0,     0.0,    0.0]),
]

# Reflected Impulse ir/W^{1/3} (kPa·ms/kg^{1/3})
SURFACE_REFLECTED_IMPULSE = [
    (0.06, 40.00,  [6.7853, -1.3466,  0.1010, -0.01123, 0.0,     0.0,    0.0]),
]

# Arrival Time ta/W^{1/3} (ms/kg^{1/3})
SURFACE_ARRIVAL_TIME = [
    (0.06,  1.50,  [-0.7604, 1.8058,  0.1257, -0.0437, -0.0310, -0.00669, 0.0]),
    (1.50, 40.00,  [-0.7137, 1.5732,  0.5561, -0.4213,  0.1054, -0.00929, 0.0]),
]

# Positive Phase Duration to/W^{1/3} (ms/kg^{1/3})
SURFACE_POSITIVE_DURATION = [
    (0.20,  1.02,  [0.5426,  3.2299, -1.5931, -5.9667, -4.0815, -0.9149,  0.0]),
    (1.02,  2.80,  [0.5440,  2.7082, -9.7354, 14.3425, -9.7791,  2.8535,  0.0]),
    (2.80, 40.00,  [-2.4608, 7.1639, -5.6215,  2.2711, -0.44994, 0.03486, 0.0]),
]


def _eval_swisdak_polynomial(coeffs: List[float], Z: float) -> float:
    """Evaluates a Swisdak (1994) simplified polynomial."""
    U = math.log(Z)  # natural logarithm per Swisdak (1994)
    log_Y = 0.0
    for i, c in enumerate(coeffs):
        log_Y += c * (U ** i)
    return math.exp(log_Y)


def _select_and_eval(tables: list, Z: float) -> float:
    """Selects the appropriate piecewise polynomial range for scaled distance Z and evaluates it."""
    overall_min = tables[0][0]
    overall_max = tables[-1][1]
    Z_clamped = max(Z, overall_min)
    Z_clamped = min(Z_clamped, overall_max)
    
    for z_min, z_max, coeffs in tables:
        if z_min <= Z_clamped <= z_max:
            return _eval_swisdak_polynomial(coeffs, Z_clamped)
            
    return _eval_swisdak_polynomial(tables[-1][2], Z_clamped)


def solve_decay_parameter(pso: float, impulse: float, duration: float) -> float:
    """Solves decay parameter 'b' using Newton-Raphson method."""
    if impulse <= 0.0 or pso <= 0.0 or duration <= 0.0:
        return 0.0
    k = impulse / (pso * duration)
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


def _warn_if_out_of_bounds(Z: float, param: str) -> None:
    """
    Emits a validity warning to stderr if Z is below the minimum valid
    scaled distance for a given Swisdak (1994) Table 1 surface burst parameter.
    """
    if param not in SURFACE_VALIDITY_BOUNDS:
        return
    z_min, z_max = SURFACE_VALIDITY_BOUNDS[param]
    if Z < z_min:
        msg = (
            f"[BlastScope Validity Warning] Scaled distance Z = {Z:.4f} m/kg^(1/3) is "
            f"below the minimum valid range for '{param}' "
            f"(Swisdak 1994 Table 1: Z_min = {z_min:.2f} m/kg^(1/3)). "
            f"Parameter will be evaluated at the lower validity bound (Z = {z_min:.2f})."
        )
        warnings.warn(msg, UserWarning, stacklevel=3)
        sys.stderr.write(f"WARNING: {msg}\n")
        sys.stderr.flush()


def calculate_kb_parameters(scaled_distance: float, burst_type: str) -> dict:
    """
    Computes blast wave parameters using the Swisdak (1994) simplified
    polynomial curve fits for Surface burst, and delegates to the authentic
    BRL-TR-2555 solver for Free-Air burst.

    For Surface burst, emits a UserWarning (and stderr message) if the
    requested Z is below the minimum valid range for any parameter per
    Swisdak (1994) Table 1. The parameter will be evaluated at its lower
    validity bound (clamping).

    Valid Swisdak (1994) Surface Burst Ranges:
        Pso, is, to : Z >= 0.20 m/kg^(1/3)
        Pr, ir, ta  : Z >= 0.06 m/kg^(1/3)
    """
    Z = max(scaled_distance, 0.05)

    if burst_type in ["Free Air", "Air"]:
        # Delegate to the authentic BRL-TR-2555 solver
        # Valid range: Z >= 0.0587 m/kg^(1/3)  (Z_imp >= 0.148 ft/lb^(1/3))
        # Upper limit: Z <= 198.5 m/kg^(1/3)
        return calculate_brl_parameters_metric(Z, "Free Air")

    # --- Hemispherical Surface Burst (using Swisdak 1994 Table 1 Metric) ---

    # Emit per-parameter validity warnings before clamping occurs internally
    _warn_if_out_of_bounds(Z, "incident_pressure")
    _warn_if_out_of_bounds(Z, "incident_impulse")
    _warn_if_out_of_bounds(Z, "positive_duration")
    _warn_if_out_of_bounds(Z, "reflected_pressure")
    _warn_if_out_of_bounds(Z, "reflected_impulse")
    _warn_if_out_of_bounds(Z, "arrival_time")

    incident_p        = _select_and_eval(SURFACE_INCIDENT_PRESSURE, Z)
    reflected_p       = _select_and_eval(SURFACE_REFLECTED_PRESSURE, Z)
    positive_impulse  = _select_and_eval(SURFACE_INCIDENT_IMPULSE, Z)
    reflected_impulse = _select_and_eval(SURFACE_REFLECTED_IMPULSE, Z)
    arrival_time      = _select_and_eval(SURFACE_ARRIVAL_TIME, Z)
    positive_duration = _select_and_eval(SURFACE_POSITIVE_DURATION, Z)

    # Derived thermodynamic parameters (Rankine-Hugoniot)
    P0 = 101.325  # kPa
    C0 = 340.292  # m/s
    dynamic_p = 2.5 * (incident_p ** 2) / (7.0 * P0 + incident_p)
    shock_front_velocity = C0 * math.sqrt(1.0 + 6.0 * incident_p / (7.0 * P0))
    particle_velocity = (5.0 * C0 * incident_p) / (7.0 * P0 * math.sqrt(1.0 + 6.0 * incident_p / (7.0 * P0)))

    # Numerical Estimates
    decay_b = solve_decay_parameter(incident_p, positive_impulse, positive_duration)
    negative_duration = positive_duration * (1.0 + 1.0 / decay_b)

    return {
        "scaled_distance": Z,
        "incident_pressure": incident_p,
        "reflected_pressure": reflected_p,
        "dynamic_pressure": dynamic_p,
        "positive_impulse": positive_impulse,
        "reflected_impulse": reflected_impulse,
        "positive_duration": positive_duration,
        "negative_duration": negative_duration,
        "arrival_time": arrival_time,
        "shock_front_velocity": shock_front_velocity,
        "particle_velocity": particle_velocity,
        "decay_parameter": decay_b,
    }
