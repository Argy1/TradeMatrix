import path from "node:path";

import { defineConfig } from "vitest/config";

export default defineConfig({
  // Unit tests only; the browser tests in e2e/ run with Playwright.
  test: { include: ["src/**/*.test.ts"] },
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
});
