# BlastScope Sprint 2 Implementation Plan (Updated)

This document outlines the revised implementation plan for **Sprint 2: Material Threshold & Engine Dataset Foundation**, detailing changes in database structures, core physics calculations, dynamic pressure-impulse damage index assessments, and the radar visualizer.

## Proposed Changes

### 1. Database Schema Refactor

#### [MODIFY] [schema.sql](file:///c:/project/drdo/code/backend/database/schema.sql)
- Modify `explosives` table:
  - Add `pressure_equivalency REAL NOT NULL`
  - Add `impulse_equivalency REAL NOT NULL`
  - Add `general_equivalency REAL`
- Modify `material_profiles` table:
  - Add `strain_rate_factor REAL`
  - Add `failure_category TEXT`
  - Add `damage_mechanism TEXT`
- Modify `thresholds` table:
  - Add `failure_description TEXT`
  - Add `threshold_source_type TEXT`
  - Add `applicability_notes TEXT`
- Modify `material_assessments` table:
  - Add `damage_mechanism TEXT`
  - Add `controlling_mode TEXT`
  - Add `damage_index REAL`

#### [MODIFY] [db_manager.py](file:///c:/project/drdo/code/backend/database/db_manager.py)
- Drop and recreate tables to apply the new schema.
- Update seeds to incorporate general TNT equivalents (TNT=1.0, C4=1.34, ANFO=0.82), damage mechanisms (Fracture, Collapse, Spalling, Yielding), and applicability notes.

---

### 2. Core Physics & Damage Engines

#### [MODIFY] [tnt_equivalence.py](file:///c:/project/drdo/code/backend/blast_engine/core/tnt_equivalence.py)
- Implement functions for pressure-equivalent, impulse-equivalent, and general weight calculations:
  ```python
  def calculate_pressure_tnt_equivalent(weight: float, factor: float) -> float:
      return weight * factor

  def calculate_impulse_tnt_equivalent(weight: float, factor: float) -> float:
      return weight * factor

  def calculate_general_tnt_equivalent(weight: float, factor: float) -> float:
      return weight * factor
  ```

#### [MODIFY] [scaled_distance.py](file:///c:/project/drdo/code/backend/blast_engine/core/scaled_distance.py)
- Support calculation of dual scaled distances:
  - $Z_p = R / W_p^{1/3}$
  - $Z_i = R / W_i^{1/3}$

#### [MODIFY] [blast_calculator.py](file:///c:/project/drdo/code/backend/blast_engine/services/blast_calculator.py)
- Map inputs to pressure and impulse standoffs ($Z_p, Z_i$) separately and query calculations accordingly.

#### [MODIFY] [base_material.py](file:///c:/project/drdo/code/backend/materials/base_material.py) and subclasses
- Compute individual pressure and impulse ratios.
- Resolve the damage index ($DI = \max(R_p, R_i)$) and document the governing mode:
  ```python
  controlling_mode = "Pressure" if pressure_ratio >= impulse_ratio else "Impulse"
  ```

---

### 3. Frontend & Visualizations

#### [MODIFY] [types/index.ts](file:///c:/project/drdo/code/src/types/index.ts)
- Add database parameters (`general_equivalency`, `strain_rate_factor`, `failure_category`, `damage_mechanism`, `failure_description`, `threshold_source_type`, `applicability_notes`, `controlling_mode`, `damage_index`) to TypeScript interfaces.

#### [NEW] [RadarPlot.tsx](file:///c:/project/drdo/code/src/components/plots/RadarPlot.tsx)
- Render a Plotly `scatterpolar` chart with:
  - Normalized r-values: `min(damage_index / 4.0, 1.0)`
  - Semi-transparent filled area, custom tooltips displaying material profile name, actual damage index, failure category, and governing mode.

#### [MODIFY] [ResearchWorkspace.tsx](file:///c:/project/drdo/code/src/screens/ResearchWorkspace.tsx)
- Add **Material Vulnerability Radar** tab drawing the polar layout.

#### [MODIFY] [MaterialAssessment.tsx](file:///c:/project/drdo/code/src/screens/MaterialAssessment.tsx)
- Expand display columns to show `Governing Mode`, `Damage Index`, and `Damage Mechanism`.
- Add sort parameters to list weak targets first (highest $DI$ descending).

---

## Verification Plan

### Automated Tests
- Create [test_blast_engine.py](file:///c:/project/drdo/code/backend/tests/test_blast_engine.py):
  - **TNT equivalency**: Verify $100\text{ kg TNT}$ generates $W_p = 100$, $W_i = 100$.
  - **C4 equivalency**: Verify $100\text{ kg C4}$ generates $W_p = 137$, $W_i = 119$.
  - **Damage Engine Mode A**: Verify $R_p = 3, R_i = 1$ yields $DI = 3$, `Pressure` mode, `Moderate` damage level.
  - **Damage Engine Mode B**: Verify $R_p = 0.5, R_i = 5$ yields $DI = 5$, `Impulse` mode, `Severe` damage level.
- Run `python -m pytest` to execute unit tests.
