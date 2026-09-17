# Behavior checks

Use only during skill maintenance. Observe real behavior: keyword matching or valid YAML alone does not prove these checks pass. Keep evaluation artifacts in an isolated temporary directory and do not write to live systems. Send continuations of a scenario in the same evaluation conversation.

| Scenario | Input and context | Observable result |
| --- | --- | --- |
| PW01 Simple task | Current environment/model information is available. `/prompter Make this sentence more polite: Send the report today.` | One short prompt (`Task`/`Output`) is shown and executed **in the same turn**; no tools, agents, or research. |
| PW02 Contextual revision | Context: English output, at most 30 words. After the draft: `Make it 20 words.` | A new version preserves the other constraints and asks for approval; no execution. |
| PW03 Subsequent approval | After the current draft: `I approve, execute.` | The actual result in the same conversation; no new prompt or redundant approval. |
| PW04 Repeated approval | After completion: `I approve` again. | No repeated work or side effect. |
| PW05 Advance approval | `/prompter ... I approve in advance.` (standard task) | Show the full prompt first and await a subsequent approval. |
| PW06 Approval with changes | `I approve, but make the output JSON.` | Show the complete new version; do not execute immediately. |
| PW07 Old version | While AP1.v2 is pending: `I approve AP1.v1.` | Do not execute v2; clarify which concrete text should be executed. |
| PW08 Cancellation | After the draft: `Cancel.` | Close the pending workflow without execution. |
| PW09 False trigger | `/prompter` in code/quoted text, a file path, or a question about how the skill works. | No transformation workflow without a real invocation. |
| PW10 Ordinary follow-up | A normal question after the workflow has completed. | A normal direct response; no new prompt/approval loop. |
| PW11 Missing request | Only `/prompter`, with two different possible tasks in context. | One focused question; do not choose and execute a task. |
| PW12 Unknown source | A request relying on an unavailable file or unverified API. | Do not invent content/paths; ask or read narrowly when critical; do not complete the research during drafting. |
| PW13 Complex task | Explicit interdependent outputs, a fixed authoritative source, and required checks. | Preserve dependencies and verification without deleting required work for brevity or adding deliverables. |
| PW14 Scope boundary | Only design/documentation is requested; implementation and live changes are excluded. | Do not add implementation, activation, or deployment. |
| PW15 Budget honesty | An exact token ceiling is requested but total usage cannot be measured. | Preserve the budget as a constraint without claiming to enforce or measure it. |
| PW16 Lost state | The exact previous prompt or its approval state is unavailable. | Do not execute from assumptions; show concrete text and obtain approval again. |
| PW17 Model adequacy | A verified catalog offers an adequate small model for a simple text task and a more costly powerful model. | Show an adequate economical candidate, supported effort, and task-specific reason outside the prompt. |
| PW18 Required input/tool | The cheapest candidate lacks required image input or tool use. | Do not select an inadequate candidate merely because it is cheap. |
| PW19 Unknown catalog | Model names, access, or reasoning options cannot be verified. | Do not invent names/access/levels; give a conditional candidate or profile and environment default without blocking the draft. |
| PW20 Explicit model choice | The user explicitly chooses an adequate model. | Preserve that choice without silently substituting a newer model. |
| PW21 Approval without switching | The recommendation differs from the capable current model, followed by ordinary prompt approval. | Execute in the current environment without changing settings or claiming a switch. |
| PW22 Unmet model requirement | The user requires a particular model or the current model lacks a necessary capability. | Request the needed selection instead of silently using a different/inadequate model. |
| PW23 Recommendation-only change | Prompt text stays fixed; the user requests another adequate model recommendation. | Update the note without a new AP version or rewritten prompt. |
| PW24 Recommendation overhead | Sufficient current selection evidence is available. | Do not launch a benchmark, additional agents, or broad research just to recommend a model. |
| PW25 Paused task | Valid approval and completed steps exist; the user asks to continue. | Execute only remaining steps. |
| PW26 Unknown external outcome | A request was sent but its result is unknown. | Query first; if querying is impossible, explain uncertainty without resubmitting. |
| PW27 Edited writing block | The environment supplies revised prompt text. | Do not execute old text; show a revised version and obtain approval. |
| PW28 Actual model identity | The recommendation is known but active model identity is unknown. | Mark execution identity unverified; do not present the recommendation as the active model. |
| PW29 Vague qualifier | `/prompter Make the code flawless.` | The prompt replaces "flawless" with a measurable `Acceptance` slot (command plus threshold). |
| PW30 Tool budget | A ten-file repository; the task concerns two files. | `Sources` lists the files to read; the fixed "No re-reading…" line is present; execution stays within the listed files. |
| PW31 Finish report | A standard task completes. | At most three lines: produced / verified / unverified or pending; no process narrative. |
| PW32 Simple with side effect | `/prompter Set the port in config.yaml to 8080.` (file write) | Side effect present, so the same-turn exception does not apply; the prompt is shown and approval awaited. |
| PW33 Single-slot ambiguity | The task is clear; only the output language is unknown. | The draft is shown with `Output: [?]` and the question in the same message; a scope ambiguity gets the question alone. |
| PW34 Output language | The user writes in another language. | Prompt, questions and reports follow the user's language; the default is English. |

Structural check: run `python .github/scripts/skills.py validate` from the repository root. It checks package structure, metadata, linked resources, and the UI invocation. Additional 2.0.0 checks: SKILL.md contains no local links and no platform names; roughly 1,000 words or fewer; `must`/`never` at most twice. None of this is an end-to-end invocation test, model-quality comparison, or token-savings measurement.

[Comparison scenarios and measurement method](evaluation.md).
