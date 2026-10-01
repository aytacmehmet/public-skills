# Uyarlama mimarı

[English](README.md) · Türkçe

Sürüme özgü SSCUI/CBC aktiviteleri, bağımlılıklar, hata teşhisi ve değişiklik etkisini çözümler. SAP tenant'ında işlem yürütmez.

## Kurulum

**Yula 1.4.1** içinde dağıtılır. [Plugin'in tamamını](../../README.tr.md) kurun; bu skill ortak MCP sunucusuna, kurallara ve SQLite veritabanına bağlıdır. İkinci bir bağımsız kopya kurmayın.

## Kullanım

Otomatik çağırma açıktır. Claude Code'da açık çağrı için `/yula:sap-configuration-architect` kullanın. Codex'te skill seçicisinden Yula skill'ini seçin.

Yanıtlar kullanıcının dilindedir. Teknik tanımlayıcılar değiştirilmez. Model talimatları İngilizcedir; ayrıntılı referanslar yalnız gerektiğinde yüklenir.

## Kanıt sınırı

Yerel katalog ve kaynak kanıtı; hedef tenant erişimini, aktivasyonu, yetkiyi veya başarılı çalışma sonucunu kanıtlamaz. Eksik kanıt açıkça belirtilir.
