# Belirtim Yazmanı 3.1.0

[English](README.md) · Türkçe

## Amaç
SAP Cloud ERP için ortak Claude Code/Codex belgeleme skill'i. Danışman iş/tasarım kararları en fazla üç sıralı öneriyle toplanır; uygulama tekniği soruları ABAP developer'a aittir. Bağlı geliştirmelerin ayrı ZIP'leri iş, mimari, referans ve son inceleme kapıları geçince topluca teslim edilir. Paketler kendi bağlamını içerir; developer'ın araç/model seçimine bağımlı değildir.
## Kurulum
Plugin runtime'ı Python 3.11+, Node.js 20+ ve kilitli `requirements.txt` paketlerini gerektirir. Ayrı sanal ortamda `python -m pip install -r requirements.txt` kullanın. Gömülü skill'in bağımlılığı yoktur; resmi TOON codec pakettedir.

```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install belirtim-yazmani@aytacmehmet-public
```

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/belirtim-yazmani
codex plugin add belirtim-yazmani@aytacmehmet-public
```

Claude Code'da tam skill adını, Codex'te `$belirtim-yazmani` kullanın. Bu repo yayını kurulum yapmaz veya model seçmez.

## 3.1 kullanımı
Güncel engeller ve sonraki işlem için `status <workspace> --assets-root <inputs>` çalıştırın. Son okuyuculardan önce `preflight <workspace> --assets-root <inputs>` kullanın; eksik dosya, kaynak eşlemesi, referans, pointer, açık iş kararı ve bağımlılık sözleşmesi değerlendirme paketi üretimini durdurur. Salt okunurdur ve teslim onayı vermez. `check-plan`/`check-record` aynı dosya kökünü alır; doğrulayıcı byte ve gerçek dosya parmak izleri ile işlev, UI, nesne ve kayıt birimlerini kullanır.

Özel inceleme protokolü 3.1, eski okuyucu kayıtlarının yeniden gerçekten yürütülmesini gerektirir. Her okuyucu her gereksinim için işlevsel soru ve somut plan kanıtı sunar. İlk iki okuyucu senaryo sonuçlarını `test_cases.expected` olmadan türetir; üçüncüsü tam belirtimi inceler. Paketler gerekli referans içeriğini ve sözleşmeleri içerir. Ayrıştırılmış gerçek yanıtlar hash'e bağlanır; insan teyidi zorunlu kalır ve sağlayıcı kimlik doğrulaması yerine geçmez. Public handoff şeması 3.0, üç okuyucu, iki temiz tur ve değişmez ayrı ZIP koşulları korunur. Danışman soruları gerçek `depends_on` önkoşulları tanımlayabilir; `blocked_by`/`unlocks` alanlarını gösterir.

## İşleyiş
`scripts/bv2.py` yolunu yüklenen skill'in mutlak konumundan çözün; cwd farklı olabilir.

1. `init`/`migrate`, ardından `release-init` özel TOON 3.0 hedefi oluşturur. Özgün girdiler değişmez. Mevcut 2.0 workspace için `release-upgrade` kullanılır; eski onay/inceleme kanıtı geçersizleşir, yeni diye etiketlenmez.
2. `questions` yalnız danışman BUSINESS/USER_EXPERIENCE/BUSINESS_DESIGN konularını döndürür. Öneriler metin, gerekçe, varsayım ve ayrı 0..5 tutarlılık/uygunluk/kalite puanları taşır. Ortalama A/B/C sırasını belirler; puan göreli yargıdır, onay değildir. Gerçekçi öneri yoksa gerekçe belirtilir, seçenek uydurulmaz.
3. Public `developer_decisions` bağlamı, kısıtları, mimari referansları ve paket içi girdileri tamam ABAP_DEVELOPER/IMPLEMENTATION kararlarıdır. İş açığı kapıyı aşmak için bu listeye atanamaz. Teslimde teknik karar varsa READY_FOR_DEVELOPER_DECISIONS denir; READY_FOR_CODING denmez.
4. `check-plan` değişen kontrol birimlerini ve bağımlılık hash'lerini hesaplar; `check-record` gerçek bağlı sonucu saklar. Yalnız geçmiş geçerli/değişmeyen birim tekrar kullanılır. Pahalı son okuyuculardan önce ara değişiklikleri biriktirin. Cache teslim onayı veya yeni model yürütmesi değildir.
5. Sorumluluk sınırları, mimari kısıtlar, fonksiyonel zincirler, baseline ve referansları tamamlayın. Her dosya/metin/liste/pointer ZIP içinde bulunmalıdır. Her dosya adı onaylı anlamlı kısa adla başlar. Otoriteyi manifest rolleri belirler; sabit fsts/fs-ts dosya adı üretilmez.
6. `release-approve`, son `eval-request`/`eval-record` ve `confirm-reviews` gerçek güncel snapshot onayını ve beş katmanlı incelemeyi korur. İki temiz son tur gerekir. Sahte yürütme, otomatik iş varsayılanı veya SAP değişikliği yoktur.
7. `handoff-batch`, manifest dizini içindeki `workspace` ve `assets_root` yollarından oluşan `developments` TOON listesini okur. `--output` ve `--batch-id` kullanılır. Değişen bağlı geliştirmelerin hepsi bulunmalıdır; sözleşme partner sürüm/hash/pointer'ına ve eksiksiz gereken içeriğe bağlıdır. Ayrı ZIP'ler stage edilir, doğrulanır ve tek yeni dizinde topluca yayımlanır; döngü, ortak nesneye çakışan değişiklik veya engelli partnerde final teslim çıkmaz.
8. `verify`, 3.0 rol manifestini ve salt okunur baseline için eski 2.0 paketini okur. Güncellemeler baseline içeriği ile stable-ID farkı taşır; teslimler üzerine yazılmaz. `feedback` yeni sürümlü regresyon oluşturur.

## Sözleşme ve sınırlar
Tek düzenlenebilir/public belirtim otoritesi TOON'dur; Excel türev, PNG yalnız yerleşim içindir. Gerekli bağlı sözleşme ve kaynak parçaları her ZIP'e dahil edilir; başka dosya/URL'den aranmaz. Tarafsız developer rehberi okuma sırasını, sınırları belli teknik kararları ve kabul kontrollerini açıklar; lokal skill/plugin/model, uygulama kaynağı, scaffold veya çalıştırılabilir geliştirme/test script'i teslim edilmez. Mevcut açıkça onaylanmış offline interaktif istisna ayrıdır.

Üç bağımsız okuyucu, senaryo uyuşması, gerçek PNG incelemesi ve kodsuz mimari/plan kontrolü son teslim kapılarıdır. Fixture sentetiktir; yürütme/görsel yetenek yoksa NOT_RUN. Yerel şema/ZIP kontrolü SAP yetkisi, aktivasyon, ATC, runtime veya UAT kanıtı değildir. [Doğrulama](docs/VERIFICATION.tr.md) ve [değişiklikler](docs/CHANGES.tr.md) içindedir. 3.0.0 için yeni token/latency benchmark'ı çalıştırılmadı.

## Public paket kontrolleri

`python -B skills/belirtim-yazmani/scripts/check_package.py` ve ilgili runtime testlerini çalıştırın. Tam çevrimdışı marketplace ZIP'i `python -B scripts/build_package.py --output-dir <external-artifacts>` ile oluşturun. Üretilen PACKAGE-MANIFEST.json dosyasını plugin'e kopyalayıp commit öncesi repo doğrulamasını çalıştırın. Teslim ZIP'leri repo dışında kalır. Eski Spec Writer standalone çifti emekli edilmiştir; tam plugin geçmişi ve önceki arşivler Git'te korunur. Aynı anda tek etkin Spec Writer sürümü kurun. [Public değişiklikler](CHANGELOG.tr.md) ve [yayın kökeni](PUBLICATION.json) kayıtlarına bakın.

Upstream doğrulama kayıtları private yerel aday üzerinde commit ve yayın öncesinde toplanmıştır. PUBLICATION.json aktarılan gerçek private commit'i sabitler; hosted kontroller ve merge kayıtları ayrı kanıttır. Public paketleme doğrulamanın model, maliyet veya SAP kapsamını genişletmez.
