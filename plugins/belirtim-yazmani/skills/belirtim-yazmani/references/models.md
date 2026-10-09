# Provider-local model and cost evidence

Read only for an observed provider catalog or a model/cost question. Profile selection never changes model or host settings.

## Provider-local model suggestions

Use the current provider/host's observed model catalog. The private `model_suggestion` refers only to the current host and is `recommendation_only`; catalog observation is availability metadata, not an inference call or confirmed account access. Keep `recommended_model`, `recommended_effort`, available capability and `effective_model` separate. Plugin Max/Ultra are not model reasoning values or a Claude Ultracode toggle. No automatic provider/model/settings switch is authorized by choosing a profile. Model suggestions and cost telemetry are private and never enter the developer ZIP.

| Profile | Codex writer suggestion, when available | Claude writer suggestion, when available |
| --- | --- | --- |
| Lite | gpt-6.1-sol / medium | claude-sonnet-5-5 / medium |
| Plus | gpt-6.1-sol / medium; high for uncertain boundaries | claude-sonnet-5-5 / high |
| Pro | gpt-6.1-sol / high | claude-sonnet-5-5 / high; Opus high for difficult contradictions |
| Max | gpt-6.1-sol / xhigh; gpt-6-astra / high for difficult contradictions | claude-opus-5-5 / high; xhigh for critical probes |
| Ultra | gpt-6-astra / high–xhigh; reassess gpt-6.1-sol / max if unavailable | claude-opus-5-5 / xhigh; claude-fable-5-1 only when observed and justified |

These are the approved design's initial role suggestions, not current account access or quality measurements. Baseline final readers use Sol/high or Sonnet/high when available; stronger critical readers require a reason. Smaller models may do bounded extraction/triage, with returned evidence checked by the writer. Do not silently delegate final acceptance to an unqualified cheaper model. Deterministic hashes/schema/links/inventory need no LLM. Respect product/API reasoning differences and aliases; unknown access/support stays UNKNOWN.

Optimize cost per accepted correct handoff: read unchanged sources once, use check-plan's bound unchanged units, delay final readers until business/reference closure, and give preparation agents narrow packets. Record actual input/output/cache/reasoning tokens, wall time, failed calls and rework only when telemetry exists. An estimated token budget is not an enforced hard limit. Hook contract tests, isolated package discovery and synthetic profiles do not prove provider cost, native routing, hook execution, vision or SAP runtime. Compare profiles against the same quality floor before claiming improvement.
