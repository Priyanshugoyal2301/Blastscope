import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60000,
  expect: {
    timeout: 15000,
  },
  workers: 1, // Electron tests must run sequentially
  use: {
    trace: 'on-first-retry',
  },
});
