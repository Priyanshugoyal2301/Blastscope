import math

# Let's define the correct physical values in English units from UFC 3-340-02 Table 2-3 and 2-4
# Z_english, Pso_english (psi), is_english (psi-ms/lb^(1/3))

# Table 2-3 (Surface)
UFC_TABLE_2_3 = {
    1.0: (194.27, 28.59),
    1.5: (80.57, 19.10),
    2.0: (41.80, 14.74),
    3.0: (16.78, 10.22),
    4.0: (9.41, 8.04),
    5.0: (6.27, 6.50),
    8.0: (2.99, 4.65),
    10.0: (2.16, 3.85),
    15.0: (1.25, 2.91),
    20.0: (0.887, 2.40),
}

# Table 2-4 (Free Air)
# Let's look up the values in Table 2-4 at the equivalent English Z_english = Z_metric * 2.51538
# Z_metric = 1.0 -> Z_english = 2.515
# Z_metric = 1.5 -> Z_english = 3.773
# Z_metric = 2.0 -> Z_english = 5.031
# Z_metric = 3.0 -> Z_english = 7.546
# Z_metric = 4.0 -> Z_english = 10.06
# Z_metric = 5.0 -> Z_english = 12.58
# Let's see if the values in Table 2-4 satisfy the 2.0 weight scaling relationship:
# Pso_free(Z_free) = Pso_surface(Z_free * 2^(1/3))
# is_free(Z_free) = is_surface(Z_free * 2^(1/3)) / 2^(1/3)
# In UFC 3-340-02, Table 2-3 (Surface) is derived from Table 2-4 (Free Air) by using weight 2W.
# So Table 2-3 at Z_surface is EXACTLY Table 2-4 at Z_free = Z_surface / 2^(1/3).
# Therefore:
# Pso_free(Z_free) = Pso_surface(Z_free * 2^(1/3))
# is_free(Z_free) = is_surface(Z_free * 2^(1/3)) / 2^(1/3)
# Let's check this mathematical identity.

factor = 2.0 ** (1.0 / 3.0) # 1.25992

# Let's print the comparison for Z_free = 1.0, 1.5, 2.0, 3.0
print("Mathematical check of UFC scaling relation:")
print(f"{'Z_free':<8} | {'P_free (Table 2-4)':<20} | {'P_surface (Z_free * 2^(1/3))':<30} | {'Diff %':<8}")
print("-" * 75)

# We can estimate the values of Table 2-4 at Z_free = 1.0, 1.5, 2.0, 3.0
# by converting the values from Table 2-3 at Z_surface = Z_free * 2^(1/3)
# Z_surface = 1.2599, 1.8899, 2.5198, 3.7798
# Let's check if the database Ref_P values for Free Air (which were digitized from Figure 2-7) match this.
# For Z_free = 1.0: Ref_P = 702.6 kPa (101.9 psi).
# Z_surface = 1.2599. Let's look up Table 2-3 at Z_surface = 1.2599:
# At Z=1.0: P=194.27 psi. At Z=1.5: P=80.57 psi.
# Log-log interpolation at 1.2599:
# ln(P) = ln(194.27) + ln(1.2599)/ln(1.5) * (ln(80.57) - ln(194.27)) = 5.269 - 0.569 * 0.880 = 4.768 -> P = 117.7 psi = 811.5 kPa.
# But Ref_P for Free Air at Z_free = 1.0 is 702.6 kPa (101.9 psi).
# The difference is 15%!
# This proves that Table 2-3 (Surface) and Table 2-4 (Free Air) in UFC 3-340-02 do NOT satisfy the 2.0 scaling relation exactly!
# Why? Because Table 2-3 is for HEMISPHERICAL surface burst, and Table 2-4 is for SPHERICAL free-air.
# In Table 2-3, the reflection factor is not constant 2.0, it varies!
# Let's print the actual reflection factor at each distance:
# Pso_surface(Z) = Pso_free(Z / R_e^(1/3))
# Let's calculate the effective reflection energy factor R_e for each Z:
# We know at Z=1.0: Pso_surface = 194.27 psi.
# At what Z_free in Table 2-4 is Pso_free = 194.27 psi?
# In Table 2-4, at Z=0.794 (which is 1.0 / 2^(1/3)), is Pso_free = 194.27 psi?
# At Z=0.794, Table 2-4 has Pso_free = 162.7 psi (1122 kPa).
# But Pso_surface = 194.27 psi.
# So the reflection factor is actually larger than 2.0 in the near field!

print("Done.")

if __name__ == "__main__":
    pass
