import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as readline from 'readline';

export class PythonRunner {
  private pythonProcess: ChildProcess | null = null;
  private pendingRequests: Map<string, { resolve: (val: any) => void; reject: (err: any) => void }> = new Map();
  private requestCounter = 0;

  constructor() {}

  public start(): void {
    const backendPath = path.join(__dirname, '..', 'backend', 'main.py');
    const pythonCmds = ['python', 'python3', 'py'];
    
    let spawned = false;
    for (const cmd of pythonCmds) {
      try {
        console.log(`Attempting to launch Python backend with command: ${cmd} on ${backendPath}`);
        this.pythonProcess = spawn(cmd, [backendPath], {
          env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
        });
        
        this.pythonProcess.on('error', (err) => {
          console.warn(`Failed to spawn using ${cmd}:`, err.message);
        });

        if (this.pythonProcess.pid) {
          spawned = true;
          this.setupProcessHandlers();
          break;
        }
      } catch (e: any) {
        console.warn(`Exception spawning ${cmd}:`, e.message);
      }
    }

    if (!spawned) {
      console.error('CRITICAL: Could not launch Python process using any command (python, python3, py). Make sure Python is in your PATH.');
    }
  }

  private setupProcessHandlers(): void {
    if (!this.pythonProcess || !this.pythonProcess.stdout || !this.pythonProcess.stderr) {
      return;
    }

    const rl = readline.createInterface({
      input: this.pythonProcess.stdout,
      terminal: false
    });

    rl.on('line', (line) => {
      try {
        const response = JSON.parse(line.trim());
        const id = response.id;
        
        if (id && this.pendingRequests.has(id)) {
          const { resolve, reject } = this.pendingRequests.get(id)!;
          this.pendingRequests.delete(id);
          
          if (response.success) {
            resolve(response.response);
          } else {
            reject(new Error(response.error || 'Unknown error occurred in Python backend'));
          }
        }
      } catch (e: any) {
        console.error('Error parsing line from Python stdout:', line, e.message);
      }
    });

    this.pythonProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim();
      console.log('[Python Stderr]:', msg);
    });

    this.pythonProcess.on('close', (code) => {
      console.log(`Python subprocess exited with code ${code}`);
      this.pythonProcess = null;
    });
  }

  public invoke(channel: string, payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.pythonProcess) {
        reject(new Error('Python backend process is not running'));
        return;
      }

      this.requestCounter++;
      const id = `req_${Date.now()}_${this.requestCounter}`;
      
      this.pendingRequests.set(id, { resolve, reject });
      
      const message = JSON.stringify({ id, channel, payload }) + '\n';
      this.pythonProcess.stdin!.write(message);
    });
  }

  public stop(): void {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
  }
}

export const pythonRunner = new PythonRunner();
