# Section writing guide · Technical

Generated file (source: assets/tanim.json). Column numbers start at 0 and follow the array order in the JSON. {X-nn} is the row id; [a | b] takes only these values; (KARAR) = do not decide yourself, mark it when the inputs do not state it.

## 3.1 Ön koşullar (ana veri / uyarlama)  [weight 4 · Normal · all types]
Purpose: Lists what must be ready in the system before development and testing start.
Rule: Write every precondition with its type, its concrete value and the system/tenant it is needed in. 'Hazır mı' is 'Hayır' unless the inputs report it ready.
Columns: 0 PRE ID {PRE-nn} ; 1 Tür [Ana veri | Uyarlama | Kapsam öğesi | İletişim düzenlemesi | Yetki] ; 2 Nesne / değer — Concrete value ; 3 Sistem / tenant ; 4 Sorumlu ; 5 Hazır mı [Evet | Hayır]
Good: PRE-02 Uyarlama: Satınalma siparişi esnek iş akışı etkin (Manage Workflows for Purchase Orders), şirket kodu 1710. Test tenant'ında hazır.
Example row: ["PRE-01", "Ana veri", "Tedarikçi 17300001, portal e-posta alanı dolu", "Test", "Danışman", "Evet"]
Checks: GEN_001, GEN_002
Good practice: In Public Cloud, business configuration is done in the customizing tenant and moved by transport; a communication arrangement is set up separately in every system.

## 3.2 Seçim ekranı tasarımı  [weight 3 · Normal · only Rapor]
Purpose: Defines at field level the criteria the report or job runs with.
Rule: For every selection field write the source field, type, mandatory flag, single/multiple/range selection, default and value help.
Columns: 0 Alan ID {SEL-nn} ; 1 Etiket ; 2 Kaynak (CDS.alan) ; 3 Tip / uzunluk ; 4 Zorunlu [Evet | Hayır] ; 5 Seçim türü [Tek | Çoklu | Aralık] ; 6 Varsayılan ; 7 Değer yardımı ; 8 Doğrulama → MSG — MSG-nn
Good: CompanyCode · I_PurchaseOrderAPI01.CompanyCode · CHAR(4) · zorunlu · çoklu · varsayılan 1710 · değer yardımı I_CompanyCodeStdVH.
Example row: ["SEL-01", "Şirket kodu", "I_PurchaseOrderAPI01.CompanyCode", "CHAR(4)", "Evet", "Çoklu", "1710", "I_CompanyCodeStdVH", "MSG-05"]
Checks: GEN_001, GEN_002, COND_003
Good practice: In the cloud the selection screen is a Fiori elements filter bar or application job parameters.

## 3.3 Fiori / UI5 tasarımı  [weight 8 · Kritik · only Fiori / UI5 uygulaması]
Purpose: Defines the floorplan, the elements and their behaviour so the UI5 developer can build the screen without asking.
Rule: Write the floorplan and its reason. For every screen element give the label, the behaviour condition, the annotation/control and the STEP it triggers.
Fields: floorplan = Floorplan [List Report + Object Page | Worklist | Analytical List Page | Overview Page | Freestyle] (KARAR) ; floorplan_gerekce = Floorplan gerekçesi ; semantic_object = Semantic object – action — e.g. PurchaseOrderSendLog-monitor ; launchpad = Launchpad yerleşimi — Space / page / tile ; cihaz_dil = Cihaz ve dil — e.g. desktop, tablet; TR, EN ; anahtar_kullanici = Anahtar kullanıcı uyarlaması — Allowed or not
Columns: 0 UI ID {UI-nn} ; 1 Ekran / bölüm ; 2 Öğe türü [Filtre | Kolon | Alan | Aksiyon | Sekme] ; 3 Etiket ; 4 Davranış koşulu — When visible / mandatory / read-only ; 5 Annotation / kontrol ; 6 Tetiklediği STEP — STEP-nn ; 7 Not
Good: UI-04 Aksiyon 'Yeniden gönder': yalnız Status = 'E' satırlarda etkin; @UI.lineItem type #FOR_ACTION, dataAction 'resend'; STEP-07'yi çağırır.
Bad: Kullanıcı dostu bir ekran tasarlanacaktır.
Example row: ["UI-04", "Liste", "Aksiyon", "Yeniden gönder", "Yalnız Status = 'E' iken etkin", "@UI.lineItem #FOR_ACTION 'resend'", "STEP-07", "Çoklu seçim desteklenir"]
Checks: GEN_001, GEN_002, COND_001
Good practice: Fiori elements floorplans: list report, worklist, object page, analytical list page, overview page. If the design does not fit them, freestyle or the flexible programming model is chosen and the reason is written.

## 3.4 Arayüz ve veri haritalama  [weight 10 · Kritik · only Arayüz / API, Fiori / UI5 uygulaması]
Note: For type U without an external interface this section maps source (CDS / API field) → service entity property: yon and comm_scenario are —, protokol is the OData version of 1.2, tetikleyici is the user action.
Purpose: Defines where every field comes from, where it goes and how it is transformed on the way.
Rule: Every row is one field mapping: source object.field → target object.field, data type, mandatory flag, transformation rule and one real example value.
Fields: yon = Yön [Giden | Gelen | Çift yönlü] (KARAR) ; protokol = Protokol / format — REST-JSON, OData, SOAP, event, file (KARAR) ; tetikleyici = Tetikleyici ve sıklık — Event, job interval, user action (KARAR) ; hacim = Hacim — Items/day, largest message ; comm_scenario = Communication scenario — — when none
Columns: 0 MAP ID {MAP-nn} ; 1 Kaynak nesne — CDS / API / file ; 2 Kaynak alan ; 3 Hedef nesne ; 4 Hedef alan ; 5 Veri tipi (uzunluk) ; 6 Zorunlu [Evet | Hayır] ; 7 Dönüşüm kuralı — 'Birebir' when none ; 8 Örnek değer — Source → target
Good: MAP-03: I_PurchaseOrderItemAPI01.OrderQuantity (QUAN 13,3) → JSON items[].quantity (number, zorunlu); birim ISO koduna çevrilir; örnek 120.000 → 120.
Bad: Sipariş bilgileri ilgili alanlara aktarılır.
Example row: ["MAP-01", "I_PurchaseOrderAPI01", "PurchaseOrder", "JSON gövdesi", "orderNumber", "CHAR(10) → string", "Evet", "Birebir, baştaki sıfırlar korunur", "4500001234 → \"4500001234\""]
Checks: GEN_001, GEN_002, MAP_001, COND_002, QUAL_002
Good practice: An interface FS holds protocol, field mapping and error handling together. The source is a released CDS view / API name, not a table name.

## 3.5 Adım adım işlem mantığı  [weight 12 · Kritik · all types · at least 3 rows]
Purpose: Gives the developer the logic to code as ordered, individually verifiable steps.
Rule: Write at least 3 steps. Every step names a concrete SAP object (CDS, API, class, BAdI); write which MSG is raised on error and the commit/rollback behaviour.
Columns: 0 STEP ID {STEP-nn} ; 1 Sıra — 1, 2, 3… ; 2 Tetikleyici / koşul ; 3 İşlem — What is done, with which data ; 4 SAP nesnesi — CDS | API | class | BAdI name ; 5 Girdi → çıktı ; 6 Hata durumu → MSG — MSG-nn ; 7 Commit / rollback — What is persisted, what is rolled back ; 8 İlgili REQ / SC
Good: STEP-02: I_PurchaseOrderAPI01'den ReleaseIsNotCompleted = boş ve LastChangeDateTime > son çalışma zamanı olan siparişleri oku. Kayıt yoksa MSG-01 (I) yaz ve bitir; veritabanı değişikliği yok.
Bad: Gerekli kontroller yapıldıktan sonra ilgili tablolardan veriler okunur ve sisteme kaydedilir.
Example row: ["STEP-02", "2", "Job başladı", "Onayı tamamlanmış ve son çalışmadan sonra değişmiş siparişleri oku; eşleme MAP-01, MAP-02", "I_PurchaseOrderAPI01", "Son çalışma zamanı → sipariş listesi", "Kayıt yok → MSG-01", "Değişiklik yok", "REQ-01, SC-01"]
Checks: GEN_001, GEN_002, ALGO_001, ALGO_002, ALGO_003, CONT_001, QUAL_001
Good practice: In RAP the commit belongs to the framework: persistence happens in the save sequence, COMMIT WORK is not written. ABAP Cloud uses only released APIs; ATC checks this.

## 3.6 Rapor / ALV çıktı tasarımı  [weight 3 · Normal · only Rapor]
Purpose: Defines the columns, sorting, totals and navigation of the output.
Rule: For every column write the header, source field, type, total/subtotal, default visibility and navigation target.
Fields: cikti_tipi = Çıktı tipi [Fiori elements List Report | Analytical List Page | ALV (Private) | Dosya] (KARAR) ; disa_aktarma = Dışa aktarma — Excel, PDF ; varyant = Varyant yönetimi — User / global variant
Columns: 0 Kolon ID {COL-nn} ; 1 Sıra ; 2 Başlık ; 3 Kaynak (CDS.alan) ; 4 Tip ; 5 Toplam / ara toplam ; 6 Sıralama / gruplama ; 7 Varsayılan görünür [Evet | Hayır] ; 8 Navigasyon — Semantic object-action
Good: Kolon 5: 'Net tutar' · I_PurchaseOrderItemAPI01.NetAmount · CURR(15,2) · toplam alınır, para birimine göre · varsayılan görünür.
Example row: ["COL-05", "5", "Net tutar", "I_PurchaseOrderItemAPI01.NetAmount", "CURR(15,2)", "Toplam, para birimine göre", "—", "Evet", "—"]
Checks: GEN_001, GEN_002, COND_004
Good practice: In the cloud the report output is mostly a Fiori elements list report or analytical list page; classic ALV is meaningful only in Private Edition.

## 3.7 Ekran–alan–kaynak matrisi  [weight 6 · Bonus · all types]
Purpose: Traces every screen field to its OData property, CDS field and source object; the contract between UI5 and ABAP.
Rule: Open one row per UI element of 3.3; the chain screen → OData → CDS → source must be complete.
Columns: 0 UI ID — From 3.3 ; 1 Ekran alanı ; 2 OData entity.property ; 3 CDS view.alan ; 4 Kaynak (tablo.alan / API) ; 5 Düzenlenebilir [Evet | Hayır] ; 6 Değer yardımı ; 7 MAP ref — MAP-nn
Good: UI-02 'Durum' → SendLog.Status → ZC_PO_SEND_LOG.Status → ZPO_SEND_LOG.STATUS; salt okunur; değer yardımı ZI_PO_SEND_STATUS_VH.
Example row: ["UI-02", "Durum", "SendLog.Status", "ZC_PO_SEND_LOG.Status", "ZPO_SEND_LOG.STATUS", "Hayır", "ZI_PO_SEND_STATUS_VH", "—"]
Checks: GEN_001, GEN_002
Good practice: This matrix guarantees that the UI5 and ABAP developers use the same field name and shortens test data preparation.

## 3.8 Durum makinesi / durum sözlüğü  [weight 5 · Bonus · all types]
Purpose: Defines the states the object can take, their meaning and the allowed transitions.
Rule: For every state write code, name, meaning, entry condition and allowed transitions; mark the final states.
Columns: 0 ST ID {ST-nn} ; 1 Durum kodu ; 2 Durum adı ; 3 Anlamı ; 4 Giriş koşulu (STEP) ; 5 İzinli geçişler — Code → code (trigger) ; 6 Son durum mu [Evet | Hayır]
Good: ST-03 'E' Hata: portal 4xx/5xx döndü veya zaman aşımı. Geçişler: E → Q (yeniden gönder aksiyonu), E → X (iptal). Son durum değil.
Example row: ["ST-03", "E", "Hata", "Gönderim başarısız", "STEP-05 hata dalı", "E → Q (resend), E → X (iptal)", "Hayır"]
Checks: GEN_001, GEN_002
Good practice: State name and code are written identically on screen, in the log and in tests; one dictionary is used.

## 3.9 İdempotency, tekrar ve kurtarma  [weight 5 · Bonus · all types]
Purpose: Defines what the system does when the same request arrives twice, an operation stops halfway, or a retry happens.
Rule: For every topic write the decision and the related STEP: idempotency key, retry policy, timeout, partial success, reprocessing.
Columns: 0 IDM ID {IDM-nn} ; 1 Konu [İdempotency anahtarı | Yinelenen istek | Tekrar politikası | Zaman aşımı | Kısmi başarı | Yeniden işleme | Kilitleme] ; 2 Karar — With concrete values (KARAR) ; 3 İlgili STEP ; 4 Doğrulayan TC
Good: IDM-01: Anahtar = PurchaseOrder + LastChangeDateTime; aynı anahtar ikinci kez gelirse POST atılmaz, log'a MSG-06 (I) yazılır.
Example row: ["IDM-02", "Tekrar politikası", "HTTP 5xx ve zaman aşımında 3 deneme: 1, 5, 15 dk; sonra Status = 'E'", "STEP-05", "TC-04"]
Checks: GEN_001, GEN_002
Good practice: If interfaces do not specify fallback behaviour, production sees duplicated or lost data; every retry scenario needs a test.

## 3.10 Entegrasyon sözleşmeleri  [weight 5 · Bonus · all types]
Purpose: Records the technical agreement with the counterpart system: endpoint, authentication, SLA, error contract.
Rule: For every integration write the endpoint, the communication scenario/arrangement name, the authentication, the SLA and the HTTP code → behaviour mapping.
Columns: 0 INT ID {INT-nn} ; 1 Karşı sistem ; 2 Yön [Giden | Gelen] ; 3 Protokol / format (KARAR) ; 4 Uç nokta / servis ; 5 Communication scenario ; 6 Kimlik doğrulama (KARAR) ; 7 SLA / hacim ; 8 Hata sözleşmesi — Code → behaviour (KARAR) ; 9 Versiyonlama
Good: INT-01: POST /api/v1/orders · OAuth 2.0 client credentials · ZCS_PO_SUPPLIER_PORTAL · 201 başarı, 409 yinelenen (başarı sayılır), 4xx kalıcı hata, 5xx tekrar denenir · yanıt ≤ 3 sn.
Example row: ["INT-01", "Tedarikçi portalı", "Giden", "REST / JSON", "POST /api/v1/orders", "ZCS_PO_SUPPLIER_PORTAL", "OAuth 2.0 client credentials", "≤ 3 sn; 120/gün", "201 ok · 409 ok · 4xx kalıcı · 5xx tekrar", "URL'de v1"]
Checks: GEN_001, GEN_002
Good practice: In Public Cloud an external connection is built through communication scenario → communication arrangement → communication system; the arrangement is created manually in every system.

## 3.11 Performans kriterleri  [weight 3 · Bonus · all types]
Purpose: Defines acceptable duration and data volume as measurable targets.
Rule: Every target contains a scenario, a volume and a measurement method; no adjective such as 'fast'.
Columns: 0 PERF ID {PERF-nn} ; 1 Senaryo ; 2 Veri hacmi ; 3 Hedef — Duration, memory, count (KARAR) ; 4 Ölçüm yöntemi ; 5 Tasarım önlemi — Paging, packaging, index…
Good: PERF-01: 500 siparişlik job çalışması ≤ 10 dk (Application Jobs uygulamasındaki çalışma süresi); liste ilk açılış ≤ 2 sn, 10.000 log satırı.
Example row: ["PERF-01", "Job çalışması", "500 sipariş / çalışma", "≤ 10 dk", "Application Jobs çalışma süresi", "100'lük paketlerle işleme"]
Checks: GEN_001, GEN_002
Good practice: Technical design is impossible without volume figures; targets are tied to test cases.
