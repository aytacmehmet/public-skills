# Belirtim Yazmanı 2.0.2

[English](README.md) · Türkçe

## Amaç
Kararları verilmiş SAP Cloud ERP geliştirmeleri için ortak Claude Code/Codex skill'i ve plugin runtime'ı.
Olgu ve kararları belgeler; çözüm tasarlamaz, uygulama kodlamaz veya tenant değiştirmez.
Özel TOON çalışma alanı tam hedefi ve üretici kontrol kayıtlarını ayırır.
Developer otoritesi `fsts/fsts.toon`; Excel isteğe bağlı projeksiyondur.

## Kurulum
Plugin runtime'ı Python 3.11+, Node.js 20+ ve `requirements.txt` içindeki kilitli paketleri gerektirir.
Gömülü skill'in sahip olduğu pip paketi veya script yoktur. TOON codec pakette bulunur.
Ayrı bir sanal ortamda plugin kökünden `python -m pip install -r requirements.txt` kullanın.

Claude Code:
```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install belirtim-yazmani@aytacmehmet-public
```
Codex:
```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/belirtim-yazmani
codex plugin add belirtim-yazmani@aytacmehmet-public
```
Claude Code'da `/belirtim-yazmani:belirtim-yazmani`, Codex'te `$belirtim-yazmani` kullanın
(host gösteriyorsa tam namespaced ad). İki host aynı kuralları ve runtime'ı kullanır.
Otomatik kurulum, model seçimi veya kullanıcı ayarı değişikliği yapılmaz.

## İşleyiş
`python scripts/bv2.py --help` kullanın. Runtime yolunu kurulu skill konumundan çözün;
çalışma dizini farklı olabilir. `BY_NODE`, Node executable yolunu seçebilir.

1. `init` veya `migrate`, legacy girdiyi koruyup TOON çalışma alanı açar; özgün JSON değişmez.
2. `release-init`, yetkili `delivery.spec` alanını açar; içe alınmış içerik salt okunur referans olur.
3. `profile`, `guide`, `patch`, `context` yalnız geçerli rehberi/veriyi ilişki kapanışıyla getirir.
4. `release-inspect` profili, izlenebilirliği, sıfır açık sayaçları ve üretici/kod taramasını zorlar.
5. `release-approve`, `eval-request`, `eval-record`, `confirm-reviews` gerçek sahip/okuyucu kayıtlarını özel alanda bağlar.
6. `handoff`, açık, eksik eval veya iki temiz tur yokluğunda durur. `verify` kaydedilen paketi kontrol eder.
7. `feedback`, developer'ın her spec hatasını regresyona alır ve yeni sürüm gerektirir.

A-F sözleşmesinde FS-TS, şema, manifest, readiness, nesne ve delta TOON'dur.
UI, hash ile bağlı numaralı PNG callout'ları gerektirir. İnteraktif dosyalar açık istisna,
offline doğrulama ve statik kontrol gerektirir. Her handoff tek geliştirmeye aittir ve değişmez.
Diğer geliştirme değişikliği ayrı handoff ister. Baseline artifact ve çözülmüş spec hash'i ayrıdır.
Erişememek yokluk teyidi değildir. Tam hedef ve stable-ID delta birlikte teslim edilir.

## Doğrulama ve sınırlar
Runtime bağımlılıkları kurulduktan sonra `python -m unittest discover -s tests -v` çalıştırın.
Yerel yardımcılar model/SAP servisi çağırmaz. Host bağımsız okuyucuları kullanıcının ayarlarıyla yürütür.
Üç izole okuyucu, senaryo uyuşması, gerçek PNG kontrolü ve kodsuz plan simülasyonu gerekir;
yardımcılar verilen kayıtları kontrol eder, dış yürütmeyi kimlik doğrulamasıyla kanıtlamaz. Eksik yetenek `NOT_RUN`.
Fixture'lar gerçek semantik/model/tenant kanıtı değil, kayıt simülasyonudur. Geçerli şema veya temiz
ZIP mutlak eksiksizlik, SAP aktivasyonu, ATC, runtime, UAT ya da token/hız tasarrufu kanıtlamaz.
Tarihsel 2.0.1 kaynak yeterliliği [doğrulama](docs/VERIFICATION.tr.md), kural eşlemesi `docs/RULE-COVERAGE.toon` içindedir.
Bu 2.0.2 public plugin, deponun eski 1.1.0 JSON standalone çiftinden ayrı bir dağıtımdır.
Aynı anda tek Belirtim Yazmanı sürümü kurun; tam 2.x plugin ortak TOON runtime'ının sahibidir.
[Public değişiklik geçmişine](CHANGELOG.tr.md) ve [kaynak yayın kaydına](PUBLICATION.json) bakın. Yeni model/SAP yeterliliği iddia edilmez.

## Public paket kontrolleri

`python -B skills/belirtim-yazmani/scripts/check_package.py` ve `python -B -m unittest discover -s tests -v` çalıştırın. Tam çevrimdışı marketplace ZIP'ini `python -B scripts/build_package.py --output-dir <harici-artifact-klasörü>` ile üretin. Üretilen PACKAGE-MANIFEST.json dosyasını commit öncesi kaynağa kopyalayıp repo doğrulamasını yeniden çalıştırın. Paketleyici ZIP CRC ve dosya hash'lerini doğrular; plugin kaynağını değiştirmez. Python bağımlılıkları sabitlenmiştir; değiştirilmemiş MIT TOON codec dahildir. Public ve tarihsel yeterlilik ayrı kanıtlardır.
