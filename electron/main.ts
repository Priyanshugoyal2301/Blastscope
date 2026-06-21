import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { pythonRunner } from './python-runner';
import { logger } from './logger';

// Uncaught exception capture routing
process.on('uncaughtException', (error) => {
  logger.logCrash('Uncaught Exception in Main Process', error);
});

process.on('unhandledRejection', (reason) => {
  logger.logCrash('Unhandled Rejection in Main Process', new Error(String(reason)));
});

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  logger.logElectron('Creating BrowserWindow...');
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: 'default',
  });

  // In development, load the local Vite server. In production/test, load the built HTML.
  const isDev = (process.env.NODE_ENV === 'development' || (process.env.NODE_ENV !== 'production' && !app.isPackaged)) && process.env.BLASTSCOPE_TESTING !== '1';
  if (isDev) {
    logger.logElectron('Loading Dev Vite Server: http://localhost:5173');
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    const htmlPath = path.join(__dirname, '..', 'dist', 'index.html');
    logger.logElectron(`Loading Production HTML File: ${htmlPath}`);
    mainWindow.loadFile(htmlPath);
  }

  mainWindow.on('closed', () => {
    logger.logElectron('BrowserWindow closed event triggered.');
    mainWindow = null;
  });
}

// Start Python process when Electron is ready
app.whenReady().then(() => {
  logger.logElectron('Electron Ready. Starting Python solver runner...');
  pythonRunner.start();

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Clean up Python process on exit
app.on('window-all-closed', () => {
  logger.logElectron('window-all-closed event triggered.');
  pythonRunner.stop();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  logger.logElectron('app quit event triggered.');
  pythonRunner.stop();
});

// Dynamic IPC router: maps React frontend requests straight to Python runner
const channels = [
  'scenarios:list',
  'scenarios:save',
  'scenarios:saveNote',
  'scenarios:listNotes',
  'explosives:list',
  'materials:listProfiles',
  'materials:getPIEnvelopes',
  'blast:calculateEnvironment',
  'material:assessBatch',
  'research:parametricSweep',
  'research:compareScenarios',
  'units:list',
  'units:convert',
  'ufc:search',
  'validation:runSweep',
  'validation:getSummary',
  'studies:distanceSweep',
  'studies:chargeSweep',
  'studies:explosiveComparison',
  'studies:runGrid',
  'studies:exportCSV',
  'inverse:predict',
  'database:export',
  'database:import'
];

const pythonChannels = channels.filter(c => c !== 'database:export' && c !== 'database:import');

function checkPointLimit(channel: string, payload: any): void {
  const HARD_LIMIT = 10000;
  let count = 0;
  if (channel === 'studies:distanceSweep') {
    count = (payload.distances_m?.length || 0) * (payload.profile_ids?.length || 0);
  } else if (channel === 'studies:chargeSweep') {
    count = (payload.charges_kg?.length || 0) * (payload.profile_ids?.length || 0);
  } else if (channel === 'studies:explosiveComparison') {
    count = (payload.explosive_ids?.length || 0) * (payload.distances_m?.length || 0) * (payload.profile_ids?.length || 0);
  } else if (channel === 'studies:runGrid') {
    count = (payload.charges_kg?.length || 0) * (payload.distances_m?.length || 0) * (payload.profile_ids?.length || 0);
  } else {
    return;
  }
  
  if (count > HARD_LIMIT) {
    throw new Error(`IPC Boundary Protection: Sweep point count ${count} exceeds hard limit of ${HARD_LIMIT}.`);
  }
}

for (const channel of pythonChannels) {
  ipcMain.handle(channel, async (event, payload) => {
    const start = Date.now();
    try {
      logger.logIpc(`IPC CALL channel=${channel}`);
      checkPointLimit(channel, payload);
      const result = await pythonRunner.invoke(channel, payload);
      const duration = Date.now() - start;
      logger.logIpc(`IPC SUCCESS channel=${channel} duration=${duration}ms`);
      return result;
    } catch (e: any) {
      const duration = Date.now() - start;
      logger.logIpc(`IPC ERROR channel=${channel} duration=${duration}ms error=${e.message}`, 'ERROR');
      throw e;
    }
  });
}

// Helper to get active DB path
function getDbPath(): string {
  const isPackaged = app.isPackaged;
  if (isPackaged || process.env.BLASTSCOPE_TESTING === '1') {
    return path.join(app.getPath('userData'), 'sqlite.db');
  }
  return path.join(__dirname, '..', 'backend', 'database', 'sqlite.db');
}

ipcMain.handle('database:export', async () => {
  if (!mainWindow) return { success: false, error: 'No active window' };
  logger.logIpc('IPC CALL channel=database:export');
  
  const dbPath = getDbPath();
  logger.logIpc(`database:export resolved dbPath: "${dbPath}" exists: ${fs.existsSync(dbPath)} app.getPath("userData"): "${app.getPath('userData')}" BLASTSCOPE_TESTING: "${process.env.BLASTSCOPE_TESTING}"`);
  if (!fs.existsSync(dbPath)) {
    logger.logIpc(`database:export failed: Database file not found at "${dbPath}"`, 'ERROR');
    return { success: false, error: 'Database file not found' };
  }
  
  let filePath: string;
  if (process.env.BLASTSCOPE_TESTING === '1') {
    filePath = path.join(app.getPath('userData'), 'mock_backup.db');
  } else {
    const result = await dialog.showSaveDialog(mainWindow, {
      title: 'Export BlastScope Database',
      defaultPath: 'blastscope_backup.db',
      filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
    });

    if (result.canceled || !result.filePath) {
      logger.logIpc('database:export dialog canceled');
      return { success: false, canceled: true };
    }
    filePath = result.filePath;
  }

  try {
    await fs.promises.copyFile(dbPath, filePath);
    logger.logIpc(`database:export success: DB copied to ${filePath}`);
    logger.logSolver(`Database manually exported to: ${filePath}`);
    return { success: true, filePath };
  } catch (err: any) {
    logger.logIpc(`database:export failed: ${err.message}`, 'ERROR');
    logger.logCrash('Failed to manually export database', err);
    return { success: false, error: err.message };
  }
});

ipcMain.handle('database:import', async () => {
  if (!mainWindow) return { success: false, error: 'No active window' };
  logger.logIpc('IPC CALL channel=database:import');
  
  let sourcePath: string;
  if (process.env.BLASTSCOPE_TESTING === '1') {
    sourcePath = path.join(app.getPath('userData'), 'mock_backup.db');
    if (!fs.existsSync(sourcePath)) {
      const dbPath = getDbPath();
      if (fs.existsSync(dbPath)) {
        fs.copyFileSync(dbPath, sourcePath);
      } else {
        logger.logIpc('database:import failed: mock source DB not found', 'ERROR');
        return { success: false, error: 'Mock source DB not found' };
      }
    }
  } else {
    const result = await dialog.showOpenDialog(mainWindow, {
      title: 'Import BlastScope Database',
      properties: ['openFile'],
      filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
    });

    if (result.canceled || !result.filePaths || result.filePaths.length === 0) {
      logger.logIpc('database:import dialog canceled');
      return { success: false, canceled: true };
    }
    sourcePath = result.filePaths[0];
  }

  const dbPath = getDbPath();
  const dbDir = path.dirname(dbPath);

  try {
    if (!fs.existsSync(dbDir)) {
      await fs.promises.mkdir(dbDir, { recursive: true });
    }

    logger.logElectron('Stopping Python solver to unlock database for import...');
    pythonRunner.stop();

    await fs.promises.copyFile(sourcePath, dbPath);
    logger.logIpc(`database:import success: DB imported from ${sourcePath}`);
    logger.logSolver(`Database manually imported from: ${sourcePath}`);
    
    logger.logElectron('Import successful. Restarting Python solver...');
    pythonRunner.start();

    return { success: true, filePath: dbPath };
  } catch (err: any) {
    logger.logIpc(`database:import failed: ${err.message}`, 'ERROR');
    logger.logCrash('Failed to manually import database', err);
    pythonRunner.start();
    return { success: false, error: err.message };
  }
});

if (process.env.BLASTSCOPE_TESTING === '1') {
  ipcMain.handle('test:kill-solver', async () => {
    logger.logElectron('TEST IPC: Killing solver process...');
    const proc = (pythonRunner as any).pythonProcess;
    if (proc) {
      proc.kill();
      return { success: true };
    }
    return { success: false, error: 'No process running' };
  });

  ipcMain.handle('test:freeze-solver', async () => {
    logger.logElectron('TEST IPC: Freezing solver process...');
    pythonRunner.invoke('system:ping', { simulate_freeze: true }).catch(() => {});
    return { success: true };
  });

  ipcMain.handle('test:crash-solver', async () => {
    logger.logElectron('TEST IPC: Crashing solver process...');
    pythonRunner.invoke('system:ping', { simulate_crash: true }).catch(() => {});
    return { success: true };
  });

  ipcMain.handle('test:get-recovery-attempts', async () => {
    return (pythonRunner as any).recoveryCount;
  });

  ipcMain.handle('test:reset-recovery-attempts', async () => {
    (pythonRunner as any).recoveryAttempts = 0;
    (pythonRunner as any).recoveryCount = 0;
    return { success: true };
  });
}

