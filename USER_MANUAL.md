# BlastScope User Manual & Operational Guide

Welcome to the **BlastScope** platform, an engineering tool for high-explosive blast characterization, structural vulnerability assessment, and threat reconstruction.

---

## 1. Interface Overview & Sidebar Navigation

BlastScope uses a clean sidebar navigation layout divided into six core operational screens:

* **Scenario Input**: Configure charge and standoff parameters.
* **Blast Results**: View overpressure decay profiles and temporal histories.
* **Material Assessment**: Analyze damage risks for structural materials and biological targets.
* **Research Workspace**: View comparative radar charts and the model validation benchmark suite.
* **Parametric Study**: Execute multi-point grid sweeps and visualize safety zones.
* **Threat Prediction**: Reconstruct blast source weight and distance from sensor signatures using the inverse ML model.

---

## 2. Core Operational Screens

### 2.1 Scenario Input (Physics Solver Setup)
Configure the blast source parameters to initialize calculations:
1. **Scenario Name**: Enter a descriptive name (e.g. `Main Entrance Test`).
2. **Explosive Charge Weight**: Weight of the explosive in kilograms (kg).
3. **Standoff Distance**: Distance from the detonation center to the target in meters (m).
4. **Explosive Agent Selection**: Choose from TNT, C4, RDX, HMX, ANFO, PETN, or Comp B. (The solver scales the weight dynamically using pressure/impulse equivalency factors).
5. **Burst Configuration**:
   * *Free-Air Burst*: Detonation occurs in open air; shock wave propagates spherically.
   * *Surface Burst*: Detonation occurs at or near the ground; ground reflection reflects energy, modeled as a hemispherical burst.
6. Click **Save Scenario** to persist the configuration in the local database. The scenario will appear in the sidebar list for quick access.

### 2.2 Blast Results
This screen displays the primary physical blast wave signatures computed by the Kingery-Bulmash solver:
* **Peak Overpressures**: Incident peak ($P_{so}$) and Reflected peak ($P_r$) in kPa.
* **Impulses**: Incident scaled ($i_s$) and Reflected scaled ($i_r$) in kPa-ms.
* **Wave Timing**: Arrival time ($t_a$) and Positive phase duration ($t_d$) in ms.
* **Friedlander Temporal Curve**: The plot visualizes the transient overpressure decay:
  $$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
  The decay parameter $b$ is extracted numerically via a Newton-Raphson solver to match the physical impulse.

### 2.3 Material Assessment (P-I Vulnerability)
Evaluate structural and biological damage risk based on Pressure-Impulse ($P-I$) boundaries:
* Select a material profile (Glass, Brick Masonry, Reinforced Concrete, Structural Steel, or Human blast trauma).
* The tool plots the scenario's pressure and impulse against the material's damage asymptotes:
  $$(P - P_0)(I - I_0) = K_c$$
* **Damage State Classification**: The target is classified into a damage level: `Minor`, `Moderate`, `Severe`, or `Failure` (Collapse/Lethality).

### 2.4 Research Workspace & Validation Bench
* **Vulnerability Radar**: A radar chart comparing the normalized capacity thresholds of all structural materials, useful for comparing relative protective strengths.
* **Validation Suite**: Displays a list of 30 validation benchmark cases compiled from UFC 3-340-02 reference tables, ConWep, and NSWC field tests. The grid displays reference values side-by-side with BlastScope solver outputs, along with calculated relative error percentages.

### 2.5 Parametric Study & Safety Map
Execute multi-run sweeps to map safety exclusion zones:
1. Select **Range Sweep** (varying distance for a fixed charge) or **Grid Study** (varying weight and distance).
2. Define minimum, maximum, and step increments.
3. Click **Run Study**.
4. **Vulnerability Heatmap**: Renders a 3D/2D contour chart displaying safety zones and damage contours relative to structural collapse thresholds, allowing engineers to size safe stand-off distances.

### 2.6 Threat Prediction (Inverse ML Subsystem)
Reconstruct unknown blast source parameters from sensor readings:
1. **Sensor Readings Input**: Enter measured peak incident pressure, reflected pressure, arrival time, positive duration, incident impulse, and reflected impulse.
2. Select the burst type (**Free Air** or **Surface**).
3. Click **Characterize Threat**.
4. **Subsystem Outputs**:
   * **Reconstructed Charge Weight ($W$)**: Estimated explosive charge in kg TNT.
   * **Reconstructed Standoff Distance ($d$)**: Distance from sensor to blast center in m.
   * **Calibrated Confidence Score**: The empirical probability that the prediction is accurate within a 10% tolerance (calibrated via Isotonic Regression).
   * **OOD Warning**: Flags `OUT OF TRAINING DOMAIN` if the input features violate physical relationships (Mahalanobis distance) or exceed training bounds.

---

## 3. Data Export & Reports

* **PDF Engineering Report**: Click the **Export Report** button inside the Research Workspace or Results screen. The application compiles a structured PDF document containing input parameters, wave timing values, Friedlander decay plots, and material damage classifications.
* **CSV Batch Export**: Inside the Parametric Study screen, click **Export CSV** to download the raw multi-point sweep grid results for Excel or external hydrocode analysis.
