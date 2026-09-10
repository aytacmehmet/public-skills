# Changelog

## 1.2.0 — 2026-09-10

- Smaller core with on-demand preparation/continuation references and internal task profiles.
- Separate model-note edits, prompt revisions, and explanations; handle paused tasks and unknown operation outcomes.
- Verified execution status separate from the recommended model.
- Paired bilingual evaluation inputs and a maintenance-only summarizer for supplied results/metrics, with no model calls.
- Regression checks for missing entrypoints and incorrect default invocations in shared repository validation.
- Archived 1.1.0. Reduced core instructions; no claim of measured total-token savings or automatic model switching.

## 1.1.0 — 2026-09-07

- Added an execution model, supported reasoning effort, and brief reason to each ready prompt.
- Selection considers required capabilities, quality, and total work economy without hardcoding model names.
- Unknown access/settings are explicit; prompt approval does not change models.
- Added model-selection maintenance notes and behavior scenarios; archived 1.0.0.

## 1.0.0 — 2026-09-05

- First public release of Prompter, the English counterpart of Yordamla.
- Context-aware prompt drafting, version-bound approval, and execution in the same conversation.
- Instructions to limit unnecessary work while preserving required verification.
- English installation, usage, source, behavior-check, and archive documentation.

Earlier public versions: none.
