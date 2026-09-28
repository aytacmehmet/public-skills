# Section writing guide · General and Functional

Generated file (source: assets/tanim.json). Column numbers start at 0 and follow the array order in the JSON. {X-nn} is the row id; [a | b] takes only these values; (KARAR) = do not decide yourself, mark it when the inputs do not state it.

## 1.1 Geliştirme türü (RICEF)  [weight 5 · Kritik · all types]
Note: The RICEF types are derived from the top-level 'turler' array; this section holds only fields.
Purpose: Fixes the development's identity, type and extension approach in one place; decides which sections are mandatory.
Rule: Write at least one RICEF type into the top-level `turler` array; the type table is derived from it. The extension approach and the target clean core level follow the decision in the inputs; give a reason for any level other than A.
Fields: gel_id = Geliştirme ID — e.g. GEL-MM-014 ; baslik = Geliştirme başlığı — One line; states the business outcome ; modul = Süreç alanı / modül — e.g. Satınalma (MM-PUR) ; sistem = Sistem [S/4HANA Cloud Public Edition | S/4HANA Cloud Private Edition] ; yaklasim = Genişletme yaklaşımı [Key user | Developer (ABAP Cloud) | Side-by-side (BTP)] (KARAR) ; clean_core = Hedef clean core seviyesi [A | B | C | D] (KARAR) ; cc_gerekce = A dışı seviye gerekçesi — — when the level is A ; oncelik = Öncelik [Yüksek | Orta | Düşük] ; karmasiklik = Karmaşıklık — Sets the profile: Basit → hafif, Orta → standart, Karmaşık → tam [Basit | Orta | Karmaşık] ; danisman = SAP danışmanı ; abap = ABAP geliştirici ; ui5 = UI5 geliştirici — — when none
Good: Tür: Arayüz/API + Fiori/UI5. Yaklaşım: Developer extensibility (ABAP Cloud, RAP). Hedef seviye A: yalnız released API (I_PurchaseOrderAPI01) kullanılır.
Bad: Tür: Geliştirme. Yaklaşım: standart.
Checks: GEN_001, GEN_002, META_001
Good practice: Clean core: consider key user first, then on-stack ABAP Cloud, then side-by-side BTP. Level A uses only released APIs; B classic APIs, C internal objects, D techniques that are not recommended (SAP clean core levels, 2025).

## 1.2 OData versiyonu ve backend modeli  [weight 2 · Normal · only Fiori / UI5 uygulaması, Arayüz / API]
Purpose: Makes the UI5 and ABAP developers agree on one service contract.
Rule: Write the OData version, the backend model, the use of draft and the consumed standard APIs with their version and release contract.
Fields: odata_versiyon = OData versiyonu [V2 | V4] (KARAR) ; backend_modeli = Backend modeli [RAP managed | RAP unmanaged | RAP managed + unmanaged save | CAP (BTP) | Yalnız standart API tüketimi] (KARAR) ; draft = Draft kullanımı — Evet / Hayır and the reason (KARAR) ; ui_yaklasimi = UI yaklaşımı [Fiori elements | Freestyle UI5 | Flexible programming model | —] (KARAR) ; binding_tipi = Servis binding tipi [OData V4 – UI | OData V4 – Web API | OData V2 – UI | OData V2 – Web API] (KARAR)
Columns: 0 Servis ID {SRV-nn} ; 1 Servis / API adı — Technical name ; 2 Özel mi, standart mı [Z | SAP | Dış] ; 3 Protokol ve versiyon ; 4 Release contract [C0 | C1 | C2 | —] ; 5 Amaç
Good: OData V4, RAP managed + draft, servis binding ZUI_PO_SEND_LOG_O4 (OData V4 – UI). Tüketilen: I_PurchaseOrderAPI01 (C1).
Example row: ["SRV-01", "ZUI_PO_SEND_LOG_O4", "Z", "OData V4 – UI", "—", "İzleme uygulamasının servisi"]
Checks: GEN_001, GEN_002, META_002
Good practice: Fiori elements is recommended for apps that fit a supported floorplan; features such as draft and flexible column layout reduce front-end code. Release contract: C0 extend, C1 use system-internally, C2 use as remote API.

## 2.1 Mevcut süreç (As-Is)  [weight 6 · Kritik · all types]
Purpose: Shows how the work runs today and at exactly which step the problem arises.
Rule: Write the process step by step: who does what, in which application. Flag the problem step, give its measurable effect and one real example (document number, date).
Fields: ozet = Sürecin özeti — 2–3 sentences ; sorun = Somut sorun — At which step, what happens ; etki = Ölçülebilir etki — Duration, error rate, cost; as numbers ; ornek = Spesifik örnek — Document number, date, outcome ; hacim = Sıklık / hacim — e.g. 120 sipariş/gün
Columns: 0 Adım {ASIS-nn} ; 1 Kim (rol) ; 2 Ne yapıyor — Action sentence ; 3 Uygulama / araç — Fiori App ID, transaction code, Excel… ; 4 Sorun var mı [Evet | Hayır] ; 5 Sorunun ölçülebilir etkisi
Good: Adım 3: Satınalmacı onaylı siparişi 'Manage Purchase Orders' (F0842A) uygulamasından PDF alıp e-posta ile gönderir. Günde ~120 sipariş; 12.05.2026'da 4500001234 numaralı sipariş 2 gün geç iletildi.
Bad: Mevcut süreç manuel ilerlemekte ve sorunlar yaşanmaktadır.
Example row: ["ASIS-03", "Satınalmacı", "Onaylı siparişin PDF'ini e-posta ile tedarikçiye gönderir", "F0842A + Outlook", "Evet", "Sipariş başına ~4 dk; ayda ~15 unutulan gönderim"]
Checks: GEN_001, GEN_002, PROC_002, QUAL_003
Good practice: The business need is written before the solution; without the volume (items/day) the technical design is sized wrongly.

## 2.2 Hedeflenen süreç (To-Be)  [weight 8 · Kritik · all types]
Purpose: Defines the solution, the SAP technology used and which As-Is problem each requirement solves.
Rule: Write every requirement as one sentence and one behaviour in an EARS pattern. Every REQ links to an As-Is step and carries a Given-When-Then acceptance criterion.
Fields: cozum_ozeti = Çözüm özeti — 2–3 sentences (KARAR) ; teknoloji = Kullanılan SAP teknolojisi — e.g. RAP, Application Job, Communication Arrangement (KARAR) ; cozdugu_sorun = Çözdüğü As-Is sorunu — ASIS-nn ids
Columns: 0 REQ ID {REQ-nn} ; 1 Gereksinim (EARS kalıbı) — One sentence, one behaviour ; 2 EARS tipi [Her zaman | Durum | Olay | Opsiyon | İstenmeyen | Bileşik] ; 3 Çözdüğü As-Is adımı — ASIS-nn ; 4 Kabul kriteri (Given-When-Then) ; 5 Öncelik [Must | Should | Could]
Good: REQ-01: Satınalma siparişi onayı tamamlandığında (ReleaseIsNotCompleted = boş), sistem siparişi 5 dakika içinde tedarikçi portalına REST ile gönderir. Çözdüğü: ASIS-03.
Bad: Sistem siparişleri otomatik ve hızlı şekilde ilgili yerlere iletecektir.
Example row: ["REQ-01", "Satınalma siparişi onayı tamamlandığında sistem siparişi 5 dk içinde tedarikçi portalına gönderir.", "Olay", "ASIS-03", "Given onaylı 4500001234; When job çalışır; Then portal 201 döner ve log kaydı 'Gönderildi' olur.", "Must"]
Checks: GEN_001, GEN_002, PROC_001, QUAL_003
Good practice: ISO/IEC/IEEE 29148: a requirement is necessary, singular, unambiguous and verifiable. EARS patterns: '<sistem> … yapar' · 'While <durum>' · 'When <olay>' · 'Where <özellik>' · 'If <istenmeyen durum> then'.

## 2.3 Kullanım senaryoları / varyantlar  [weight 4 · Normal · all types]
Purpose: Names the main flow and every variant / exception; the source of the test cases.
Rule: Give every scenario an SC id. Write the trigger, the precondition and the variant; do not skip empty, zero and boundary cases.
Columns: 0 SC ID {SC-nn} ; 1 Senaryo adı ; 2 Tetikleyici ; 3 Ön koşul ; 4 Ana akış özeti ; 5 Varyant / istisna ; 6 İlgili REQ — REQ-nn
Good: SC-02: Sipariş gönderildikten sonra değiştirilirse (LastChangeDateTime > gönderim zamanı) sipariş yeniden gönderilir, log'da sürüm 2 oluşur.
Example row: ["SC-01", "Onaylı siparişin ilk gönderimi", "Application job, 5 dk'da bir", "Sipariş onaylı, tedarikçi portal kullanıcısı", "Seç → JSON oluştur → POST → log yaz", "Portal 5xx dönerse SC-03", "REQ-01"]
Checks: GEN_001, GEN_002
Good practice: Edge cases are what gets skipped most: write the behaviour for empty fields, null values and out-of-range input.

## 2.4 Süreç diyagramları  [weight 2 · Normal · all types]
Purpose: Summarises the As-Is and To-Be flow visually; makes the order of steps indisputable.
Rule: If the inputs contain or cite a diagram, record it; otherwise the To-Be flow may be drawn as `mermaid` source from the steps the inputs describe (drawing a stated step is not a design decision). Every box carries an SC or STEP id. If most steps wait for decisions, switch the section off with that reason; do not write 'to be added later'.
Columns: 0 Diyagram ID {D-nn} ; 1 Tür [Akış | BPMN | Sekans | Durum] ; 2 Kapsadığı SC / REQ ; 3 Konum — Attachment, link or page ; 4 Sürüm / tarih
Good: D-01 To-Be akış (BPMN): Onay → Job → POST → Log; kutular STEP-01, STEP-02, STEP-03 kimlikleriyle etiketli.
Example row: ["D-01", "Akış", "SC-01, SC-03", "Ek-1 sayfa 2", "v1 · 14.05.2026"]
Checks: GEN_001, GEN_002
Good practice: The diagram does not repeat the text; it shows order and decision points. Mermaid in Obsidian, a pasted image in Word/Excel.

## 2.5 Bağımlılıklar, varsayımlar, kapsam dışı  [weight 6 · Kritik · all types · at least 3 rows]
Purpose: Draws the scope boundary: what we depend on, what we assume to be true, what we deliberately do not do.
Rule: Fill all three dimensions: at least one Bağımlılık, one Varsayım, one Kapsam dışı. Every row has an owner and a verification status.
Fields: kapsam_ici = Kapsam içi — One sentence: what this development does ; kapsam_siniri = Kapsam sınırı — Company code, document type, channel
Columns: 0 ID {DEP/ASM/OOS-nn} ; 1 Tür [Bağımlılık | Varsayım | Kapsam dışı] ; 2 Açıklama ; 3 Sahibi ; 4 Durum [Açık | Doğrulandı | Geçersiz] ; 5 Doğrulanma tarihi ; 6 Etkilediği bölüm
Good: OOS-01 Kapsam dışı: Sözleşme (outline agreement) çağrı siparişleri gönderilmez. ASM-01 Varsayım: Portal aynı siparişi 'Idempotency-Key' başlığıyla tekilleştirir (portal ekibi, 10.05.2026'da doğrulandı).
Bad: Diğer sistemlerin hazır olduğu varsayılmıştır.
Example row: ["DEP-01", "Bağımlılık", "Portal REST uç noktası /api/v1/orders test ortamında açık olmalı", "Portal ekibi", "Doğrulandı", "10.05.2026", "3.10"]
Checks: GEN_001, GEN_002, SCOPE_000, SCOPE_001, SCOPE_002, CONT_004, QUAL_007
Good practice: Scope is written as IN / OUT and frozen by sign-off; otherwise it keeps growing.
