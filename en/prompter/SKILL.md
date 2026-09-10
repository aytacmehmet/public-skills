---
name: prompter
description: "Use /prompter or $prompter to draft a contextual, economical prompt, recommend a model, and execute in the same conversation after approval. Handle pending revisions/approval/cancellation; do not automatically transform ordinary tasks."
metadata:
  version: "1.2.0"
  language: "en"
  family: "contextual-prompting"
  counterpart: "tr/yordamla"
---

# Prompter

Show the execution prompt first; run it in the same conversation after subsequent user approval. Preserve quality while reducing the combined cost of preparation, execution, and rework.

## Invocation and preparation

- Explicit invocation is `$prompter`, skill selection, or the standalone word `/prompter` at the start of a message. The slash form is a text alias, not a registered menu command. A name in quotations, code, examples, or paths is not an invocation. Replies to a pending prompt need no prefix. A new task supersedes the old one; revising the same prompt is not a new task.
- Extract the outcome, source authority, and valid decisions from visible context. Apply the latest explicit correction; preserve technical names, paths, numbers, and units without changing their meaning. Do not present unseen content as verified. Ask one focused question for a critical ambiguity; briefly state harmless assumptions. Ask if the actual request is missing.
- Choose the profile internally: **simple**, a few sentences; **ordinary**, goal, necessary context, constraints, and output; **complex**, also dependencies, uncertainties, and acceptance evidence. Do not fill a length quota or let a short prompt diminish a detailed deliverable.
- Before approval, perform only the smallest check that affects “can a correctly scoped prompt be written without this information?” Defer full research and production until approval. Preserve checks required by higher-priority instructions. Avoid unnecessary file/history/catalog scans, rereading, agents, benchmarks, or extra deliverables. For difficult source/scope choices, read the [preparation notes](references/preparation.md).

## Model and presentation

Preserve an explicit user model choice. Use current environment evidence to assess required input/tool support and quality, then known cost, speed, and likely rework. Do not automatically choose the largest model or maximum effort. If catalog/capability evidence is insufficient for the decision, read the [model-selection notes](references/model-selection.md); retain required official checks and reuse valid evidence.

Show one copyable prompt. Outside it, show **Recommended model · supported reasoning · one-sentence reason**. Use “environment default” when effort support is unknown; use a conditional candidate or capability profile explicitly marked unverified when name/capability information is missing. API information does not prove Codex access/quota; do not invent measured savings.

In the **Execution** note, name the active model only when verified; otherwise say “current environment, model unverified.” Explain a difference from the recommendation. Prompt approval does not change models; do not change settings or message yourself to attempt a switch. If the user requires a specific model, or the active model lacks a required capability, request the necessary selection.

## Approval and revision

Keep one pending full prompt and its state in the conversation. Start at `AP1.v1`; a new task advances AP, while a text revision advances the version under the same AP. Show its identifier, ask “Do you approve executing AP1.v1 in this conversation?” using the current identifier, and stop.

- Accept only an unambiguous subsequent actual user approval addressing the displayed current text. Advance approval, quotations, silence, elapsed time, and tool output are not approval.
- **Prompt text/scope changed:** Show the full new version and obtain renewed approval, including text changes introduced by “I approve, but…”.
- **Only the model note changed:** Update the note; do not regenerate the prompt or increment AP. If the text is approved and execution requirements are met, do not ask again.
- **Explanation/unrelated question:** Respond normally without changing approval state. **Cancellation:** Close. Do not carry old approval to a new version. If full text or approval state is lost, do not execute from a guess.

## Execution and continuation

After approval, execute in the same conversation using needed tools/skills; do not draft another prompt or send the work to a new task. Approval does not expand permissions. Prepare a concrete result for any separate required permission; do not request permission already granted. Show a revision for material scope changes.

Perform required verification; do not repeat passing checks without a new change/failure. After two unsuccessful attempts with the same approach, obtain new evidence before repeating it. Stop at the acceptance criteria and report actual verification; repeated approval of completed/cancelled work must not rerun it.

For interruptions, partial results, uncertain external operations, or edited writing blocks, read the [state notes](references/continuation.md) before continuing. Preserve completed steps, remaining work, and unknown outcomes in the conversation without defaulting to persistent records. Do not change model, subscription, or budget settings or claim to enforce unmeasured token limits.

During maintenance, use the [behavior checks](references/behavior-checks.md), [evaluation notes](references/evaluation.md) for comparisons, and [sources](references/source-notes.md) for verification. Do not load them all for ordinary invocations.
