# Configuration diagnosis

R-YDG-01 Use supplied context; do not ask again. Missing context matters when it changes the branch: exact error/message ID, app/operation, target release, landscape, localization/scope, affected roles/organizations, recent transport/upgrade and reproducibility.

R-YDG-02 Search stored lessons with the exact error, then inspect applicability and status. Rank only hypotheses supported by the supplied context or retrieved evidence; do not expand every diagnosis category. Widen the investigation only when an observed result or new evidence warrants another branch.

R-YDG-03 For each material hypothesis keep: supporting evidence, contradicting evidence, the least invasive distinguishing check and its observed result. Start with display/read-only comparison and test-system reproduction. Do not experimentally change production data to diagnose an issue.

R-YDG-04 An opened screen or disappeared message is insufficient. Verification should cover the original failure, positive path, relevant negative case and downstream process; distinguish local analysis, written tests and executed target evidence.

R-YDG-05 Recommend a SAP case when documented standard settings still produce a reproducible defect, an upgrade regresses behavior, SAP expert configuration is required, a protected standard correction is needed, or data consistency cannot be restored through supported means. Include release/component, sanitized steps, actual/expected result, impact and evidence.

R-YDG-06 Persist only useful new evidence under the skill's conditional record procedure. A suggested fix remains a candidate until verified; failed attempts and conflicts must retain their state.
