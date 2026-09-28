# Changelog

## 1.1.0 — 2026-09-28

- Model-facing text is English in both language packages: the `SKILL.md` body of `tr/belirtim-yazmani` is now the same English instruction set as `en/spec-writer` (only name, description triggers and the default user language differ); the guidance prose in `assets/tanim.json` (purpose, rule, hints, good practice, rule titles, readiness categories, profiles), the generated references, `soru-setleri.md` and `sap-sozluk.md`, and the messages, help texts and comments of `bv.py`, `derle.py` and `oz_test.py` are English.
- The document content model stays Turkish by design: section titles, field labels, column names, option values, markers (`KARAR BEKLİYOR`, `BİLGİ BEKLİYOR`, `[DOĞRULANACAK]`), EARS patterns, good/bad example cells and the rendered documents are unchanged. The validation appendix inside a rendered document now carries English validator messages.
- Behavior unchanged; self-test 14/14 in both packages. Archived 1.0.0.

## 1.0.0 — 2026-09-20

- First public release. For an SAP Cloud ERP development whose decisions are made, it first produces a validated JSON content file and then renders the requested output: Word, Excel, a single Markdown file, or an Obsidian vault.
- Content model: 32 sections in 7 groups (base weight 119, bonus 35, 9 critical sections), `PREFIX-nn` IDs and the chain REQ → SC → STEP → OBJ / MAP / MSG → TC. The single source is `assets/tanim.json`; the references, the JSON schema and the shape block in the instructions are generated from it by `scripts/derle.py`.
- `scripts/bv.py` (standard library only): `bilgi`, `iskelet`, `eksik`, `denetle`, `yama`, `ozet`, `dok`. Validation separates a **defect** to fix from a finding that only **waits for input** because a cell waits for a decision or a fact; it catches SAP standard object names that appear neither in the inputs nor in the project catalog; it derives the 6.2 traceability matrix from the references.
- Documentation only: it makes no design decision. A missing decision is written as `KARAR BEKLİYOR (OPEN-nn)`, a missing fact as `BİLGİ BEKLİYOR (OPEN-nn)`, an unverified SAP name as `[DOĞRULANACAK]`, each linked to section 7.3.
- The mechanical indicator is a by-product, not a target; it computes the rule part only.
- Two ways to run: bundle mode (with the scripts) and text mode (`SKILL.md` alone; JSON and Markdown).

Earlier public versions: none.
