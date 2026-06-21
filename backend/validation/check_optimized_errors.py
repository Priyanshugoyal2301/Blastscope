import math
import sqlite3

# Optimized coefficients
OPTIMIZED_SPHERICAL_P = [
    (0.148,  2.900, [6.56473, -2.06707, -0.28669, 0.13897, 0.08131, 0.0, 0.0]),
    (2.900, 23.800, [3.61594, 4.48734, -5.46266, 2.02546, -0.26044, 0.0, 0.0]),
    (23.800, 198.500, [5.39971, -1.33447, 0.0, 0.0, 0.0, 0.0, 0.0]),
]

OPTIMIZED_SPHERICAL_I = [
    (0.148,  2.900, [4.97684, -0.92232, -0.11323, 0.07582, 0.03658, 0.0, 0.0]),
    (2.900, 23.800, [-2.50228, 16.73448, -14.93514, 5.40371, -0.70159, 0.0, 0.0]),
    (23.800, 198.500, [5.84795, -1.2916, 0.0, 0.0, 0.0, 0.0, 0.0]),
]

def eval_poly(Z, coefs):
    u = math.log(Z)
    val = sum(c * (u ** i) for i, c in enumerate(coefs))
    return math.exp(val)

def select_and_eval(tables, Z):
    overall_min = tables[0][0]
    overall_max = tables[-1][1]
    Z_clamped = max(Z, overall_min)
    Z_clamped = min(Z_clamped, overall_max)
    for z_min, z_max, coeffs in tables:
        if z_min <= Z_clamped <= z_max:
            return eval_poly(Z_clamped, coeffs)
    return eval_poly(Z_clamped, tables[-1][2])

def main():
    conn = sqlite3.connect("backend/database/sqlite.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM validation_cases WHERE burst_type='Free Air'")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print("Evaluating optimized spherical coefficients:")
    p_errs = []
    i_errs = []
    
    for c in cases:
        Z = c["scaled_distance"]
        p_ref = c["reference_pressure"]
        i_ref = c["reference_impulse"]
        
        p_calc = select_and_eval(OPTIMIZED_SPHERICAL_P, Z)
        i_calc = select_and_eval(OPTIMIZED_SPHERICAL_I, Z)
        
        p_err = (abs(p_calc - p_ref) / p_ref) * 100.0
        i_err = (abs(i_calc - i_ref) / i_ref) * 100.0
        
        p_errs.append(p_err)
        i_errs.append(i_err)
        
        print(f"ID={c['id']} Z={Z:.3f} Ref_P={p_ref} Calc_P={p_calc:.3f} Err_P={p_err:.2f}% | Ref_I={i_ref} Calc_I={i_calc:.3f} Err_I={i_err:.2f}%")
        
    print(f"\nAverage Pressure Error: {sum(p_errs)/len(p_errs):.2f}%")
    print(f"Average Impulse Error: {sum(i_errs)/len(i_errs):.2f}%")

if __name__ == "__main__":
    main()
