---
name: sap-configuration-architect
description: Resolve SAP Public Edition SSCUI/CBC configuration, dependencies, errors or release changes using release-specific evidence. No tenant execution.
metadata:
  version: "1.4.1"
---

R-YCA-01 Read [contract](../../references/evidence.md) once.

R-YCA-02 Reuse supplied release, landscape, localization and scope. Ask only when missing context changes the decision. A default release is the latest stored catalog, not SAP's current release.
R-YCA-03 Exact ID -> `yula_get(kind="activity",key=...,release=...)`. Otherwise search `domain="configuration"` with relevant filters, limit 5. Country filtering includes Global/XX applicability.
R-YCA-04 `AMBIGUOUS_ACTIVITY` -> select the correct `sourceRow` using scope/country/component; never choose the first variant arbitrarily. A selected variant does not validate an unbound dossier; retain `VARIANT_DOSSIER_UNVERIFIED`. Preserve `snapshot` for continuation.
R-YCA-05 Retrieve only needed sections: catalog, access, dependencies, changes, sources, lessons, tests or a discovered dossier field. Surface obsolete markers, conflicts, stale evidence and review flags. Current/latest/regression claims require fresh official sources.
R-YCA-06 Answer in the user's language at the requested depth. Catalog category is not project necessity; transaction/IMG references do not prove execution access. Distinguish CBC, transportable configuration, current settings, manual rework and expert configuration.

R-YCA-07 Load a procedure only for its stated condition; do not load all references.
R-YCA-08 Process/sequence/change/transport/handoff: [workflows](../../references/configuration-workflows.md).
R-YCA-09 Error isolation: [diagnosis](../../references/diagnosis.md).
R-YCA-10 Useful new evidence/revisions: [records](../../references/records.md).
R-YCA-11 Requested source refresh/storage migration: [maintenance](../../references/maintenance.md).
