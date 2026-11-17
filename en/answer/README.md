# Answer

[English catalog](../README.md) · [Türkçe: Yanıt](../../tr/yanit/README.md)

Answer suggests **2–5 useful messages you could send next** in the current conversation. It considers the goal, completed work, remaining decisions, blockers and your latest corrections, then ranks distinct options with **0–100 prediction scores**. Three options are the default when three genuinely useful alternatives exist.

## Use

```text
/answer
/answer Give me two short options.
/answer Focus on the unresolved review findings.
```

The Turkish counterpart is [Yanıt](../../tr/yanit/README.md), called with `/yanıt`. Answer defaults to English; Yanıt defaults to Turkish. An explicit request can change the prose language; each entrypoint keeps its own score and rationale labels.

These are text triggers interpreted by the skill, not registrations in an application's built-in slash menu. If your client reserves slash input, select the skill or use `$answer`. The UI starter `/answer $answer` keeps the requested text trigger and the exact native skill selector together. Quoted commands, `/answering`, and questions about the skill do not activate prediction generation.

## Output

Each option has a numbered bold title, an integer score, a copyable message and a short rationale. An illustrative two-option result:

**1. Draft the PR description — Recommended** (Prediction score: 99)

> Draft a concise PR title and description covering the problem, changed behavior, and completed tests for this fix.

Why: This completes the remaining PR preparation.

**2. Explain the behavior change** (Prediction score: 85)

> Explain how the fix changes the user's experience, using the existing evidence to compare the previous and corrected behavior.

Why: This provides a different way to understand the completed change.

Scores are heuristic estimates of contextual suitability, **not probabilities, measured accuracy or proof that an action is authorized**. The example score 99 is not a fixed value. Scores descend, ties are allowed, and a recommendation marker is omitted when no clear preference is justified.

## Context and action boundaries

- Start with the current conversation. If a missing fact could change the suggestions, make at most three targeted, read-only checks of relevant project files or already available connected sources.
- Preserve current constraints, rejected directions and existing authorization. Do not repeat completed work or duplicate an operation already running without a concrete reason.
- Offer clarification or closure when context is thin or the work is finished; do not invent extra work to fill the list.
- Stop after presenting suggestions. Do not send messages, modify files/settings/memory, start new service connections, install tools or execute a proposed task during prediction generation.

Selecting an option later is a new ordinary task request for that displayed message. Asking to shorten an option edits its text. An ambiguous number is clarified before any action.

## Install

Ask Codex's Skill Installer to install `en/answer` from this repository, or copy this individual package into a skill discovery directory supported by your host. Install `tr/yanit` separately if you want the Turkish entrypoint. Keep the reference file with the skill and preserve an existing installation before replacing it.

Check that **Answer** appears in the skill list. This package has no MCP server, background service, hooks or Python runtime dependency. Client discovery behavior and built-in command menus are separate from the skill's text-trigger rules.

## Files and verification

- [SKILL.md](SKILL.md): entrypoint, metadata, numbered rules and output contract.
- [Edge cases](references/edge-cases.md): conditionally loaded rules for missing context, finished work and short selections.
- [UI metadata](agents/openai.yaml): display name and starter prompt.
- [Changelog](CHANGELOG.md), [archive guide](archived/README.md), and [GPL-3.0 license](LICENSE).

The two language packages share identical English model-facing rules and references; names, descriptions and human documentation are localized. Use the repository's [validation and versioning instructions](../CONTRIBUTING.md). Package checks do not establish prediction quality, native UI compatibility, token savings or superiority over Composer Predictions. Those require separate behavioral or comparative evidence; no such superiority is claimed.
