import os
import shutil
import sqlite3
import pytest
from backend.database.db_manager import DatabaseManager

# Helper to locate migration scripts
MIGRATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "migrations"))

def run_sql_file(conn, filename):
    filepath = os.path.join(MIGRATIONS_DIR, filename)
    with open(filepath, "r") as f:
        sql = f.read()
    conn.executescript(sql)

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_migration.db"
    yield str(db_file)
    if db_file.exists():
        try:
            os.remove(db_file)
        except Exception:
            pass

def test_upgrade_v1_to_v5(temp_db):
    # Setup database at version 1
    conn = sqlite3.connect(temp_db)
    run_sql_file(conn, "001_initial.sql")
    
    # Insert mock data
    conn.execute("INSERT INTO explosives (id, name, pressure_equivalency, impulse_equivalency) VALUES (1, 'TestTNT', 1.0, 1.0)")
    conn.execute("""
        INSERT INTO scenarios (id, name, explosive_id, charge_weight, distance, burst_type)
        VALUES (101, 'V1 Scenario', 1, 100.0, 10.0, 'Surface')
    """)
    conn.execute("CREATE TABLE migration_history (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("INSERT INTO migration_history (version) VALUES (1)")
    conn.commit()
    conn.close()

    # Run DatabaseManager upgrades (v1 -> v5)
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # Verify scenarios and data survived
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM scenarios WHERE id = 101").fetchone()
    assert row is not None
    assert row["name"] == "V1 Scenario"
    
    # Check that new tables from v2, v3, v4 exist
    # validation_cases (v2)
    val_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='validation_cases'").fetchone()
    assert val_table is not None

    # sources (v3)
    src_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sources'").fetchone()
    assert src_table is not None

    # notes (v4)
    notes_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'").fetchone()
    assert notes_table is not None
    
    # Verify we can insert notes now (v4 feature)
    conn.execute("INSERT INTO notes (scenario_id, note) VALUES (101, 'Note on V1 scenario after upgrading to V5')")
    conn.commit()
    
    note_row = conn.execute("SELECT * FROM notes WHERE scenario_id = 101").fetchone()
    assert note_row["note"] == "Note on V1 scenario after upgrading to V5"
    
    # Check max version in migration_history is 5
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    conn.close()

def test_upgrade_v2_to_v5(temp_db):
    # Setup database at version 2
    conn = sqlite3.connect(temp_db)
    run_sql_file(conn, "001_initial.sql")
    run_sql_file(conn, "002_validation.sql")
    
    conn.execute("INSERT INTO explosives (id, name, pressure_equivalency, impulse_equivalency) VALUES (1, 'TestTNT', 1.0, 1.0)")
    conn.execute("CREATE TABLE migration_history (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("INSERT INTO migration_history (version) VALUES (1)")
    conn.execute("INSERT INTO migration_history (version) VALUES (2)")
    
    # Insert validation case
    conn.execute("""
        INSERT INTO validation_cases (id, charge_weight, distance, scaled_distance, reference_pressure, reference_impulse)
        VALUES (201, 5.0, 3.0, 1.5, 200.0, 80.0)
    """)
    conn.commit()
    conn.close()

    # Run DatabaseManager upgrades (v2 -> v5)
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # Verify validation cases survived
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM validation_cases WHERE id = 201").fetchone()
    assert row is not None
    assert row["reference_pressure"] == 200.0
    
    # Verify notes table (v4) exists
    notes_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'").fetchone()
    assert notes_table is not None
    
    # Check max version in migration_history is 5
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    conn.close()

def test_upgrade_v3_to_v5(temp_db):
    # Setup database at version 3
    conn = sqlite3.connect(temp_db)
    run_sql_file(conn, "001_initial.sql")
    run_sql_file(conn, "002_validation.sql")
    run_sql_file(conn, "003_pi_curves.sql")
    
    conn.execute("INSERT INTO explosives (id, name, pressure_equivalency, impulse_equivalency) VALUES (1, 'TestTNT', 1.0, 1.0)")
    conn.execute("CREATE TABLE migration_history (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    for v in [1, 2, 3]:
        conn.execute("INSERT INTO migration_history (version) VALUES (?)", (v,))
        
    conn.execute("INSERT INTO sources (id, title, authors, year) VALUES (301, 'Test Source Book', 'Dr. Blast', 2024)")
    conn.commit()
    conn.close()

    # Run DatabaseManager upgrades (v3 -> v5)
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # Verify source survived
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM sources WHERE id = 301").fetchone()
    assert row is not None
    assert row["authors"] == "Dr. Blast"
    
    # Verify notes table (v4) exists
    notes_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'").fetchone()
    assert notes_table is not None
    
    # Check max version in migration_history is 5
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    conn.close()

def test_upgrade_empty_to_v5(temp_db):
    # Start with empty db (no tables at all)
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    conn = db.get_connection()
    # Check max version in migration_history is 5
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    
    # Check that standard seeded explosives exist (like TNT, C4)
    tnt_row = conn.execute("SELECT * FROM explosives WHERE name = 'TNT'").fetchone()
    assert tnt_row is not None
    assert tnt_row["pressure_equivalency"] == 1.0
    conn.close()

def test_upgrade_already_v5_idempotency(temp_db):
    # 1. Initialize completely
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # Check max version
    conn = db.get_connection()
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    conn.close()
    
    # Backup folder should not contain backups yet
    db_dir = os.path.dirname(temp_db)
    backup_dir = os.path.join(db_dir, "backups")
    backups_before = os.listdir(backup_dir) if os.path.exists(backup_dir) else []
    
    # 2. Run DatabaseManager again (simulate second launch/idempotency)
    db_second = DatabaseManager(temp_db, force_rebuild=False)
    
    # Check that no new backups were created
    backups_after = os.listdir(backup_dir) if os.path.exists(backup_dir) else []
    assert len(backups_before) == len(backups_after)
    
    # Check that maximum version remains 5
    conn = db_second.get_connection()
    row2 = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row2[0] == 5
    
    # Assert number of rows in migration_history remains exactly 5
    count = conn.execute("SELECT COUNT(*) FROM migration_history").fetchone()[0]
    assert count == 5
    conn.close()

def test_upgrade_corrupted_db(temp_db):
    # Create corrupted file
    with open(temp_db, "w") as f:
        f.write("Corrupted file content that is not a SQLite database!")
        
    # Run DatabaseManager. It should catch the error, back up, and recreate.
    db = DatabaseManager(temp_db, force_rebuild=False)
    
    # Verify we got a working DB at version 5
    conn = db.get_connection()
    row = conn.execute("SELECT MAX(version) FROM migration_history").fetchone()
    assert row[0] == 5
    conn.close()
    
    # Verify backup of corrupted file exists
    db_dir = os.path.dirname(temp_db)
    backup_dir = os.path.join(db_dir, "backups")
    assert os.path.exists(backup_dir)
    backup_files = os.listdir(backup_dir)
    assert any("sqlite_corrupted" in f for f in backup_files)
