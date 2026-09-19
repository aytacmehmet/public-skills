# SAPUI5 and Fiori elements engineering guide

Read this reference when making decisions about project architecture, source code, model/binding, performance, security and testing.

## Table of contents

1. Version and architecture decision
2. Reading the project from evidence
3. Fiori elements / freestyle decision tree
4. Manifest-first and project structure
5. TypeScript, modules and public API
6. XML view, fragment and controller
7. Model, OData and routing
8. i18n, theming and accessibility
9. Performance and security
10. Test and build quality gates
11. Code generation guardrails

## 1. Version and architecture decision

The `version-profiles.json` file inside the skill is only a reviewed scaffold dependency set; it is not evidence of the target system runtime. First find the actual system version and the `minUI5Version` value separately; verify availability against the API Reference.

Source: [SAPUI5 Demo Kit](https://ui5.sap.com/)

Main principle: as much SAP Fiori elements as possible, as much freestyle SAPUI5 as necessary.

- New standard business application: Fiori elements for OData V4.
- Standard structure + small custom need: official extension point/building block.
- Standard structure + custom page: Fiori elements custom page/flexible programming model.
- Unique interaction, non-standard protocol or a need for fully custom UI/performance: freestyle SAPUI5.
- Existing OData V2 app: keep the existing model or do a planned V4 migration; do not use the approach of wrapping a V2 service with the V4 model (deprecated).

Sources:

- [Modern Development](https://ui5.sap.com/docs/topics/4cb54eb25b7e4df794c05268e83c22b4.html)
- [Developing Apps with SAP Fiori Elements](https://ui5.sap.com/docs/topics/03265b0408e2432c9571d6b3feb6b1fd.html)
- [Fiori Elements for OData V4](https://ui5.sap.com/docs/topics/13ee8ba1b0264ba08dc15a4aee02c91f.html)

## 2. Reading the project from evidence

Before writing code, open the following:

- `package.json`, lockfile and scripts
- `ui5.yaml` and tooling version
- `webapp/manifest.json`, `Component.*`, `index.html`
- Views, fragments, controllers, models, formatters and custom controls
- Annotation XML/CDS metadata extension and the service `$metadata`
- Test folders and CI settings
- ESLint/UI5 Linter/TypeScript config
- Target deploy/FLP setting and approuter/destination information

Determine the following:

- UI5 runtime/minimum version
- Fiori elements V2/V4 or freestyle
- OData V2/V4, draft, transactional/read-only
- TypeScript/JavaScript and module format
- Existing stable ID, i18n, routing and test style
- Whether the extension point in use is public/stable

If the target runtime could not be verified, limit production code to the safe common feature set and state this as an explicit assumption.

## 3. Fiori elements / freestyle decision tree

### Choose Fiori elements OData V4

- If List Report, Object Page, Analytical List Page or a supported standard pattern fits
- If fields, value help, actions, draft and navigation can be defined through metadata/annotations
- If a RAP/OData V4 UI service exists or can be designed
- If upgrade resilience and reducing frontend code are important

A standard floorplan optimizes building block interactions at framework level and carries Design System compliance automatically.

### Choose Fiori elements custom page/building block

- If the standard floorplan covers most needs but a limited custom layout is required
- If you want to keep the advantages of framework messages, edit flow, draft and metadata
- If an official Flexible Programming Model building block covers the need

### Choose freestyle

- If there is a unique interaction that a standard floorplan/building block does not cover
- If non-OData/multiple data sources and custom orchestration are required
- If custom visualization or a device capability is at the center of the application

Justify the decision in `design-contract.json`. "More freedom" or "more beautiful" alone is not a justification for freestyle.

## 4. Manifest-first and project structure

Default freestyle structure:

```text
project/
├─ package.json
├─ ui5.yaml
├─ tsconfig.json                  # if TypeScript
└─ webapp/
   ├─ manifest.json
   ├─ Component.ts|js
   ├─ view/
   ├─ controller/
   ├─ model/
   ├─ i18n/
   ├─ css/                        # only if needed
   └─ test/{unit,integration,e2e}/
```

Sources:

- [Basic App Files](https://ui5.sap.com/docs/topics/28b59ca857044a7890a22aec8cf1fee9.html)
- [Folder Structure](https://ui5.sap.com/docs/topics/003f755d46d34dd1bbce9ffe08c8d46a.html)

Manifest rules:

- Keep the app ID, min UI5, libraries, models, dataSources, root view, routing and density in `manifest.json`.
- If the new project targets UI5 1.136+, use Manifest Version 2; do not generate Manifest V2 for an older runtime.
- In Manifest V1, configure the root view and targets as async. In Manifest V2, do not write the removed `async` fields; asynchronous behavior is the default.
- For standalone startup use `sap/ui/core/ComponentSupport`; inside the FLP use the launchpad lifecycle.
- Define libraries under `sap.ui5/dependencies/libs`, models under `sap.ui5/models` and services under `sap.app/dataSources`.
- Do not use the deprecated `sap.ui5/resources/js`, sync component creation or the component constructor directly.
- Use `UIComponent` in `Component.ts|js`; implement `sap.ui.core.IAsyncContentCreation` in a suitable version.

Sources:

- [Manifest and Manifest-First](https://ui5.sap.com/docs/topics/be0cf40f61184b358b5faedaec98b2da.html)
- [Asynchronous Loading](https://ui5.sap.com/docs/topics/676b636446c94eada183b1218a824717.html)
- [Model Preload](https://ui5.sap.com/docs/topics/26ba6a5c1e5c417f8b21cce1411dba2c.html)

## 5. TypeScript, modules and public API

Prefer TypeScript in a new freestyle project. Do not force an existing JavaScript project into an unnecessary bulk migration.

- Use `@sapui5/types` for official SAPUI5.
- Pin the runtime, types, UI5 CLI and plugin versions so that they are compatible with the target version.
- Make typecheck a CI quality gate.
- Use only APIs that are documented as public in the API Reference.
- Do not use deprecated, experimental, protected/private APIs or private DOM/classes.
- Use `sap.ui.define` for eager dependencies; use `sap.ui.require` for lazy usage.
- Do not access UI5 classes through global names such as `sap.m.Button`; use module imports. Do not confuse the documented `sap.ui.define`/`sap.ui.require` loader APIs with this prohibition. Do not generate `sap.ui.getCore()` or global controller resolution.
- Use UI5 or native browser APIs instead of the jQuery API.

Sources:

- [TypeScript Support](https://ui5.sap.com/docs/topics/a7ee9617bc794b6fad21e4df38e31128.html)
- [TypeScript FAQ](https://ui5.sap.com/docs/topics/8439949bbdc34141bd2b9194f91d42c2.html)
- [Use Only Public APIs](https://ui5.sap.com/docs/topics/b0d5fe2f1b0b497cbd67cd5a1d35fa4c.html)
- [Best Practices for Developers](https://ui5.sap.com/docs/topics/28fcd55b04654977b63dacbee0552712.html)

## 6. XML view, fragment and controller

- Choose XML as the default for views/fragments.
- Do not generate HTMLView, JSView or JSONView; they are deprecated.
- Keep the view short and semantic; turn a repeated/popup part into a fragment.
- Load fragments asynchronously with `Controller.loadFragment`.
- Match the view and controller names; keep the controller structure parallel to the view structure.
- Bind the XML handler to the controller instance in the `.onPress` form.
- In XML, obtain the required module with `core:require`, or with `template:require` in templating.
- Use `this.byId()`/view-scoped lookup instead of `sap.ui.getCore().byId()` or `Element.getElementById()`.
- Give a stable, semantic ID to every control that matters to the user and to tests.
- Do not pile business logic into the controller; separate it into formatter/helper/service modules.
- Do not use direct DOM manipulation, inline HTML/SVG/CSS or global event handlers.

Sources:

- [MVC](https://ui5.sap.com/docs/topics/07afcf400eb344c2916e4eb3a400ff7b.html)
- [Short and Simple Views](https://ui5.sap.com/docs/topics/b0d7db7930f64b9399dc2b4979293873.html)
- [Stable IDs](https://ui5.sap.com/docs/topics/79e910e6a0d949c7acb051b33170bebc.html)

## 7. Model, OData and routing

Model selection:

- Remote business data: an ODataModel that matches the actual service version
- Local UI state: named JSONModel
- Translatable text: named ResourceModel/i18n

Do not copy backend data into a JSONModel unnecessarily. Use UI5 data type/binding validation and formatting. Clean up the lifecycle of programmatic models and event handlers.

### OData V4

- Use binding-based access (`bindContext`, `bindList`, `bindProperty`).
- Use the `request*` APIs that return a Promise.
- Keep the context at the center of CRUD/bound operations.
- Evaluate `autoExpandSelect: true`; explicitly `$select` any field that the controller will read separately.
- Use server-side filter/sort/paging; do not pull the entire entity set to the client.
- Use a narrow `$select`, a controlled `$expand`, growing/paging and batch groups.
- In a transactional flow, plan a separate `updateGroupId`, `submitBatch`, `resetChanges` and `hasPendingChanges`.
- Leave CSRF handling to the OData model; do not write custom token management without justification.
- If metadata is on the critical startup path, evaluate preload/early request in the target version.

Sources:

- [OData V4 Model](https://ui5.sap.com/docs/topics/5de13cf4dd1f4a3480f7e2eaaee3f5b8.html)
- [Data Access](https://ui5.sap.com/docs/topics/9613f1f2d88747cab21896f7216afdac.html)
- [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html)
- [Batch Control](https://ui5.sap.com/docs/topics/74142a38e3d4467c8d6a70b28764048f.html)

### Routing

- Keep `routes`, `targets` and the shared `config` values in the manifest.
- Use hash-based routes that are compatible with deep links/bookmarks.
- Make required/optional/query parameters an explicit contract.
- Provide a not-found/bypassed target.
- Encode/decode the object key when writing it to the route.
- Do not repeat view/component creation by hand; use targets/lazy loading.

Source: [Routing Configuration](https://ui5.sap.com/docs/topics/902313063d6f45aeaa3388cc4c13c34e.html)

## 8. i18n, theming and accessibility

- Put user-visible labels, tooltips, errors, empty states, ARIA texts and dynamic messages into i18n.
- Define the fallback and the supported locales.
- Produce locale-aware dates/numbers/amounts/units with UI5 types/formatters.
- Provide a real `Label`/`labelFor` for inputs; give icon-only buttons an accessible name.
- Verify `ariaLabelledBy`, `ariaDescribedBy`, landmarks, table titles and focus.
- Do not modify standard control output by hand.
- Use theme parameters/CSS custom properties instead of hard-coded colors/dimensions.
- In a standalone prototype Horizon may be selected; in a production app do not unnecessarily override the user/system theme selection.

Sources:

- [Localized Texts](https://ui5.sap.com/docs/topics/91f385926f4d1014b6dd926db0e91070.html)
- [Accessibility Recommendations](https://ui5.sap.com/docs/topics/ee37fc7138b843c0a66700f0aeaba3fe.html)
- [Labeling and Tooltips](https://ui5.sap.com/docs/topics/329a029f39e249a1bf89e3ffc006c8e1.html)
- [Theming](https://ui5.sap.com/docs/topics/497c27a8ee26426faacd2b8a1751794a.html)

## 9. Performance and security

### Performance

- No sync module/data loading.
- Async bootstrap/component/view/fragment/routing.
- Manifest-first and only the required libraries/modules.
- Component preload with the UI5 CLI.
- No 404 resource paths.
- Minimal `$select/$expand`, server paging and small payloads.
- No unnecessary nested controls in the template of a large aggregation.
- Measure the cost of network requests, bundles and rendering.
- Check the UI5 Support Assistant and the console.

Source: [Performance Checklist](https://ui5.sap.com/docs/topics/9c6400eb7dc145b78e94a81e6e390780.html)

### Security

- Treat authentication, authorization and session as backend responsibilities.
- Treat client validation as UX; make server validation mandatory.
- Be CSP compliant: no inline scripts/events, `eval`, `javascript:` URLs or sync loader.
- Sanitize arbitrary HTML/SVG or do not use it.
- Validate external URLs against an allowlist.
- Do not write sensitive data to localStorage.
- Use the CSRF mechanism of the OData model.
- Do not add a third-party library without a license, CSP and supply-chain justification.

Sources:

- [Securing Apps](https://ui5.sap.com/docs/topics/91f3d8706f4d1014b6dd926db0e91070.html)
- [CSP](https://ui5.sap.com/docs/topics/fe1a6dba940e479fb7c3bc753f92b28c.html)

## 10. Test and build quality gates

Test layers:

- QUnit: formatter/helper/controller-domain unit tests; treat the discovery of zero tests as a failure
- OPA5: navigation, binding and user interaction within the same app; prefer the current UI5 Test Starter approach
- wdi5: real browser, FLP/auth and end-to-end system flow

Use stable UI5 ID/property selectors; do not bind to the CSS/DOM structure. Use framework synchronization instead of fixed sleeps.

Recommended order:

1. Dependency install + lockfile
2. TypeScript typecheck
3. UI5 Linter
4. Project lint/format
5. QUnit
6. OPA5
7. wdi5 if required
8. UI5 CLI production build
9. Open the build in a real browser/FLP sandbox
10. Support Assistant, console and network check

Sources:

- [Testing Overview](https://ui5.sap.com/docs/topics/7cdee404cac441888539ed7bfe076e57.html)
- [QUnit](https://ui5.sap.com/docs/topics/09d145cd86ee4f8e9d08715f1b364c51.html)
- [OPA5](https://ui5.sap.com/docs/topics/2696ab50faad458f9b4027ec2f9b884d.html)
- [UI5 CLI](https://ui5.github.io/cli/stable/)
- [UI5 Linter](https://github.com/UI5/linter)

## 11. Code generation guardrails

Treat the following as errors:

- Use of a new API/Manifest v2 without verifying the target version
- Deprecated/experimental/private APIs
- Global UI5 class access outside the documented loader/bootstrap APIs, or use of `sap.ui.getCore()` or `jQuery.sap.*`
- `async: false`, sync XHR or sync factories
- Inline script/style, `eval`, direct DOM manipulation
- Hard-coded UI text, colors and locale formats
- Pulling backend data to the client in bulk, or N+1 requests
- Treating frontend visibility/disabled state as authorization
- Rewriting Fiori elements behavior in the controller
- A missing stable ID on a control that matters to tests and to the user
- Not inspecting the actual rendering of the application even though UI5 Linter/build succeeded
- A QUnit/OPA5/Playwright command discovering zero tests, or imitating visible rendering with a fixed sleep
- An unreviewed major dependency change through `npm audit fix --force`; report production and build-time risks separately
