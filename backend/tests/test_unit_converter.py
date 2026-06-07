import pytest
from backend.blast_engine.core.unit_converter import convert

def test_convert_pressure():
    # 1 MPa = 1000 kPa
    assert pytest.approx(convert(1, "MPa", "kPa")) == 1000.0
    # 101.325 kPa = 1 atm
    assert pytest.approx(convert(101.325, "kPa", "atm")) == 1.0
    # Conversions back and forth
    val_psi = convert(15, "psi", "kPa")
    val_back = convert(val_psi, "kPa", "psi")
    assert pytest.approx(val_back) == 15.0

def test_convert_distance():
    # 1 ft = 0.3048 m
    assert pytest.approx(convert(10, "ft", "m")) == 3.048
    assert pytest.approx(convert(3.048, "m", "ft")) == 10.0

def test_unsupported_unit():
    with pytest.raises(ValueError):
        convert(100, "unknown_unit", "kPa")
