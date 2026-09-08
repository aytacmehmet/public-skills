# Vault contract — schema 1

Read this when deciding ownership, creating a detailed document, or adopting an existing Vault. This is the project convention supplied by this skill, not an SAP-mandated format.

## Layout

```text
<project>/
  AGENTS.md                         # or the effective root AGENTS.override.md
  obsidian/
    vault.json                      # project key, schema, allowed source Markdown
    Home.md
    Development-Index.md
    Shared-Index.md
    Documentation-Policy.md
    developments/DEV-001-name/
      Overview.md                   # identity, purpose, authority, dependencies
      Current-State.md              # authoritative lifecycle and resume summary
      History.md                    # dated events; preserve earlier entries
      Open-Items.md                 # live questions and preserved resolutions
      Design.md                     # add the following only when needed
      Process.md
      Objects.md
      UI.md
      Verification.md
      Sources.md
      Handover.md
      decisions/ADR-001.md
      source-snapshots.json          # optional file fingerprints, not authority
    shared/SHR-001-name/             # same core/optional page contract
    architecture/                   # entity ARCH, same page contract
    assets/<entity-ID>/              # screenshots and bounded evidence artifacts
    assets/guidance-backups/         # previous root instruction bytes
    templates/                      # English templates; no project evidence
```

Do not create a daily-note hierarchy or one document per tiny edit. Split large History pages by period only when needed; retain the original entries and maintain links from the active History. Before archiving, account for event-ID replay lookup (the helper checks the current History file only). Keep event markers in that file or extend the lookup deliberately; do not silently break replay protection.

## Identity and navigation

Use uppercase stable project/entity IDs such as `ACME-ERP`, `DEV-001`, and `SHR-001`. `ARCH` owns shared architecture. IDs are unique within a Vault, never recycled, and independent of a display title. Slugs use lowercase letters/digits/hyphens. Keep folder names stable whenever possible.

All instantiated notes have unique `id`, `kind`, and ISO `updated` fields. Entity notes also have `entity`. Overview adds `title` and `dependencies` (a list of quoted wikilinks). Current State alone owns entity lifecycle: planned, active, blocked, review, done, archived. An ADR has a separate decision status: proposed, accepted, rejected, superseded. Optional flat properties may include owner, tags, aliases, source_ref, release, and reviewed_at; use consistent types. Do not encode evidence tables as nested YAML.

Every entity page links Home, its Overview, and Current State. Use explicit Vault-root paths for inter-note links and real attachment extensions. Keep links outside code fences when they should be navigable. Table aliases require `\|`. Mermaid-only node links do not replace ordinary relationship links.

## Information ownership

| Information | Owning record | What a consumer stores |
| --- | --- | --- |
| Shared contract or rule | Shared component or Architecture design/ADR | Link, consumed version, local adaptation |
| Development intent and dependency list | Overview | Index contains derived links only |
| Current lifecycle and next work | Current State | Derived index status; a dated handoff can link it |
| Events and past results | History plus original evidence | A brief active summary and precise reference |
| Approved architecture decision | Accepted ADR | Decision ID, current implication, link |
| SAP object | One owning development/shared inventory | Reuse link; do not claim a second owner |
| Source authority | Sources, referencing originals | Claim mapping and review baseline |

`dependencies` means consumer -> provider. `relate --from-id DEV-001 --to-id SHR-001` updates this property; generated consumer lists supply the reverse navigation. Record integration nature, versions, input/output semantics, failure behavior, rationale, and acceptance impact in the consumer's dependency contract details. Other links are navigation unless explicitly recorded as dependencies. A cycle may be legitimate but needs an architectural explanation; the impact query terminates on cycles.

## Development coverage

Use templates as prompts for relevant evidence, not as a requirement to fabricate every section. Each material requirement should reach design/process, owned implementation objects, and verification via stable references. Capture error/alternate flows as well as the normal path. A simple change can be documented within the core pages and a few links; add pages when the content has an independent lifecycle or becomes too long.

Object inventory entries need exact object type/name, package, purpose, ownership/reuse, source location, dependencies, observed state, and evidence/date. Useful groupings are persistence/CDS, RAP behavior and logic, services/integration, UI/navigation, authorization/configuration, and tests/operations. Distinguish planned, local source, observed in tenant, active/published, and tested based on real evidence.

Verification needs actual environment/client/release, baseline, scope, result, time, and evidence. Never hardcode project tenant identities from an unrelated project. Local lint/package checks do not establish activation, authorizations, live OData behavior, business UAT, or go-live approval. Completion criteria belong to the specific development; document any remaining delivery gates even if local coding is complete.

Screenshots must have a real source and English caption; distinguish mockup, local preview, and tenant capture. Store them in the owning asset folder and reference from UI. Preserve the actual capture time and provenance when available; use unknown where unavailable. Do not synthesize an image as evidence of a real screen. Mermaid diagrams should follow the prose and evidence; label proposed designs clearly.

## History and stale knowledge

Record event ID, occurred_at (possibly unknown), recorded_at, change, reason, impact, next action, and evidence. Use a new correction event for errors. Preserve accepted ADR text and approval evidence; record supersession separately with links in both directions. Source hashes are optional retrieval aids for selected original files. They cannot establish online-document freshness, source authority, approval, or correct interpretation.

Read a changed source before updating its fingerprint. Otherwise the warning would be cleared without reviewing documentation drift. Record material divergences as open items until reconciled. Maintain concise accepted constraints and next action in Current State so a new session can resume with minimal reading; include sufficient evidence links to verify that summary.
