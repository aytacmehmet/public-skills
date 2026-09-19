import { defineConfig } from "@playwright/test";

const port = Number(process.env.UI5_TEST_PORT ?? "8081");
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error("UI5_TEST_PORT must be an integer from 1024 to 65535");

export default defineConfig({
  testDir: "./tests/integration",
  use: { baseURL: `http://127.0.0.1:${port}`, trace: "retain-on-failure" },
  webServer: {
    command: `ui5 serve --port ${port}`,
    url: `http://127.0.0.1:${port}/index.html`,
    reuseExistingServer: false,
    timeout: 120_000
  }
});
