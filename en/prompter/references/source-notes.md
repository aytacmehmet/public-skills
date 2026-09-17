# Sources and design notes

Sources checked on 2026-09-05. This file is for maintenance; do not reread it or refresh the web sources for every prompt.

- [OpenAI — Prompting](https://learn.chatgpt.com/docs/prompting): describe the goal, context that changes the result, output format, and boundaries without filling a template unnecessarily. For coding work, identify relevant sources and verification expectations.
- [OpenAI — Cost optimization](https://developers.openai.com/api/docs/guides/cost-optimization): reduce necessary requests and input/output size while preserving accuracy. This skill targets execution and rework costs as well as prompt size; it does not present API advice as measured desktop subscription quota savings.
- [OpenAI — Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization): use fewer requests, select relevant context, and avoid unnecessary generation. Latency, token, price, and quota savings are not interchangeable. Batching independent reads does not require multiple agents.
- [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills): use discriminating descriptions, on-demand instructions, and optional references. `$prompter` explicitly invokes the skill; `/prompter` is a description-matched text alias and does not register a custom application menu command.

Discovery and installation paths may vary by Codex surface and version. Follow the [skill introduction](../README.md) and verify discovery in your environment. Do not extract archive ZIPs inside an installed skill directory: older `SKILL.md` files may be discovered separately.

`agents/openai.yaml` preserves the default discovery policy. Setting `allow_implicit_invocation: false` preserves explicit `$` invocation but may weaken discovery of the `/prompter` text alias. SKILL.md defines the usage boundary.

AP identifiers, version-bound approval, task profiles, and revisiting the diagnosis after two unsuccessful attempts are this skill's design choices, not official product guarantees. The profiles have not been measured as optimal and no percentage of token savings has been established. A skill alone cannot enforce an exact total token ceiling.

Model-recommendation sources, checked on 2026-09-07 (introduced in 1.1.0, kept in 2.0.0):

- [OpenAI — Model selection](https://developers.openai.com/api/docs/guides/model-selection): assess cost and latency among options meeting the quality requirement.
- [OpenAI — Models](https://learn.chatgpt.com/docs/models): environment model/reasoning selection and the time/token impact of higher effort.

No fixed model list is maintained; recommendations and actual model selection are separate. Since 2.0.0 the preparation, model-selection and continuation notes live inside SKILL.md as the `<preparation>`, `<model_note>` and `<recovery>` sections; the runtime file links to nothing, and the files in `references/` are maintenance material only.
