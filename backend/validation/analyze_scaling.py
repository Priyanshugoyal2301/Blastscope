import sqlite3
import math

# Surface burst coefficients from kingery_bulmash.py
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
    
    print(f"Analyzing {len(cases)} Free Air cases:")
    print(f"{'ID':<3} | {'Z':<6} | {'Ref P':<8} | {'Calc P (Scaled Surface)':<22} | {'Err P %':<8} | {'Ref I':<8} | {'Calc I (Scaled Surface)':<22} | {'Err I %':<8}")
    print("-" * 115)
    
    # Ground reflection scaling factor
    # W_surface = W_free / 2 -> Z_surface = Z_free * 2^(1/3)
    factor = 2.0 ** (1.0 / 3.0)
    
    p_errs = []
    i_errs = []
    
    for c in cases:
        Z = c["scaled_distance"]
        p_ref = c["reference_pressure"]
        i_ref = c["reference_impulse"]
        
        # Scale Z
        Z_surface = Z * factor
        
        p_calc = select_and_eval(SURFACE_INCIDENT_PRESSURE, Z_surface)
        
        # Scaling impulse: Impulse is/W^(1/3) is scaled.
        # Since is_scaled_surface = is / W_surface^(1/3) and is_scaled_free = is / W_free^(1/3)
        # and W_surface = W_free / 2, we have:
        # is_scaled_surface = is / (W_free/2)^(1/3) = is_scaled_free * 2^(1/3)
        # So is_scaled_free = is_scaled_surface / 2^(1/3).
        # Let's verify if that is correct.
        i_calc_surface = select_and_eval(SURFACE_INCIDENT_IMPULSE, Z_surface)
        i_calc = i_calc_surface * factor
        
        p_err = abs(p_calc - p_ref) / p_ref * 100
        i_err = abs(i_calc - i_ref) / i_ref * 100
        
        p_errs.append(p_err)
        i_errs.append(i_err)
        
        print(f"{c['id']:<3} | {Z:<6.3f} | {p_ref:<8.1f} | {p_calc:<22.3f} | {p_err:<8.2f}% | {i_ref:<8.1f} | {i_calc:<22.3f} | {i_err:<8.2f}%")
        
    print("-" * 115)
    print(f"Average Pressure Error: {sum(p_errs)/len(p_errs):.2f}%")
    print(f"Average Impulse Error: {sum(i_errs)/len(i_errs):.2f}%")

if __name__ == "__main__":
    main()
