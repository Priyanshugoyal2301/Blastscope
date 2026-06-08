import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { pythonRunner } from './python-runner';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
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

  // In development, load the local Vite server. In production, load the built HTML.
  const isDev = process.env.NODE_ENV === 'development' || (process.env.NODE_ENV !== 'production' && !app.isPackaged);
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Start Python process when Electron is ready
app.whenReady().then(() => {
  console.log('Starting Python backend process...');
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
  pythonRunner.stop();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
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
  'database:export',
  'database:import'
];

const pythonChannels = channels.filter(c => c !== 'database:export' && c !== 'database:import');

for (const channel of pythonChannels) {
  ipcMain.handle(channel, async (event, payload) => {
    try {
      return await pythonRunner.invoke(channel, payload);
    } catch (e: any) {
      console.error(`Error executing IPC invoke on channel ${channel}:`, e.message);
      throw e;
    }
  });
}



// Helper to get active DB path
function getDbPath(): string {
  const isPackaged = app.isPackaged;
  const appdata = process.env.APPDATA;
  if (isPackaged && appdata) {
    return path.join(appdata, 'BlastScope', 'sqlite.db');
  }
  return path.join(__dirname, '..', 'backend', 'database', 'sqlite.db');
}

ipcMain.handle('database:export', async () => {
  if (!mainWindow) return { success: false, error: 'No active window' };
  const dbPath = getDbPath();
  if (!fs.existsSync(dbPath)) {
    return { success: false, error: 'Database file not found' };
  }
  
  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Export BlastScope Database',
    defaultPath: 'blastscope_backup.db',
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
  });

  if (result.canceled || !result.filePath) {
    return { success: false, canceled: true };
  }

  try {
    await fs.promises.copyFile(dbPath, result.filePath);
    return { success: true, filePath: result.filePath };
  } catch (err: any) {
    console.error('Failed to export database:', err);
    return { success: false, error: err.message };
  }
});

ipcMain.handle('database:import', async () => {
  if (!mainWindow) return { success: false, error: 'No active window' };
  
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Import BlastScope Database',
    properties: ['openFile'],
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
  });

  if (result.canceled || !result.filePaths || result.filePaths.length === 0) {
    return { success: false, canceled: true };
  }

  const sourcePath = result.filePaths[0];
  const dbPath = getDbPath();
  const dbDir = path.dirname(dbPath);

  try {
    if (!fs.existsSync(dbDir)) {
      await fs.promises.mkdir(dbDir, { recursive: true });
    }

    console.log('Stopping Python solver to unlock database...');
    pythonRunner.stop();

    await fs.promises.copyFile(sourcePath, dbPath);
    console.log('Import successful. Restarting Python solver...');
    pythonRunner.start();

    return { success: true, filePath: dbPath };
  } catch (err: any) {
    console.error('Failed to import database:', err);
    pythonRunner.start();
    return { success: false, error: err.message };
  }
});

