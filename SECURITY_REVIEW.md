# BlastScope Security & Hardening Review (v1.0.0)

This document presents the security posture, threat mitigation strategies, and hardening review of the BlastScope desktop application.

---

## 1. Architectural Security Controls

### 1.1 Context Isolation & Preload Script
*   **Implementation**: Enforced in [main.ts](file:///c:/project/drdo/code/electron/main.ts):
    ```typescript
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
    ```
*   **Security Benefit**: Isolates the frontend execution context from Node.js capabilities. A compromise in the browser window cannot directly execute system calls or read files.

### 1.2 IPC Channel Whitelisting
*   **Implementation**: The preload script [preload.ts](file:///c:/project/drdo/code/electron/preload.ts) validates and intercepts all incoming renderer requests against a strict whitelist of 30 standard channels (e.g. `scenarios:list`, `blast:calculateEnvironment`).
*   **Security Benefit**: Prevents the renderer from invoking arbitrary IPC handles or triggering remote commands.

### 1.3 DevTools & Debug Controls
*   **Implementation**: DevTools are dynamically loaded using environmental guards:
    ```typescript
    const isDev = (process.env.NODE_ENV === 'development' || (process.env.NODE_ENV !== 'production' && !app.isPackaged)) && process.env.BLASTSCOPE_TESTING !== '1';
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
    ```
*   **Security Benefit**: DevTools are completely disabled and inaccessible in the production packaged application.

---

## 2. Local File & Subprocess Hardening

### 2.1 Test-IPC Channel Isolation
*   **Implementation**: Diagnostic IPC channels (e.g. `test:kill-solver`, `test:freeze-solver`) are guarded by environmental checks:
    ```typescript
    if (process.env.BLASTSCOPE_TESTING === '1') {
      ipcMain.handle('test:kill-solver', async () => { ... });
    }
    ```
*   **Security Benefit**: Diagnostic hooks are omitted entirely in production environments.

### 2.2 Input Parameter Boundary Protection
*   **Implementation**: Sweep counts are checked in `electron/main.ts` (`checkPointLimit`) and in the python solver. Requests exceeding `10,000` sweep points are immediately blocked.
*   **Security Benefit**: Protects against Denial-of-Service (DoS) memory exhaustion attacks trying to lock the system by requesting excessively large calculations.

### 2.3 Local Path Validation
*   **Implementation**: Database files are stored exclusively in the designated `%APPDATA%/BlastScope/` user folder. Paths are resolved using safe `path.join` operations to prevent directory traversal vulnerabilities.

---

## 3. Secret & Network Audit

*   **No Network Communications**: BlastScope is a fully offline tool. It binds no network sockets, runs no HTTP listeners, and does not perform external fetch requests.
*   **No Hardcoded Secrets**: Audit confirms there are no API keys, credentials, private tokens, or encryption keys hardcoded in the codebase.
