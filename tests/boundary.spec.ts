import { _electron as electron } from 'playwright';
import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('BlastScope Sweep Point Boundary E2E Suite', () => {
  const mainJsPath = path.join(__dirname, '..', 'dist-electron', 'main.js');

  test('IPC Layer Enforces 10,000 Point Boundary Limit', async () => {
    process.env.BLASTSCOPE_TESTING = '1';
    console.log('Launching Electron to verify IPC-layer point limits...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // 1. Try to invoke studies:runGrid with 10,100 points (101 * 100 * 1)
    const largePayload = {
      explosive_id: 1,
      charges_kg: Array.from({ length: 101 }, (_, i) => i + 1),
      distances_m: Array.from({ length: 100 }, (_, i) => i + 1),
      profile_ids: [1],
      burst_type: 'Surface'
    };

    console.log('Invoking studies:runGrid with 10,100 points via IPC...');
    let ipcError: any = null;
    try {
      await window.evaluate((payload) => (window as any).api.invoke('studies:runGrid', payload), largePayload);
    } catch (err: any) {
      ipcError = err;
    }

    console.log('Error returned from IPC:', ipcError?.message);
    expect(ipcError).not.toBeNull();
    expect(ipcError.message).toContain('IPC Boundary Protection');
    expect(ipcError.message).toContain('exceeds hard limit of 10000');

    await electronApp.close();
  });

  test('UI Layer Enforces 10,000 Point Limit and Disables Button', async () => {
    process.env.BLASTSCOPE_TESTING = '1';
    console.log('Launching Electron to verify UI-layer point limits...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // Navigate to Parametric Study tab
    console.log('Navigating to Parametric Study tab...');
    await window.locator('button:has-text("Parametric Study")').click();
    await window.waitForTimeout(500);

    // Select Grid Study sub-tab
    console.log('Selecting Grid Study tab...');
    await window.locator('button:has-text("Grid Study")').click();
    await window.waitForTimeout(500);

    // Enter range yielding 100 charges (1:100:1)
    console.log('Entering charge range yielding 100 points...');
    const chargeInput = window.locator('input[type="text"]').nth(0);
    await chargeInput.clear();
    await chargeInput.fill('1:100:1');

    // Enter range yielding 101 distances (1:101:1)
    console.log('Entering distance range yielding 101 points...');
    const distanceInput = window.locator('input[type="text"]').nth(1);
    await distanceInput.clear();
    await distanceInput.fill('1:101:1');

    await window.waitForTimeout(1000);

    // 1. Verify warning text and points indicator
    console.log('Verifying estimated point count text indicates 30,300...');
    const bodyText = await window.locator('body').innerText();
    expect(bodyText).toContain('30,300');

    // 2. Verify "Run Study" button is disabled
    const runBtn = window.locator('button:has-text("Run Study"), button:has-text("Run Sweep")');
    const isDisabled = await runBtn.first().isDisabled();
    console.log(`Is Run Study button disabled? ${isDisabled}`);
    expect(isDisabled).toBe(true);

    // 3. Now let's change distances to 1:30:1 to get exactly 9,000 points (100 * 30 * 3)
    console.log('Entering distance range yielding 30 points (total 9,000 points)...');
    await distanceInput.clear();
    await distanceInput.fill('1:30:1');
    await window.waitForTimeout(1000);

    // Verify it is no longer disabled
    const isDisabledNow = await runBtn.first().isDisabled();
    console.log(`Is Run Study button disabled at 9,000 points? ${isDisabledNow}`);
    expect(isDisabledNow).toBe(false);

    await electronApp.close();
  });
});
