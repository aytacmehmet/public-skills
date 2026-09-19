# Changelog

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
