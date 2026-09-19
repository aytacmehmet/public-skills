---
name: sap-fiori-design
description: "End-to-end SAP Fiori for Web design and development skill based on the official SAP Design System and SAPUI5 guidelines. Use it when asked to design, review, code or refactor an SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototype/PNG, List Report, Object Page, OData/RAP or S/4HANA screen; and also when asked to read an ABAP package from a local ADT/abapGit package, a ZIP or a configured read-only ADT connection and generate the UI according to the CDS/RAP/service contract. Connects visual design, backend evidence and production code through traceable contracts; applies target version, accessibility, performance, security and Clean Core gates."
metadata:
  version: "1.0.0"
  language: "en"
  family: "sap-fiori-design"
  counterpart: "tr/sap-fiori-tasarim"
---

# SAP Fiori Design

Design the SAP Fiori for Web screen first in the context of the business task and the target system, then turn the same design into a prototype and production code with real SAPUI5 controls. Derive visual quality from the SAP standard, and technical quality from the target runtime and verifiable quality gates.

## Invariant rules

1. Use `design-contract.json` as the single source for design and code. Map the pages, fields, actions, states and responsive behaviors in the PNG, the interactive prototype and the production code to this contract.
2. Take the PNG from a running UI5 prototype whenever possible. Do not draw a text- and control-heavy SAP screen with a generative image. Use a generative image only for an explicitly requested decorative illustration, and keep it separate from the UI layer.
3. Evaluate the standard floorplan and the SAP Fiori elements OData V4 option first. Choose freestyle SAPUI5 only when a verified requirement exceeds the standard.
4. Do not assume the newest API without verifying the SAPUI5 version and capabilities of the target system. In an existing project, preserve the version, language and structure rules.
5. Make custom CSS, custom controls, controller extensions and frontend business logic the last resort. Use theme tokens, standard controls, annotations and documented extension points.
6. Treat accessibility, responsive/adaptive behavior, i18n, security, error/empty/loading states and the authorization model as part of the design.
7. Do not mistake frontend visibility for authorization. Enforce data and action authorization in the backend.
8. Accept SAP's official AI Fiori skill as a useful baseline, but do not forget that it is experimental and requires human verification. Cross-verify with the target version documentation.
9. Treat only the files that the user provided or explicitly marked as the target project as project evidence. Do not report a `minUI5Version`/manifest value from the skill template, the sample prototype or an unrelated workspace as a target system finding; if there is no evidence, leave the value as `unknown`.
10. If an ABAP package is provided, produce `abap-backend-contract.json` before choosing the UI architecture. Do not confuse information extracted from the CDS/RAP/service source with real `$metadata`, runtime, authorization or released-object verification.
11. Perform live package reading only with preconfigured read-only ADT tools. Do not treat a package read request as permission to write, activate, publish, transport or deploy; do not ask the user for credentials, a private key or RSA in the chat.

## Source routing

Before the work starts, read only the references that are needed:

- For visual language, theme, tokens, typography, icons, density and accessibility: [design-foundations.md](references/design-foundations.md).
- For floorplan, control and state decisions: [floorplans-and-patterns.md](references/floorplans-and-patterns.md).
- For SAPUI5/Fiori elements project and code rules: [ui5-engineering.md](references/ui5-engineering.md).
- For reading an ABAP package/ZIP/ADT snapshot and the backend → UI mapping: [abap-package-intake.md](references/abap-package-intake.md).
- For the RAP, OData V4, ABAP Cloud and Clean Core data contract: [rap-backend-contract.md](references/rap-backend-contract.md).
- For PNG/interactive/code delivery formats and the verification matrix: [delivery-and-quality.md](references/delivery-and-quality.md).
- For the official links to be verified live and the version note: [official-sources.md](references/official-sources.md).

In the commands, `<skill root>` is the base directory that the host reports for this skill; run the scripts independently of the working directory in the form `python -B "<skill root>/scripts/<name>.py"`. `-B` prevents `__pycache__` from being written into the skill folder.

If detail is needed about a specific UI element or floorplan, additionally open the official, target-versioned SAP page. Do not treat a UI5 Demo Kit sample on its own as Fiori design evidence.

## End-to-end workflow

### 1. Scope the request and the output

Extract the following information from the chat, the existing files, the service metadata, the screenshots and the user requirements:

- User role, decision/task and success criterion
- Main business object, sub-objects, statuses and actions
- Target product/system: S/4HANA Cloud Public/Private, on-premise, BTP or standalone UI5
- SAPUI5/Fiori guideline version, OData V2/V4, RAP and draft status
- Existing project or new project; Fiori elements, freestyle or unknown
- Primary devices, language/RTL, theme/branding and accessibility target
- Requested output: `PNG`, `interactive`, `PNG+interactive`, `code` or a combination
- Test, deployment and delivery boundaries

Do not ask again for what is already in the context. If there is a single major gap that would change the outcome, ask one short question; otherwise record the assumption explicitly. If the visual format is not stated, assume `PNG+interactive` and derive the PNG from the prototype.

### 2. Open the evidence, model the ABAP package and lock the target version

If the user has put an existing project in scope, first read that project's `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller files, annotation/CDS sources, tests and service metadata. If the user has not provided a project/files, do not inspect an unrelated workspace as if it were the target project. Check the difference between `minUI5Version` and the real runtime.

If the user has provided an ABAP package, an ADT export, an abapGit folder/ZIP or a live package name, read the [abap-package-intake.md](references/abap-package-intake.md) guide. For a local source:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name <package> --service-uri <observed-uri> --protocol odata-v4
```

If the package contains more than one service definition or more than one candidate entity set, the inspector does not make a choice; it writes this into `gaps`. Name the UI service with `--service-definition` and the main entity set with `--entity-set`, based on evidence.

In a live system, only if read-only ADT tools (for example the `sap-cloud-erp` MCP server) are available and the connection is preconfigured, read all package pages and the required active source pages SHA-bound and create a normalized ADT snapshot; then convert it into the contract with the same inspector. If there is no tool, ask for a local export and record this as a blocker. Do not guess an object or a service URI from the package name.

Transfer the entity, field, association, annotation, draft, action, validation, side effect, DCL and service exposure evidence in `abap-backend-contract.json` into the design contract. Do not move on to production code without resolving the `gaps` list or recording an explicit blocker/assumption. Do not treat the parser result as compiler/activation/service preview evidence. Verify the fields that the inspector could not read (`unparsedElements`) and the runtime-dependent operations under `dynamicFeatureControl` against the real `$metadata`; do not design the `draftActions` list as business actions.

In a new project, if the target version is unknown, do not scaffold production code; produce only a prototype or a contract and leave the version as `unknown`. For a production scaffold, require a reviewed exact profile that is compatible with the target. `--ui5-version` only selects the scaffold profile (tooling and `minUI5Version`); the runtime observed in the target system is given separately with `--target-ui5-runtime` and stays `unknown` in the contract unless it is given. If the profile is newer than the observed runtime, the scaffold refuses; add a reviewed new profile (with its own lockfile) for that runtime. If there is internet access, verify the official documentation live via [official-sources.md](references/official-sources.md). Do not say “observed/verified” without actually opening the live page in this turn and seeing the version indicator; treat the static research snapshot only as a search hint. Record the Fiori guideline version and the SAPUI5 runtime version in separate fields, with the full value + URL + check date, and do not write one in place of the other.

### 3. Create the design contract

Create the workspace with `python -B "<skill root>/scripts/scaffold_fiori_workspace.py" <output> --app-id <name.space> --name <name> --language <tr|en> --output <type>`; this operation produces `design-contract.json` together with the local `design-contract.schema.json` file. Do not change the type of the template fields or the root schema for a temporary answer; if there is a new need, update the schema and the validator in the same change. Keep the verified/assumed/unknown distinction in `context.evidence` and the source version in `sources`. Always define the following:

- `context`: role, task, object, system, version and verified/assumed information
- `architecture`: selected floorplan, framework, rationale, rejected alternatives and, for production code, `minUI5Version`
- `informationArchitecture`: pages, sections, navigation and priority
- `fieldsAndActions`: field semantics, mandatory status, value help, action placement and authorization
- `states`: initial, loading, populated, empty, error, no-auth and the relevant edit/draft states
- `responsive`: S/M/L/XL behavior, cozy/compact and the phone alternative for the table
- `accessibility`: heading hierarchy, labels, keyboard/focus, ARIA relationships and text alternatives
- `dataContract`: entity, navigation, action/function, `$select`, narrow `$expand`, paging and side effects
- `backendEvidence`: ABAP contract path/hash, package, source mode, integrity, active version and open gaps
- `traceability`: requirement → screen/control → ABAP object/file → service/annotation → test mapping

Re-read the design contract before the code. If a visual and a technical decision conflict, resolve the conflict here.

### 4. Make the floorplan and technology decision

Use the following order of priority:

1. Standard SAP Fiori elements OData V4 floorplan
2. Fiori elements + documented building block/extension point
3. Fiori elements custom page/flexible programming model
4. Freestyle SAPUI5
5. Custom control; only if the others do not meet the requirement

Evaluate List Report + Object Page for list/filter/drill-down; Analytical List Page for analytical filter-chart-table work; Flexible Column Layout for a real list-detail(-detail) flow. Make the floorplan choice not only by appearance but according to the task, data volume, editing flow, device and backend capability.

For decision detail, read [floorplans-and-patterns.md](references/floorplans-and-patterns.md) and [ui5-engineering.md](references/ui5-engineering.md).

### 5. Produce the interactive design

With `--output interactive`, generate the `assets/ui5-prototype/` skeleton into a separate `prototype/` folder, or use the existing application as the prototype. Do not deliver this template as production code. Build a working flow with real SAPUI5 controls, a pinned prototype runtime, the Horizon theme and mock JSON/OData data.

- Separate the shell from the application content; do not repeat the FLP shell inside the production app.
- Make the critical flows work: filtering, selection, navigation, create/edit/save/cancel, validation, dialogs and messages.
- Show the relevant empty, dense, error, unauthorized and loading states in an accessible way.
- Use UI5 responsive controls and layouts instead of fixed pixel layout.
- Do not connect to real user data or a production service by default; use mock data.
- Put control texts into the i18n resource; even in a design sample, show locale-aware numbers/dates/units.

### 6. Produce the PNG

If a PNG is requested, open the prototype in a real browser, inspect the visual once loading has completed, and take a screenshot. Deliver at least the primary target view; additionally sample the S/M/L/XL classes for quality control. State the screen, state, breakpoint, theme and density in the file name.

If a PNG and an interactive prototype are requested together, use the same build and the same data state. Do not design the two outputs separately by hand.

### 7. Write the production code

In an existing project, follow the local style. When generating a new code scaffold, do not proceed unless the framework, UI5 version, service protocol/URI and entity set come from user evidence or from a verified `abap-backend-contract.json` file. `--output code` generation creates a project under `app/` that is independent of the prototype. The new scaffold generates OData V4 only; it can read and preserve an existing OData V2 application but does not imitate it with the V4 template. Use TypeScript in a new freestyle application; do not force an existing JavaScript project into a wholesale migration without justification. Apply the following:

- Do not add the removed `async` fields for a Manifest V2 target; use the framework's asynchronous default and asynchronous bootstrap
- Exact-pinned UI5 CLI, UI5 Linter, runtime/types/tooling versions and an up-to-date lockfile
- XML View/Fragment or a suitable typed view; short views, stable IDs and dot-prefixed event handlers to the controller
- Avoiding global names, deprecated/experimental APIs, sync XHR, inline script/style and direct DOM manipulation
- `i18n`, UI5 data types, message handling, busy handling, error catching and lifecycle cleanup
- OData V4 model/binding; server-side filter/sort/page, narrow data selection and controlled batch groups
- In Fiori elements, solving with annotation/config; placing extension code only in a documented extension point
- Standard theme parameters and layout classes; not using hard-coded color/font/shadow/radius
- Not leaking sensitive information, not injecting dynamic HTML and not making security decisions in the frontend
- QUnit unit tests, OPA5 integration flows, a zero-test check and, if in scope, wdi5/Playwright end-to-end tests

If backend design or UI annotations are required, apply the rules in [rap-backend-contract.md](references/rap-backend-contract.md). Do not claim that a usable SAP API/object is “released” without verifying its release status in the live system.

### 8. Verify at each layer

First apply the [delivery-and-quality.md](references/delivery-and-quality.md) matrix according to the delivery type. Then run the static check:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <output-folder> --contract <output-folder>/design-contract.json
```

The validator fails on warnings by default. It checks that the manifest `minUI5Version` value is equal to `architecture.minUI5Version` in the contract and not newer than the target `ui5Runtime` value; if the runtime is `unknown`, a warning keeps the gate closed. A temporary `--allow-warnings` may be used only while the design is in progress; do not use it at the delivery gate. In a suitable project, additionally run `npm ci`, typecheck/manifest validation, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant and the browser console. Do not rely on the exit code alone; inspect the number of discovered tests, the application and the PNG with your own eyes.

Perform adversarial testing:

- Long translation and RTL
- Zero records, thousands of records and a delayed service
- Unauthorized action, backend validation error and concurrency/draft conflict
- Keyboard-only and visible focus
- S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW
- The same fields, actions, states and priority across PNG/prototype/code

If the same verification error is patched twice, re-test the assumption.

### 9. Deliver in a calibrated way

Give the result first. Then present only the evidence required for the decision:

- File links: PNG, interactive prototype, source code and `design-contract.json`
- Selected floorplan/framework and a short rationale
- Target/assumed UI5 and Fiori guideline version
- Tests that were run and the observed results
- Assumptions that could not be verified and the remaining real risks
- Requirement → design → code → test traceability

If a file has been generated but has not been opened and inspected, do not consider it finished. Do not report a file that was not provided, a test that was not run or a runtime value that was not seen as observed evidence.

## Ready-made resources

- `assets/design-contract.template.json` and `assets/design-contract.schema.json`: the contract that connects the visual with the code, and its machine-readable schema.
- `assets/abap-backend-contract.schema.json`: the schema of the package inventory and the RAP/OData/UI evidence.
- `assets/version-profiles.json`: the set of jointly verified, exact-pinned UI5/tooling profiles for a new project, and the `defaultProfile`. The template lockfiles belong to this profile; when adding a new profile, regenerate the lockfile with that profile.
- `assets/ui5-prototype/`: prototype with mock data, for interactive design only.
- `assets/ui5-production-freestyle/`: production skeleton with TypeScript, UI5 CLI/Linter, QUnit, OPA5 and browser quality gates.
- `assets/ui5-production-fiori-elements/`: metadata-first skeleton with OData V4 List Report/Object Page and a browser smoke test.
- `scripts/scaffold_fiori_workspace.py`: creates the prototype and the production project separately and safely, according to the output type.
- `scripts/inspect_abap_package.py`: produces the backend contract from a local package/ZIP or a read-only ADT snapshot.
- `scripts/validate_fiori_delivery.py`: checks strict JSON, contract-code semantics, project structure and risks in a fail-closed manner.
- `tests/test_skill_tools.py`: behavior tests of the three scripts; run them with `python -B "<skill root>/tests/test_skill_tools.py"` whenever a script or template changes.

Do not copy the templates blindly; adapt them to the target version and the existing project structure.
