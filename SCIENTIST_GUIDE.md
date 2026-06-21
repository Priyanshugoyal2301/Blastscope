# BlastScope Blast Physics & Structural Response Scientific Reference Guide (v1.0.0)

This reference guide is compiled for blast physics researchers, defense scientists, and structural safety engineers. It details the scientific foundations, mathematical formulations, thermodynamic assumptions, empirical models, and material response criteria implemented in the BlastScope desktop simulation suite.

---

## 1. Core Physics & Solver Features

### 1.1 Standoff Scaling and TNT Equivalency (Hopkinson-Cranz Model)

#### 1.1.1 Scientific Purpose
 Detonation of a high explosive (HE) releases a high-pressure detonation wave that expands into the surrounding atmosphere, forming a shock front. Standoff scaling normalizes blast wave properties across varying charge weights and distances, allowing arbitrary threat scenarios to be evaluated using standard reference data (usually TNT).

#### 1.1.2 Inputs
*   $W_{\text{actual}}$: Actual charge weight of the explosive agent ($kg$).
*   $R$: Physical standoff distance from the detonation center to the target ($m$).
*   Explosive Agent coefficients: Pressure-specific equivalency ($e_p$), Impulse-specific equivalency ($e_i$), and General energy equivalency ($e_g$).

#### 1.1.3 Units
*   Standoff Range $R$: Meters ($m$)
*   Charge Weight $W$: Kilograms ($kg$)
*   Scaled Distance $Z$: Meters per cube-root of kilograms ($m/\text{kg}^{1/3}$)
*   Equivalency Factors: Dimensionless ($e \in [0.4, 2.0]$)

#### 1.1.4 Assumptions
1.  **Point Source Detonation**: The explosive charge is assumed to be a sphere (free-air) or hemisphere (surface burst) concentrated at a single geometric point.
2.  **Isotropic Expansion**: Shock waves expand spherically or hemispherically without reflection off secondary obstacles, topographical features, or atmospheric gradients.
3.  **Perfect Reflection (for Surface Bursts)**: The detestation ground plane is rigid and non-deformable. No energy is lost to cratering, ground shock wave propagation, or soil displacement.
4.  **Ambient Atmosphere Standard**: Ambient pressure ($P_0$) is exactly $101.325\text{ kPa}$ (1.0 atm) and ambient temperature is $15^\circ\text{C}$.

#### 1.1.5 Equations
The Hopkinson-Cranz scaled distance $Z$ is computed as:
$$Z = \frac{R}{W_{\text{eq}}^{1/3}}$$
Where the equivalent charge weight $W_{\text{eq}}$ is scaled using specific equivalency factors based on the target blast parameter:
*   For Peak Incident and Reflected Pressures:
    $$W_{\text{eq, pressure}} = W_{\text{actual}} \times e_p$$
*   For Positive Phase Impulses:
    $$W_{\text{eq, impulse}} = W_{\text{actual}} \times e_i$$
*   For General Standoff Reports and Boundary Sweeps:
    $$W_{\text{eq, general}} = W_{\text{actual}} \times e_g$$

Dual scaling resolves the physical discrepancy of non-TNT agents, which release their chemical energy at rates different from pure TNT, resulting in separate pressure and impulse scaling factors.

#### 1.1.6 References
*   **DoD UFC 3-340-02 (2008)**: *Structures to Resist the Effects of Accidental Detonations*, US Department of Defense.
*   **Baker, W. E. (1973)**: *Explosions in Air*, University of Texas Press.
*   **Hopkinson, B. (1915)**: *British Ordnance Board Minutes 13565*.
*   **Cranz, C. (1926)**: *Lehrbuch der Ballistik*, Springer-Verlag.

#### 1.1.7 Outputs
*   $W_{\text{eq}}$: Equivalent TNT charge weights ($kg$) for pressure, impulse, and general scaling.
*   $Z_p, Z_i, Z_g$: Scaled distances ($m/\text{kg}^{1/3}$).

#### 1.1.8 Interpretation & Decision Support
*   **Physical Meaning**: Scaled distance ($Z$) represents the geometric similarity of the blast wave. A $1000\text{ kg}$ TNT charge at $10\text{ m}$ produces the same overpressure history as a $1\text{ kg}$ charge at $1\text{ m}$ ($Z = 1.0\text{ m/kg}^{1/3}$).
*   **Decisions**: Establishing safety perimeters. Standoff distances must ensure that target structures lie in regions where $Z$ is large enough to drop peak loading demands below structural capacities.
*   **Key Assumptions**: Ground hardness. If a surface burst occurs on soft clay rather than concrete, a portion of the blast energy goes into ground deformation (cratering), which reduces air-blast parameters. Consequently, calculations using this model are conservative.

#### 1.1.9 Limitations
*   Invalid in the extreme near-field ($Z < 0.05\text{ m/kg}^{1/3}$), where blast physics are dominated by high-pressure detonation products rather than classical shock waves.
*   Does not account for non-spherical charges (e.g., cylindrical shells), which produce non-uniform directional blast distributions.

---

### 1.2 Overpressure and Impulse Prediction (Kingery-Bulmash Model)

#### 1.2.1 Scientific Purpose
Calculates free-field blast wave parameters at a given scaled distance. The Kingery-Bulmash curves are the global standard for predicting incident overpressure, reflected overpressure, arrival time, positive duration, and impulse.

#### 1.2.2 Inputs
*   $Z$: Scaled distance ($m/\text{kg}^{1/3}$).
*   Burst Type: 'Free Air' (spherical expansion) or 'Surface' (hemispherical expansion).

#### 1.2.3 Units
*   Peak Incident Overpressure ($P_{so}$): Kilopascals ($kPa$)
*   Peak Reflected Overpressure ($P_r$): Kilopascals ($kPa$)
*   Positive Impulse ($i_s$): Kilopascal-milliseconds ($kPa\cdot ms$)
*   Arrival Time ($t_a$): Milliseconds ($ms$)
*   Positive Phase Duration ($t_d$): Milliseconds ($ms$)

#### 1.2.4 Assumptions
1.  **Ideal Gas Air Behavior**: Air behaves as a semi-perfect gas.
2.  **Polynomial Curve Fitting**: The digitized parameters are accurately represented by the Swisdak (1994) piecewise polynomial fits of the original Kingery-Bulmash curves.

#### 1.2.5 Equations
Shock parameters are evaluated using Swisdak polynomial coefficients:
$$U = \ln(Z)$$
$$\ln(Y) = C_0 + C_1 U + C_2 U^2 + C_3 U^3 + C_4 U^4$$
$$Y = \exp\left(\sum_{j=0}^4 C_j U^j\right)$$
Where $Y$ represents the blast parameter ($P_{so}, P_r, i_s, t_a, t_d$) and $C_j$ represents the fit coefficients.

To resolve reflection at normal incidence, the Rankine-Hugoniot pressure reflection relationship is evaluated:
$$P_r = 2 P_{so} \left( \frac{7 P_0 + 4 P_{so}}{7 P_0 + P_{so}} \right)$$
Where $P_0 = 101.325\text{ kPa}$ is ambient atmospheric pressure.

Rankine-Hugoniot Dynamic Pressure ($Q$), representing transient wind force behind the shock front, is computed as:
$$Q = \frac{2.5 P_{so}^2}{7 P_0 + P_{so}}$$

#### 1.2.6 References
*   **Kingery, C. N., & Bulmash, G. (1984)**: *Airblast Parameters from Spherical Blue Ripple Detonations*, BRL-TR-2555, Ballistic Research Laboratory.
*   **Swisdak, M. M. (1994)**: *Simplified Kingery-Bulmash Calculations*, NSWCDD/TR-93/363, Naval Surface Warfare Center.

#### 1.2.7 Outputs
*   Incident pressure ($P_{so}$), reflected pressure ($P_r$), dynamic pressure ($Q$), positive impulse ($i_s$), positive duration ($t_d$), negative duration ($t_{d,-}$), and arrival time ($t_a$).

#### 1.2.8 Interpretation & Decision Support
*   **Physical Meaning**: Overpressure ($P_{so}$) represents the pressure rise above ambient atmospheric conditions. Reflected pressure ($P_r$) accounts for the dynamic stagnation of the high-speed air mass striking a solid wall. Dynamic pressure ($Q$) represents the drag force exerted on slender structures (like towers).
*   **Decisions**: Building cladding design. Glazing must resist the reflected overpressure $P_r$, whereas structural columns may only experience incident overpressure $P_{so}$ plus dynamic drag $Q$ as the shock wave wraps around them.
*   **Key Assumptions**: Ideal shock reflection. If the wall is inclined relative to the shock front propagation path (non-normal incidence), oblique reflection occurs, reducing the peak reflected pressure. The normal incidence assumption ($90^\circ$) represents the worst-case scenario.

#### 1.2.9 Limitations
*   Valid range is bounded by $0.05 \le Z \le 40\text{ m/kg}^{1/3}$.
*   Does not model gas flow around complex geometries (shielding or diffraction).

---

### 1.3 Shock Wave Time-History (Modified Friedlander Curve)

#### 1.3.1 Scientific Purpose
Reconstructs the continuous pressure-time profile $P(t)$ of the shock wave. This is critical for dynamic structural calculations (like SDOF solvers or FEA), which require pressure histories rather than just peak values.

#### 1.3.2 Inputs
*   Peak Incident Overpressure ($P_{so}$) or Peak Reflected Overpressure ($P_r$).
*   Positive Phase Duration ($t_d$).
*   Positive Impulse ($i_s$).

#### 1.3.3 Units
*   Time $t$: Milliseconds ($ms$)
*   Decay parameter $b$: Dimensionless

#### 1.3.4 Assumptions
1.  **Discontinuous Shock Front**: The pressure rises instantaneously to its peak value at $t = t_a$.
2.  **Smooth Exponential Decay**: The decay of the positive phase is represented by a single exponential term, omitting high-frequency turbulence.

#### 1.3.5 Equations
The overpressure history is modeled using the Modified Friedlander equation:
$$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
Where the decay parameter $b$ is solved numerically to satisfy:
$$i_s = \int_0^{t_d} P(t) dt = P_{so} \frac{t_d}{b^2} \left(b - 1 + e^{-b}\right)$$

#### 1.3.6 References
*   **Friedlander, F. G. (1946)**: *The Diffraction of Sound Pulses I. Diffraction by a Semi-infinite Plane*, Proceedings of the Royal Society of London. Series A.

#### 1.3.7 Outputs
*   Continuous overpressure time-series data $P(t)$.
*   Decay parameter $b$.

#### 1.3.8 Interpretation & Decision Support
*   **Physical Meaning**: The shape of the pressure wave. A high $b$ value indicates rapid decay, which is typical of far-field blast waves, while a low $b$ value yields a more linear decay curve, representing prolonged loading.
*   **Decisions**: Dynamic load modeling. Used to determine the dynamic load history for SDOF analysis.
*   **Key Assumptions**: Single positive phase. The model neglects the negative (suction) phase, which can cause rebound damage in flexible panels.

#### 1.3.9 Limitations
*   Only models standard spherical or hemispherical free-field profiles. It cannot model complex blast wave shapes, such as those that result from internal reflections in enclosed spaces.

---

## 2. Material Response & Vulnerability Models

### 2.1 Hyperbolic Pressure-Impulse (P-I) Damage Curves

#### 2.1.1 Scientific Purpose
Predicts structural damage levels by comparing peak pressure loading (force demand) against impulse loading (energy demand). This approach accounts for the dynamic response characteristics of structures, which behave differently depending on whether they are loaded impulsively, dynamically, or quasi-statically.

#### 2.1.2 Inputs
*   Peak loading demand: Overpressure ($P$) and Impulse ($I$).
*   Material-specific thresholds: Static pressure limits ($P_{threshold}$) and impulse limits ($I_{threshold}$) for minor, moderate, severe, and failure damage states.

#### 2.1.3 Units
*   Pressure Asymptote $P_0$: Kilopascals ($kPa$)
*   Impulse Asymptote $I_0$: Kilopascal-milliseconds ($kPa\cdot ms$)
*   Dynamic Curve Constant $K_c$: Kilopascals-squared milliseconds ($kPa^2\cdot ms$)

#### 2.1.4 Assumptions
1.  **Hyperbolic Damage Boundary**: The boundary between damage states follows a hyperbolic form in the P-I domain.
2.  **Asymptote Scaling**: The dynamic asymptotes are proportional to the static capacity thresholds ($P_0 = 0.70 \times P_{threshold}, I_0 = 0.70 \times I_{threshold}$).
3.  **Single Degree of Freedom (SDOF) Equivalency**: The component is assumed to behave as an equivalent mass-spring system, neglecting higher-order structural vibration modes.

#### 2.1.5 Equations
The damage boundary is defined by the hyperbolic equation:
$$(P - P_0)(I - I_0) = K_c$$
Where:
$$P_0 = 0.70 \times P_{threshold}$$
$$I_0 = 0.70 \times I_{threshold}$$
$$K_c = (P_{threshold} - P_0)(I_{threshold} - I_0)$$

For any threat point $(P_{\text{actual}}, I_{\text{actual}})$, the damage state is exceeded if:
$$I_{\text{actual}} > I_0 \quad \text{and} \quad P_{\text{actual}} \ge P_0 + \frac{K_c}{I_{\text{actual}} - I_0}$$

```
   Pressure (P)
      ^
      |      / Exceeded Damage Zone
      |     /  (Structural Damage / Failure)
      |    / 
  P_t |---+  . (Actual Threat Point)
      |   | \
  P_0 | - - - - - - - - - Asymptote (Dynamic Load Limit)
      |   |   \
      |   |    \ Safe Zone
      |   |     \
      +---+---------------------> Impulse (I)
         I_0  I_t
```

#### 2.1.6 References
*   **Mays, G. C., & Smith, P. D. (1995)**: *Blast Effects on Buildings*, Thomas Telford Publications.
*   **ASCE (2010)**: *Design of Blast-Resistant Buildings in Petrochemical Facilities*, American Society of Civil Engineers.

#### 2.1.7 Outputs
*   Exceeded damage states (Safe, Minor, Moderate, Severe, Failure).
*   Dynamic Damage Index ($DI = \max(P_{\text{ratio}}, I_{\text{ratio}})$).

#### 2.1.8 Interpretation & Decision Support
*   **Physical Meaning**: Represents three dynamic loading regimes:
    1.  **Impulsive Regime ($t_d \ll T_n$)**: Loading duration is much shorter than the natural period of the structure ($T_n$). Damage is governed by impulse ($I$).
    2.  **Quasi-Static/Pressure Regime ($t_d \gg T_n$)**: Loading duration is much longer than $T_n$. Damage is governed by peak pressure ($P$).
    3.  **Dynamic/Transition Regime ($t_d \approx T_n$)**: Damage depends on both pressure and impulse.
*   **Decisions**: Retrofitting design. If a wall falls in the impulsive regime, increasing its mass can improve resistance; if it falls in the pressure-sensitive regime, increasing its structural stiffness is more effective.
*   **Key Assumptions**: The boudary fits are derived for standard rectangular structural panels. Complex or irregular geometries can deviate from this hyperbolic model.

#### 2.1.9 Limitations
*   Does not model cumulative damage from progressive collapse or multiple sequential blasts.

---

### 2.2 Weibull Glazing Fragility Model

#### 2.2.1 Scientific Purpose
Glazing is typically the most vulnerable element of a building facade. The Weibull glazing fragility model predicts glass breakage probabilities by accounting for the brittle behavior of glass and the distribution of microscopic surface flaws.

#### 2.2.2 Inputs
*   Actual blast loading demand: Reflected overpressure ($P_r$) and positive impulse ($i_s$).
*   Glazing type (Monolithic Annealed vs. Laminated).
*   Glazing thresholds ($P_{\text{threshold}}, I_{\text{threshold}}$).

#### 2.2.3 Units
*   Damage Index ($DI$): Dimensionless
*   Glazing Breakage Probability ($P_b$): Dimensionless ($P_b \in [0.0, 1.0]$)

#### 2.2.4 Assumptions
1.  **Weibull Distribution**: Glass fracture probability follows a two-parameter Weibull distribution.
2.  **Flaw Distribution**: Surface defects are uniformly distributed, making larger panes more vulnerable.
3.  **Ductile PVB Interlayer**: Laminated glass is tougher and more ductile due to the plastic polyvinyl butyral (PVB) interlayer, which prevents shard scattering.

#### 2.2.5 Equations
The glass breakage probability ($P_b$) is computed as:
$$P_b = 1.0 - e^{-0.693 (DI)^m}$$
Where:
$$DI = \max\left(\frac{P_{\text{actual}}}{P_{\text{threshold}}}, \frac{I_{\text{actual}}}{I_{\text{threshold}}}\right)$$
*   $m = 2.5$ for Monolithic Annealed Glass (representing brittle fracture behavior).
*   $m = 1.8$ for Laminated Glass (representing ductile PVB interlayer tearing).

The hazard classification is mapped based on the computed breakage probability:
*   $P_b < 0.05 \implies$ **Glazing Safe** (negligible risk of breakage).
*   $0.05 \le P_b < 0.50 \implies$ **Low Hazard** (moderate breakage probability, shards remain largely contained).
*   $P_b \ge 0.50 \implies$ **High Hazard** (high breakage probability, risk of high-velocity shard scattering).

#### 2.2.6 References
*   **ISO 16933:2007**: *Glass in Building — Explosion-Resistant Security Glazing*, International Organization for Standardization.
*   **ASTM E1300**: *Standard Practice for Determining Load Resistance of Glass in Buildings*.
*   **FEMA 426**: *Reference Manual to Mitigate Potential Terrorist Attacks Against Buildings*.

#### 2.2.7 Outputs
*   Glazing Breakage Probability ($P_b$).
*   Glazing Hazard Category (Glazing Safe, Low Hazard, High Hazard).

#### 2.2.8 Interpretation & Decision Support
*   **Physical Meaning**: $P_b$ represents the probability that a glass pane will fracture under the design load.
*   **Decisions**: Facade design. High hazard classifications require switching to laminated glass, applying anti-shatter window film, or increasing the standoff distance.
*   **Key Assumptions**: The model assumes standard pane dimensions (typically $1.2\text{ m} \times 1.5\text{ m}$). Larger windows will experience higher breakage rates due to the statistical likelihood of surface flaws.

#### 2.2.9 Limitations
*   Does not model the trajectory or velocity of scattered shards.

---

## 3. Chart & Plot Interpretations

### 3.1 Blast Overpressure Decay Plot (Friedlander Curve)

```
  Overpressure (P)
     ^
  Pso|  |
     |   \ Positive Phase
     |    \  (Compressed air pushes outward)
     |     \
     |      \           Positive Duration (td)
   P0+-------\----------------+------------------> Time (t)
     |  ta    \              /  Negative Phase
     |         \____________/     (Suction / dynamic rebound)
     |<------->|
    Arrival (ta)
```

1.  **Physical Meaning**: Illustrates the pressure wave profile at a target location. Shows the arrival time ($t_a$), the shock front ($P_{so}$), and the positive phase duration ($t_d$).
2.  **Interpretation**:
    *   **Discontinuous Rise**: Represents the shock front.
    *   **Area Under positive curve**: Represents positive impulse ($i_s$).
    *   **Negative Suction Phase**: Below ambient pressure ($P_0$). This phase can pull lightweight cladding elements off structures.
3.  **Decisions**: Helps identify structural vulnerability to suction forces and dynamic rebound, which can trigger flexural failures during the negative phase.
4.  **Assumptions**: Spherical wave expansion, standard atmosphere.

---

### 3.2 Pressure-Impulse (P-I) Overlay Plot

1.  **Physical Meaning**: Maps structural demand against capacity.
2.  **Interpretation**:
    *   **Hyperbolic Curves**: Represent the boundaries between different damage levels (Minor, Moderate, Severe, Failure).
    *   **Target Point**: Represents the loading demand $(P, I)$ for the active scenario.
    *   **Positioning**: A target point located above a curve indicates that the structure is predicted to exceed that damage level.
3.  **Decisions**: Used to select materials. If the threat point lies above the concrete failure curve, designers must increase panel thickness or reinforcement.
4.  **Assumptions**: Single degree of freedom (SDOF) approximation.

---

### 3.3 Vulnerability Map Heatmap

1.  **Physical Meaning**: Spatial footprint of damage around a detonation point.
2.  **Interpretation**:
    *   **Color coding**: Indicates damage severity (Safe = Green, Failure = Red/Dark Red).
    *   **Spatial extent**: Displays the radius of each damage zone.
3.  **Decisions**: Used for building placement, facility layout optimization, and establishing safe standoffs.
4.  **Assumptions**: Isotropic wave propagation, flat topography, no shielding.

---

### 3.4 Standoff/Charge Sweeps (1D Sensitivity Curves)

1.  **Physical Meaning**: Illustrates how material damage changes with variations in standoff distance or charge weight.
2.  **Interpretation**:
    *   **Standoff Sweep**: Damage decreases as distance increases.
    *   **Charge Sweep**: Damage increases with charge weight.
    *   **Steep slopes**: Indicate sensitivity to small parameter changes.
3.  **Decisions**: Helps establish minimum safe standoffs.
4.  **Assumptions**: Single parameter variation.

---

### 3.5 Multi-Scenario Overlay and Radar Charts

1.  **Physical Meaning**: Renders comparative threat profiles.
2.  **Interpretation**:
    *   **Radar Axis**: Shows relative severity across parameters (pressure, impulse, weight, distance).
    *   **Expansion**: Highlights which threat is more severe in different distance regimes.
3.  **Decisions**: Supports risk assessment and threat prioritization.
4.  **Assumptions**: Normalization ranges.

---

## 4. Scientific Assumptions & Model Limitations

| Model / Feature | Key Assumptions | Physical Limitations |
|---|---|---|
| **Standoff Scaling ($Z$)** | Spherical expansion; rigid ground reflection. | Near-field singularities ($Z < 0.05$); ignores soil cratering losses. |
| **Kingery-Bulmash Curve fits** | Polynomial representation; standard atmosphere. | Fits are limited to $0.05 \le Z \le 40$; does not model complex geometries. |
| **P-I Hyperbolic Envelopes** | Hyperbolic damage boundaries; asymptote scaling. | Single degree of freedom (SDOF) approximation; neglects higher-order vibration modes. |
| **Glazing Fragility Model** | Two-parameter Weibull distribution; standard panel dimensions. | Assumes standard pane size; does not model shard trajectory. |
| **Spatial Vulnerability Map** | Isotropic wave propagation; flat topography. | Neglects building shielding, channel effects, and reflections. |
