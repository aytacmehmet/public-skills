# Belirtim Yazmanı 3.2.2

English · [Türkçe](README.tr.md)

## 3.2.2 pooled reader sources

One complete source per byte hash is carried in each protocol 3.2 reader packet; references retain source identity/hash/pointer. The runtime decodes each source once and blocks excessive serialization before output. Use `read-reference <packet> --reference-id <ID>` or initialize `source_pool.Reader` once for repeated pointer access. Legacy packets use explicit `--allow-legacy` read-only access; their old review records and owner execution confirmation do not provide current-protocol credit. Public schema, profile budgets, three full readers, blindness, approvals and two clean rounds are unchanged.

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

## 3.2.1 native host compatibility
Codex 0.160.0 native probes identified manifest selection and Windows hook launch compatibility issues in the initial 3.2.0 package. Version 3.2.1 uses `.codex-plugin/plugin.json` as the active Codex entrypoint and retains portable agent-plugin metadata at `metadata/agent-plugin.json`. Its Windows hook command uses the native runtime's `${PLUGIN_ROOT}` substitution with quoted paths, compatible with the runtime's default command shell. Reinstall/update the complete plugin package to receive these changes. Native hook loading, trust, event execution and provider work remain separate checks; this patch preserves the five profiles and every business, approval and final review gate.

## 3.2 work profiles
Choose **Lite / Yalın, Plus / Gelişmiş, Pro / Yetkin, Max / Doruk or Ultra / Üstün** for the development's working intensity. The skill first presents one grounded recommendation card with risk/source rationale, unknowns, full-reader capacity, conditional preparation budget and a model suggestion inside the current provider family. The user's actual choice is recorded privately. It does not approve business defaults, the specification, a model/setting change or release. Existing document profiles `hafif/standart/tam` remain separate.

| Profile | Preparation attempts at most | Concurrent children at most | Total attempts per episode at most |
| --- | ---: | ---: | ---: |
| Lite / Yalın | 0 | 1 | 12 |
| Plus / Gelişmiş | 1 | 1 | 13 |
| Pro / Yetkin | 2 | 2 | 14 |
| Max / Doruk | 4 | 3 | 16 |
| Ultra / Üstün | 6 | 3 | 18 |

Each profile keeps three full-scope independent readers per final round and two clean current-snapshot rounds. The reviewer attempt ceiling is 12 in every episode; preparation ceilings are conditional, not targets. Failed/cancelled attempts, retries and revisions remain charged. Profile/host/coordinated-run limits apply together, with no more than three children and no nested agents. Linked workspaces share one coordinator file; unrelated host jobs require explicit slot accounting. Unknown/insufficient full-reader capacity blocks final dispatch/release. A lower selection is honored; a plan that does not fit waits for an explicit split/profile/budget decision.

Resolve the absolute `scripts/bv2.py` path from the skill directory, then use `work-profiles catalog`, `work-recommend`, `work-select`, `work-status`, `work-admit`, `work-begin` and `work-finish`. Native child dispatch belongs to the host skill; the CLI persists private selections, quota reservations, receipts and admission checks. It never launches a fixed-model subprocess. Packet issuance is not actual reader execution: reserve and finish each dispatched reader separately. See the [work profile protocol](skills/belirtim-yazmani/references/work-profiles.md) for arguments, scoring, capacity and recovery.

Command hook adapters add scoped admission/diagnostics. Native leaf PreToolUse requires the actual call ID and atomically claims an already charged reservation in the explicitly selected external coordinator; the same host/event ID is idempotent and a different call ID cannot reuse the attempt. This hook writes only the coordinator reservation; workspace specifications and user configuration are unchanged. Hook discovery, trust and runtime remain distinct; explicit core admission protects final release when hooks are skipped or unsupported. Capability/model access, vision and telemetry stay private and explicit; measured savings, provider dispatch and native host hook qualification require separate evidence. Final work-profile state never enters developer ZIPs.

## 3.1 operation
Run `status <workspace> --assets-root <inputs>` for current blockers and the next action. Before final readers run `preflight <workspace> --assets-root <inputs>`; missing assets, source mappings, references, pointers, business closure and dependency contracts stop packet issuance. It is read-only and does not approve a release. `check-plan`/`check-record` accept the same assets root and use checker-byte/physical-file fingerprints plus functional, UI, object and record units.

Private review protocol 3.1 requires fresh execution of old reader records. Every reader supplies a functional question per requirement and concrete plan evidence. The first two readers derive scenario outcomes without `test_cases.expected`; the third inspects the complete specification. Packets include needed reference content and contracts. Actual parsed replies are hash-bound; owner confirmation remains mandatory and does not authenticate providers. Public handoff schema 3.0, three readers, two clean rounds and immutable separate ZIPs remain unchanged. Consultant questions may declare real `depends_on` prerequisites and report `blocked_by`/`unlocks`.

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

Three independent readers, scenario agreement, real PNG inspection and code-free architecture/plan checks are still final release gates. Fixtures are synthetic; unavailable execution/vision is NOT_RUN. Local schema/ZIP checks are not SAP authorization, activation, ATC, runtime or UAT proof. See [verification](docs/VERIFICATION.md) and [changes](docs/CHANGES.md). The historical 3.0.0 benchmark limitation remains; profile/provider cost and native host execution remain separate qualification scopes for 3.2.1.
