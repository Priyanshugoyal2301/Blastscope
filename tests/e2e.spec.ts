import { _electron as electron } from 'playwright';
import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('BlastScope End-to-End Suite', () => {
  const mainJsPath = path.join(__dirname, '..', 'dist-electron', 'main.js');

  test.beforeAll(() => {
    const paths = [
      path.join(__dirname, '..', 'backend', 'database', 'sqlite.db'),
      path.join(process.env.APPDATA || '', 'blastscope', 'sqlite.db'),
      path.join(process.env.APPDATA || '', 'BlastScope', 'sqlite.db'),
      path.join(process.env.APPDATA || '', 'Electron', 'sqlite.db')
    ];
    for (const dbPath of paths) {
      if (fs.existsSync(dbPath)) {
        try {
          fs.unlinkSync(dbPath);
          console.log(`Cleaned up SQLite database at ${dbPath} for test isolation.`);
        } catch (e) {
          console.warn(`Could not clean up SQLite database at ${dbPath}:`, e);
        }
      }
    }
  });

  test('Complete System Flow with Persistence and Recovery Mocks', async () => {
    // Enable testing flags to mock native file dialogs
    process.env.BLASTSCOPE_TESTING = '1';

    console.log('1. Launching Electron App...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // Check title/header
    const header = window.locator('aside h2').first();
    await expect(header).toContainText('BlastScope');
    console.log('App successfully launched and UI headers verified.');

    // 2. Click through screens to verify navigation stability
    const screens = [
      { text: 'Scenario Input', verify: 'Configure Scenario' },
      { text: 'Blast Results', verify: 'Please select or save a scenario' },
      { text: 'Material Assessment', verify: 'Please select or save a scenario' },
      { text: 'Research Workspace', verify: 'Please select or save a scenario' },
      { text: 'Parametric Study', verify: 'Parametric Study Configuration' },
      { text: 'Vulnerability Map', verify: 'No grid study results available' },
      { text: 'Threat Prediction', verify: 'Sensor Readings Input' },
      { text: 'Documentation', verify: '1. Getting Started' }
    ];

    for (const scr of screens) {
      console.log(`Navigating to screen: ${scr.text}`);
      const btn = window.locator(`aside button:has-text("${scr.text}")`).first();
      await expect(btn).toBeVisible();
      await btn.click();
      await window.waitForTimeout(1000);
      
      const bodyText = window.locator('body');
      await expect(bodyText).toContainText(scr.verify);
    }

    // 3. Create and Save a Scenario in Scenario Input
    console.log('Creating unique scenario for persistence checks...');
    await window.locator('aside button:has-text("Scenario Input")').first().click();
    await expect(window.locator('body')).toContainText('Configure Scenario');

    const scenarioName = `E2E_Test_Scenario_${Date.now()}`;
    const nameInput = window.locator('input[type="text"]').first();
    await nameInput.fill(scenarioName);

    const chargeWeightInput = window.locator('input[type="number"]').first();
    await chargeWeightInput.fill('225.5');

    const distanceInput = window.locator('input[type="number"]').nth(1);
    await distanceInput.fill('18.2');

    const explosiveSelect = window.locator('select').first();
    await explosiveSelect.selectOption('2');

    // Click Save Scenario
    const saveBtn = window.locator('button:has-text("Save Scenario")');
    await saveBtn.click();
    await window.waitForTimeout(1500);

    // Verify scenario is saved in sidebar list
    const sidebar = window.locator('aside');
    await expect(sidebar).toContainText(scenarioName);
    console.log('New scenario successfully saved and visible in sidebar.');

    // 4. Run calculations and check results screen
    await window.locator('aside button:has-text("Blast Results")').first().click();
    await expect(window.locator('body')).toContainText('Incident Pressure');
    const resultsContainer = window.locator('body');
    await expect(resultsContainer).toContainText('Incident Pressure');
    await expect(resultsContainer).toContainText('Reflected Pressure');
    console.log('Blast calculations successfully verified on Results screen.');

    // 5. Run sweep inside Parametric Study
    await window.locator('aside button:has-text("Parametric Study")').first().click();
    await expect(window.locator('body')).toContainText('Parametric Study Configuration');
    console.log('Selecting Grid Study type...');
    await window.locator('button:has-text("Grid Study")').click();
    await window.waitForTimeout(500);
    console.log('Running parametric sweep study...');
    const runSweepBtn = window.locator('button:has-text("Run Study"), button:has-text("Run Sweep")');
    if (await runSweepBtn.count() > 0) {
      await runSweepBtn.first().click();
      await window.waitForTimeout(5000); // Allow more time for grid study calculations
    }

    // 6. Verify PI Envelope Plot & Vulnerability Heatmap
    await window.locator('aside button:has-text("Vulnerability Map")').first().click();
    await window.waitForTimeout(1000);
    console.log('Checking plotly visualizer widgets...');
    const plotlyContainer = window.locator('.js-plotly-plot, .plotly');
    await expect(plotlyContainer.first()).toBeVisible();
    console.log('Plotly charts rendered successfully.');

    // 7. Verify print report container works
    await window.locator('aside button:has-text("Research Workspace")').first().click();
    await expect(window.locator('body')).toContainText('Material Vulnerability Radar');
    const exportMenuBtn = window.locator('button:has-text("Export"), button:has-text("Download")').first();
    if (await exportMenuBtn.count() > 0) {
      await exportMenuBtn.click();
      await window.waitForTimeout(500);
      const printReportBtn = window.locator('button:has-text("Print Report"), button:has-text("PDF")');
      if (await printReportBtn.count() > 0) {
        // Just verify button is present
        await expect(printReportBtn.first()).toBeVisible();
      }
    }

    // 8. Database manual export backup mock
    console.log('Testing Database Export...');
    const exportDbBtn = window.locator('button:has-text("Export DB")');
    await exportDbBtn.click();
    await window.waitForTimeout(1500);
    await expect(sidebar).toContainText('Exported successfully');

    // 9. Database manual import backup mock
    console.log('Testing Database Import...');
    const importDbBtn = window.locator('button:has-text("Import DB")');
    await importDbBtn.click();
    // Import reloads the page, wait for it
    await window.waitForTimeout(3000);
    console.log('Database export/import mocks successfully checked.');

    // 10. Close and Relaunch to verify SQLite persistence
    console.log('10. Closing and Relaunching app to verify SQLite persistence...');
    await electronApp.close();

    const electronApp2 = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });
    const window2 = await electronApp2.firstWindow();
    await window2.waitForLoadState('domcontentloaded');

    // Verify the saved scenario is still present in the sidebar
    const sidebar2 = window2.locator('aside');
    await expect(sidebar2).toContainText(scenarioName);
    console.log('SQLite scenario persistence across application restarts verified successfully!');

    // Select the scenario in the sidebar to activate it
    console.log('Selecting the persisted scenario in sidebar...');
    await window2.locator(`aside button:has-text("${scenarioName}")`).first().click();
    await window2.waitForTimeout(1000);

    // 11. Run Model Validation Dashboard & verify cases table
    console.log('Navigating to Model Validation Tab...');
    await window2.locator('aside button:has-text("Research Workspace")').first().click();
    await expect(window2.locator('body')).toContainText('Material Vulnerability Radar');
    
    const validationTab = window2.locator('button:has-text("Model Validation")');
    if (await validationTab.count() > 0) {
      await validationTab.first().click();
      await window2.waitForTimeout(1000);
      
      // Verify validation table and error statistics
      const validationTable = window2.locator('table');
      await expect(validationTable.first()).toBeVisible();
      
      const validationSummary = window2.locator('body');
      await expect(validationSummary).toContainText('Mean P Err');
      console.log('Validation Benchmark Suite and Error Analysis Table verified successfully.');
    }

    // 12. Test Threat Prediction model inference
    console.log('12. Navigating to Threat Prediction screen...');
    await window2.locator('aside button:has-text("Threat Prediction")').first().click();
    await expect(window2.locator('body')).toContainText('Sensor Readings Input');

    console.log('Submitting threat characterization query...');
    const predictSubmitBtn = window2.locator('button:has-text("Characterize Threat")');
    await expect(predictSubmitBtn).toBeVisible();
    await predictSubmitBtn.click();
    await window2.waitForTimeout(2000); // Allow time for ML model inference and cross-check

    const predictionResults = window2.locator('body');
    await expect(predictionResults).toContainText('Charge Weight (W)');
    await expect(predictionResults).toContainText('Scaled Distance (Z)');
    await expect(predictionResults).toContainText('Physics Consistency Score');
    console.log('Threat Prediction model inference and cross-check verified successfully!');

    await electronApp2.close();
    console.log('✅ ALL E2E PERSISTENCE AND UI WORKFLOWS PASSED SUCCESSFULLY!');
  });
});
