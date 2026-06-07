import os
import sqlite3
import pytest
from backend.database.db_manager import DatabaseManager

def test_persistence_integrity():
    db_file = "backend/database/sqlite.db"
    
    # Ensure database is initialized
    db = DatabaseManager(db_file)
    
    # 1. Insert a test scenario
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Clear existing test entries if they exist
    cursor.execute("DELETE FROM scenarios WHERE name = 'Integrity Test Scenario'")
    
    # Insert new
    cursor.execute("""
        INSERT INTO scenarios (name, explosive_id, charge_weight, distance, burst_type, unit_system)
        VALUES ('Integrity Test Scenario', 1, 150.0, 35.0, 'Surface', 'Metric')
    """)
    scenario_id = cursor.lastrowid
    
    # Insert a test note
    cursor.execute("""
        INSERT INTO notes (scenario_id, note)
        VALUES (?, 'This is a persistence verification note.')
    """, (scenario_id,))
    
    # Insert a test cached result
    cursor.execute("""
        INSERT INTO scenario_results (scenario_id, model_version_id, scaled_distance, 
                                      incident_pressure, reflected_pressure, dynamic_pressure, 
                                      positive_impulse, positive_duration, negative_duration, arrival_time)
        VALUES (?, 1, 5.0, 50.0, 120.0, 15.0, 100.0, 12.0, 20.0, 10.0)
    """, (scenario_id,))
    
    conn.commit()
    conn.close()
    
    # 2. Simulate app restart by instantiating db manager again
    db_restart = DatabaseManager(db_file, force_rebuild=False)
    conn_restart = db_restart.get_connection()
    cursor_restart = conn_restart.cursor()
    
    # Retrieve and verify scenario
    cursor_restart.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
    sc_row = cursor_restart.fetchone()
    assert sc_row is not None
    assert sc_row["name"] == "Integrity Test Scenario"
    assert sc_row["charge_weight"] == 150.0
    
    # Retrieve and verify note
    cursor_restart.execute("SELECT * FROM notes WHERE scenario_id = ?", (scenario_id,))
    note_row = cursor_restart.fetchone()
    assert note_row is not None
    assert note_row["note"] == "This is a persistence verification note."
    
    # Retrieve and verify result cache
    cursor_restart.execute("SELECT * FROM scenario_results WHERE scenario_id = ?", (scenario_id,))
    res_row = cursor_restart.fetchone()
    assert res_row is not None
    assert res_row["model_version_id"] == 1
    assert res_row["incident_pressure"] == 50.0
    
    # Cleanup test entries
    cursor_restart.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
    conn_restart.commit()
    conn_restart.close()
    
    print("\nDatabase persistence checked successfully. All values recovered after simulated restart!")
