# BlastScope Software Demonstration Storyboard

This storyboard outlines a 5-minute operational demonstration video showcasing the features, physics engine solver, and machine learning subsystem of the **BlastScope** platform.

---

## Storyboard Flow & Narration Script

### Scene 1: Introduction & Platform Welcome
* **Duration**: 0:00 – 0:30
* **Visual**: Close-up of the desktop launching the application. Show the clean, premium, dark-themed BlastScope UI loading to the **Scenario Input** home screen. Hover cursor over the sidebar navigation menu.
* **Action**:
  * Mouse highlights the sidebar navigation panel.
* **Narration Script**:
  > *"Welcome to BlastScope, a high-fidelity, self-contained desktop platform designed for blast wave propagation analysis, material vulnerability mapping, and inverse machine learning threat characterization. Today, we will walkthrough a complete engineering assessment from scenario definition to ML-powered threat reconstruction."*

---

### Scene 2: Scenario Input & Database Persistence
* **Duration**: 0:30 – 1:15
* **Visual**: The screen is on the **Scenario Input** tab. The operator enters:
  * Name: `Tactical Shelter Check`
  * Weight: `150` kg
  * Distance: `20` m
  * Explosive Agent: `C4`
  * Burst Type: `Surface Burst` (Hemispherical)
* **Action**: Clicks **Save Scenario**. The scenario name instantly appears in the sidebar history panel. The operator clicks on previous scenarios to show instant database reloading, then clicks back on `Tactical Shelter Check`.
* **Narration Script**:
  > *"We begin by configuring a blast scenario. Let's define a 150 kg C4 charge detonating at ground level, representing a hemispherical surface burst, 20 meters from our target structure. Saving the scenario commits it to our local SQLite database. We can see our scenario history persisted in the sidebar, allowing us to reload parameters instantly."*

---

### Scene 3: Forward Blast Solver & Decay Curves
* **Duration**: 1:15 – 2:00
* **Visual**: Transition to the **Blast Results** screen.
* **Action**: Highlight computed numerical fields (Incident Pressure: 104.9 kPa, Positive Duration: 23.4 ms). The operator hovers their cursor over the interactive **Friedlander Decay Profile** plot, showing data points along the temporal overpressure curve.
* **Narration Script**:
  > *"Switching to Blast Results, the Kingery-Bulmash solver displays our primary blast wave parameters. We see peak incident pressure, reflected pressure, timing, and scaled impulses. The interactive chart plots the temporal overpressure profile using the Modified Friedlander equation. Rather than using static approximations, BlastScope runs an embedded Newton-Raphson numerical solver to calculate the physical decay parameter, matching the physical positive impulse exactly."*

---

### Scene 4: Pressure-Impulse (P-I) Material Assessment
* **Duration**: 2:00 – 2:45
* **Visual**: Transition to the **Material Assessment** screen.
* **Action**: The operator opens the material dropdown and selects `Reinforced Concrete M30`, then `Glass 6mm Monolithic`, and finally `Human Vulnerability`. Show the plot coordinates of the current blast loading (104.9 kPa pressure, 450 kPa-ms impulse) relative to the colored damage asymptote contours.
* **Narration Script**:
  > *"Next, we evaluate structural and biological vulnerability on the Material Assessment screen. We select our material profile. The platform maps our scenario's pressure and impulse coordinates against the hyperbolic damage curves derived from UFC 3-340-02 and ISO guidelines. Our current blast loading is instantly classified. We see that while standard glazing fails, our reinforced concrete slab remains safe, and human personnel face moderate blast injury risk."*

---

### Scene 5: Parametric Studies & Vulnerability Heatmaps
* **Duration**: 2:45 – 3:30
* **Visual**: Transition to the **Parametric Study** screen, then the **Vulnerability Map** screen.
* **Action**: Click the **Grid Study** tab. Define ranges (Weight: 10 to 500 kg, Distance: 5 to 50 m). Click **Run Study**. Switch to the Vulnerability Map to display a beautiful 3D/2D contour safety heatmap showing concrete collapse regions.
* **Narration Script**:
  > *"For site layout optimization, we can run a Parametric Study. By defining a grid sweep over charge weights and standoffs, BlastScope evaluates hundreds of iterations. The Vulnerability Map visualizes the results as a contour heatmap, clearly marking safe standoff boundaries and collapse zones, assisting engineers in sizing exclusion zones."*

---

### Scene 6: Inverse ML Threat Characterization
* **Duration**: 3:30 – 4:30
* **Visual**: Transition to the **Threat Prediction** screen.
* **Action**:
  1. **In-Distribution Run**: Enter pressures and timings from a valid scenario (e.g., incident pressure: 44.0 kPa, positive duration: 58.4 ms). Click **Characterize Threat**. Displays Predicted Weight = ~100 kg, Distance = ~23 m, and Confidence = 95.0%.
  2. **OOD Run**: Enter corrupted/impossible parameters (e.g., incident pressure: 1000 kPa, arrival time: 1000 ms, duration: 1 ms). Click **Characterize Threat**. The screen immediately flags `OUT OF TRAINING DOMAIN` in red, and the confidence score drops to <= 15.0%.
* **Narration Script**:
  > *"When responding to a blast event, we often only have sensor readings. The Threat Prediction screen uses our Separate Trees Random Forest inverse model to reconstruct source parameters from wave signatures. Inputting consistent signatures yields highly accurate charge weights and distances with a 95% calibrated confidence score. However, if we input inconsistent or out-of-range sensor readings, our OOD detection immediately intercepts the query. It flags the input as out-of-distribution using multivariate Mahalanobis distance, protecting the user from unphysical machine learning predictions."*

---

### Scene 7: PDF Reporting & Conclusion
* **Duration**: 4:30 – 5:00
* **Visual**: The operator navigates to the **Research Workspace** tab and clicks **Export Report**. The PDF viewer displays the generated validation document.
* **Action**: Mouse scrolls through the PDF pages showing the title, tables, and Friedlander plot, then closes the app.
* **Narration Script**:
  > *"Finally, we can export our results to an engineering report. Clicking Export compiles a detailed PDF document with plots, tables, and damage classifications. BlastScope combines rigorous air-blast physics, material assessments, and calibrated machine learning into a single, production-ready environment. Thank you for watching."*
