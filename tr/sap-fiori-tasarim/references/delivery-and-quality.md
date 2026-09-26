# Delivery formats and quality gates

Read before producing a PNG, an interactive prototype, code or a combined delivery, and before saying "done".

Sections: 1 delivery model · 2 PNG · 3 interactive · 4 production code · 5 combined traceability · 6 visual matrix · 7 technical matrix · 8 adversarial scenarios · 9 report · 10 validator findings · 11 review

## 1. Common delivery model

- `design-contract.json` first, in every scope; the single source for prototype, PNG, code, tests and the verification report. Chain: requirements → ABAP package / service metadata → `abap-backend-contract.json` → `design-contract.json` → outputs.
- Evidence status (schema-enforced): `verified` observed in this work · `assumed` accepted without evidence · `unknown` not known yet · `blocked` cannot proceed without it. Never lose an unverified target version, service or authorization.
- One state list: `initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth`, plus edit/draft states. `states` equals `verification.states`; PNG names and the `?state=` switch use these IDs. Missing `initial|populated|empty|error|no-auth` → `error`; missing `loading|no-results` → `warning`; the schema requires at least five.
- Incremental workspace: the contract is created once; move from prototype to code with `--output all` in the same folder; never hand-copy the contract or use `--reset-contract` for that.

## 2. PNG contract

A PNG is an implementable screen specification. Mandatory: captured from the running UI5 prototype or a verified real app render · explicit viewport, breakpoint, theme, density and state · realistic readable sample data, nothing sensitive · main task and primary action visible · loading/empty/error/no-auth/mobile variants as required · same build and data state as the prototype.

Name: `<app>-<screen>-<state>-<breakpoint>-<theme>-<density>.png`, e.g. `sales-order-list-populated-L-sap_horizon-compact.png`, `sales-order-object-error-S-sap_horizon-cozy.png`. `<state>` is a contract state ID (anything else → `PNG_NAME`); `<theme>` is the contract theme name (`sap_horizon`, `sap_horizon_dark`, `sap_horizon_hcb`, `sap_horizon_hcw`).

Before capture: fonts/theme/resources loaded · no lingering busy state · no console errors or 404s · title, navigation, actions, status and columns inspected · the longest/strangest sample captured too. Never a generative image for a text-bearing SAP screen; a concept moodboard is not an implementable SAPUI5 specification.

## 3. Interactive prototype contract

Runs the task flow without a production backend. In-scope flows: search/filter/go or live filtering · selection and navigation · create/edit/save/cancel · dialog/popover/value help · validation/message popover · busy → success/error · empty/no-results/no-auth · responsive navigation and mobile adaptation.

Technical: real SAPUI5 controls and layouts · Horizon/default theme, mock JSON/OData · async bootstrap, manifest-first · stable IDs, i18n · no writes to a production service · deterministic `?state=initial|loading|populated|empty|no-results|error|no-auth` (the template ships it; every designed state reproducible and capturable) · dialogs as fragments, required-field errors in `valueState`, focus on the first invalid field · keyboard and visible focus. A "fake shell" is context only; never repeated in production code.

## 4. Production code contract

Runnable completeness for the scope, not snippets.

- Freestyle: `package.json`, lockfile, `ui5.yaml`, TypeScript config · `webapp/manifest.json`, `Component.*` · XML views/fragments, controllers/helpers/models · `i18n.properties` · mock/config for the dev profile only · QUnit/OPA5 (+ wdi5 if needed) · lint/build config.
- Fiori elements: generator structure preserved · manifest target/page config · backend/local annotations, CDS metadata extension if needed · only official extension fragments/controllers/building blocks · draft/action/side-effect and navigation contract · the skeleton ships manifest validation and a Playwright smoke test; add OPA5/wdi5 journeys from the service metadata.
- Existing project: change only what is needed; keep style and dependency layout; no broad migration without request.

## 5. Combined delivery and traceability

| Contract element | PNG | Interactive | Code | Test |
|---|---|---|---|---|
| Page/section | Visible | Navigable | Route/view/page config | OPA5/wdi5 |
| Field | Label/value/state | Editable/display | Binding/annotation | Unit/integration |
| Action | Placement/semantic | Works | Handler/RAP action | Happy + failure |
| Loading | Visible state | Transition | Busy lifecycle | Delayed mock |
| Empty/error/no-auth | Separate state | Reproducible | Message/state logic | Edge case |
| Responsive | S/M/L/XL | Reflow/adapt | Responsive control/config | Viewport test |
| Accessibility | Label/focus appearance | Keyboard | ARIA/stable ID | Manual/tool check |

A contract element missing from any output is a blocker or explicitly out of scope.

## 6. Visual verification matrix

| Size | Viewport | Check |
|---|---:|---|
| S | 390×844 | Single column, mobile table/dialog/navigation |
| M | 768×1024 | Tablet collapse/reflow |
| L | 1280×800 | Desktop main target |
| XL | 1600×1000 | Max width, spacing, multiple columns |

Themes: Morning Horizon, Evening Horizon, High Contrast Black, High Contrast White. Density: cozy, compact. Not every combination needs a PNG: verify the critical screens and report the cells actually checked.

Visual check: page hierarchy and whitespace · single primary action · label/field alignment · table identity and column priority · semantic color + text/icon · focus, selected, hover, disabled/read-only · truncation, overflow, pop-in, scroll · long localization and RTL · empty/error/loading/no-auth.

## 7. Technical verification matrix

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <delivery-root> --contract <delivery-root>/design-contract.json
```

Checks strict JSON, contract/manifest semantics and structural risks; warnings close the gate by default; `--allow-warnings` is a temporary development escape and no substitute for build/test/render.

Version checks: the manifest `minUI5Version` must equal `architecture.minUI5Version` (`SEMANTIC_MIN_UI5`) and must not be newer than `context.targetSystem.ui5Runtime` (`SEMANTIC_UI5_VERSION`). An `unknown` runtime raises `CONTRACT_TARGET_UNKNOWN` as a warning for a code delivery (gate closed) and as `info` for PNG/prototype only. The color check flags only CSS values and quoted color literals; route hashes and ID selectors are not colors.

With an ABAP package in scope the validator also checks the `abap-backend-contract.json` schema, file SHA-256 integrity, active/complete status, inventory hash, service protocol/URI/entity-set consistency and backend → design traceability. A `partial` backend contract is a warning and closes the strict gate.

Also discover and run from the project: install/lockfile · TypeScript typecheck · UI5 Linter and project lint · QUnit · OPA5 · wdi5 (in scope) · UI5 CLI production build · Support Assistant · browser console/network.

| Claim | Evidence |
|---|---|
| JSON/manifest correct | Parse + schema/structure check |
| Code compiles | Typecheck/build output |
| Tests pass | Test report with the test count |
| App opens | Real browser render |
| Visual correct | PNG/screenshot inspected |
| Responsive | S/M/L/XL real viewports |
| Accessible | Keyboard, focus, screen reader/ARIA, high contrast |
| Backend compatible | Metadata, preview/integration, target release |
| Package evidence complete | Inventory count + source hash + backend contract hash + active/truncation check |

Zero discovered tests with exit code 0 is not a pass; a suspiciously clean result means checking test discovery and the target path.

## 8. Adversarial scenarios

Run the relevant ones beyond the happy path: zero, one, thousands of records · long text, very long object IDs, null/missing fields · slow service, timeout, 4xx/5xx, retry · backend validation, warnings, multi-message · unauthorized field/action and whole-page no-auth · draft conflict, stale ETag, concurrent edit, cancel data loss · offline/connection loss (if supported) · RTL, Turkish characters, German-length expansion · keyboard-only, focus return after dialogs, screen reader labels · zoom/text resize and high contrast · Grid/Analytical/Tree Table alternative on a phone.

## 9. Delivery report

1 result and file links · 2 floorplan/framework and rationale · 3 target UI5 / Fiori guideline / backend release · 4 verifications run and observed results · 5 visual-matrix cells actually checked · 6 verified/assumed/blocked topics · 7 the known risk or the single next step needing a user decision.

"Done" requires: files reopened · diff read · script/build/test output read · app/PNG seen · first, last and strangest scenario sampled · result compared with the original request.

## 10. Validator findings

`error` and `warning` close the gate (`--allow-warnings` temporarily opens warnings only), `info` does not. Common codes with the script's default severity; other codes (`SCHEMA_*`, `MANIFEST_*`, `PROJECT_*`, `XML_*`, `BACKEND_*`, pattern checks) explain themselves through `severity` and message in the `--json` output.

| Finding | Severity | Meaning | Fix |
|---|---|---|---|
| `CONTRACT_PLACEHOLDER` | warning | Contract still holds `Replace with …`, `replace-with-…`, `pending-…`, `verify-…` or a bare `YYYY-MM-DD` | Real value; `unknown` if not known, `blocked` if it stops the work |
| `CONTRACT_STATE` | error | `initial`, `populated`, `empty`, `error` or `no-auth` neither designed nor listed in `stateExceptions` | Design the state and align `verification.states`, or record why it does not apply |
| `CONTRACT_STATE_EXCEPTION` / `CONTRACT_STATE_EXCEPTION_CONFLICT` | error | A `stateExceptions` row lacks a required state or a reason / excepts a state that is also designed | One reasoned row per non-applicable required state; never both design and except a state |
| `CONTRACT_STATE_RECOMMENDED` | warning | `loading` or `no-results` not designed | Design the state, align `verification.states` |
| `SEMANTIC_STATES` | warning | `states` and `verification.states` differ | Same IDs in both lists |
| `SEMANTIC_I18N_KEY` | warning | A `*Key` text key (under `informationArchitecture`, `fieldsAndActions`) missing from the first `i18n.properties` of the delivered tree | Add the key or fix the contract (Fiori elements apps take texts from annotations; this check and `SEMANTIC_ACTION_ID` are skipped there) |
| `SEMANTIC_ACTION_ID` | warning | A contract action has no control with that stable ID in any XML view/fragment | Add the action to the UI or drop it from the contract (skipped for Fiori elements) |
| `CONTRACT_A11Y_EVIDENCE` | warning | `verification.accessibilityEvidence` empty or a row lacks `check`/`method`/`result` | Record the check really performed; perform it if missing |
| `CONTRACT_DATA_BUDGET` / `CONTRACT_COMMANDS` | warning | `initialSelect` or `verification.commands` empty for a code delivery | Name the first-render fields and the commands run |
| `CONTRACT_TARGET_UNKNOWN` | warning (code) / info (prototype, PNG) | A `context.targetSystem` field is `unknown`, or `launchIntent` is not an object while `launchContext: flp` | Observe and record the target; keep `unknown` and say so if not known |
| `CONTRACT_TRACEABILITY_ROW` / `CONTRACT_SOURCES_ROW` | warning | A traceability or source row has an empty mandatory field | Complete or remove the row |
| `CONTRACT_RELEASED_UNVERIFIED` | warning | ABAP evidence exists but `releasedApisVerified` not verified | Check in the target system; write `true` or `not-applicable` |
| `SEMANTIC_MIN_UI5` / `SEMANTIC_UI5_VERSION` | error | Manifest `minUI5Version` differs from `architecture.minUI5Version` / is newer than the target runtime (code delivery only) | Fix the profile or the contract; record the observed runtime |
| `SEMANTIC_FLP_INBOUND` | warning | `launchContext: flp` but `app/webapp/manifest.json` has no inbound matching `launchIntent` | Generate with `--semantic-object/--action` or add it; set `launchContext` correctly for a standalone app |
| `SEMANTIC_SEARCH_UNVERIFIED` | warning | `app/` sends `$search` and `serverCapabilities.search` is not `true` | Find `@Search.searchable` or `$metadata` SearchRestrictions evidence, or use `$filter` |
| `SEMANTIC_SEARCH_CONFLICT` | error | `serverCapabilities.search` is `true` but the backend contract's `service.metadata` declares the main entity set not searchable | Use `$filter`, or correct the evidence after checking the target `$metadata` |
| `PNG_NAME` | warning | Capture name off-pattern or names a state the contract does not design | Rename the file |
| `PNG_REPORT_MISSING` / `PNG_DIGEST` | warning / error | Reviewed captures were not recorded / a PNG is unrecorded, changed or missing since `record_captures.py` ran | Review the captures, then run `record_captures.py`; re-review and re-record after any change |
| `MANIFEST_V2` | error (delivery) / warning (`--review`) | `minUI5Version` 1.136+ but manifest `_version` below 2 | Manifest V2 in a new project; plan the migration in an existing one |
| `BACKEND_PARTIAL` | warning | Backend contract `partial`: gaps, truncation or inactive sources | Resolve `gaps` or report as an open risk |
| `BACKEND_INVENTORY_UNVERIFIED` | info | Package source declares no system inventory | State it in the report; gate stays open |

Never silence a finding with an invented value; every `verified` and every accessibility result is an observation.

## 11. Reviewing an existing project

`validate_fiori_delivery.py <project-root> --review` needs no contract (and ignores one), writes no file and fails only on `error`. Contract, package, PNG and `PROJECT_*` checks are off; new-project conventions (`MANIFEST_V2`, `MANIFEST_I18N`, `MANIFEST_DENSITY`) become `warning`. It sees static patterns (deprecated/global APIs, sync loading, inline styles, hard-coded text/colors, stable IDs, manifest structure). For floorplan fit, action placement, state coverage, accessibility and OData usage read the project and write each finding as `file:line · severity · rule and source · observation · proposal`. Unseen runtime behavior is not a finding.
