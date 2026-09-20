# Bölüm yazım bilgisi · Teknik

Üretilmiş dosyadır (kaynak: assets/tanim.json). Sütun numaraları 0'dan başlar ve JSON'daki dizi sırasıdır. {X-nn} satır kimliğidir; [a | b] yalnız bu değerleri alır; (KARAR) = kararı sen verme, girdide yoksa işaretle.

## 3.1 Ön koşullar (ana veri / uyarlama)  [ağırlık 4 · Normal · tüm türler]
Amaç: Geliştirme ve test başlamadan sistemde hazır olması gerekenleri listeler.
Kural: Her ön koşulu türüyle, somut değeriyle ve hangi sistemde/tenant'ta gerektiğiyle yazın. 'Hazır mı', hazır olduğu girdide bildirilmedikçe 'Hayır'dır.
Sütunlar: 0 PRE ID {PRE-nn} ; 1 Tür [Ana veri | Uyarlama | Kapsam öğesi | İletişim düzenlemesi | Yetki] ; 2 Nesne / değer — Somut değer ; 3 Sistem / tenant ; 4 Sorumlu ; 5 Hazır mı [Evet | Hayır]
İyi: PRE-02 Uyarlama: Satınalma siparişi esnek iş akışı etkin (Manage Workflows for Purchase Orders), şirket kodu 1710. Test tenant'ında hazır.
Örnek satır: ["PRE-01", "Ana veri", "Tedarikçi 17300001, portal e-posta alanı dolu", "Test", "Danışman", "Evet"]
Denetim: GEN_001, GEN_002
İyi pratik: Public Cloud'da iş yapılandırması customizing tenant'ında yapılır ve transport ile taşınır; communication arrangement her sistemde ayrıca kurulur.

## 3.2 Seçim ekranı tasarımı  [ağırlık 3 · Normal · yalnız Rapor]
Amaç: Raporun veya job'un hangi kriterlerle çalışacağını alan düzeyinde tanımlar.
Kural: Her seçim alanı için kaynak alanı, tipi, zorunluluğu, tek/çoklu/aralık seçimini, varsayılanı ve değer yardımını yazın.
Sütunlar: 0 Alan ID {SEL-nn} ; 1 Etiket ; 2 Kaynak (CDS.alan) ; 3 Tip / uzunluk ; 4 Zorunlu [Evet | Hayır] ; 5 Seçim türü [Tek | Çoklu | Aralık] ; 6 Varsayılan ; 7 Değer yardımı ; 8 Doğrulama → MSG — MSG-nn
İyi: CompanyCode · I_PurchaseOrderAPI01.CompanyCode · CHAR(4) · zorunlu · çoklu · varsayılan 1710 · değer yardımı I_CompanyCodeStdVH.
Örnek satır: ["SEL-01", "Şirket kodu", "I_PurchaseOrderAPI01.CompanyCode", "CHAR(4)", "Evet", "Çoklu", "1710", "I_CompanyCodeStdVH", "MSG-05"]
Denetim: GEN_001, GEN_002, COND_003
İyi pratik: Cloud'da seçim ekranı, Fiori elements filtre çubuğu veya application job parametreleri olarak gerçekleşir.

## 3.3 Fiori / UI5 tasarımı  [ağırlık 8 · Kritik · yalnız Fiori / UI5 uygulaması]
Amaç: UI5 geliştiricinin ekranı sormadan kurabilmesi için floorplan'i, öğeleri ve davranışları tanımlar.
Kural: Floorplan'i ve gerekçesini yazın. Her ekran öğesi için etiketi, davranış koşulunu, annotation/kontrolü ve tetiklediği STEP'i verin.
Alanlar: floorplan = Floorplan [List Report + Object Page | Worklist | Analytical List Page | Overview Page | Freestyle] (KARAR) ; floorplan_gerekce = Floorplan gerekçesi ; semantic_object = Semantic object – action — Örn. PurchaseOrderSendLog-monitor ; launchpad = Launchpad yerleşimi — Space / page / tile ; cihaz_dil = Cihaz ve dil — Örn. masaüstü, tablet; TR, EN ; anahtar_kullanici = Anahtar kullanıcı uyarlaması — İzinli mi
Sütunlar: 0 UI ID {UI-nn} ; 1 Ekran / bölüm ; 2 Öğe türü [Filtre | Kolon | Alan | Aksiyon | Sekme] ; 3 Etiket ; 4 Davranış koşulu — Görünür / zorunlu / salt okunur ne zaman ; 5 Annotation / kontrol ; 6 Tetiklediği STEP — STEP-nn ; 7 Not
İyi: UI-04 Aksiyon 'Yeniden gönder': yalnız Status = 'E' satırlarda etkin; @UI.lineItem type #FOR_ACTION, dataAction 'resend'; STEP-07'yi çağırır.
Kötü: Kullanıcı dostu bir ekran tasarlanacaktır.
Örnek satır: ["UI-04", "Liste", "Aksiyon", "Yeniden gönder", "Yalnız Status = 'E' iken etkin", "@UI.lineItem #FOR_ACTION 'resend'", "STEP-07", "Çoklu seçim desteklenir"]
Denetim: GEN_001, GEN_002, COND_001
İyi pratik: Fiori elements floorplan'leri: list report, worklist, object page, analytical list page, overview page. Tasarım bunlara uymuyorsa freestyle veya flexible programming model seçilir; gerekçe yazılır.

## 3.4 Arayüz ve veri haritalama  [ağırlık 10 · Kritik · yalnız Arayüz / API, Fiori / UI5 uygulaması]
Not: Dış arayüzü olmayan U türünde bu bölüm kaynak (CDS / API alanı) → servis entity property eşlemesidir: yon ve comm_scenario —, protokol 1.2'deki OData versiyonu, tetikleyici kullanıcı eylemidir.
Amaç: Her alanın nereden geldiğini, nereye gittiğini ve yolda nasıl dönüştüğünü tanımlar.
Kural: Her satır tek alan eşlemesidir: kaynak nesne.alan → hedef nesne.alan, veri tipi, zorunluluk, dönüşüm kuralı ve gerçek bir örnek değer.
Alanlar: yon = Yön [Giden | Gelen | Çift yönlü] (KARAR) ; protokol = Protokol / format — REST-JSON, OData, SOAP, olay, dosya (KARAR) ; tetikleyici = Tetikleyici ve sıklık — Olay, job aralığı, kullanıcı aksiyonu (KARAR) ; hacim = Hacim — Adet/gün, en büyük mesaj ; comm_scenario = Communication scenario — Yoksa —
Sütunlar: 0 MAP ID {MAP-nn} ; 1 Kaynak nesne — CDS / API / dosya ; 2 Kaynak alan ; 3 Hedef nesne ; 4 Hedef alan ; 5 Veri tipi (uzunluk) ; 6 Zorunlu [Evet | Hayır] ; 7 Dönüşüm kuralı — Yoksa 'Birebir' ; 8 Örnek değer — Kaynak → hedef
İyi: MAP-03: I_PurchaseOrderItemAPI01.OrderQuantity (QUAN 13,3) → JSON items[].quantity (number, zorunlu); birim ISO koduna çevrilir; örnek 120.000 → 120.
Kötü: Sipariş bilgileri ilgili alanlara aktarılır.
Örnek satır: ["MAP-01", "I_PurchaseOrderAPI01", "PurchaseOrder", "JSON gövdesi", "orderNumber", "CHAR(10) → string", "Evet", "Birebir, baştaki sıfırlar korunur", "4500001234 → \"4500001234\""]
Denetim: GEN_001, GEN_002, MAP_001, COND_002, QUAL_002
İyi pratik: Arayüz FS'inde protokol, alan eşlemesi ve hata yönetimi birlikte bulunmalıdır. Kaynak olarak released CDS view / API adı yazılır, tablo adı değil.

## 3.5 Adım adım işlem mantığı  [ağırlık 12 · Kritik · tüm türler · en az 3 satır]
Amaç: Geliştiricinin kodlayacağı mantığı sıralı, tek tek doğrulanabilir adımlar halinde verir.
Kural: En az 3 adım yazın. Her adım somut bir SAP nesnesi (CDS, API, sınıf, BAdI) içerir; hata durumunda hangi MSG'nin verileceği ve commit/rollback davranışı yazılır.
Sütunlar: 0 STEP ID {STEP-nn} ; 1 Sıra — 1, 2, 3… ; 2 Tetikleyici / koşul ; 3 İşlem — Ne yapılır, hangi veriyle ; 4 SAP nesnesi — CDS | API | sınıf | BAdI adı ; 5 Girdi → çıktı ; 6 Hata durumu → MSG — MSG-nn ; 7 Commit / rollback — Ne kalıcı olur, ne geri alınır ; 8 İlgili REQ / SC
İyi: STEP-02: I_PurchaseOrderAPI01'den ReleaseIsNotCompleted = boş ve LastChangeDateTime > son çalışma zamanı olan siparişleri oku. Kayıt yoksa MSG-01 (I) yaz ve bitir; veritabanı değişikliği yok.
Kötü: Gerekli kontroller yapıldıktan sonra ilgili tablolardan veriler okunur ve sisteme kaydedilir.
Örnek satır: ["STEP-02", "2", "Job başladı", "Onayı tamamlanmış ve son çalışmadan sonra değişmiş siparişleri oku; eşleme MAP-01, MAP-02", "I_PurchaseOrderAPI01", "Son çalışma zamanı → sipariş listesi", "Kayıt yok → MSG-01", "Değişiklik yok", "REQ-01, SC-01"]
Denetim: GEN_001, GEN_002, ALGO_001, ALGO_002, ALGO_003, CONT_001, QUAL_001
İyi pratik: RAP'te commit çerçeveye aittir: kayıt 'save sequence' içinde yapılır, COMMIT WORK yazılmaz. ABAP Cloud'da yalnız released API kullanılır; ATC bunu denetler.

## 3.6 Rapor / ALV çıktı tasarımı  [ağırlık 3 · Normal · yalnız Rapor]
Amaç: Çıktının kolonlarını, sıralamasını, toplamlarını ve navigasyonunu tanımlar.
Kural: Her kolon için başlık, kaynak alan, tip, toplam/ara toplam, varsayılan görünürlük ve navigasyon hedefini yazın.
Alanlar: cikti_tipi = Çıktı tipi [Fiori elements List Report | Analytical List Page | ALV (Private) | Dosya] (KARAR) ; disa_aktarma = Dışa aktarma — Excel, PDF ; varyant = Varyant yönetimi — Kullanıcı / genel varyant
Sütunlar: 0 Kolon ID {COL-nn} ; 1 Sıra ; 2 Başlık ; 3 Kaynak (CDS.alan) ; 4 Tip ; 5 Toplam / ara toplam ; 6 Sıralama / gruplama ; 7 Varsayılan görünür [Evet | Hayır] ; 8 Navigasyon — Semantic object-action
İyi: Kolon 5: 'Net tutar' · I_PurchaseOrderItemAPI01.NetAmount · CURR(15,2) · toplam alınır, para birimine göre · varsayılan görünür.
Örnek satır: ["COL-05", "5", "Net tutar", "I_PurchaseOrderItemAPI01.NetAmount", "CURR(15,2)", "Toplam, para birimine göre", "—", "Evet", "—"]
Denetim: GEN_001, GEN_002, COND_004
İyi pratik: Cloud'da rapor çıktısı çoğunlukla Fiori elements list report veya analytical list page'dir; klasik ALV yalnız Private Edition'da anlamlıdır.

## 3.7 Ekran–alan–kaynak matrisi  [ağırlık 6 · Bonus · tüm türler]
Amaç: Her ekran alanını OData özelliğine, CDS alanına ve kaynak nesneye kadar izler; UI5 ile ABAP arasındaki sözleşmedir.
Kural: 3.3'teki her UI öğesi için tek satır açın; zincir ekran → OData → CDS → kaynak olarak eksiksiz olsun.
Sütunlar: 0 UI ID — 3.3'ten ; 1 Ekran alanı ; 2 OData entity.property ; 3 CDS view.alan ; 4 Kaynak (tablo.alan / API) ; 5 Düzenlenebilir [Evet | Hayır] ; 6 Değer yardımı ; 7 MAP ref — MAP-nn
İyi: UI-02 'Durum' → SendLog.Status → ZC_PO_SEND_LOG.Status → ZPO_SEND_LOG.STATUS; salt okunur; değer yardımı ZI_PO_SEND_STATUS_VH.
Örnek satır: ["UI-02", "Durum", "SendLog.Status", "ZC_PO_SEND_LOG.Status", "ZPO_SEND_LOG.STATUS", "Hayır", "ZI_PO_SEND_STATUS_VH", "—"]
Denetim: GEN_001, GEN_002
İyi pratik: Bu matris, UI5 ve ABAP geliştiricinin aynı alan adını kullanmasını garanti eder ve test verisi hazırlığını kısaltır.

## 3.8 Durum makinesi / durum sözlüğü  [ağırlık 5 · Bonus · tüm türler]
Amaç: Nesnenin alabileceği durumları, anlamlarını ve izinli geçişleri tanımlar.
Kural: Her durum için kod, ad, anlam, giriş koşulu ve izinli geçişleri yazın; son durumları işaretleyin.
Sütunlar: 0 ST ID {ST-nn} ; 1 Durum kodu ; 2 Durum adı ; 3 Anlamı ; 4 Giriş koşulu (STEP) ; 5 İzinli geçişler — Kod → kod (tetikleyici) ; 6 Son durum mu [Evet | Hayır]
İyi: ST-03 'E' Hata: portal 4xx/5xx döndü veya zaman aşımı. Geçişler: E → Q (yeniden gönder aksiyonu), E → X (iptal). Son durum değil.
Örnek satır: ["ST-03", "E", "Hata", "Gönderim başarısız", "STEP-05 hata dalı", "E → Q (resend), E → X (iptal)", "Hayır"]
Denetim: GEN_001, GEN_002
İyi pratik: Durum adı ve kodu ekranda, log'da ve testte aynı yazılır; tek sözlük kullanılır.

## 3.9 İdempotency, tekrar ve kurtarma  [ağırlık 5 · Bonus · tüm türler]
Amaç: Aynı isteğin iki kez gelmesi, yarıda kalan işlem ve yeniden deneme durumlarında sistemin ne yapacağını tanımlar.
Kural: Her konu için kararı ve ilgili STEP'i yazın: idempotency anahtarı, tekrar politikası, zaman aşımı, kısmi başarı, yeniden işleme.
Sütunlar: 0 IDM ID {IDM-nn} ; 1 Konu [İdempotency anahtarı | Yinelenen istek | Tekrar politikası | Zaman aşımı | Kısmi başarı | Yeniden işleme | Kilitleme] ; 2 Karar — Somut değerlerle (KARAR) ; 3 İlgili STEP ; 4 Doğrulayan TC
İyi: IDM-01: Anahtar = PurchaseOrder + LastChangeDateTime; aynı anahtar ikinci kez gelirse POST atılmaz, log'a MSG-06 (I) yazılır.
Örnek satır: ["IDM-02", "Tekrar politikası", "HTTP 5xx ve zaman aşımında 3 deneme: 1, 5, 15 dk; sonra Status = 'E'", "STEP-05", "TC-04"]
Denetim: GEN_001, GEN_002
İyi pratik: Arayüzlerde 'fallback' davranışı yazılmazsa üretimde veri tekrarı veya kayıp oluşur; her tekrar senaryosunun bir testi olmalıdır.

## 3.10 Entegrasyon sözleşmeleri  [ağırlık 5 · Bonus · tüm türler]
Amaç: Karşı sistemle yapılan teknik anlaşmayı kayıt altına alır: uç nokta, kimlik doğrulama, SLA, hata sözleşmesi.
Kural: Her entegrasyon için uç noktayı, communication scenario/arrangement adını, kimlik doğrulamayı, SLA'yı ve HTTP kodu → davranış eşlemesini yazın.
Sütunlar: 0 INT ID {INT-nn} ; 1 Karşı sistem ; 2 Yön [Giden | Gelen] ; 3 Protokol / format (KARAR) ; 4 Uç nokta / servis ; 5 Communication scenario ; 6 Kimlik doğrulama (KARAR) ; 7 SLA / hacim ; 8 Hata sözleşmesi — Kod → davranış (KARAR) ; 9 Versiyonlama
İyi: INT-01: POST /api/v1/orders · OAuth 2.0 client credentials · ZCS_PO_SUPPLIER_PORTAL · 201 başarı, 409 yinelenen (başarı sayılır), 4xx kalıcı hata, 5xx tekrar denenir · yanıt ≤ 3 sn.
Örnek satır: ["INT-01", "Tedarikçi portalı", "Giden", "REST / JSON", "POST /api/v1/orders", "ZCS_PO_SUPPLIER_PORTAL", "OAuth 2.0 client credentials", "≤ 3 sn; 120/gün", "201 ok · 409 ok · 4xx kalıcı · 5xx tekrar", "URL'de v1"]
Denetim: GEN_001, GEN_002
İyi pratik: Public Cloud'da dış bağlantı communication scenario → communication arrangement → communication system zinciriyle kurulur; arrangement her sistemde elle oluşturulur.

## 3.11 Performans kriterleri  [ağırlık 3 · Bonus · tüm türler]
Amaç: Kabul edilebilir süreyi ve veri hacmini ölçülebilir hedeflerle tanımlar.
Kural: Her hedef bir senaryo, bir hacim ve bir ölçüm yöntemi içerir; 'hızlı' gibi sıfat kullanılmaz.
Sütunlar: 0 PERF ID {PERF-nn} ; 1 Senaryo ; 2 Veri hacmi ; 3 Hedef — Süre, bellek, adet (KARAR) ; 4 Ölçüm yöntemi ; 5 Tasarım önlemi — Sayfalama, paketleme, indeks…
İyi: PERF-01: 500 siparişlik job çalışması ≤ 10 dk (Application Jobs uygulamasındaki çalışma süresi); liste ilk açılış ≤ 2 sn, 10.000 log satırı.
Örnek satır: ["PERF-01", "Job çalışması", "500 sipariş / çalışma", "≤ 10 dk", "Application Jobs çalışma süresi", "100'lük paketlerle işleme"]
Denetim: GEN_001, GEN_002
İyi pratik: Hacim bilgisi olmadan teknik tasarım yapılamaz; hedefler test senaryosuna bağlanır.
