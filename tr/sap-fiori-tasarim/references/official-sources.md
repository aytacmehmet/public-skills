# Official SAP source index and currency rule

Use to verify the target version or to find the live page for a control, pattern or API.

## Currency workflow

1. Find the target product and the real SAPUI5 runtime version; the `manifest.json` minimum is not the runtime.
2. Open the versioned SAP Fiori guideline page that matches the target.
3. Confirm the control/API is public and non-deprecated in the target UI5 API Reference.
4. Confirm Fiori elements features/prerequisites in the target-version Help/Demo Kit.
5. Confirm ABAP object/API release status in the target S/4HANA release/ADT.
6. Write source URL, page version and check date into `design-contract.json`.

Research snapshot, 27 August 2026 (not a fixed fact for later work): SAP Fiori for Web portal 1.151 with content consolidated up to 1.148 · skill scaffold profile SAPUI5/types 1.151.0 (never target-runtime evidence) · SAP's experimental Fiori AI skill based on v1.145 (May 2026).

## Main portals

- [SAP Design System](https://www.sap.com/design-system) · [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web) · [SAPUI5 Demo Kit](https://ui5.sap.com/) · [SAP Help Portal](https://help.sap.com/)
- [SAP Fiori AI skill description](https://www.sap.com/design-system/fiori-design-web/v1-145/resources/ai-skills/sap-fiori-guidelines) · [SAP AI Skills Library sources](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines)

## Visual system and accessibility

- [Design Principles](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/design-principles)
- [Guideline Versioning](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/versioning)
- [Fiori for Web UI Kit](https://www.sap.com/design-system/fiori-design-web/v1-148/resources/libraries/sap-fiori-for-web-ui-kit)
- [Design Tokens](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/design-tokens)
- [Theming](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/theming)
- [Typography Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/typography/typography-horizon)
- [Iconography Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/iconography/iconography-horizon)
- [Accessibility in SAP Fiori](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/product-standards/accessibility-in-sap-fiori)
- [Keyboard Support](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/interaction/keyboard-support)
- [UI5 ARIA Labeling](https://ui5.sap.com/#/topic/f38c21c2f71e455e8d4a959522035a1f)

## Floorplans and patterns

- [When to Use Which Floorplan](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/when-to-use-which-floorplan)
- [List Report](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/list-report-floorplan-sap-fiori-element)
- [Object Page Content Area](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/frameworks/sap-fiori-elements/object-page/object-page-content-area-sap-fiori-elements)
- [Dynamic Page](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/dynamic-page-layout/usage)
- [Flexible Column Layout](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/page-layouts/flexible-column-layout/)
- [Table Overview](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/ui-elements/tables/table-overview)
- [Filter Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/filter-bar/)
- [UI Element States](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/ui-element-states)
- [Messaging](https://www.sap.com/design-system/fiori-design-web/v1-120/foundations/best-practices/global-patterns/messaging/messaging)
- [Busy Handling](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/ui-elements/busy-handling)

## UI5 engineering

- [Best Practices for Developers](https://ui5.sap.com/docs/topics/28fcd55b04654977b63dacbee0552712.html)
- [Performance Checklist](https://ui5.sap.com/docs/topics/9c6400eb7dc145b78e94a81e6e390780.html)
- [TypeScript Support](https://ui5.sap.com/docs/topics/a7ee9617bc794b6fad21e4df38e31128.html)
- [Manifest and Manifest-First](https://ui5.sap.com/docs/topics/be0cf40f61184b358b5faedaec98b2da.html)
- [Asynchronous Loading](https://ui5.sap.com/docs/topics/676b636446c94eada183b1218a824717.html)
- [Stable IDs](https://ui5.sap.com/docs/topics/79e910e6a0d949c7acb051b33170bebc.html)
- [Use Only Public APIs](https://ui5.sap.com/docs/topics/b0d5fe2f1b0b497cbd67cd5a1d35fa4c.html)
- [OData V4 Model](https://ui5.sap.com/docs/topics/5de13cf4dd1f4a3480f7e2eaaee3f5b8.html)
- [Fiori Elements for OData V4](https://ui5.sap.com/docs/topics/13ee8ba1b0264ba08dc15a4aee02c91f.html)
- [Fiori Elements V4 Prerequisites](https://ui5.sap.com/docs/topics/f2344b5e78164b2b9c27ef8b068f295c.html)
- [Testing Overview](https://ui5.sap.com/docs/topics/7cdee404cac441888539ed7bfe076e57.html)
- [UI5 CLI](https://ui5.github.io/cli/stable/)
- [UI5 Linter](https://github.com/UI5/linter)

## RAP, ABAP Cloud and Clean Core

- [ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap)
- [Defining Business Service for Fiori UI](https://help.sap.com/docs/abap-cloud/abap-rap/defining-business-service-for-fiori-ui?version=s4hana_cloud)
- [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)
- [Service Binding](https://help.sap.com/docs/abap-cloud/abap-rap/service-binding)
- [Released APIs](https://help.sap.com/docs/ABAP_Cloud/abap-development-tools-user-guide/released-apis)
- [Public Released APIs](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis)
- [Clean Core Extensibility](https://help.sap.com/docs/abap-cloud/developer-guide-from-classic-abap-to-abap-cloud/clean-core-extensibility-and-abap-based-extensions)

## Link versions and source guardrail

Guideline links point at the page versions whose content was checked during research (v1-96 … v1-148); pages do not exist at the same address in every version, so they were not moved to one base version. Before citing a link, open the same page for the target version and record that URL. The repository link check proves reachability only, not currency.

Prefer official SAP/UI5 primary sources · never a search summary in place of the opened page · legacy `experience.sap.com` pages only when no current `sap.com/design-system` equivalent exists, with the version noted · a working sample does not prove Fiori compliance · never generate a module/class/property without public API documentation · make "latest" concrete with a date and a version.
