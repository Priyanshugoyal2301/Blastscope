# BlastScope Executive Summary (v1.0.0)

This document provides a high-level overview of the BlastScope desktop application, detailing its deployment context, security posture, core features, and verification metrics.

---

## 1. Project Mission & Context
BlastScope is a desktop-based, offline structural blast safety and hazard assessment platform. It was designed for use by defense researchers, structural engineers, blast analysts, and safety evaluation boards (such as DRDO). The application allows users to simulate high-explosive detonations, predict air-blast parameters, and evaluate the vulnerability of typical construction elements.

---

## 2. Core Capabilities
*   **Dual Blast Wave Scaling**: Implements Hopkinson-Cranz standoff scaling and TNT equivalency using separate factors for pressure ($e_p$) and impulse ($e_i$) to resolve chemical differences between non-TNT agents.
*   **Parametric Sweeps**: Evaluates structural response boundaries across varying standoffs and yields using 1D sweeps and 2D grid sweeps.
*   **Spatial Vulnerability Mapping**: Maps blast risk contours spatially around a detonation point, highlighting safety corridors.
*   **Scientific Validation**: Includes a validation suite of 30 historical trials, verifying solver accuracy againstConWep and military standards.

---

## 3. Technology Stack & Deployment
*   **Frontend**: React (v18.3), TypeScript, Vite (v5.0), and Recharts/HTML Canvas for rendering.
*   **Backend Shell**: Electron (v30), which manages window states and handles secure IPC preload bridges.
*   **Database**: Local SQLite3 database running in Write-Ahead Logging (WAL) mode.
*   **Physics Solver**: Standalone compiled Python suite packaged using PyInstaller.
*   **Deployment Model**: 100% offline standalone execution on Windows 10 & 11, with zero system dependencies (no local Node, npm, or Python runtime required).
