import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
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
  'blast:calculateEnvironment',
  'material:assessBatch',
  'research:parametricSweep',
  'research:compareScenarios',
  'units:list',
  'units:convert',
  'ufc:search'
];

for (const channel of channels) {
  ipcMain.handle(channel, async (event, payload) => {
    try {
      return await pythonRunner.invoke(channel, payload);
    } catch (e: any) {
      console.error(`Error executing IPC invoke on channel ${channel}:`, e.message);
      throw e;
    }
  });
}
