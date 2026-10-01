# Yula 1.4.1

English · [Türkçe](README.tr.md)

Evidence-backed SAP S/4HANA Cloud Public Edition object advice, ABAP Cloud call contracts and configuration architecture in one **Codex and Claude Code** plugin. Answers follow the user's language; model instructions, tool schemas and shared technical references are English.

## Contents

- [Released object advisor](skills/sap-released-object-advisor/README.md): select and explain objects.
- [Released object developer](skills/sap-released-object-developer/README.md): exact public signatures and call context.
- [Configuration architect](skills/sap-configuration-architect/README.md): SSCUI/CBC, dependencies, diagnosis and release impact.
- Four offline read tools: `yula_search`, `yula_get`, `yula_check`, `yula_status`. Updates are explicit CLI operations.
- A populated SQLite seed: **37,030 catalog entries, 33,307 object contexts, 244,715 members, 4,328 configuration activities**. Dates, hashes and gaps are in `data/manifest.json`.

## Installation

Requires **Python 3.11+ with SQLite FTS5**, available as `python` in the host's PATH. No pip/npm install or SAP connection is needed for offline use. This public repository needs no private GitHub access.

Claude Code:

```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install yula@aytacmehmet-public
```

Codex CLI:

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/yula
codex plugin add yula@aytacmehmet-public
```

Start a new host session. See [installation and updates](references/installation.md) for preflight, local/ZIP installation and host details. Install the complete plugin; individual skill folders depend on shared files.

## Database and updates

`data/yula.sqlite.zip` contains the complete **472,088,576-byte SQLite database**, compressed to 78,681,985 bytes. No Git LFS client or seed download is needed. First use checks the archive hash, member name, expanded size, CRC, SQLite hash and schema, then publishes an external snapshot. The expanded SHA-256 is `bf16b36d56dd4382dea07a3c5cd63250095e9ba3500b8a607f37b5228996b620`, unchanged from 1.2.0.

The MCP manifest explicitly selects `@user/yula`: `YULA_DATA_ROOT` if set; otherwise `%LOCALAPPDATA%/yula` on Windows, `$XDG_DATA_HOME/yula` or `~/.local/share/yula` elsewhere. Set `YULA_DATA_ROOT` in the host launch environment to isolate hosts. Allow roughly 1 GB of free space for first-use staging; updates and retained rollback snapshots need additional space. The plugin directory is immutable.

Run from the installed plugin directory; a concrete external `--data-root PATH` overrides the environment:

```text
python scripts/yula.py --data-root @user/yula status
python scripts/yula.py --data-root @user/yula check --source sap-released
python scripts/yula.py --data-root @user/yula apply --plan /path/from/check/plan.json --hash SHA256_FROM_CHECK
python scripts/yula.py --data-root @user/yula rollback --expected-active CURRENT_SHA256 --to BACKUP_SHA256
```

Use the exact plan path/hash returned by `check`. Copy `config/sources.example.json` outside the plugin for optional sources, then select them with `check --config /external/sources.json --source SOURCE_ID`. Supported inputs: official released-object JSON, SAP Help topics/documents, compatible object/configuration SQLite, configuration folders/workbooks, evidence records and read-only SAP CLAS/INTF metadata. Credentials are environment-variable references only. Metadata refresh does not refresh public signatures. Updates stage and validate before atomic publication; previous snapshots remain available for rollback. No schedule or background updater is installed.

## Verification and limits

```text
python scripts/preflight.py --host both
python scripts/check_package.py --work-dir /external/yula-check
python -B -m unittest discover -s tests -v
```

Tests use temporary directories; set `YULA_TEST_ROOT` to choose their parent. CI verifies the compressed and decoded database, package hashes, repository rules and runtime tests. `tests/validation.json`, `tests/host-compatibility.json` and `tests/review-1.2.0.json` are explicitly versioned historical 1.2.0 evidence; the current repository CI verifies 1.4.1.

There are **2,539 current released objects without enriched context**. Only two capabilities and one recipe are curated; other candidates need contract evidence. Unknown fetch dates and historical failed ingestion records stay visible. Local tests do not establish SAP tenant/compiler/ATC/runtime readiness. Controlled Codex MCP, activation and safety results are recorded in the [historical 1.4.0 qualification evidence](tests/qualification-1.4.0.json); no general token-saving or SAP tenant qualification is claimed. Claude model evaluation remains NOT_RUN.

## Distribution and licensing

1.3.1 fixes Codex MCP startup: Codex does not expand `${CLAUDE_PLUGIN_ROOT}`, so `.codex-plugin/plugin.json` now declares the server inline, starts it from the installed plugin root (`cwd: "."`) and forwards `YULA_DATA_ROOT`. Runtime, skills and corpus are unchanged. 1.3.0 adds repository marketplace integration, bilingual documentation, bounded compressed-seed loading, explicit CLI data targets and distribution tests. Base corpus content is unchanged. Source/runtime are [GPL-3.0](LICENSE); retained SAP source terms and attribution are in `LICENSES/` and [provenance](references/provenance.md). Public plugin release history uses committed Git revisions; complete delivery ZIPs are external artifacts, not duplicate repository archives. See the [changelog](CHANGELOG.md) and [source publication record](PUBLICATION.json) for the first public-skills distribution.

Rebuild the delivery with `python scripts/build_package.py --output-dir /external/artifacts`. Copy its generated `PACKAGE-MANIFEST.json` into the plugin source before committing, then run package validation. The builder never modifies the source.

## Bounded retrieval and task scope

Version 1.4.1 reads accepted structured research summaries with an explicit JSON representation. Oversized structured activity records use lossless `json_record_page` responses. Set `textOffset` to the returned `nextTextOffset`, keep the record `offset` and `snapshot` unchanged, and follow the returned record `nextOffset` only after its text pages complete. When advancing the record offset, omit `textOffset` until the next response selects `json_record_page`. Partial JSON is not complete record evidence. The text page may shrink further to respect the MCP response bound.

Corpus lookup uses the four read-only tools; MCP resources and host filesystem searches are not corpus lookup fallbacks. Correct a named argument or use a supported targeted section once, then report the evidence gap. Explicitly requested storage maintenance retains its CLI diagnostic procedure.

Diagnosis considers evidence-relevant hypotheses. Full transport details are produced for a requested transport plan. Upgrade analysis compares stored release partitions; refreshing/importing source content requires an explicitly requested maintenance task. Local catalog facts and test results do not establish target-tenant availability or execution.
