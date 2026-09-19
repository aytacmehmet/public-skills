---
name: sap-fiori-design
description: "End-to-end SAP Fiori for Web design and development skill based on the official SAP Design System and SAPUI5 guidelines. Use it when asked to design, review, code or refactor an SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototype/PNG, List Report, Object Page, OData/RAP or S/4HANA screen; and also when asked to read an ABAP package from a local ADT/abapGit package, a ZIP or a configured read-only ADT connection and generate the UI according to the CDS/RAP/service contract. Connects visual design, backend evidence and production code through traceable contracts; applies target version, accessibility, performance, security and Clean Core gates."
metadata:
  version: "1.2.0"
  language: "en"
  family: "sap-fiori-design"
  counterpart: "tr/sap-fiori-tasarim"
---

# SAP Fiori Design

Design the screen first in the context of the business task and the target system; then turn the same design into a prototype and production code with real SAPUI5 controls. Derive visual quality from the SAP standard, and technical quality from the target runtime and verifiable quality gates. Talk to the user in their language; default English. The user's instruction takes precedence over this guideline.

<invariants>
1. The single source for design and code is `design-contract.json`. Map every page, field, action, state and responsive behavior in the PNG, the prototype and the production code to this contract; every text key and action ID in the contract must be present in the delivered UI.
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
12. Do not leave template text (`Replace …`, `pending-…`, `YYYY-MM-DD`) in the contract and do not write an invented value to pass the gate. Record what you do not know as `unknown` and what stops progress as `blocked`.

- Bad: the template manifest contains `minUI5Version: 1.151.0` → reporting "The target system is SAPUI5 1.151.0".
- Good: leave `ui5Runtime: unknown`; say "1.151.0 is only the scaffold profile, verify the runtime in the target system".
</invariants>

<references>
Before the work starts, read only the file that is needed:

| Topic | File |
|---|---|
| Visual language, theme, tokens, typography, icons, density, accessibility | [design-foundations.md](references/design-foundations.md) |
| Floorplan, control and state decisions | [floorplans-and-patterns.md](references/floorplans-and-patterns.md) |
| SAPUI5/Fiori elements project and code rules, code generation guardrails | [ui5-engineering.md](references/ui5-engineering.md) |
| Reading an ABAP package/ZIP/ADT snapshot, inspector output, backend → UI mapping | [abap-package-intake.md](references/abap-package-intake.md) |
| RAP, OData V4, ABAP Cloud and Clean Core data contract | [rap-backend-contract.md](references/rap-backend-contract.md) |
| Delivery formats, validator findings, verification matrix | [delivery-and-quality.md](references/delivery-and-quality.md) |
| Official links to be verified live and the version note | [official-sources.md](references/official-sources.md) |

`references/behavior-checks.md` and `references/source-notes.md` are for skill maintenance only; do not read them at runtime.

In the commands, `<skill root>` is the base directory that the host reports for this skill. Run the scripts in the form `python -B "<skill root>/scripts/<name>.py"`; every script lists all of its flags with `--help`. In Git Bash a service URI that starts with `/` is converted into a path; use PowerShell or put `MSYS_NO_PATHCONV=1` in front of the command.

If detail is needed for a specific UI element or floorplan, additionally open the official, target-versioned SAP page. A UI5 Demo Kit sample on its own is not Fiori design evidence.
</references>

<scope>
Fill in the following fields from the chat, the existing files, the service metadata, the screenshots and the requirements; write `unknown` for what is not known, do not invent:

`Role and task` (user role, decision/task, success criterion) · `Business object` (main object, sub-objects, statuses, actions) · `Target system` (S/4HANA Cloud Public/Private, on-premise, BTP or standalone UI5; for FLP the semantic object and action) · `Version and protocol` (SAPUI5 runtime, Fiori guideline version, OData V2/V4, RAP, draft) · `Project` (existing or new; Fiori elements, freestyle or unknown) · `Device and language` (primary devices, language/RTL, theme/branding, accessibility target) · `Output` (`png`, `interactive`, `png+interactive`, `code`, `all` or `review`) · `Limits` (test, deployment, delivery).

Do not ask again for what is already in the context. If there is a single major gap that would change the outcome, ask one short question; otherwise record the assumption in the contract and continue. If the visual format is not stated, assume `png+interactive`.

| Output | Produced | Prerequisite | If the target is `unknown` |
|---|---|---|---|
| `png` / `png+interactive` | `prototype/` + `visuals/*.png` | None; the PNG is a real browser capture | Information note; the gate can open |
| `interactive` | `prototype/` | None | Information note; the gate can open |
| `code` / `all` | `app/` (independent of the prototype) | Framework, reviewed `--ui5-version` profile, observed service URI and entity set | Warning; the gate stays closed |
| `review` | Findings report; no files are produced | An existing project that has been put in scope | — |
</scope>

<evidence>
- **Existing project:** if the user has put it in scope, first read `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller, annotation/CDS sources, tests and the service metadata. If no project was provided, do not inspect an unrelated workspace as if it were the target project. Check the difference between `minUI5Version` and the real runtime.
- **ABAP package** (ADT export, abapGit folder/ZIP or a live package name): first read [abap-package-intake.md](references/abap-package-intake.md), then:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name <package> --service-uri <observed-uri> --protocol odata-v4
```

- **The choice belongs to the evidence, not to the inspector:** if there is more than one service definition, the inspector chooses one only if all of the readable service bindings point to the same definition; otherwise it writes it into `gaps`. Name the UI service with `--service-definition` and the main entity set with `--entity-set`, based on evidence.
- **Live system:** only if read-only ADT tools (for example the `sap-cloud-erp` MCP server) are available and the connection is preconfigured, read all package pages and the required active source pages SHA-bound, create a normalized ADT snapshot and pass it to the same inspector. If there is no tool, ask for a local export and record it as a blocker. Do not guess an object or a service URI from the package name.
- **Transfer into the contract:** carry the field roles under `uiSemantics` (`lineItemFields`, `selectionFields`, `valueHelpFields`, `hiddenFields`, …) and the draft, action, validation, side effect, DCL and service exposure evidence into the design contract. Do not move on to production code before the `gaps` are resolved or an explicit blocker/assumption is written. Verify `unparsedElements` and what is under `dynamicFeatureControl` against the real `$metadata`; do not design the `draftActions` list as business actions; do not send `$search` to an entity that is not in `searchableEntities`. The parser result is not compiler/activation/service preview evidence; the completeness of a local export is the provider's statement (`inventoryVerified: false`).
- **Lock the version:** if the target version is unknown, do not scaffold production code; produce only a prototype or a contract and leave the version as `unknown`. `--ui5-version` only selects the scaffold profile (tooling and `minUI5Version`); the runtime observed in the target system is given separately with `--target-ui5-runtime`. If the profile is newer than the observed runtime or does not have its own lockfile, the scaffold refuses; add a reviewed new profile for that runtime.
- **Live verification:** if there is internet access, open the official documentation via [official-sources.md](references/official-sources.md). Do not say "observed/verified" without actually opening the page in this turn and seeing the version indicator; a static research note is only a search hint. Record the Fiori guideline version and the SAPUI5 runtime version in separate fields, with the full value + URL + check date.

- Bad: the package contains `Z_UI_ORDER` and `Z_API_ORDER`, the binding cannot be read → picking the first one and writing it into the manifest.
- Good: show the `gaps` line, determine the UI service from the source, and run again with `--service-definition Z_UI_ORDER`.
</evidence>

<contract>
Create or extend the workspace:

```powershell
python -B "<skill root>/scripts/scaffold_fiori_workspace.py" <output> --app-id <name.space> --name <name> `
  --language <tr|en> --output <type> [--backend-contract <output>/abap-backend-contract.json] `
  [--semantic-object <object> --action <action>]
```

An existing `design-contract.json` is the designer's work: a later run (for example `--output all` after the prototype) preserves the contract and only adds the missing tree and the fields that belong to the scaffold. `--force` only renews the `prototype/` and `app/` files; starting the contract from scratch requires `--reset-contract`, and the old file is kept as `.bak`. The schemas belong to the skill and are renewed on every run; do not change the type of the template fields for a temporary answer, for a new need update the schema and the validator in the same change.

Fill in all of the following fields:

- `context`: role, task, object, system, version, `launchIntent` for FLP; `context.evidence[].status` is only `verified`, `assumed`, `unknown` or `blocked`
- `architecture`: floorplan, framework, rationale, rejected alternatives; `minUI5Version` for production code
- `informationArchitecture`: pages, sections, navigation, priority
- `fieldsAndActions`: field semantics, mandatory status, value help, action placement and authorization; every `labelKey`/`titleKey` is present in i18n, every action `id` is present in the view with the same stable ID
- `states`: `initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth` and the relevant edit/draft states; `verification.states` carries the same list
- `responsive`: S/M/L/XL behavior, cozy/compact, the phone alternative for the table
- `accessibility`: heading hierarchy, labels, keyboard/focus, ARIA relationships, text alternatives
- `dataContract`: entity, navigation, action/function, `initialSelect`, narrow `$expand`, paging, side effects, `serverCapabilities.search`, `releasedApisVerified`
- `backendEvidence`: ABAP contract path/hash, package, source mode, integrity, active version, open gaps
- `verification`: the commands, and `accessibilityEvidence` that records what was actually tested with `check`/`method`/`result`
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

Evaluate List Report + Object Page for list/filter/drill-down; Analytical List Page for analytical filter-chart-table work; Flexible Column Layout for a real list-detail(-detail) flow. Make the choice not by appearance but according to the task, data volume, editing flow, device and backend capability. The inspector's `recommendation.framework` value is a recommendation; a justified freestyle decision may deviate from it, and the rejected alternative is written into the contract. Details: [floorplans-and-patterns.md](references/floorplans-and-patterns.md), [ui5-engineering.md](references/ui5-engineering.md).
</architecture>

<prototype>
With `--output interactive`, generate the `assets/ui5-prototype/` skeleton into a separate `prototype/` folder, or use the existing application as the prototype. Do not deliver this template as production code. Build a working flow with real SAPUI5 controls, a pinned prototype runtime (CDN; does not work offline), the Horizon theme and mock data selected according to the language.

- Separate the shell from the application content; do not repeat the FLP shell inside the production app.
- Make the critical flows work: filtering, selection, navigation, create/edit/save/cancel, validation, dialogs and messages. Load the dialog as a fragment; show a field error on the field with `valueState` and move the focus to the first field in error.
- Make every designed state reproducible with `?state=loading|empty|no-results|error|no-auth`; the template carries this switch, extend it if you add a new state.
- Use UI5 responsive controls and layouts instead of fixed pixel layout.
- Do not connect to real user data or a production service; use mock data.
- Put control texts into the i18n resource; even in a sample, show locale-aware numbers/dates/units.

**PNG:** open the prototype in a real browser, inspect it once loading has completed, and take a screenshot. Deliver at least the primary target view; sample the S/M/L/XL classes for quality control. The file name has the form `<app>-<screen>-<state>-<S|M|L|XL>-<theme>-<cozy|compact>.png`, and `<state>` is a state ID from the contract. If a PNG and a prototype are requested together, use the same build and the same data state; do not design the two separately by hand.
</prototype>

<production>
In an existing project, follow the local style. In a new scaffold, do not proceed unless the framework, UI5 profile, service protocol/URI and entity set come from user evidence or from a verified `abap-backend-contract.json` file. `--output code` creates a project under `app/` that is independent of the prototype. The new scaffold generates OData V4 only; it reads and preserves an existing OData V2 application but does not imitate it with the V4 template. Use TypeScript in a new freestyle application; do not force an existing JavaScript project into a wholesale migration without justification.

Before writing code, read [ui5-engineering.md](references/ui5-engineering.md) and treat the guardrails in section 11 as errors. Preserve the contract that the templates carry:

- Manifest-first, asynchronous bootstrap, no removed `async` field for a Manifest V2 target; exactly pinned tooling and an up-to-date lockfile.
- Freestyle: a deep-linkable detail route (the key is encoded in the hash, only a key predicate is accepted), `bypassed` → not-found target, stable IDs, i18n, server-side filter/sort/page. `$search` stays only if `serverCapabilities.search: true`; otherwise replace it with `$filter`.
- Fiori elements: solve with annotation/config; `webapp/annotations/annotation.xml` is only for a verified, UI-specific need; put extension code only in a documented extension point.
- FLP: `--semantic-object`/`--action` adds an inbound to the manifest; do not write `verified` without verifying the intent against the target catalog.
- Theme parameters and layout classes; no hard-coded color/font/shadow/radius, no dynamic HTML, no security decisions in the frontend.
- QUnit, OPA5 (including the list → detail and not-found journeys), a zero-test check; wdi5/Playwright end-to-end tests if in scope.

If backend design or UI annotations are required, apply the rules in [rap-backend-contract.md](references/rap-backend-contract.md). Do not call an SAP API/object "released" without verifying its release status in the live system.
</production>

<verification>
First apply the [delivery-and-quality.md](references/delivery-and-quality.md) matrix according to the delivery type, then run the static check:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <output-folder> --contract <output-folder>/design-contract.json
```

The validator uses three severity levels: `error` and `warning` close the gate, `info` does not. `--allow-warnings` is temporary, only while the design is in progress; do not use it at the delivery gate. The gate does not stop at form: template text, a missing state, a text key or action without a counterpart in the UI, empty accessibility evidence, an unverified `$search`/FLP inbound/released status and a version mismatch are findings too. The meaning and the fix of every finding code are in section 10 of [delivery-and-quality.md](references/delivery-and-quality.md); do not silence a finding with an invented value.

In a suitable project, additionally run `npm ci`, typecheck/manifest validation, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant and the browser console. Do not rely on the exit code alone: read the number of discovered tests, and inspect the application and the PNG with your own eyes.

Perform adversarial testing: long translation and RTL · zero records, thousands of records, a delayed service · unauthorized action, backend validation error, concurrency/draft conflict · keyboard-only and visible focus · S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW · the same fields, actions, states and priority across PNG/prototype/code.

If you have patched the same verification error twice, stop patching and re-test the assumption.
</verification>

<review>
If you are asked to review an existing application, do not start the design flow and do not change files:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <project-root> --review
```

`--review` does not require a contract; it scans the manifest, view, controller and style files and fails only on an `error` finding. The script only sees static patterns; on top of it, read the project in the `<evidence>` order and assess floorplan suitability, action placement, states, accessibility, i18n, OData usage and authorization assumptions against the relevant reference. Give every finding in the following form, in order of severity:

`file:line` · `blocker | important | suggestion` · rule and its source (reference section or official page) · observation · proposed change

Do not write runtime, service or screen behavior that you did not see as a finding; collect it under the heading "could not be verified". A fix is made only if the user asks for it, and it follows the project's own style.
</review>

<self_check>
Before saying "done": you re-opened every file · you read the script/build/test output · you saw the application and the PNG · you sampled the first, the last and the strangest scenario · you saw that no template text is left in the contract · you compared the result with the original request. A file that was generated but not opened and inspected is not finished.
</self_check>

<delivery>
Give the result first, then only the evidence required for the decision; no process narration:

1. File links: PNG, interactive prototype, source code, `design-contract.json`
2. Selected floorplan/framework and a one-sentence rationale
3. Target and scaffold UI5 version, Fiori guideline version — each separately
4. Tests that were run and the observed results; the validator's `error`/`warning`/`info` counts
5. Assumptions that could not be verified, open `gaps` and the remaining real risks
6. Requirement → design → code → test traceability

Do not report a file that was not provided, a test that was not run or a runtime value that was not seen as observed evidence. Report the observation, not the intention.
</delivery>

<resources>
`assets/`: the contract template and two schemas, `version-profiles.json` (profiles, `defaultProfile`, the `templateLockfileProfile` that the template lockfile belongs to, a `lockfileDir` per profile), the prototype and two production skeletons. `scripts/`: `inspect_abap_package.py`, `scaffold_fiori_workspace.py`, `validate_fiori_delivery.py`. `tests/test_skill_tools.py`: run it with `python -B "<skill root>/tests/test_skill_tools.py"` whenever a script or template changes. Do not copy the templates blindly; adapt them to the target version and the existing project structure.
</resources>
