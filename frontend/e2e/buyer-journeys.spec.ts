import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("direct search reaches URL-backed results and preserves return navigation", async ({ page }) => {
  await page.goto("/en-ae");
  await page.getByLabel("Make or model").fill("Toyota");
  await page.getByRole("button", { name: "Search cars" }).click();
  await expect(page).toHaveURL(/\/en-ae\/cars\?q=Toyota/);
  await expect(page.getByRole("heading", { name: "Cars for sale" })).toBeVisible();
  await page.getByRole("link", { name: /^View / }).first().click();
  const back = page.getByRole("link", { name: "Back to results" });
  await expect(back).toHaveAttribute("href", /q=Toyota/);
  await back.click();
  await expect(page).toHaveURL(/q=Toyota/);
});

test("fixture assistant converges on the catalogue query", async ({ page }) => {
  await page.goto("/en-ae");
  await page.getByRole("button", { name: "Describe what you need" }).click();
  await page.getByLabel("Describe your ideal car").fill("A GCC SUV under AED 180k from 2021");
  await page.getByRole("button", { name: /Start AI search/ }).click();
  await expect(page.getByRole("heading", { name: "Describe your next car" })).toBeVisible();
  await page.getByRole("link", { name: /Search now/ }).click();
  await expect(page).toHaveURL(/bodyType=SUV/);
  await expect(page).toHaveURL(/priceMax=180000/);
});

test("comparison and shortlist persist in the browser profile", async ({ page }) => {
  await page.goto("/en-ae/cars");
  await page.getByRole("button", { name: "Compare" }).nth(0).click();
  await page.getByRole("button", { name: "Compare" }).nth(0).click();
  await page.getByRole("button", { name: "Add to shortlist" }).first().click();
  await page.getByRole("link", { name: /Compare now/ }).click();
  await expect(page.getByRole("heading", { name: "Compare vehicles" })).toBeVisible();
  await expect(page.getByText("2 of 4 vehicles")).toBeVisible();
  await page.goto("/en-ae/shortlist");
  await expect(page.getByRole("heading", { name: "Buyer workspace" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Remove from shortlist" })).toHaveCount(1);
  await page.reload();
  await expect(page.getByRole("button", { name: "Remove from shortlist" })).toHaveCount(1);
});

test("model intelligence responds to controls without horizontal page overflow", async ({ page }) => {
  await page.goto("/en-ae/market/toyota/land-cruiser");
  await expect(page.getByRole("heading", { level: 1, name: "Toyota Land Cruiser" })).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflow).toBe(false);
});

test("home has no automatically detectable accessibility violations", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One full axe pass is sufficient.");
  await page.goto("/en-ae");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
