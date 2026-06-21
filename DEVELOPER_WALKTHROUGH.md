# BlastScope Developer Walkthrough & UI Control Guide (v1.0.0)

This developer walkthrough explains the front-to-back execution cycle of BlastScope's user interface. It catalogues every button, dropdown, table, chart, and modal across all screens, explaining the underlying code hooks, Inter-Process Communication (IPC) channels, SQLite tables, calculation engines, and generated outputs.

---

## 1. Global Navigation & Sidebar (`src/components/Sidebar.tsx`)

The sidebar handles global navigation, scenario management, and database import/export commands.

### 1.1 UI Controls & Interactive Elements

#### 1.1.1 Navigation Tab Items
*   **What it does**: Switches the active screen display (Input, Blast Results, Material Assessment, Research, Parametric, Vulnerability Map, Documentation).
*   **Which code executes**: Triggers `setActiveTab(tabId)` inside `src/App.tsx`.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Updates local React state, causing the router to mount the corresponding screen component.

#### 1.1.2 Scenario History Selection List
*   **What it does**: Loads a previously saved blast threat scenario as the active project.
*   **Which code executes**: Triggers `onSelectScenario(scenario)` inside `src/components/Sidebar.tsx`.
*   **Which IPC call runs**: Triggers `scenarios:listNotes` to fetch associated commentary.
*   **Which database tables are touched**: `scenarios` (SELECT), `notes` (SELECT).
*   **Which calculations run**: None.
*   **Which outputs are generated**: Updates the active scenario context across all pages, refreshing result overlays, plots, and assessments.

#### 1.1.3 "Export Database" Button
*   **What it does**: Opens a native OS dialog box to backup the active SQLite database.
*   **Which code executes**: Triggers `handleExportDB()` inside `src/components/Sidebar.tsx` and handles copy operations in `electron/main.ts`.
*   **Which IPC call runs**: `database:export`
*   **Which database tables are touched**: All active database tables are copied as a single file.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Generates a duplicate `.db` file at the user's chosen location.

#### 1.1.4 "Import Database" Button
*   **What it does**: Prompts the user to select a backed-up `.db` file, replacing the active project database.
*   **Which code executes**: Triggers `handleImportDB()` inside `src/components/Sidebar.tsx`.
*   **Which IPC call runs**: `database:import`
*   **Which database tables are touched**: Overwrites all tables in the active SQLite file (`%APPDATA%/BlastScope/sqlite.db`).
*   **Which calculations run**: None.
*   **Which outputs are generated**: Safely stops the Python runner to release database locks, replaces the active file, and restarts the runner.

---

## 2. Screen: Configure Scenario (`src/screens/ScenarioInput.tsx`)

This screen captures physical parameters to establish detonation threats.

```
   +------------------------------------+------------------------------------+
   |         Configure Scenario         |         Research Notebook          |
   |                                    |                                    |
   |  Name: [ Concrete Slab Test A   ]  |  [Type note here...      ] [Add]   |
   |  Agent: [ TNT                 v ]  |                                    |
   |  Weight (kg): [ 100             ]  |  * [12:04:12] Test Case A:         |
   |  Distance (m): [ 20             ]  |    Validated against UFC Figure    |
   |  Burst: [ Surface Burst       v ]  |    2-15 curves.                    |
   |  Units: (x) Metric   ( ) Imperial  |                                    |
   |                                    |                                    |
   |       [Compute & Save Scenario]    |                                    |
   +------------------------------------+------------------------------------+
```

### 2.1 UI Controls & Interactive Elements

#### 2.1.1 "New" Scenario Button
*   **What it does**: Clears current input fields, sets parameters to default values, and prepares the form to save a new record.
*   **Which code executes**: `handleCreateNew()` inside `ScenarioInput.tsx`.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Resets input states to default values ($W = 100\text{ kg}$, $R = 20\text{ m}$, Surface Burst, Metric units).

#### 2.1.2 "Explosive Type" Dropdown
*   **What it does**: Selects the explosive compound to scale.
*   **Which code executes**: `setExplosiveId(Number(e.target.value))` inside `ScenarioInput.tsx`.
*   **Which IPC call runs**: None (reads seed data loaded at startup via `explosives:list`).
*   **Which database tables are touched**: `explosives`.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Changes the active explosive ID in the local form state.

#### 2.1.3 "Units System" Radio Buttons
*   **What it does**: Switches input labels and placeholders between Metric ($kg, m$) and Imperial ($lb, ft$).
*   **Which code executes**: `setUnitSystem(value)` inside `ScenarioInput.tsx`.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Updates labels on the form interface.

#### 2.1.4 "Compute & Save Scenario" Button
*   **What it does**: Validates inputs, saves the scenario, calculates blast environment parameters, and runs material damage assessments.
*   **Which code executes**: `handleSaveScenario(e)` inside `ScenarioInput.tsx`.
*   **Which IPC call runs**: `scenarios:save`
*   **Which database tables are touched**:
    *   `scenarios` (INSERT or UPDATE)
    *   `scenario_results` (INSERT or UPDATE)
    *   `material_assessments` (INSERT or UPDATE)
*   **Which calculations run**:
    *   TNT weight scaling: $W_p = W \cdot e_p$, $W_i = W \cdot e_i$, $W_g = W \cdot e_g$.
    *   Scaled distances: $Z_p = R / W_p^{1/3}$, $Z_i = R / W_i^{1/3}$, $Z_g = R / W_g^{1/3}$.
    *   Polynomial fitting for overpressure, impulse, duration, and arrival times.
    *   Rankine-Hugoniot reflected overpressure and dynamic wind force calculations.
    *   Progressive material damage assessment and glass failure probability.
*   **Which outputs are generated**: Inserts results into the SQLite cache, updates the sidebar list, and returns assessment records.

#### 2.1.5 "Add Note" Button (Research Notebook)
*   **What it does**: Saves a researcher's commentary linked to the active scenario.
*   **Which code executes**: `handleAddNote(e)` inside `ScenarioInput.tsx`.
*   **Which IPC call runs**: `scenarios:saveNote`
*   **Which database tables are touched**: `notes` (INSERT).
*   **Which calculations run**: None.
*   **Which outputs are generated**: Adds a new note to the SQLite database and refreshes the scrollable notebook view.

---

## 3. Screen: Blast Results (`src/screens/BlastResults.tsx`)

This screen displays calculated shock wave metrics and outputs the positive phase pressure-time decay curve.

### 3.1 UI Controls & Interactive Elements

#### 3.1.1 "Pressure Units" / "Impulse Units" Dropdowns
*   **What it does**: Converts display metrics on the fly (e.g. from kPa to psi or bar).
*   **Which code executes**: `api.units.convert` routing wrapper inside the screen file.
*   **Which IPC call runs**: `units:convert`
*   **Which database tables are touched**: None (calculates using in-memory parameters).
*   **Which calculations run**: Divides the metric base value by the target conversion factor.
*   **Which outputs are generated**: Refreshes screen labels with converted parameters.

#### 3.1.2 Blast Curve Plot (`src/components/plots/BlastCurvePlot.tsx`)
*   **What it does**: Renders an interactive overpressure decay curve showing pressure values over time.
*   **Which code executes**: `BlastCurvePlot` component renders using the Recharts library.
*   **Which IPC call runs**: None (uses calculations passed from frontend state).
*   **Which database tables are touched**: None.
*   **Which calculations run**:
    *   Decay parameter $b$ is calculated numerically.
    *   Evaluates the Modified Friedlander equation:
        $$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
        Across 300 points spanning from $t = 0$ to $t = 1.5 \times t_d$.
*   **Which outputs are generated**: Generates SVG paths to plot the curve, highlighting the arrival time, positive duration, and peak overpressure.

---

## 4. Screen: Material Assessment (`src/screens/MaterialAssessment.tsx`)

This screen displays damage levels, failure modes, and plots pressure-impulse (P-I) envelopes.

### 4.1 UI Controls & Interactive Elements

#### 4.1.1 Material Profile Selection Cards
*   **What it does**: Updates the screen details and chart to display information for the selected material profile.
*   **Which code executes**: Updates state variables `selectedProfileId` and `selectedProfileName`.
*   **Which IPC call runs**: `materials:getPIEnvelopes`
*   **Which database tables are touched**: `material_response_curves` (SELECT), `sources` (SELECT).
*   **Which calculations run**:
    *   Calculates 300 plotting coordinates along the hyperbola:
        $$P = P_0 + \frac{K_c}{I - I_0}$$
        For each damage state (Minor, Moderate, Severe, Failure).
*   **Which outputs are generated**: Generates coordinates array for the P-I curves.

#### 4.1.2 P-I Plot Overlay (`src/components/plots/PIPlot.tsx`)
*   **What it does**: Plots structural demand against capacity envelopes.
*   **Which code executes**: Recharts plotting logic in `PIPlot.tsx`.
*   **Which IPC call runs**: None (uses pre-fetched curves data).
*   **Which database tables are touched**: None.
*   **Which calculations run**: Formats overpressure and impulse coordinates onto logarithmic axes.
*   **Which outputs are generated**: Dynamic scatter chart overlaying the scenario threat coordinate $(P_{\text{actual}}, I_{\text{actual}})$ onto capacity curves.

---

## 5. Screen: Research Workspace (`src/screens/ResearchWorkspace.tsx`)

This screen compares multiple blast scenarios and runs verification benchmarks.

### 5.1 UI Controls & Interactive Elements

#### 5.1.1 Scenario Selection Checkboxes
*   **What it does**: Selects which scenarios are included in radar and multi-curve overlay plots.
*   **Which code executes**: Toggles scenario IDs inside `selectedScenarioIds` array state.
*   **Which IPC call runs**: `research:compareScenarios`
*   **Which database tables are touched**: `scenarios` (SELECT), `explosives` (SELECT).
*   **Which calculations run**: Evaluates blast parameters at 50 increments along the distance range ($R \in [1, 100]$ m) for each selected scenario.
*   **Which outputs are generated**: Array of distance-decay coordinates for compared scenarios.

#### 5.1.2 "Run Scientific Validation Sweep" Button
*   **What it does**: Runs validation tests against the benchmark database and outputs error statistics.
*   **Which code executes**: `handleRunValidation()` inside `ResearchWorkspace.tsx`.
*   **Which IPC call runs**: `validation:runSweep` followed by `validation:getSummary`.
*   **Which database tables are touched**: `validation_cases` (UPDATE), `model_versions` (SELECT).
*   **Which calculations run**:
    *   Calculates blast parameters for 30 historical trials.
    *   Computes absolute and relative errors against reference values.
    *   Computes overall and group-specific RMSE, Mean Error, and p95 limits.
*   **Which outputs are generated**: Updates validation records and displays error tables.

#### 5.1.3 Scenario Comparison Plot (`src/components/plots/ComparisonPlot.tsx`)
*   **What it does**: Overlays blast overpressure decay curves.
*   **Which code executes**: Renders comparison curves using Recharts.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: Formats compared overpressure curves.
*   **Which outputs are generated**: Interactive line chart.

---

## 6. Screen: Parametric Study (`src/screens/ParametricStudy.tsx`)

This screen configures and runs parameter sweeps and exports results to CSV.

### 6.1 UI Controls & Interactive Elements

#### 6.1.1 "Sweep Variable" Dropdown
*   **What it does**: Selects the parameter to vary (standoff distance vs. charge weight).
*   **Which code executes**: Sets the `sweepVariable` state variable.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: None.
*   **Which outputs are generated**: Updates form labels and input ranges.

#### 6.1.2 "Run Sweep/Grid Study" Button
*   **What it does**: Validates bounds, enforces calculations limits, and runs sweeps.
*   **Which code executes**: `handleRunSweep()` inside `ParametricStudy.tsx`.
*   **Which IPC call runs**: `studies:distanceSweep`, `studies:chargeSweep`, or `studies:runGrid`.
*   **Which database tables are touched**: `explosives` (SELECT), `material_profiles` (SELECT), `thresholds` (SELECT), `material_response_curves` (SELECT).
*   **Which calculations run**:
    *   Iterates through range steps, running blast and material damage assessments.
    *   Computes material vulnerability rankings and standoff limits.
*   **Which outputs are generated**: Returns an array of sweep results and vulnerability rankings.

#### 6.1.3 "Export CSV Results" Button
*   **What it does**: Exports sweep results as a CSV file.
*   **Which code executes**: `handleExportCSV()` inside `ParametricStudy.tsx`.
*   **Which IPC call runs**: `studies:exportCSV`
*   **Which database tables are touched**: None.
*   **Which calculations run**: Formats results to CSV.
*   **Which outputs are generated**: Writes a CSV file to disk.

---

## 7. Screen: Vulnerability Map (`src/screens/VulnerabilityMap.tsx`)

This screen visualizes spatial risk contours around a detonation center.

### 7.1 UI Controls & Interactive Elements

#### 7.1.1 Zoom and Pan Canvas Controls
*   **What it does**: Adjusts the scale and focus of the spatial map.
*   **Which code executes**: Redraws grid elements on the HTML5 canvas based on zoom states.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**: Computes coordinate transforms for canvas pixels.
*   **Which outputs are generated**: Updates the canvas display.

#### 7.1.2 Standoff Range Inspection Hover
*   **What it does**: Displays coordinates and damage levels as the mouse moves over the canvas.
*   **Which code executes**: Calculates the standoff distance at the mouse cursor position.
*   **Which IPC call runs**: None.
*   **Which database tables are touched**: None.
*   **Which calculations run**:
    *   Standoff distance: $R = \sqrt{(x - x_{\text{center}})^2 + (y - y_{\text{center}})^2} \times \text{scale}$.
*   **Which outputs are generated**: Displays coordinates and damage levels in a hover tooltip.
