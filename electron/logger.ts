import * as fs from 'fs';
import * as path from 'path';
import { app } from 'electron';

export class Logger {
  private logsDir: string;

  constructor() {
    // Redirect logs to workspace-local logs/ folder during E2E testing for easier debugging
    if (process.env.BLASTSCOPE_TESTING === '1') {
      this.logsDir = path.join(__dirname, '..', 'logs');
    } else {
      const appData = app ? app.getPath('userData') : process.env.APPDATA || '';
      if (appData) {
        this.logsDir = path.join(appData, 'logs');
      } else {
        this.logsDir = path.join(__dirname, '..', 'logs');
      }
    }

    this.ensureDirectoryExists();
  }

  private ensureDirectoryExists(): void {
    try {
      if (!fs.existsSync(this.logsDir)) {
        fs.mkdirSync(this.logsDir, { recursive: true });
      }
    } catch (err) {
      console.error('Failed to create logs directory:', err);
    }
  }

  private writeLog(filename: string, message: string, level: string = 'INFO'): void {
    this.ensureDirectoryExists();
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 23);
    const formattedMessage = `[${timestamp}] [${level}] ${message}\n`;
    const logFilePath = path.join(this.logsDir, filename);

    try {
      // Append to the file, print warning if fails
      fs.appendFileSync(logFilePath, formattedMessage, 'utf8');
      
      // Limit file size to 10MB to avoid disk bloat
      const stats = fs.statSync(logFilePath);
      if (stats.size > 10 * 1024 * 1024) {
        fs.renameSync(logFilePath, `${logFilePath}.old`);
      }
    } catch (err) {
      console.warn(`Failed writing to log file ${filename}:`, err);
    }
  }

  public logElectron(message: string, level: string = 'INFO'): void {
    console.log(`[Electron] [${level}]: ${message}`);
    this.writeLog('electron.log', message, level);
  }

  public logIpc(message: string, level: string = 'INFO'): void {
    this.writeLog('ipc.log', message, level);
  }

  public logBackend(message: string, level: string = 'INFO'): void {
    this.writeLog('backend.log', message, level);
  }

  public logCrash(message: string, error?: any): void {
    let msg = message;
    if (error) {
      msg += `\nError: ${error.message || error}\nStack: ${error.stack || 'No Stack Trace'}`;
    }
    console.error(`[CRASH]: ${msg}`);
    this.writeLog('crash.log', msg, 'CRITICAL');
  }

  public logSolver(message: string, level: string = 'INFO'): void {
    console.log(`[Solver] [${level}]: ${message}`);
    this.writeLog('solver.log', message, level);
  }
}

export const logger = new Logger();
