import sqlite3
from backend.database.db_manager import DatabaseManager
from backend.blast_engine.services.blast_calculator import BlastCalculatorService

db = DatabaseManager(force_rebuild=False)
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM validation_cases")
cases = [dict(row) for row in cursor.fetchall()]

print("Validation cases:")
for case in cases[:15]:
    # Print reference vs calculated
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
    
    print(f"ID={case['id']} W={case['charge_weight']} R={case['distance']} class={case['ground_truth_class']}")
    print(f"  Pressure: Ref={case['reference_pressure']} Calc={p_calc:.3f} Err={p_err:.3f}%")
    print(f"  Impulse:  Ref={case['reference_impulse']} Calc={i_calc:.3f} Err={i_err:.3f}%")
conn.close()
