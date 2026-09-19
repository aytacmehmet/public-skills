# Changelog

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
