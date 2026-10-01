# Source maintenance (load only for updates)

R-YMT-01 Runtime: Python 3.11+ with SQLite FTS5, standard library only. Entrypoint: `scripts/yula.py` relative to the installed plugin. MCP lookups are offline; maintenance is an explicit CLI operation. No scheduler, background service or SAP mutation is installed.

R-YMT-02 Select external storage explicitly with `--data-root PATH` before the subcommand or `YULA_DATA_ROOT`. The MCP manifest selects `--data-root @user/yula`: use `YULA_DATA_ROOT` when set, otherwise `%LOCALAPPDATA%/yula` on Windows or `$XDG_DATA_HOME/yula` / `~/.local/share/yula` elsewhere. A concrete PATH overrides the environment. First use verifies `data/yula.sqlite.zip`, expands its single member outside the plugin with size/hash/CRC checks, validates SQLite, then publishes the snapshot. Existing data is preserved across plugin upgrades; no database download is required.

## Operations

```text
python scripts/yula.py --data-root @user/yula status
python scripts/yula.py --data-root @user/yula doctor
python scripts/yula.py --data-root @user/yula migrate
python scripts/yula.py --data-root @user/yula check --source sap-released
python scripts/yula.py --data-root @user/yula check --config /absolute/sources.json --source selected-source-id
python scripts/yula.py --data-root @user/yula apply --plan /absolute/plan.json --hash SHA256_FROM_CHECK
python scripts/yula.py --data-root @user/yula rollback --expected-active CURRENT_SHA256 --to BACKUP_SHA256
```

R-YMT-03 Use the exact returned plan path and hash. `check` downloads/reads selected sources, stages normalized differences and validates a candidate; it does not replace active data. `apply` rejects an edited plan/candidate or a base generation changed since check. The old immutable snapshot is the backup. Publication and rollback change only an atomic `current.json` pointer under a cross-process kernel lock; un-pinned reads reopen the pointer; a response snapshot pins related reads and pagination. Process death releases the lock. Orphan stages are never active.

R-YMT-04 Identical content returns `current`; no new corpus is published. Completed HTTPS response checkpoints are reused only after hash validation. SAP Help pages are keyed by exact build and file; interrupted document work resumes completed pages. Partial bytes and partial documents are never published. Downloads use verified TLS, no redirects, finite size/time bounds and at most two retries. Restart `check` after a failure; it uses valid checkpoints and creates a fresh plan.

R-YMT-05 `doctor` verifies the active hash, schema, SQLite integrity, foreign keys, catalog counts and retrieval-index coverage. Unsupported schema versions fail closed. Storage revision 2 adds exact-name/identity indexes and per-topic provenance without changing the base schema ABI (`user_version=1`). `migrate` stages this additive revision and returns a plan/hash for normal `apply`; existing snapshots and rollback remain intact. Old working data stays readable until migration; changed-source maintenance also adds the revision in its staged candidate. Upgrade both hosts when sharing a corpus. Future incompatible schemas require an explicit converter. Do not edit a snapshot in place or silently recreate an unknown database.

## Source configuration v1

R-YMT-06 Use `config/sources.json` for bundled official sources. Only `sap-released` is enabled by default; optional Help sources require explicit selection. `--source` selects configured sources regardless of their `enabled` flag. Without it, only enabled sources run. The catalog runs before system-object reads.

R-YMT-07 For local/system sources, copy `config/sources.example.json` outside the plugin, set the appropriate environment variables, and select only intended source IDs. IDs own source freshness/fingerprints; keep them stable. `path` may be absolute or relative to the external configuration file; `pathEnv` reads an external environment variable. A workbook URL replaces `path`/`pathEnv` when downloading an official SAP workbook.

| Adapter | Accepted input / behavior |
|---|---|
| `released-catalog` | SAP's exact Public Edition `objectReleaseInfoLatest.json`, formatVersion 1. Validates unique type/name and known states. Retains removed identities as `notListed`; no silent deletion of historical contracts. |
| `sap-help` | Complete `https://help.sap.com/docs/product/deliverable/topic` URL. `mode=topic` refreshes only that topic; `document` resolves the full TOC/build and publishes only a complete result. Default `maxTopics=5000`; exceeding it aborts. |
| `legacy-objects` | Compatible SAP Brain object-knowledge SQLite, including public content, members, evidence, mappings and recipes. Uses SQLite backup, validates schema and exact official identities. Replaces the imported object-domain projection; stored Yula records/configuration/docs and current catalog remain. New identities require a catalog refresh first. |
| `configuration-db` | Compatible SCA SQLite with canonical catalog, access, expert, document and knowledge tables. Replaces only the included release partitions. Dossier/source files absent from an index require `configuration-root`. |
| `configuration-root` | SCA root containing `data/releases/` canonical JSON/JSONL/Markdown. Copies into staging and rebuilds the index there; original files are never changed. Reconciles dossier profiles and source registries, including withdrawals; locally recorded immutable revisions are reprojected afterwards. |
| `configuration-workbook` | SAP SSCUI `.xlsm` with an explicit four-digit `release`, a matching release worksheet, access-map worksheet and expert sheets. Reads ZIP/XML; never executes macros. Replaces catalog/access/expert data for that release and flags affected curated records for review. |
| `knowledge-records` | UTF-8 JSON array following the skill's conditional record procedure. Immutable revisions; evidence gates run before publication. |
| `sap-adt-metadata` | Exact catalog-released CLAS/INTF identities, HTTPS `origin`/`originEnv`, optional `authorizationEnv` containing the complete authorization header. GETs the ADT metadata shell only; validates returned identity. No discovery, source/main, implementation, business data or writes. Stores sanitized metadata observations separately; existing signatures are not marked refreshed. |

R-YMT-08 The native SAP adapter is intentionally bounded to verified route formats. Other object types/public signatures use compatible reviewed corpus imports. A configured connector and passing local contract test do not establish live tenant authorization; absent connections are reported as unavailable. Never put credentials into source JSON, a record, a database, log or the ZIP.

R-YMT-09 Review flags preserve prior dossier/edge/lesson evidence when a catalog or What's New change affects an activity. They do not auto-promote evidence to a new release. Candidate, stale and conflicting knowledge remains visibly nonauthoritative.

R-YMT-10 To refresh many sources, select only those relevant to the task. Large Help documents can take time; run the CLI through the host's normal asynchronous process mechanism and observe its result. Do not repeatedly poll an unchanged operation or reload the entire corpus into model context.

R-YMT-11 Documentation provenance is topic-specific. Version/language changes create separate partitions. Newly fetched non-overlapping chunks reassemble exactly. Imported legacy fragments remain labelled `legacy_chunks`; their unknown fetch dates are not invented. A stale topic hash fails closed.
