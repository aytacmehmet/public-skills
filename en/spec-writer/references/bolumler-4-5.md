# Section writing guide · SAP Objects, Errors and Authorization

Generated file (source: assets/tanim.json). Column numbers start at 0 and follow the array order in the JSON. {X-nn} is the row id; [a | b] takes only these values; (KARAR) = do not decide yourself, mark it when the inputs do not state it.

## 4.1 Geliştirilecek nesneler listesi  [weight 4 · Normal · all types]
Purpose: The single catalog of every custom and standard SAP object named in the document.
Rule: Every object named in the document is defined here once, and every object here is used in at least one STEP, MAP or UI row. The SAP type comes from the list (references/sap-sozluk.md); custom names follow the project naming rules.
Columns: 0 OBJ ID {OBJ-nn} ; 1 Nesne adı — Technical name ; 2 SAP tipi — TABL, DDLS, BDEF, SRVD, SRVB, CLAS, MSAG, SUSO … or by name: BAdI, API, IAM app, Application job … (full list: references/sap-sozluk.md) ; 3 Kaynak [Z | SAP] ; 4 Yeni / değişen [Yeni | Değişen | Kullanılan] ; 5 Paket / yazılım bileşeni ; 6 Dil versiyonu / release contract ; 7 Açıklama ; 8 Kullanıldığı yer — STEP / MAP / UI
Good: OBJ-03 · ZBP_R_PO_SEND_LOG · CLAS (behavior implementation) · Yeni · paket ZMM_PO_SEND · ABAP for Cloud Development · STEP-04, STEP-07.
Example row: ["OBJ-01", "ZPO_SEND_LOG", "TABL", "Z", "Yeni", "ZMM_PO_SEND", "ABAP for Cloud Development", "Gönderim log tablosu", "STEP-04, STEP-06"]
Checks: GEN_001, GEN_002, OBJ_001, SAP_001, SAP_002, SAP_003, SAP_004
Good practice: In ABAP Cloud, objects are written with the 'ABAP for Cloud Development' language version; the release contract (C1/C2) of a consumed SAP object must appear in the catalog.

## 4.2 DDIC yapıları  [weight 4 · Normal · all types]
Purpose: Defines custom tables, structures and data elements at field level.
Rule: For every field write the key flag, data element or type, length and value range. The object name must equal the OBJ row in 4.1.
Columns: 0 Nesne (OBJ) — Table / structure name ; 1 Alan ; 2 Anahtar [Evet | Hayır] ; 3 Veri elemanı / tip ; 4 Uzunluk ; 5 Açıklama ; 6 Değer aralığı / domain ; 7 Not
Good: ZPO_SEND_LOG · STATUS · anahtar değil · ZMM_PO_SEND_STATUS (CHAR 1) · sabit değerler Q, S, E, X.
Example row: ["ZPO_SEND_LOG", "STATUS", "Hayır", "ZMM_PO_SEND_STATUS", "CHAR 1", "Gönderim durumu", "Q, S, E, X", "3.8 ile aynı"]
Checks: GEN_001, GEN_002, SAP_003, SAP_004
Good practice: Field names are written exactly as in 3.4 and 3.7; one data element per concept.

## 4.3 Genişletmeler (BAdI / Exit)  [weight 3 · Normal · all types]
Purpose: Defines where standard behaviour is intercepted and the logic of the intervention.
Rule: Write the technical name of the extension point, whether it is released, the filter value, the trigger moment and the logic (STEP ref).
Columns: 0 EXT ID {EXT-nn} ; 1 Genişletme noktası — BAdI / custom field / custom logic name ; 2 Released mı [Evet | Hayır] ; 3 Uygulama adı ; 4 Filtre ; 5 Tetiklenme anı ; 6 Mantık → STEP
Good: EXT-01: BAdI MM_PUR_S4_PO_MODIFY_HEADER (released) · uygulama ZMM_PO_HDR_PORTAL_FLAG · onay sonrası özel alan YY1_PortalSend_PDH = 'X' · STEP-01.
Example row: ["EXT-01", "MM_PUR_S4_PO_MODIFY_HEADER", "Evet", "ZMM_PO_HDR_PORTAL_FLAG", "—", "Sipariş kaydı öncesi", "STEP-01"]
Checks: GEN_001, GEN_002, SAP_003, SAP_004
Good practice: In Public Cloud only released extension points may be used; implicit enhancement and modification are clean core level D.

## 4.4 Form tasarımı  [weight 3 · Normal · only Form]
Purpose: Defines the layout, field sources and print conditions of the output form.
Rule: Write the form technology, the output channel and the language; for every form field give the region, source, format and display condition.
Fields: form_teknolojisi = Form teknolojisi — e.g. Adobe Forms (form template) (KARAR) ; cikti_kanal = Çıktı tipi ve kanal — Print, e-mail, EDI ; dil_kagit = Dil ve kağıt — e.g. TR, EN · A4 ; tetikleme = Tetikleme koşulu — Output determination rule
Columns: 0 Alan ID {FRM-nn} ; 1 Form bölgesi [Başlık | Kalem | Alt bilgi] ; 2 Etiket ; 3 Kaynak — CDS.field ; 4 Biçim ; 5 Gösterim koşulu
Good: Alan 'Teslim tarihi' · kalem tablosu · I_PurchaseOrderScheduleLineAPI01.ScheduleLineDeliveryDate · GG.AA.YYYY · yalnız kalem kategorisi standart ise.
Example row: ["FRM-07", "Kalem", "Teslim tarihi", "I_PurchaseOrderScheduleLineAPI01.ScheduleLineDeliveryDate", "GG.AA.YYYY", "Her kalemde"]
Checks: GEN_001, GEN_002, COND_005
Good practice: A form FS holds layout, output channels and print conditions together; a sample output image is attached.

## 5.1 Hata kontrolleri ve mesajlar  [weight 6 · Kritik · all types · at least 2 rows]
Purpose: Defines in which situation which message is raised, with which type, and what the system does.
Rule: Write at least two different error situations. They follow from the stated rules: mandatory input missing, no authorization, no data, counterpart not answering. Every row has the type (E/W/I/S/A), the message text, the STEP/UI that raises it and the system behaviour. For a message the framework raises itself, the class column reads 'Standart (çerçeve mesajı)'; the class and number of a custom message are technical draft.
Columns: 0 MSG ID {MSG-nn} ; 1 Kontrol / durum — When it occurs ; 2 Nerede — STEP-nn / UI-nn ; 3 Tip [E | W | I | S | A] ; 4 Mesaj sınıfı – no ; 5 Mesaj metni — With &1 &2 variables ; 6 Sistem davranışı — Stops, continues, rolls back ; 7 Kullanıcının yapacağı
Good: MSG-03 · E · ZMM_PO_SEND 003 · 'Sipariş &1 portala gönderilemedi: HTTP &2' · STEP-05 · Status = 'E', sonraki siparişe geçilir.
Bad: Hata oluşursa kullanıcıya uygun mesaj gösterilir.
Example row: ["MSG-03", "Portal 4xx/5xx döndü", "STEP-05", "E", "ZMM_PO_SEND 003", "Sipariş &1 portala gönderilemedi: HTTP &2", "Status = 'E'; sonraki siparişe geçilir", "İzleme uygulamasından 'Yeniden gönder'"]
Checks: GEN_001, GEN_002, ERR_001, ERR_002, ERR_003, QUAL_006
Good practice: A message is written so the user understands the next step. In RAP, messages return through the 'reported' structure; unwanted situations use the EARS 'If … then' pattern.

## 5.2 Backend yetkilendirme  [weight 4 · Normal · all types]
Purpose: Defines which authorization object is checked on the server side, with which fields and values, and where.
Rule: Write the authorization object, its fields, the activity, the check point and the MSG raised on failure.
Columns: 0 AUTH ID {AUTH-nn} ; 1 Yetki nesnesi ; 2 Alanlar ve değerler ; 3 Aktivite — 01 | 02 | 03 | 06 | 16 ; 4 Kontrol noktası — STEP / BDEF authorization ; 5 Restriction type / field ; 6 Başarısızlık → MSG
Good: AUTH-01: ZMM_POSND · BUKRS = siparişin şirket kodu, ACTVT = 02 · BDEF 'authorization master (instance)' içinde 'resend' aksiyonu için · başarısızsa MSG-07 (E).
Example row: ["AUTH-01", "ZMM_POSND", "BUKRS = sipariş şirket kodu", "02", "BDEF instance authorization, aksiyon 'resend'", "Şirket kodu (leading)", "MSG-07"]
Checks: GEN_001, GEN_002, AUTH_001
Good practice: In Public Cloud the authorization object is restricted in the business role through restriction type/field: Read, Write and Value Help access are defined separately.

## 5.3 Frontend yetkilendirme  [weight 4 · Normal · all types]
Purpose: Defines to whom, through which catalog and role, the application is visible.
Rule: Write the IAM app, the business catalog, the business role template and the launchpad placement; state the UI elements hidden or disabled by authorization.
Columns: 0 AUTH ID {AUTH-nn} ; 1 IAM app ; 2 Business catalog ; 3 Business role (şablon) ; 4 Space / page / tile ; 5 Gizlenen / pasif UI öğesi — UI-nn and condition ; 6 Erişim türü — Read | Write | Value help
Good: AUTH-02: IAM app ZMM_PO_SEND_MON_EXT · business catalog ZMM_BC_PO_SEND_MON · rol şablonu 'Satınalmacı' · 'Yeniden gönder' butonu Write erişimi yoksa pasif.
Example row: ["AUTH-02", "ZMM_PO_SEND_MON_EXT", "ZMM_BC_PO_SEND_MON", "Satınalmacı (BR_PURCHASER kopyası)", "Satınalma / Sipariş izleme / Gönderim izleme", "UI-04: Write yoksa pasif", "Read, Write"]
Checks: GEN_001, GEN_002, AUTH_001
Good practice: A custom app is attached to a business catalog through an IAM app, and the catalog to a business role. If a second role of the same user carries 'Unrestricted', the restriction is void.

## 5.4 Mesaj sözlüğü  [weight 4 · Bonus · all types]
Note: Message class, type and TR text are joined from 5.1; only these 4 columns are written here.
Purpose: Keeps a single bilingual list of all messages in the message class.
Rule: For every MSG of 5.1 write message class, number, type, TR and EN short text and the variables.
Columns: 0 MSG ref — MSG-nn from 5.1 ; 1 Kısa metin (EN) ; 2 Değişkenler — Meaning of &1…&4 ; 3 Uzun metin [Var | Yok]
Good: ZMM_PO_SEND · 003 · E · 'Sipariş &1 portala gönderilemedi: HTTP &2' · 'Purchase order &1 could not be sent: HTTP &2' · &1 sipariş no, &2 HTTP kodu.
Example row: ["MSG-03", "Purchase order &1 could not be sent: HTTP &2", "&1 sipariş no, &2 HTTP kodu", "Var"]
Checks: GEN_001, GEN_002, ERR_003
Good practice: Message texts must be translatable; text is not embedded in code, it lives in the message class.
