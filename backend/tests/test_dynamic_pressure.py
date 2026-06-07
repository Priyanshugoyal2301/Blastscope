import pytest
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

def test_dynamic_pressure_formula():
    # Verify the dynamic pressure behind the shock front for specific overpressures
    # using Rankine-Hugoniot relations with P0 = 101.325 kPa.
    P0 = 101.325
    
    # 1. Test case P_so = 100.0 kPa
    # Q = 2.5 * 100^2 / (7 * 101.325 + 100) = 25000 / (709.275 + 100) = 25000 / 809.275 = 30.89 kPa
    p_so_1 = 100.0
    expected_q_1 = 2.5 * (p_so_1 ** 2) / (7.0 * P0 + p_so_1)
    
    # 2. Test case P_so = 500.0 kPa
    # Q = 2.5 * 500^2 / (7 * 101.325 + 500) = 625000 / 1209.275 = 516.84 kPa
    p_so_2 = 500.0
    expected_q_2 = 2.5 * (p_so_2 ** 2) / (7.0 * P0 + p_so_2)
    
    # We can check the values returned by calculate_kb_parameters for a given scaled distance
    # Let's verify that the dynamic_pressure key matches the formula exactly.
    res_surf = calculate_kb_parameters(1.5, "Surface")
    p_actual = res_surf["incident_pressure"]
    q_actual = res_surf["dynamic_pressure"]
    q_expected = 2.5 * (p_actual ** 2) / (7.0 * P0 + p_actual)
    
    assert pytest.approx(q_actual) == q_expected
    
    # Check manual benchmark calculations
    # If Pso = 100, Q should be ~30.89 kPa
    assert pytest.approx(expected_q_1, rel=1e-4) == 30.892
    # If Pso = 500, Q should be ~516.84 kPa
    assert pytest.approx(expected_q_2, rel=1e-4) == 516.843
