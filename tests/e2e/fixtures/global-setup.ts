import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

import { chromium, type FullConfig } from "@playwright/test";

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const storagePath = "tests/e2e/.auth/storage-state.json";
  mkdirSync(dirname(storagePath), { recursive: true });
  await page.goto(`${config.projects[0]?.use?.baseURL ?? "http://localhost"}/login`);
  await page.getByLabel(/e-mail/i).fill("admin@triagem.local");
  await page.getByLabel(/senha/i).fill("Admin@2024");
  await page.getByRole("button", { name: /entrar/i }).click();
  await page.context().storageState({ path: storagePath });
  await browser.close();
}

export default globalSetup;
