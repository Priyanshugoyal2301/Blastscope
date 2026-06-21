# BlastScope Test Evidence Index (v1.0.0-RC3)

This index maps the compiled verification records, test logs, and packaged installers produced during the v1.0.0-RC3 release certification cycle.

---

## 1. Automated Testing Reports

*   **Pytest Report**: XML report containing the execution status of all 47 Python solver unit tests.
    *   File Path: [pytest-report.xml](file:///c:/project/drdo/code/release_evidence/pytest/pytest-report.xml)
    *   Status: ✅ 47 / 47 Passed
*   **Playwright E2E Report**: HTML report containing step-by-step logs and screenshots for the 6 Electron E2E integration specs.
    *   File Path: [playwright-report/index.html](file:///c:/project/drdo/code/release_evidence/playwright/index.html)
    *   Status: ✅ 6 / 6 Passed

---

## 2. Stability & Performance (Soak) Logs

*   **Soak Results CSV**: Chronological log tracking process RSS memory usage (Main, Renderer, Solver) over execution loops.
    *   File Path: [soak_results.csv](file:///c:/project/drdo/code/release_evidence/soak/soak_results.csv)
    *   Status: ✅ Passed (zero memory leaks or handles leakage detected)

---

## 3. Production Installers & Hashes

*   **Installer Files**:
    *   NSIS Setup Installer: [BlastScope Setup 1.0.0.exe](file:///c:/project/drdo/code/release_evidence/installers/BlastScope%20Setup%201.0.0.exe) (77.4 MB)
    *   Portable Binary Package: [BlastScope 1.0.0.exe](file:///c:/project/drdo/code/release_evidence/installers/BlastScope%201.0.0.exe) (77.2 MB)
*   **SHA256 Hash Table**: Hashes used to verify package integrity.
    *   File Path: [hashes.txt](file:///c:/project/drdo/code/release_evidence/installers/hashes.txt)
    *   Values:
        *   `BlastScope 1.0.0.exe`: `DF5C89FA1858EA91CA286C92B93EA9156FFA05F535486B5950DE43F06444A554`
        *   `BlastScope Setup 1.0.0.exe`: `CECF375F7CDB751B727EE0316C7A05B0550FF1E3E4CF9E242D02B34F67662855`

---

## 4. Multi-Environment & Report Verification

*   **VM Installation Checklist**: Details execution audits on Windows 10/11 Home and Pro editions.
    *   File Path: [vm_execution_verification.md](file:///c:/project/drdo/code/release_evidence/screenshots/vm_execution_verification.md)
*   **PDF Exports Visual Audit**: Documents CSS print-isolation checks and page-break configurations.
    *   File Path: [pdf_export_verification.md](file:///c:/project/drdo/code/release_evidence/reports/pdf_export_verification.md)

---

## 5. SQL Migrations & Execution Logs

*   **Seeded SQL Migrations**:
    *   [001_initial.sql](file:///c:/project/drdo/code/release_evidence/migrations/001_initial.sql)
    *   [002_validation.sql](file:///c:/project/drdo/code/release_evidence/migrations/002_validation.sql)
    *   [003_pi_curves.sql](file:///c:/project/drdo/code/release_evidence/migrations/003_pi_curves.sql)
    *   [004_sprint5_studies.sql](file:///c:/project/drdo/code/release_evidence/migrations/004_sprint5_studies.sql)
*   **System Process Logs**:
    *   [electron.log](file:///c:/project/drdo/code/release_evidence/logs/electron.log)
    *   [ipc.log](file:///c:/project/drdo/code/release_evidence/logs/ipc.log)
    *   [backend.log](file:///c:/project/drdo/code/release_evidence/logs/backend.log)
    *   [solver.log](file:///c:/project/drdo/code/release_evidence/logs/solver.log)
    *   [crash.log](file:///c:/project/drdo/code/release_evidence/logs/crash.log)
