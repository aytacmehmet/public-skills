# Delivery formats and quality gates

Read this reference when producing a PNG, an interactive design, code or a combined delivery, and before saying “done”.

## Contents

1. Common delivery model
2. PNG contract
3. Interactive design contract
4. Production code contract
5. Combined delivery and traceability
6. Visual verification matrix
7. Technical verification matrix
8. Adversarial scenarios
9. Delivery report

## 1. Common delivery model

In every scope, produce `design-contract.json` first. Let this file be the single source across the following outputs:

```text
requirements
    ↓
ABAP package / service metadata
    ↓
abap-backend-contract.json
    ↓
design-contract.json
    ├─ interactive prototype
    ├─ PNG captures
    ├─ production UI5/Fiori elements code
    └─ tests + verification report
```

In the contract, evidence status is one of exactly four values (enforced by the schema): `verified` observed in this work · `assumed` accepted without evidence · `unknown` not known yet · `blocked` work cannot proceed without it. If the target version, the service or the authorization has not been verified, do not lose this information.

The states to design are one list as well: `initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth`, plus edit/draft states where they apply. `states` and `verification.states` carry the same IDs; PNG names and the prototype's `?state=` switch use these IDs.

The workspace is incremental: `design-contract.json` is created once and later scaffold runs keep it. When moving from the prototype to production code, run `--output all` in the same folder; do not copy the contract by hand and do not use `--reset-contract`.

## 2. PNG contract

A PNG is not merely an aesthetic visual; it is an implementable screen specification.

Mandatory:

- Capture from a running UI5 prototype or a verified real app render
- Clear viewport, breakpoint, theme, density and state
- Readable, realistic sample data; no sensitive/production data
- Showing the main task of the application and the primary action
- Loading, empty, error, no-auth and mobile variants according to the requirement
- PNG and prototype from the same build/data state

Naming:

```text
<app>-<screen>-<state>-<breakpoint>-<theme>-<density>.png
```

Example:

```text
sales-order-list-populated-L-horizon-compact.png
sales-order-object-validation-S-horizon-cozy.png
```

Before capture:

1. Wait for the font/theme/resource loading.
2. Check that the busy state has not remained unintentionally.
3. Check for console errors and 404s.
4. Visually inspect the title, navigation, action, status and table column.
5. Also capture the sample with the strangest/longest text.

Do not use a generative image model for a text-bearing SAP screen. Even if the user only asks for a concept moodboard, make clear that this is not an implementable SAPUI5 specification.

## 3. Interactive design contract

The interactive design must run the task flow without a production backend.

From the mandatory flows, implement those relevant to the scope:

- Search/filter/go or live filtering
- Table/list selection and navigation
- Create/edit/save/cancel
- Dialog/popover/value help
- Validation/message popover
- Busy/loading → success/error
- Empty/no-results/no-auth
- Responsive navigation and mobile adaptation

Technical:

- Real SAPUI5 controls and layouts
- Horizon/default theme and mock JSON/OData data
- Async bootstrap and manifest-first
- Stable IDs and i18n
- No writing to a production service
- Deterministic state display through `?state=loading|empty|no-results|error|no-auth` (the template carries it); every designed state must be reproducible and capturable this way
- The dialog is loaded as a fragment; a required-field error appears in the field's `valueState` and focus moves to the first invalid field
- Keyboard and visible focus

If the prototype contains a “fake shell”, mark it as being for context presentation only. Do not repeat the FLP shell in the production app code.

## 4. Production code contract

A code delivery must not be just a snippet; it must have the runnable completeness that the scope requires.

Typical files for a new freestyle app:

- `package.json`, lockfile, `ui5.yaml`, TypeScript config
- `webapp/manifest.json`, `Component.*`
- XML view/fragment, controller/helper/model
- `i18n.properties`
- Mock/config for the development profile only
- QUnit/OPA5 and, if needed, wdi5
- Lint/build config

For Fiori elements:

- Preserve the generator/project structure
- Manifest target/page config
- Backend/local annotations and, if required, CDS metadata extension
- Only official extension fragments/controllers/building blocks
- Draft/action/side effect and navigation contract
- Test/preview that works with the service metadata

In an existing project, change only the file that is required; preserve the style and dependency arrangement. Do not perform a broad migration unless the user asks for it.

## 5. Combined delivery and traceability

If there is PNG + interactive + code, verify the following correspondence:

| Contract element | PNG | Interactive | Code | Test |
|---|---|---|---|---|
| Page/section | Visible | Navigable | Route/view/page config | OPA5/wdi5 |
| Field | Label/value/state | Editable/display | Binding/annotation | Unit/integration |
| Action | Placement/semantic | Works | Handler/RAP action | Happy + failure |
| Loading | Visible state | Transition | Busy lifecycle | Delayed mock |
| Empty/error/no-auth | Separate state | Reproducible | Message/state logic | Edge case |
| Responsive | S/M/L/XL | Reflow/adapt | Responsive control/config | Viewport test |
| Accessibility | Label/focus appearance | Keyboard | ARIA/stable ID | Manual/tool check |

Mark an element that is in the contract but missing from one of the outputs as a blocker or as explicitly out of scope.

## 6. Visual verification matrix

Test at least the following classes:

| Size | Example viewport | Check |
|---|---:|---|
| S | 390×844 | Single column, mobile table/dialog/navigation |
| M | 768×1024 | Tablet collapse/reflow |
| L | 1280×800 | Desktop main target |
| XL | 1600×1000 | Max width/spacing/multiple columns |

Themes:

- Morning Horizon
- Evening Horizon
- High Contrast Black
- High Contrast White

Density:

- Cozy
- Compact

Delivering a separate PNG for every combination is not mandatory; however, verify the appearance of the critical screens and report which combinations you actually checked.

Visual check:

- Page hierarchy and whitespace
- Uniqueness of the primary action
- Label/field alignment
- Table identity and column priority
- Semantic color + text/icon
- Focus, selected, hover, disabled/read-only
- Truncation, overflow, pop-in and scroll
- Long localization and RTL
- Empty/error/loading/no-auth

## 7. Technical verification matrix

Static check:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <delivery-root> --contract <delivery-root>/design-contract.json
```

This script checks strict JSON, contract/manifest semantics and basic structural risks; warnings close the gate by default. `--allow-warnings` is only a temporary escape hatch during development; it does not replace a real build/test/render.

The version check compares two separate values: the manifest `minUI5Version` must be the same as `architecture.minUI5Version` in the contract (`SEMANTIC_MIN_UI5`) and must not be newer than the target `context.targetSystem.ui5Runtime` value (`SEMANTIC_UI5_VERSION`). If the runtime is `unknown`, `CONTRACT_TARGET_UNKNOWN` is a warning for a code delivery and keeps the gate closed; for a PNG/prototype-only delivery it is `info`, because a prototype may not know its target yet. The color check flags only CSS values and quoted color literals; a route hash or an ID selector is not counted as a color.

If an ABAP package is in scope, the validator additionally checks the `abap-backend-contract.json` schema, the file SHA-256 integrity, the active/complete status, the package inventory hash, the service protocol/URI/entity set consistency and the backend → design traceability. A `partial` backend contract produces a warning and closes the strict delivery gate.

Discover the appropriate commands from the project and run them:

- Dependency install/lockfile
- TypeScript typecheck
- UI5 Linter and project lint
- QUnit
- OPA5
- wdi5 (if in scope)
- UI5 CLI production build
- Support Assistant
- Browser console/network

Evidence layers:

| Claim | Evidence |
|---|---|
| JSON/manifest is correct | Parse + schema/structure check |
| Code compiles | Typecheck/build output |
| Tests pass | Test report; read the test count |
| App opens | Real browser render |
| Visual is correct | Visual inspection of the PNG/screenshot |
| Responsive | S/M/L/XL real viewport |
| Accessible | Keyboard, focus, screen reader/ARIA and high contrast |
| Backend compatible | Metadata, preview/integration and target release |
| Package evidence is complete | Inventory count + source hash + backend contract hash + active/truncation check |

If zero tests are found and the command returns 0, do not count it as a successful test. When the result is too clean, verify the test discovery and the target path.

## 8. Adversarial scenarios

Beyond the happy path, run at least the relevant ones:

- Zero records, one record, thousands of records
- Long text, very long object ID and null/missing field
- Slow service, timeout, 4xx/5xx and retry
- Backend validation, warning and multi-message
- Unauthorized field/action and whole-page no-auth
- Draft conflict, stale ETag, concurrent edit and cancel data loss
- Offline/connection loss (if the product supports it)
- RTL, Turkish characters, German-length expansion
- Keyboard-only, focus return after dialog, screen reader label
- Zoom/text resize and high contrast
- Grid/Analytical/Tree Table alternative on the phone

## 9. Delivery report

Report briefly but with evidence:

1. Result and file links
2. Selected floorplan/framework and rationale
3. Target UI5/Fiori guideline/backend release
4. Verifications that were run and the observed results
5. The cells of the visual matrix that were actually checked
6. Verified/assumed/blocked topics
7. The known risk or the single next step that requires a user decision

To say “done”:

- Reopen the files
- Read the diff
- Read the script/build/test output
- See the app/PNG
- Sample the first, the last and the strangest scenario
- Compare again with the original request

## 10. Validator findings

Severity: `error` and `warning` close the gate (`--allow-warnings` temporarily opens warnings only), `info` does not. The common ones:

| Finding | Meaning | What to do |
|---|---|---|
| `CONTRACT_PLACEHOLDER` | The contract still holds `Replace …`, `pending-…`, `verify-…` or `YYYY-MM-DD` | Write the real value; `unknown` if not known, `blocked` if it stops the work |
| `CONTRACT_STATE_RECOMMENDED` | `loading` or `no-results` is not designed | Design the state and align `verification.states` |
| `SEMANTIC_STATES` | `states` and `verification.states` differ | Bring both lists to the same IDs |
| `SEMANTIC_I18N_KEY` | A `labelKey`/`titleKey` of the contract is missing from the i18n bundle | Add the key or correct the contract (in a Fiori elements app texts come from annotations and are not checked) |
| `SEMANTIC_ACTION_ID` | A contract action has no control with the same stable ID | Add the action to the UI or remove it from the contract if out of scope |
| `CONTRACT_A11Y_EVIDENCE` | `verification.accessibilityEvidence` is empty | Record the check you really performed with `check`/`method`/`result`; perform it if you did not |
| `CONTRACT_DATA_BUDGET` / `CONTRACT_COMMANDS` | `initialSelect` or `verification.commands` is empty for a code delivery | Name the first-render fields and the commands that were run |
| `CONTRACT_RELEASED_UNVERIFIED` | ABAP evidence exists but `releasedApisVerified` was not verified | Check it in the target system; write `true` or `not-applicable` |
| `SEMANTIC_FLP_INBOUND` | `launchContext: flp` but the manifest has no inbound matching `launchIntent` | Generate it with `--semantic-object/--action` or add it to the manifest; correct `launchContext` for a standalone app |
| `SEMANTIC_SEARCH_UNVERIFIED` | The app sends `$search` and `serverCapabilities.search` is not `true` | Find the `@Search.searchable` evidence or use `$filter` |
| `PNG_NAME` | The capture name does not follow the pattern or names a state the contract does not design | Rename the file |
| `BACKEND_INVENTORY_UNVERIFIED` (`info`) | The package source declares no system inventory | State it in the report; it does not close the gate |

Do not silence a finding with an invented value to pass the gate. Every `verified` and every accessibility result you write into the contract must be an observation.

## 11. Reviewing an existing project

`validate_fiori_delivery.py <project-root> --review` needs no contract, produces no files and fails only on an `error` finding. The script sees static patterns (deprecated/global APIs, synchronous loading, inline styles, hard-coded text/colors, stable IDs, manifest structure). For floorplan fit, action placement, state coverage, accessibility and OData usage, read the project and write each finding as `file:line · severity · rule and its source · observation · proposal`. Do not count runtime behavior you have not seen as a finding.
