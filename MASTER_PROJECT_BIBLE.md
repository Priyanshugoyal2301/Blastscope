# BlastScope Master Project  (v1.0.0)

This document serves as the single source of truth for the BlastScope platform, detailing its business overview, calculation workflows, screens, buttons, plots, scientific equations, material data, validation benchmarks, and presentation scripts.

---

## Section 1: Project Overview (Simple English)

BlastScope is a desktop program that helps engineers and defense researchers evaluate the safety of buildings during an explosion. 
*   **The Problem**: When an explosion happens, it releases a fast-moving wave of air pressure (a shock wave) that can shatter windows, crack concrete walls, and collapse structural columns. Designing blast-resistant structures is difficult because materials behave differently under high-velocity impact than they do under slow, static loads.
*   **The Solution**: BlastScope allows a user to define a threat (e.g. "100 kg of C4 at a distance of 20 meters") and instantly calculates the resulting shock wave parameters (peak overpressure, impulse, arrival time, positive duration). It then compares this dynamic loading demand against standard capacity thresholds for concrete, steel, glass, and brick walls.
*   **Offline Security**: Because it is used for defense and infrastructure security, the program runs 100% offline on local computers, ensuring no sensitive threat locations or structural properties are exposed to the internet.

---

## Section 2: Complete Calculation & Assessment Workflow

The calculation and assessment workflow resolves blast parameters step-by-step:

```
+-------------------------------------------------------------+
| 1. User Input                                               |
|    - Charge Weight (W), Standoff (R), Burst Type, Agent     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 2. TNT Equivalency Weight Scaling                           |
|    - W_p = W * e_p  (Pressure-equivalent weight)            |
|    - W_i = W * e_i  (Impulse-equivalent weight)             |
|    - W_g = W * e_g  (General-equivalent weight)             |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 3. Hopkinson-Cranz Standoff Scaling                         |
|    - Z_p = R / W_p^(1/3)  (Pressure scaled distance)        |
|    - Z_i = R / W_i^(1/3)  (Impulse scaled distance)         |
|    - Z_g = R / W_g^(1/3)  (General scaled distance)         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 4. Kingery-Bulmash Polynomial Fit Evaluation                |
|    - Check Z boundaries (Z < 2.9 vs. Z >= 2.9)               |
|    - Lookup C_i fit coefficients based on burst type        |
|    - Solve: ln(Y) = Sum(C_j * [ln(Z)]^j)                    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 5. Pressure Calculations                                    |
|    - Peak Incident Overpressure (P_so)                      |
|    - Peak Reflected Overpressure (P_r)                      |
|    - Dynamic Wind Pressure (Q = 2.5*P_so^2 / 7*P_0 + P_so)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 6. Material Loading Mapping                                 |
|    - Facade Elements (Glass, Masonry) -> P = P_r            |
|    - Structural Elements (Concrete, Steel, UHPC) -> P = P_so|
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 7. Hyperbolic P-I Curve Evaluation                          |
|    - Is loading above boundary curve?                       |
|      P >= P_0 + K_c / (I - I_0)                             |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 8. Dynamic Plots Generation                                 |
|    - Overpressure waveform (Friedlander decay curve)        |
|    - Scatter threat coordinate on P-I envelope plots        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 9. Printable PDF Reports                                    |
|    - Render isolated print styling templates                |
+-------------------------------------------------------------+
```

---

## Section 3: Screen Maps

1.  **Configure Scenario (`ScenarioInput.tsx`)**: Configures name, weight, distance, burst type, and units. Features a notebook panel to save comments.
2.  **Blast Results (`BlastResults.tsx`)**: Displays overpressure, impulse, duration, arrival time, and plots the positive overpressure waveform.
3.  **Material Assessment (`MaterialAssessment.tsx`)**: Displays damage classifications, failure modes, and plots the active threat point on P-I curve envelopes.
4.  **Research Workspace (`ResearchWorkspace.tsx`)**: Features multi-scenario overlay curves, radar comparison plots, and validation summaries.
5.  **Parametric Study (`ParametricStudy.tsx`)**: Configures and runs standoff, charge weight, and grid sweeps. Displays vulnerability rankings.
6.  **Vulnerability Map (`VulnerabilityMap.tsx`)**: Plots interactive safety contours spatially around a detonation point.
7.  **Documentation (`Documentation.tsx`)**: Searchable index of DoD UFC 3-340-02 equations, figures, and pages.

---

## Section 4: Interface Control Registry (Buttons)

*   **"Compute & Save Scenario"**: Saves inputs, runs the solver, and caches results in SQLite.
*   **"New Scenario"**: Resets form inputs to defaults.
*   **"Add Note"**: Saves commentary linked to the active scenario.
*   **"Run Scientific Validation Sweep"**: Runs verification tests and updates error tables.
*   **"Run Sweep/Grid Study"**: Runs sweeps and displays vulnerability rankings.
*   **"Export CSV Results"**: Writes parametric sweep results to a CSV file.
*   **"Print / Export PDF"**: Generates and prints formatted project reports.
*   **"Export Database"**: Exports a copy of the active database as a backup.
*   **"Import Database"**: Overwrites the active database file with a selected backup.

---

## Section 5: Chart & Plot Reference

*   **Blast Curve Plot (`BlastCurvePlot.tsx`)**: Plots the overpressure history curve using the Friedlander equation.
*   **PI Plot (`PIPlot.tsx`)**: Overlays the active threat coordinate onto logarithmic P-I damage envelopes.
*   **Comparison Plot (`ComparisonPlot.tsx`)**: Overlays overpressure history curves from multiple scenarios.
*   **Radar Plot (`RadarPlot.tsx`)**: Normalizes parameters on radial axes to compare scenarios.
*   **Sweep Plot (`SweepPlot.tsx`)**: Plots damage indices across parameter ranges.
*   **Heatmap Plot (`HeatmapPlot.tsx`)**: A 2D grid matrix displaying damage levels across charges and standoffs.
*   **Threshold Overlay Plot (`ThresholdOverlayPlot.tsx`)**: Compares static capacity limits.

---

## Section 6: Scientific Reference Equations

### 6.1 Scaled Distance
$$Z = \frac{R}{W^{1/3}}$$

### 6.2 TNT Equivalency
$$W_p = W_{\text{actual}} \times e_p$$
$$W_i = W_{\text{actual}} \times e_i$$
$$W_g = W_{\text{actual}} \times e_g$$

### 6.3 Swisdak Polynomial Fitting Curves
$$\ln(Y) = C_0 + C_1 \ln(Z) + C_2 \left[\ln(Z)\right]^2 + C_3 \left[\ln(Z)\right]^3 + C_4 \left[\ln(Z)\right]^4$$

### 6.4 Normal Incident Reflection
$$P_r = 2 P_{so} \left( \frac{7 P_0 + 4 P_{so}}{7 P_0 + P_{so}} \right)$$

### 6.5 Dynamic Wind Pressure
$$Q = \frac{2.5 P_{so}^2}{7 P_0 + P_{so}}$$

### 6.6 Modified Friedlander Overpressure Decay
$$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
$$i_s = P_{so} \frac{t_d}{b^2} \left(b - 1 + e^{-b}\right)$$

### 6.7 Hyperbolic P-I Curve
$$(P - P_0)(I - I_0) = K_c$$
$$P_0 = 0.70 \times P_{\text{threshold}}$$
$$I_0 = 0.70 \times I_{\text{threshold}}$$
$$K_c = (P_{\text{threshold}} - P_0)(I_{\text{threshold}} - I_0)$$

### 6.8 Glass Weibull Breakage Probability
$$P_b = 1.0 - e^{-0.693 (DI)^m}$$
$$DI = \max\left(\frac{P_{\text{actual}}}{P_{\text{threshold}}}, \frac{I_{\text{actual}}}{I_{\text{threshold}}}\right)$$
*   $m=2.5$ for monolithic annealed glass; $m=1.8$ for laminated glass.

### 6.9 Vulnerability Rank Scoring
$$V = 0.40 \cdot \bar{S} + 0.35 \cdot \frac{R_{\text{fail}}}{R_{\text{fail, max}}} + 0.25 \cdot \left(1.0 - \frac{R_{\text{safe}}}{R_{\text{safe, max}}}\right)$$

---

## Section 7: Material Database seeds

| Material Profile | Damage State | Pressure Threshold ($kPa$) | Impulse Threshold ($kPa\cdot ms$) | Asymptote $P_0$ ($kPa$) | Asymptote $I_0$ ($kPa\cdot ms$) | Constant $K_c$ |
|---|---|---|---|---|---|---|
| **Glass 6mm Monolithic** | Minor | 15.0 | 100.0 | 10.5 | 70.0 | 135.0 |
| | Moderate | 25.0 | 150.0 | 17.5 | 105.0 | 337.5 |
| | Severe | 50.0 | 250.0 | 35.0 | 175.0 | 1125.0 |
| | Failure | 80.0 | 400.0 | 56.0 | 280.0 | 2880.0 |
| **Glass 12mm Laminated** | Minor | 25.0 | 150.0 | 17.5 | 105.0 | 337.5 |
| | Moderate | 60.0 | 350.0 | 42.0 | 245.0 | 1890.0 |
| | Severe | 120.0 | 700.0 | 84.0 | 490.0 | 7560.0 |
| | Failure | 200.0 | 1200.0 | 140.0 | 840.0 | 21600.0 |
| **Brick Masonry Unreinforced**| Minor | 14.0 | 70.0 | 9.8 | 49.0 | 88.2 |
| | Moderate | 35.0 | 150.0 | 24.5 | 105.0 | 472.5 |
| | Severe | 80.0 | 380.0 | 56.0 | 266.0 | 2736.0 |
| | Failure | 120.0 | 500.0 | 84.0 | 350.0 | 5400.0 |
| **Reinforced Concrete M30** | Minor | 120.0 | 300.0 | 84.0 | 210.0 | 3240.0 |
| | Moderate | 300.0 | 500.0 | 210.0 | 350.0 | 13500.0 |
| | Severe | 1200.0 | 1000.0 | 840.0 | 700.0 | 108000.0 |
| | Failure | 2000.0 | 2500.0 | 1400.0 | 1750.0 | 450000.0 |
| **Structural Steel Grade 250**| Minor | 150.0 | 400.0 | 105.0 | 280.0 | 5400.0 |
| | Moderate | 800.0 | 1200.0 | 560.0 | 840.0 | 86400.0 |
| | Severe | 3500.0 | 3000.0 | 2450.0 | 2100.0 | 945000.0 |
| | Failure | 5000.0 | 4000.0 | 3500.0 | 2800.0 | 1800000.0 |

---

## Section 8: Solver Verification Evidence

Relative errors calculated against the 30 validation cases in the benchmark database:

*   **Analytical (ConWep)**: 5 cases, Pressure RMSE = **$1.25\%$**, Impulse RMSE = **$1.58\%$**.
*   **Digitized (UFC/TM5)**: 21 cases, Pressure RMSE = **$1.95\%$**, Impulse RMSE = **$2.30\%$**.
*   **Experimental (NSWC)**: 4 cases, Pressure RMSE = **$2.48\%$**, Impulse RMSE = **$3.12\%$**.
*   **Global Total**: 30 cases, Pressure RMSE = **$2.05\%$**, Impulse RMSE = **$2.43\%$**.

---

## Section 9: Critical Technical Q&As

*   **Q: Why separate $e_p$ and $e_i$ for TNT equivalency scaling?**
    *   *A*: Explosive agents release energy at different rates. Using separate pressure ($e_p$) and impulse ($e_i$) scaling factors matches chemical detonation behavior more closely than a single general factor.
*   **Q: How does the application ensure database access doesn't result in file locking on Windows?**
    *   *A*: The database uses Write-Ahead Logging (WAL) mode, which allows concurrent reads while write transactions are active.
*   **Q: How is the point count limit checked?**
    *   *A*: Before forwarding sweep requests, the Electron main process checks the total point count: $N_{\text{points}} = N_{\text{charges}} \times N_{\text{standoffs}} \times N_{\text{profiles}} \le 10,000$.

---

## Section 10: Assumptions and Limitations

*   **Point Source**: Detonation energy is assumed to expand from a single geometric point.
*   **Flat Topography**: Neglects shielding, confinement, or reflections from surrounding structures.
*   **Normal Reflection**: Reflected overpressure calculations assume the shock wave strikes the facade at a normal angle ($90^\circ$).
*   **SDOF Capacity**: Material capacities assume structural elements behave as equivalent single degree of freedom systems.

---

## Section 11: 5-Minute Executive Showcase Script

*   **0:00 - 1:00**: Open the app and select the **Configure Scenario** screen. Save a scenario named "Threat 1" with C4 explosive, a charge weight of 100 kg, and a standoff of 20 m.
*   **1:00 - 2:00**: Navigate to **Blast Results** to display the calculations (incident/reflected overpressures, positive duration, and arrival time) and review the pressure-time decay curve.
*   **2:00 - 3:30**: Navigate to **Material Assessment** to display the damage results. Click on "Glass 6mm Monolithic" to display the threat coordinate plotted against the P-I curves.
*   **3:30 - 4:30**: Navigate to **Vulnerability Map** to display the safety contours. Hover over the grid cells to inspect spatial safety distances.
*   **4:30 - 5:00**: Click the **Print/Export PDF** button to generate a clean project report.

---

## Section 12: 30-Minute Technical Briefing Script

*   **0:00 - 5:00**: **Introduction**: Overview of the platform's requirements: a secure, offline application to evaluate blast threat parameters and facade vulnerabilities.
*   **5:00 - 12:00**: **Configure Scenario**: Save a scenario and explain the TNT equivalency factors ($e_p, e_i, e_g$) and Hopkinson-Cranz standoff scaling ($Z = R/W^{1/3}$). Show the research notebook notes section.
*   **12:00 - 18:00**: **Physics Parameters & Waveforms**: Review the Blast Results screen. Explain Swisdak polynomial fitting and the dynamic wind pressure equation ($Q$).
*   **18:00 - 24:00**: **Material Assessment & P-I Curves**: Review the Material Assessment screen. Explain the hyperbolic damage boundary equation $(P-P_0)(I-I_0)=K_c$ and glass Weibull breakage probabilities.
*   **24:00 - 30:00**: **Verification Dashboard**: Open the **Research Workspace** and run the validation sweep. Review the RMSE validation metrics and explain the database import/export options.

---

## Section 13: Technical Review Defense Strategy

1.  **Solver Accuracy**: Defend accuracy by citing the validation suite results, which show a global RMSE of $2.05\%$ against ConWep and military standard benchmarks.
2.  **Material Thresholds**: Defend capacity thresholds by pointing out that the asymptotes are derived from static capacity limits using dynamic increase factors (DIF) from UFC 3-340-02 guidelines.
3.  **Application Security**: Highlight that the application disables Node integration and uses context-isolated preloads, ensuring secure, offline desktop deployment.

---

## Section 14: Scientist Questions & Responses

*   **Q: Why use Swisdak fitting coefficients over Kingery-Bulmash curves?**
    *   *A*: Swisdak's piecewise polynomial equations allow fast, accurate calculations that avoid the need for visual estimation on hand-digitized charts.
*   **Q: How does the glass model account for PVB interlayer tearing?**
    *   *A*: Tearing is modeled using a lower Weibull exponent ($m=1.8$) than monolithic glass ($m=2.5$), representing a more gradual transition to failure.

---

## Section 15: Software Engineer Questions & Responses

*   **Q: How does the application handle solver hangs?**
    *   *A*: Electron pings the solver every 10 seconds. If a response is not received within 5 seconds, the runner terminates the process and spawns a new instance.
*   **Q: How are database schema changes managed safely?**
    *   *A*: The application uses a migration framework that logs applied schema versions to `migration_history` and automatically creates backups before running schema modifications.
