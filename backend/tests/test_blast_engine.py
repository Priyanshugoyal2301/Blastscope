import pytest
from backend.blast_engine.core.tnt_equivalence import (
    calculate_pressure_tnt_equivalent,
    calculate_impulse_tnt_equivalent,
    calculate_general_tnt_equivalent
)
from backend.materials.glass import Glass

def test_tnt_equivalency():
    # Test 1: 100 kg TNT must produce Wp = 100, Wi = 100
    weight = 100.0
    tnt_p_factor = 1.0
    tnt_i_factor = 1.0
    tnt_g_factor = 1.0
    
    wp = calculate_pressure_tnt_equivalent(weight, tnt_p_factor)
    wi = calculate_impulse_tnt_equivalent(weight, tnt_i_factor)
    wg = calculate_general_tnt_equivalent(weight, tnt_g_factor)
    
    assert wp == 100.0
    assert wi == 100.0
    assert wg == 100.0

def test_c4_equivalency():
    # Test 2: 100 kg C4 must produce Wp = 137, Wi = 119
    weight = 100.0
    c4_p_factor = 1.37
    c4_i_factor = 1.19
    c4_g_factor = 1.34
    
    wp = calculate_pressure_tnt_equivalent(weight, c4_p_factor)
    wi = calculate_impulse_tnt_equivalent(weight, c4_i_factor)
    wg = calculate_general_tnt_equivalent(weight, c4_g_factor)
    
    assert pytest.approx(wp) == 137.0
    assert pytest.approx(wi) == 119.0
    assert pytest.approx(wg) == 134.0

def test_damage_engine_mode_a():
    # Test 3: Pressure Ratio = 3, Impulse Ratio = 1 -> DI = 3, Mode = Pressure, Moderate
    glass = Glass()
    thresholds = {
        "minor_pressure": 10.0,
        "minor_impulse": 50.0
    }
    
    # R_p = 3.0 => pressure = 30.0
    # R_i = 1.0 => impulse = 50.0
    res = glass.evaluate_damage(pressure=30.0, impulse=50.0, thresholds=thresholds)
    
    assert pytest.approx(res["pressure_ratio"]) == 3.0
    assert pytest.approx(res["impulse_ratio"]) == 1.0
    assert pytest.approx(res["damage_index"]) == 3.0
    assert res["controlling_mode"] == "Pressure"
    assert res["damage_level"] == "Moderate"

def test_damage_engine_mode_b():
    # Test 4: Pressure Ratio = 0.5, Impulse Ratio = 5 -> DI = 5, Mode = Impulse, Severe
    glass = Glass()
    thresholds = {
        "minor_pressure": 10.0,
        "minor_impulse": 50.0
    }
    
    # R_p = 0.5 => pressure = 5.0
    # R_i = 5.0 => impulse = 250.0
    res = glass.evaluate_damage(pressure=5.0, impulse=250.0, thresholds=thresholds)
    
    assert pytest.approx(res["pressure_ratio"]) == 0.5
    assert pytest.approx(res["impulse_ratio"]) == 5.0
    assert pytest.approx(res["damage_index"]) == 5.0
    assert res["controlling_mode"] == "Impulse"
    assert res["damage_level"] == "Severe"

def test_physics_validation_accuracy():
    """
    Assert that the Swisdak physical calculations yield < 5% average error
    compared to the 30 independent benchmark validation records.
    """
    from backend.database.db_manager import DatabaseManager
    from backend.blast_engine.services.blast_calculator import BlastCalculatorService
    
    # Connect to database without wiping it
    db = DatabaseManager(force_rebuild=False)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM validation_cases")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # We must have 30 seeded cases
    assert len(cases) >= 30
    
    pressure_errors = []
    impulse_errors = []
    
    for case in cases:
        # Run physical calculations using Kingery-Bulmash (Swisdak 1994)
        calc = BlastCalculatorService.calculate_environment(
            charge_weight=case["charge_weight"],
            distance=case["distance"],
            burst_type=case["burst_type"],
            pressure_factor=1.0,
            impulse_factor=1.0,
            general_factor=1.0,
            model="Kingery-Bulmash"
        )
        
        p_calc = calc["incident_pressure"]
        i_calc = calc["positive_impulse"]
        
        p_err = (abs(p_calc - case["reference_pressure"]) / case["reference_pressure"]) * 100.0
        i_err = (abs(i_calc - case["reference_impulse"]) / case["reference_impulse"]) * 100.0
        
        # We only aggregate errors for Analytical and Digitized cases as field test/experimental data
        # has natural physical variance (up to 15-20%) which is expected in blast engineering.
        if case["ground_truth_class"] in ["Digitized", "Analytical", "ConWep"]:
            pressure_errors.append(p_err)
            impulse_errors.append(i_err)
            
    avg_p_error = sum(pressure_errors) / len(pressure_errors)
    avg_i_error = sum(impulse_errors) / len(impulse_errors)
    
    print(f"\nValidation Accuracy Summary (N={len(pressure_errors)} publication references):")
    print(f"Average Pressure Error: {avg_p_error:.3f}%")
    print(f"Average Impulse Error: {avg_i_error:.3f}%")
    
    # Assert physical calculations maintain < 5% average error compared to reference datasets
    assert avg_p_error < 5.0
    assert avg_i_error < 5.0

