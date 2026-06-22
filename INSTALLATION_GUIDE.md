# BlastScope Installation & Deployment Guide

This guide provides step-by-step instructions for installing and deploying the **BlastScope** platform.

---

## 1. System Requirements

* **Operating System**: Windows 10 or Windows 11 (64-bit).
* **Processor**: Intel Core i3 / AMD Ryzen 3 or higher.
* **Memory (RAM)**: 4 GB minimum (8 GB recommended).
* **Storage**: 500 MB of available hard disk space.
* **Display**: 1280x800 minimum resolution.

> [!NOTE]
> BlastScope is packaged as a fully self-contained application. There is **no requirement** to install Python, Node.js, SQLite, or other compiler toolchains on the host computer. All runtime dependencies are bundled inside the executable.

---

## 2. Distribution Packages

BlastScope is distributed in two formats (located in the `dist-package/` folder after compilation):

1. **Standard Installer** (`BlastScope Setup 1.0.0.exe`):
   * Installs the platform globally or per-user.
   * Creates Desktop and Start Menu shortcuts.
   * Registers uninstall configurations.
2. **Portable Version** (a standalone directory):
   * Run the platform directly by double-clicking `BlastScope.exe` in the extracted folder.
   * Useful for restricted environments where installer execution is blocked by administration policies.

---

## 3. Installation Steps

### 3.1 Standard Setup
1. Download the installer file: `BlastScope Setup 1.0.0.exe`.
2. Double-click the file to launch the setup wizard.
3. Choose the installation directory (default: `C:\Users\<Username>\AppData\Local\Programs\blastscope` or `C:\Program Files\BlastScope`).
4. Select whether to create a desktop shortcut.
5. Click **Install**. Once finished, check **Run BlastScope** and click **Finish**.

### 3.2 Portable Run
1. Extract the portable ZIP archive to your local directory (e.g. `C:\BlastScope_Portable`).
2. Locate `BlastScope.exe` in the root folder.
3. Double-click `BlastScope.exe` to launch the application.

---

## 4. Application Directories & Database File Layout

On startup, BlastScope initializes its folder structure and SQLite database in the user's roaming directory:

* **Database File Location**: 
  `C:\Users\<Username>\AppData\Roaming\BlastScope\sqlite.db`
* **Log Directory**:
  `C:\Users\<Username>\AppData\Roaming\BlastScope\logs\`
* **Database Backups Directory**:
  `C:\Users\<Username>\AppData\Roaming\BlastScope\backups\`

### 4.1 Automated Database Initialization
* **Database Creation**: If `sqlite.db` is missing on launch, the application creates a fresh database file automatically.
* **Schema Migrations**: The system reads the bundled schema and runs SQL migrations to build the tables.
* **Parameter Seeding**: The explosives library (TNT, C4, RDX, HMX, ANFO, PETN, Comp B), unit definitions, standard material vulnerability profiles (Glass, Masonry, Concrete, Steel, Human), and UFC validation benchmark cases are seeded automatically on first launch.

---

## 5. Subsystem Architecture & Process Recovery

BlastScope runs a multi-process architecture:
1. **Frontend UI**: Built with HTML/CSS/JavaScript and rendered via Electron's chromium browser window.
2. **Backend Engine**: A compiled standalone executable (`blastscope-solver.exe`) built using PyInstaller.

### 5.1 Process Monitoring & Heartbeats
* The Electron main process maintains a persistent heartbeat connection with the Python backend process, pinging it every 10 seconds.
* **Unexpected Termination Recovery**: If the Python backend process crashes or terminates, the Electron runner captures the exit event, unbinds pending IPC requests, and triggers an automated recovery routine.
* **Self-Healing Loop**: The app attempts to relaunch the standalone backend solver up to **3 times**. If recovery is successful, it notifies the user with a status toast and processes the request queue. If recovery fails after 3 attempts, it alerts the user that a fatal crash occurred.

### 5.2 Database Corruption Healing
* If the SQLite database file gets corrupted or migrations fail on startup:
  1. The backend service intercepts the exception.
  2. It copies the corrupted database to `backups/sqlite_corrupted_<timestamp>.db` to preserve user data.
  3. It unlinks/removes the corrupted `sqlite.db` file.
  4. It automatically runs a clean initialization to recreate and re-seed a healthy database, ensuring the app remains launchable.
