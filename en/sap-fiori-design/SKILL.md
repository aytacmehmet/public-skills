---
name: sap-fiori-design
description: "End-to-end SAP Fiori for Web design and development skill based on the official SAP Design System and SAPUI5 guidelines. Use it when asked to design, review, code or refactor an SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototype/PNG, List Report, Object Page, OData/RAP or S/4HANA screen; and also when asked to read an ABAP package from a local ADT/abapGit package, a ZIP or a configured read-only ADT connection and generate the UI according to the CDS/RAP/service contract. Connects visual design, backend evidence and production code through traceable contracts; applies target version, accessibility, performance, security and Clean Core gates."
metadata:
  version: "1.1.0"
  language: "en"
  family: "sap-fiori-design"
  counterpart: "tr/sap-fiori-tasarim"
---

# SAP Fiori Design

Design the screen first in the context of the business task and the target system; then turn the same design into a prototype and production code with real SAPUI5 controls. Derive visual quality from the SAP standard, and technical quality from the target runtime and verifiable quality gates. Talk to the user in their language; default English. The user's instruction takes precedence over this guideline.

<invariants>
1. The single source for design and code is `design-contract.json`. Map every page, field, action, state and responsive behavior in the PNG, the prototype and the production code to this contract.
2. Take the PNG from a running UI5 prototype. Do not draw a text- and control-heavy SAP screen with a generative image; use a generative image only for an explicitly requested decorative illustration and keep it separate from the UI layer.
3. Evaluate the standard floorplan and the SAP Fiori elements OData V4 option first. Choose freestyle SAPUI5 only when a verified requirement exceeds the standard.
4. Do not assume the newest API without verifying the SAPUI5 version and capabilities of the target system. In an existing project, preserve the version, language and structure rules.
5. Custom CSS, custom controls, controller extensions and frontend business logic are the last resort. Use theme tokens, standard controls, annotations and documented extension points.
6. Accessibility, responsive/adaptive behavior, i18n, security, error/empty/loading states and the authorization model are part of the design.
7. Frontend visibility is not authorization. Enforce data and action authorization in the backend.
8. SAP's official AI Fiori skill is a useful baseline, but it is experimental and requires human verification. Cross-verify with the target version documentation.
9. Only the files that the user provided or explicitly marked as the target project are project evidence. Do not report a `minUI5Version`/manifest value from the skill template, the sample prototype or an unrelated workspace as a target system finding; if there is no evidence, leave the value as `unknown`.
10. If an ABAP package is provided, produce `abap-backend-contract.json` before choosing the UI architecture. Do not confuse information extracted from the source with real `$metadata`, runtime, authorization or released-object verification.
11. Read a live package only with preconfigured read-only ADT tools. A read request is not permission to write, activate, publish, transport or deploy; do not ask for credentials, a private key or RSA in the chat.

- Bad: the template manifest contains `minUI5Version: 1.151.0` → reporting "The target system is SAPUI5 1.151.0".
- Good: leave `ui5Runtime: unknown`; say "1.151.0 is only the scaffold profile, verify the runtime in the target system".
</invariants>

<references>
Before the work starts, read only the file that is needed:

| Topic | File |
|---|---|
| Visual language, theme, tokens, typography, icons, density, accessibility | [design-foundations.md](references/design-foundations.md) |
| Floorplan, control and state decisions | [floorplans-and-patterns.md](references/floorplans-and-patterns.md) |
| SAPUI5/Fiori elements project and code rules | [ui5-engineering.md](references/ui5-engineering.md) |
| Reading an ABAP package/ZIP/ADT snapshot, backend → UI mapping | [abap-package-intake.md](references/abap-package-intake.md) |
| RAP, OData V4, ABAP Cloud and Clean Core data contract | [rap-backend-contract.md](references/rap-backend-contract.md) |
| PNG/interactive/code delivery formats and the verification matrix | [delivery-and-quality.md](references/delivery-and-quality.md) |
| Official links to be verified live and the version note | [official-sources.md](references/official-sources.md) |

`references/behavior-checks.md` and `references/source-notes.md` are for skill maintenance only; do not read them at runtime.

In the commands, `<skill root>` is the base directory that the host reports for this skill. Run the scripts independently of the working directory in the form `python -B "<skill root>/scripts/<name>.py"`; `-B` prevents `__pycache__` from being written into the skill folder.

If detail is needed for a specific UI element or floorplan, additionally open the official, target-versioned SAP page. A UI5 Demo Kit sample on its own is not Fiori design evidence.
</references>

<scope>
Fill in the following fields from the chat, the existing files, the service metadata, the screenshots and the requirements; write `unknown` for what is not known, do not invent:

`Role and task` (user role, decision/task, success criterion) · `Business object` (main object, sub-objects, statuses, actions) · `Target system` (S/4HANA Cloud Public/Private, on-premise, BTP or standalone UI5) · `Version and protocol` (SAPUI5 runtime, Fiori guideline version, OData V2/V4, RAP, draft) · `Project` (existing or new; Fiori elements, freestyle or unknown) · `Device and language` (primary devices, language/RTL, theme/branding, accessibility target) · `Output` (`png`, `interactive`, `png+interactive`, `code` or a combination) · `Limits` (test, deployment, delivery).

Do not ask again for what is already in the context. If there is a single major gap that would change the outcome, ask one short question; otherwise record the assumption in the contract and continue. If the visual format is not stated, assume `png+interactive`.

| Output | Produced | Prerequisite |
|---|---|---|
| `png` / `png+interactive` | `prototype/` + `visuals/*.png` | None; the PNG is a real browser capture |
| `interactive` | `prototype/` | None |
| `code` | `app/` (independent of the prototype) | Framework, reviewed `--ui5-version` profile, observed service URI and entity set |
| `all` | All of them | The `code` prerequisites |
</scope>

<evidence>
- **Existing project:** if the user has put it in scope, first read `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller, annotation/CDS sources, tests and the service metadata. If no project was provided, do not inspect an unrelated workspace as if it were the target project. Check the difference between `minUI5Version` and the real runtime.
- **ABAP package** (ADT export, abapGit folder/ZIP or a live package name): first read [abap-package-intake.md](references/abap-package-intake.md), then:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name <package> --service-uri <observed-uri> --protocol odata-v4
```

- **The choice belongs to the evidence, not to the inspector:** if the package contains more than one service definition or candidate entity set, the inspector does not choose; it writes it into `gaps`. Name the UI service with `--service-definition` and the main entity set with `--entity-set`, based on evidence.
- **Live system:** only if read-only ADT tools (for example the `sap-cloud-erp` MCP server) are available and the connection is preconfigured, read all package pages and the required active source pages SHA-bound, create a normalized ADT snapshot and pass it to the same inspector. If there is no tool, ask for a local export and record it as a blocker. Do not guess an object or a service URI from the package name.
- **Transfer into the contract:** carry the entity, field, association, annotation, draft, action, validation, side effect, DCL and service exposure evidence into the design contract. Do not move on to production code before the `gaps` are resolved or an explicit blocker/assumption is written. Verify `unparsedElements` and what is under `dynamicFeatureControl` against the real `$metadata`; do not design the `draftActions` list as business actions. The parser result is not compiler/activation/service preview evidence.
- **Lock the version:** if the target version is unknown, do not scaffold production code; produce only a prototype or a contract and leave the version as `unknown`. `--ui5-version` only selects the scaffold profile (tooling and `minUI5Version`); the runtime observed in the target system is given separately with `--target-ui5-runtime`. If the profile is newer than the observed runtime, the scaffold refuses; add a reviewed new profile (with its own lockfile) for that runtime.
- **Live verification:** if there is internet access, open the official documentation via [official-sources.md](references/official-sources.md). Do not say "observed/verified" without actually opening the page in this turn and seeing the version indicator; a static research note is only a search hint. Record the Fiori guideline version and the SAPUI5 runtime version in separate fields, with the full value + URL + check date.

- Bad: the package contains `Z_UI_ORDER` and `Z_API_ORDER` → picking the first one and writing it into the manifest.
- Good: show the `gaps` line, determine the UI service from the source, and run again with `--service-definition Z_UI_ORDER`.
</evidence>

<contract>
Create the workspace; the operation produces `design-contract.json` together with the local `design-contract.schema.json` file:

```powershell
python -B "<skill root>/scripts/scaffold_fiori_workspace.py" <output> --app-id <name.space> --name <name> `
  --language <tr|en> --output <type> [--backend-contract <output>/abap-backend-contract.json]
```

Do not change the type of the template fields or the root schema for a temporary answer; for a new need, update the schema and the validator in the same change. Fill in all of the following fields:

- `context`: role, task, object, system, version; the verified/assumed/unknown distinction in `context.evidence`
- `architecture`: floorplan, framework, rationale, rejected alternatives; `minUI5Version` for production code
- `informationArchitecture`: pages, sections, navigation, priority
- `fieldsAndActions`: field semantics, mandatory status, value help, action placement and authorization
- `states`: initial, loading, populated, empty, error, no-auth and the relevant edit/draft states
- `responsive`: S/M/L/XL behavior, cozy/compact, the phone alternative for the table
- `accessibility`: heading hierarchy, labels, keyboard/focus, ARIA relationships, text alternatives
- `dataContract`: entity, navigation, action/function, `$select`, narrow `$expand`, paging, side effects
- `backendEvidence`: ABAP contract path/hash, package, source mode, integrity, active version, open gaps
- `traceability`: requirement → screen/control → ABAP object/file → service/annotation → test
- `sources`: URL, version, check date

Re-read the contract before the code. If a visual and a technical decision conflict, resolve the conflict here.
</contract>

<architecture>
Order of priority:

1. Standard SAP Fiori elements OData V4 floorplan
2. Fiori elements + documented building block/extension point
3. Fiori elements custom page/flexible programming model
4. Freestyle SAPUI5
5. Custom control; only if the others do not meet the requirement

Evaluate List Report + Object Page for list/filter/drill-down; Analytical List Page for analytical filter-chart-table work; Flexible Column Layout for a real list-detail(-detail) flow. Make the choice not by appearance but according to the task, data volume, editing flow, device and backend capability. Details: [floorplans-and-patterns.md](references/floorplans-and-patterns.md), [ui5-engineering.md](references/ui5-engineering.md).
</architecture>

<prototype>
With `--output interactive`, generate the `assets/ui5-prototype/` skeleton into a separate `prototype/` folder, or use the existing application as the prototype. Do not deliver this template as production code. Build a working flow with real SAPUI5 controls, a pinned prototype runtime, the Horizon theme and mock JSON/OData data.

- Separate the shell from the application content; do not repeat the FLP shell inside the production app.
- Make the critical flows work: filtering, selection, navigation, create/edit/save/cancel, validation, dialogs and messages.
- Show the empty, dense, error, unauthorized and loading states in an accessible way.
- Use UI5 responsive controls and layouts instead of fixed pixel layout.
- Do not connect to real user data or a production service; use mock data.
- Put control texts into the i18n resource; even in a sample, show locale-aware numbers/dates/units.

**PNG:** open the prototype in a real browser, inspect it once loading has completed, and take a screenshot. Deliver at least the primary target view; sample the S/M/L/XL classes for quality control. File name: `<app>-<screen>-<state>-<breakpoint>-<theme>-<density>.png`. If a PNG and a prototype are requested together, use the same build and the same data state; do not design the two separately by hand.
</prototype>

<production>
In an existing project, follow the local style. In a new scaffold, do not proceed unless the framework, UI5 profile, service protocol/URI and entity set come from user evidence or from a verified `abap-backend-contract.json` file. `--output code` creates a project under `app/` that is independent of the prototype. The new scaffold generates OData V4 only; it reads and preserves an existing OData V2 application but does not imitate it with the V4 template. Use TypeScript in a new freestyle application; do not force an existing JavaScript project into a wholesale migration without justification.

- Do not add the removed `async` fields for a Manifest V2 target; use the framework's asynchronous default and asynchronous bootstrap.
- Pin the UI5 CLI, UI5 Linter and runtime/types/tooling versions exactly; keep the lockfile up to date.
- XML View/Fragment or a suitable typed view; short views, stable IDs, dot-prefixed event handlers to the controller.
- No global names, deprecated/experimental APIs, sync XHR, inline script/style or direct DOM manipulation.
- `i18n`, UI5 data types, message handling, busy handling, error catching and lifecycle cleanup.
- OData V4 model/binding; server-side filter/sort/page, narrow data selection, controlled batch groups.
- In Fiori elements, solve with annotation/config; put extension code only in a documented extension point.
- Standard theme parameters and layout classes; no hard-coded color/font/shadow/radius.
- No leaking of sensitive information, no injecting of dynamic HTML, no security decisions in the frontend.
- QUnit unit tests, OPA5 integration flows, a zero-test check; wdi5/Playwright end-to-end tests if in scope.

If backend design or UI annotations are required, apply the rules in [rap-backend-contract.md](references/rap-backend-contract.md). Do not call an SAP API/object "released" without verifying its release status in the live system.
</production>

<verification>
First apply the [delivery-and-quality.md](references/delivery-and-quality.md) matrix according to the delivery type, then run the static check:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <output-folder> --contract <output-folder>/design-contract.json
```

The validator also fails on warnings; `--allow-warnings` is temporary, only while the design is in progress; do not use it at the delivery gate. The manifest `minUI5Version` value must be equal to `architecture.minUI5Version` in the contract and must not be newer than the target `ui5Runtime` value; if the runtime is `unknown`, a warning keeps the gate closed. In a suitable project, additionally run `npm ci`, typecheck/manifest validation, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant and the browser console. Do not rely on the exit code alone: read the number of discovered tests, and inspect the application and the PNG with your own eyes.

Perform adversarial testing: long translation and RTL · zero records, thousands of records, a delayed service · unauthorized action, backend validation error, concurrency/draft conflict · keyboard-only and visible focus · S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW · the same fields, actions, states and priority across PNG/prototype/code.

If you have patched the same verification error twice, stop patching and re-test the assumption.
</verification>

<self_check>
Before saying "done": you re-opened every file · you read the script/build/test output · you saw the application and the PNG · you sampled the first, the last and the strangest scenario · you compared the result with the original request. A file that was generated but not opened and inspected is not finished.
</self_check>

<delivery>
Give the result first, then only the evidence required for the decision; no process narration:

1. File links: PNG, interactive prototype, source code, `design-contract.json`
2. Selected floorplan/framework and a one-sentence rationale
3. Target and scaffold UI5 version, Fiori guideline version — each separately
4. Tests that were run and the observed results
5. Assumptions that could not be verified, open `gaps` and the remaining real risks
6. Requirement → design → code → test traceability

Do not report a file that was not provided, a test that was not run or a runtime value that was not seen as observed evidence. Report the observation, not the intention.
</delivery>

<resources>
- `assets/design-contract.template.json`, `assets/design-contract.schema.json`: the contract that connects the visual with the code, and its machine-readable schema.
- `assets/abap-backend-contract.schema.json`: the schema of the package inventory and the RAP/OData/UI evidence.
- `assets/version-profiles.json`: jointly verified, exact-pinned UI5/tooling profiles and the `defaultProfile`. The template lockfiles belong to this profile; when adding a new profile, regenerate the lockfile with that profile.
- `assets/ui5-prototype/`: prototype with mock data, for interactive design only.
- `assets/ui5-production-freestyle/`: production skeleton with TypeScript, UI5 CLI/Linter, QUnit, OPA5 and browser quality gates.
- `assets/ui5-production-fiori-elements/`: metadata-first skeleton with OData V4 List Report/Object Page and a browser smoke test.
- `scripts/scaffold_fiori_workspace.py`: creates the prototype and the production project separately and without overwriting, according to the output type.
- `scripts/inspect_abap_package.py`: produces the backend contract from a local package/ZIP or a read-only ADT snapshot.
- `scripts/validate_fiori_delivery.py`: checks strict JSON, contract-code semantics, project structure and risks in a fail-closed manner.
- `tests/test_skill_tools.py`: behavior tests of the three scripts; run them with `python -B "<skill root>/tests/test_skill_tools.py"` whenever a script or template changes.

Do not copy the templates blindly; adapt them to the target version and the existing project structure.
</resources>
