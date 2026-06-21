import pytest
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

# Exact calculated outputs from the current verified Swisdak (1994) implementation
# to ensure zero regression in future changes.
# Z, Expected Pso, Expected Pr, Expected is_scaled, Expected ir_scaled, Expected ta_scaled, Expected to_scaled
SWISDAK_SOLVER_OUTPUTS = [
    (0.20,  17310.4,  185300.9,  369.5,  10519.7,  0.0371,  0.2434),
    (0.50,   4887.6,   39421.9,  166.2,   2370.7,  0.1432,  0.2807),
    (1.00,   1353.7,    8151.8,  236.3,    884.7,  0.4675,  1.7205),
    (2.00,    283.7,    1058.4,  134.6,    363.8,  1.6930,  2.0532),
    (5.0,     43.2,     100.9,   59.3,    125.6,  8.2420,  3.7934),
    (10.0,     14.9,      31.5,   31.0,     59.3, 21.6576,  4.7793),
]

@pytest.mark.parametrize("Z,expected_pso,expected_pr,expected_is,expected_ir,expected_ta,expected_to", SWISDAK_SOLVER_OUTPUTS)
def test_swisdak_surface_regression(Z, expected_pso, expected_pr, expected_is, expected_ir, expected_ta, expected_to):
    """
    Assert that the Python solver's Kingery-Bulmash implementation produces parameters
    matching the baseline calculations within very tight tolerance (<= 0.5%).
    """
    res = calculate_kb_parameters(Z, "Surface")
    
    assert abs(res["incident_pressure"] - expected_pso) / expected_pso * 100 <= 0.5
    assert abs(res["reflected_pressure"] - expected_pr) / expected_pr * 100 <= 0.5
    assert abs(res["positive_impulse"] - expected_is) / expected_is * 100 <= 0.5
    assert abs(res["reflected_impulse"] - expected_ir) / expected_ir * 100 <= 0.5
    assert abs(res["arrival_time"] - expected_ta) / expected_ta * 100 <= 0.5
    assert abs(res["positive_duration"] - expected_to) / expected_to * 100 <= 0.5

def test_kb_parameters_structure():
    """Verify return format structure of the Kingery-Bulmash calculator."""
    res = calculate_kb_parameters(1.0, "Surface")
    required_keys = {
        "scaled_distance", "incident_pressure", "reflected_pressure", "dynamic_pressure",
        "positive_impulse", "reflected_impulse", "positive_duration", "negative_duration",
        "arrival_time", "shock_front_velocity", "particle_velocity", "decay_parameter"
    }
    assert required_keys.issubset(res.keys())
    assert res["scaled_distance"] == 1.0
    
    # Verify velocity values are physical (speed of sound ~340 m/s for low overpressure)
    assert res["shock_front_velocity"] > 340.0
    assert res["particle_velocity"] >= 0.0
