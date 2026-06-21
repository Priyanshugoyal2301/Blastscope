import { _electron as electron } from 'playwright';
import { test, expect } from '@playwright/test';
import * as path from 'path';

test.describe('BlastScope Subprocess Recovery E2E Suite', () => {
  const mainJsPath = path.join(__dirname, '..', 'dist-electron', 'main.js');

  test('Kill Case - Solver manually killed recovers successfully', async () => {
    process.env.BLASTSCOPE_TESTING = '1';
    console.log('Starting Kill Case E2E...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // 1. Reset recovery attempts
    await window.evaluate(() => (window as any).api.invoke('test:reset-recovery-attempts'));
    
    // 2. Kill the solver
    console.log('Sending kill command...');
    await window.evaluate(() => (window as any).api.invoke('test:kill-solver'));

    // 3. Wait for the 10s heartbeat interval + buffer to detect and recover
    console.log('Waiting 12 seconds for heartbeat recovery to execute...');
    await window.waitForTimeout(12000);

    // 4. Verify that recovery attempts incremented to 1
    const attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    console.log(`Recovery attempts after kill: ${attempts}`);
    expect(attempts).toBe(1);

    // 5. Verify the app is still functional by listing explosives (needs active backend solver)
    const explosives = await window.evaluate(() => (window as any).api.invoke('explosives:list'));
    expect(explosives.length).toBeGreaterThan(0);
    console.log('App is verified functional after recovery.');

    await electronApp.close();
  });

  test('Freeze Case - Solver frozen is detected by heartbeat and restarted', async () => {
    process.env.BLASTSCOPE_TESTING = '1';
    console.log('Starting Freeze Case E2E...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // 1. Reset recovery attempts
    await window.evaluate(() => (window as any).api.invoke('test:reset-recovery-attempts'));

    // 2. Freeze the solver (15s sleep block in backend)
    console.log('Sending freeze command...');
    await window.evaluate(() => (window as any).api.invoke('test:freeze-solver'));

    // 3. Wait for heartbeat timeout (runs every 10s, timeout is 5s)
    console.log('Waiting 18 seconds for freeze timeout detection and recovery...');
    await window.waitForTimeout(18000);

    // 4. Verify recovery attempts incremented to 1
    const attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    console.log(`Recovery attempts after freeze: ${attempts}`);
    expect(attempts).toBe(1);

    // 5. Verify the app is still functional
    const explosives = await window.evaluate(() => (window as any).api.invoke('explosives:list'));
    expect(explosives.length).toBeGreaterThan(0);
    console.log('App is verified functional after freeze timeout.');

    await electronApp.close();
  });

  test('Crash Loop Case - Multi-crash exceeding limit displays error page', async () => {
    process.env.BLASTSCOPE_TESTING = '1';
    console.log('Starting Crash Loop Case E2E...');
    const electronApp = await electron.launch({
      args: [mainJsPath],
      env: process.env
    });

    const window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');

    // 1. Reset recovery attempts
    await window.evaluate(() => (window as any).api.invoke('test:reset-recovery-attempts'));

    // 2. Trigger crash 1
    console.log('Triggering crash 1...');
    await window.evaluate(() => (window as any).api.invoke('test:crash-solver'));
    await window.waitForTimeout(3000);
    let attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    expect(attempts).toBe(1);

    // Trigger crash 2
    console.log('Triggering crash 2...');
    await window.evaluate(() => (window as any).api.invoke('test:crash-solver'));
    await window.waitForTimeout(3000);
    attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    expect(attempts).toBe(2);

    // Trigger crash 3
    console.log('Triggering crash 3...');
    await window.evaluate(() => (window as any).api.invoke('test:crash-solver'));
    await window.waitForTimeout(3000);
    attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    expect(attempts).toBe(3);

    // Trigger crash 4 (exceeds maxRecoveryAttempts = 3)
    console.log('Triggering crash 4...');
    await window.evaluate(() => (window as any).api.invoke('test:crash-solver'));
    await window.waitForTimeout(3000);
    
    attempts = await window.evaluate(() => (window as any).api.invoke('test:get-recovery-attempts'));
    console.log(`Final recovery attempts count: ${attempts}`);
    expect(attempts).toBe(4);

    // 3. Verify the frontend displays the crash error page
    const errorTitle = window.locator('#solver-error-title');
    await expect(errorTitle).toBeVisible();
    await expect(errorTitle).toContainText('Solver Process Crash Loop Detected');
    console.log('Frontend successfully displayed the crash loop error page.');

    await electronApp.close();
  });
});
