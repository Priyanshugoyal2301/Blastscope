import pytest
import math
from backend.materials.glass import Glass
from backend.materials.rc import ReinforcedConcrete
from backend.materials.steel import Steel
from backend.materials.masonry import Masonry
from backend.materials.uhpc import UHPC

def test_glass_progressive_monolithic():
    glass = Glass(name="Glass 6mm Monolithic")
    thresholds = {
        "minor_pressure": 15.0,
        "minor_impulse": 100.0,
    }
    
    # 1. At very low load, should be Glazing Safe and low breakage probability
    res1 = glass.evaluate_damage(pressure=1.0, impulse=10.0, thresholds=thresholds)
    assert res1["damage_state"] == "Glazing Safe"
    assert res1["severity_score"] < 0.05
    assert res1["confidence_level"] == "High"
    assert "monolithic" in res1["damage_mechanism"].lower()
    
    # 2. At minor threshold, DI should be 1.0, and Pb should be ~0.50 (Weibull calculation)
    res2 = glass.evaluate_damage(pressure=15.0, impulse=100.0, thresholds=thresholds)
    assert res2["damage_state"] == "High Hazard"
    assert pytest.approx(res2["severity_score"], abs=0.05) == 0.50

def test_glass_progressive_laminated():
    glass = Glass(name="Glass 12mm Laminated")
    thresholds = {
        "minor_pressure": 25.0,
        "minor_impulse": 150.0,
    }
    # At minor threshold, DI = 1.0, Pb should be ~0.50
    res = glass.evaluate_damage(pressure=25.0, impulse=150.0, thresholds=thresholds)
    assert res["damage_state"] == "High Hazard"
    assert pytest.approx(res["severity_score"], abs=0.05) == 0.50
    assert "laminated" in res["damage_mechanism"].lower()

def test_concrete_progressive():
    rc = ReinforcedConcrete()
    thresholds = {
        "minor_pressure": 120.0,
        "minor_impulse": 300.0,
        "moderate_pressure": 300.0,
        "moderate_impulse": 500.0,
        "severe_pressure": 1200.0,
        "severe_impulse": 1000.0,
        "failure_pressure": 2000.0,
        "failure_impulse": 2500.0,
    }
    
    # Safe -> Elastic
    res_safe = rc.evaluate_damage(pressure=50.0, impulse=100.0, thresholds=thresholds)
    assert res_safe["damage_state"] == "Elastic"
    assert 0.0 <= res_safe["severity_score"] < 0.20
    
    # Minor -> Cracking
    res_minor = rc.evaluate_damage(pressure=150.0, impulse=320.0, thresholds=thresholds) # Pressure ratio larger
    assert res_minor["damage_state"] == "Cracking"
    assert 0.20 <= res_minor["severity_score"] < 0.40
    
    # Moderate -> Spalling
    res_mod = rc.evaluate_damage(pressure=400.0, impulse=600.0, thresholds=thresholds)
    assert res_mod["damage_state"] == "Spalling"
    assert 0.40 <= res_mod["severity_score"] < 0.60
    
    # Severe -> Scabbing
    res_sev = rc.evaluate_damage(pressure=1300.0, impulse=1100.0, thresholds=thresholds)
    assert res_sev["damage_state"] == "Scabbing"
    assert 0.60 <= res_sev["severity_score"] < 0.80
    
    # Failure -> Breaching
    res_fail = rc.evaluate_damage(pressure=2100.0, impulse=2600.0, thresholds=thresholds)
    assert res_fail["damage_state"] == "Breaching"
    assert 0.80 <= res_fail["severity_score"] <= 1.0

def test_steel_progressive():
    steel = Steel()
    thresholds = {
        "minor_pressure": 150.0,
        "minor_impulse": 400.0,
        "moderate_pressure": 800.0,
        "moderate_impulse": 1200.0,
        "severe_pressure": 3500.0,
        "severe_impulse": 3000.0,
        "failure_pressure": 5000.0,
        "failure_impulse": 4000.0,
    }
    
    # Minor -> Yield
    res = steel.evaluate_damage(pressure=200.0, impulse=450.0, thresholds=thresholds)
    assert res["damage_state"] == "Yield"
    assert 0.25 <= res["severity_score"] < 0.50
    
    # Moderate -> Membrane
    res = steel.evaluate_damage(pressure=900.0, impulse=1300.0, thresholds=thresholds)
    assert res["damage_state"] == "Membrane"
    assert 0.50 <= res["severity_score"] < 0.75
    
    # Severe -> Tearing
    res = steel.evaluate_damage(pressure=3600.0, impulse=3100.0, thresholds=thresholds)
    assert res["damage_state"] == "Tearing"
    assert 0.75 <= res["severity_score"] <= 1.0

def test_hyperbolic_curve_check():
    rc = ReinforcedConcrete()
    thresholds = {
        "minor_pressure": 120.0,
        "minor_impulse": 300.0,
    }
    
    # Let's define a minor curve
    curves = [
        {
            "damage_state": "Minor",
            "curve_type": "Hyperbolic",
            "pressure_asymptote": 84.0,   # 120 * 0.7
            "impulse_asymptote": 210.0,   # 300 * 0.7
            "curve_constant": 3240.0,     # (120-84)*(300-210) = 36 * 90 = 3240
        }
    ]
    
    # 1. Point below asymptotes: P = 80, I = 200 -> Safe
    res1 = rc.evaluate_damage(pressure=80.0, impulse=200.0, thresholds=thresholds, curves=curves)
    assert res1["damage_level"] == "Safe"
    
    # 2. Point above asymptotes but below curve:
    # Say I = 250 (which is > 210).
    # Curve P(250) = 84 + 3240 / (250 - 210) = 84 + 3240 / 40 = 84 + 81 = 165
    # Let's test at P = 150 (below 165) -> Safe
    res2 = rc.evaluate_damage(pressure=150.0, impulse=250.0, thresholds=thresholds, curves=curves)
    assert res2["damage_level"] == "Safe"
    
    # 3. Point above curve: P = 170 (above 165) -> Minor
    res3 = rc.evaluate_damage(pressure=170.0, impulse=250.0, thresholds=thresholds, curves=curves)
    assert res3["damage_level"] == "Minor"
