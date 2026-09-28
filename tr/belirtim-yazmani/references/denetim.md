# Mechanical validation and indicator

Generated file (source: assets/tanim.json). When code can run, `scripts/bv.py denetle` is authoritative; otherwise the list below is applied by hand.

## Scoring engine rules (mechanical counterparts)

| Rule | Requires | Weight | Severity | Section |
|---|---|---|---|---|
| GEN_001 | No template placeholder text left | 3 | warning | all |
| GEN_002 | Section sufficiently filled | 3 | warning | all |
| SCOPE_000 | At least one scope dimension stated | 3 | warning | 2.5 |
| SCOPE_001 | Scope boundary drawn | 4 | warning | 2.5 |
| SCOPE_002 | All three scope dimensions stated | 2 | info | 2.5 |
| ERR_001 | Message type is clear | 4 | warning | 5.1 |
| ERR_002 | More than one error situation handled | 3 | warning | 5.1 |
| ERR_003 | Message list is a table | 2 | info | 5.1, 5.4 |
| ALGO_001 | Algorithm names concrete SAP objects | 8 | error | 3.5 |
| ALGO_002 | Processing logic split into steps | 4 | warning | 3.5 |
| ALGO_003 | No vague phrases | 3 | warning | 3.5 |
| MAP_001 | Field mapping is concrete | 6 | warning | 3.4 |
| TEST_001 | Test data is concrete | 4 | warning | 6.1 |
| TEST_002 | Error / negative scenario present | 3 | warning | 6.1 |
| PROC_001 | Target process free of vague phrases | 3 | warning | 2.2 |
| PROC_002 | Current process states a concrete problem | 3 | warning | 2.1 |
| AUTH_001 | Authorization check is concrete | 3 | warning | 5.2, 5.3 |
| OBJ_001 | Object names given | 2 | info | 4.1 |
| SAP_001 | Used objects are defined in the catalog | 4 | warning | 4.1 |
| SAP_002 | Catalog objects are used in the document | 2 | info | 4.1 |
| SAP_003 | Object names resolve to an SAP type | 3 | warning | 4.1, 4.2, 4.3 |
| SAP_004 | Naming and length rules followed | 2 | warning | 4.1, 4.2, 4.3 |
| OPEN_001 | Open points clarified | 2 | info | 7.3 |

Legacy engine rules (reported separately, not part of the indicator): META_001 Development type selected (1.1) · META_002 OData version for Fiori (1.2) · FILL_001 Section minimum fill (Tümü) · FILL_002 Mandatory section left empty (Tümü) · COND_001 3.3 for Fiori (3.3) · COND_002 3.4 for API/interface (3.4) · COND_003 3.2 for report (3.2) · COND_004 ALV output for report (3.6) · COND_005 4.4 for form (4.4) · CONT_001 Algorithm has at least 3 items (3.5) · CONT_002 At least 2 test scenarios (6.1) · CONT_003 Open points clarified (7.3) · CONT_004 Out of scope stated (2.5) · QUAL_001 Algorithm names concrete SAP object (3.5) · QUAL_002 Data mapping table (3.4) · QUAL_003 As-Is/To-Be vague phrase (2.1, 2.2) · QUAL_004 Test with concrete data (6.1) · QUAL_005 At least one error/edge case (6.1) · QUAL_006 Error message type (E/W/I) (5.1) · QUAL_007 Dependency/Assumption/Out of scope, all three (2.5).

## The skill's own checks

| Rule | Severity | What it checks |
|---|---|---|
| YAPI_001–009 | error / warning | Schema version, type and profile, undefined section or field, row length, option values, id format, duplicate id |
| KRITIK_001 | error | A critical section cannot be switched off |
| ZINCIR_001 | error | Every cited id must be defined |
| ZINCIR_002 | warning | Every REQ needs at least one SC, STEP and TC |
| UYD_001 | error | An SAP standard object name must appear in the inputs or the project catalog, or be marked `[DOĞRULANACAK]` |
| UYD_002 | warning | Objects to verify need an open point in 7.3 |
| KARAR_001 | warning | A BEKLİYOR marker must carry an OPEN-nn |
| KARAR_002 | warning | An open point cited by a KARAR marker needs a readiness category |
| OPEN_001 | warning / info | An open point needs an owner (name or role; a defect). Rows without a target date count as waiting for input |
| OPEN_002 | warning | 7.3 'Etkilediği bölüm' must contain section numbers valid in this document |
| ZINCIR_003 | info | Every message of type E or A needs a test case |
| YAPI_010 | warning | meta, surum_gecmisi and onaylar cells must be filled (— when none) |

## Defects and waiting for input

`denetle` returns two kinds of result. **Defect**: a finding caused by the writing, to be fixed. **Waiting for input**: the rule fails only because a cell waits for a decision or a fact; the indicator counts it, but there is nothing to fix and no content is invented. The exit code is 1 only for defect-level errors.

## Manual checklist (when code cannot run)

1. No `«…»`, TBD, TODO or empty cell; `—` when none.
2. 2.5 has Bağımlılık, Varsayım and Kapsam dışı; the scope boundary is written.
3. 2.1 has a problem step marked 'Evet' with a numeric effect.
4. No vague phrases in 2.2 and 3.5.
5. 3.5 has at least 3 steps; most steps name an SAP object; error → MSG and commit/rollback are written.
6. Every 3.4 row has source, target, type and example value.
7. 5.1 has at least 2 rows; type E/W/I/S/A.
8. 6.1 has at least 2 cases; at least one Negatif or Sınır; the test data contains real-format numbers.
9. 5.2 / 5.3 rows have object, field-value, activity and catalog names.
10. Every object named in other sections is in 4.1; every 4.1 name appears in another section; the type is from the list; Z names follow the rule.
11. Every cited id is defined; every REQ has SC, STEP and TC.
12. Every BEKLİYOR marker and every `[DOĞRULANACAK]` maps to a 7.3 row; open rows have an owner (name or role) and affected section numbers.

## Indicator

Computed from mechanical rules only; the real engine scores quality (LLM part). A by-product, not a target.

- Section rule score = 100 × (1 − remaining rule weight / evaluated rule weight); `info` rule × 0.5; at most 40 when an `error` rule remains.
- Average = weighted average over applicable base sections and written bonus sections.
- Penalties: every critical section below 40 −5; if the 2 lowest base sections are 30+ below the average −5, 45+ below −7.5 (at most −15); every categorised open point in 7.3 −2 (at most −5 per item, −20 in total).
- Bands: ≥ 85 Geliştirmeye hazır · 70–84 Koşullu · < 70 Revizyon.
- Thresholds and coefficients are assumptions made without seeing the scoring engine's code; they exist for the indicator, not as a target.
