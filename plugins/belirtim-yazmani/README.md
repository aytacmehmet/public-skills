# Belirtim Yazmanı 2.0.2

English · [Türkçe](README.tr.md)

## Purpose
One shared Claude Code/Codex skill and plugin-owned runtime for decided SAP Cloud ERP developments.
It documents facts and decisions; it does not design solutions, code applications or mutate tenants.
The private TOON workspace keeps the complete target and private control records separate.
The developer authority is `fsts/fsts.toon`. Excel is an optional projection.

## Installation
Python 3.11+, Node.js 20+, and the locked packages in `requirements.txt` are required by the
plugin runtime. No pip packages or scripts are owned by the embedded skill. The TOON codec is vendored.
Use a virtual environment and `python -m pip install -r requirements.txt` at the plugin root.

Claude Code:
```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install belirtim-yazmani@aytacmehmet-public
```
Codex:
```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/belirtim-yazmani
codex plugin add belirtim-yazmani@aytacmehmet-public
```
Invoke `/belirtim-yazmani:belirtim-yazmani` in Claude Code or `$belirtim-yazmani` in Codex
(use the namespaced name if shown by the host). Both use the same rules and runtime.
No automatic installation, model selection or user configuration change is performed.

## Workflow
Use `python scripts/bv2.py --help`. Resolve the runtime path from the installed skill directory;
the working directory may differ. `BY_NODE` can select the Node executable.

1. `init` or `migrate` keeps the legacy input and creates a TOON workspace; original JSON is untouched.
2. `release-init` opens the authoritative `delivery.spec`; imported content becomes read-only reference.
3. `profile`, `guide`, `patch` and `context` expose only applicable guidance/data with reference closure.
4. `release-inspect` enforces typed profiles, traceability, zero-open counters and producer/code scans.
5. `release-approve`, `eval-request`, `eval-record` and `confirm-reviews` bind genuine owner/reviewer records privately.
6. `handoff` refuses any gap, missing review or fewer than two consecutive clean rounds. `verify` checks saved artifacts.
7. `feedback` records each developer defect as a regression and requires a new version.

The A-F handoff contract uses TOON for the FS-TS, schema, manifest, readiness, objects and delta.
UI requires numbered PNG callouts bound by hashes. Interactive assets require an explicit exception,
offline verification and static checks. Each handoff covers one development and remains immutable.
Changes to another development require its own handoff. Baseline artifact and decoded spec hashes differ.
No access is not verified absence. Full target plus stable-ID delta is delivered.

## Verification and limits
Run `python -m unittest discover -s tests -v` after installing runtime dependencies.
Local helpers do not call model or SAP services. Hosts run independent readers using the user's settings.
Three isolated readers, scenario agreement, actual PNG review and code-free plan simulation are required;
helpers validate supplied execution records and cannot authenticate external runs. Missing capability is `NOT_RUN`.
Fixtures simulate records, not actual semantic/model/tenant qualification. Neither a valid schema nor a clean
ZIP proves absolute completeness, SAP activation, ATC, runtime, UAT or token/latency savings.
Historical 2.0.1 source qualification is preserved in [verification](docs/VERIFICATION.md); rule coverage is in
`docs/RULE-COVERAGE.toon`. This 2.0.2 public plugin is separate from the repository's legacy 1.1.0 JSON standalone pair.
Install one version of Spec Writer at a time; the complete 2.x plugin owns its shared TOON runtime.
See the [public changelog](CHANGELOG.md) and [source publication record](PUBLICATION.json). New model/SAP qualification is not claimed.

## Public package checks

Run `python -B skills/belirtim-yazmani/scripts/check_package.py` and `python -B -m unittest discover -s tests -v`. Rebuild the complete offline marketplace ZIP with `python -B scripts/build_package.py --output-dir <external-artifacts>`. Copy the generated PACKAGE-MANIFEST.json into the source before committing and rerun repository validation. The builder verifies ZIP CRC and per-file hashes and does not modify the plugin source. Python dependencies remain pinned; the unmodified MIT TOON codec is included. Public and historical qualification are separate evidence.
