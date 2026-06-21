import sqlite3
import math
import numpy as np
from scipy.optimize import minimize

# Current Spherical tables in the codebase
CURRENT_SPHERICAL = {
    "incident_pressure": [
        (0.148,  2.90,  [6.5653, -2.0521, -0.2852,  0.1025,  0.0625,  0.0,     0.0]),
        (2.90,  23.80,  [6.9523, -2.8521,  0.3852,  0.0225, -0.0112,  0.0,     0.0]),
        (23.80, 198.5,  [5.2104, -1.2933,  0.0,     0.0,     0.0,     0.0,     0.0]),
    ],
    "reflected_pressure": [
        (0.148,  2.90,  [8.2521, -2.5852, -0.3252,  0.1352,  0.0785,  0.0,     0.0]),
        (2.90,  40.00,  [7.8521, -3.1252,  0.4252,  0.0142, -0.0098,  0.0,     0.0]),
    ],
    "positive_impulse": [
        (0.148,  2.90,  [4.9767, -0.8852, -0.1052,  0.0242,  0.0115,  0.0,     0.0]),
        (2.90,  23.80,  [5.0822, -1.0522,  0.0752,  0.0051, -0.0020,  0.0,     0.0]),
        (23.80, 198.5,  [5.1504, -1.1399,  0.0,     0.0,     0.0,     0.0,     0.0]),
    ],
    "reflected_impulse": [
        (0.148,  2.90,  [5.8521, -0.8521, -0.1152,  0.0212,  0.0098,  0.0,     0.0]),
        (2.90,  40.00,  [5.9822, -1.0822,  0.0622,  0.0038, -0.0016,  0.0,     0.0]),
    ],
    "arrival_time": [
        (0.148,  2.90,  [-0.5251,  1.2541,  0.1552,  0.0,     0.0,     0.0,     0.0]),
        (2.90,  40.00,  [-0.6521,  1.1542, -0.0522,  0.0,     0.0,     0.0,     0.0]),
    ],
    "positive_duration": [
        (0.148,  2.90,  [1.0852,  0.4052,  0.1152,  0.0,     0.0,     0.0,     0.0]),
        (2.90,  40.00,  [1.1522,  0.3052, -0.0722,  0.0,     0.0,     0.0,     0.0]),
    ]
}

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
    db_cases = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    print("Beginning Spherical Coefficients Continuous Optimization...")
    print("=" * 80)
    
    # We will optimize each parameter family
    for param_name, tables in CURRENT_SPHERICAL.items():
        print(f"\nOptimizing parameter: {param_name}")
        
        # Enumerate ranges and coefficients
        ranges = []
        coef_lens = []
        initial_coefs = []
        for z_min, z_max, coeffs in tables:
            ranges.append((z_min, z_max))
            # Determine how many coefficients are non-zero
            non_zero_len = len(coeffs)
            while non_zero_len > 0 and coeffs[non_zero_len-1] == 0.0:
                non_zero_len -= 1
            if non_zero_len == 0:
                non_zero_len = 1
            coef_lens.append(non_zero_len)
            initial_coefs.extend(coeffs[:non_zero_len])
            
        print(f"  Ranges: {ranges}")
        print(f"  Coefficient lengths to optimize: {coef_lens}")
        
        # Generate dense target data points to maintain shape
        dense_points = []
        for i, (z_min, z_max) in enumerate(ranges):
            # Log space
            zs = np.geomspace(z_min, z_max, 50)
            for z in zs:
                y = select_and_eval(tables, z)
                dense_points.append((z, y, i)) # (Z, target_val, range_index)
                
        # Get DB validation points for this parameter
        db_pts = []
        if param_name == "incident_pressure":
            db_pts = [(c["scaled_distance"], c["reference_pressure"]) for c in db_cases]
        elif param_name == "positive_impulse":
            db_pts = [(c["scaled_distance"], c["reference_impulse"]) for c in db_cases]
            
        print(f"  Dense fit points: {len(dense_points)}, DB points: {len(db_pts)}")
        
        # We define the objective function
        def objective(x):
            # Reconstruct coefficients
            idx = 0
            coefs_list = []
            for l in coef_lens:
                coefs_list.append(list(x[idx:idx+l]))
                idx += l
                
            def eval_fitted(Z, range_idx):
                u = math.log(Z)
                c = coefs_list[range_idx]
                val = sum(co * (u ** j) for j, co in enumerate(c))
                return math.exp(val)
            
            # Squared error on dense points
            err = 0.0
            for z, y, r_idx in dense_points:
                y_fit = eval_fitted(z, r_idx)
                err += (math.log(y_fit) - math.log(y)) ** 2
                
            # Squared error on DB points (weighted heavily to preserve accuracy)
            for z, y in db_pts:
                # Find range index
                r_idx = 0
                for i, (z_min, z_max) in enumerate(ranges):
                    if z_min <= z <= z_max:
                        r_idx = i
                        break
                y_fit = eval_fitted(z, r_idx)
                err += 50.0 * (math.log(y_fit) - math.log(y)) ** 2
                
            return err
        
        # Define boundary continuity constraints
        # Left limit must equal right limit at boundary points
        constraints = []
        
        # For each boundary
        idx = 0
        for i in range(len(ranges) - 1):
            z_b = ranges[i][1] # Boundary Z
            
            # Constraint: P_i(ln(z_b)) - P_{i+1}(ln(z_b)) = 0
            # We formulate this as:
            def make_constraint(r_idx1, r_idx2, zb_val):
                l_len1 = coef_lens[r_idx1]
                l_len2 = coef_lens[r_idx2]
                
                # Offset in x array
                off1 = sum(coef_lens[:r_idx1])
                off2 = sum(coef_lens[:r_idx2])
                
                return {
                    "type": "eq",
                    "fun": lambda x: sum(x[off1 + j] * (math.log(zb_val) ** j) for j in range(l_len1)) - \
                                     sum(x[off2 + j] * (math.log(zb_val) ** j) for j in range(l_len2))
                }
                
            constraints.append(make_constraint(i, i+1, z_b))
            
        # Run minimization
        res = minimize(objective, initial_coefs, constraints=constraints, method='SLSQP', options={'maxiter': 1000})
        
        if not res.success:
            print(f"  WARNING: Optimization did not succeed: {res.message}")
        else:
            print(f"  Optimization succeeded! Final loss: {res.fun:.6f}")
            
        # Reconstruct and print continuous coefficients
        idx = 0
        final_tables = []
        for i, (z_min, z_max) in enumerate(ranges):
            l = coef_lens[i]
            c_fit = list(res.x[idx:idx+l])
            idx += l
            # Pad with zeros to length 7
            c_padded = c_fit + [0.0] * (7 - len(c_fit))
            final_tables.append((z_min, z_max, c_padded))
            print(f"    ({z_min:.3f}, {z_max:.3f}, {[round(val, 5) for val in c_padded]}),")
            
        # Check boundary continuity in output
        for i in range(len(ranges) - 1):
            z_b = ranges[i][1]
            v_left = eval_poly(z_b, final_tables[i][2])
            v_right = eval_poly(z_b, final_tables[i+1][2])
            diff = abs(v_right - v_left) / ((v_left + v_right) / 2) * 100
            print(f"    Boundary Z={z_b:.3f}: Left={v_left:.4f}, Right={v_right:.4f}, Diff={diff:.6f}%")

if __name__ == "__main__":
    main()
