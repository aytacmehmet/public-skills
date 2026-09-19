import { readFile } from "node:fs/promises";

const manifest = JSON.parse(await readFile(new URL("../webapp/manifest.json", import.meta.url), "utf8"));
const targets = manifest?.["sap.ui5"]?.routing?.targets ?? {};
const serialized = JSON.stringify(targets);
if (!serialized.includes("sap.fe.templates.ListReport") || !serialized.includes("sap.fe.templates.ObjectPage")) {
  throw new Error("Manifest must define SAP Fiori elements ListReport and ObjectPage targets.");
}
const service = manifest?.["sap.app"]?.dataSources?.mainService;
if (service?.settings?.odataVersion !== "4.0" || !service?.uri?.startsWith("/")) {
  throw new Error("mainService must be an application-relative OData V4 service.");
}
console.log("Manifest contract is valid.");
