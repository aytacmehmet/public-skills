# Belirtim Yazmanı 3.0.0

English · [Türkçe](README.tr.md)

## Purpose
Shared Claude Code/Codex documentation skill for SAP Cloud ERP. Consultant business/design decisions are collected with at most three ranked suggestions; implementation questions belong to the ABAP developer. Separate linked-development ZIPs are delivered together after all business, architecture, reference and final review gates pass. The package is self-contained and neutral to the developer's tools/model.

## Installation
The plugin-owned runtime requires Python 3.11+, Node.js 20+ and the locked `requirements.txt` packages. Use a virtual environment and `python -m pip install -r requirements.txt`. No dependencies belong to the embedded skill; the official TOON codec is vendored.

```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install belirtim-yazmani@aytacmehmet-public
```

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/belirtim-yazmani
codex plugin add belirtim-yazmani@aytacmehmet-public
```

Invoke the namespaced skill in Claude Code or `$belirtim-yazmani` in Codex. This repository publication does not install anything or select a model.

## Workflow
Resolve `scripts/bv2.py` from the absolute loaded skill directory; cwd may differ.

1. `init`/`migrate`, then `release-init` create a 3.0 private TOON target. Original inputs remain untouched. Existing 2.0 workspaces use `release-upgrade`; old approval/review evidence is invalidated, not silently relabeled.
2. `questions` returns consultant BUSINESS/USER_EXPERIENCE/BUSINESS_DESIGN items only. Options carry text, rationale, assumptions and separate 0..5 consistency/suitability/quality scores. Their mean orders A/B/C; scores are relative judgments, not approval. No grounded options means an explicit reason, not invented alternatives.
3. Public `developer_decisions` records are bounded ABAP_DEVELOPER/IMPLEMENTATION choices with sufficient context, constraints, architecture refs and locally packaged inputs. Business gaps cannot be assigned to this list to evade a gate. Delivered open technical choices mean READY_FOR_DEVELOPER_DECISIONS, not READY_FOR_CODING.
4. `check-plan` computes changed check units and dependency hashes; `check-record` stores actual bound results. Reuse only passed unchanged units. Accumulate intermediate edits before expensive stable-snapshot independent reviews. Cache never approves a release or claims a fresh model run.
5. Complete responsibility boundaries, architecture constraints, functional chains, baseline and references. Every referenced file/text/list/pointer must exist locally in the ZIP. Every basename starts with the approved meaningful short name. Manifest roles identify the authority; no fixed fsts/fs-ts filenames are emitted.
6. `release-approve`, final `eval-request`/`eval-record`, and `confirm-reviews` preserve genuine current-snapshot approval and five-layer review. Two clean final rounds are required. No fake execution, autonomous business defaults or SAP mutation.
7. `handoff-batch` reads a TOON manifest with `developments` entries containing `workspace` and `assets_root` paths inside the manifest directory. Use `--output` and `--batch-id`. Changed linked developments must all be present; contracts bind partner version/hash/source pointer and complete needed content. Separate ZIPs are staged, verified and published together in one new directory; cycles, overlapping mutations or a blocked partner publish nothing.
8. `verify` reads 3.0 role manifests and legacy 2.0 packages as references. Updates contain baseline content plus stable-ID changes; immutable deliveries are never overwritten. `feedback` creates a new-version regression.

## Contract and limits
TOON is the only editable/public specification authority; optional Excel is derived, PNG layout-only. Required dependency contracts and source excerpts are included in each ZIP, not obtained from other files or URLs. Neutral developer instructions describe the reading order, bounded technical decisions and acceptance checks; no local skill/plugin/model, application source, scaffolds or executable development/test scripts are shipped. An existing explicitly authorized offline interactive exception remains separate.

Three independent readers, scenario agreement, real PNG inspection and code-free architecture/plan checks are still final release gates. Fixtures are synthetic; unavailable execution/vision is NOT_RUN. Local schema/ZIP checks are not SAP authorization, activation, ATC, runtime or UAT proof. See [verification](docs/VERIFICATION.md) and [changes](docs/CHANGES.md). No new token/latency benchmark was run for 3.0.0.

## Public package checks

Run `python -B skills/belirtim-yazmani/scripts/check_package.py` and the targeted runtime tests. Build the complete offline marketplace ZIP with `python -B scripts/build_package.py --output-dir <external-artifacts>`. Copy the generated PACKAGE-MANIFEST.json into the plugin before committing and run repository validation. Artifacts remain outside the repository. The existing 1.1.0 JSON standalone pair retains its own lineage; install one Spec Writer version at a time. See [public changes](CHANGELOG.md) and [publication provenance](PUBLICATION.json).
