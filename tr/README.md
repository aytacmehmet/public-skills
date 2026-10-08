# Türkçe skill'ler

[English](../en/README.md) · [Depo ana sayfası](../README.md) · [Katkı ve sürüm yönetimi](CONTRIBUTING.md)

| Skill | Ne yapar? | İngilizce karşılığı |
| --- | --- | --- |
| [Yordamla](yordamla/README.md) | Bağlama uygun prompt üretir, yürütme modeli önerir, onay ister ve aynı sohbette uygular. | [Prompter](../en/prompter/README.md) |
| [SAP Fiori Tasarım](sap-fiori-tasarim/README.md) | SAP Fiori for Web ekranı tasarlar, ABAP paketini (isteğe bağlı olarak servis `$metadata`'sını da) kanıtlı sözleşmeye çevirir; aynı sözleşmeden UI5 prototipi, kayıtlı PNG'ler ve üretim kodu üretir. | [SAP Fiori Design](../en/sap-fiori-design/README.md) |

Her skill klasöründe en güncel yönerge, tanıtım, arayüz bilgileri, gerektiğinde destek kaynakları, değişiklik geçmişi ve kendi `archived/` klasörü bulunur. Güncel sürüm `SKILL.md` içindeki `metadata.version` alanında kayıtlıdır.

Dil klasörünün tamamı yerine istediğiniz skill'in kendi klasörünü kurun. Kurulum adımları skill tanıtımında bulunur. Eski sürüm ZIP'leri inceleme ve geri dönüş hazırlığı içindir; aktif skill değildir.

Türkçe ve İngilizce karşılıklar aynı sürümü ve davranışı paylaşır; adlar, açıklamalar ve belgeler ilgili dilde yazılır. Yönergeler çoğunlukla yerelleştirilir; SAP Fiori Tasarım çiftinde modele dönük metin iki pakette İngilizcedir. Bu çift de kullanıcının dilinde yanıt verir. Skill eklemeden veya güncelleme yayımlamadan önce [katkı ve sürüm yönetimini](CONTRIBUTING.md) okuyun.

## Tam plugin paketleri

[Yula 1.4.1](../plugins/yula/README.tr.md), Codex ve Claude Code için released object danışmanlığını, ABAP Cloud sözleşmelerini, konfigürasyon mimarisini, dört çevrimdışı MCP okuma aracını ve dolu SQLite veritabanını birlikte sunar. Üç skill ortak dosyalara bağlı olduğundan repo marketplace'inden tam plugin'i kurun. [Plugin katkı kuralları](CONTRIBUTING.md#tam-plugin-paketleri).

[Belirtim Yazmanı 3.1.0](../plugins/belirtim-yazmani/README.tr.md), SAP Cloud ERP geliştirmelerini kendi kendine yeterli TOON FS-TS, danışmanın cevaplayacağı sorular ve koordineli ayrı geliştirme handoff’ları olarak belgeler. Ortak Python/Node runtime ve sabit codec ile tam plugin'i kurun.
