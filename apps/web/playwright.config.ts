import { defineConfig, devices } from "@playwright/test";

// Smoke tests against a running app (the dev server, or BASE_URL for a deployed site).
export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:3000",
    ...devices["Desktop Chrome"],
    // PW_CHANNEL=chrome uses the installed Google Chrome (fresh temporary profile) instead of
    // Playwright's own Chromium download.
    ...(process.env.PW_CHANNEL ? { channel: process.env.PW_CHANNEL } : {}),
  },
  webServer: process.env.BASE_URL
    ? undefined
    : { command: "npm run dev", url: "http://localhost:3000", reuseExistingServer: true, timeout: 120_000 },
  reporter: [["list"]],
});
