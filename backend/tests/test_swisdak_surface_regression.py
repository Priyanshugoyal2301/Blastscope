"""
test_swisdak_surface_regression.py
====================================

Automated regression tests for the Swisdak (1994) Hemispherical Surface Burst
polynomial implementation in kingery_bulmash.py.

Reference Values:
    Swisdak (1994), Table 3 (Metric Summary)
    DTIC ADA526744, U.S. Naval Surface Warfare Center

Tolerance (per user specification):
    Pressure (Pso, Pr) : <= 1.0 %
    Impulse (is)       : <= 1.0 %
    Arrival Time (ta)  : <= 1.0 %
    Positive Duration  : <= 1.0 %

Coverage:
    Z = 0.20, 0.50, 1.0, 2.0, 5.0, 10.0, 20.0  m/kg^(1/3)

Validity Note:
    The Swisdak (1994) Table 1 equations are valid for:
        Pso, is, to : Z >= 0.20 m/kg^(1/3)
        Pr, ir, ta  : Z >= 0.06 m/kg^(1/3)
    Tests at Z = 0.20 are exactly at the lower validity bound.
"""

import pytest
import warnings
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

# ===========================================================================
#  SWISDAK (1994) TABLE 3 REFERENCE VALUES — HEMISPHERICAL SURFACE BURST
#  Source: DTIC ADA526744, Table 3 (Metric)
#
#  Columns: (Z, Pso_kPa, Pr_kPa, is_kPa_ms, ta_ms_per_kg13, to_ms_per_kg13)
#  Note: ta and to are SCALED values (per kg^(1/3)), so for W=1 kg they equal
#        the physical values in ms directly.
# ===========================================================================
SWISDAK_TABLE_3_REFERENCE = [
    # Z (m/kg^1/3)  Pso (kPa)   Pr (kPa)    is (kPa-ms) ta (ms/kg^1/3) to (ms/kg^1/3)
    (0.20,          17310.4,    185300.9,   369.5,       0.0371,        0.2434),
    (0.50,           4887.6,     39421.9,   166.2,       0.1432,        0.2807),
    (1.00,           1353.7,      8151.8,   236.3,       0.4675,        1.7205),
    (2.00,            283.7,      1058.4,   134.6,       1.6930,        2.0532),
    (5.00,             43.2,       100.9,    59.3,       8.2420,        3.7934),
    (10.00,            14.9,        31.5,    31.0,      21.6576,        4.7793),
    (20.00,             6.1,        12.4,    15.9,      49.9338,        5.9402),
]

# Tolerance in percent (1% per specification)
TOLERANCE_PRESSURE_PCT = 1.0
TOLERANCE_IMPULSE_PCT  = 1.0
TOLERANCE_TIME_PCT     = 1.0


# ===========================================================================
#  PARAMETRIZED REGRESSION TESTS
# ===========================================================================

@pytest.mark.parametrize(
    "Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to",
    SWISDAK_TABLE_3_REFERENCE
)
def test_swisdak_surface_incident_pressure(Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to):
    """Incident pressure Pso must match Swisdak Table 3 within 1%."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # Z=0.20 is at boundary — suppress
        res = calculate_kb_parameters(Z, "Surface")

    pso = res["incident_pressure"]
    err_pct = abs(pso - ref_pso) / ref_pso * 100.0
    assert err_pct <= TOLERANCE_PRESSURE_PCT, (
        f"Pso failure at Z={Z}: "
        f"BlastScope={pso:.2f} kPa, Swisdak={ref_pso:.2f} kPa, "
        f"error={err_pct:.4f}% > {TOLERANCE_PRESSURE_PCT}%"
    )


@pytest.mark.parametrize(
    "Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to",
    SWISDAK_TABLE_3_REFERENCE
)
def test_swisdak_surface_reflected_pressure(Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to):
    """Reflected pressure Pr must match Swisdak Table 3 within 1%."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        res = calculate_kb_parameters(Z, "Surface")

    pr = res["reflected_pressure"]
    err_pct = abs(pr - ref_pr) / ref_pr * 100.0
    assert err_pct <= TOLERANCE_PRESSURE_PCT, (
        f"Pr failure at Z={Z}: "
        f"BlastScope={pr:.2f} kPa, Swisdak={ref_pr:.2f} kPa, "
        f"error={err_pct:.4f}% > {TOLERANCE_PRESSURE_PCT}%"
    )


@pytest.mark.parametrize(
    "Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to",
    SWISDAK_TABLE_3_REFERENCE
)
def test_swisdak_surface_incident_impulse(Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to):
    """Incident impulse is must match Swisdak Table 3 within 1%."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        res = calculate_kb_parameters(Z, "Surface")

    is_calc = res["positive_impulse"]
    err_pct = abs(is_calc - ref_is) / ref_is * 100.0
    assert err_pct <= TOLERANCE_IMPULSE_PCT, (
        f"is failure at Z={Z}: "
        f"BlastScope={is_calc:.4f} kPa-ms, Swisdak={ref_is:.4f} kPa-ms, "
        f"error={err_pct:.4f}% > {TOLERANCE_IMPULSE_PCT}%"
    )


@pytest.mark.parametrize(
    "Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to",
    SWISDAK_TABLE_3_REFERENCE
)
def test_swisdak_surface_arrival_time(Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to):
    """Arrival time ta must match Swisdak Table 3 within 1%."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        res = calculate_kb_parameters(Z, "Surface")

    ta = res["arrival_time"]
    err_pct = abs(ta - ref_ta) / ref_ta * 100.0
    assert err_pct <= TOLERANCE_TIME_PCT, (
        f"ta failure at Z={Z}: "
        f"BlastScope={ta:.6f} ms, Swisdak={ref_ta:.6f} ms, "
        f"error={err_pct:.4f}% > {TOLERANCE_TIME_PCT}%"
    )


@pytest.mark.parametrize(
    "Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to",
    SWISDAK_TABLE_3_REFERENCE
)
def test_swisdak_surface_positive_duration(Z, ref_pso, ref_pr, ref_is, ref_ta, ref_to):
    """Positive duration to must match Swisdak Table 3 within 1%."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        res = calculate_kb_parameters(Z, "Surface")

    to = res["positive_duration"]
    err_pct = abs(to - ref_to) / ref_to * 100.0
    assert err_pct <= TOLERANCE_TIME_PCT, (
        f"to failure at Z={Z}: "
        f"BlastScope={to:.6f} ms, Swisdak={ref_to:.6f} ms, "
        f"error={err_pct:.4f}% > {TOLERANCE_TIME_PCT}%"
    )


# ===========================================================================
#  VALIDITY BOUNDARY TESTS
# ===========================================================================

def test_validity_warning_emitted_below_pso_z_min():
    """
    Confirm that a UserWarning is raised when Z < 0.20 for Pso/is/to parameters.
    The test triggers this by requesting Z = 0.10 (below the 0.20 bound).
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        calculate_kb_parameters(0.10, "Surface")

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    assert len(user_warnings) >= 3, (
        f"Expected at least 3 UserWarning(s) for Z=0.10 (Pso, is, to are all out of bounds), "
        f"but got {len(user_warnings)}"
    )

    warning_messages = " ".join(str(w.message) for w in user_warnings)
    assert "incident_pressure" in warning_messages or "incident_impulse" in warning_messages, (
        "Expected warning message to reference a specific out-of-range parameter"
    )


def test_no_validity_warning_at_z020():
    """
    Confirm that no UserWarning is emitted for Z = 0.20 (exactly at the lower
    validity bound for Pso, is, to). This is the edge case that must NOT warn.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        calculate_kb_parameters(0.20, "Surface")

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    # Z = 0.20 is exactly the bound — our warning fires on strict Z < z_min,
    # so no warnings should be emitted here.
    assert len(user_warnings) == 0, (
        f"Unexpected UserWarning(s) at Z=0.20 (boundary): {[str(w.message) for w in user_warnings]}"
    )


def test_no_validity_warning_above_z020():
    """Confirm no UserWarning is emitted for an in-range scaled distance (Z = 1.0)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        calculate_kb_parameters(1.0, "Surface")

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    assert len(user_warnings) == 0, (
        f"Unexpected UserWarning(s) at Z=1.0: {[str(w.message) for w in user_warnings]}"
    )


def test_reflected_params_valid_at_z006():
    """
    Confirm that Pr, ir, ta do NOT trigger validity warnings at Z=0.06 (their lower bound).
    Only Pso, is, to (Z_min=0.20) should warn.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        calculate_kb_parameters(0.06, "Surface")

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    # At Z=0.06, Pr/ir/ta are exactly at their bound (no warn),
    # but Pso/is/to are below 0.20 (should warn).
    warning_messages = " ".join(str(w.message) for w in user_warnings)
    # Verify that reflective parameter warnings are NOT among them
    assert "reflected_pressure" not in warning_messages, (
        "Unexpected warning for reflected_pressure at Z=0.06 (its lower validity bound)"
    )
    assert "arrival_time" not in warning_messages, (
        "Unexpected warning for arrival_time at Z=0.06 (its lower validity bound)"
    )
    # Pso, is, to should warn
    assert len(user_warnings) >= 3, (
        f"Expected at least 3 UserWarning(s) at Z=0.06 for Pso/is/to, got {len(user_warnings)}"
    )


# ===========================================================================
#  RETURN STRUCTURE INTEGRITY TEST
# ===========================================================================

def test_surface_output_keys_complete():
    """Verify the output dictionary contains all required keys."""
    res = calculate_kb_parameters(1.0, "Surface")
    required_keys = {
        "scaled_distance", "incident_pressure", "reflected_pressure", "dynamic_pressure",
        "positive_impulse", "reflected_impulse", "positive_duration", "negative_duration",
        "arrival_time", "shock_front_velocity", "particle_velocity", "decay_parameter"
    }
    assert required_keys.issubset(res.keys()), (
        f"Missing keys: {required_keys - res.keys()}"
    )


def test_surface_physical_monotonicity():
    """
    Pressure must decrease monotonically as Z increases (basic physics check).
    Verify across the validated range Z = 0.5, 1, 2, 5, 10, 20.

    Note on positive impulse: Swisdak (1994) Table 3 documents a local impulse
    maximum near Z ~ 1.0 m/kg^(1/3) (is rises from 166.2 at Z=0.5 to 236.3 at
    Z=1.0 before decreasing). This is a known physical feature of the near-field
    surface burst signature and is correctly reproduced by the solver. The
    monotonicity assertion for impulse is therefore applied only for Z >= 2.0
    where strict decrease is expected.
    """
    z_vals = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
    results = [calculate_kb_parameters(z, "Surface") for z in z_vals]

    # Pressure must decrease everywhere
    for i in range(len(results) - 1):
        assert results[i]["incident_pressure"] > results[i + 1]["incident_pressure"], (
            f"Pso not monotonically decreasing between Z={z_vals[i]} and Z={z_vals[i+1]}"
        )

    # Impulse must decrease from Z=2 onwards (known local maximum at Z~1)
    impulse_z2_onwards = [r["positive_impulse"] for r in results[2:]]  # Z = 2, 5, 10, 20
    for i in range(len(impulse_z2_onwards) - 1):
        assert impulse_z2_onwards[i] > impulse_z2_onwards[i + 1], (
            f"is not decreasing for Z={z_vals[i+2]} -> Z={z_vals[i+3]}"
        )


def test_free_air_not_affected_by_surface_warnings():
    """
    Confirm that Free Air mode never triggers Surface-specific validity warnings,
    even for very small Z.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        calculate_kb_parameters(0.05, "Free Air")

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    surface_warnings = [w for w in user_warnings if "Swisdak" in str(w.message)]
    assert len(surface_warnings) == 0, (
        f"Surface-specific Swisdak warnings should not fire for Free Air mode: "
        f"{[str(w.message) for w in surface_warnings]}"
    )
