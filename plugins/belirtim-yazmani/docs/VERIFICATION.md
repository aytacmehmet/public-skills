# Release verification

English · [Türkçe](VERIFICATION.tr.md)

## 2.0.1 candidate evidence
Local 2.0.1 publication gates passed: repository validators, six standalone release packages, 71 plugin tests, 31 release-tooling tests, the standard-library package check and skill frontmatter validation. Claude strict manifest validation passed; isolated Codex `plugin/read` reported localVersion 2.0.1 and the updated shared skill, without installation or a model call. Hosted final-head CI is separate and must pass before merge.

On 2026-10-01, token audit `tca-20260930-002`, paired run `x8`, passed 20 cases across two variants with three repeats (120 real Codex runs). This is the exact discovery description applied in 2.0.1; the release version and documentation were then updated mechanically. See `TOKEN-EVAL.toon` for the recorded metrics and hashes.

Task quality stayed 1.00; invocation/non-invocation accuracy rose from 0.70 to 1.00. Cost per successful task index fell 24013.9 → 19491.3 (-18.8%, measured weighted-token index, not money or billing). Tool calls fell 4.73 → 4.03; failed calls 1.80 → 1.20; retries 1.80 → 1.07. The description estimate increased 74 → 91 tokens while the body estimate stayed 1753. Residual path failures remain. No controlled latency or TOON-versus-JSON benchmark was run.

Runner: codex-cli 0.153.4; configured model/effort: default; served model: unknown. Qualification is limited to this Codex configuration and suite; Claude model execution remains NOT_RUN. An isolated snapshot of auditor 1.5.1-codex.2 used Windows-only attempt paths, unchanged parent-plugin support, native workspace sandbox grading and the same pinned official TOON 4.1.1 codec through stdin. Positive/negative grading controls passed; ACLs, auth and isolation were not relaxed. Invalid infrastructure trials and two clarified test-output labels were excluded before the candidate comparison. This is not the full handoff reader/visual/tenant release gate.

## Original 2.0.0 evidence
Version 2.0.0; original pinned public source `1e7717606641a8dbd0e390142a739acd157bae38`.
The prepared distribution passed 71 local runtime/seeded-error tests and 49 A-F rule mappings.
Claude Code 2.1.285 passed strict manifest validation. Codex 0.153.4 `plugin/read` discovered
the common skill in an isolated profile without installing it or making a model call.

Repository publication changes English machine metadata, bilingual docs, permanent R-BYW IDs,
catalogs, private standalone redirects/archives and CI wiring. Runtime/checker/codec behavior stays
unchanged. Repository validators passed; 31 release-tooling tests and 71 plugin tests passed locally. Final-head CI remains separate and must be green before merge.

## Token boundary
The original 2.0.0 repository entry was locally counted at 1258 o200k_base tokens (tiktoken 0.14.0).
The pre-publication comparison of identical rules selected short Markdown over hybrid/TOON
instruction bodies. FS-TS data remains TOON. Reference files are loaded only when needed.
This is input-file counting, not end-to-end cost, billing, speed or semantic superiority.
The original 2.0.0 publication did not run Claude tokenization or a real model comparison; the later Codex result is recorded above.

## Unrun qualification
Actual three-reader semantic execution, actual visual reader qualification and SAP tenant,
activation, ATC, runtime and UAT are NOT_RUN. Fixtures simulate trusted review records for mechanical
tests; they are never fresh model or tenant evidence. A real handoff remains blocked until genuine
independent execution, owner confirmation and all current-snapshot release gates are complete.
Windows/Linux hosted CI is separate from local validation and must be green before merging.
