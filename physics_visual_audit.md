# Physics Visual Audit Report

This report presents a visual inspection of all primary blast parameters plotted against scaled distance $Z$ for both Surface and Free Air bursts. Known piecewise boundaries are marked with red dashed lines. Each plot is analyzed for oscillations, spikes, discontinuities, clipping, and unexpected extrema.

---

## Surface Burst

### Incident Pressure vs Z

![Surface Incident Pressure](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/surface_incident_pressure.png)

**Boundaries**: $Z = 2.90$, $Z = 23.80$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | Smooth monotonic decay over the full range |
| Spikes | **NONE** | No sudden jumps exceeding 1% |
| Discontinuities | **MINOR** | +0.70% step jump at $Z = 23.80$ boundary (published equation mismatch) |
| Clipping | **EXPECTED** | 926 identical values at the lower Z boundary ($Z < 0.20$ clamped to $Z = 0.20$). This is the **published validity floor** of Swisdak Table 1 |
| Unexpected Extrema | **2 reversals** | Caused by the $Z = 23.80$ boundary discontinuity creating a local minimum then maximum |

---

### Reflected Pressure vs Z

![Surface Reflected Pressure](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/surface_reflected_pressure.png)

**Boundaries**: $Z = 2.00$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **NONE** | Boundary at $Z = 2.00$ is smooth to within 0.05% |
| Clipping | **NONE** | Reflected pressure table starts at $Z = 0.06$ |
| Unexpected Extrema | **NONE** | |

---

### Positive Impulse vs Z

![Surface Positive Impulse](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/surface_positive_impulse.png)

**Boundaries**: $Z = 0.96$, $Z = 2.38$, $Z = 33.70$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **MINOR** | Slight upward oscillation in $Z \in [0.50, 0.96]$ — published polynomial fit artifact |
| Spikes | **NONE** | |
| Discontinuities | **MINOR** | Value jumps at $Z = 0.96$ (0.23%) and $Z = 2.38$ (2.43%) |
| Clipping | **EXPECTED** | 926 identical values at lower boundary (impulse table starts at $Z = 0.20$) |
| Unexpected Extrema | **2 reversals** | Local minimum around $Z \approx 0.50$ from polynomial oscillation |

---

### Arrival Time vs Z

![Surface Arrival Time](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/surface_arrival_time.png)

**Boundaries**: $Z = 1.50$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **NONE** | Boundary at $Z = 1.50$ is smooth to within 0.19% |
| Clipping | **NONE** | Arrival time table starts at $Z = 0.06$ |
| Unexpected Extrema | **NONE** | |

---

### Positive Duration vs Z

![Surface Positive Duration](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/surface_positive_duration.png)

**Boundaries**: $Z = 1.02$, $Z = 2.80$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **MINOR** | Value jumps at $Z = 1.02$ (1.14%) and $Z = 2.80$ (0.89%) — published equation boundary |
| Clipping | **EXPECTED** | 926 identical values at lower boundary (duration table starts at $Z = 0.20$) |
| Unexpected Extrema | **NONE** | Duration exhibits a physical U-shape (decreases then increases), which is correct behavior |

---

## Free Air Burst

### Incident Pressure vs Z

![Free Air Incident Pressure](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/free_air_incident_pressure.png)

**Boundaries**: None (single polynomial over full range)

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **NONE** | $C^\infty$ continuous |
| Clipping | **NONE** | |
| Unexpected Extrema | **NONE** | |

---

### Reflected Pressure vs Z

![Free Air Reflected Pressure](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/free_air_reflected_pressure.png)

**Boundaries**: None

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **NONE** | $C^\infty$ continuous |
| Clipping | **NONE** | |
| Unexpected Extrema | **NONE** | |

---

### Positive Impulse vs Z

![Free Air Positive Impulse](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/free_air_positive_impulse.png)

**Boundaries**: $Z = 0.793$ (piecewise transition in imperial $\log_{10}(Z_\text{imp}) = 0.30103$)

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **MINOR** | Slight upward oscillation in $Z \in [0.41, 0.79]$ — ARL-TR-1310 polynomial fit artifact |
| Spikes | **NONE** | |
| Discontinuities | **MINOR** | Value jump at $Z = 0.793$ (0.59%) — published piecewise boundary |
| Clipping | **NONE** | |
| Unexpected Extrema | **2 reversals** | Local minimum around $Z \approx 0.41$ from polynomial oscillation |

---

### Arrival Time vs Z

![Free Air Arrival Time](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/free_air_arrival_time.png)

**Boundaries**: None

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **NONE** | $C^\infty$ continuous |
| Clipping | **NONE** | |
| Unexpected Extrema | **NONE** | |

---

### Positive Duration vs Z

![Free Air Positive Duration](C:/Users/Priyanshu Goyal/.gemini/antigravity-ide/brain/2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c/plots/free_air_positive_duration.png)

**Boundaries**: $Z = 0.181$, $Z = 0.889$, $Z = 2.281$

| Check | Result | Detail |
| :--- | :--- | :--- |
| Oscillations | **NONE** | |
| Spikes | **NONE** | |
| Discontinuities | **MINOR** | Value jumps at boundaries (max 1.00% at $Z = 0.889$) — published piecewise boundary |
| Clipping | **EXPECTED** | 786 identical values below $Z \approx 0.181$ where CONWEP clamps $\log_{10}(t_d) = -0.824$ |
| Unexpected Extrema | **NONE** | Duration exhibits a physical U-shape, which is correct |

---

## Anomaly Summary

| Anomaly Type | Surface Count | Free Air Count | Root Cause | Blocking? |
| :--- | :--- | :--- | :--- | :--- |
| **Oscillations** | 1 (impulse) | 1 (impulse) | Published polynomial fit artifacts (Runge's phenomenon) | **NO** |
| **Spikes** | 0 | 0 | — | — |
| **Discontinuities** | 4 boundaries | 4 boundaries | Published piecewise equations do not match at boundaries | **NO** |
| **Clipping** | 3 parameters | 1 parameter | Correct clamping at published validity floors ($Z_\min = 0.20$ Surface, $\log_{10}(t_d) = -0.824$ Free Air) | **NO** |
| **Unexpected Extrema** | 2 (pressure, impulse) | 2 (impulse) | Boundary jumps and polynomial oscillations | **NO** |
| **NaN / Inf / Negative** | 0 | 0 | — | — |

## Verdict

**PASS**. All detected anomalies originate from published equation characteristics. No implementation defects, no NaN/Inf values, no negative values, and no unexplained artifacts. The curves are visually consistent with standard Kingery-Bulmash / Swisdak reference plots.
