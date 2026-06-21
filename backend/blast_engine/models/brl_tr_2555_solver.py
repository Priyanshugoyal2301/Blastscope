"""
BRL-TR-2555 / CONWEP Reference-Grade Forward Blast Solver
=========================================================

Implements the official high-order Kingery-Bulmash (1984) polynomial formulations
for spherical free-air and hemispherical surface bursts in Imperial units internally,
matching the CONWEP lineage code (ARL-TR-1310).

Units System Internally:
  - Scaled distance (Z): ft / lb^(1/3)
  - Pressures (Pso, Pr, Q): psi
  - Scaled impulses (is, ir): psi-ms / lb^(1/3)
  - Scaled times (ta, td): ms / lb^(1/3)

Units System at Boundaries:
  - Scaled distance (Z): m / kg^(1/3)
  - Pressures: kPa
  - Scaled impulses: kPa-ms / kg^(1/3)
  - Scaled times: ms / kg^(1/3)
  - Velocities (U, up): m/s
"""

import math
from typing import Dict, Any


# ===========================================================================
#  BRL-TR-2555 / CONWEP COEFFICIENTS & CONSTANTS (Imperial Units)
#  Source: U.S. Army Research Laboratory Report ARL-TR-1310 (CONWEP), Appendix A
# ===========================================================================

# Incident Overpressure Pso (psi) - cpso(0:11, 2)
# isurf = 1 (Surface burst), isurf = 2 (Air burst)
CPSO_SURFACE = [
    1.9422502013, -1.6958988741, -0.154159376846, 0.514060730593,
    0.0988534365274, -0.293912623038, -0.0268112345019, 0.109097496421,
    0.00162846756311, -0.0214631030242, 0.0001456723382, 0.00167847752266
]

CPSO_FREE_AIR = [
    1.77284970457, -1.69012801396, 0.00804973591951, 0.336743114941,
    -0.00516226351334, -0.0809228619888, -0.00478507266747, 0.00793030472242,
    0.0007684469735, 0.0, 0.0, 0.0
]

# Reflected Overpressure Pr (psi)
# Surface (csurf, 0:11)
CSURF_PREF = [
    2.56431321138, -2.21030870597, -0.218536586295, 0.895319589372,
    0.24989009775, -0.569249436807, -0.11791682383, 0.224131161411,
    0.0245620259375, -0.0455116002694, -0.00190930738887, 0.00361471193389
]
# Free Air (cfree, 0:9)
CFREE_PREF = [
    2.39106134946, -2.21400538997, 0.035119031446, 0.657599992109,
    0.0141818951887, -0.243076636231, -0.0158699803158, 0.0492741184234,
    0.00227639644004, -0.00397126276058
]

# Arrival Time ta/W^(1/3) (ms/lb^(1/3))
# Surface (csurf, 0:9)
CSURF_TARR = [
    -0.173607601251, 1.35706496258, 0.052492798645, -0.196563954086,
    -0.0601770052288, 0.0696360270891, 0.0215297490092, -0.0161658930785,
    -0.00232531970294, 0.00147752067524
]
# Free Air (cfree, 0:7)
CFREE_TARR = [
    -0.0423733936826, 1.36456871214, -0.0570035692784, -0.182832224796,
    0.0118851436014, 0.0432648687627, -0.0007997367834, -0.00436073555033
]

# Reflected Impulse ir/W^(1/3) (psi-ms/lb^(1/3))
# Surface (csurf, 0:3)
CSURF_XIMPR = [
    1.75291677799, -0.949516092853, 0.112136118689, -0.0250659183287
]
# Free Air (cfree, 0:3)
CFREE_XIMPR = [
    1.60579280091, -0.903118886091, 0.101771877942, -0.0242139751146
]

# Incident Impulse is/W^(1/3) (psi-ms/lb^(1/3))
# Surface (csurf1 0:4, csurf2 0:7)
CSURF_XIMPS_1 = [
    1.57159240621, -0.502992763686, 0.171335645235, 0.0450176963051, -0.0118964626402
]
CSURF_XIMPS_2 = [
    0.719852655584, -0.384519026965, -0.0280816706301, 0.00595798753822,
    0.014544526107, -0.00663289334734, -0.00284189327204, 0.0013644816227
]
# Free Air (cfree1 0:4, cfree2 0:8)
CFREE_XIMPS_1 = [
    1.43534136453, -0.443749377691, 0.168825414684, 0.0348138030308, -0.010435192824
]
CFREE_XIMPS_2 = [
    0.599008468099, -0.40463292088, -0.0142721946082, 0.00912366316617,
    -0.0006750681404, -0.00800863718901, 0.00314819515931, 0.00152044783382,
    -0.0007470265899
]

# Positive Phase Duration to/W^(1/3) (ms/lb^(1/3))
# Surface (csurf1 0:5, csurf2 0:8, csurf3 0:5)
CSURF_TDUR_1 = [
    -0.728671776005, 0.130143717675, 0.134872511954, 0.0391574276906,
    -0.00475933664702, -0.00428144598008
]
CSURF_TDUR_2 = [
    0.20096507334, -0.0297944268976, 0.030632954288, 0.0183405574086,
    -0.0173964666211, -0.00106321963633, 0.00562060030977, 0.0001618217499,
    -0.0006860188944
]
CSURF_TDUR_3 = [
    0.572462469964, 0.0933035304009, -0.0005849420883, -0.00226884995013,
    -0.00295908591505, 0.00148029868929
]
# Free Air (cfree1 0:8, cfree2 0:8, cfree3 0:7)
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


# ===========================================================================
#  ENVIRONMENTAL CONSTANTS (CONWEP / BRL-TR-2555 Imperial)
# ===========================================================================
P0_IMP = 14.696  # psi
C0_IMP = 1116.0  # ft/s


# ===========================================================================
#  CONVERSION FACTOR CONSTANTS
# ===========================================================================
# Converting Z: Z_imperial = Z_metric * Z_CONV
# 1 m = 3.280839895 ft, 1 kg = 2.2046226218 lbs
# So Z_CONV = (1/0.3048) / ((1/0.45359237)**(1/3)) ≈ 2.5207224213797623
Z_CONV = (1.0 / 0.3048) / ((1.0 / 0.45359237) ** (1.0 / 3.0))

# Pressure Conversion: 1 psi = 6.89475729 kPa
PSI_TO_KPA = 6.89475729

# Scaled time (Arrival time, Duration): ms/lb^(1/3) to ms/kg^(1/3)
# t_metric = t_imperial * (0.45359237)**(-1/3) ≈ t_imperial * 1.301549583
TIME_SCALED_CONV = (0.45359237) ** (-1.0 / 3.0)

# Scaled impulse: psi-ms/lb^(1/3) to kPa-ms/kg^(1/3)
# i_metric = i_imperial * PSI_TO_KPA * TIME_SCALED_CONV ≈ i_imperial * 8.973906385
IMPULSE_SCALED_CONV = PSI_TO_KPA * TIME_SCALED_CONV


def _eval_poly_horner(coeffs: list, u: float) -> float:
    """Evaluates a polynomial using Horner's method to match FORTRAN exactly."""
    val = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        val = val * u + c
    return val


def solve_decay_parameter_conwep(pso: float, impulse: float, duration: float) -> float:
    """
    Newton-Raphson solver to compute Modified Friedlander decay parameter.
    Implements the exact CONWEP subroutine conwep-decay logic.
    """
    if impulse <= 0.0 or pso <= 0.0 or duration <= 0.0:
        return 0.0
    ptoi = pso * duration / impulse
    if ptoi <= 1.0:
        return 0.0
    
    # Initial guess
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


def calculate_brl_parameters_imperial(Z_imp: float, burst_type: str) -> Dict[str, float]:
    """
    Computes all blast parameters in Imperial units using the exact CONWEP polynomials.
    """
    isurf = 1 if burst_type == "Surface" else 2
    zlog = math.log10(Z_imp)
    
    # 1. Incident Peak Overpressure Pso
    u_pso = -0.756579301809 + 1.35034249993 * zlog
    if isurf == 1:
        coeffs_pso = CPSO_SURFACE
    else:
        coeffs_pso = CPSO_FREE_AIR
    pso = 10.0 ** _eval_poly_horner(coeffs_pso, u_pso)
    
    # 2. Reflected Peak Pressure Pr
    if isurf == 1:
        u_pr = -0.789312405513 + 1.36637719229 * zlog
        coeffs_pr = CSURF_PREF
    else:
        u_pr = -0.756579301809 + 1.35034249993 * zlog
        coeffs_pr = CFREE_PREF
    pro = 10.0 ** _eval_poly_horner(coeffs_pr, u_pr)
    
    # 3. Arrival Time ta
    if isurf == 1:
        u_ta = -0.755684472698 + 1.37784223635 * zlog
        coeffs_ta = CSURF_TARR
    else:
        u_ta = -0.80501734056 + 1.37407043777 * zlog
        coeffs_ta = CFREE_TARR
    ta = 10.0 ** _eval_poly_horner(coeffs_ta, u_ta)
    
    # 4. Reflected Impulse ir
    if isurf == 1:
        u_ir = -0.781951689212 + 1.33422049854 * zlog
        coeffs_ir = CSURF_XIMPR
    else:
        u_ir = -0.757659920369 + 1.37882996018 * zlog
        coeffs_ir = CFREE_XIMPR
    impr = 10.0 ** _eval_poly_horner(coeffs_ir, u_ir)
    
    # 5. Incident Impulse is
    if isurf == 1:
        if zlog < 0.382017:
            u_is = 0.832468843425 + 3.0760329666 * zlog
            coeffs_is = CSURF_XIMPS_1
        else:
            u_is = -2.91358616806 + 2.40697745406 * zlog
            coeffs_is = CSURF_XIMPS_2
    else:
        if zlog < 0.30103:
            u_is = 1.04504877747 + 3.24299066475 * zlog
            coeffs_is = CFREE_XIMPS_1
        else:
            u_is = -2.67912519532 + 2.30629231803 * zlog
            coeffs_is = CFREE_XIMPS_2
    impo = 10.0 ** _eval_poly_horner(coeffs_is, u_is)
    
    # 6. Positive Phase Duration to
    if isurf == 1:
        if zlog < -0.34:
            to_log = -0.725
        elif zlog < 0.4048337:
            u_to = -0.1790217052 + 5.25099193925 * zlog
            to_log = _eval_poly_horner(CSURF_TDUR_1, u_to)
        elif zlog < 0.845098:
            u_to = -5.85909812338 + 9.2996288611 * zlog
            to_log = _eval_poly_horner(CSURF_TDUR_2, u_to)
        else:
            u_to = -4.92699491141 + 3.46349745571 * zlog
            to_log = _eval_poly_horner(CSURF_TDUR_3, u_to)
    else:
        if zlog < -0.34:
            to_log = -0.824
        elif zlog < 0.350248:
            u_to = 0.209440059933 + 5.11588554305 * zlog
            to_log = _eval_poly_horner(CFREE_TDUR_1, u_to)
        elif zlog < 0.7596678:
            u_to = -5.06778493835 + 9.2996288611 * zlog
            to_log = _eval_poly_horner(CFREE_TDUR_2, u_to)
        else:
            u_to = -4.39590184126 + 3.1524725264 * zlog
            to_log = _eval_poly_horner(CFREE_TDUR_3, u_to)
    to = 10.0 ** to_log
    
    # 7. Decay parameter and Duration adjustments
    zlo = 0.45 if isurf == 1 else 0.37
    if Z_imp >= zlo:
        if (pso * to / impo <= 2.5) or (pro * to / impr <= 2.5):
            to = 2.5 * max(impo / pso, impr / pro)
        a = solve_decay_parameter_conwep(pso, impo, to)
        b = solve_decay_parameter_conwep(pro, impr, to)
    else:
        if (pso * to / impo <= 2.0) or (pro * to / impr <= 2.0):
            to = 2.0 * max(impo / pso, impr / pro)
        a = 0.0
        b = 0.0
        
    # Derived parameters (Rankine-Hugoniot)
    q = 2.5 * (pso ** 2) / (7.0 * P0_IMP + pso)
    u_velocity = C0_IMP * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0_IMP))
    up = (5.0 * C0_IMP * pso) / (7.0 * P0_IMP * math.sqrt(1.0 + 6.0 * pso / (7.0 * P0_IMP)))
    
    # Negative duration
    decay = a
    if decay > 0.0:
        td_neg = to * (1.0 + 1.0 / decay)
    else:
        td_neg = to * 1.5
        
    return {
        "scaled_distance": Z_imp,
        "incident_pressure": pso,
        "reflected_pressure": pro,
        "dynamic_pressure": q,
        "positive_impulse": impo,
        "reflected_impulse": impr,
        "positive_duration": to,
        "negative_duration": td_neg,
        "arrival_time": ta,
        "shock_front_velocity": u_velocity,
        "particle_velocity": up,
        "decay_parameter": decay
    }


def calculate_brl_parameters_metric(Z_metric: float, burst_type: str) -> Dict[str, float]:
    """
    Calcules blast parameters in Metric units by converting to/from Imperial at boundaries.
    """
    # 1. Convert Z to Imperial
    # Clamp Z_metric to protect polynomial stability
    if burst_type == "Surface":
        Z_metric_clamped = max(Z_metric, 0.0238)  # corresponds to Z_imp = 0.06
        Z_metric_clamped = min(Z_metric_clamped, 198.5)
    else:
        Z_metric_clamped = max(Z_metric, 0.0587)  # corresponds to Z_imp = 0.148
        Z_metric_clamped = min(Z_metric_clamped, 198.5)
        
    Z_imp = Z_metric_clamped * Z_CONV
    
    # 2. Evaluate in Imperial
    imp_results = calculate_brl_parameters_imperial(Z_imp, burst_type)
    
    # 3. Convert outputs to Metric
    return {
        "scaled_distance": Z_metric,
        "incident_pressure": imp_results["incident_pressure"] * PSI_TO_KPA,
        "reflected_pressure": imp_results["reflected_pressure"] * PSI_TO_KPA,
        "dynamic_pressure": imp_results["dynamic_pressure"] * PSI_TO_KPA,
        "positive_impulse": imp_results["positive_impulse"] * IMPULSE_SCALED_CONV,
        "reflected_impulse": imp_results["reflected_impulse"] * IMPULSE_SCALED_CONV,
        "positive_duration": imp_results["positive_duration"] * TIME_SCALED_CONV,
        "negative_duration": imp_results["negative_duration"] * TIME_SCALED_CONV,
        "arrival_time": imp_results["arrival_time"] * TIME_SCALED_CONV,
        "shock_front_velocity": imp_results["shock_front_velocity"] * 0.3048,
        "particle_velocity": imp_results["particle_velocity"] * 0.3048,
        "decay_parameter": imp_results["decay_parameter"]
    }
