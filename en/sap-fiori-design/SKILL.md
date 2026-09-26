---
name: sap-fiori-design
description: "End-to-end SAP Fiori for Web design and delivery. Use it to design, review, code or refactor SAP Fiori, SAPUI5/UI5 and Fiori elements screens (List Report, Object Page, mockup/prototype/PNG, OData/RAP, S/4HANA), and to read an ABAP package from a local ADT/abapGit export, a ZIP or a configured read-only ADT connection into a backend contract and generate the UI from it. Links visual design, backend evidence and production code through traceable contracts; applies target-version, accessibility, performance, security and Clean Core gates. Accepts requests in any language and answers in the user's language."
metadata:
  version: "2.0.0"
  language: "en"
  family: "sap-fiori-design"
  counterpart: "tr/sap-fiori-tasarim"
---

# SAP Fiori Design

Design the screen from the business task and the target system, then turn the same design into a prototype and production code built from real SAPUI5 controls. Visual quality comes from the SAP standard, technical quality from the target runtime and verifiable gates. Answer in the user's language; these instructions and the references are English and identical in both language packages. An explicit user instruction overrides this guideline.

<invariants>
1. `design-contract.json` is the single source for PNG, prototype and code; every text key and action ID in it exists in the delivered UI.
2. PNGs are captures of the running UI5 prototype; never draw a text- or control-heavy SAP screen with a generative image (decorative illustrations only, outside the UI layer).
3. Standard floorplan and Fiori elements OData V4 first; freestyle SAPUI5 only when a verified requirement exceeds the standard.
4. Verify the target SAPUI5 version and capabilities before using an API; keep an existing project's version, language and structure rules.
5. Custom CSS, custom controls, controller extensions and frontend business logic are last resorts; prefer theme tokens, standard controls, annotations, documented extension points.
6. Accessibility, responsive/adaptive behavior, i18n, security, loading/empty/error/no-auth states and the authorization model are part of the design.
7. Frontend visibility is not authorization; the backend enforces data and action authorization.
8. SAP's official AI Fiori skill is a useful but experimental baseline; cross-check with the target-version documentation.
9. Only files the user provided or marked as the target project are evidence; a `minUI5Version`/manifest value from the skill template, sample prototype or an unrelated workspace is never a target finding — write `unknown`.
10. With an ABAP package, produce `abap-backend-contract.json` before choosing the architecture; source-derived facts are not `$metadata`, runtime, authorization or released-object verification.
11. Read a live package only through preconfigured read-only ADT tools; reading is not permission to write, activate, publish, transport or deploy; never ask for credentials, private keys or RSA in chat.
12. Leave no template text (`Replace with …`, `replace-with-…`, `pending-…`, `verify-…`, `YYYY-MM-DD`) in the contract and never invent a value to pass the gate: unknown → `unknown`, blocking → `blocked`.

- Bad: template manifest has `minUI5Version: 1.151.0` → "target system is SAPUI5 1.151.0".
- Good: `ui5Runtime: unknown`; "1.151.0 is the scaffold profile; verify the runtime in the target system".
</invariants>

<references>
Read only the file the task needs:

| Topic | File |
|---|---|
| Visual language, themes, tokens, typography, icons, density, accessibility | [design-foundations.md](references/design-foundations.md) |
| Floorplans, controls, states, messaging | [floorplans-and-patterns.md](references/floorplans-and-patterns.md) |
| SAPUI5/Fiori elements project and code rules, code-generation guardrails | [ui5-engineering.md](references/ui5-engineering.md) |
| ABAP package/ZIP/ADT snapshot intake, inspector output, backend → UI mapping | [abap-package-intake.md](references/abap-package-intake.md) |
| RAP, OData V4, ABAP Cloud, Clean Core data contract | [rap-backend-contract.md](references/rap-backend-contract.md) |
| Delivery formats, validator findings, verification matrices | [delivery-and-quality.md](references/delivery-and-quality.md) |
| Official links to verify live, version note | [official-sources.md](references/official-sources.md) |

`references/behavior-checks.md` and `references/source-notes.md` are maintenance-only; do not read them at runtime.

`<skill root>` is the base directory the host reports for this skill; run scripts as `python -B "<skill root>/scripts/<name>.py"` (`--help` lists every flag). Git Bash rewrites a service URI starting with `/` into a path: use PowerShell or prefix `MSYS_NO_PATHCONV=1`. For a specific control or floorplan open the official target-versioned SAP page; a Demo Kit sample alone is not design evidence.
</references>

<scope>
Fill from chat, files in scope, service metadata, screenshots and requirements; write `unknown` instead of inventing: `Role and task` · `Business object` (main/sub-objects, statuses, actions) · `Target system` (S/4HANA Cloud Public/Private, on-premise, BTP or standalone UI5; FLP semantic object and action) · `Version and protocol` (SAPUI5 runtime, Fiori guideline version, OData V2/V4, RAP, draft) · `Project` (existing or new; Fiori elements, freestyle or unknown) · `Device and language` (devices, language/RTL, theme/branding, accessibility target) · `Output` · `Limits` (test, deployment, delivery).

Do not re-ask what the context holds. Ask one short question only for a single gap that changes the outcome; otherwise record the assumption and continue. Default visual format: `png+interactive`.

| Output | Produced | Prerequisite | Target `unknown` |
|---|---|---|---|
| `png` / `png+interactive` | `prototype/` + `visuals/*.png` | None; the PNG is a real browser capture | `info`; gate can open |
| `interactive` | `prototype/` | None | `info`; gate can open |
| `code` | `app/` (independent of the prototype) | Framework, reviewed `--ui5-version` profile, observed service URI and entity set | `warning`; gate closed |
| `all` | `prototype/` + `visuals/` + `app/` | As `code` | `warning`; gate closed |
| `review` | Findings report, no files (`validate_fiori_delivery.py --review`; not a scaffold `--output`) | Existing project in scope | — |
</scope>

<evidence>
- **Existing project:** read `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, views/fragments/controllers, annotation/CDS sources, tests and service metadata first; never inspect an unrelated workspace; distinguish `minUI5Version` from the real runtime.
- **ABAP package** (ADT export, abapGit folder/ZIP, live package name): read [abap-package-intake.md](references/abap-package-intake.md), then:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name <package> --service-uri <observed-uri> --protocol odata-v4 [--metadata <observed-$metadata.xml>]
```

- **Evidence chooses:** with several service definitions the inspector selects one only when every readable service binding names it; otherwise it records a gap. Name the UI service with `--service-definition` and the leading entity set with `--entity-set`, from evidence.
- **Live system:** only with preconfigured read-only ADT tools (for example the `sap-cloud-erp` MCP server): read every package page and the needed active sources SHA-bound, build the normalized snapshot, feed it to the inspector. No tools → ask for a local export, record a blocker. Never guess objects or service URIs from a package name.
- **Into the contract:** carry the `uiSemantics` roles (`lineItemFields`, `selectionFields`, `valueHelpFields`, `hiddenFields`, …), draft, actions, validations, side effects, DCL and service exposure into the design contract. No production code while `gaps` are unresolved without an explicit blocker/assumption. Verify `unparsedElements` and `dynamicFeatureControl` against real `$metadata`; `draftActions` are never business actions; `$search` only for entities in `searchableEntities` or whose `service.metadata` (from `--metadata`) declares search support, never against a metadata `false`. Parser output is not compiler/activation/preview evidence; local-export completeness is the provider's statement (`inventoryVerified: false`).
- **Lock the version:** unknown target version → no production scaffold, only prototype/contract with `unknown`. `--ui5-version` selects the scaffold profile (tooling, `minUI5Version`); the observed runtime goes into `--target-ui5-runtime`. The scaffold refuses a profile newer than the observed runtime or without its own lockfile (the template lockfile belongs to `templateLockfileProfile`; other profiles bring a `lockfileDir`). It still scaffolds without `--target-ui5-runtime`: that rule is yours, and the validator keeps the gate closed with `CONTRACT_TARGET_UNKNOWN`.
- **Live verification:** open the official page via [official-sources.md](references/official-sources.md); say "verified" only after seeing the page and its version indicator in this turn. Record the Fiori guideline version and the SAPUI5 runtime separately: value + URL + check date.

- Bad: package has `Z_UI_ORDER` and `Z_API_ORDER`, binding unreadable → pick the first, write it into the manifest.
- Good: show the gap, determine the UI service from source, rerun with `--service-definition Z_UI_ORDER`.
</evidence>

<contract>
Create or extend the workspace:

```powershell
python -B "<skill root>/scripts/scaffold_fiori_workspace.py" <output> --app-id <name.space> --name <name> `
  --language <tr|en> --output <png|interactive|png+interactive|code|all> `
  [--framework <freestyle-sapui5|fiori-elements-odata-v4> --ui5-version <profile> --service-uri <observed-uri> --entity-set <set>] `
  [--target-ui5-runtime <observed-runtime>] [--backend-contract <output>/abap-backend-contract.json] `
  [--semantic-object <object> --action <action>] [--force] [--reset-contract] [--json]
```

`code`/`all` require the first bracket (`--backend-contract` may supply URI, entity set and protocol); `--action` needs `--semantic-object`. An existing contract is the designer's work: later runs keep it and add only missing trees and scaffold-owned fields; `--force` renews only `prototype/` and `app/`; `--reset-contract` alone restarts the contract, keeps `.bak`, leaves the trees. Schemas belong to the skill and are renewed every run; a new field changes schema and validator together.

Fill every field:

- `context`: role, task, object, system, version, `launchIntent` for FLP; `evidence[].status` ∈ `verified | assumed | unknown | blocked`
- `architecture`: floorplan, framework, rationale, rejected alternatives; `minUI5Version` for code
- `informationArchitecture`: pages, sections, navigation, priority
- `fieldsAndActions`: field semantics, mandatory, value help, action placement and authorization; every `labelKey`/`titleKey` in i18n, every action `id` in the view with the same stable ID
- `states`: `initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth` plus edit/draft states; `verification.states` identical (missing one of the first five = `error`, missing `loading`/`no-results` = `warning`); a required state that cannot occur goes into `stateExceptions` with a reason instead of being dropped
- `responsive`: S/M/L/XL behavior, cozy/compact, phone alternative for tables
- `accessibility`: heading hierarchy, labels, keyboard/focus, ARIA relations, text alternatives
- `dataContract`: entity, navigation, actions/functions, `initialSelect`, narrow `$expand`, paging, side effects, `serverCapabilities.search`, `releasedApisVerified`
- `backendEvidence`: ABAP contract path/hash, package, source mode, completeness, active version, open gaps
- `verification`: commands and `accessibilityEvidence` rows (`check`/`method`/`result`) for what was really tested
- `traceability`: requirement → screen/control → ABAP object/file → service/annotation → test
- `sources`: URL, version, check date

Re-read the contract before coding; resolve visual-versus-technical conflicts here.
</contract>

<architecture>
Priority: 1 standard Fiori elements OData V4 floorplan · 2 Fiori elements + documented building block/extension point · 3 Fiori elements custom page / flexible programming model · 4 freestyle SAPUI5 · 5 custom control, only when nothing else fits.

List Report + Object Page for list/filter/drill-down; Analytical List Page for filter-chart-table analysis; Flexible Column Layout for real list-detail(-detail). Decide by task, data volume, edit flow, device and backend capability, not by looks. The inspector's `recommendation.framework` is a recommendation: a justified freestyle decision may deviate, and the rejected alternative goes into the contract (the scaffold fills an empty `alternativesRejected` from the framework decision; a freestyle reason arrives as template text you replace with the verified requirement). Details: [floorplans-and-patterns.md](references/floorplans-and-patterns.md), [ui5-engineering.md](references/ui5-engineering.md).
</architecture>

<prototype>
`--output interactive` renders `assets/ui5-prototype/` into `prototype/` (or use the existing app as the prototype); never deliver the template as production code. Real SAPUI5 controls, the pinned CDN runtime (unavailable offline), Horizon theme, language-selected mock data.

- Shell separate from app content; the FLP shell is never repeated in the production app.
- Working critical flows: filter, select, navigate, create/edit/save/cancel, validation, dialogs, messages; dialogs as fragments, field errors via `valueState`, focus on the first invalid field.
- Every designed state reproducible via `?state=initial|loading|populated|empty|no-results|error|no-auth`; extend the switch for new states.
- Responsive controls and layouts, no fixed pixels; mock data only; control texts in i18n with locale-aware numbers/dates/units.

**PNG:** open the prototype in a real browser, inspect after loading, capture; at least the primary target view, S/M/L/XL sampled. Name `<app>-<screen>-<state>-<S|M|L|XL>-<theme>-<cozy|compact>.png` with `<state>` a contract state ID. PNG and prototype requested together share one build and data state. Review each capture, then record them with `record_captures.py <output> --ui5-version <prototype runtime>`; the gate reports unrecorded or changed PNGs. At S, responsive tables drop non-key columns: wait for a key value before capturing.
</prototype>

<production>
Existing project: local style. New scaffold: only with framework, UI5 profile, service protocol/URI and entity set from user evidence or a verified `abap-backend-contract.json`; `--output code` creates `app/` independent of the prototype; OData V4 only (an existing V2 app is preserved, never imitated with the V4 template); new freestyle apps in TypeScript, no forced migration of existing JavaScript.

Read [ui5-engineering.md](references/ui5-engineering.md) first; its section 11 guardrails are errors. Keep the template contract:

- Manifest-first, async bootstrap, no removed `async` fields under Manifest V2; exactly pinned tooling and a current lockfile.
- Freestyle: deep-linkable detail route (encoded key predicate only), `bypassed` → not-found target, stable IDs, i18n, server-side filter/sort/page. `$search` stays only with `serverCapabilities.search: true`; the skeleton starts with `$search` and the validator reports `SEMANTIC_SEARCH_UNVERIFIED` until you switch to `$filter` or record `@Search.searchable` evidence.
- Fiori elements: annotations/config first; `webapp/annotations/annotation.xml` only for a verified UI-only need; extension code only in documented extension points.
- FLP: `--semantic-object`/`--action` add a manifest inbound; `verified` only after checking the target catalog.
- Theme parameters and layout classes; no hard-coded color/font/shadow/radius, no dynamic HTML, no security decisions in the frontend.
- Freestyle: QUnit, OPA5 (list → detail and not-found journeys), zero-test check. Fiori elements: the skeleton ships manifest validation and a Playwright smoke test; add OPA5/wdi5 journeys from the service metadata. wdi5/Playwright end-to-end when in scope.

Backend design or UI annotations: [rap-backend-contract.md](references/rap-backend-contract.md). Never call an SAP API/object "released" without verifying it in the live system.
</production>

<verification>
Apply the [delivery-and-quality.md](references/delivery-and-quality.md) matrix, then run:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <output-folder> --contract <output-folder>/design-contract.json
```

`error` and `warning` close the gate, `info` does not; `--allow-warnings` is for work in progress, never the delivery gate. The gate checks content: template text, missing states, text keys or actions absent from the UI, empty accessibility evidence, unverified `$search`/FLP inbound/released status, unrecorded or changed captures and version mismatches are findings. Common codes with severity and fix: delivery-and-quality.md section 10; others explain themselves in `--json` (`severity`, message). Never silence a finding with an invented value.

Where the project allows, also run `npm ci`, typecheck/manifest validation, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, Support Assistant and the browser console. Read discovered test counts, not only exit codes; inspect the app and the PNG yourself.

Adversarial pass: long translations and RTL · zero, one, thousands of records, delayed service · unauthorized action, backend validation error, concurrency/draft conflict · keyboard-only and visible focus · S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW · identical fields, actions, states, priority across PNG/prototype/code. After patching the same error twice, stop and re-test the assumption.
</verification>

<review>
A review request starts no design flow and changes no file:

```powershell
python -B "<skill root>/scripts/validate_fiori_delivery.py" <project-root> --review
```

`--review` needs no contract and ignores one; contract, package and PNG checks are off; new-project conventions (Manifest V2, `supportedLocales`/`fallbackLocale`, `contentDensities`) are `warning`; only `error` fails. Controller-relative, `cmd:` and `core:require` handlers are explicit; comments, `webapp/test` and `webapp/localService` are not reviewed as source. It sees static patterns only: read the project in `<evidence>` order and judge floorplan fit, action placement, states, accessibility, i18n, OData usage and authorization assumptions against the references. Findings, most severe first: `file:line` · `blocker | important | suggestion` · rule and its source (reference section or official page) · observation · proposed change. Unseen runtime, service or screen behavior goes under "could not be verified". Fix only on request, in the project's style.
</review>

<self_check>
Before "done": every file re-opened · script/build/test output read · app and PNG seen · first, last and strangest scenario sampled · no template text left in the contract · result compared with the original request. A generated file nobody opened is not finished.
</self_check>

<delivery>
Result first, then decision-relevant evidence only, no process narration: 1 file links (PNG, prototype, source, `design-contract.json`) · 2 floorplan/framework with a one-sentence rationale · 3 target UI5 runtime, scaffold profile and Fiori guideline version, each separately · 4 tests run and observed results, validator `error`/`warning`/`info` counts · 5 unverified assumptions, open `gaps`, remaining real risks · 6 requirement → design → code → test traceability. Never report an unprovided file, an unrun test or an unseen runtime value as observed.
</delivery>

<resources>
`assets/`: contract template, two schemas, `version-profiles.json` (`profiles`, `defaultProfile`, `templateLockfileProfile`, per-profile `lockfileDir`), the prototype and two production skeletons. `scripts/`: `inspect_abap_package.py`, `scaffold_fiori_workspace.py`, `validate_fiori_delivery.py`, `record_captures.py`. `tests/test_skill_tools.py`: run `python -B "<skill root>/tests/test_skill_tools.py"` after any script or template change. Adapt templates to the target version and the existing structure; never copy them blindly.
</resources>
