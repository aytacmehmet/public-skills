# Prompter

[English catalog](../README.md) · [Türkçe: Yordamla](../../tr/yordamla/README.md)

Prompter turns your rough request into an actionable prompt that fits the current conversation. It selects the useful level of detail, shows you the result, and executes it in the same conversation after you approve it.

## Install

In Codex with Skill Installer available, send:

```text
$skill-installer Install the skill from https://github.com/aytacmehmet/public-skills/tree/main/en/prompter
```

Alternatively, copy this individual folder into a skill discovery directory supported by your Codex installation. Consult the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) for the appropriate location. Confirm that **Prompter** appears in your skill list; discovery may require a new turn or restarting the host. If a copy is already installed, preserve it before replacing it.

## Use

```text
$prompter Prepare the implementation we discussed, preserving the approved decisions and running only the necessary checks.
```

`/prompter` at the start of a submitted message is also recognized as a text alias. It does not create a slash-menu command. Use `$prompter` or select the skill if your interface does not accept that text.

1. Prompter considers the request and relevant conversation context.
2. It shows one prompt, such as **AP1.v1**, a model/reasoning recommendation, and a brief reason; then asks for approval.
3. Reply **“I approve”** to execute, request a revision, or say **“Cancel.”**
4. Approved work continues in the same conversation.

Revisions receive a new version and require approval of that version. Approval of a completed prompt does not rerun its work. Ordinary messages outside an active workflow are handled normally.

## Model recommendation

Each ready prompt includes a **recommended model**, **supported reasoning effort**, and **one-sentence reason**. Selection considers required capabilities and quality first, then cost and speed. There is no fixed model list; unverifiable model/access information produces a conditional recommendation or a required capability profile.

Select the recommended model in the interface if you want to use it. **Saying “I approve” does not automatically change the model; execution uses the current environment.** If you require a particular model, or the current model is known to lack a required capability, the skill does not silently continue under an unmet condition. The recommendation is not a measured cost or accuracy guarantee.

## How it controls unnecessary work

The prompt preserves the requested outcome, source authority, constraints, and sufficient verification. It avoids automatic extra reports, broad scans, extra agents, and repeated passing checks. Short tasks receive short prompts; a request for a detailed deliverable retains the required detail.

There is no measured guarantee of token savings or an enforceable token ceiling. The workflow itself adds drafting and approval overhead, which can be significant for very small tasks. It does not automatically change your model or account settings. Approval covers the displayed task; existing host permissions still apply.

## Files and versions

- [SKILL.md](SKILL.md): current instructions and version metadata.
- [UI metadata](agents/openai.yaml): display name, description, and default invocation.
- [Behavior checks](references/behavior-checks.md): maintenance scenarios, not a claim that every scenario has passed on every host.
- [Sources](references/source-notes.md): design references and limitations.
- [Model-selection notes](references/model-selection.md): capability, quality, and economy criteria.
- [Changelog](CHANGELOG.md) and [archived releases](archived/README.md).
- [GPL-3.0 license](LICENSE).

The current version lives here, not under a `latest/` or version-number directory. Older published versions are immutable ZIP snapshots in `archived/`. Do not extract them inside a directory scanned for skills.
