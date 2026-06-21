const { _electron: electron } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Parse CLI arguments
const args = {};
process.argv.slice(2).forEach(arg => {
  const [key, value] = arg.split('=');
  args[key.replace(/^--/, '')] = value;
});

const durationSec = parseInt(args.duration || 7200, 10); // Default to 2 hours (7200s)
const iterationDelay = parseInt(args.delay || 1000, 10); // Delay between steps

const logFile = path.join(__dirname, '..', 'logs', 'soak_results.csv');
const logDir = path.dirname(logFile);
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// Write CSV header if not exists
if (!fs.existsSync(logFile)) {
  fs.writeFileSync(logFile, "Timestamp,Iteration,ElapsedSeconds,MainRSS_MB,RendererRSS_MB,SolverRSS_MB,PeakMainRSS_MB,PeakRendererRSS_MB,PeakSolverRSS_MB\n");
}

function getDescendants(parentPid) {
  try {
    const output = execSync(
      `powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq ${parentPid} } | Select-Object ProcessId, CommandLine, Name | ConvertTo-Json"`,
      { stdio: ['pipe', 'pipe', 'ignore'] }
    ).toString().trim();
    if (!output) return [];
    let list = JSON.parse(output);
    if (!Array.isArray(list)) list = [list];
    
    let results = [...list];
    for (const child of list) {
      if (child && child.ProcessId) {
        results.push(...getDescendants(child.ProcessId));
      }
    }
    return results;
  } catch (err) {
    return [];
  }
}

function getProcessMemory(pid) {
  try {
    const bytesStr = execSync(`powershell -Command "(Get-Process -Id ${pid}).WorkingSet64"`, {
      stdio: ['pipe', 'pipe', 'ignore']
    }).toString().trim();
    const bytes = parseInt(bytesStr, 10);
    return isNaN(bytes) ? 0 : bytes;
  } catch (e) {
    return 0;
  }
}

async function runSoakTest() {
  console.log(`Starting Soak Test for duration: ${durationSec} seconds...`);
  process.env.BLASTSCOPE_TESTING = '1';
  
  const mainJsPath = path.join(__dirname, '..', 'dist-electron', 'main.js');
  const electronApp = await electron.launch({
    args: [mainJsPath],
    env: process.env
  });

  const window = await electronApp.firstWindow();
  await window.waitForLoadState('domcontentloaded');

  const mainPid = electronApp.process().pid;
  console.log(`Main Process PID: ${mainPid}`);

  let rendererPid = null;
  let solverPid = null;
  
  await window.waitForTimeout(2000);
  const descendants = getDescendants(mainPid);
  console.log(`Found ${descendants.length} descendant processes.`);
  
  for (const proc of descendants) {
    if (!proc) continue;
    const cmd = proc.CommandLine || '';
    const name = proc.Name || '';
    if (cmd.includes('--type=renderer')) {
      rendererPid = proc.ProcessId;
    } else if (cmd.includes('main.py') || name.includes('blastscope-solver') || cmd.includes('blastscope-solver')) {
      solverPid = proc.ProcessId;
    }
  }

  console.log(`Renderer Process PID: ${rendererPid || 'Not Found'}`);
  console.log(`Solver Process PID: ${solverPid || 'Not Found'}`);

  const startTime = Date.now();
  const endTime = startTime + durationSec * 1000;
  let iteration = 0;

  let peakMain = 0;
  let peakRenderer = 0;
  let peakSolver = 0;

  while (Date.now() < endTime) {
    iteration++;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    console.log(`\n--- Iteration ${iteration} | Elapsed: ${elapsed}s / ${durationSec}s ---`);

    try {
      // 1. Navigation Flow
      const screens = ['Scenario Input', 'Blast Results', 'Material Assessment', 'Research Workspace', 'Parametric Study', 'Vulnerability Map', 'Documentation'];
      for (const scr of screens) {
        const btn = window.locator(`button:has-text("${scr}")`);
        if (await btn.count() > 0) {
          await btn.first().click();
          await window.waitForTimeout(200);
        }
      }

      // 2. Scenario Creation Flow
      await window.locator('button:has-text("Scenario Input")').click();
      await window.waitForTimeout(200);
      
      const scenarioName = `Soak_Sc_${iteration}_${Date.now()}`;
      const nameInput = window.locator('input[type="text"]').first();
      await nameInput.fill(scenarioName);

      const chargeWeightInput = window.locator('input[type="number"]').first();
      await chargeWeightInput.fill('150.0');

      const distanceInput = window.locator('input[type="number"]').nth(1);
      await distanceInput.fill('15.0');

      await window.locator('button:has-text("Save Scenario")').click();
      await window.waitForTimeout(500);

      // 3. Grid Sweep Study Flow
      await window.locator('button:has-text("Parametric Study")').click();
      await window.waitForTimeout(200);
      await window.locator('button:has-text("Grid Study")').click();
      await window.waitForTimeout(200);
      const runSweepBtn = window.locator('button:has-text("Run Study"), button:has-text("Run Sweep")');
      if (await runSweepBtn.count() > 0) {
        await runSweepBtn.first().click();
        await window.waitForTimeout(1000);
      }

      // Collect memory metrics
      const mainRSS = getProcessMemory(mainPid);
      const rendererRSS = rendererPid ? getProcessMemory(rendererPid) : 0;
      const solverRSS = solverPid ? getProcessMemory(solverPid) : 0;

      const mainMB = (mainRSS / (1024 * 1024)).toFixed(2);
      const rendererMB = (rendererRSS / (1024 * 1024)).toFixed(2);
      const solverMB = (solverRSS / (1024 * 1024)).toFixed(2);

      peakMain = Math.max(peakMain, parseFloat(mainMB));
      peakRenderer = Math.max(peakRenderer, parseFloat(rendererMB));
      peakSolver = Math.max(peakSolver, parseFloat(solverMB));

      console.log(`Memory RSS (MB) | Main: ${mainMB} (Peak: ${peakMain}) | Renderer: ${rendererMB} (Peak: ${peakRenderer}) | Solver: ${solverMB} (Peak: ${peakSolver})`);

      // Write to CSV
      const timestamp = new Date().toISOString();
      fs.appendFileSync(logFile, `${timestamp},${iteration},${elapsed},${mainMB},${rendererMB},${solverMB},${peakMain.toFixed(2)},${peakRenderer.toFixed(2)},${peakSolver.toFixed(2)}\n`);

    } catch (e) {
      console.error(`Error in iteration ${iteration}:`, e.message);
    }

    await window.waitForTimeout(iterationDelay);
  }

  console.log("\nSoak test completed successfully!");
  await electronApp.close();
}

runSoakTest().catch(err => {
  console.error("Critical error in soak test runner:", err);
  process.exit(1);
});
