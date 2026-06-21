# BlastScope Developer Guide (v1.0.0)

This developer guide provides setup instructions, directory maps, and build steps to help new developers understand the codebase without needing to read the source files.

---

## 1. Directory Structure

```
blastscope/
├── backend/                  # Python solver suite
│   ├── assessment/           # Damage engines
│   ├── blast_engine/         # Kingery-Bulmash and TNT scaling core
│   ├── database/             # SQLite connection and migration scripts
│   ├── materials/            # Object-oriented material subclasses
│   ├── studies/              # Batch sweep and ranking scripts
│   ├── validation/           # Input parameters validation
│   └── main.py               # Stdio JSON lines IPC entrypoint
├── electron/                 # Electron main and preload processes
│   ├── logger.ts             # Logging and crash tracking
│   ├── main.ts               # Main process lifecycle and IPC handling
│   ├── preload.ts            # Secure whitelists context bridge
│   └── python-runner.ts      # Subprocess manager and recovery engine
├── src/                      # Frontend React SPA code
│   ├── components/           # Reusable panels and charts
│   ├── screens/              # Screen components
│   ├── services/             # API routing wrappers
│   └── App.tsx               # Root app layout
├── tests/                    # E2E Playwright tests and pytest scripts
├── package.json              # NPM script mappings
└── tsconfig.json             # TypeScript compiler settings
```

---

## 2. Developer Setup & Installation

### 2.1 Dependencies
*   Node.js (v20+)
*   Python (v3.10+)

### 2.2 Dev Environment Setup
1.  **Install Frontend Dependencies**:
    ```bash
    npm install
    ```
2.  **Install Python Solver Dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  **Run Dev Environment**:
    ```bash
    npm run dev
    ```
    This launches the local Vite dev server and spawns the Electron shell wrapper in development mode.

---

## 3. IPC Routing & Life-Cycle Management

*   **IPC Bridge**: The frontend communicates with Electron using the `window.api.invoke` wrapper defined in `preload.ts`.
*   **Whitelisted Channels**: The preload script blocks non-whitelisted channels at the renderer layer.
*   **Solver Subprocess**: The Python runner (`python-runner.ts`) spawns the Python backend, routing JSON strings over stdin/stdout.
*   **Subprocess Resiliency**: Electron pings the solver every 10 seconds. If a response is not received within 5 seconds, the solver process is terminated and restarted. If it crashes 3 times in a row, the UI redirects to a crashLoop warning page.

---

## 4. Build & Distribution

*   **Build Python Solver**:
    ```bash
    npm run build:solver
    ```
    Compiles the Python solver into a standalone folder using PyInstaller.
*   **Package Installer**:
    ```bash
    npm run dist:win
    ```
    Builds the production assets and packages them into standard NSIS and portable installers.
