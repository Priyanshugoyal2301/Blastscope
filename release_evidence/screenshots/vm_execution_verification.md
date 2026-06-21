# Clean VM Installation & Execution Verification Record

This document records the installation and startup validation of the final packages on fresh Windows virtual environments.

---

## 1. Operating System Targets Verified

| Target OS Edition | Package Type Tested | Execution Outcome | GPU Acceleration |
|---|---|---|---|
| **Windows 10 Home (22H2)** | NSIS Installer | ✅ Success (Calculations run) | CPU Software Rasterization Fallback |
| **Windows 10 Pro (22H2)** | Portable Binary | ✅ Success (Sweeps run) | Native D3D11 Acceleration |
| **Windows 11 Home (23H2)** | NSIS Installer | ✅ Success (Calculations run) | CPU Software Rasterization Fallback |
| **Windows 11 Pro (23H2)** | Portable Binary | ✅ Success (Sweeps run) | Native D3D11 Acceleration |

---

## 2. Environment Constraints Checked

*   **No local Python installed**: Excluded from Windows PATH. Standalone `blastscope-solver.exe` loaded all standard mathematical and SQLite modules from its unpacked folder.
*   **No local Node.js or npm installed**: Excluded from Windows PATH. Electron packaging ran fully stand-alone.
*   **No VS Build Tools, C++ compiler, or Git installed**: Confirmed no system DLL resolution issues.
*   **Permissions**: Portable build successfully runs from a non-admin `Desktop` folder. NSIS setup successfully registers under `Program Files` using admin elevation and stores data in `%APPDATA%/BlastScope/`.
