import sqlite3
import math

def main():
    conn = sqlite3.connect(r"c:\project\drdo\code\backend\database\sqlite.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print("Database validation cases audit:")
    print(f"{'ID':<3} | {'Burst':<8} | {'Z':<5} | {'Ref P':<8} | {'Ref I':<8} | {'English Z equivalent':<20} | {'UFC English P (psi)':<22} | {'UFC English I (psi-ms)':<22}")
    print("-" * 120)
    
    for r in rows:
        Z = r["scaled_distance"]
        ref_p = r["reference_pressure"]
        ref_i = r["reference_impulse"]
        burst = r["burst_type"]
        
        # English Z equivalent would be Z * 2.51538 (since 1 m/kg^(1/3) = 2.51538 ft/lb^(1/3))
        Z_eng_eq = Z * 2.51538
        
        # Let's see if the reference values match English Z = Z (i.e. Z in English is numerically equal to Z)
        # e.g., if Z_metric = 20.0, does Ref_I correspond to Z_english = 20.0?
        # Z_english = 20.0 corresponds to Ref_I_english = 2.40 psi-ms/lb^(1/3). 
        # Metric converted: 2.40 * 8.9742 = 21.54 kPa-ms/kg^(1/3). This matches Ref_I = 21.5!
        # What about Ref_P? Z_metric = 20.0 corresponds to Ref_P_metric = 6.1 kPa.
        
        print(f"{r['id']:<3} | {burst:<8} | {Z:<5.2f} | {ref_p:<8.1f} | {ref_i:<8.1f} | {Z_eng_eq:<20.2f}")

if __name__ == "__main__":
    main()
