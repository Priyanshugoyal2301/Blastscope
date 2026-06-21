import math
from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters

W = 225.0
R = 15.0

# W^(1/3)
w_one_third = W ** (1.0 / 3.0)
Z = R / w_one_third

print(f"W = {W} kg")
print(f"R = {R} m")
print(f"w_one_third = {w_one_third:.6f}")
print(f"Z = {Z:.6f}")

for burst in ["Surface", "Free Air"]:
    print(f"\n--- Burst: {burst} ---")
    kb = calculate_kb_parameters(Z, burst)
    
    # Raw polynomial outputs (which are scaled values for Z)
    p_inc = kb["incident_pressure"]
    p_ref = kb["reflected_pressure"]
    i_inc_scaled = kb["positive_impulse"]
    i_ref_scaled = kb["reflected_impulse"]
    t_arr_scaled = kb["arrival_time"]
    t_dur_scaled = kb["positive_duration"]
    
    # Scale them by W^(1/3) where appropriate
    i_inc_actual = i_inc_scaled * w_one_third
    i_ref_actual = i_ref_scaled * w_one_third
    t_arr_actual = t_arr_scaled * w_one_third
    t_dur_actual = t_dur_scaled * w_one_third
    
    print(f"Raw Incident Pressure = {p_inc:.4f} kPa")
    print(f"Raw Reflected Pressure = {p_ref:.4f} kPa")
    print(f"Raw Incident Impulse (scaled) = {i_inc_scaled:.4f} kPa-ms")
    print(f"Scaled Actual Incident Impulse = {i_inc_actual:.4f} kPa-ms")
    print(f"Raw Reflected Impulse (scaled) = {i_ref_scaled:.4f} kPa-ms")
    print(f"Scaled Actual Reflected Impulse = {i_ref_actual:.4f} kPa-ms")
    print(f"Raw Arrival Time (scaled) = {t_arr_scaled:.4f} ms")
    print(f"Scaled Actual Arrival Time = {t_arr_actual:.4f} ms")
    print(f"Raw Duration (scaled) = {t_dur_scaled:.4f} ms")
    print(f"Scaled Actual Duration = {t_dur_actual:.4f} ms")
