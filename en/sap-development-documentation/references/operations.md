# Operations

Read this for setup, helper execution, safe adoption, or a concrete validation issue. Commands assume the skill root as the working directory; otherwise use the script's actual absolute path. The `--project` parameter is always the selected real project directory.

## Runtime and setup

Python 3.12+ and PyYAML 6.x are required. `scripts/requirements.txt` describes the only third-party dependency. Prefer an existing runtime with PyYAML. Run new/changed helpers in an isolated workspace first.

```powershell
python -X utf8 -B scripts/vault.py --project '<project-root>' --dry-run init --key ACME-ERP --install-guidance
python -X utf8 -B scripts/vault.py --project '<project-root>' init --key ACME-ERP --install-guidance
```

The second command creates the Vault and merges a marked documentation section into the effective root instruction file. If both root instruction files exist, AGENTS.override.md is used. Existing bytes are backed up under the Vault before a change. Nothing changes global instructions or Obsidian registration/settings. Inspect deeper applicable instruction overrides and resolve actual conflicts as part of the project setup.

Open `<project-root>/obsidian` as a Vault using Obsidian's existing-folder flow. Optionally set its attachment location to `assets`, new-note location to an appropriate registered folder, and enable the core Backlinks panel. These UI settings do not enforce Codex filesystem writes. The generated Vault needs no community plugin, Dataview, external database, or background service.

## Add and elaborate

```powershell
python -X utf8 -B scripts/vault.py --project '<project-root>' add --kind development --id DEV-001 --slug purchase-extension --title 'Purchase Extension'
python -X utf8 -B scripts/vault.py --project '<project-root>' add --kind shared --id SHR-001 --slug validation-service --title 'Validation Service'
python -X utf8 -B scripts/vault.py --project '<project-root>' page --id DEV-001 --template design
python -X utf8 -B scripts/vault.py --project '<project-root>' page --id DEV-001 --template decision --record-id ADR-001 --title 'Validation contract ownership'
python -X utf8 -B scripts/vault.py --project '<project-root>' relate --from-id DEV-001 --to-id SHR-001
```

Available optional templates: design, process, objects, ui, verification, sources, handover, decision. The same modes work for `ARCH`. Then author the meaningful content in the returned fixed paths. Existing pages are retained. Review the diff; preserve frontmatter, navigation, and managed markers. Run reindex after adding, renaming, or manually changing dependencies. Explain each dependency's contract and reason in its owning Overview.

The helper intentionally has no generic arbitrary-output-path option or destructive migration command. When writing content manually, resolve the full destination under the confirmed Vault first. Keep asset filenames safe and within the entity folder. Do not follow symlinks/junctions for writes. Do not put scratch reports into a second documentation tree.

## Record progress and resume

```powershell
python -X utf8 -B scripts/vault.py --project '<project-root>' checkpoint --id DEV-001 --event-id EVT-20260908-001 --status active --summary 'Documented the proposed validation contract; approval remains pending.' --next 'Review the contract with its owner.' --evidence 'See the proposed ADR and source references.'
python -X utf8 -B scripts/vault.py --project '<project-root>' context --id DEV-001
python -X utf8 -B scripts/vault.py --project '<project-root>' impact --id SHR-001
```

Add `--occurred-at` only with a supported ISO date/time from evidence. Without it, the event's occurrence is unknown; the recording timestamp is real UTC. Reusing an event ID with identical arguments is a no-op; differing arguments require a new correction ID. Supply reason, effect, and links in the summary/evidence when relevant. For long/multiline prose, prefer a local UTF-8 file and a direct file edit preserving the contract rather than complicated shell quoting. Do not interpolate untrusted shell text.

Checkpoint updates only the Current State checkpoint block and lifecycle plus appending History. It does not infer accepted decisions, close open items, verify evidence, or synchronize all semantic prose. The agent must update those affected sections as part of the same logical change. A done lifecycle does not imply tenant readiness; the exact acceptance scope and remaining gates must be stated.

Context returns the selected Current State, dependency IDs, source drift for the selected entity and its direct dependencies, and links. Its default body limit is 5,500 characters; it reports truncation explicitly. Read omitted material when flagged. This is a bounded retrieval aid, not exact token accounting. Impact follows recorded consumers transitively and stops at visited nodes.

## Fingerprints

```powershell
python -X utf8 -B scripts/vault.py --project '<project-root>' source --id DEV-001 --source 'src/contract.json' --source 'specs/approved-requirement.pdf'
```

Only run this after reviewing the selected original files. It writes `source-snapshots.json` beside the entity notes with observed hashes/times. Context/check compares actual files to that baseline and warns on change or disappearance. Describe the semantic role, original URI/path, actual review time, authority and supported claims on Sources. Use normal source references for external URLs or unavailable tenant evidence. A byte fingerprint is not a review receipt.

## Check and recover

```powershell
python -X utf8 -B scripts/vault.py --project '<project-root>' reindex
python -X utf8 -B scripts/vault.py --project '<project-root>' check
python -X utf8 -B scripts/vault.py --project '<project-root>' check --audit-project
python -X utf8 -B scripts/test_vault.py
```

`check` reads Markdown mechanically without loading the full Vault into model context. It checks managed notes, basic properties, core pages, IDs, wikilink files/headings/blocks, navigation, source drift, and derived indexes. The optional location audit lists unclassified Markdown outside the Vault, excluding build/runtime folders and configured source-owned exceptions. It does not delete or move files. Review any additional `allowed_markdown` patterns narrowly; adding a broad exception hides future misplaced documentation.

Do not imply that this validator checks arbitrary Markdown links, natural-language truth, complete business coverage, Mermaid grammar/rendering, screenshot provenance, or the live Obsidian/SAP UI. Review those when part of the acceptance scope. Templates are intentionally parameterized and excluded from note validation. A warning about a long Current State or changed evidence requires judgment; it is not an automatic semantic failure.

Writes are preflighted, serialized with a project-local lock, checked against the read baseline, and replaced per file. On a caught failure, rollback touches only the helper's own unchanged writes. This is not a database transaction across power loss. After an unexpected process interruption, inspect `.documentation.lock` (PID/time), the actual files, and source-control diff before manually clearing a stale lock and rerunning validation. Never remove another active writer's lock or overwrite concurrent human changes.

## Adopt existing material

1. Read applicable instructions, the target Vault's structure, and the narrowly relevant source inventory. Establish authority and record a path/ID mapping in the intended Vault. Keep original FS/TS and repository history intact.
2. For an unmanaged nonempty Vault, perform explicit adoption with reviewed file edits: establish schema-1 `vault.json`, the four root guides, registered entity folders/core notes and template copies without overwriting foreign content. The initializer will not do this migration automatically. Use the schema here and the assets as the reference; the normal checker then establishes structural conformance. For a managed Vault, reuse its IDs and extend it normally.
3. Classify each Markdown source as canonical original, source-owned tool/package documentation, temporary scratch, or a development narrative to consolidate. Copy/link or migrate only within the requested scope; inspect existing target content before merging. Retain original authority and record historical occurrence separately from this import's recording date.
4. Rebuild links and indexes, check the adopted Vault, inspect relevant diagrams and screenshots, and report remaining unresolved history. A conflict or unavailable source is an open item. Do not label a scaffold as an imported project history.

Minimal marker for a reviewed adoption (add only justified source-owned exceptions):

```json
{"schema_version": 1, "project_key": "ACME-ERP", "language": "en", "allowed_markdown": ["AGENTS.md", "AGENTS.override.md", "README.md"]}
```
