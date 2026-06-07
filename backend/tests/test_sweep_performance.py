import time
import pytest
from backend.blast_engine.services.blast_calculator import BlastCalculatorService

def test_sweep_performance():
    # Set up parameters
    weight = 100.0
    tnt_equiv = 1.0
    burst_type = "Surface"
    
    # 1. Benchmark 1000 calculations
    start_time = time.time()
    results_1000 = []
    for i in range(1000):
        distance = 1.0 + i * 0.1
        res = BlastCalculatorService.calculate_environment(weight, distance, burst_type, tnt_equiv, tnt_equiv, tnt_equiv)
        results_1000.append(res)
    duration_1000 = time.time() - start_time
    
    # 2. Benchmark 5000 calculations
    start_time = time.time()
    results_5000 = []
    for i in range(5000):
        distance = 1.0 + i * 0.02
        res = BlastCalculatorService.calculate_environment(weight, distance, burst_type, tnt_equiv, tnt_equiv, tnt_equiv)
        results_5000.append(res)
    duration_5000 = time.time() - start_time
    
    print(f"\n1000 calculations took: {duration_1000:.4f}s")
    print(f"5000 calculations took: {duration_5000:.4f}s")
    
    # Verify execution is extremely fast (e.g., 5000 calculations should easily take under 300ms in pure Python)
    assert len(results_1000) == 1000
    assert len(results_5000) == 5000
    assert duration_5000 < 0.5, "5000 blast calculations should take less than 500ms"
