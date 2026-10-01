# Conditional configuration workflows

R-YCW-01 Select the requested mode; do not run every workflow.

R-YCW-02 **Process design / Fit-to-Standard:** bound the business outcome, process and subprocess; identify scope/localization, organization, master data and integration dependencies. Map each activity to `foundation_mandatory`, `process_mandatory`, `recommended`, `conditional`, `optional` or `not_applicable` for that context. Distinguish these decisions from the catalog's category. Explain standard gaps with evidence before requesting released-object development context.

R-YCW-03 **Sequencing:** retrieve exact predecessor/successor edges with direction, condition, release and source. Preserve `confirmed`, `strong_inference`, `hypothesis` and lifecycle status. Name similarity is not an edge. `must_precede` needs direct evidence; otherwise state an inferred recommendation. Inspect cycles before producing an execution order. Keep obsolete/superseded identities for historical traceability.

R-YCW-04 **Transport:** resolve 2-system versus 3-system landscape and CBC versus in-system access. Classify each action separately: transportable business configuration; current setting in target systems; manual production rework; SAP expert configuration; CBC scope/org changes; development transport. `Redo in P` is a signal to verify in target-release instructions, not a universal command. Report only the requested classification or constraint unless a full transport plan is requested; for that plan state origin/destination, dependency order, owner, precheck, import, target rework, smoke/regression evidence and rollback/forward-fix.

R-YCW-05 **Change impact:** trace key reuse, assignments, open documents, master data, accounting/tax/numbering, integrations, authorizations and extensions. Assess alternatives before changing irreversible keys or records whose deletion is unsupported. Identify affected activities, dossier/lesson review flags and tests with observable expected results.

R-YCW-06 **Upgrade:** compare the existing requested release partitions; if one is missing, report the gap. Import/refresh only for explicitly requested corpus maintenance, retaining each release as a separate partition. Compare added/removed IDs and changes to name, scope, component, localization, configuration approach, category, redo/deletion/upload and access mapping. Keep catalog differences distinct from official What's New. Do not carry dossier validation into a new release automatically; record explicit revalidation. Check latest-reference-content requirements for the actual landscape.

R-YCW-07 **Expert case / development handoff:** provide exact identity/release, reproducible issue or standard gap, checked official sources, access/scope evidence, sanitized reproduction, expected/actual outcome, impact, safe diagnostics already completed and the required decision. For development, identify the Clean Core boundary and dependency evidence still needed.

R-YCW-08 Deliver only the decision and supporting details needed for the request. Tests are risk-dependent: positive and original failure path, negative/boundary, authorization, integration/downstream and post-transport checks where affected. Written tests are not execution evidence.
