# BlastScope Implementation Plan: RC3 Validation & Release Sprint (v1.0.0-RC3)

This plan details the technical verification and release procedures for the RC3 validation cycle, aiming to stress-test packaging, database migrations, logging, long-duration stability, and package a production-ready v1.0.0 installer.

---

## Release Gate Hierarchy

The v1.0.0 production release is gated based on three validation categories:

### 1. Hard Blockers (Must Pass)
- **Clean Environment Verification**: PACKAGED app executes on clean Windows 10 & 11 VMs with zero dependencies (no Python, Node, npm, Git, or VS Build Tools).
- **Migration Security & Idempotency**: DB upgrades (v1, v2, v3) migrate successfully to v4. `already-v4 -> v4` idempotency check verifies no duplicate migrations run and no new backups/schema changes are generated.
- **Graceful Failures**: Corrupted databases fail gracefully (backup -> log failure -> inform user) without losing or modifying the original database.
- **Process Recovery**: Subprocess kills, freezes, and repeated crashes recover gracefully without infinite restart loops.
- **Boundary Precision**: 10k sweep limit blocks at exactly 10,001 points (9,999/10,000 success) across all three layers (Frontend, IPC, Backend).
- **Data Integrity**: Saved scenarios, notes, assessments, and sweep points remain identical across manual export/import and restart cycles, verified using SHA256 hashes.
- **Concurrency & Locks**: Parallel requests (saves, calculations, note writes, sweeps) execute without encountering SQLite database locks, lost records, or IPC deadlocks.
- **Professional Appearance Certification**: The release is blocked if any text/dropdown text becomes invisible or blends into backgrounds, any table header is clipped, any chart legend overlaps data, any screen contains placeholder text, or any screen requires developer explanation. First-time users must be able to understand all screens within 5 minutes.

### 2. High Priority (Should Pass)
- **Light Scientific Theme Application**: Main app panels transformed from dark/black backgrounds to a professional, light, neutral engineering workspace (MATLAB/ANSYS style).
- **Long-Duration Stability (2h / 12h)**: Soak tests assert zero memory leaks, handle leaks, or heartbeat false-positives.
- **Layout Fidelity**: PDF print reports (Report A, B, C) render without clipped tables, overflows, or hidden Plotly charts.
- **Documentation & Guides**: Complete user guides and scripts are written and reviewed for scientific clarity.

### 3. Final Certification
- **24h Soak**: Verified stable peak/avg memory and memory delta/hour metrics.
- **Multi-OS Installer Verification**: Verified NSIS installers and Portable builds function correctly on both Windows 10 and 11 environments.
- **Walkthrough Demo Certification**: Three narrative video demonstrations showing executive overview, technical walkthrough, and reliability recovery recorded and documented in `DEMO_CERTIFICATION.md`.

---

## Proposed Verification Workstreams

### 1. Multi-Environment & Packaged Verification (Workstream 1)
- Package final Windows NSIS and Portable installers using `npm run dist:win`.
- Verify packaged application (`win-unpacked/BlastScope.exe`) on clean VMs.

### 2. DB Migration Path Upgrade Verification (Workstream 2)
- Upgrade Test Matrix: `v1 -> v4`, `v2 -> v4`, `v3 -> v4`, `empty DB -> v4`, `already-v4 -> v4` (idempotency), `corrupted DB -> fail gracefully`.

### 3. Long-Duration Stability & Soak Testing (Workstream 3)
- Execute `scripts/soak-test.js` in loops for 2h, 12h, and 24h.
- Export metrics to `logs/soak_results.csv` (Main RSS, Renderer RSS, Solver RSS, Peak/Avg memory, and Memory Delta/Hour).

### 4. Sweep Stress & Boundary Testing (Workstream 4)
- 10k point hard limits boundary testing:
  - `9,999` points -> **Success**
  - `10,000` points -> **Success**
  - `10,001` points -> **Blocked** (disabled buttons and UI warnings)
- Layer Enforcement: Frontend validation, Electron IPC, and Python Backend.

### 5. PDF Print Report Validation (Workstream 5)
- Verify layout (no clipping/overflows, full chart rendering) for three distinct reports:
  - Report A: Minimal single-scenario details.
  - Report B: Detailed multi-scenario comparisons.
  - Report C: Large sweep report with validation benchmarks.

### 6. Subprocess Recovery Validation (Workstream 6)
- **Kill Case**: Manually kill solver -> verify heartbeat triggers restart and UI survives.
- **Freeze Case**: Inject a sleep loop -> verify timeout is detected (5s limit) and solver restarts.
- **Crash Loop Case**: Force solver to crash repeatedly -> verify limit (3 attempts) is hit and UI displays error screen.

### 7. Data Integrity Validation (Workstream 7)
- **Data Integrity Tests**: Create a test script `tests/data_integrity.py` asserting SHA256 hashes of scenarios, notes, assessments, and sweeps remain identical across export, import, and application restart cycles.

### 8. Concurrent Operation Stress Testing (Workstream 8)
- **Concurrency Tests**: Create `backend/tests/test_concurrency.py` simulating:
  - 10 parallel scenario saves
  - 10 parallel blast calculations
  - 10 parallel note writes
  - 10 parallel sweep requests
  - Assert zero database locks, lost records, or IPC deadlocks.

### 9. Installer Upgrade Validation (Workstream 9)
- **Upgrade Verification**: Verify upgrade paths from legacy distributions:
  - `v0.5.1 -> v1.0.0`
  - `v0.6 -> v1.0.0`
  - `v0.7 RC -> v1.0.0`
  - Assert database survives, settings/notes/scenarios survive, and no duplicate migrations or database corruption occurs.

### 10. UX/UI Modernization & Product Demo Certification (Workstream 10)
- **Light Scientific Design Language Theme**:
  - Refactor the application styling away from dark background/neon themes to a neutral, light engineering workspace.
  - Main Background: `#F5F7FA`
  - Secondary Background/Panels: `#FFFFFF`
  - Sidebar panel: `#E9EEF5`
  - Borders: `#D6DCE5`
  - Text Primary: `#1F2937`
  - Text Secondary: `#4B5563`
  - Accent Color: `#2563EB` (Engineering Blue)
  - Success Indicator: `#16A34A`
  - Warning Indicator: `#D97706`
  - Critical Hazard: `#DC2626`
- **Component Design Standardization**: Refactor all dropdown menus, form text elements, buttons, tables, modals, and plots to share contrast-compliant (#1F2937 text) styling.
- **Accessibility contrast audit**: Verify WCAG AA / AAA compliance for form validation elements, focus states, and text visibility.
- **Scientific Dashboard Verification**:
  - Forms: Confirm dropdown option lists, selected items, focus states, and placeholders are highly visible.
  - Tables: Fix overflows and ensure sort arrows and headings are unclipped.
  - Plotly: Ensure axes, labels, and legends are fully visible and readable on light backgrounds.
  - PI Curves: Render publication-quality envelopes with clearly shaded threshold zones.
  - Vulnerability Maps: Use scientific heatmap palettes and clear standoff scaling.
- **UI Bug Elimination Pass**: Audit and sign off on `ui_bug_checklist.md`.
- **Narration and Demo Script**: Complete a full application demonstration sequence documented in `DEMO_SCRIPT.md` and record narrated showcase walkthroughs.

---

## Required Release Artifacts

The following six documents are generated and stored as canonical release records in the workspace:
1. **`USER_FUNCTIONAL_GUIDE.md`**: Explains every button, field, screen, and workflow from a scientific and operational standpoint.
2. **`DEMO_SCRIPT.md`**: Exact sequence of steps for demonstrating the app, detailing user action, expected results, and engineering context.
3. **`DEMO_CERTIFICATION.md`**: Certification log documenting three recorded demos:
   - **Demo 1 — Executive Overview (5 min)**: Rapid calculation, assessment, and PDF export.
   - **Demo 2 — Technical Walkthrough (20-30 min)**: Comprehensive tour of all screens and sweeps.
   - **Demo 3 — Reliability Demonstration**: Real-time process kills, timeout restarts, and upgrade migrations.
4. **`UI_BUG_CHECKLIST.md`**: Tracking record of visual issues (dropdown text visibility, chart overlaps, truncation) found and certified as fixed.
5. **`KNOWN_LIMITATIONS.md`**: Document of current non-blocking system limitations and future roadmap goals (v1.1, v1.2, v2.0).
6. **`RELEASE_CHECKLIST.md`**: Release gate sign-off document listing version, git hashes, tests outcome, clean VM check, soak metrics, and final approvals.
