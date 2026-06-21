import math
import sqlite3
from backend.database.db_manager import DatabaseManager

# Define official Swisdak 1994 metric coefficients for hemispherical surface burst
def eval_poly(Z, coefs):
    u = math.log(Z)
    val = sum(c * (u ** i) for i, c in enumerate(coefs))
    return math.exp(val)

def calc_official_surface(Z):
    # Incident Pressure (kPa)
    if Z < 0.2:
        p = 0.0
    elif 0.2 <= Z <= 2.9:
        p = eval_poly(Z, [7.2106, -2.1069, -0.3229, 0.1117, 0.0685])
    elif 2.9 < Z <= 23.8:
        p = eval_poly(Z, [7.5938, -3.0523, 0.40977, 0.0261, -0.01267])
    elif 23.8 < Z <= 198.5:
        p = eval_poly(Z, [6.0536, -1.4066, 0.0, 0.0, 0.0])
    else:
        p = 0.0
        
    # Incident Impulse (kPa-ms) (unscaled)
    if Z < 0.2:
        imp = 0.0
    elif 0.2 <= Z <= 0.96:
        imp = eval_poly(Z, [5.522, 1.117, 0.6, -0.292, -0.087])
    elif 0.96 < Z <= 2.38:
        imp = eval_poly(Z, [5.465, -0.308, -1.464, 1.362, -0.432])
    elif 2.38 < Z <= 33.7:
        imp = eval_poly(Z, [5.2749, -0.4677, -0.2499, 0.0588, -0.00554])
    elif 33.7 < Z <= 158.7:
        imp = eval_poly(Z, [5.9825, -1.062, 0.0, 0.0, 0.0])
    else:
        imp = 0.0
        
    return p, imp

def main():
    db = DatabaseManager(force_rebuild=False)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases WHERE burst_type='Surface'")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print("Surface Burst cases error comparison with official Swisdak (1994):")
    p_errs = []
    i_errs = []
    for c in cases:
        Z = c["scaled_distance"]
        p_ref = c["reference_pressure"]
        i_ref = c["reference_impulse"]
        
        p_calc, i_calc = calc_official_surface(Z)
        
        p_err = (abs(p_calc - p_ref) / p_ref) * 100.0
        i_err = (abs(i_calc - i_ref) / i_ref) * 100.0
        
        p_errs.append(p_err)
        i_errs.append(i_err)
        
        print(f"ID={c['id']} Z={Z:.3f} Ref_P={p_ref} Calc_P={p_calc:.3f} Err_P={p_err:.2f}% | Ref_I={i_ref} Calc_I={i_calc:.3f} Err_I={i_err:.2f}%")
        
    print(f"\nAverage Pressure Error: {sum(p_errs)/len(p_errs):.2f}%")
    print(f"Average Impulse Error: {sum(i_errs)/len(i_errs):.2f}%")

if __name__ == "__main__":
    main()
