# public-skills

Reusable AI skills, organized by language. Choose a language to browse, install, and maintain skills.

Dillere göre düzenlenmiş, yeniden kullanılabilir AI skill'leri. Skill'leri incelemek, kurmak ve sürümlerini yönetmek için bir dil seçin.

| Language / Dil | Catalog / Katalog | Skills / Skill'ler |
| --- | --- | --- |
| English | [Browse English skills](en/README.md) | [Prompter](en/prompter/README.md), [SAP Fiori Design](en/sap-fiori-design/README.md) |
| Türkçe | [Türkçe skill'leri incele](tr/README.md) | [Yordamla](tr/yordamla/README.md), [SAP Fiori Tasarım](tr/sap-fiori-tasarim/README.md) |

## Complete plugins / Tam plugin paketleri

| Plugin | Version / Sürüm | Documentation / Belgeler |
| --- | --- | --- |
| Yula | 1.4.1 | [English](plugins/yula/README.md) · [Türkçe](plugins/yula/README.tr.md) |
| Belirtim Yazmanı | 3.1.0 | [English](plugins/belirtim-yazmani/README.md) · [Türkçe](plugins/belirtim-yazmani/README.tr.md) |

Install Yula with its shared runtime, MCP server and populated SQLite corpus from the native Codex or Claude Code marketplace. The three plugin skills must stay together. Standalone language packages retain their existing release/archive rules; complete plugins follow the [English](en/CONTRIBUTING.md#complete-plugins) / [Turkish](tr/CONTRIBUTING.md#tam-plugin-paketleri) plugin rules.

Yula'yı ortak runtime, MCP sunucusu ve dolu SQLite veritabanıyla native Codex veya Claude Code marketplace'inden kurun. Üç plugin skill'i birlikte tutulmalıdır. Dil paketlerinin mevcut sürüm/arşiv kuralları devam eder; tam plugin'ler yukarıdaki iki dilde açıklanan plugin kurallarını izler.

```text
.agents/plugins/marketplace.json  ← Codex marketplace
.claude-plugin/marketplace.json  ← Claude Code marketplace
plugins/yula/                    ← complete bilingual plugin
plugins/belirtim-yazmani/         ← complete TOON FS-TS plugin
en/
  README.md
  CONTRIBUTING.md
  prompter/
    README.md          ← current introduction
    SKILL.md           ← current instructions
    agents/
    references/
    archived/          ← previous releases as versioned ZIPs
  sap-fiori-design/
    SKILL.md           ← English instructions; shared scripts and UI5 templates
    scripts/
    assets/
    references/
    tests/
    archived/          ← first public release: guide only
tr/
  README.md
  CONTRIBUTING.md
  yordamla/
    README.md          ← güncel tanıtım
    SKILL.md           ← güncel yönerge
    agents/
    references/
    archived/          ← önceki sürümlerin sürümlü ZIP'leri
  sap-fiori-tasarim/
    SKILL.md           ← Türkçe yönergeler; ortak betikler ve UI5 şablonları
    scripts/
    assets/
    references/
    tests/
    archived/          ← ilk herkese açık yayın: yalnız rehber
```

The latest release always lives directly in its skill folder. Older releases are stored inside that skill's `archived/` folder. Shared repository checks live in `.github/`.

En güncel sürüm doğrudan kendi skill klasöründe bulunur. Eski sürümler aynı skill'in `archived/` klasöründe saklanır. Ortak depo kontrolleri `.github/` altında bulunur.

[License / Lisans: GPL-3.0](LICENSE)
