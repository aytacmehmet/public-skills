# Persistent knowledge records

R-YKR-01 Persist useful new evidence, not every lookup. Prepare a UTF-8 JSON **array** and import it through `knowledge-records` using check → hash-bound apply. Revisions are immutable: the same ID/release/revision cannot change; new revisions must increase. Earlier revisions remain in `yula_records`; the current searchable projection selects the latest accepted revision.

R-YKR-02 Required common fields:

```json
{
  "kind": "research",
  "id": "activity-100274-context",
  "release": "2608",
  "revision": 1,
  "title": "Configure Matching and Duplicate Check: scoped evidence",
  "status": "researched",
  "activityId": "100274",
  "summary": "An original evidence-backed explanation of the specific context.",
  "sources": [{
    "id": "official-source-id",
    "url": "https://help.sap.com/docs/SAP_S4HANA_CLOUD",
    "checkedAt": "2026-09-23T00:00:00Z",
    "claim": "Replace this example with the exact claim supported by the page actually read."
  }]
}
```

R-YKR-03 The example demonstrates structure, not validated research. Supply the actual topic URL and observed checked date. Supported kinds: `research`, `dependency`, `incident`, `lesson`, `whats_new`. Release is four digits. IDs use letters/digits/underscore/dot/colon/hyphen. Bound imports to 1000 records and 8 MiB.

R-YKR-04 **Research:** `activityId`, official source, summary and only relevant dossier fields (`purpose`, `prerequisites`, `access`, `procedure`, `transport`, `tests`, `risks`, `rollback`, `whats_new`). Sources carry ID, URL, timezone-aware checked date and supported claim; future dates beyond five minutes of clock skew are rejected. Community pages alone cannot satisfy a primary-source gate. `validated` additionally requires `verification` evidence; do not equate source presence with runtime proof.
R-YKR-05 **Dependency:** `sourceActivityId`, `targetActivityId`, `relation`, `evidenceLevel`, condition/reason. Conditional edges require a condition. Confirmed edges require official evidence plus explicit verification. Confirmed status must also have confirmed evidenceLevel. A new research revision replaces its active source links while prior revisions remain immutable. Preserve direction. Common relations: `must_precede`, `recommended_before`, `required_if`, `defines_key_for`, `assigns_object_from`, `determines_behavior_of`, `mutually_exclusive_with`, `requires_manual_rework_in_p`, `requires_current_setting`, `requires_expert_configuration`, `requires_business_catalog`, `supersedes`, `split_into`.
R-YKR-06 **Incident:** `activityIds`, symptom/context, hypotheses, root cause, resolution and verification. `verified`/`closed` require explicit verification evidence. Record failed/inconclusive outcomes rather than silently treating them as solutions.
R-YKR-07 **Lesson:** `activityIds`, applicability, rootCause, resolution, verification, rollback and status. Validation requires an official source plus one successful case, or two independent successful cases plus `architectReviewed=true`. `verification`, `successfulCases` and `activityIds` are bounded lists of nonempty strings. Case IDs belong in `successfulCases`. These are recorded operator assertions, not tests executed by Yula. Unproven lessons remain `candidate`.
R-YKR-08 **What's New:** `activityIds`, `changeType`, `validFrom`, official source, summary and impact. Importing a change flags related activities for review. A stored change entry is not a complete current-release search.

R-YKR-09 Supported states: candidate, researched, reviewed, validated, confirmed, stale, contradicted, deprecated, superseded, rejected, observed, diagnosed, fix_proposed, fix_applied, verified, closed, failed, inconclusive. Use a state appropriate to the kind; never promote evidence merely to satisfy a schema. Preserve contradictory conditions and provenance in a new revision.

R-YKR-10 No business documents, people, tenant identifiers, usernames, cookies, secrets or implementation source. The importer rejects credential fields and sanitizes known transport identifiers; the author still owns semantic redaction. This is local corpus maintenance, not permission for any SAP mutation.
