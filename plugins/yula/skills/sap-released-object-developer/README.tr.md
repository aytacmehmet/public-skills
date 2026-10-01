# Released nesne geliştiricisi

[English](README.md) · Türkçe

Kesin public imzaları ve kısa ABAP Cloud çağrı bağlamını getirir. Yalnız amaç soruları advisor skill'ine yönlendirilir.

## Kurulum

**Yula 1.4.1** içinde dağıtılır. [Plugin'in tamamını](../../README.tr.md) kurun; bu skill ortak MCP sunucusuna, kurallara ve SQLite veritabanına bağlıdır. İkinci bir bağımsız kopya kurmayın.

## Kullanım

Otomatik çağırma açıktır. Claude Code'da açık çağrı için `/yula:sap-released-object-developer` kullanın. Codex'te skill seçicisinden Yula skill'ini seçin.

Yanıtlar kullanıcının dilindedir. Teknik tanımlayıcılar değiştirilmez. Model talimatları İngilizcedir; ayrıntılı referanslar yalnız gerektiğinde yüklenir.

## Kanıt sınırı

Yerel katalog ve kaynak kanıtı; hedef tenant erişimini, aktivasyonu, yetkiyi veya başarılı çalışma sonucunu kanıtlamaz. Eksik kanıt açıkça belirtilir.
