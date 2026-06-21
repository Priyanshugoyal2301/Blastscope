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
    cursor.execute("SELECT * FROM validation_cases")
    cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    pressure_errors = []
    impulse_errors = []
    
    for case in cases:
        if case["burst_type"] == "Surface":
            p_calc, i_calc = calc_official_surface(case["scaled_distance"])
        else:
            # use current free air
            Z = case["scaled_distance"]
            if Z < 2.9:
                p_calc = eval_poly(Z, [6.5653, -2.0521, -0.2852, 0.1025, 0.0625])
                i_calc = eval_poly(Z, [4.9767, -0.8852, -0.1052, 0.0242, 0.0115])
            else:
                p_calc = eval_poly(Z, [6.9523, -2.8521, 0.3852, 0.0225, -0.0112])
                i_calc = eval_poly(Z, [5.0822, -1.0522, 0.0752, 0.0051, -0.0020])
                
        p_err = (abs(p_calc - case["reference_pressure"]) / case["reference_pressure"]) * 100.0
        i_err = (abs(i_calc - case["reference_impulse"]) / case["reference_impulse"]) * 100.0
        
        if case["ground_truth_class"] in ["Digitized", "Analytical", "ConWep"]:
            pressure_errors.append(p_err)
            impulse_errors.append(i_err)
            
    avg_p_error = sum(pressure_errors) / len(pressure_errors)
    avg_i_error = sum(impulse_errors) / len(impulse_errors)
    
    print(f"Aggregated errors (N={len(pressure_errors)}):")
    print(f"Average Pressure Error: {avg_p_error:.3f}%")
    print(f"Average Impulse Error: {avg_i_error:.3f}%")

if __name__ == "__main__":
    main()
