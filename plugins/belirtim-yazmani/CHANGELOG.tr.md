# Değişiklik geçmişi

[English](CHANGELOG.md) · Türkçe

## 3.3.0 — 2026-10-09

- PUBLICATION.json içinde kaydedilen commit edilmiş tam private 3.3.0 plugin'i aktar; ortak runtime, schema, codec, okuyucu tanımları, hook'lar, tüm testler ve seçici talimat rotaları dahil.
- İki senaryo okuyucusunu atanmış kimlikle bağla, açık oracle/peer erişimini reddet, açık hazırlık engellerini ve en düşük ACTIVE koordineli profil/host sınırını uygula. Tarihsel 3.0/3.1/3.2 paketleri salt okuma kalır; yeni kredi özel protokol 3.3 ister.
- Toplu referans erişimi, tek snapshot değerlendirmesi, hedefli/final doğrulama ve kapalı sandbox üst klasörleri için strict fiziksel yol doğrulaması ekle. Public şema 3.0, değişmez ayrı ZIP, insan onayı ve tam üç okuyucu/iki temiz tur tabanı korunur.
- Public'e özel builder/hash kontrollerini ve tarihsel kayıtları koru. Yerel/sağlayıcı/host kanıtı hosted CI, gerçek handoff okuyucusu/görsel ve SAP kabulünden ayrıdır; genel hız veya token tasarrufu iddia edilmez.

## 3.2.2 — 2026-10-09

- Yönetişimli profiller ve native 3.2.1 uyumluluğu dahil tam private 3.2.2 pluginini PUBLICATION.json kesin commit’inden aktar.
- Her tam okuyucu kaynağını bir kez havuzla, hash/pointer erişimini koru ve serileştirme aşımını engelle. Protocol 3.2 yeni kayıt ve güncel yürütme teyidi gerektirir; eski paketler açık salt okunur veridir.
- Profil/onay/kör okuyucu/iki temiz tur kapılarını koru; gerçek RMP incelemesi veya benchmark çalıştırılmaz.

## 3.1.0 — 2026-10-08

- PUBLICATION.json içindeki kesin private 3.1.0 commit'ini aktarır; iki host manifestini ve tam runtime/şema/test/codec paketini korur.
- Erken salt okunur preflight/status, ortak fiziksel dosya eşlemesi, okuyucuya referans içeriği, daha güçlü işlev/plan/yanıt bağlaması ve beklenen cevabı gizleyen senaryo girdileri ekler.
- Geçerli ve değişmemiş işlev/UI/nesne/kayıt kontrollerini gerçek dosya/doğrulayıcı parmak izleriyle tekrar kullanır; geçerli örnek ZIP byte'larını değiştirmeden katı codec işlemlerini toplar.
- Public 3.0 handoff biçimini, onay/üç okuyucu/iki tur kapılarını ve ayrı değişmez geliştirme ZIP'lerini korur. Eski özel incelemeler protokol 3.1 ile yürütülmelidir.
- Tarihsel doğrulamayı ve public builder/hash kontrollerini korur. Yerel model kanıtı sınırlandırılmıştır; karşılaştırmalı maliyet, tam handoff okuyucusu veya SAP doğrulaması iddia edilmez.

## 3.0.0 — 2026-10-02

- Yayınlanmış private 3.0.0 kaynağı tam olarak aktarılır; public paket hash kontrolü ve tekrarlanabilir çevrimdışı üretici korunur.
- Danışmana iş/tasarım soruları için en fazla üç sıralı ve puanlı öneri sunulur; sınırları belli developer teknik kararları kendi kendine yeterli TOON otoritesinde tutulur.
- Etkilenen geliştirmeler bütün kapılar geçince ayrı ZIP'ler halinde birlikte teslim edilir; her dosya kısa geliştirme adıyla başlar ve gerekli sözleşme/referanslar yerel olarak dahil edilir.
- Mimari, beş katmanlı/iki turlu yayın kontrolleri, değiştirilemez baseline/import uyumluluğu ve hash'e bağlı artımlı kontrol planı korunur.
- Public marketplace kimliği ve eski standalone yayın geçmişi korunur. Doğrulanmamış token-audit adayı dahil edilmez; yeni tasarruf veya model/SAP qualification iddiası yoktur.

## 2.0.2 — 2026-10-01

- PUBLICATION.json içinde kaydedilen private-skills-plugins main commit'inden alınan ilk tam public-skills plugin dağıtımı.
- İki native marketplace'e `belirtim-yazmani@aytacmehmet-public` adıyla kaydedilir; üç plugin manifesti, skill metadata, paket kontrolü ve iki dilli kurulum/yayın belgeleri eşitlenir.
- Harici deterministik marketplace ZIP üreticisi ve dosya bazlı paket manifesti eklenir. TOON şemaları, runtime, 17 kural, kaynak/codec lisansları ve tarihsel 2.0.1 yeterlilik korunur.
- Public 1.1.0 JSON standalone paketler ve arşivleri korunur. Bu plugin tam 2.x TOON dağıtımıdır; aynı anda tek sürüm kurulur.

Önceki kaynak geçmişi [kaynak değişikliklerinde](docs/CHANGES.tr.md) ve [provenance kaydında](PUBLICATION.json) korunur. Eski public-skills plugin arşivi uydurulmaz. Plugin geçmişi commit'li Git sürümlerindedir; tam teslim ZIP'leri repo dışında tutulur.
