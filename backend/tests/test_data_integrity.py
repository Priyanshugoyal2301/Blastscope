import os
import sqlite3
import json
import hashlib
import shutil
import pytest
from backend.database.db_manager import DatabaseManager
from backend.studies.sweep_engine import SweepEngine
from backend.studies.batch_runner import BatchRunner

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_data_integrity.db"
    yield str(db_file)
    if db_file.exists():
        try:
            os.remove(db_file)
        except Exception:
            pass

def sanitize_data(data):
    """Recursively removes non-deterministic fields like timestamps and random IDs."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if k in ["created_at", "calculated_at", "applied_at", "validated_at"]:
                continue
            if k == "study_id":
                sanitized[k] = "deterministic_study_id"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        sanitized_list = [sanitize_data(item) for item in data]
        if all(isinstance(item, dict) for item in sanitized_list):
            def sort_key(d):
                keys = ["id", "scenario_id", "profile_id", "charge_kg", "distance_m", "name", "profile_name", "damage_state"]
                return tuple(d.get(k, "") for k in keys)
            try:
                sanitized_list.sort(key=sort_key)
            except Exception:
                pass
        return sanitized_list
    else:
        return data

def compute_sha256(data):
    sanitized = sanitize_data(data)
    serialized = json.dumps(sanitized, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def get_db_snapshot(db):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch scenarios
    cursor.execute("SELECT * FROM scenarios ORDER BY id")
    scenarios = [dict(row) for row in cursor.fetchall()]
    
    # 2. Fetch notes
    cursor.execute("SELECT * FROM notes ORDER BY id")
    notes = [dict(row) for row in cursor.fetchall()]
    
    # 3. Fetch scenario_results
    cursor.execute("SELECT * FROM scenario_results ORDER BY id")
    results = [dict(row) for row in cursor.fetchall()]
    
    # 4. Fetch material_assessments
    cursor.execute("SELECT * FROM material_assessments ORDER BY id")
    assessments = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "scenarios": scenarios,
        "notes": notes,
        "results": results,
        "assessments": assessments
    }

def test_data_integrity_lifecycle(temp_db, tmp_path):
    # Initialize DB (which runs migrations and seeds default data)
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # 1. Insert custom test scenarios and notes
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Insert Scenario 1
    cursor.execute("""
        INSERT INTO scenarios (name, explosive_id, charge_weight, distance, burst_type, unit_system)
        VALUES ('Integrity Scenario A', 1, 250.0, 45.0, 'Surface', 'Metric')
    """)
    sc1_id = cursor.lastrowid
    
    # Insert Note for Scenario 1
    cursor.execute("""
        INSERT INTO notes (scenario_id, note)
        VALUES (?, 'Verification note for scenario A.')
    """, (sc1_id,))
    
    # Insert Scenario 2
    cursor.execute("""
        INSERT INTO scenarios (name, explosive_id, charge_weight, distance, burst_type, unit_system)
        VALUES ('Integrity Scenario B', 2, 50.0, 15.0, 'Free Air', 'Metric')
    """)
    sc2_id = cursor.lastrowid
    
    # Insert Note for Scenario 2
    cursor.execute("""
        INSERT INTO notes (scenario_id, note)
        VALUES (?, 'Verification note for scenario B.')
    """, (sc2_id,))
    
    # Save dummy scenario results & assessments to test persistence
    cursor.execute("""
        INSERT INTO scenario_results (scenario_id, model_version_id, scaled_distance, 
                                      incident_pressure, reflected_pressure, dynamic_pressure, 
                                      positive_impulse, positive_duration, negative_duration, arrival_time)
        VALUES (?, 1, 3.5, 80.0, 190.0, 25.0, 150.0, 15.0, 25.0, 8.0)
    """, (sc1_id,))
    sr1_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO material_assessments
        (scenario_result_id, profile_id, damage_level, damage_state, severity_score, 
         pressure_ratio, impulse_ratio, damage_index, controlling_mode, damage_mechanism, 
         assessment_reason, confidence_level, source_reference, response_model_version)
        VALUES (?, 1, 'Moderate', 'Flexural Crack', 0.65, 0.8, 1.2, 1.2, 'Impulse', 'Shear', 
                'Exceeds moderate impulse', 'High', 'UFC 3-340-02', 'v1.0')
    """, (sr1_id,))
    
    conn.commit()
    conn.close()
    
    # 2. Capture baseline database state
    baseline_snapshot = get_db_snapshot(db)
    baseline_hashes = {key: compute_sha256(val) for key, val in baseline_snapshot.items()}
    
    # 3. Capture baseline sweep execution state (deterministic sweeps)
    # Fetch explosive factors & profile for sweep
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM explosives WHERE id = 1")
    tnt_exp = dict(cursor.fetchone())
    cursor.execute("""
        SELECT mp.*, t.minor_pressure, t.minor_impulse, t.moderate_pressure, t.moderate_impulse,
               t.severe_pressure, t.severe_impulse, t.failure_pressure, t.failure_impulse, m.family
        FROM material_profiles mp
        JOIN materials m ON mp.material_id = m.id
        LEFT JOIN thresholds t ON mp.id = t.profile_id
        WHERE mp.id = 1
    """)
    rc_profile = dict(cursor.fetchone())
    # Retrieve curves for this profile
    cursor.execute("SELECT * FROM material_response_curves WHERE profile_id = 1 ORDER BY id")
    rc_profile["curves"] = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Perform Distance Sweep
    dist_sweep_res = SweepEngine.distance_sweep(tnt_exp, 150.0, [5, 10, 20, 50, 100], [rc_profile])
    dist_sweep_hash = compute_sha256(dist_sweep_res)
    
    # Perform Grid Sweep
    grid_sweep_res = BatchRunner.run_grid(tnt_exp, [10.0, 50.0, 100.0], [5.0, 15.0, 30.0], [rc_profile])
    grid_sweep_hash = compute_sha256(grid_sweep_res)
    
    # 4. Simulate manual Database Export (copy database file to a backup path)
    backup_file = str(tmp_path / "manual_backup.db")
    shutil.copy2(temp_db, backup_file)
    assert os.path.exists(backup_file)
    
    # 5. Clear the main database content to simulate a fresh environment or corruption recovery
    os.remove(temp_db)
    assert not os.path.exists(temp_db)
    
    # 6. Simulate manual Database Import (restore backup file to main db path)
    shutil.copy2(backup_file, temp_db)
    assert os.path.exists(temp_db)
    
    # 7. Instantiate db manager again to simulate application restart and recover data
    db_restored = DatabaseManager(temp_db, force_rebuild=False)
    
    # 8. Fetch restored snapshot and assert hashes match baseline EXACTLY
    restored_snapshot = get_db_snapshot(db_restored)
    for key in baseline_hashes:
        restored_hash = compute_sha256(restored_snapshot[key])
        assert restored_hash == baseline_hashes[key], f"SHA256 mismatch for table '{key}' after export/import!"
        
    # 9. Verify restored sweep executions are identical
    conn_restored = db_restored.get_connection()
    cursor_restored = conn_restored.cursor()
    cursor_restored.execute("SELECT * FROM explosives WHERE id = 1")
    tnt_exp_restored = dict(cursor_restored.fetchone())
    cursor_restored.execute("""
        SELECT mp.*, t.minor_pressure, t.minor_impulse, t.moderate_pressure, t.moderate_impulse,
               t.severe_pressure, t.severe_impulse, t.failure_pressure, t.failure_impulse, m.family
        FROM material_profiles mp
        JOIN materials m ON mp.material_id = m.id
        LEFT JOIN thresholds t ON mp.id = t.profile_id
        WHERE mp.id = 1
    """)
    rc_profile_restored = dict(cursor_restored.fetchone())
    cursor_restored.execute("SELECT * FROM material_response_curves WHERE profile_id = 1 ORDER BY id")
    rc_profile_restored["curves"] = [dict(row) for row in cursor_restored.fetchall()]
    conn_restored.close()
    
    restored_dist_sweep = SweepEngine.distance_sweep(tnt_exp_restored, 150.0, [5, 10, 20, 50, 100], [rc_profile_restored])
    restored_dist_sweep_hash = compute_sha256(restored_dist_sweep)
    assert restored_dist_sweep_hash == dist_sweep_hash, "Distance sweep SHA256 mismatch after restart!"
    
    restored_grid_sweep = BatchRunner.run_grid(tnt_exp_restored, [10.0, 50.0, 100.0], [5.0, 15.0, 30.0], [rc_profile_restored])
    restored_grid_sweep_hash = compute_sha256(restored_grid_sweep)
    assert restored_grid_sweep_hash == grid_sweep_hash, "Grid sweep SHA256 mismatch after restart!"
    
    print("\nData integrity validation passed successfully: SHA256 hashes match exactly!")
