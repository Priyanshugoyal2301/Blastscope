import math
import sqlite3
from backend.database.db_manager import DatabaseManager

# Current Free Air coefficients from the codebase
def eval_poly(Z, coefs):
    u = math.log(Z)
    val = sum(c * (u ** i) for i, c in enumerate(coefs))
    return math.exp(val)

def calc_current_free_air(Z):
    if Z < 2.9:
        p = eval_poly(Z, [6.5653, -2.0521, -0.2852, 0.1025, 0.0625])
        imp = eval_poly(Z, [4.9767, -0.8852, -0.1052, 0.0242, 0.0115])
    else:
        p = eval_poly(Z, [6.9523, -2.8521, 0.3852, 0.0225, -0.0112])
        imp = eval_poly(Z, [5.0822, -1.0522, 0.0752, 0.0051, -0.0020])
    return p, imp

def main():
    db = DatabaseManager(force_rebuild=False)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases WHERE burst_type='Free Air'")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print("Free Air Burst cases error comparison with current codebase coefficients:")
    p_errs = []
    i_errs = []
    for c in cases:
        Z = c["scaled_distance"]
        p_ref = c["reference_pressure"]
        i_ref = c["reference_impulse"]
        
        p_calc, i_calc = calc_current_free_air(Z)
        
        p_err = (abs(p_calc - p_ref) / p_ref) * 100.0
        i_err = (abs(i_calc - i_ref) / i_ref) * 100.0
        
        p_errs.append(p_err)
        i_errs.append(i_err)
        
        print(f"ID={c['id']} Z={Z:.3f} Ref_P={p_ref} Calc_P={p_calc:.3f} Err_P={p_err:.2f}% | Ref_I={i_ref} Calc_I={i_calc:.3f} Err_I={i_err:.2f}%")
        
    print(f"\nAverage Pressure Error: {sum(p_errs)/len(p_errs):.2f}%")
    print(f"Average Impulse Error: {sum(i_errs)/len(i_errs):.2f}%")

if __name__ == "__main__":
    main()
