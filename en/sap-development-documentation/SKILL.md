---
name: sap-development-documentation
description: "Create and maintain English SAP Cloud ERP development documentation and resumable project memory in a project-local Obsidian Vault. Use for Vault setup, documenting development changes, decisions, dependencies, objects, evidence, or resuming work from those records. Does not implement SAP changes or replace authoritative project specifications."
metadata:
  version: "1.0.0"
  language: "en"
  family: "sap-development-documentation"
  counterpart: "tr/sap-gelistirme-dokumantasyonu"
---

# SAP Development Documentation

Keep each development's design and progress traceable in `<project>/obsidian`. Write documentation in English; converse in the user's language. Preserve technical names, source wording when quoted, and approved decisions. The user's instructions take precedence over this skill.

## Enter the right project

Resolve the real project root from the user's request and current checkout. A projectless chat directory is not evidence of a SAP project. Read applicable project instructions and the existing Vault marker/index before writing. If the target is materially ambiguous, ask only for the project root while preparing independent work.

On setup, use `scripts/vault.py --project <root> init --key <stable-project-key> --install-guidance`. First inspect an existing Vault; initialization refuses an unmanaged, nonempty Vault so its content can be mapped and adopted deliberately. See [operations](references/operations.md) for adoption and commands. Never create a second parallel Vault to bypass this condition. Existing authorization for the requested local setup is sufficient; do not add a confirmation loop.

The helper writes documentation inside `obsidian`; the optional guidance step updates the effective root `AGENTS.md` or `AGENTS.override.md`, retaining unrelated text and a backup. Inspect applicable deeper overrides too. Do not change global settings, activate SAP objects, install Obsidian plugins, or migrate unrelated sources as a side effect of documentation work.

## Resume before editing

1. Read the small project entry/index, then run `context --id <id>`. Read the complete Current State if the result says it was truncated. This is a character limit for retrieval, not a token quota.
2. Open the selected Overview and only the relevant design, accepted decisions, open items, and direct dependency contracts. Follow more dependencies when an actual impact requires them. Use `impact --id <id>` to find recorded consumers.
3. Check the source snapshot's changed-file list and any known release/tenant boundary. A matching hash establishes byte equality only, not correctness, completeness, freshness of an online source, or SAP runtime evidence.
4. State the next task from the actual records. If current code, accepted design, and a summary conflict, identify the conflict, use the authoritative evidence, and correct the stale summary with a linked history entry.

Do not read all journals, reread unchanged sources, import entire conversations, or load every skill reference on each turn. Search by stable ID, object name, source path, or decision ID before widening retrieval. The Vault is project memory; it does not authorize writes to Codex's global memories.

## Route documentation

Use `developments/<ID>-<slug>/` for a development, `shared/<ID>-<slug>/` for reusable components, and `architecture/` for project-wide architecture. Four core pages are created: Overview, Current State, History, and Open Items. Add Design, Process, Objects, UI, Verification, Sources, Handover, and individual ADR pages only when useful. The [Vault contract](references/vault-contract.md) defines their responsibilities and SAP evidence fields.

Use English templates in `assets/templates/`. Add pages with the helper rather than inventing paths. Maintain root-relative wikilinks using `/` even on Windows. Use one owning record for each fact; link to shared contracts instead of copying them. Generated indexes, page lists, and consumer lists are derived; update source records and run `reindex`. Keep relationship rationale and the consumed contract version in the consumer Overview.

An existing canonical FS/TS or code artifact remains authoritative unless the user explicitly changes that authority. A Sources page maps references to claims, versions, provenance, and review dates. Recover historical facts only from accessible evidence; distinguish `occurred_at` from `recorded_at`. Missing history is an open question, not permission to invent an event or acceptance.

## Checkpoint meaningful work

At a completed logical change, accepted decision, new blocker, handoff, or interruption boundary:

- Update the affected design, objects, evidence, open items, and dependency consumers as warranted by the change.
- Add a stable event with `checkpoint`; it appends History and refreshes Current State. Replaying the same event is a no-op; a changed payload needs a new correction event. Preserve accepted ADRs; supersede them with a linked new decision when needed.
- Keep Current State compact: purpose, active constraints/decisions, last real verification, blockers, next executable action, and only essential links. Move old detail to History without deleting evidence. Refresh source snapshots only after reviewing the changed source and updating its dependent records.
- Run `reindex` and `check`. Use `check --audit-project` at setup, adoption, or a documentation-location review. Diagnose failures before reporting completion. Tests, activation, UAT, and go-live remain distinct evidence levels.

Documentation of an authorized development change is part of that work; do not wait for a separate documentation request. A skill alone cannot enforce every future session or prevent arbitrary filesystem writes. Project instructions provide the routing agreement; the helper bounds its own writes, and the audit detects unclassified Markdown.

## Validation and boundaries

The helper requires Python 3.12+ and PyYAML 6.x. Use the available runtime; do not install dependencies needlessly. Command syntax, safe updates, evidence handling, and the scoped self-test are in [operations](references/operations.md). Source rationale and checked official links are in [sources](references/sources.md); open them only when the underlying behavior needs refreshing.

Structural checks do not prove English quality, diagram rendering, actual screenshot provenance, semantic consistency, or SAP readiness. Visually inspect relevant diagrams/UI with available tools when that result is part of the task. Describe exactly what was checked. Do not claim measured token savings without a comparable measurement.
