# Bölüm yazım bilgisi · SAP Nesneleri, Hata ve Yetki

Üretilmiş dosyadır (kaynak: assets/tanim.json). Sütun numaraları 0'dan başlar ve JSON'daki dizi sırasıdır. {X-nn} satır kimliğidir; [a | b] yalnız bu değerleri alır; (KARAR) = kararı sen verme, girdide yoksa işaretle.

## 4.1 Geliştirilecek nesneler listesi  [ağırlık 4 · Normal · tüm türler]
Amaç: Dokümanda adı geçen tüm özel ve standart SAP nesnelerinin tek kataloğudur.
Kural: Dokümanda geçen her nesne burada bir kez tanımlanır ve buradaki her nesne dokümanda en az bir STEP, MAP veya UI satırında kullanılır. SAP tipi listeden seçilir (references/sap-sozluk.md); özel adlar projenin adlandırma kuralına uyar.
Sütunlar: 0 OBJ ID {OBJ-nn} ; 1 Nesne adı — Teknik ad ; 2 SAP tipi — TABL, DDLS, BDEF, SRVD, SRVB, CLAS, MSAG, SUSO … ya da adıyla: BAdI, API, IAM app, Application job … (tam liste: references/sap-sozluk.md) ; 3 Kaynak [Z | SAP] ; 4 Yeni / değişen [Yeni | Değişen | Kullanılan] ; 5 Paket / yazılım bileşeni ; 6 Dil versiyonu / release contract ; 7 Açıklama ; 8 Kullanıldığı yer — STEP / MAP / UI
İyi: OBJ-03 · ZBP_R_PO_SEND_LOG · CLAS (behavior implementation) · Yeni · paket ZMM_PO_SEND · ABAP for Cloud Development · STEP-04, STEP-07.
Örnek satır: ["OBJ-01", "ZPO_SEND_LOG", "TABL", "Z", "Yeni", "ZMM_PO_SEND", "ABAP for Cloud Development", "Gönderim log tablosu", "STEP-04, STEP-06"]
Denetim: GEN_001, GEN_002, OBJ_001, SAP_001, SAP_002, SAP_003, SAP_004
İyi pratik: ABAP Cloud'da nesneler 'ABAP for Cloud Development' dil versiyonuyla yazılır; kullanılan SAP nesnesinin release contract'ı (C1/C2) katalogda görünmelidir.

## 4.2 DDIC yapıları  [ağırlık 4 · Normal · tüm türler]
Amaç: Özel tablo, yapı ve veri elemanlarını alan düzeyinde tanımlar.
Kural: Her alan için anahtar bilgisi, veri elemanı veya tip, uzunluk ve değer aralığı yazın. Nesne adı 4.1'deki OBJ satırıyla aynı olmalı.
Sütunlar: 0 Nesne (OBJ) — Tablo / yapı adı ; 1 Alan ; 2 Anahtar [Evet | Hayır] ; 3 Veri elemanı / tip ; 4 Uzunluk ; 5 Açıklama ; 6 Değer aralığı / domain ; 7 Not
İyi: ZPO_SEND_LOG · STATUS · anahtar değil · ZMM_PO_SEND_STATUS (CHAR 1) · sabit değerler Q, S, E, X.
Örnek satır: ["ZPO_SEND_LOG", "STATUS", "Hayır", "ZMM_PO_SEND_STATUS", "CHAR 1", "Gönderim durumu", "Q, S, E, X", "3.8 ile aynı"]
Denetim: GEN_001, GEN_002, SAP_003, SAP_004
İyi pratik: Alan adları 3.4 ve 3.7'deki adlarla birebir aynı yazılır; aynı kavram için tek veri elemanı kullanılır.

## 4.3 Genişletmeler (BAdI / Exit)  [ağırlık 3 · Normal · tüm türler]
Amaç: Standart davranışa müdahale edilen noktaları ve müdahalenin mantığını tanımlar.
Kural: Genişletme noktasının teknik adını, released olup olmadığını, filtre değerini, tetiklenme anını ve mantığı (STEP ref) yazın.
Sütunlar: 0 EXT ID {EXT-nn} ; 1 Genişletme noktası — BAdI / özel alan / özel mantık adı ; 2 Released mı [Evet | Hayır] ; 3 Uygulama adı ; 4 Filtre ; 5 Tetiklenme anı ; 6 Mantık → STEP
İyi: EXT-01: BAdI MM_PUR_S4_PO_MODIFY_HEADER (released) · uygulama ZMM_PO_HDR_PORTAL_FLAG · onay sonrası özel alan YY1_PortalSend_PDH = 'X' · STEP-01.
Örnek satır: ["EXT-01", "MM_PUR_S4_PO_MODIFY_HEADER", "Evet", "ZMM_PO_HDR_PORTAL_FLAG", "—", "Sipariş kaydı öncesi", "STEP-01"]
Denetim: GEN_001, GEN_002, SAP_003, SAP_004
İyi pratik: Public Cloud'da yalnız released genişletme noktaları kullanılabilir; implicit enhancement ve modifikasyon clean core seviye D'dir.

## 4.4 Form tasarımı  [ağırlık 3 · Normal · yalnız Form]
Amaç: Çıktı formunun düzenini, alan kaynaklarını ve basım koşullarını tanımlar.
Kural: Form teknolojisini, çıktı kanalını ve dili yazın; her form alanı için bölgeyi, kaynağı, biçimi ve gösterim koşulunu verin.
Alanlar: form_teknolojisi = Form teknolojisi — Örn. Adobe Forms (form şablonu) (KARAR) ; cikti_kanal = Çıktı tipi ve kanal — Yazdırma, e-posta, EDI ; dil_kagit = Dil ve kağıt — Örn. TR, EN · A4 ; tetikleme = Tetikleme koşulu — Çıktı belirleme kuralı
Sütunlar: 0 Alan ID {FRM-nn} ; 1 Form bölgesi [Başlık | Kalem | Alt bilgi] ; 2 Etiket ; 3 Kaynak — CDS.alan ; 4 Biçim ; 5 Gösterim koşulu
İyi: Alan 'Teslim tarihi' · kalem tablosu · I_PurchaseOrderScheduleLineAPI01.ScheduleLineDeliveryDate · GG.AA.YYYY · yalnız kalem kategorisi standart ise.
Örnek satır: ["FRM-07", "Kalem", "Teslim tarihi", "I_PurchaseOrderScheduleLineAPI01.ScheduleLineDeliveryDate", "GG.AA.YYYY", "Her kalemde"]
Denetim: GEN_001, GEN_002, COND_005
İyi pratik: Form FS'inde düzen, çıktı kanalları ve basım koşulları birlikte bulunur; örnek çıktı görseli eklenir.

## 5.1 Hata kontrolleri ve mesajlar  [ağırlık 6 · Kritik · tüm türler · en az 2 satır]
Amaç: Hangi durumda hangi mesajın, hangi tipte verileceğini ve sistemin ne yapacağını tanımlar.
Kural: En az iki farklı hata durumu yazın. Durumlar anlatılan kurallardan çıkar: zorunlu girdi eksik, yetki yok, veri bulunamadı, karşı sistem yanıt vermiyor. Her satırda tip (E/W/I/S/A), mesaj metni, tetiklendiği STEP/UI ve sistemin davranışı bulunur. Çerçevenin kendi verdiği mesajda sınıf sütununa 'Standart (çerçeve mesajı)' yazılır; özel mesajın sınıfı ve numarası teknik taslaktır.
Sütunlar: 0 MSG ID {MSG-nn} ; 1 Kontrol / durum — Ne zaman oluşur ; 2 Nerede — STEP-nn / UI-nn ; 3 Tip [E | W | I | S | A] ; 4 Mesaj sınıfı – no ; 5 Mesaj metni — &1 &2 değişkenleriyle ; 6 Sistem davranışı — Durur, devam eder, geri alır ; 7 Kullanıcının yapacağı
İyi: MSG-03 · E · ZMM_PO_SEND 003 · 'Sipariş &1 portala gönderilemedi: HTTP &2' · STEP-05 · Status = 'E', sonraki siparişe geçilir.
Kötü: Hata oluşursa kullanıcıya uygun mesaj gösterilir.
Örnek satır: ["MSG-03", "Portal 4xx/5xx döndü", "STEP-05", "E", "ZMM_PO_SEND 003", "Sipariş &1 portala gönderilemedi: HTTP &2", "Status = 'E'; sonraki siparişe geçilir", "İzleme uygulamasından 'Yeniden gönder'"]
Denetim: GEN_001, GEN_002, ERR_001, ERR_002, ERR_003, QUAL_006
İyi pratik: Mesaj, kullanıcının bir sonraki adımı anlayacağı şekilde yazılır. RAP'te mesajlar 'reported' yapısıyla döner; istenmeyen durumlar EARS 'If … then' kalıbıyla ifade edilir.

## 5.2 Backend yetkilendirme  [ağırlık 4 · Normal · tüm türler]
Amaç: Sunucu tarafında hangi yetki nesnesinin, hangi alan ve değerle, nerede kontrol edileceğini tanımlar.
Kural: Yetki nesnesini, alanlarını, aktiviteyi, kontrol noktasını ve başarısızlıkta verilecek MSG'yi yazın.
Sütunlar: 0 AUTH ID {AUTH-nn} ; 1 Yetki nesnesi ; 2 Alanlar ve değerler ; 3 Aktivite — 01 | 02 | 03 | 06 | 16 ; 4 Kontrol noktası — STEP / BDEF authorization ; 5 Restriction type / field ; 6 Başarısızlık → MSG
İyi: AUTH-01: ZMM_POSND · BUKRS = siparişin şirket kodu, ACTVT = 02 · BDEF 'authorization master (instance)' içinde 'resend' aksiyonu için · başarısızsa MSG-07 (E).
Örnek satır: ["AUTH-01", "ZMM_POSND", "BUKRS = sipariş şirket kodu", "02", "BDEF instance authorization, aksiyon 'resend'", "Şirket kodu (leading)", "MSG-07"]
Denetim: GEN_001, GEN_002, AUTH_001
İyi pratik: Public Cloud'da yetki nesnesi restriction type/field üzerinden business role'de kısıtlanır: Read, Write ve Value Help erişimleri ayrı ayrı tanımlanır.

## 5.3 Frontend yetkilendirme  [ağırlık 4 · Normal · tüm türler]
Amaç: Uygulamanın kime, hangi katalog ve rol üzerinden görüneceğini tanımlar.
Kural: IAM app, business catalog, business role şablonu ve launchpad yerleşimini yazın; yetkiye göre gizlenen/pasifleşen UI öğelerini belirtin.
Sütunlar: 0 AUTH ID {AUTH-nn} ; 1 IAM app ; 2 Business catalog ; 3 Business role (şablon) ; 4 Space / page / tile ; 5 Gizlenen / pasif UI öğesi — UI-nn ve koşul ; 6 Erişim türü — Read | Write | Value help
İyi: AUTH-02: IAM app ZMM_PO_SEND_MON_EXT · business catalog ZMM_BC_PO_SEND_MON · rol şablonu 'Satınalmacı' · 'Yeniden gönder' butonu Write erişimi yoksa pasif.
Örnek satır: ["AUTH-02", "ZMM_PO_SEND_MON_EXT", "ZMM_BC_PO_SEND_MON", "Satınalmacı (BR_PURCHASER kopyası)", "Satınalma / Sipariş izleme / Gönderim izleme", "UI-04: Write yoksa pasif", "Read, Write"]
Denetim: GEN_001, GEN_002, AUTH_001
İyi pratik: Özel uygulama bir IAM app ile business catalog'a, katalog da business role'e bağlanır. Aynı kullanıcıdaki ikinci rolde 'Unrestricted' varsa kısıt geçersiz kalır.

## 5.4 Mesaj sözlüğü  [ağırlık 4 · Bonus · tüm türler]
Not: Mesaj sınıfı, tip ve TR metin 5.1'den birleştirilir; burada yalnız bu 4 sütun yazılır.
Amaç: Mesaj sınıfındaki tüm mesajların iki dilde tek listesini tutar.
Kural: 5.1'deki her MSG için mesaj sınıfı, numara, tip, TR ve EN kısa metin ile değişkenleri yazın.
Sütunlar: 0 MSG ref — 5.1'deki MSG-nn ; 1 Kısa metin (EN) ; 2 Değişkenler — &1…&4 anlamları ; 3 Uzun metin [Var | Yok]
İyi: ZMM_PO_SEND · 003 · E · 'Sipariş &1 portala gönderilemedi: HTTP &2' · 'Purchase order &1 could not be sent: HTTP &2' · &1 sipariş no, &2 HTTP kodu.
Örnek satır: ["MSG-03", "Purchase order &1 could not be sent: HTTP &2", "&1 sipariş no, &2 HTTP kodu", "Var"]
Denetim: GEN_001, GEN_002, ERR_003
İyi pratik: Mesaj metinleri çevrilebilir olmalı; metin kod içine gömülmez, mesaj sınıfında tutulur.
