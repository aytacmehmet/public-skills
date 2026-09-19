# Değişiklik geçmişi

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
