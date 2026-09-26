# SAPUI5 and Fiori elements engineering guide

Read when deciding project architecture, source code, models/bindings, performance, security and tests.

Sections: 1 version and architecture · 2 reading the project · 3 decision tree · 4 manifest and structure · 5 TypeScript and public API · 6 views and controllers · 7 models, OData, routing · 8 i18n, theming, accessibility · 9 performance and security · 10 test and build gates · 11 code-generation guardrails

## 1. Version and architecture decision

`assets/version-profiles.json` is a reviewed scaffold dependency set, not target-runtime evidence. Find the real system version and `minUI5Version` separately; confirm API availability in the [SAPUI5 Demo Kit](https://ui5.sap.com/) API Reference.

Principle: as much Fiori elements as possible, as much freestyle as necessary ([Modern Development](https://ui5.sap.com/docs/topics/4cb54eb25b7e4df794c05268e83c22b4.html), [Developing Apps with SAP Fiori Elements](https://ui5.sap.com/docs/topics/03265b0408e2432c9571d6b3feb6b1fd.html), [Fiori Elements for OData V4](https://ui5.sap.com/docs/topics/13ee8ba1b0264ba08dc15a4aee02c91f.html)):

- New standard business app → Fiori elements for OData V4.
- Standard structure + small custom need → official extension point/building block.
- Standard structure + custom page → Fiori elements custom page / flexible programming model.
- Unique interaction, non-standard protocol, fully custom UI/performance → freestyle SAPUI5.
- Existing OData V2 app → keep the model or plan a V4 migration; never wrap a V2 service with the V4 model (deprecated).

## 2. Reading the project from evidence

Open before coding: `package.json`, lockfile, scripts · `ui5.yaml` and tooling version · `webapp/manifest.json`, `Component.*`, `index.html` · views, fragments, controllers, models, formatters, custom controls · annotation XML/CDS metadata extensions and service `$metadata` · test folders and CI · ESLint/UI5 Linter/TypeScript config · deploy/FLP, approuter/destination settings.

Determine: UI5 runtime and minimum version · Fiori elements V2/V4 or freestyle · OData V2/V4, draft, transactional/read-only · TypeScript/JavaScript and module format · existing stable-ID, i18n, routing and test style · whether used extension points are public/stable.

Unverified runtime → restrict production code to the safe common feature set and state the assumption.

## 3. Fiori elements / freestyle decision tree

**Fiori elements OData V4** when List Report, Object Page, Analytical List Page or another supported pattern fits · fields, value help, actions, draft and navigation are expressible in metadata/annotations · a RAP/OData V4 UI service exists or can be designed · upgrade resilience and less frontend code matter. Standard floorplans optimize building-block interaction at framework level and carry Design System compliance automatically.

**Custom page / building block** when the standard floorplan covers most needs but a limited custom layout is required · framework messaging, edit flow, draft and metadata advantages must stay · an official Flexible Programming Model building block covers the need.

**Freestyle** when a unique interaction has no standard floorplan/building block · non-OData or multiple data sources need custom orchestration · custom visualization or a device capability is the center of the app.

Justify the decision in `design-contract.json`. "More freedom" or "prettier" is not a justification.

## 4. Manifest-first and project structure

Default freestyle layout ([Basic App Files](https://ui5.sap.com/docs/topics/28b59ca857044a7890a22aec8cf1fee9.html), [Folder Structure](https://ui5.sap.com/docs/topics/003f755d46d34dd1bbce9ffe08c8d46a.html)):

```text
project/
├─ package.json
├─ ui5.yaml
├─ tsconfig.json                  # TypeScript
└─ webapp/
   ├─ manifest.json
   ├─ Component.ts|js
   ├─ view/  controller/  model/  i18n/
   ├─ css/                        # only if needed
   └─ test/{unit,integration,e2e}/
```

Manifest rules ([Manifest and Manifest-First](https://ui5.sap.com/docs/topics/be0cf40f61184b358b5faedaec98b2da.html), [Asynchronous Loading](https://ui5.sap.com/docs/topics/676b636446c94eada183b1218a824717.html), [Model Preload](https://ui5.sap.com/docs/topics/26ba6a5c1e5c417f8b21cce1411dba2c.html)):

- App ID, min UI5, libraries, models, dataSources, root view, routing and density live in `manifest.json`.
- New project targeting UI5 1.136+ → Manifest Version 2; never Manifest V2 for an older runtime. An existing project may keep V1; plan the migration (the validator reports it as `warning` in `--review`).
- Manifest V1: root view and targets async. Manifest V2: do not write the removed `async` fields; async is the default.
- Standalone start via `sap/ui/core/ComponentSupport`; inside FLP use the launchpad lifecycle.
- Libraries under `sap.ui5/dependencies/libs`, models under `sap.ui5/models`, services under `sap.app/dataSources`.
- No deprecated `sap.ui5/resources/js`, no sync component creation, no direct component constructor.
- `Component.ts|js` extends `UIComponent` and implements `sap.ui.core.IAsyncContentCreation` where the version supports it.

## 5. TypeScript, modules and public API

New freestyle → TypeScript; existing JavaScript → no forced bulk migration ([TypeScript Support](https://ui5.sap.com/docs/topics/a7ee9617bc794b6fad21e4df38e31128.html), [TypeScript FAQ](https://ui5.sap.com/docs/topics/8439949bbdc34141bd2b9194f91d42c2.html), [Use Only Public APIs](https://ui5.sap.com/docs/topics/b0d5fe2f1b0b497cbd67cd5a1d35fa4c.html), [Best Practices for Developers](https://ui5.sap.com/docs/topics/28fcd55b04654977b63dacbee0552712.html)):

- `@sapui5/types` for official SAPUI5; runtime, types, UI5 CLI and plugin versions pinned compatibly with the target; typecheck is a CI gate.
- Only APIs documented as public; no deprecated, experimental, protected/private APIs, no private DOM/classes.
- `sap.ui.define` for eager, `sap.ui.require` for lazy dependencies. No global class access such as `sap.m.Button` — use module imports (the documented loader APIs are not covered by this ban). No `sap.ui.getCore()`, no global controller resolution.
- UI5 or native browser APIs instead of jQuery.

## 6. XML view, fragment and controller

[MVC](https://ui5.sap.com/docs/topics/07afcf400eb344c2916e4eb3a400ff7b.html), [Short and Simple Views](https://ui5.sap.com/docs/topics/b0d7db7930f64b9399dc2b4979293873.html), [Stable IDs](https://ui5.sap.com/docs/topics/79e910e6a0d949c7acb051b33170bebc.html): XML views/fragments by default; no HTMLView/JSView/JSONView (deprecated) · short semantic views, repeated/popup parts as fragments loaded with `Controller.loadFragment` · view and controller names match, structures parallel · handlers bound as `.onPress` · modules in XML via `core:require` (`template:require` in templating) · `this.byId()`/view-scoped lookup instead of `sap.ui.getCore().byId()` or `Element.getElementById()` · stable semantic IDs on every control that matters to users and tests · business logic in formatter/helper/service modules, not piled into controllers · no direct DOM manipulation, inline HTML/SVG/CSS or global event handlers.

## 7. Models, OData and routing

Models: remote business data → ODataModel matching the real service version · local UI state → named JSONModel · translatable text → named ResourceModel. Do not copy backend data into a JSONModel; use UI5 types/binding validation and formatting; clean up programmatic models and handlers.

**OData V4** ([OData V4 Model](https://ui5.sap.com/docs/topics/5de13cf4dd1f4a3480f7e2eaaee3f5b8.html), [Data Access](https://ui5.sap.com/docs/topics/9613f1f2d88747cab21896f7216afdac.html), [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html), [Batch Control](https://ui5.sap.com/docs/topics/74142a38e3d4467c8d6a70b28764048f.html)): binding-based access (`bindContext`, `bindList`, `bindProperty`) · Promise-returning `request*` APIs · context at the center of CRUD/bound operations · consider `autoExpandSelect: true` and `$select` explicitly what the controller reads · server-side filter/sort/paging, never the whole entity set · narrow `$select`, controlled `$expand`, growing/paging, batch groups · transactional flows plan `updateGroupId`, `submitBatch`, `resetChanges`, `hasPendingChanges` · CSRF stays with the OData model · metadata on the critical path → evaluate preload/early requests for the target version.

**Routing** ([Routing Configuration](https://ui5.sap.com/docs/topics/902313063d6f45aeaa3388cc4c13c34e.html)): `routes`, `targets` and shared `config` in the manifest · hash-based, deep-linkable routes · required/optional/query parameters as an explicit contract · a not-found/bypassed target · object keys encoded/decoded in the route · targets/lazy loading instead of manual view creation.

## 8. i18n, theming and accessibility

[Localized Texts](https://ui5.sap.com/docs/topics/91f385926f4d1014b6dd926db0e91070.html), [Accessibility Recommendations](https://ui5.sap.com/docs/topics/ee37fc7138b843c0a66700f0aeaba3fe.html), [Labeling and Tooltips](https://ui5.sap.com/docs/topics/329a029f39e249a1bf89e3ffc006c8e1.html), [Theming](https://ui5.sap.com/docs/topics/497c27a8ee26426faacd2b8a1751794a.html): every user-visible label, tooltip, error, empty state, ARIA text and dynamic message in i18n · fallback and supported locales defined · locale-aware dates/numbers/amounts/units via UI5 types/formatters · real `Label`/`labelFor` for inputs, accessible names for icon-only buttons · `ariaLabelledBy`, `ariaDescribedBy`, landmarks, table titles and focus verified · standard control output never modified by hand · theme parameters/CSS custom properties instead of hard-coded values · Horizon may be fixed in a standalone prototype; production apps do not override the user/system theme without reason.

## 9. Performance and security

**Performance** ([Performance Checklist](https://ui5.sap.com/docs/topics/9c6400eb7dc145b78e94a81e6e390780.html)): no sync module/data loading · async bootstrap/component/view/fragment/routing · manifest-first, only needed libraries/modules · Component preload via UI5 CLI · no 404 resource paths · minimal `$select/$expand`, server paging, small payloads · no unnecessary nested controls in large aggregation templates · measure network, bundle and render cost · check Support Assistant and console.

**Security** ([Securing Apps](https://ui5.sap.com/docs/topics/91f3d8706f4d1014b6dd926db0e91070.html), [CSP](https://ui5.sap.com/docs/topics/fe1a6dba940e479fb7c3bc753f92b28c.html)): authentication, authorization and session belong to the backend · client validation is UX, server validation is mandatory · CSP-compliant: no inline scripts/events, `eval`, `javascript:` URLs or sync loader · arbitrary HTML/SVG sanitized or avoided · external URLs allowlisted · no sensitive data in localStorage · OData model CSRF · no third-party library without license, CSP and supply-chain justification.

## 10. Test and build quality gates

Layers ([Testing Overview](https://ui5.sap.com/docs/topics/7cdee404cac441888539ed7bfe076e57.html), [QUnit](https://ui5.sap.com/docs/topics/09d145cd86ee4f8e9d08715f1b364c51.html), [OPA5](https://ui5.sap.com/docs/topics/2696ab50faad458f9b4027ec2f9b884d.html), [UI5 CLI](https://ui5.github.io/cli/stable/), [UI5 Linter](https://github.com/UI5/linter)): QUnit for formatter/helper/controller-domain units (zero discovered tests = failure) · OPA5 for navigation, binding and interaction inside the app, via the UI5 Test Starter · wdi5 for real browser, FLP/auth and end-to-end flows. Stable UI5 ID/property selectors, never CSS/DOM structure; framework synchronization, never fixed sleeps.

Order: 1 install + lockfile · 2 typecheck · 3 UI5 Linter · 4 project lint/format · 5 QUnit · 6 OPA5 · 7 wdi5 if required · 8 UI5 CLI production build · 9 open the build in a real browser/FLP sandbox · 10 Support Assistant, console and network.

## 11. Code generation guardrails

Errors: new API or Manifest V2 without a verified target version · deprecated/experimental/private API · global UI5 class access outside documented loader/bootstrap APIs, `sap.ui.getCore()`, `jQuery.sap.*` · `async: false`, sync XHR, sync factories · inline script/style, `eval`, direct DOM manipulation · hard-coded UI text, colors, locale formats · bulk backend reads or N+1 requests · frontend visibility/disabled state treated as authorization · Fiori elements behavior rewritten in a controller · missing stable ID on a control that matters to tests or users · rendering not inspected although linter/build passed · a QUnit/OPA5/Playwright run discovering zero tests or faking visible rendering with fixed sleeps · unreviewed major dependency changes via `npm audit fix --force` (report production and build-time risk separately).
