# BlastScope Plot Reference Guide (v1.0.0)

This guide documents the data structures, visual layouts, and plotting logic implemented in BlastScope's chart components.

---

## 1. Blast Curve Plot (`src/components/plots/BlastCurvePlot.tsx`)
*   **Purpose**: Plots the pressure-time decay history of the shock wave.
*   **Data Structure**: An array of 300 coordinate objects:
    ```typescript
    interface DataPoint {
      time: number;       // ms
      pressure: number;   // kPa or psi
    }
    ```
*   **Plotting Logic**: Plots the wave profile from $t = 0$ to $t = 1.5 \times t_d$ using the Modified Friedlander equation.
*   **Visual Highlights**:
    *   Y-Axis: Overpressure ($kPa$ or $psi$).
    *   X-Axis: Time ($ms$).
    *   Annotations: Displays markers for peak overpressure ($P_{so}$), positive phase duration ($t_d$), and arrival time ($t_a$).

---

## 2. Pressure-Impulse (P-I) Plot (`src/components/plots/PIPlot.tsx`)
*   **Purpose**: Plots structural loading demand against material capacity curves.
*   **Data Structure**:
    *   Curves array containing coordinate points generated from the hyperbola equation:
        $$P = P_0 + \frac{K_c}{I - I_0}$$
    *   Scatter point representing the active threat scenario $(P_{\text{actual}}, I_{\text{actual}})$.
*   **Plotting Logic**: Uses logarithmic scales to plot curves for Minor, Moderate, Severe, and Failure boundaries.
*   **Visual Highlights**: Shows the threat point relative to the capacity curves, highlighting the predicted damage state.

---

## 3. Parametric Sweep Plot (`src/components/plots/SweepPlot.tsx`)
*   **Purpose**: Plots damage indexes or severity scores across varying standoffs or charge weights.
*   **Data Structure**:
    ```typescript
    interface SweepPoint {
      sweep_variable: number;     // standoff (m) or weight (kg)
      damage_index: number;       // ratio
      severity_score: number;     // probability or dynamic indicator
    }
    ```
*   **Plotting Logic**: Connects values along a line chart to illustrate sensitivity to parameter changes.

---

## 4. Grid Sweep Heatmap (`src/components/plots/HeatmapPlot.tsx`)
*   **Purpose**: A 2D matrix displaying damage levels across varying charges and standoffs.
*   **Data Structure**: 2D grid matrix of calculation points.
*   **Plotting Logic**: Colors grid cells based on the predicted damage state:
    *   **Safe**: Green
    *   **Minor**: Yellow
    *   **Moderate**: Orange
    *   **Severe**: Red
    *   **Failure**: Dark Red
*   **Visual Highlights**: Enables users to identify safe boundaries at a glance.

---

## 5. Comparison Radar Plot (`src/components/plots/RadarPlot.tsx`)
*   **Purpose**: Compares parameters (peak pressure, impulse, duration, weight, distance) across multiple scenarios.
*   **Data Structure**: Normalized attributes mapped radially.
*   **Plotting Logic**: Plots parameters on normalized radial axes to visualize relative severity.
