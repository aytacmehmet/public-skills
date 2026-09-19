import { expect, test } from "@playwright/test";

test("runs discovered OPA5 journeys with zero failures", async ({ page }) => {
  test.setTimeout(120_000);
  const runtimeErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") runtimeErrors.push(message.text());
  });
  page.on("requestfailed", (request) => failedRequests.push(`${request.method()} ${request.url()}: ${request.failure()?.errorText ?? "failed"}`));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (!url.pathname.startsWith("__SERVICE_URI__")) {
      await route.continue();
      return;
    }
    if (url.pathname.endsWith("$metadata")) {
      await route.fulfill({
        contentType: "application/xml",
        headers: { "OData-Version": "4.0" },
        body: `<?xml version="1.0" encoding="utf-8"?>
          <edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
            <edmx:DataServices>
              <Schema Namespace="Mock" xmlns="http://docs.oasis-open.org/odata/ns/edm">
                <EntityType Name="Item"><Key><PropertyRef Name="ID"/></Key><Property Name="ID" Type="Edm.String" Nullable="false"/></EntityType>
                <EntityContainer Name="Container"><EntitySet Name="__ENTITY_SET__" EntityType="Mock.Item"/></EntityContainer>
              </Schema>
            </edmx:DataServices>
          </edmx:Edmx>`
      });
      return;
    }
    if (url.pathname.endsWith("$batch")) {
      const requestBody = route.request().postData() ?? "";
      const requestCount = Math.max(1, [...requestBody.matchAll(/(?:^|\r?\n)GET\s+[^\s]+\s+HTTP\/1\.1/gm)].length);
      const boundary = "batchresponse_ui5_test";
      const responsePart = [
        `--${boundary}`,
        "Content-Type: application/http",
        "Content-Transfer-Encoding: binary",
        "",
        "HTTP/1.1 200 OK",
        "Content-Type: application/json;odata.metadata=minimal",
        "OData-Version: 4.0",
        "",
        JSON.stringify({ "@odata.context": "$metadata#__ENTITY_SET__", "@odata.count": 0, value: [] })
      ].join("\r\n");
      await route.fulfill({
        status: 200,
        headers: { "Content-Type": `multipart/mixed; boundary=${boundary}`, "OData-Version": "4.0" },
        body: `${Array.from({ length: requestCount }, () => responsePart).join("\r\n")}\r\n--${boundary}--\r\n`
      });
      return;
    }
    await route.fulfill({ contentType: "application/json", headers: { "OData-Version": "4.0" }, body: JSON.stringify({ value: [] }) });
  });
  await page.goto("/test/Test.qunit.html?testsuite=test-resources/__APP_PATH__/testsuite.qunit&test=integration/opaTests");
  const result = page.locator("#qunit-testresult");
  await expect(result).toContainText("completed", { timeout: 90_000 });
  const failures = await page.locator("#qunit-tests > li.fail").allTextContents();
  expect(failures, failures.join("\n")).toEqual([]);
  const total = Number(await result.locator(".total").textContent());
  expect(total).toBeGreaterThan(0);
  expect(runtimeErrors, runtimeErrors.join("\n")).toEqual([]);
  expect(failedRequests, failedRequests.join("\n")).toEqual([]);
});
