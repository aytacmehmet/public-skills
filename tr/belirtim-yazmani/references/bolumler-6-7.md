# Section writing guide · Test and Operations

Generated file (source: assets/tanim.json). Column numbers start at 0 and follow the array order in the JSON. {X-nn} is the row id; [a | b] takes only these values; (KARAR) = do not decide yourself, mark it when the inputs do not state it.

## 6.1 Test senaryoları ve verileri  [weight 10 · Kritik · all types · at least 2 rows]
Purpose: Defines with real data the scenarios that must run for the development to be accepted.
Rule: At least 2 cases; at least one happy path, at least one negative/boundary. Every case has real test data (document number, supplier, company code), steps, expected result and expected MSG.
Columns: 0 TC ID {TC-nn} ; 1 Senaryo türü [Mutlu yol | Negatif | Sınır] ; 2 Kapsadığı REQ / SC ; 3 Ön koşul ve test verisi — Real document number, master data ; 4 Adımlar ; 5 Beklenen sonuç — Observable ; 6 Beklenen MSG — MSG-nn ; 7 Test tipi [ABAP Unit | Entegrasyon | UI (OPA5) | UAT] ; 8 Durum [Planlandı | Geçti | Kaldı]
Good: TC-03 Negatif: sipariş 4500001240, tedarikçi 17300001, portal 500 döner → 3 deneme sonrası Status = 'E', MSG-03 (E) log'da, izleme uygulamasında kırmızı.
Bad: Çeşitli siparişlerle test edilir ve doğru çalıştığı görülür.
Example row: ["TC-01", "Mutlu yol", "REQ-01, SC-01", "Sipariş 4500001234, tedarikçi 17300001, şirket kodu 1710, onaylı", "1) Job'u çalıştır 2) İzleme uygulamasını aç", "Portal 201; log Status = 'S'; gönderim ≤ 5 dk", "MSG-02", "Entegrasyon", "Planlandı"]
Checks: GEN_001, GEN_002, TEST_001, TEST_002, CONT_002, QUAL_004, QUAL_005
Good practice: The acceptance criterion reads 'when X then Y, observed at Z'. ABAP Unit unit tests and OPA5/QUnit UI tests are named as test types.

## 6.2 İzlenebilirlik matrisi  [weight 4 · Bonus · all types]
Note: Fully derived: the script generates it from id references. Never written into the JSON.
Purpose: Proves in one table that every requirement is designed, coded and tested.
Rule: One row per REQ: SC → STEP → OBJ/MAP → MSG → TC. An empty cell = an uncovered requirement.
Good: REQ-01 → SC-01, SC-03 → STEP-01, STEP-02 → OBJ-01, OBJ-03 → MAP-01, MAP-02 → MSG-01, MSG-03 → TC-01, TC-03 · Kapsama: Tam.
Checks: GEN_001, GEN_002
Good practice: Two-way traceability: every REQ links to at least one TC and every TC to at least one REQ (ISO/IEC/IEEE 29148).

## 6.3 Kod kalitesi ve doğrulama kanıtı  [weight 3 · Bonus · all types]
Purpose: Records with which tools the code was verified before delivery, and the result.
Rule: For every piece of evidence write the tool, the target, the result and where the evidence is. Record open findings in 7.3 and in the readiness penalty table.
Columns: 0 QA ID {QA-nn} ; 1 Kanıt [ATC | ABAP Unit | CVA / güvenlik | UI5 lint | OPA5-QUnit | Kod incelemesi | İstisna kaydı] ; 2 Araç / varyant ; 3 Hedef ; 4 Sonuç ; 5 Kanıt konumu ; 6 Tarih
Good: QA-01: ATC, varyant ABAP_CLOUD_DEVELOPMENT_DEFAULT · hedef öncelik 1–2 bulgu = 0 · sonuç 0/0 · kanıt: ATC sonuç ekran görüntüsü, 20.05.2026.
Example row: ["QA-01", "ATC", "ABAP_CLOUD_DEVELOPMENT_DEFAULT", "Öncelik 1–2 bulgu = 0", "0 / 0", "Ek-3 ATC sonucu", "20.05.2026"]
Checks: GEN_001, GEN_002
Good practice: ABAP Test Cockpit is the main tool of clean core governance; priority 1 and 2 findings block release, exemptions are recorded.

## 7.1 Loglama ve izlenebilirlik  [weight 3 · Normal · all types]
Purpose: Defines what to look at when a problem occurs in production.
Rule: For every log event write the level, the target (application log object/subobject), the key fields written and the retention period.
Columns: 0 LOG ID {LOG-nn} ; 1 Olay ; 2 Seviye [Info | Warning | Error] ; 3 Hedef — Application log object / subobject ; 4 İçerik (anahtar alanlar) ; 5 Saklama süresi ; 6 İzleme uygulaması
Good: LOG-02: Gönderim hatası · Error · Application Log nesnesi ZMM_PO_SEND / alt nesne OUTBOUND · sipariş no, HTTP kodu, deneme sayısı · 90 gün.
Example row: ["LOG-02", "Gönderim hatası", "Error", "ZMM_PO_SEND / OUTBOUND", "Sipariş no, HTTP kodu, deneme sayısı", "90 gün", "Gönderim izleme (UI-01) → Application Logs"]
Checks: GEN_001, GEN_002
Good practice: In ABAP Cloud the application log uses a released API; navigation from the monitoring app to the log by the log key (order number) is planned.

## 7.2 Transport ve devreye alma  [weight 3 · Normal · all types]
Purpose: Defines in which order and with which transport vehicle the objects go live, and the manual steps.
Rule: Write the transport units (transport request, software collection) and the manual steps in every system, in order; add the rollback plan.
Fields: bilesen_paket = Yazılım bileşeni / paket ; transportlar = Transport request(ler) — BİLGİ BEKLİYOR when unknown ; software_collection = Software collection (key user) — — when none ; canli_tarihi = Planlanan canlı tarihi
Columns: 0 Sıra ; 1 Adım ; 2 Taşınan / yapılan — Transport, collection, manual step ; 3 Sistem — Geliştirme | Test | Üretim ; 4 Sorumlu ; 5 Geri alma (KARAR)
Good: Sıra 3: Test ve üretimde communication arrangement ZCS_PO_SUPPLIER_PORTAL elle oluşturulur (Basis, portal OAuth istemci bilgileriyle); geri alma: arrangement pasifleştirilir.
Example row: ["3", "Communication arrangement oluştur", "ZCS_PO_SUPPLIER_PORTAL, elle", "Test, Üretim", "Basis", "Arrangement pasifleştirilir"]
Checks: GEN_001, GEN_002
Good practice: In the 3-system Public Cloud landscape, developer objects move by transport request, key user extensions by software collection; business configuration comes from the customizing tenant.

## 7.3 Açık noktalar  [weight 2 · Normal · all types]
Purpose: Makes every undecided topic visible with its owner and date.
Rule: Every open point has an owner (name or role) and a readiness penalty category; the target date is written only when given, otherwise it stays —. No BEKLİYOR marker in these rows. Once decided, the 'Karar' column is filled and the status becomes 'Kararlaştırıldı'. If there is no open point at all, the section is switched off with the reason 'Açık nokta yok'.
Columns: 0 OPEN ID {OPEN-nn} ; 1 Konu — As a question; except the rows 'DOĞRULANACAK nesneler: …' and 'Teknik taslak geliştirici onayı bekliyor: …' ; 2 Etkilediği bölüm — Section numbers, comma-separated: 3.4, 3.5 ; 3 Sahibi — Name or role ; 4 Hedef tarih — When given; otherwise — ; 5 Durum [Açık | Kararlaştırıldı | Kapandı] ; 6 Karar — — until decided ; 7 Hazırlık cezası kategorisi [Yayına alınmamış nesne | Açık ATC/CVA bulgusu | Tasarım/sözleşme açığı | Geçici çözüm / hardcode | Karar bekleyen konu | İstisna kaydı yapılmamış bulgu | —]
Good: OPEN-02: Portal 409 yanıtı başarı mı sayılacak? · Sahibi: portal ekibi · 22.05.2026 · Kategori: Tasarım/sözleşme açığı · Karar: başarı sayılır (INT-01 güncellendi).
Example row: ["OPEN-02", "Portal 409 yanıtı başarı mı sayılacak?", "3.10, 3.9", "Portal ekibi", "22.05.2026", "Kararlaştırıldı", "Başarı sayılır", "Tasarım/sözleşme açığı"]
Checks: GEN_001, GEN_002, OPEN_001, CONT_003
Good practice: An FS with open points is not handed to development, or the sections an open point affects are marked explicitly; the signed version is archived.
