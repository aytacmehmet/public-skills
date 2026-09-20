# Bölüm yazım bilgisi · Genel ve Fonksiyonel

Üretilmiş dosyadır (kaynak: assets/tanim.json). Sütun numaraları 0'dan başlar ve JSON'daki dizi sırasıdır. {X-nn} satır kimliğidir; [a | b] yalnız bu değerleri alır; (KARAR) = kararı sen verme, girdide yoksa işaretle.

## 1.1 Geliştirme türü (RICEF)  [ağırlık 5 · Kritik · tüm türler]
Not: RICEF türleri belgenin üst düzeyindeki 'turler' dizisinden türetilir; bu bölümde yalnız alanlar yazılır.
Amaç: Geliştirmenin kimliğini, türünü ve genişletme yaklaşımını tek yerde sabitler; hangi bölümlerin zorunlu olduğunu belirler.
Kural: Üst düzeydeki `turler` dizisine en az bir RICEF türü yazın; tür tablosu ondan türetilir. Genişletme yaklaşımı ve hedef clean core seviyesi girdideki karara göre yazılır; A dışındaki seviye için gerekçe yazın.
Alanlar: gel_id = Geliştirme ID — Örn. GEL-MM-014 ; baslik = Geliştirme başlığı — Tek satır; iş sonucunu anlatır ; modul = Süreç alanı / modül — Örn. Satınalma (MM-PUR) ; sistem = Sistem [S/4HANA Cloud Public Edition | S/4HANA Cloud Private Edition] ; yaklasim = Genişletme yaklaşımı [Key user | Developer (ABAP Cloud) | Side-by-side (BTP)] (KARAR) ; clean_core = Hedef clean core seviyesi [A | B | C | D] (KARAR) ; cc_gerekce = A dışı seviye gerekçesi — Seviye A ise — ; oncelik = Öncelik [Yüksek | Orta | Düşük] ; karmasiklik = Karmaşıklık — Profili belirler: Basit → hafif, Orta → standart, Karmaşık → tam [Basit | Orta | Karmaşık] ; danisman = SAP danışmanı ; abap = ABAP geliştirici ; ui5 = UI5 geliştirici — Yoksa —
İyi: Tür: Arayüz/API + Fiori/UI5. Yaklaşım: Developer extensibility (ABAP Cloud, RAP). Hedef seviye A: yalnız released API (I_PurchaseOrderAPI01) kullanılır.
Kötü: Tür: Geliştirme. Yaklaşım: standart.
Denetim: GEN_001, GEN_002, META_001
İyi pratik: Clean core: önce key user, sonra on-stack ABAP Cloud, sonra side-by-side BTP değerlendirilir. Seviye A yalnız released API kullanır; B classic API, C dahili nesne, D önerilmeyen tekniklerdir (SAP clean core seviyeleri, 2025).

## 1.2 OData versiyonu ve backend modeli  [ağırlık 2 · Normal · yalnız Fiori / UI5 uygulaması, Arayüz / API]
Amaç: UI5 ve ABAP geliştiricinin aynı servis sözleşmesi üzerinde anlaşmasını sağlar.
Kural: OData versiyonunu, backend modelini, taslak (draft) kullanımını ve tüketilen standart API'leri sürüm ve release contract bilgisiyle yazın.
Alanlar: odata_versiyon = OData versiyonu [V2 | V4] (KARAR) ; backend_modeli = Backend modeli [RAP managed | RAP unmanaged | RAP managed + unmanaged save | CAP (BTP) | Yalnız standart API tüketimi] (KARAR) ; draft = Draft kullanımı — Evet / Hayır ve gerekçe (KARAR) ; ui_yaklasimi = UI yaklaşımı [Fiori elements | Freestyle UI5 | Flexible programming model | —] (KARAR) ; binding_tipi = Servis binding tipi [OData V4 – UI | OData V4 – Web API | OData V2 – UI | OData V2 – Web API] (KARAR)
Sütunlar: 0 Servis ID {SRV-nn} ; 1 Servis / API adı — Teknik ad ; 2 Özel mi, standart mı [Z | SAP | Dış] ; 3 Protokol ve versiyon ; 4 Release contract [C0 | C1 | C2 | —] ; 5 Amaç
İyi: OData V4, RAP managed + draft, servis binding ZUI_PO_SEND_LOG_O4 (OData V4 – UI). Tüketilen: I_PurchaseOrderAPI01 (C1).
Örnek satır: ["SRV-01", "ZUI_PO_SEND_LOG_O4", "Z", "OData V4 – UI", "—", "İzleme uygulamasının servisi"]
Denetim: GEN_001, GEN_002, META_002
İyi pratik: Fiori elements, desteklenen floorplan'lere uyan uygulamalarda önerilir; draft ve flexible column layout gibi özellikler ön yüz kodunu azaltır. Release contract: C0 genişlet, C1 sistem içi kullan, C2 uzak API olarak kullan.

## 2.1 Mevcut süreç (As-Is)  [ağırlık 6 · Kritik · tüm türler]
Amaç: Bugün işin nasıl yürüdüğünü ve sorunun tam olarak hangi adımda doğduğunu gösterir.
Kural: Süreci adım adım yazın; her adımda kim, hangi uygulamada, ne yapıyor. Sorunlu adımı işaretleyin, ölçülebilir etkisini ve gerçek bir örneği (belge no, tarih) verin.
Alanlar: ozet = Sürecin özeti — 2–3 cümle ; sorun = Somut sorun — Hangi adımda, ne oluyor ; etki = Ölçülebilir etki — Süre, hata oranı, maliyet; sayıyla ; ornek = Spesifik örnek — Belge no, tarih, sonuç ; hacim = Sıklık / hacim — Örn. 120 sipariş/gün
Sütunlar: 0 Adım {ASIS-nn} ; 1 Kim (rol) ; 2 Ne yapıyor — Eylem cümlesi ; 3 Uygulama / araç — Fiori App ID, işlem kodu, Excel… ; 4 Sorun var mı [Evet | Hayır] ; 5 Sorunun ölçülebilir etkisi
İyi: Adım 3: Satınalmacı onaylı siparişi 'Manage Purchase Orders' (F0842A) uygulamasından PDF alıp e-posta ile gönderir. Günde ~120 sipariş; 12.05.2026'da 4500001234 numaralı sipariş 2 gün geç iletildi.
Kötü: Mevcut süreç manuel ilerlemekte ve sorunlar yaşanmaktadır.
Örnek satır: ["ASIS-03", "Satınalmacı", "Onaylı siparişin PDF'ini e-posta ile tedarikçiye gönderir", "F0842A + Outlook", "Evet", "Sipariş başına ~4 dk; ayda ~15 unutulan gönderim"]
Denetim: GEN_001, GEN_002, PROC_002, QUAL_003
İyi pratik: İş ihtiyacı çözümden önce yazılır; hacim (adet/gün) belirtilmezse teknik tasarım yanlış boyutlanır.

## 2.2 Hedeflenen süreç (To-Be)  [ağırlık 8 · Kritik · tüm türler]
Amaç: Çözümü, kullanılan SAP teknolojisini ve her gereksinimin hangi As-Is sorununu çözdüğünü tanımlar.
Kural: Her gereksinimi tek cümle, tek davranış olacak şekilde EARS kalıbıyla yazın. Her REQ bir As-Is adımına bağlanır ve bir Given-When-Then kabul kriteri taşır.
Alanlar: cozum_ozeti = Çözüm özeti — 2–3 cümle (KARAR) ; teknoloji = Kullanılan SAP teknolojisi — Örn. RAP, Application Job, Communication Arrangement (KARAR) ; cozdugu_sorun = Çözdüğü As-Is sorunu — ASIS-nn kimlikleri
Sütunlar: 0 REQ ID {REQ-nn} ; 1 Gereksinim (EARS kalıbı) — Tek cümle, tek davranış ; 2 EARS tipi [Her zaman | Durum | Olay | Opsiyon | İstenmeyen | Bileşik] ; 3 Çözdüğü As-Is adımı — ASIS-nn ; 4 Kabul kriteri (Given-When-Then) ; 5 Öncelik [Must | Should | Could]
İyi: REQ-01: Satınalma siparişi onayı tamamlandığında (ReleaseIsNotCompleted = boş), sistem siparişi 5 dakika içinde tedarikçi portalına REST ile gönderir. Çözdüğü: ASIS-03.
Kötü: Sistem siparişleri otomatik ve hızlı şekilde ilgili yerlere iletecektir.
Örnek satır: ["REQ-01", "Satınalma siparişi onayı tamamlandığında sistem siparişi 5 dk içinde tedarikçi portalına gönderir.", "Olay", "ASIS-03", "Given onaylı 4500001234; When job çalışır; Then portal 201 döner ve log kaydı 'Gönderildi' olur.", "Must"]
Denetim: GEN_001, GEN_002, PROC_001, QUAL_003
İyi pratik: ISO/IEC/IEEE 29148: gereksinim gerekli, tekil, belirsiz olmayan ve doğrulanabilir olmalı. EARS kalıpları: '<sistem> … yapar' · 'While <durum>' · 'When <olay>' · 'Where <özellik>' · 'If <istenmeyen durum> then'.

## 2.3 Kullanım senaryoları / varyantlar  [ağırlık 4 · Normal · tüm türler]
Amaç: Ana akışı ve tüm varyant / istisna durumlarını adlandırır; test senaryolarının kaynağıdır.
Kural: Her senaryoya SC kimliği verin. Tetikleyiciyi, ön koşulu ve varyantı yazın; boş, sıfır ve sınır değer durumlarını atlamayın.
Sütunlar: 0 SC ID {SC-nn} ; 1 Senaryo adı ; 2 Tetikleyici ; 3 Ön koşul ; 4 Ana akış özeti ; 5 Varyant / istisna ; 6 İlgili REQ — REQ-nn
İyi: SC-02: Sipariş gönderildikten sonra değiştirilirse (LastChangeDateTime > gönderim zamanı) sipariş yeniden gönderilir, log'da sürüm 2 oluşur.
Örnek satır: ["SC-01", "Onaylı siparişin ilk gönderimi", "Application job, 5 dk'da bir", "Sipariş onaylı, tedarikçi portal kullanıcısı", "Seç → JSON oluştur → POST → log yaz", "Portal 5xx dönerse SC-03", "REQ-01"]
Denetim: GEN_001, GEN_002
İyi pratik: En sık atlanan konu kenar durumlardır: boş alan, null değer, aralık dışı girdi için davranış yazılmalıdır.

## 2.4 Süreç diyagramları  [ağırlık 2 · Normal · tüm türler]
Amaç: As-Is ve To-Be akışını görsel olarak özetler; adımların sırasını tartışmasız hale getirir.
Kural: Girdide bir diyagram varsa ya da anılıyorsa onu kaydedin; yoksa To-Be akışı, girdide anlatılan adımlardan `mermaid` kaynağı olarak çizilebilir (anlatılan adımı çizmek tasarım kararı değildir). Her kutu bir SC ya da STEP kimliği taşır. Adımların çoğu karar bekliyorsa bölümü gerekçesiyle geçersiz kılın; 'daha sonra eklenecek' yazmayın.
Sütunlar: 0 Diyagram ID {D-nn} ; 1 Tür [Akış | BPMN | Sekans | Durum] ; 2 Kapsadığı SC / REQ ; 3 Konum — Ek, bağlantı veya sayfa ; 4 Sürüm / tarih
İyi: D-01 To-Be akış (BPMN): Onay → Job → POST → Log; kutular STEP-01, STEP-02, STEP-03 kimlikleriyle etiketli.
Örnek satır: ["D-01", "Akış", "SC-01, SC-03", "Ek-1 sayfa 2", "v1 · 14.05.2026"]
Denetim: GEN_001, GEN_002
İyi pratik: Diyagram metni tekrar etmez, sırayı ve karar noktalarını gösterir. Obsidian'da Mermaid, Word/Excel'de yapıştırılmış görsel kullanılır.

## 2.5 Bağımlılıklar, varsayımlar, kapsam dışı  [ağırlık 6 · Kritik · tüm türler · en az 3 satır]
Amaç: Kapsam sınırını çizer: neye bağlıyız, neyi doğru kabul ettik, neyi bilerek yapmıyoruz.
Kural: Üç boyutun üçünü de doldurun: en az bir Bağımlılık, bir Varsayım, bir Kapsam dışı. Her satırın sahibi ve doğrulanma durumu olsun.
Alanlar: kapsam_ici = Kapsam içi — Tek cümle: bu geliştirme neyi yapar ; kapsam_siniri = Kapsam sınırı — Şirket kodu, belge türü, kanal
Sütunlar: 0 ID {DEP/ASM/OOS-nn} ; 1 Tür [Bağımlılık | Varsayım | Kapsam dışı] ; 2 Açıklama ; 3 Sahibi ; 4 Durum [Açık | Doğrulandı | Geçersiz] ; 5 Doğrulanma tarihi ; 6 Etkilediği bölüm
İyi: OOS-01 Kapsam dışı: Sözleşme (outline agreement) çağrı siparişleri gönderilmez. ASM-01 Varsayım: Portal aynı siparişi 'Idempotency-Key' başlığıyla tekilleştirir (portal ekibi, 10.05.2026'da doğrulandı).
Kötü: Diğer sistemlerin hazır olduğu varsayılmıştır.
Örnek satır: ["DEP-01", "Bağımlılık", "Portal REST uç noktası /api/v1/orders test ortamında açık olmalı", "Portal ekibi", "Doğrulandı", "10.05.2026", "3.10"]
Denetim: GEN_001, GEN_002, SCOPE_000, SCOPE_001, SCOPE_002, CONT_004, QUAL_007
İyi pratik: Kapsam 'İÇİNDE / DIŞINDA' olarak yazılır ve onay imzasıyla dondurulur; aksi halde kapsam sürekli genişler.
