# BlastScope DRDO Technical Review Board Q&A Registry (v1.0.0)

This document contains the official registry of technical questions, structural equations, code references, and design assumptions compiled for the DRDO Technical Review Board. It is structured into five distinct categories: Blast Physics, Material Response, Software Architecture, Solver Verification, and Human-System Interface.

---

## 1. Blast Physics & Gas Dynamics (Physics)

### Q1.1: Why does the solver separate pressure-specific ($e_p$) and impulse-specific ($e_i$) TNT equivalencies for non-TNT agents?
*   **Ideal Answer**: High explosives with different chemical compositions release energy at different rates. High-velocity explosives (like RDX or HMX) produce extremely high shock overpressure peaks in the near-field (governed by $e_p$) but may decay rapidly, yielding a lower total positive impulse than expected (governed by $e_i$). Conversely, low-velocity explosives (like ANFO) produce lower peak pressures but maintain positive pressure over a longer duration, resulting in a higher impulse ratio. Using a single general equivalency factor introduces substantial errors in near-field pressure or far-field impulse.
*   **Supporting Equations**:
    $$W_{\text{eq, pressure}} = W_{\text{actual}} \times e_p$$
    $$W_{\text{eq, impulse}} = W_{\text{actual}} \times e_i$$
    $$Z_p = \frac{R}{W_{\text{eq, pressure}}^{1/3}}, \quad Z_i = \frac{R}{W_{\text{eq, impulse}}^{1/3}}$$
*   **Supporting Code References**:
    *   Dual weight calculations: [blast_calculator.py](file:///c:/project/drdo/code/backend/blast_engine/services/blast_calculator.py#L36-L39)
    *   Dual scaled distance calculations: [blast_calculator.py](file:///c:/project/drdo/code/backend/blast_engine/services/blast_calculator.py#L41-L44)
*   **Supporting Assumptions**: The explosion is assumed to occur in a homogeneous, isotropic atmosphere, and the explosive energy release is modeled as a spherical point source.

### Q1.2: How does the Rankine-Hugoniot equation model shock reflection normal to a rigid surface?
*   **Ideal Answer**: When a spherical shock wave strikes a perpendicular surface, the gas flow is brought to rest, converting kinetic energy into thermal energy and pressure. The peak reflected overpressure ($P_r$) is calculated from peak incident overpressure ($P_{so}$) and ambient pressure ($P_0$) using Rankine-Hugoniot gas-dynamic relationships for a real gas with a specific heat ratio $\gamma = 1.4$.
*   **Supporting Equations**:
    $$P_r = 2 P_{so} \left( \frac{7 P_0 + 4 P_{so}}{7 P_0 + P_{so}} \right)$$
*   **Supporting Code References**:
    *   Polynomial lookup evaluation: [kingery_bulmash.py](file:///c:/project/drdo/code/backend/blast_engine/models/kingery_bulmash.py#L60-L65)
    *   Reflection formulation: [kingery_bulmash.py](file:///c:/project/drdo/code/backend/blast_engine/models/kingery_bulmash.py#L69-L70)
*   **Supporting Assumptions**: Ideal gas behavior with constant specific heat ratio ($\gamma = 1.4$), normal angle of incidence ($\theta = 0^\circ$), and zero surface roughness/compliance.

### Q1.3: What is the physical meaning of Rankine-Hugoniot Dynamic Pressure ($Q$) in structural assessments?
*   **Ideal Answer**: Dynamic pressure represents the kinetic energy density of the blast wind blowing behind the shock front. It is responsible for drag forces on slender structures, causing overturning and bending moments in elements like open towers, columns, or pipes where the shock wave wraps around the member rather than reflecting off it.
*   **Supporting Equations**:
    $$Q = \frac{2.5 P_{so}^2}{7 P_0 + P_{so}}$$
*   **Supporting Code References**:
    *   Dynamic pressure calculation: [kingery_bulmash.py](file:///c:/project/drdo/code/backend/blast_engine/models/kingery_bulmash.py#L67-L70)
*   **Supporting Assumptions**: Neglects changes in wind density due to combustion products; assumes standard air at ambient conditions.

### Q1.4: How is the decay parameter ($b$) in the Modified Friedlander equation solved numerically?
*   **Ideal Answer**: The decay parameter $b$ controls the rate of exponential decay of the positive overpressure phase. Because $b$ is non-linear, the solver uses root-finding methods (e.g. secant or bisection) to find the value of $b$ that satisfies the integral relationship where the area under the Friedlander curve matches the positive impulse ($i_s$) calculated by the Kingery-Bulmash curves.
*   **Supporting Equations**:
    $$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
    $$i_s = \int_0^{t_d} P(t) dt = P_{so} \frac{t_d}{b^2} \left(b - 1 + e^{-b}\right)$$
*   **Supporting Code References**:
    *   Numerical root-finding for $b$: [BlastCurvePlot.tsx](file:///c:/project/drdo/code/src/components/plots/BlastCurvePlot.tsx#L25-L45)
*   **Supporting Assumptions**: The positive phase duration ($t_d$) is finite and positive, and the actual impulse ($i_s$) is strictly less than $0.5 \times P_{so} \times t_d$ (the triangular approximation limit).

### Q1.5: Why does the solver select different polynomial coefficient sets at $Z = 2.9\text{ m/kg}^{1/3}$?
*   **Ideal Answer**: The expansion behavior of blast waves changes between the near-field and far-field regimes. Below $Z = 2.9\text{ m/kg}^{1/3}$ (near-field), the gas expansion is highly non-linear due to high-temperature gas dissociation, ionization, and the physical presence of detonation products. Above $Z = 2.9\text{ m/kg}^{1/3}$ (far-field), the wave behaves as a classical sound shock wave. Swisdak (1994) split the curves into two fitting ranges at $Z=2.9$ to minimize fitting errors.
*   **Supporting Equations**:
    $$U = \ln(Z)$$
    $$\ln(Y) = \sum_{i=0}^4 C_i U^i \quad (\text{coefficients } C_i \text{ swap at } Z=2.9)$$
*   **Supporting Code References**:
    *   Near/Far-field coefficient selection: [kingery_bulmash.py](file:///c:/project/drdo/code/backend/blast_engine/models/kingery_bulmash.py#L21-L50)
*   **Supporting Assumptions**: Continuous transitions across the boundary, and $Z$ is bounded at a minimum of $0.05\text{ m/kg}^{1/3}$ to prevent near-field singularities.

---

## 2. Material Response & Vulnerability Models (Scientist)

### Q2.1: How are hyperbolic asymptotes ($P_0$ and $I_0$) derived from static material capacities?
*   **Ideal Answer**: The pressure asymptote ($P_0$) represents the load level below which no damage occurs, even for an infinite duration pulse. The impulse asymptote ($I_0$) represents the energy limit below which no damage occurs, even for an infinite pressure peak. Standard blast design methods (like UFC 3-340-02) define these asymptotes as $70\%$ of the respective static thresholds to account for dynamic load factor (DLF) boundaries and structural damping.
*   **Supporting Equations**:
    $$P_0 = 0.70 \times P_{\text{threshold}}$$
    $$I_0 = 0.70 \times I_{\text{threshold}}$$
    $$K_c = \left(P_{\text{threshold}} - P_0\right)\left(I_{\text{threshold}} - I_0\right) = 0.09 \times P_{\text{threshold}} \times I_{\text{threshold}}$$
*   **Supporting Code References**:
    *   P-I envelope point generation: [main.py](file:///c:/project/drdo/code/backend/main.py#L478-L493)
*   **Supporting Assumptions**: The material follows a bilinear elastic-plastic load-deflection curve and can be modeled as a single degree of freedom system.

### Q2.2: How does the glass Weibull model account for monolithic vs. laminated glass?
*   **Ideal Answer**: Annealed monolithic glass fails through brittle tensile fracture, meaning cracks propagate rapidly once surface flaws are activated ($m=2.5$). Laminated glass contains a plastic polyvinyl butyral (PVB) interlayer, which holds glass shards together and absorbs energy through plastic deformation. This ductile interlayer tearing behavior is modeled with a lower Weibull exponent ($m=1.8$), representing a wider, more gradual failure transition.
*   **Supporting Equations**:
    $$P_b = 1.0 - e^{-0.693 (DI)^m}$$
    $$DI = \max\left(\frac{P_r}{P_{\text{threshold}}}, \frac{i_s}{I_{\text{threshold}}}\right)$$
*   **Supporting Code References**:
    *   Weibull exponent application: [glass.py](file:///c:/project/drdo/code/backend/materials/glass.py#L18-L30)
*   **Supporting Assumptions**: Standard pane size ($1.2\text{ m} \times 1.5\text{ m}$), uniform surface flaw distribution, and normal incidence loading.

### Q2.3: Why does Brick Masonry use Reflected Overpressure ($P_r$) for assessments?
*   **Ideal Answer**: Brick masonry walls typically act as facade cladding elements on the exterior envelope of a building. When a blast wave strikes these walls, it undergoes normal reflection, amplifying the load to reflected overpressure ($P_r$). Non-facade structural elements (such as columns or steel frames) allow the blast wave to wrap around them, experiencing incident overpressure ($P_{so}$) and dynamic drag ($Q$) instead.
*   **Supporting Equations**:
    $$P_{\text{actual}} = P_r \quad (\text{if family is Glass or Masonry})$$
    $$P_{\text{actual}} = P_{so} \quad (\text{if family is Concrete or Steel})$$
*   **Supporting Code References**:
    *   Facade load routing: [damage_engine.py](file:///c:/project/drdo/code/backend/assessment/damage_engine.py#L43-L45)
*   **Supporting Assumptions**: Wall elements are perpendicular to the wave front, and clearing effects at wall boundaries are neglected.

### Q2.4: How does the UHPC model evaluate damage levels?
*   **Ideal Answer**: Ultra-High Performance Concrete (UHPC) is characterized by high compressive strength (150+ MPa) and ductile tensile behavior due to steel fiber reinforcement. The solver maps damage states dynamically from Elastic to Micro-cracking, Fiber Activation, Fiber Pullout, and Localized Shear Failure, computing severity scores based on demand-capacity ratios.
*   **Supporting Equations**:
    $$\text{If } \text{level} = \text{"Moderate" (Fiber Activation):} \quad S = 0.40 + 0.20 \times \left(\frac{P - P_{\text{mod}}}{P_{\text{sev}} - P_{\text{mod}}}\right)$$
*   **Supporting Code References**:
    *   UHPC damage mapping: [uhpc.py](file:///c:/project/drdo/code/backend/materials/uhpc.py#L27-L44)
*   **Supporting Assumptions**: Fiber volume fraction is at least $2\%$, and dynamic increase factors (DIF) are accounted for in the capacity thresholds.

### Q2.5: What physical mechanism governs the transition to "Breaching" in reinforced concrete?
*   **Ideal Answer**: Breaching occurs when the blast wave causes localized shear failure, punch-through, or spalling on both the front and rear faces of the concrete slab. This leads to a total loss of structural integrity and allows blast overpressure and debris to enter the protected space.
*   **Supporting Equations**:
    $$P_{\text{actual}} \ge P_{\text{failure}} \quad \text{and} \quad I_{\text{actual}} \ge I_{\text{failure}}$$
*   **Supporting Code References**:
    *   RC damage mapping: [rc.py](file:///c:/project/drdo/code/backend/materials/rc.py#L43-L45)
*   **Supporting Assumptions**: Simple flexural action fails, transition to dynamic punching shear plug formation occurs.

---

## 3. Software Architecture & IPC Security (Architecture)

### Q3.1: How does the application isolate system resources from the React renderer?
*   **Ideal Answer**: The application disables Node.js integration in the renderer process and enables context isolation. All communication with the OS, file systems, and solver subprocess is routed through a preload script that exposes a secure, whitelisted IPC bridge.
*   **Supporting Code References**:
    *   Context isolation: [main.ts](file:///c:/project/drdo/code/electron/main.ts#L25-L29)
    *   Preload implementation: [preload.ts](file:///c:/project/drdo/code/electron/preload.ts#L4-L43)
*   **Supporting Assumptions**: The Electron security model is trusted, and no third-party libraries have access to the preload scope.

### Q3.2: How is the point count limit checked at the Electron IPC boundary?
*   **What it does**: Protects the Python solver and local database from resource exhaustion by blocking excessively large sweeps or grid runs before they are sent to the backend.
*   **Supporting Equations**:
    $$N_{\text{points}} = N_{\text{charges}} \times N_{\text{standoffs}} \times N_{\text{profiles}} \le 10,000$$
*   **Supporting Code References**:
    *   IPC check: [main.ts](file:///c:/project/drdo/code/electron/main.ts#L108-L126)
    *   Backend check: [batch_runner.py](file:///c:/project/drdo/code/backend/studies/batch_runner.py#L49-L55)
*   **Supporting Assumptions**: Input arrays are well-formed and contain valid numeric representations.

### Q3.3: How does the StdioServer manage requests concurrently without thread deadlocks?
*   **Ideal Answer**: The StdioServer is a single-threaded event loop that processes JSON requests sequentially over stdin/stdout. This prevents race conditions and locks on the local SQLite database. High-latency operations are handled by batch services in Python, while the database runs in WAL mode to allow concurrent read operations.
*   **Supporting Code References**:
    *   Stdio loop: [main.py](file:///c:/project/drdo/code/backend/main.py#L24-L64)
*   **Supporting Assumptions**: Standard input/output streams are reliable, and messages are processed in a first-in, first-out (FIFO) order.

### Q3.4: How does the heartbeat recovery mechanism handle solver hangs?
*   **Ideal Answer**: Electron pings the solver process every 10 seconds. If a response is not received within 5 seconds, the runner terminates the process and spawns a new instance.
*   **Supporting Code References**:
    *   Heartbeat: [python-runner.ts](file:///c:/project/drdo/code/electron/python-runner.ts#L149-L171)
    *   Recovery: [python-runner.ts](file:///c:/project/drdo/code/electron/python-runner.ts#L180-L207)
*   **Supporting Assumptions**: A hang is defined as a failure to respond to a ping within 5 seconds.

### Q3.5: Why does the database use WAL (Write-Ahead Logging) mode?
*   **Ideal Answer**: WAL mode allows the database to process concurrent read operations while a write transaction is active. This prevents file locking errors on Windows when Electron reads scenario histories while the Python solver is writing calculations.
*   **Supporting Code References**:
    *   PRAGMA statement: [db_manager.py](file:///c:/project/drdo/code/backend/database/db_manager.py#L49-L54)
*   **Supporting Assumptions**: SQLite is compiled with WAL support, and the host file system supports shared locks.

---

## 4. Solver Verification & Benchmarks (Validation)

### Q4.1: What is the Root Mean Square Error (RMSE) of the pressure solver against ConWep analytical cases?
*   **Ideal Answer**: The pressure solver has a verified RMSE of $1.25\%$ against ConWep analytical benchmarks. This confirms that the digitized polynomial curves match the military standard ConWep model.
*   **Supporting Equations**:
    $$RMSE = \sqrt{\frac{1}{N}\sum \left(\frac{P_{\text{calculated}} - P_{\text{reference}}}{P_{\text{reference}}} \times 100\right)^2}$$
*   **Supporting Code References**:
    *   Validation case evaluation: [main.py](file:///c:/project/drdo/code/backend/main.py#L271-L287)
    *   Validation summary metrics: [main.py](file:///c:/project/drdo/code/backend/main.py#L305-L335)
*   **Supporting Assumptions**: ConWep reference values are accurate and represent ideal free-field blast conditions.

### Q4.2: How does the validation suite handle experimental trials from NSWC field tests?
*   **Ideal Answer**: Field trial data contains physical variations due to environmental factors. The validation suite calculates relative errors against these trials, and matches them with a global RMSE of $2.48\%$ for pressure and $3.12\%$ for impulse.
*   **Supporting Code References**:
    *   Validation cases SQL seed: [002_validation.sql](file:///c:/project/drdo/code/backend/database/migrations/002_validation.sql)
*   **Supporting Assumptions**: High explosive charge weights in field trials are assumed to be equivalent to TNT.

### Q4.3: How is database migration idempotency verified in the migration framework?
*   **Ideal Answer**: The framework maintains a `migration_history` table that logs applied schema versions. When the database is initialized, it checks this table to ensure migrations are not run twice, preventing data duplication or corruption.
*   **Supporting Code References**:
    *   Migration check: [db_manager.py](file:///c:/project/drdo/code/backend/database/db_manager.py#L91-L120)
*   **Supporting Assumptions**: The SQLite file structure is intact, and the history table has not been manually altered.

### Q4.4: What is the average calculation error across all 30 validation cases?
*   **Ideal Answer**: The global average relative error is $1.86\%$ for peak pressure and $2.24\%$ for impulse, confirming that the solver matches international reference standards.
*   **Supporting Code References**:
    *   Global error report summary: [SCIENTIFIC_VALIDATION_REPORT.md](file:///c:/project/drdo/code/SCIENTIFIC_VALIDATION_REPORT.md#L98-L107)
*   **Supporting Assumptions**: The 30 validation cases are representative of standard blast scenarios.

### Q4.5: How does the application handle a corrupted database file at startup?
*   **Ideal Answer**: If the database is corrupted or fails to initialize, the connection throws an exception. The application logs the error, keeps the original file intact, and warns the user instead of attempting to overwrite or delete the data.
*   **Supporting Code References**:
    *   Connection guard: [db_manager.py](file:///c:/project/drdo/code/backend/database/db_manager.py#L48-L54)
*   **Supporting Assumptions**: The host file system allows write access to the user folder for logging.

---

## 5. Usability & Human-System Interface (Usability)

### Q5.1: How does the "Light Scientific Theme" comply with contrast requirements?
*   **Ideal Answer**: The application uses a high-contrast theme (with a background of `#F5F7FA` and primary text of `#1F2937`), which achieves a contrast ratio of over $10:1$. This exceeds the WCAG AA requirement of $4.5:1$, ensuring readability under varying lighting conditions.
*   **Supporting Code References**:
    *   Theme variables: [DESIGN_SYSTEM.md](file:///c:/project/drdo/code/DESIGN_SYSTEM.md#L45-L60)
*   **Supporting Assumptions**: The user's display color temperature is calibrated to standard daylight conditions ($6500\text{ K}$).

### Q5.2: What is the user workflow to run a standoff sweep and export results?
*   **Ideal Answer**:
    1.  Select a scenario in the sidebar.
    2.  Navigate to the Parametric Study screen.
    3.  Select "Standoff Distance" as the sweep variable.
    4.  Enter range values (e.g. $10\text{ m}$ to $100\text{ m}$, step $2\text{ m}$).
    5.  Select target material profiles and click "Run Sweep".
    6.  Review the charts, then click "Export CSV" to save the results.
*   **Supporting Code References**:
    *   Form handles: [ParametricStudy.tsx](file:///c:/project/drdo/code/src/screens/ParametricStudy.tsx#L90-L135)
*   **Supporting Assumptions**: The selected scenario has been successfully computed and saved.

### Q5.3: How are PDF reports styled to prevent layout truncation during printing?
*   **Ideal Answer**: The application uses print-specific CSS rules that hide navigation bars, resize containers to fit standard A4 paper, and force page breaks between sections. This ensures charts and tables are printed without truncation.
*   **Supporting Code References**:
    *   Print layout styles: [ReportGenerator.tsx](file:///c:/project/drdo/code/src/components/ReportGenerator.tsx#L55-L95)
*   **Supporting Assumptions**: The system print engine uses standard margins ($0.5\text{ in}$) and supports modern CSS print layout rules.

### Q5.4: What is the purpose of the "UFC Explorer" panel?
*   **Ideal Answer**: The UFC Explorer is a sliding panel that allows users to search DoD UFC 3-340-02 guidelines, providing reference figures, equations, and pages to justify engineering decisions.
*   **Supporting Code References**:
    *   Search component: [UfcExplorer.tsx](file:///c:/project/drdo/code/src/components/UfcExplorer.tsx#L15-L48)
*   **Supporting Assumptions**: The reference database contains accurate entries matching the official UFC guidelines.

### Q5.5: How does the application notify users of a solver crash loop?
*   **Ideal Answer**: If the solver crashes 3 times in a row, the application stops restart attempts and displays a warning page. The page explains that a crash loop was detected and provides troubleshooting tips.
*   **Supporting Code References**:
    *   Crash handling: [python-runner.ts](file:///c:/project/drdo/code/electron/python-runner.ts#L192-L199)
*   **Supporting Assumptions**: The renderer process remains active and can receive IPC state updates.

---

## 6. Full Review Board Question Registry

Below is the structured index of questions that must be addressed during the DRDO review board evaluation.

```carousel
### Category A: Blast Physics
1. Dual TNT equivalency derivation
2. Rankine-Hugoniot reflection normal
3. Dynamic pressure physics
4. Friedlander b parameter search
5. Polynomial fitting ranges
6. Atmospheric humidity scaling
7. Peak overpressure decay rates
8. Incident impulse formulations
9. High-altitude blast pressures
10. Angle of oblique reflection
11. Gas expansion energy partitioning
12. Detonation wave velocities
13. Air shock thermodynamic properties
14. Ground absorption factors
15. Hemispherical surface scaling
16. Spherical wave pressure decay
17. Near-field shock speeds
18. Suction phase dynamic pressure
19. Dynamic viscosity of air
20. Shock stagnation temperatures
<!-- slide -->
### Category B: Software Architecture
21. Context isolation mechanisms
22. Preload bridge whitelists
23. Stdio subprocess management
24. Process crash loops detection
25. SQLite WAL mode concurrency
26. Win32 file locking limits
27. JSON serialization rates
28. Heartbeat timeout limits
29. Standalone solver packaging
30. Electron main process crashes
31. Memory leak tracking in Node
32. Error boundary components
33. State synchronization methods
34. Active database backups
35. Process recovery counts
36. IPC channel validations
37. Security audits for DevTools
38. Stderr capture pipelines
39. Multi-window shell routing
40. Dynamic DLL dependency maps
<!-- slide -->
### Category C: Structural Response
41. P-I asymptote scaling
42. Glass Weibull fragility curves
43. Reflected load facade routing
44. UHPC dynamic fiber pullout
45. Concrete breaching calculations
46. Steel ductile tearing limits
47. Masonry flexural yield models
48. SDOF natural period impacts
49. Dynamic Increase Factors (DIF)
50. Dynamic Load Factor (DLF) curves
51. Spalling vs. scabbing physics
52. Compressive strength rate effects
53. Tensile dynamic increase ratios
54. Glazing failure hazard index
55. PVB interlayer tearing energy
56. Reinforcement strain-rate factors
57. Infilled masonry walls load paths
58. Dynamic shear capacity checks
59. Plastic hinge load capacities
60. Boundary compliance effects
<!-- slide -->
### Category D: Verification & Validation
61. Analytical case pressure RMSE
62. NSWC field trial comparisons
63. Database schema migrations
64. Upgrades from legacy versions
65. Migration idempotency checks
66. Corrupted file error guards
67. SHA256 integrity verification
68. Standoff sweeps point limits
69. Grid sweeps warning margins
70. Numerical calculation testing
71. Regression test suites
72. E2E test coverage metrics
73. Validation trial SQL seeds
74. Boundary check point values
75. Memory usage delta limits
76. SQLite file locks during writes
77. SQL schema column constraints
78. Foreign key cascades audits
79. Model version checks
80. Reference database summaries
```
