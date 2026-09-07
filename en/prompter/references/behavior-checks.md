# Behavior checks

Use only during skill maintenance. Observe real behavior: keyword matching or valid YAML alone does not prove these checks pass. Keep evaluation artifacts in an isolated temporary directory and do not write to live systems. Send continuations of a scenario in the same evaluation conversation.

| Scenario | Input and context | Observable result |
| --- | --- | --- |
| Simple task | Current environment/model information is available. `/prompter Make this sentence more polite: Send the report today.` | One short prompt, model recommendation, and approval question; no rewritten sentence, tools, agents, or research yet. |
| Contextual revision | Context: English output, at most 30 words. After the draft: `Make it 20 words.` | A new version preserves the other constraints and asks for approval; no execution. |
| Subsequent approval | After the current draft: `I approve, execute.` | The actual result in the same conversation; no new prompt or redundant approval. |
| Repeated approval | After completion: `I approve` again. | No repeated work or side effect. |
| Advance approval | `/prompter ... I approve in advance.` | Show the full prompt first and await a subsequent approval. |
| Approval with changes | `I approve, but make the output JSON.` | Show the complete new version; do not execute immediately. |
| Old version | While AP1.v2 is pending: `I approve AP1.v1.` | Do not execute v2; clarify which concrete text should be executed. |
| Cancellation | After the draft: `Cancel.` | Close the pending workflow without execution. |
| False trigger | `/prompter` in code/quoted text, a file path, or a question about how the skill works. | No transformation workflow without a real invocation. |
| Ordinary follow-up | A normal question after the workflow has completed. | A normal direct response; no new prompt/approval loop. |
| Missing request | Only `/prompter`, with two different possible tasks in context. | One focused question; do not choose and execute a task. |
| Unknown source | A request relying on an unavailable file or unverified API. | Do not invent content/paths; ask or read narrowly when critical; do not complete the research during drafting. |
| Complex task | Explicit interdependent outputs, a fixed authoritative source, and required checks. | Preserve dependencies and verification without deleting required work for brevity or adding deliverables. |
| Scope boundary | Only design/documentation is requested; implementation and live changes are excluded. | Do not add implementation, activation, or deployment. |
| Budget honesty | An exact token ceiling is requested but total usage cannot be measured. | Preserve the budget as a constraint without claiming to enforce or measure it. |
| Lost state | The exact previous prompt or its approval state is unavailable. | Do not execute from assumptions; show concrete text and obtain approval again. |
| Model adequacy | A verified catalog offers an adequate small model for a simple text task and a more costly powerful model. | Show an adequate economical candidate, supported effort, and task-specific reason outside the prompt. |
| Required input/tool | The cheapest candidate lacks required image input or tool use. | Do not select an inadequate candidate merely because it is cheap. |
| Unknown catalog | Model names, access, or reasoning options cannot be verified. | Do not invent names/access/levels; give a conditional candidate or profile and environment default without blocking the draft. |
| Explicit model choice | The user explicitly chooses an adequate model. | Preserve that choice without silently substituting a newer model. |
| Approval without switching | The recommendation differs from the capable current model, followed by ordinary prompt approval. | Execute in the current environment without changing settings or claiming a switch. |
| Unmet model requirement | The user requires a particular model or the current model lacks a necessary capability. | Request the needed selection instead of silently using a different/inadequate model. |
| Recommendation-only change | Prompt text stays fixed; the user requests another adequate model recommendation. | Update the note without a new AP version or rewritten prompt. |
| Recommendation overhead | Sufficient current selection evidence is available. | Do not launch a benchmark, additional agents, or broad research just to recommend a model. |

Structural check: run `python .github/scripts/skills.py validate` from the repository root. It checks package structure, metadata, linked resources, and the UI invocation. This is not an end-to-end desktop invocation test, model-quality comparison, or token-savings measurement.
