import pytest
from backend.validation.scenario_validator import validate_scenario_params, ValidationError
from backend.materials.rc import ReinforcedConcrete
from backend.assessment.damage_engine import DamageEngine

def test_scenario_parameter_validation():
    """Verify input validation limits and exception raising."""
    # Valid params should not raise
    validate_scenario_params(100.0, 15.0, "Surface")
    validate_scenario_params(1.0, 0.1, "Free Air")

    # Invalid charge weights
    with pytest.raises(ValidationError, match="Charge weight must be strictly greater than 0 kg"):
        validate_scenario_params(0.0, 15.0, "Surface")
    with pytest.raises(ValidationError, match="Charge weight must be strictly greater than 0 kg"):
        validate_scenario_params(-5.0, 15.0, "Surface")

    # Invalid standoffs
    with pytest.raises(ValidationError, match="Distance must be at least 0.1 meters"):
        validate_scenario_params(10.0, 0.05, "Surface")
    with pytest.raises(ValidationError, match="Distance must be at least 0.1 meters"):
        validate_scenario_params(10.0, -1.0, "Surface")

    # Invalid burst types
    with pytest.raises(ValidationError, match="Invalid burst type"):
        validate_scenario_params(100.0, 10.0, "Underwater")

def test_evaluate_damage_asymptote_bounds():
    """Verify that hyperbolic PI curve boundaries handle asymptote limits safely."""
    rc = ReinforcedConcrete("RC Panel Test")
    
    # Define a mock curve with pressure asymptote = 100, impulse asymptote = 200, Kc = 5000
    curves = [{
        "pressure_asymptote": 100.0,
        "impulse_asymptote": 200.0,
        "curve_constant": 5000.0,
        "damage_state": "Moderate",
        "curve_type": "Hyperbolic"
    }]
    
    thresholds = {
        "minor_pressure": 50.0,
        "minor_impulse": 100.0
    }

    # Case 1: Impulse is less than or equal to the impulse asymptote. Should return Safe (or Minor, but NOT exceed the curve to Moderate).
    res1 = rc.evaluate_damage(pressure=500.0, impulse=199.0, thresholds=thresholds, curves=curves)
    assert res1["damage_level"] != "Moderate"

    # Case 2: Pressure is less than or equal to the pressure asymptote.
    res2 = rc.evaluate_damage(pressure=99.0, impulse=1000.0, thresholds=thresholds, curves=curves)
    assert res2["damage_level"] != "Moderate"

    # Case 3: Exactly on the asymptote boundaries.
    res3 = rc.evaluate_damage(pressure=100.0, impulse=200.0, thresholds=thresholds, curves=curves)
    assert res3["damage_level"] != "Moderate"

    # Case 4: Far exceeding the curve (e.g. pressure=150, impulse=500 -> P_curve = 100 + 5000/300 = 116.6)
    res4 = rc.evaluate_damage(pressure=150.0, impulse=500.0, thresholds=thresholds, curves=curves)
    assert res4["damage_level"] == "Moderate"

def test_evaluate_damage_zero_negative_loads():
    """Ensure zero or negative pressure/impulse loads yield 'Safe' damage levels without exceptions."""
    rc = ReinforcedConcrete("RC Panel Test")
    thresholds = {
        "minor_pressure": 50.0,
        "minor_impulse": 100.0
    }

    res_zero = rc.evaluate_damage(0.0, 0.0, thresholds)
    assert res_zero["damage_level"] == "Safe"
    assert res_zero["damage_index"] == 0.0

    res_neg = rc.evaluate_damage(-10.0, -50.0, thresholds)
    assert res_neg["damage_level"] == "Safe"
    assert res_neg["damage_index"] <= 0.0

def test_damage_engine_obliquity_90_degrees():
    """Verify that a 90 degree angle of incidence reduces reflected parameters to incident parameters."""
    blast_results = {
        "incident_pressure": 100.0,
        "reflected_pressure": 300.0,
        "positive_impulse": 200.0,
        "reflected_impulse": 500.0,
        "positive_duration": 10.0,
        "dynamic_pressure": 20.0,
        "angle_of_incidence": 90.0  # Cos(90) = 0
    }
    
    profiles = [{
        "id": 1,
        "profile_name": "Masonry Facade Test",
        "family": "Masonry",
        "minor_pressure": 50.0,
        "minor_impulse": 100.0,
        "moderate_pressure": 150.0,
        "moderate_impulse": 300.0,
        "severe_pressure": 300.0,
        "severe_impulse": 600.0,
        "failure_pressure": 500.0,
        "failure_impulse": 1000.0,
    }]
    
    # Assess batch
    assessments = DamageEngine.assess_batch(blast_results, profiles)
    assert len(assessments) == 1
    
    # At 90 degrees cos^2(theta) = 0, so adjusted pressure = incident pressure = 100 kPa
    # Since Masonry is a facade, it gets adjusted. Let's make sure the ratio uses P_actual = 100 kPa.
    # minor_pressure is 50.0, so pressure ratio should be 100 / 50 = 2.0.
    assert assessments[0]["pressure_ratio"] == pytest.approx(2.0)
