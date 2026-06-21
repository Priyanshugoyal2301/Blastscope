import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';
import { app, BrowserWindow } from 'electron';
import { logger } from './logger';

export interface QueuedRequest {
  id: string;
  channel: string;
  payload: any;
  resolve: (val: any) => void;
  reject: (err: any) => void;
}

export class PythonRunner {
  private pythonProcess: ChildProcess | null = null;
  private pendingRequests: Map<string, { resolve: (val: any) => void; reject: (err: any) => void; channel: string }> = new Map();
  private requestCounter = 0;
  
  private pingInterval: NodeJS.Timeout | null = null;
  private manualStop = false;
  private recoveryAttempts = 0;
  private recoveryCount = 0;
  private readonly maxRecoveryAttempts = 3;
  private isRecovering = false;

  private requestQueue: QueuedRequest[] = [];
  private activeRequestId: string | null = null;
  private requestTimeouts: Map<string, NodeJS.Timeout> = new Map();
  private isProcessingQueue = false;

  constructor() {}

  public start(): void {
    const isPackaged = app ? app.isPackaged : false;
    this.manualStop = false;
    this.activeRequestId = null;

    if (isPackaged) {
      const solverExe = path.join(process.resourcesPath, 'backend-dist', 'blastscope-solver', 'blastscope-solver.exe');
      logger.logElectron(`Packaged environment detected. Attempting to launch executable backend: ${solverExe}`);
      
      try {
        this.pythonProcess = spawn(solverExe, [], {
          env: { 
            ...process.env, 
            BLASTSCOPE_PACKAGED: '1',
            BLASTSCOPE_USER_DATA_DIR: app.getPath('userData')
          }
        });
        
        if (this.pythonProcess.pid) {
          logger.logElectron(`Standalone solver process successfully started with PID: ${this.pythonProcess.pid}`);
          this.setupProcessHandlers();
          this.startHeartbeat();
          this.processQueue();
        } else {
          logger.logCrash('CRITICAL: Standalone solver process failed to return PID.');
        }
      } catch (err: any) {
        logger.logCrash('Exception launching standalone packaged solver:', err);
      }
    } else {
      // Development fallback
      const backendPath = path.join(__dirname, '..', 'backend', 'main.py');
      const pythonCmds = ['python', 'python3', 'py'];
      let spawned = false;

      for (const cmd of pythonCmds) {
        try {
          logger.logElectron(`Attempting to launch Python backend in DEV mode with command: ${cmd} on ${backendPath}`);
          this.pythonProcess = spawn(cmd, [backendPath], {
            env: { 
              ...process.env, 
              PYTHONPATH: path.join(__dirname, '..'),
              BLASTSCOPE_USER_DATA_DIR: app.getPath('userData')
            }
          });
          
          if (this.pythonProcess.pid) {
            spawned = true;
            logger.logElectron(`DEV Python backend process spawned with PID ${this.pythonProcess.pid} using ${cmd}`);
            this.setupProcessHandlers();
            this.startHeartbeat();
            this.processQueue();
            break;
          }
        } catch (e: any) {
          logger.logElectron(`Failed to spawn DEV backend using ${cmd}: ${e.message}`, 'WARN');
        }
      }

      if (!spawned) {
        logger.logCrash('CRITICAL: Could not launch Python process in DEV mode using python, python3, or py.');
      }
    }
  }

  private setupProcessHandlers(): void {
    if (!this.pythonProcess || !this.pythonProcess.stdout || !this.pythonProcess.stderr) {
      return;
    }

    const currentProcess = this.pythonProcess;

    const rl = readline.createInterface({
      input: this.pythonProcess.stdout,
      terminal: false
    });

    rl.on('line', (line) => {
      try {
        const response = JSON.parse(line.trim());
        const id = response.id;
        
        if (id && this.pendingRequests.has(id)) {
          const { resolve, reject, channel } = this.pendingRequests.get(id)!;
          this.pendingRequests.delete(id);
          this.clearRequestTimeout(id);
          
          if (response.success) {
            logger.logSolver(`IPC SUCCESS channel=${channel} req_id=${id}`);
            resolve(response.response);
          } else {
            logger.logSolver(`IPC FAILURE channel=${channel} req_id=${id} error=${response.error || 'Unknown'}`, 'ERROR');
            reject(new Error(response.error || 'Unknown error occurred in Python backend'));
          }

          if (this.activeRequestId === id) {
            this.activeRequestId = null;
          }
          this.processQueue();
        }
      } catch (e: any) {
        logger.logBackend(`Error parsing line from Python stdout: ${e.message}. Line: ${line}`, 'ERROR');
      }
    });

    this.pythonProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim();
      logger.logBackend(`[Stderr] ${msg}`);
    });

    this.pythonProcess.on('close', (code) => {
      logger.logElectron(`Python subprocess exited with code ${code}`, 'WARN');
      if (currentProcess !== this.pythonProcess) {
        logger.logElectron(`Defunct process closed (expected during restart), ignoring close event.`);
        return;
      }
      this.pythonProcess = null;
      this.stopHeartbeat();
      
      // Auto recovery on unexpected exit
      if (!this.manualStop && !this.isRecovering) {
        logger.logElectron('Unexpected backend exit detected. Launching recovery...', 'WARN');
        this.recover();
      }
    });
  }

  public invoke(channel: string, payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.requestCounter++;
      const id = `req_${Date.now()}_${this.requestCounter}`;
      
      this.requestQueue.push({ id, channel, payload, resolve, reject });
      this.processQueue();
    });
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessingQueue || this.activeRequestId || this.isRecovering) {
      return;
    }
    if (this.requestQueue.length === 0) {
      return;
    }
    
    this.isProcessingQueue = true;
    const request = this.requestQueue.shift();
    if (!request) {
      this.isProcessingQueue = false;
      return;
    }

    if (!this.pythonProcess) {
      request.reject(new Error('Python backend process is not running'));
      this.isProcessingQueue = false;
      this.processQueue();
      return;
    }

    const { id, channel, payload, resolve, reject } = request;
    this.activeRequestId = id;
    this.pendingRequests.set(id, { resolve, reject, channel });
    logger.logIpc(`SEND channel=${channel} req_id=${id}`);

    const timeout = setTimeout(() => {
      logger.logElectron(`Request ${id} timed out after 30s. Triggering recovery.`, 'ERROR');
      this.handleRequestTimeout(id);
    }, 30000);
    this.requestTimeouts.set(id, timeout);

    try {
      const message = JSON.stringify({ id, channel, payload }) + '\n';
      this.pythonProcess.stdin!.write(message);
    } catch (err: any) {
      this.clearRequestTimeout(id);
      this.pendingRequests.delete(id);
      this.activeRequestId = null;
      reject(err);
      this.recover();
    } finally {
      this.isProcessingQueue = false;
    }
  }

  private clearRequestTimeout(id: string): void {
    const timeout = this.requestTimeouts.get(id);
    if (timeout) {
      clearTimeout(timeout);
      this.requestTimeouts.delete(id);
    }
  }

  private handleRequestTimeout(id: string): void {
    if (this.pendingRequests.has(id)) {
      const { reject, channel } = this.pendingRequests.get(id)!;
      this.pendingRequests.delete(id);
      this.requestTimeouts.delete(id);
      
      reject(new Error(`IPC Request timeout on channel ${channel} after 30000ms`));
      
      if (this.activeRequestId === id) {
        this.activeRequestId = null;
      }
      
      this.recover();
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.pingInterval = setInterval(async () => {
      if (this.isRecovering || !this.pythonProcess) return;
      
      try {
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Heartbeat Timeout')), 5000)
        );
        
        await Promise.race([
          this.invoke('system:ping', {}),
          timeoutPromise
        ]);
        
        this.recoveryAttempts = 0; // reset attempts on successful ping
      } catch (err: any) {
        logger.logElectron(`Heartbeat failed: ${err.message}`, 'WARN');
        this.recover();
      }
    }, 10000);
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private recover(): void {
    if (this.isRecovering) return;
    this.isRecovering = true;
    this.stopHeartbeat();
    
    if (this.pythonProcess) {
      try {
        this.pythonProcess.kill();
      } catch (e) {}
      this.pythonProcess = null;
    }

    if (this.activeRequestId && this.pendingRequests.has(this.activeRequestId)) {
      const { reject } = this.pendingRequests.get(this.activeRequestId)!;
      this.clearRequestTimeout(this.activeRequestId);
      this.pendingRequests.delete(this.activeRequestId);
      reject(new Error('Backend process crashed or restarted'));
    }
    this.activeRequestId = null;

    this.recoveryAttempts++;
    this.recoveryCount++;
    if (this.recoveryAttempts > this.maxRecoveryAttempts) {
      logger.logCrash(`CRITICAL: Solver recovery failed after ${this.maxRecoveryAttempts} attempts.`);
      this.notifyFrontendCrash();
      
      for (const req of this.requestQueue) {
        req.reject(new Error('Backend process crashed and failed recovery'));
      }
      this.requestQueue = [];
      this.isRecovering = false;
      return;
    }

    logger.logElectron(`Attempting backend restart (Attempt ${this.recoveryAttempts}/${this.maxRecoveryAttempts})...`);
    this.start();
    this.isRecovering = false;
    
    this.notifyFrontendStatus('recovered');
    
    this.processQueue();
  }

  private notifyFrontendCrash(): void {
    this.notifyFrontendStatus('crashed');
  }

  private notifyFrontendStatus(status: 'crashed' | 'recovered'): void {
    try {
      const windows = BrowserWindow.getAllWindows();
      for (const w of windows) {
        if (!w.isDestroyed()) {
          w.webContents.send('solver:status', { status, attempts: this.recoveryAttempts });
        }
      }
    } catch (err) {
      logger.logElectron(`Failed to notify frontend status: ${err}`, 'WARN');
    }
  }

  public stop(): void {
    this.manualStop = true;
    this.stopHeartbeat();
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
    
    for (const [id, { reject }] of this.pendingRequests.entries()) {
      this.clearRequestTimeout(id);
      reject(new Error('Backend process stopped by Electron'));
    }
    this.pendingRequests.clear();
    this.requestQueue = [];
    this.activeRequestId = null;
  }
}

export const pythonRunner = new PythonRunner();
