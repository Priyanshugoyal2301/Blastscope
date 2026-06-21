import os
import pytest
import threading
import concurrent.futures
from backend.database.db_manager import DatabaseManager
from backend.blast_engine.services.blast_calculator import BlastCalculatorService
from backend.studies.batch_runner import BatchRunner

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "concurrency_test.db"
    db = DatabaseManager(str(db_file), force_rebuild=True)
    yield db
    if db_file.exists():
        try:
            os.remove(db_file)
        except Exception:
            pass

def test_concurrent_operations(temp_db):
    """
    Simulate concurrent execution of:
    - 10 parallel scenario saves
    - 10 parallel blast calculations
    - 10 parallel note writes
    - 10 parallel sweep/grid requests
    Verifies that no database locks occur and data is written safely.
    """
    db = temp_db

    # Shared list to store exceptions raised in threads
    exceptions = []

    def perform_save(scenario_idx):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            with conn:
                cursor.execute("""
                    INSERT INTO scenarios (name, explosive_id, charge_weight, distance, burst_type, unit_system)
                    VALUES (?, 1, 100.0, 15.0, 'Surface', 'Metric')
                """, (f"Scenario_{scenario_idx}",))
            conn.close()
        except Exception as e:
            exceptions.append(("save", e))

    def perform_calculation(scenario_idx):
        try:
            # Blast calculation is a pure function that doesn't lock DB, but let's test it thread-safely
            res = BlastCalculatorService.calculate_environment(
                charge_weight=150.0,
                distance=12.5,
                burst_type='Surface',
                pressure_factor=1.0,
                impulse_factor=1.0,
                general_factor=1.0
            )
            assert res["incident_pressure"] > 0
        except Exception as e:
            exceptions.append(("calculation", e))

    def perform_note_write(scenario_idx):
        try:
            # We first need a scenario to attach the note to. Since scenarios are inserted,
            # we can fetch/insert a scenario safely or write to a pre-existing scenario_id.
            conn = db.get_connection()
            cursor = conn.cursor()
            with conn:
                # Insert scenario first to avoid foreign key violations
                cursor.execute("""
                    INSERT INTO scenarios (name, explosive_id, charge_weight, distance, burst_type)
                    VALUES (?, 1, 50.0, 10.0, 'Free Air')
                """, (f"Note_Scenario_{scenario_idx}",))
                scenario_id = cursor.lastrowid
                
                cursor.execute("""
                    INSERT INTO notes (scenario_id, note)
                    VALUES (?, ?)
                """, (scenario_id, f"Concurrent note test details for index {scenario_idx}"))
            conn.close()
        except Exception as e:
            exceptions.append(("note_write", e))

    def perform_sweep(scenario_idx):
        try:
            # Simulate a charge sweep or grid study request
            explosive = {"name": "TNT", "pressure_equivalency": 1.0, "impulse_equivalency": 1.0, "general_equivalency": 1.0}
            charges = [50.0, 100.0, 200.0]
            distances = [10.0, 20.0, 30.0]
            profiles = [
                {"id": 1, "profile_name": "Concrete M30", "family": "Concrete", "failure_category": "Quasi-brittle", "damage_mechanism": "Spalling", "curves": []}
            ]
            res = BatchRunner.run_grid(explosive, charges, distances, profiles, 'Surface')
            assert "points" in res
            assert len(res["points"]) > 0
        except Exception as e:
            exceptions.append(("sweep", e))

    # Execute all operations concurrently using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        futures = []
        for i in range(10):
            futures.append(executor.submit(perform_save, i))
            futures.append(executor.submit(perform_calculation, i))
            futures.append(executor.submit(perform_note_write, i))
            futures.append(executor.submit(perform_sweep, i))
            
        concurrent.futures.wait(futures)

    # Check for any exceptions thrown during thread execution
    if exceptions:
        for op, err in exceptions:
            print(f"Concurrency Error in {op}: {err}")
        pytest.fail(f"Exceptions occurred during concurrent stress testing: {exceptions}")

    # Verify database state after concurrent operations
    conn = db.get_connection()
    sc_count = conn.execute("SELECT COUNT(*) FROM scenarios").fetchone()[0]
    note_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    conn.close()

    # 10 saves + 10 note writes (which also save a scenario) = 20 scenarios
    assert sc_count == 20
    assert note_count == 10
    print("\n✅ Concurrency test completed successfully with 0 database locks or deadlocks!")
