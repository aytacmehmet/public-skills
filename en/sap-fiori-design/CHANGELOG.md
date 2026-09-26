# Changelog

## 2.0.0 — 2026-09-27

Major release: the Turkish package now shares the English model-facing instructions, the contract schema is stricter (see 1.3.0 below), and the capture evidence is part of the gate. The development repository retired its private copy in favor of a private plugin; this public package is the maintained standalone edition.

- **State exceptions:** a required state that cannot occur is listed in `stateExceptions` with a reason instead of being dropped; `CONTRACT_STATE_EXCEPTION` and `CONTRACT_STATE_EXCEPTION_CONFLICT` guard the list, and `states` may hold fewer than five entries when the rest are excepted.
- **`$metadata` search support:** `inspect_abap_package.py --metadata <file>` records entity sets and their declared `$search` support (V4 `Capabilities.SearchRestrictions`, V2 `sap:searchable`) in `service.metadata`, with gaps for a protocol mismatch or a missing entity set; the gate reports `SEMANTIC_SEARCH_CONFLICT` when the contract claims search the metadata denies.
- **Review mode:** `cmd:` handlers and `core:require` aliases count as explicit handlers; script comments and `webapp/test`/`webapp/localService` are no longer reported as source findings.
- **Recorded captures:** the new `record_captures.py` writes `visuals/capture-report.json` with each reviewed PNG hash; the gate reports `PNG_REPORT_MISSING` and `PNG_DIGEST`. At S, wait for a key value: responsive tables drop non-key columns.
- Maintenance: FD33–FD36 behavior scenarios; four tool tests. 1.2.0 archived.

### Also included: changes prepared as 1.3.0 and 1.4.0 in the development repository (never published here separately)

#### 1.4.0

- **Model-facing files are English and shared:** the `SKILL.md` body and every file under `references/` are identical in the English and Turkish packages (only the front matter differs); the skill answers in the user's language. Instructions and references were condensed for token efficiency: repeated link blocks removed, rules reduced to one-line imperatives, section numbers and every rule, table, command and validator code kept; about 11% fewer bytes than 1.2.0 despite the added rules and the larger validator table. The repository pair test asserts the equality.

#### 1.3.0

- **Documentation ↔ script consistency:** the scaffold command in the instructions shows the flags that code requires (`--framework`, `--ui5-version`, `--service-uri`, `--entity-set`) plus `--target-ui5-runtime` and `--json`; the template-text vocabulary (`Replace with …`, `replace-with-…`, `pending-…`, `verify-…`, `YYYY-MM-DD`) is the same everywhere and a bare `Replace` is no longer a finding; the README now says that an unknown target closes the gate only for a code delivery; delivery §10 gained a severity column and the codes `CONTRACT_STATE`, `CONTRACT_TARGET_UNKNOWN`, `SEMANTIC_MIN_UI5`, `SEMANTIC_UI5_VERSION`, `CONTRACT_TRACEABILITY_ROW`/`CONTRACT_SOURCES_ROW`, `MANIFEST_V2`, `BACKEND_PARTIAL`; the Fiori elements exemption is stated for `SEMANTIC_ACTION_ID`; the PNG example uses a canonical state name; the multiple-service-definition rule is described in one way in the intake reference.
- **Scaffold:** `--reset-contract` works on its own, takes a `.bak` and keeps the `prototype/`/`app/` trees; both schemas are renewed on every run; `--action` without `--semantic-object` is refused; `--semantic-object` writes `launchContext: flp` into the contract and the template default became `unknown`; when code is added an empty `alternativesRejected` is filled according to the framework decision; the scaffold-profile evidence row no longer piles up; the freestyle contract uses the skeleton's real i18n key (`idColumn`); a contract without `project.outputs` is refused with a clear error.
- **Validator:** `--review` reports the new-project conventions (`MANIFEST_V2`, `MANIFEST_I18N`, `MANIFEST_DENSITY`) as `warning` in an existing project; an incomplete traceability/source row is a warning with its own `_ROW` code; the schema enforces `context.targetSystem`, `responsive.breakpoints`, the `accessibility` booleans, `dataContract.authorization` and the `verification` fields as strictly as the validator.
- **Inspector:** `composition … of` relations are read into `model.associations[]` with a `kind`; `--entity-set` is case-insensitive; with a single service definition a binding that names another definition writes a `gaps` warning; the snapshot `sha256`/`objectName` fields, the 5,000-file cap and the fact that `complete`/`activeSourcesOnly` are declarations for a local export are documented.
- **Templates:** the prototype also reproduces `?state=initial`, unused i18n keys and the nested `_version` fields under Manifest V2 were removed; dead code was removed from the freestyle skeleton and the `empty`/`no-results` texts were separated; the Fiori elements manifest declares `sap.insights` as a lazy dependency and the console filter in the smoke test is justified.
- **References:** corrected that `Go` is the default filter mode of the List Report; stated that an existing project may keep Manifest V1; tied the research date in the design foundations to a single record; the interface description covers the skill's full scope. 1.2.0 archived.

## 1.2.0 — 2026-09-19

- **The delivery gate now checks content:** template text left in the contract (`CONTRACT_PLACEHOLDER`), an undesigned `loading`/`no-results`, a difference between `states` and `verification.states`, a text key missing from i18n, an action ID missing from the views, empty accessibility evidence, empty `initialSelect`/commands in a code delivery, an unverified released status, FLP inbound and `$search` are findings. PNG names are matched against the contract's state IDs. The new `info` severity does not close the gate: an `unknown` target in a prototype-only delivery and a package source whose inventory cannot be verified are notes.
- **Incremental scaffold:** an existing `design-contract.json` is kept; a later run adds only the missing tree and the scaffold-owned fields. `--force` refreshes only the `prototype/` and `app/` files; `--reset-contract` saves the old contract as `.bak`. The inspector's framework recommendation no longer blocks an explicit freestyle decision.
- **Review mode:** `validate_fiori_delivery.py --review` scans an existing project that has no contract; the instructions gained a `<review>` section that defines the finding format.
- **One vocabulary:** evidence status is enforced by the schema as `verified | assumed | unknown | blocked`; the state list (`initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth`) is the same in the instructions, the template, the validator and the references.
- **Inspector:** field → annotation mapping and role lists such as `lineItemFields`, `selectionFields`, `valueHelpFields`, `hiddenFields` (DDLS and DDLX), `@Search.searchable`, custom/abstract entities and classic views, the service binding → service definition link, `inventoryVerified`/`notes`, and ZIP limits for total size and compression ratio.
- **Templates:** the prototype shows every state through `?state=loading|empty|no-results|error|no-auth`, its dialog is a fragment that reports errors through `valueState`, and mock data follows `--language`; the freestyle skeleton has a deep-linkable detail route, a `bypassed` → not-found target and OPA5 journeys that exercise them; the Fiori elements skeleton has a local annotation file; `--semantic-object/--action` adds the FLP inbound to the manifest. The template contract is aligned with the prototype's real i18n keys and control IDs.
- **Fix:** in the freestyle template `npm run typecheck` had failed since 1.0.0 because `playwright.config.ts` needed Node typings; the configuration now compiles without an extra dependency. The empty-path OData V4 property binding is written with `targetType: 'any'` and `mode: 'OneTime'`.
- **Profiles:** the template lockfile belongs to `templateLockfileProfile`; another profile cannot scaffold code without bringing its own `lockfileDir`.
- **Sources:** legacy `experience.sap.com` links carry a version note; the reason for differing link versions is explained.
- Maintenance: FD27–FD32 behavior scenarios; on the repository side `skills.py export` (a renamed copy with an overlay for another host), a weekly link check and a workflow that installs, builds and tests the templates. Both production templates and the prototype were verified in a real environment for this release. 1.1.0 archived.

## 1.1.0 — 2026-09-19

- Instructions moved to the Prompter 2.0.0 structure: imperative mood, XML sections in workflow order (`<invariants>` … `<resources>`), scope slots, reference and output/prerequisite tables, two good/bad examples, a self-check, and a result-first delivery report. Rules and behavior are unchanged.
- References split into two kinds: seven domain references are read at runtime only when needed; the new FD01–FD26 behavior checks and the source and design notes are for maintenance only and are not linked from the instructions.
- The scaffold command appears in the instructions in full (`--language`, `--backend-contract`); the PNG naming pattern moved into the instructions.
- Maintenance: the repository test checks the same section order in both languages, that maintenance references are not linked from the instructions, and the FD scenario numbering. 1.0.0 archived.

## 1.0.0 — 2026-09-19

- First public release, paired with Turkish SAP Fiori Tasarım.
- Contract-led flow: `abap-backend-contract.json` from an ABAP package, `design-contract.json` from that; from the same contract an interactive UI5 prototype, PNG captures taken from the prototype, and a TypeScript freestyle or Fiori elements OData V4 production skeleton.
- Static delivery validator that also fails on warnings: strict JSON, bundled schema, SHA-256 evidence chain, contract ↔ manifest consistency, deprecated and unsafe patterns.
- The service binding protocol is also read from the separate type + version fields of abapGit and ADT exports; XML namespace URLs are no longer cut as if they were comments.
- Behavior definitions are read per entity and per statement: parenthesised `create/update/delete`, create by association, dynamic feature control, functions; draft actions are separated from business actions; `etag` and `total etag` are kept apart.
- The CDS element list handles nested and multi-line annotations, expressions containing commas, and a quoted `//`; an element it cannot classify goes into `unparsedElements` and `gaps` instead of being dropped.
- With several service definitions or entity set candidates it no longer picks the first one; it asks for an explicit choice through `--service-definition` and `--entity-set`.
- The scaffold profile is no longer reported as the target system runtime: `--target-ui5-runtime` is passed separately and stays `unknown` otherwise; the validator checks that `minUI5Version` is not newer than the runtime. The default profile comes from `defaultProfile` in `version-profiles.json`.
- Narrower color and hard-coded text checks: a route hash, an ID selector, an icon URI, and values without letters no longer produce findings.
- Scripts are invoked through a working-directory independent `<skill root>` path and with `python -B`.

Earlier public versions: none.
