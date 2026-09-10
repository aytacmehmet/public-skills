# Interruption and revision state

Read for interruptions, partial results, uncertain external operations, or edited writing blocks. Do not create state files, logs, or hashes for simple tasks.

When necessary, keep a compact conversation record: task/version, full approved text, state, completed steps, pending step, and any operation reference. Do not print it on every message. States: drafting, awaiting approval, executing, paused, outcome unknown, completed, cancelled.

| State | Next behavior |
| --- | --- |
| Text/scope revision | Do not carry old approval forward; show the full new version and await approval. |
| Model-note-only change or explanation | Preserve prompt text and AP version; an explanation is not approval. |
| User edited a writing block | Use the latest text supplied by the environment. If it changed, show a revision; do not treat the old copy or unseen edits as approved. |
| Paused work, “continue” | Preserve valid approval and completed steps; resume only remaining work. Obtain approval for new scope. |
| Request sent, outcome unknown | A timeout does not prove failure. Query by operation reference/idempotency key when available; do not repeat writes/submissions without resolving the result. If querying is impossible, explain the uncertainty and required user decision. |
| Completed or cancelled | Repeated approval does not rerun the task. An explicit new repeat task receives a new AP identifier. |
| Full text/approval lost | Do not continue from a guess; show a concrete scope from available evidence and obtain approval. |

Report observed operation results, not intentions. Do not rerun completed steps to create an appearance of success. This instruction-only skill contains no persistent execution ledger, automatic model switcher, or external-operation controller; these require a separate, verified integration.
