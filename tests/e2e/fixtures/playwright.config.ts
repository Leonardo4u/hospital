import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "../",
  timeout: 10000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: "http://localhost",
    browserName: "chromium",
    headless: true,
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    storageState: "tests/e2e/.auth/storage-state.json",
  },
  globalSetup: "./global-setup.ts",
});
