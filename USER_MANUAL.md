# BlastScope User Manual (v1.0.0)

This manual provides step-by-step instructions for performing blast safety assessments using the BlastScope platform.

---

## 1. Defining Blast Threat Scenarios
1.  Open the application and select **Configure Scenario** in the navigation bar.
2.  Enter a name for the scenario in the **Scenario Name** field.
3.  Select the **Explosive Type** from the dropdown menu (e.g. C4, ANFO, TNT).
4.  Enter the explosive charge mass in the **Charge Weight** field.
5.  Enter the standoff distance in the **Distance** field.
6.  Select the **Burst Type** (Free Air, Air, or Surface).
7.  Select the **Units System** (Metric vs. Imperial).
8.  Click **Compute & Save Scenario**. The saved scenario will appear in the sidebar list.

---

## 2. Analyzing Blast Wave Decay
1.  Navigate to the **Blast Results** screen.
2.  Review the calculation summary (incident pressure, reflected pressure, arrival time, positive duration).
3.  Inspect the **Pressure-Time Decay Plot** to visualize overpressure decay and positive duration.
4.  Use the dropdown menus to convert display units as needed (e.g. converting kPa to psi).

---

## 3. Assessing Material Vulnerability
1.  Navigate to the **Material Assessment** screen.
2.  Review the damage summary cards (displaying damage levels from Safe to Failure, failure modes, and severity scores).
3.  Select a material profile to plot its pressure-impulse (P-I) capacity envelopes.
4.  Review the threat coordinate overlay to identify the safety margin relative to capacity curves.

---

## 4. Conducting Parametric Sweeps
1.  Navigate to the **Parametric Study** screen.
2.  Select a sweep type (e.g. standoff sweeps, charge sweeps, 2D grid sweeps).
3.  Define the step ranges (minimum, maximum, and step size).
4.  Select target material profiles and click **Run Sweep**.
5.  Review the vulnerability rankings and safety thresholds.
6.  Click **Export CSV** to save the calculations to disk.

---

## 5. Mapping Spatial Vulnerability
1.  Navigate to the **Vulnerability Map** screen.
2.  Select the active scenario and target material profile.
3.  Zoom or pan the map to center the detonation point.
4.  Hover over grid cells to inspect spatial safety distances and hazard zones.
