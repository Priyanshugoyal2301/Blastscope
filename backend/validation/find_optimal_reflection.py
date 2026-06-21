import sqlite3
import math
from scipy.optimize import minimize

# Surface burst coefficients
SURFACE_INCIDENT_PRESSURE = [
    (0.20,  2.90,  [7.2106, -2.1069, -0.3229,  0.1117,  0.0685,  0.0,     0.0]),
    (2.90, 23.80,  [7.5938, -3.0523,  0.40977, 0.0261, -0.01267, 0.0,     0.0]),
    (23.80, 198.5, [6.0536, -1.4066,  0.0,     0.0,     0.0,     0.0,     0.0]),
]

SURFACE_INCIDENT_IMPULSE = [
    (0.20,  0.96,  [5.5220,  1.1170,  0.6000, -0.2920, -0.0870,  0.0,    0.0]),
    (0.96,  2.38,  [5.4650, -0.3080, -1.4640,  1.3620, -0.4320,  0.0,    0.0]),
    (2.38, 33.70,  [5.2749, -0.4677, -0.2499,  0.0588, -0.00554, 0.0,    0.0]),
    (33.70, 158.7, [5.9825, -1.0620,  0.0,     0.0,     0.0,     0.0,    0.0]),
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
    
    # Let's check the error for different reflection factors
    # We want to find a factor 'k' such that Z_surface = Z_free * k^(1/3)
    # yields the best fit for both pressure and impulse.
    # Note: in the database, the reference pressure is at Z_english = Z,
    # and the reference impulse is at Z_english = Z.
    # So Z passed in is actually Z_english.
    # If the solver evaluates at Z_english = Z, let's see how they correspond.
    
    print("Testing reflection factors for pressure and impulse:")
    print(f"{'Factor (k)':<12} | {'Avg P Error %':<15} | {'Avg I Error %':<15}")
    print("-" * 50)
    
    best_k = 2.0
    min_combined_err = 999.0
    
    for k_val in [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]:
        factor = k_val ** (1.0 / 3.0)
        p_errs = []
        i_errs = []
        for c in cases:
            Z = c["scaled_distance"]
            p_ref = c["reference_pressure"]
            i_ref = c["reference_impulse"]
            
            # Z_surface = Z_free * k^(1/3)
            Z_surface = Z * factor
            
            p_calc = select_and_eval(SURFACE_INCIDENT_PRESSURE, Z_surface)
            
            # Scaled impulse relationship:
            # is_scaled_free = is_scaled_surface / k^(1/3)
            i_calc = select_and_eval(SURFACE_INCIDENT_IMPULSE, Z_surface) / factor
            
            p_err = abs(p_calc - p_ref) / p_ref * 100
            i_err = abs(i_calc - i_ref) / i_ref * 100
            p_errs.append(p_err)
            i_errs.append(i_err)
            
        avg_p = sum(p_errs)/len(p_errs)
        avg_i = sum(i_errs)/len(i_errs)
        print(f"{k_val:<12.1f} | {avg_p:<15.2f}% | {avg_i:<15.2f}%")
        
        combined = avg_p + avg_i
        if combined < min_combined_err:
            min_combined_err = combined
            best_k = k_val
            
    print("-" * 50)
    print(f"Best reflection factor: {best_k} with combined error {min_combined_err:.2f}%")

if __name__ == "__main__":
    main()
