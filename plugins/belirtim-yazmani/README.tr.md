# Belirtim Yazmanı 3.3.0

[English](README.md) · Türkçe

## 3.3 kabul ve seçici çalışma

Protocol 3.3, üç atanmış rolü ve oracle kabulünü bağlar. Senaryo uyumu yanıt dizisinin sırasından bağımsız olarak okuyucu kimliğiyle karşılaştırılır. Preflight, sağlanan kaynak/sözleşme/metinlerde mevcut testlerin açık beklenen cevaplarını veya diğer okuyucu yanıtlarını engeller; özgün içerik tam korunur ve güvensiz kaynak sözleşmesi dispatch öncesi çözülmelidir. Eski 3.0/3.1/3.2 paketleri açık tarihsel salt okuma girdileri olarak kalır.

Hazırlık engelleri çocuk kabulünü durdurur; tek yazar eksikleri kapatabilir. Ortak coordinator ACTIVE seçilmiş workspace/episode profillerini kaydeder; bunların en düşük profil/host eşzamanlılığını, en fazla üç çocuğu uygular. Başarılı ve kaydedilmiş handoff katılımı kapatır, harcanan girişim geçmişini silmez. Otomatik süre dolumu, kota iadesi veya model değişimi eklenmez.

Kısa giriş ve yalnız gerekli intake, dispatch veya model rotası okunur. Birden fazla `--reference-id`, tek doğrulanmış paket yüklemesiyle seçili alt kümeyi çözer; tek kimlik çıktısı değişmez. `status` snapshot'ı bir kez değerlendirir. Ara değişikliklerde `python -X utf8 -B scripts/check.py --changed scripts/<changed-file>.py`; aday kararlı olduğunda bir kez `--final` kullanın. Doğrulayıcı etkilenen deterministik testleri seçer, LLM başlatmaz. Final handoff için tüm A-F kapıları, üç tam bağımsız okuyucu ve iki temiz kararlı tur gereklidir.

## 3.2.2 okuyucu kaynak havuzu

Her protocol 3.2 okuyucu paketinde dosya hash başına tek tam kaynak bulunur; referanslar kaynak kimliği/hash/pointer bağını korur. Runtime kaynağı bir kez decode eder ve aşırı serileştirme hacminde çıktı üretmeden BLOCKED verir. `read-reference <packet> --reference-id <ID>` kullanın veya tekrar erişim için `source_pool.Reader` nesnesini bir kez oluşturun. Eski paketler açık `--allow-legacy` seçeneğiyle salt okunur erişimdir; eski inceleme kayıtları ve yürütme teyidi yeni protokol için güncel kredi sağlamaz. Public şema, profil bütçeleri, üç tam okuyucu, körlük, onaylar ve iki temiz tur korunur.

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

## 3.2.1 native host uyumluluğu
Codex 0.160.0 native sondaları, ilk 3.2.0 paketinde manifest seçimi ve Windows hook başlatma uyumluluğu sorunlarını belirledi. 3.2.1, etkin Codex giriş noktası olarak `.codex-plugin/plugin.json` kullanır; taşınabilir agent-plugin metadata'sını `metadata/agent-plugin.json` içinde korur. Windows hook komutu, native runtime'ın `${PLUGIN_ROOT}` yer değiştirmesini tırnaklı yollarla kullanarak runtime'ın varsayılan komut kabuğuyla uyum sağlar. Bu değişiklikler için tam plugin paketini yeniden kurun/güncelleyin. Native hook yüklenmesi, güveni, olay yürütmesi ve sağlayıcı işi ayrı kontroller olarak kalır; yama beş profili ve bütün iş, onay ve final inceleme kapılarını korur.

## 3.2 çalışma profilleri
Geliştirmenin çalışma yoğunluğu için **Lite / Yalın, Plus / Gelişmiş, Pro / Yetkin, Max / Doruk veya Ultra / Üstün** seçin. Skill önce risk/kaynak gerekçesi, bilinmeyenler, tüm kapsamı okuyacak okuyucu kapasitesi, koşullu hazırlık bütçesi ve mevcut sağlayıcı ailesindeki model önerisini tek seçim kartında sunar. Kullanıcının gerçek seçimi özel çalışma kaydına alınır. Seçim iş varsayılanlarını, belirtimi, model/ayar değişikliğini veya teslimi onaylamaz. Mevcut belge profilleri `hafif/standart/tam` ayrı kalır.

| Profil | En çok hazırlık denemesi | En çok eşzamanlı alt ajan | Episode başına en çok toplam deneme |
| --- | ---: | ---: | ---: |
| Lite / Yalın | 0 | 1 | 12 |
| Plus / Gelişmiş | 1 | 1 | 13 |
| Pro / Yetkin | 2 | 2 | 14 |
| Max / Doruk | 4 | 3 | 16 |
| Ultra / Üstün | 6 | 3 | 18 |

Her profil final tur başına tüm kapsamı okuyan üç bağımsız okuyucuyu ve aynı güncel snapshot üzerinde iki temiz turu korur. Okuyucu deneme tavanı her episode'da 12'dir; hazırlık tavanları koşulludur, hedef değildir. Başarısız/iptal denemeler, tekrarlar ve revizyonlar bütçede sayılmaya devam eder. Profil/host/koordineli çalışma sınırları birlikte uygulanır; en çok üç alt ajan açılır, iç içe ajan açılmaz. Bağlı workspace'ler ortak coordinator dosyasını kullanır; ilgisiz host işlerinin dolu slotları ayrıca hesaba katılır. Bilinmeyen/yetersiz tam-okuyucu kapasitesi final çalıştırmayı/teslimi durdurur. Daha düşük seçim korunur; sığmayan plan için açık bölme/profil/bütçe kararı beklenir.

Skill dizininden mutlak `scripts/bv2.py` yolunu çözerek `work-profiles catalog`, `work-recommend`, `work-select`, `work-status`, `work-admit`, `work-begin` ve `work-finish` kullanın. Gerçek alt ajan çalıştırma host skill'ine aittir; CLI özel seçim, kota rezervasyonu, receipt ve ilerleme kontrollerini saklar. Sabit modelle subprocess başlatmaz. Okuyucu paketi üretimi gerçek okuyucu yürütmesi değildir: her çalıştırılan okuyucu ayrı rezerve edilir ve tamamlanır. Argümanlar, puanlama, kapasite ve toparlama için [çalışma profili protokolüne](skills/belirtim-yazmani/references/work-profiles.md) bakın.

Command hook adaptörleri işlem kapsamıyla sınırlı ilerleme kontrolü/diagnostic ekler. Native leaf PreToolUse gerçek çağrı kimliğini gerektirir ve zaten bütçede sayılan rezervasyonu açıkça seçilen harici coordinator içinde atomik olarak bu çağrıya bağlar; aynı host/olay kimliği tekrarında işlem yinelenmez, farklı çağrı kimliği aynı denemeyi kullanamaz. Bu hook yalnız coordinator rezervasyonuna yazar; workspace belirtimi ve kullanıcı ayarları değişmez. Hook keşfi, güveni ve runtime ayrı kanıtlardır; hook atlandığında veya desteklenmediğinde açık core kontrolü final teslimi korur. Yetenek/model erişimi, görsel destek ve telemetri özel kayıtta açıkça tutulur; ölçülmüş tasarruf, sağlayıcı çalıştırma ve native host hook kalifikasyonu ayrı kanıt gerektirir. Çalışma profili kaydı geliştirici ZIP'ine girmez.

## 3.1 kullanımı
Güncel engeller ve sonraki işlem için `status <workspace> --assets-root <inputs>` çalıştırın. Son okuyuculardan önce `preflight <workspace> --assets-root <inputs>` kullanın; eksik dosya, kaynak eşlemesi, referans, pointer, açık iş kararı ve bağımlılık sözleşmesi değerlendirme paketi üretimini durdurur. Salt okunurdur ve teslim onayı vermez. `check-plan`/`check-record` aynı dosya kökünü alır; doğrulayıcı byte ve gerçek dosya parmak izleri ile işlev, UI, nesne ve kayıt birimlerini kullanır.

Tarihsel özel inceleme protokolü 3.1 kayıtları için güncel protokolle taze yürütme gerekir. Her okuyucu her gereksinim için işlevsel soru ve somut plan kanıtı sunar. İlk iki okuyucu senaryo sonuçlarını `test_cases.expected` olmadan türetir; üçüncüsü tam belirtimi inceler. Paketler gerekli referans içeriğini ve sözleşmeleri içerir. Ayrıştırılmış gerçek yanıtlar hash'e bağlanır; insan teyidi zorunlu kalır ve sağlayıcı kimlik doğrulaması yerine geçmez. Public handoff şeması 3.0, üç okuyucu, iki temiz tur ve değişmez ayrı ZIP koşulları korunur. Danışman soruları gerçek `depends_on` önkoşulları tanımlayabilir; `blocked_by`/`unlocks` alanlarını gösterir.

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

Üç bağımsız okuyucu, senaryo uyuşması, gerçek PNG incelemesi ve kodsuz mimari/plan kontrolü son teslim kapılarıdır. Fixture sentetiktir; yürütme/görsel yetenek yoksa NOT_RUN. Yerel şema/ZIP kontrolü SAP yetkisi, aktivasyon, ATC, runtime veya UAT kanıtı değildir. [Doğrulama](docs/VERIFICATION.tr.md) ve [değişiklikler](docs/CHANGES.tr.md) içindedir. Tarihsel 3.0.0 benchmark sınırı geçerlidir; profil/sağlayıcı maliyeti ve native host yürütmesi 3.2.1 için ayrı kalifikasyon kapsamları olarak kalır.
