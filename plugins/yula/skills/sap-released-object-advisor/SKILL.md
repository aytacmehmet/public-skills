---
name: sap-released-object-advisor
description: Identify or explain a released SAP Public Edition object for a capability. Use developer for signatures, ABAP code or call examples.
metadata:
  version: "1.4.1"
---

R-YRA-01 Read [contract](../../references/evidence.md) once.

R-YRA-02 Resolve intent, operation and any exact identity from the request. Preserve technical identifiers; normalize retrieval intent to English when the user's language lacks stored aliases.
R-YRA-03 Exact type/name -> `yula_get(kind="object",objectType=...,key=...)`. Unknown type/name -> `yula_search(domain="objects",query=...,limit=5)`; retrieve only the selected candidate. An exact name search preserves all matching types.
R-YRA-04 `curated_mapping` binds a stored alias to a capability. `lexical_candidate` and `exact_identity` do not prove the requested operation. Retrieve the selected `members` for inputs, outputs, usage warnings or uncertain operation; `declaration` resolves remaining contract gaps. Catalog-only fallback discovers identities, not semantics.
R-YRA-05 Answer: supported object/member + purpose + essential prerequisite + material evidence gap. Use the user's language; preserve SAP names. Code/signature requests belong to developer. Stop when the question is answered; reuse existing evidence.

R-YRA-06 Missing/stale evidence -> name the gap. Load [maintenance](../../references/maintenance.md) only for a requested refresh or storage fault, not every lookup.
