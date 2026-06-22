const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('--- Starting Standalone Python Solver Compilation ---');

// Verify Python installation
const pythonCheck = spawnSync('python', ['--version'], { encoding: 'utf8' });
if (pythonCheck.status !== 0) {
  console.error('ERROR: Python is not available in PATH. Standalone build requires local Python.');
  process.exit(1);
}
console.log(`Using Python: ${pythonCheck.stdout.trim() || pythonCheck.stderr.trim()}`);

// Check if PyInstaller is installed
console.log('Checking for PyInstaller...');
const pyinstallerCheck = spawnSync('python', ['-c', 'import PyInstaller'], { encoding: 'utf8' });
if (pyinstallerCheck.status !== 0) {
  console.log('PyInstaller not found. Installing PyInstaller...');
  const installResult = spawnSync('python', ['-m', 'pip', 'install', 'pyinstaller'], {
    stdio: 'inherit',
    shell: true
  });
  if (installResult.status !== 0) {
    console.error('ERROR: Failed to install PyInstaller via pip.');
    process.exit(1);
  }
  console.log('PyInstaller successfully installed.');
} else {
  console.log('PyInstaller is already installed.');
}

// Clean previous build directories to prevent stale caches
const distPath = path.join(__dirname, '..', 'backend-dist');
const buildPath = path.join(__dirname, '..', 'build-solver');
if (fs.existsSync(distPath)) {
  console.log(`Cleaning previous build folder: ${distPath}`);
  fs.rmSync(distPath, { recursive: true, force: true });
}
if (fs.existsSync(buildPath)) {
  console.log(`Cleaning previous build temp folder: ${buildPath}`);
  fs.rmSync(buildPath, { recursive: true, force: true });
}

// Execute PyInstaller command
// On Windows, --add-data uses ";" separator
// --onedir structures the solver as a folder
console.log('Compiling main.py to standalone executable...');
const pyinstallerCmd = 'pyinstaller';
const args = [
  '--onedir',
  '--name', 'blastscope-solver',
  '--distpath', distPath,
  '--workpath', buildPath,
  '--paths', '.',
  '--add-data', 'backend/database/schema.sql;backend/database',
  '--add-data', 'backend/database/migrations;backend/database/migrations',
  '--add-data', 'backend/blast_engine/models;blast_engine/models',
  'backend/main.py'
];

console.log(`Running: ${pyinstallerCmd} ${args.join(' ')}`);
const buildResult = spawnSync(pyinstallerCmd, args, {
  stdio: 'inherit',
  shell: true,
  cwd: path.join(__dirname, '..')
});

if (buildResult.status !== 0) {
  console.error('ERROR: PyInstaller compilation failed.');
  process.exit(1);
}

console.log('\n✅ Standalone solver successfully compiled in: backend-dist/blastscope-solver/');
process.exit(0);
