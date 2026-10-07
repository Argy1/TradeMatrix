import { expect, test } from "@playwright/test";

// The four widths from docs/08; screenshots land in test-results/ for a visual check.
const WIDTHS = [1440, 1024, 768, 390];

test("markets home lists every coin with its signals", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "See which way the market leans before you decide." })).toBeVisible();
  for (const symbol of ["BTC", "ETH", "SOL", "BNB", "XRP"]) {
    await expect(page.getByRole("link", { name: new RegExp(`^${symbol}`) }).first()).toBeVisible();
  }
  await expect(page.getByText("Created by Argy").first()).toBeVisible();
});

test("coin page shows a complete, honest signal", async ({ page }) => {
  await page.goto("/markets/BTC?tf=1h");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("rise or fall in the next 1h");
  const card = page.getByRole("article", { name: /signal/ });
  await expect(card).toBeVisible({ timeout: 60_000 });
  await expect(card.getByText("TRADEMATRIX SIGNAL")).toBeVisible();
  await expect(card.getByRole("heading", { name: "Why this signal" })).toBeVisible();
  await expect(card.getByRole("heading", { name: "How reliable is it?" })).toBeVisible();
  await expect(card.getByText(/not financial advice/)).toBeVisible();
  await expect(page.locator('section[aria-label="Chart"] canvas').first()).toBeVisible();
});

for (const width of WIDTHS) {
  test(`coin page has no horizontal scroll at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/markets/ETH?tf=4h");
    await expect(page.getByRole("article", { name: /signal/ })).toBeVisible({ timeout: 60_000 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    await page.screenshot({ path: `test-results/coin-${width}.png`, fullPage: true });
  });
}

test("alerts are offered to signed-out visitors without showing anyone's data", async ({ page }) => {
  await page.goto("/alerts");
  await expect(page.getByRole("heading", { level: 1, name: "Alerts" })).toBeVisible();
  await expect(page.getByText(/Sign in to get a notification/)).toBeVisible();
  await expect(page.getByRole("main").getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
  // The button under the signal leads to sign-in instead of failing silently.
  await page.goto("/markets/BTC?tf=1h");
  const card = page.getByRole("article", { name: /signal/ });
  await expect(card).toBeVisible({ timeout: 60_000 });
  await expect(card.getByRole("link", { name: "Sign in to get alerts" })).toHaveAttribute("href", "/login");
});
