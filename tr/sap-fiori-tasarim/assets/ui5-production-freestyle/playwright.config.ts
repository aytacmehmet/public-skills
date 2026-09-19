import { defineConfig } from "@playwright/test";

// Read the environment without Node typings: the app is type-checked against the UI5 and QUnit types only.
const environment = (globalThis as { process?: { env: Record<string, string | undefined> } }).process?.env ?? {};
const port = Number(environment.UI5_TEST_PORT ?? "8080");
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error("UI5_TEST_PORT must be an integer from 1024 to 65535");

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  use: { baseURL: `http://127.0.0.1:${port}`, trace: "retain-on-failure" },
  webServer: {
    command: `ui5 serve --port ${port}`,
    url: `http://127.0.0.1:${port}/index.html`,
    reuseExistingServer: false,
    timeout: 120_000
  }
});
