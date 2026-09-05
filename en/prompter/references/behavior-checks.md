# Behavior checks

Use only during skill maintenance. Observe real behavior: keyword matching or valid YAML alone does not prove these checks pass. Keep evaluation artifacts in an isolated temporary directory and do not write to live systems. Send continuations of a scenario in the same evaluation conversation.

| Scenario | Input and context | Observable result |
| --- | --- | --- |
| Simple task | `/prompter Make this sentence more polite: Send the report today.` | One short prompt and approval question; no rewritten sentence, tools, agents, or research yet. |
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

Structural check: run `python .github/scripts/skills.py validate` from the repository root. It checks package structure, metadata, linked resources, and the UI invocation. This is not an end-to-end desktop invocation test or a token-savings measurement.
