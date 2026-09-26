# Değişiklik geçmişi

## 2.0.0 — 2026-09-27

Major sürüm: Türkçe paket artık İngilizce model talimatlarını paylaşır, sözleşme şeması daha katıdır (aşağıdaki 1.3.0'a bakın) ve yakalama kanıtı kapının parçasıdır. Geliştirme deposu kendi kopyasını özel bir plugin lehine emekliye ayırdı; bu public paket bakımı süren bağımsız sürümdür.

- **Durum istisnaları:** oluşamayacak zorunlu bir durum atılmak yerine gerekçesiyle `stateExceptions` listesine yazılır; listeyi `CONTRACT_STATE_EXCEPTION` ve `CONTRACT_STATE_EXCEPTION_CONFLICT` korur, geri kalanı istisna olduğunda `states` beşten az kayıt içerebilir.
- **`$metadata` arama desteği:** `inspect_abap_package.py --metadata <file>`, entity set'leri ve beyan edilmiş `$search` desteklerini (V4 `Capabilities.SearchRestrictions`, V2 `sap:searchable`) `service.metadata` altına yazar; protokol uyuşmazlığı veya eksik entity set gap olur. Sözleşme metadata'nın reddettiği aramayı iddia ederse kapı `SEMANTIC_SEARCH_CONFLICT` bildirir.
- **İnceleme modu:** `cmd:` handler'ları ve `core:require` alias'ları açık handler sayılır; betik yorumları ve `webapp/test`/`webapp/localService` artık kaynak bulgusu üretmez.
- **Kayıtlı yakalamalar:** yeni `record_captures.py`, incelenen her PNG'nin hash'ini `visuals/capture-report.json`'a yazar; kapı `PNG_REPORT_MISSING` ve `PNG_DIGEST` bildirir. S genişliğinde anahtar bir değeri bekleyin: responsive tablolar anahtar olmayan sütunları kaldırır.
- Bakım: FD33–FD36 davranış senaryoları; dört araç testi. 1.2.0 arşivlendi.

### Ayrıca: geliştirme deposunda 1.3.0 ve 1.4.0 olarak hazırlanan, burada ayrıca yayımlanmamış değişiklikler

#### 1.4.0

- **Modele dönük dosyalar İngilizce ve ortak:** `SKILL.md` gövdesi ve `references/` altındaki her dosya İngilizce ve Türkçe pakette aynıdır (yalnız frontmatter farklıdır); skill kullanıcıya kendi dilinde cevap verir. Yönerge ve referanslar token verimi için sıkıştırıldı: tekrar eden bağlantı blokları kaldırıldı, kurallar tek satırlık emir kipine indirildi; bölüm numaraları ile her kural, tablo, komut ve doğrulayıcı kodu korundu; eklenen kurallara ve büyüyen doğrulayıcı tablosuna rağmen 1.2.0'a göre yaklaşık %11 daha az bayt. Depo çift testi eşitliği denetler.

#### 1.3.0

- **Belge ↔ betik tutarlılığı:** yönergedeki scaffold komutu kod için zorunlu bayrakları (`--framework`, `--ui5-version`, `--service-uri`, `--entity-set`) ve `--target-ui5-runtime`, `--json` bayraklarını gösterir; şablon metni sözlüğü (`Replace with …`, `replace-with-…`, `pending-…`, `verify-…`, `YYYY-MM-DD`) her yerde aynıdır ve `Replace` tek başına artık bulgu değildir; bilinmeyen hedefin yalnız kod tesliminde kapıyı kapattığı README'de düzeltildi; delivery §10 önem sütunu kazandı ve `CONTRACT_STATE`, `CONTRACT_TARGET_UNKNOWN`, `SEMANTIC_MIN_UI5`, `SEMANTIC_UI5_VERSION`, `CONTRACT_TRACEABILITY_ROW`/`CONTRACT_SOURCES_ROW`, `MANIFEST_V2`, `BACKEND_PARTIAL` eklendi; `SEMANTIC_ACTION_ID` için Fiori elements muafiyeti yazıldı; PNG örneği kanonik bir durum adı kullanır; çoklu service definition kuralı intake referansında tek biçimde anlatılır.
- **Scaffold:** `--reset-contract` tek başına çalışır, `.bak` alır ve `prototype/`/`app/` ağaçlarını korur; iki şema her çalıştırmada yenilenir; `--action` `--semantic-object` olmadan reddedilir; `--semantic-object` sözleşmede `launchContext: flp` yazar, şablon varsayılanı `unknown` oldu; kod eklenirken boş `alternativesRejected` framework kararına göre doldurulur; scaffold profili kanıt satırı birikmez; freestyle sözleşmesi iskeletin gerçek i18n anahtarını (`idColumn`) kullanır; `project.outputs` eksik sözleşme açık hatayla reddedilir.
- **Doğrulayıcı:** `--review` mevcut projede yeni proje kurallarını (`MANIFEST_V2`, `MANIFEST_I18N`, `MANIFEST_DENSITY`) `warning` olarak bildirir; eksik izlenebilirlik/kaynak satırı ayrı `_ROW` koduyla uyarıdır; şema `context.targetSystem`, `responsive.breakpoints`, `accessibility` boolean'ları, `dataContract.authorization` ve `verification` alanlarını doğrulayıcıyla aynı sıkılıkta zorlar.
- **Inspector:** `composition … of` ilişkileri `model.associations[]` içinde `kind` ile okunur; `--entity-set` büyük/küçük harfe duyarsızdır; tek service definition varken binding başka tanımı gösteriyorsa `gaps` uyarısı yazılır; snapshot `sha256`/`objectName` alanları, 5.000 dosya sınırı ve yerel export'ta `complete`/`activeSourcesOnly` değerlerinin beyan olduğu belgelendi.
- **Şablonlar:** prototip `?state=initial` durumunu da üretir, kullanılmayan i18n anahtarları ve Manifest V2 altındaki iç `_version` alanları kaldırıldı; freestyle iskeletinde ölü kod temizlendi ve `empty`/`no-results` metinleri ayrıldı; Fiori elements manifest'i `sap.insights`'ı lazy bağımlılık olarak bildirir ve smoke testindeki konsol filtresi gerekçelendirildi.
- **Referanslar:** List Report filtre modunda varsayılanın `Go` olduğu düzeltildi; Manifest V1 ile mevcut projenin kalabileceği yazıldı; tasarım temellerindeki araştırma tarihi tek kayda bağlandı; arayüz açıklaması skill'in tam kapsamını anlatır. 1.2.0 arşivlendi.

## 1.2.0 — 2026-09-19

- **Teslim kapısı içeriği de denetler:** sözleşmede kalan şablon metni (`CONTRACT_PLACEHOLDER`), tasarlanmamış `loading`/`no-results`, `states` ↔ `verification.states` farkı, i18n'de olmayan metin anahtarı, view'da olmayan eylem kimliği, boş erişilebilirlik kanıtı, kod tesliminde boş `initialSelect`/komutlar, doğrulanmamış released durumu, FLP inbound'u ve `$search` artık bulgudur. PNG adları sözleşmedeki durum kimlikleriyle eşleştirilir. Yeni `info` düzeyi kapıyı kapatmaz: yalnız prototip tesliminde hedefin `unknown` olması ve envanteri doğrulanamayan paket kaynağı bilgi notudur.
- **Artımlı scaffold:** var olan `design-contract.json` korunur; sonraki çalıştırma yalnız eksik ağacı ve scaffold'a ait alanları ekler. `--force` yalnız `prototype/` ve `app/` dosyalarını yeniler; `--reset-contract` eski sözleşmeyi `.bak` olarak saklar. Inspector'ın framework önerisi artık açık bir freestyle kararını engellemez.
- **İnceleme modu:** `validate_fiori_delivery.py --review`, sözleşmesi olmayan mevcut projeyi tarar; yönergeye bulgu biçimini tanımlayan `<review>` bölümü eklendi.
- **Tek sözlük:** kanıt durumu `verified | assumed | unknown | blocked` olarak şemada zorlanır; durum listesi (`initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth`) yönerge, şablon, doğrulayıcı ve referanslarda aynıdır.
- **Inspector:** alan → annotation eşlemesi ve `lineItemFields`, `selectionFields`, `valueHelpFields`, `hiddenFields` gibi rol listeleri (DDLS ve DDLX), `@Search.searchable`, custom/abstract entity ve klasik view, service binding → service definition bağı, `inventoryVerified`/`notes`, ZIP toplam boyut ve sıkıştırma oranı sınırı.
- **Şablonlar:** prototip `?state=loading|empty|no-results|error|no-auth` ile her durumu gösterir, dialog fragment'tir ve hatayı `valueState` ile verir, mock veri `--language` ile seçilir; freestyle iskelette deep-link'lenebilir ayrıntı route'u, `bypassed` → not-found hedefi ve bunları sınayan OPA5 yolculukları var; Fiori elements iskeletinde yerel annotation dosyası var; `--semantic-object/--action` manifest'e FLP inbound'u ekler. Şablon sözleşmesi prototipin gerçek i18n anahtarları ve kontrol kimlikleriyle hizalandı.
- **Düzeltme:** freestyle şablonunda `npm run typecheck`, `playwright.config.ts` Node tipleri gerektirdiği için 1.0.0'dan beri başarısızdı; yapılandırma artık ek bağımlılık olmadan derlenir. Boş yollu OData V4 property binding'i `targetType: 'any'` ve `mode: 'OneTime'` ile yazıldı.
- **Profiller:** şablon lockfile'ı `templateLockfileProfile`'a aittir; başka profil kendi `lockfileDir` klasörünü getirmeden kod scaffold edemez.
- **Kaynaklar:** eski `experience.sap.com` bağlantıları sürüm notu taşır; bağlantı sürümlerinin neden farklı olduğu açıklandı.
- Bakım: FD27–FD32 davranış senaryoları; depo tarafında `skills.py export` (başka host için yeniden adlandırılmış, overlay'li kopya), haftalık bağlantı kontrolü ve şablonları kurup build/test eden iş akışı. İki üretim şablonu ve prototip bu sürümde gerçek ortamda doğrulandı. 1.1.0 arşivlendi.

## 1.1.0 — 2026-09-19

- Yönerge Yordamla 2.0.0 yapısına geçirildi: emir kipi, iş akışı sırasını izleyen XML bölümleri (`<invariants>` … `<resources>`), kapsam alanları, referans ve çıktı/ön koşul tabloları, iki iyi/kötü örnek, öz-kontrol ve sonuç-önce teslim raporu. Kurallar ve davranış değişmedi.
- Referanslar iki türe ayrıldı: yedi alan referansı çalışma zamanında yalnız gerektiğinde okunur; yeni FD01–FD26 davranış kontrolleri ile kaynak ve tasarım notları yalnız bakım içindir ve yönergeden bağlantı almaz.
- Scaffold komutu yönergede tam biçimiyle (`--language`, `--backend-contract`) verildi; PNG adlandırma kalıbı yönergeye taşındı.
- Bakım: depo testi iki dilde aynı bölüm sırasını, bakım referanslarının yönergeden bağlanmadığını ve FD senaryo numaralarını denetler. 1.0.0 arşivlendi.

## 1.0.0 — 2026-09-19

- İngilizce SAP Fiori Design ile eşleştirilmiş ilk herkese açık yayın.
- Sözleşme odaklı akış: ABAP paketinden `abap-backend-contract.json`, ondan `design-contract.json`; aynı sözleşmeden interaktif UI5 prototipi, prototipten alınan PNG ve TypeScript freestyle veya Fiori elements OData V4 üretim iskeleti.
- Uyarıda da başarısız olan statik teslim doğrulayıcısı: strict JSON, paket içi şema, SHA-256 kanıt zinciri, sözleşme ↔ manifest tutarlılığı, deprecated/güvensiz kalıplar.
- Service binding protokolü, abapGit ve ADT export'larındaki ayrı tip + sürüm alanlarından da okunur; XML namespace URL'leri artık yorum sanılıp kesilmez.
- Behavior definition her entity için ayrı ve ifade bazında okunur: parantezli `create/update/delete`, association üzerinden create, dinamik feature control, function'lar; draft action'lar iş action'larından ayrılır; `etag` ile `total etag` ayrı tutulur.
- CDS element listesi iç içe ve çok satırlı annotation'ları, virgül içeren ifadeleri ve tırnak içindeki `//` dizgisini doğru okur; sınıflandıramadığı elementi düşürmek yerine `unparsedElements` ve `gaps` içine yazar.
- Birden fazla service definition veya entity set adayı varsa ilkini seçmez; `--service-definition` ve `--entity-set` ile açık seçim ister.
- Scaffold profili artık hedef sistem runtime'ı olarak raporlanmaz: `--target-ui5-runtime` ayrı verilir, verilmezse `unknown` kalır; doğrulayıcı `minUI5Version` değerinin runtime'dan yeni olmamasını denetler. Varsayılan profil `version-profiles.json` içindeki `defaultProfile` alanından okunur.
- Renk ve sabit metin denetimleri daraltıldı: route hash'i, ID seçicisi, ikon URI'si ve harf içermeyen değerler bulgu üretmez.
- Betikler çalışma dizininden bağımsız `<skill kökü>` yoluyla ve `python -B` ile çağrılır.

Önceki herkese açık sürüm: yok.
