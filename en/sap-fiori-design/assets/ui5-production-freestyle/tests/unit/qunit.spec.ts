import { expect, test } from "@playwright/test";

test("runs discovered UI5 QUnit tests with zero failures", async ({ page }) => {
  test.setTimeout(120_000);
  const runtimeErrors: string[] = [];
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") runtimeErrors.push(message.text());
  });
  await page.goto("/test/Test.qunit.html?testsuite=test-resources/__APP_PATH__/testsuite.qunit&test=unit/unitTests");
  const result = page.locator("#qunit-testresult");
  await expect(result).toContainText("completed", { timeout: 60_000 });
  const failures = await page.locator("#qunit-tests > li.fail").allTextContents();
  expect(failures, failures.join("\n")).toEqual([]);
  const total = Number(await result.locator(".total").textContent());
  expect(total).toBeGreaterThan(0);
  expect(runtimeErrors, runtimeErrors.join("\n")).toEqual([]);
});
