# Spec Writer skill

[English](README.md) · Türkçe

## Kapsam
Claude Code ve Codex için ortak, modele dönük giriş. Yalnız ilgili referansları okur
ve plugin'in sahip olduğu runtime'ı çağırır. Skill'e ait bağımlılık veya executable yoktur.
Kurulum, geçiş, eval kapıları ve testler için [plugin rehberini](../../README.tr.md) kullanın.
Kullanıcının diliyle yanıt verir; varsayılan Türkçedir. Kural gövdesi İngilizcedir.

## Çalışma profilleri
3.2.0; Lite / Yalın, Plus / Gelişmiş, Pro / Yetkin, Max / Doruk ve Ultra / Üstün seviyelerini özel çalışma yoğunluğu seçimi olarak ekler. Kullanıcının seçiminden önce tek öneri kartı sunulur. Hazırlık, deneme bütçeleri, host kapasitesi ve sağlayıcı ailesindeki model önerileri değişir; tüm kapsamı okuyan üç okuyucu, iki temiz final turu ve insan onayı ortaktır. `hafif/standart/tam` belge profilleri ayrı kalır. Yalnız ilgili akışta [work-profiles](references/work-profiles.md) okunur; runtime otomatik model seçmez veya sağlayıcı subprocess'i başlatmaz. Paket keşfi ve sentetik testler native yürütme veya ölçülmüş tasarruf değildir.

3.2.1, Codex 0.160.0 sondalarından sonra native Codex manifest seçimini ve taşınabilir Windows hook başlatmayı düzeltir. Etkin host manifesti `.codex-plugin/plugin.json`; taşınabilir metadata `metadata/agent-plugin.json` içindedir. Beş profilli protokol, 22 kuralın tamamı ve mevcut kalite kapıları değişmez. Güncel tam plugin paketini kullanın; native güven/olay yürütmesi ve sağlayıcı maliyeti kendi kanıtlarını gerektirmeye devam eder.

3.2.2 her tam okuyucu kaynağını dosya hash başına bir kez saklar ve pointer bağlarını korur. Protocol 3.2 paketlerini ve güncel protokol yürütme teyidini kullanın; tarihsel paketler açık salt okunur uyumluluktur.
