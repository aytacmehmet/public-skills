# Model-selection notes

Use only for complex capability requirements, missing catalogs, or material model tradeoffs. This file is not a model/price list and does not freeze model names or rankings.

## Decision order

1. **User preference:** Preserve required models, budgets, speed, and quality constraints. Flag a known conflict between an explicit model preference and the task; do not silently substitute another model.
2. **Feasibility:** Required image/audio/text input, file and tool support, context limits, and environment access. Do not choose on price or name alone without establishing these. A stronger model does not supply a missing connection or permission.
3. **Sufficient quality:** Uncertainty, dependencies, error impact, and likely rework. Use provided evaluation evidence; a model family name is not an accuracy guarantee.
4. **Economy:** Among adequate candidates, consider known cost, latency, and likely retries. Do not claim “cheapest” without price evidence. Do not create a separate model/agent for every stage or an automatic escalation plan.

## Evidence and recommendation boundaries

The session's current environment catalog establishes available options; official model documentation describes general capabilities. Do not substitute one type of evidence for the other. Treat a user's unverified model list as a user statement. Do not assume a catalog from an old version is still current.

When the catalog is missing, make the recommendation conditional or describe the required capability profile. Use an available `openai-docs` skill for a needed check when appropriate; otherwise consult the official source directly. Reuse evidence that remains valid and preserve higher-priority verification requirements.

## Output and execution

Place the model, supported reasoning effort, and a one-sentence reason outside the prompt. In a separate execution note, identify the verified active model or state that its identity is unverified. Add alternatives only when the primary recommendation is unavailable or the user requests a comparison. Mark uncertainty beside the affected field instead of creating an explanatory report.

Ordinary prompt approval authorizes execution in the current environment. A user who wants the recommended model selects it in the interface. Do not claim the model changed without confirmation. If the user requires a specific model or a required capability is known to be absent, explain the unmet condition and request the necessary user action. For a model-note-only change, do not regenerate the prompt or increment AP; preserve valid text approval.

## Sources

Checked on 2026-09-07:

- [OpenAI — Model selection](https://developers.openai.com/api/docs/guides/model-selection): assess cost and latency among options meeting the quality requirement.
- [OpenAI — Models](https://learn.chatgpt.com/docs/models): environment model/reasoning selection and the time/token impact of higher effort.

These principles do not require a live benchmark for every recommendation. The recommendation is an evidence-based choice, not a measured universal optimum.
