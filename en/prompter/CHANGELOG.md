# Changelog

## 2.0.0 — 2026-09-17

- Single runtime file: `SKILL.md` has no links and loads no references; preparation, model-selection and continuation notes were merged into its `<preparation>`, `<model_note>` and `<recovery>` sections and the three reference files were removed.
- Slot template with mandatory `Sources`, `Out of scope`, `Output`, `Acceptance` and `Stop` slots (plus `Dependencies` and `Uncertainties` for complex tasks), a fixed tool-budget line, conversion of vague qualifiers into measurable statements, and a three-item self-check before the prompt is shown.
- Explicit profile criteria; single-slot ambiguities are asked together with a `[?]`-marked draft.
- Behavior change: simple tasks with no side effects are shown and executed in the same turn; all other tasks keep version-bound approval. Short positive replies count as approval of the single pending prompt; approval of an older version asks instead of executing.
- One-line model note when the recommendation equals the current model; the approved text is the sole execution scope; the finish report is at most three lines.
- Instructions rewritten in English-style imperative form with XML sections and two good/bad examples; the output language follows the user (default English).
- Maintenance: behavior checks PW29–PW34, updated structural checks, model-selection sources moved into the source notes. Archived 1.2.0.

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
