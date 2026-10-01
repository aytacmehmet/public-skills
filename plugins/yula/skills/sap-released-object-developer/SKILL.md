---
name: sap-released-object-developer
description: Retrieve public signatures or produce ABAP Cloud code/call context for released SAP Public Edition objects. Use advisor for purpose-only questions.
metadata:
  version: "1.4.1"
---

R-YRD-01 Read [contract](../../references/evidence.md) once.

R-YRD-02 Resolve operation and identity. Search only when identity is unknown.
R-YRD-03 Exact member -> `yula_get(kind="object",objectType=...,key=...,section="members",member=...)`. This response already checks catalog eligibility and includes provenance/usage constraints; do not precede it with redundant summary/check calls.
R-YRD-04 Batch-check additional SAP dependencies with `yula_check`. Do not speculate about unused dependencies. Retain the response `snapshot` across related checks/pages.
R-YRD-05 Missing/truncated signature -> follow the explicit gap or `declaration` pagination. Verify parameter direction/type, optionality, exceptions, transaction/save phase and operation from the public contract. Never invent a member or infer writes from read support.
R-YRD-06 Return the smallest sufficient call context or code. `REVIEW_REQUIRED` -> draft + concrete target verification gaps. `FAIL` -> reject dependency; inspect an official successor. Respond in the user's language; retain technical identifiers.

R-YRD-07 Yula does not execute or mutate SAP. For authorized corpus maintenance read [maintenance](../../references/maintenance.md). Native system refresh is CLAS/INTF metadata only and never refreshes public signatures.
