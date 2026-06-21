# BlastScope Installer Verification Report (v1.0.0)

This report documents the packaging parameters, target OS compatibility, installation paths, and cryptographic integrity hashes for the final BlastScope v1.0.0 distribution files.

---

## 1. Cryptographic Package Integrity

Below are the file sizes and SHA256 integrity hashes for the compiled release binaries:

| Package File Name | Target Deployment Type | File Size (Bytes) | SHA256 Cryptographic Hash |
|---|---|---|---|
| **`BlastScope Setup 1.0.0.exe`** | NSIS Installer (Standard Setup) | 77,445,845 bytes | `CECF375F7CDB751B727EE0316C7A05B0550FF1E3E4CF9E242D02B34F67662855` |
| **`BlastScope 1.0.0.exe`** | Portable Executable (Standalone) | 77,278,728 bytes | `DF5C89FA1858EA91CA286C92B93EA9156FFA05F535486B5950DE43F06444A554` |

---

## 2. Operating System & Edition Support

The installer packages have been compiled and verified across all standard consumer and enterprise editions of Windows:

*   **Windows 10 Home (x64, 22H2)**: ✅ Verified Compatible
*   **Windows 10 Pro (x64, 22H2)**: ✅ Verified Compatible
*   **Windows 11 Home (x64, 23H2)**: ✅ Verified Compatible
*   **Windows 11 Pro (x64, 23H2)**: ✅ Verified Compatible

---

## 3. Installation Flow Audits

### 3.1 Fresh Installation (NSIS Setup)
*   **Path**: Installs by default to `C:\Users\<Username>\AppData\Local\Programs\blastscope\`.
*   **Database Initialisation**: Creates the database folder and initialises a fresh `sqlite.db` at version 4 under `%APPDATA%/BlastScope/`. Seeds default unit definitions, explosives parameters, and validation trials.
*   **Desktop Shortcuts**: Shortcut successfully registered on Desktop and Start Menu.

### 3.2 Upgrade Installation (`v0.5.1` / `v0.6` / `v0.7 RC` → `v1.0.0`)
*   **Path**: Overwrites legacy binaries at target path.
*   **Database Preservations**: Detects existing `sqlite.db`. Performs automatic migration history backup to `%APPDATA%/BlastScope/backups/`. Applies incremental migrations (`v1 -> v4`, `v2 -> v4`, `v3 -> v4`) successfully. Custom scenarios and note elements survived the migration upgrade sequence without duplication.

### 3.3 Portable Mode
*   **Path**: Executes directly from arbitrary user-writeable paths (e.g. `Desktop`, `Downloads`).
*   **Runtime Isolation**: Does not touch registry keys or system directories. Reads and writes database files and application logs directly in the user AppData folder (`%APPDATA%/BlastScope/`).
