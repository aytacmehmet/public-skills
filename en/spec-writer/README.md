# Spec Writer

[English catalog](../README.md) · [Türkçe: Belirtim Yazmanı](../../tr/belirtim-yazmani/README.md)

Writes the FS-TS (functional + technical specification) for an SAP Cloud ERP development whose decisions are already made. It first produces a validated JSON content file and then asks which output you want: Word, Excel, a single Markdown file, or an Obsidian vault. Documentation only: it does not choose the approach, technology, extension point or API. A missing decision or fact is not filled with a guess; it is marked and linked to section 7.3 (open points).

## Languages and installation

The instructions and this introduction are in English. The [Turkish counterpart](../../tr/belirtim-yazmani/README.md) offers the same behavior with Turkish instructions. Scripts, the definition file, examples and references are byte-identical in both packages. The content model of the generated document (section titles, column names, markers, script commands and messages) is intentionally Turkish; SAP terms stay in English. Use this package when you want English instructions for a Turkish FS-TS.

If Skill Installer is available:

```text
Use $skill-installer to install the skill at https://github.com/aytacmehmet/public-skills/tree/main/en/spec-writer.
```

Alternatively, copy only this skill folder to the skill discovery location your environment supports. Do not install the English and Turkish packages together; they trigger on the same work under two names.

The core script uses only the Python 3.11+ standard library. Word rendering needs `python-docx`, Excel rendering needs `openpyxl`; without them JSON, Markdown and the vault are still produced. Where code cannot run, the skill works from `SKILL.md` alone: it builds the JSON and Markdown by hand and says that it cannot create .docx or .xlsx.

The package ships no logo. For a logo on the cover and in the header, place your own PNG at `assets/logo.png` or pass `dok --logo file.png`.

## Usage

```text
Use $spec-writer to write the FS-TS from the attached development request and meeting notes. Project profile: proje.json.
```

```text
Use $spec-writer to validate spec.json and render it as Word and as an Obsidian vault.
```

## How it works

```text
inputs + proje.json ─> one question round ─> spec.json ─> validate ─> report ─> "which output?" ─> docx | xlsx | md | vault
                                              (bv.py iskelet, bilgi, yama)  (defect / waiting for input)   (bv.py dok)
```

- **Content model:** 32 sections in 7 groups; each section's weight, class (critical, normal, bonus) and applicable RICEF types live in `assets/tanim.json`. The references, `assets/icerik-semasi.json` and the shape block in the instructions are generated from it by `scripts/derle.py`.
- **Profile:** `hafif`, `standart`, `tam` only decide which bonus sections open.
- **Markers:** a missing decision is `KARAR BEKLİYOR (OPEN-nn)`, a missing fact `BİLGİ BEKLİYOR (OPEN-nn)`, an SAP standard name found neither in the inputs nor in the project catalog `[DOĞRULANACAK]`. Each one maps to a 7.3 row.
- **Validation:** `bv.py denetle` separates defects to fix from rules that fail only because a cell waits for a decision or a fact. It checks that every cited ID exists, that every REQ has an SC, STEP and TC, that the 4.1 object catalog is consistent and that names follow the naming rules; it derives the 6.2 traceability matrix.
- **Project profile:** naming rules and the verified SAP object catalog stay outside the skill, in the project (`assets/proje-ornek.json` is a sample).

## Verification and limits

```text
python -B scripts/oz_test.py
```

The self-test covers the freshness of the generated files, the totals of the definition file, a clean pass of the example content, detection of the expected rules in a mutated copy, the skeleton and patch commands, and the four renderers (a renderer is skipped when `python-docx` or `openpyxl` is missing).

The mechanical indicator computes the rule part only; weights, thresholds and penalties are assumptions stored in `assets/tanim.json` and should be adapted to your own scoring criteria. It does not measure content quality. The validator cannot see an asserted default (for example an unfounded `Must`); that rule is left to the model in the instructions. It does not verify SAP object names in a system: it only checks whether they appear in the inputs or the project catalog. The skill does not connect to an SAP system, write code or estimate effort.
