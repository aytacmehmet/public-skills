# Bölüm yazım bilgisi · Test ve İşletim

Üretilmiş dosyadır (kaynak: assets/tanim.json). Sütun numaraları 0'dan başlar ve JSON'daki dizi sırasıdır. {X-nn} satır kimliğidir; [a | b] yalnız bu değerleri alır; (KARAR) = kararı sen verme, girdide yoksa işaretle.

## 6.1 Test senaryoları ve verileri  [ağırlık 10 · Kritik · tüm türler · en az 2 satır]
Amaç: Geliştirmenin kabul edilmesi için çalıştırılacak senaryoları gerçek veriyle tanımlar.
Kural: En az 2 senaryo; en az biri mutlu yol, en az biri negatif/sınır. Her senaryoda gerçek test verisi (belge no, tedarikçi, şirket kodu), adımlar, beklenen sonuç ve beklenen MSG bulunur.
Sütunlar: 0 TC ID {TC-nn} ; 1 Senaryo türü [Mutlu yol | Negatif | Sınır] ; 2 Kapsadığı REQ / SC ; 3 Ön koşul ve test verisi — Gerçek belge no, ana veri ; 4 Adımlar ; 5 Beklenen sonuç — Gözlenebilir ; 6 Beklenen MSG — MSG-nn ; 7 Test tipi [ABAP Unit | Entegrasyon | UI (OPA5) | UAT] ; 8 Durum [Planlandı | Geçti | Kaldı]
İyi: TC-03 Negatif: sipariş 4500001240, tedarikçi 17300001, portal 500 döner → 3 deneme sonrası Status = 'E', MSG-03 (E) log'da, izleme uygulamasında kırmızı.
Kötü: Çeşitli siparişlerle test edilir ve doğru çalıştığı görülür.
Örnek satır: ["TC-01", "Mutlu yol", "REQ-01, SC-01", "Sipariş 4500001234, tedarikçi 17300001, şirket kodu 1710, onaylı", "1) Job'u çalıştır 2) İzleme uygulamasını aç", "Portal 201; log Status = 'S'; gönderim ≤ 5 dk", "MSG-02", "Entegrasyon", "Planlandı"]
Denetim: GEN_001, GEN_002, TEST_001, TEST_002, CONT_002, QUAL_004, QUAL_005
İyi pratik: Kabul kriteri 'X olduğunda Y, Z'de gözlenir' biçiminde yazılır. ABAP Unit birim testleri ve OPA5/QUnit UI testleri test tipi olarak belirtilir.

## 6.2 İzlenebilirlik matrisi  [ağırlık 4 · Bonus · tüm türler]
Not: Tamamen türetilir: kimlik atıflarından betik üretir. JSON'a yazılmaz.
Amaç: Her gereksinimin tasarlandığını, kodlandığını ve test edildiğini tek tabloda kanıtlar.
Kural: Her REQ için tek satır: SC → STEP → OBJ/MAP → MSG → TC. Boş hücre = kapsanmamış gereksinim.
İyi: REQ-01 → SC-01, SC-03 → STEP-01, STEP-02 → OBJ-01, OBJ-03 → MAP-01, MAP-02 → MSG-01, MSG-03 → TC-01, TC-03 · Kapsama: Tam.
Denetim: GEN_001, GEN_002
İyi pratik: İki yönlü izlenebilirlik: her REQ en az bir TC'ye, her TC en az bir REQ'e bağlanır (ISO/IEC/IEEE 29148).

## 6.3 Kod kalitesi ve doğrulama kanıtı  [ağırlık 3 · Bonus · tüm türler]
Amaç: Kodun teslimden önce hangi araçlarla doğrulandığını ve sonucunu kayıt altına alır.
Kural: Her kanıt için aracı, hedefi, sonucu ve kanıtın konumunu yazın. Açık bulgu varsa 7.3'e ve hazırlık cezası tablosuna işleyin.
Sütunlar: 0 QA ID {QA-nn} ; 1 Kanıt [ATC | ABAP Unit | CVA / güvenlik | UI5 lint | OPA5-QUnit | Kod incelemesi | İstisna kaydı] ; 2 Araç / varyant ; 3 Hedef ; 4 Sonuç ; 5 Kanıt konumu ; 6 Tarih
İyi: QA-01: ATC, varyant ABAP_CLOUD_DEVELOPMENT_DEFAULT · hedef öncelik 1–2 bulgu = 0 · sonuç 0/0 · kanıt: ATC sonuç ekran görüntüsü, 20.05.2026.
Örnek satır: ["QA-01", "ATC", "ABAP_CLOUD_DEVELOPMENT_DEFAULT", "Öncelik 1–2 bulgu = 0", "0 / 0", "Ek-3 ATC sonucu", "20.05.2026"]
Denetim: GEN_001, GEN_002
İyi pratik: ABAP Test Cockpit clean core yönetişiminin ana aracıdır; öncelik 1 ve 2 bulgular yayını engeller, istisnalar (exemption) kayıt altına alınır.

## 7.1 Loglama ve izlenebilirlik  [ağırlık 3 · Normal · tüm türler]
Amaç: Üretimde sorun çıktığında neye bakılacağını tanımlar.
Kural: Her log olayı için seviye, hedef (application log nesnesi/alt nesnesi), yazılan anahtar alanlar ve saklama süresi yazılır.
Sütunlar: 0 LOG ID {LOG-nn} ; 1 Olay ; 2 Seviye [Info | Warning | Error] ; 3 Hedef — Application log nesne / alt nesne ; 4 İçerik (anahtar alanlar) ; 5 Saklama süresi ; 6 İzleme uygulaması
İyi: LOG-02: Gönderim hatası · Error · Application Log nesnesi ZMM_PO_SEND / alt nesne OUTBOUND · sipariş no, HTTP kodu, deneme sayısı · 90 gün.
Örnek satır: ["LOG-02", "Gönderim hatası", "Error", "ZMM_PO_SEND / OUTBOUND", "Sipariş no, HTTP kodu, deneme sayısı", "90 gün", "Gönderim izleme (UI-01) → Application Logs"]
Denetim: GEN_001, GEN_002
İyi pratik: ABAP Cloud'da application log için released API kullanılır; log anahtarı (sipariş no) ile izleme uygulamasından log'a navigasyon planlanır.

## 7.2 Transport ve devreye alma  [ağırlık 3 · Normal · tüm türler]
Amaç: Nesnelerin hangi sırayla, hangi taşıma aracıyla canlıya gideceğini ve elle yapılacak adımları tanımlar.
Kural: Taşıma birimlerini (transport request, software collection) ve her sistemde elle yapılacak adımları sırayla yazın; geri alma planını ekleyin.
Alanlar: bilesen_paket = Yazılım bileşeni / paket ; transportlar = Transport request(ler) — Bilinmiyorsa BİLGİ BEKLİYOR ; software_collection = Software collection (key user) — Yoksa — ; canli_tarihi = Planlanan canlı tarihi
Sütunlar: 0 Sıra ; 1 Adım ; 2 Taşınan / yapılan — Transport, collection, elle adım ; 3 Sistem — Geliştirme | Test | Üretim ; 4 Sorumlu ; 5 Geri alma (KARAR)
İyi: Sıra 3: Test ve üretimde communication arrangement ZCS_PO_SUPPLIER_PORTAL elle oluşturulur (Basis, portal OAuth istemci bilgileriyle); geri alma: arrangement pasifleştirilir.
Örnek satır: ["3", "Communication arrangement oluştur", "ZCS_PO_SUPPLIER_PORTAL, elle", "Test, Üretim", "Basis", "Arrangement pasifleştirilir"]
Denetim: GEN_001, GEN_002
İyi pratik: 3 sistemli Public Cloud yapısında geliştirici nesneleri transport request ile, key user genişletmeleri software collection ile taşınır; iş yapılandırması customizing tenant'ından gelir.

## 7.3 Açık noktalar  [ağırlık 2 · Normal · tüm türler]
Amaç: Henüz karara bağlanmamış her konuyu sahibi ve tarihiyle görünür kılar.
Kural: Her açık noktanın sahibi (ad ya da rol) ve hazırlık cezası kategorisi olur; hedef tarih yalnız verilmişse yazılır, yoksa — kalır. Bu satırlarda BEKLİYOR işareti kullanılmaz. Karar verilince 'Karar' sütunu doldurulur ve durum 'Kararlaştırıldı' olur. Hiç açık nokta yoksa bölüm 'Açık nokta yok' gerekçesiyle geçersiz kılınır.
Sütunlar: 0 OPEN ID {OPEN-nn} ; 1 Konu — Soru biçiminde; 'DOĞRULANACAK nesneler: …' ve 'Teknik taslak geliştirici onayı bekliyor: …' satırları dışında ; 2 Etkilediği bölüm — Bölüm numaraları, virgülle: 3.4, 3.5 ; 3 Sahibi — Ad ya da rol ; 4 Hedef tarih — Verilmişse; yoksa — ; 5 Durum [Açık | Kararlaştırıldı | Kapandı] ; 6 Karar — Karar verilene kadar — ; 7 Hazırlık cezası kategorisi [Yayına alınmamış nesne | Açık ATC/CVA bulgusu | Tasarım/sözleşme açığı | Geçici çözüm / hardcode | Karar bekleyen konu | İstisna kaydı yapılmamış bulgu | —]
İyi: OPEN-02: Portal 409 yanıtı başarı mı sayılacak? · Sahibi: portal ekibi · 22.05.2026 · Kategori: Tasarım/sözleşme açığı · Karar: başarı sayılır (INT-01 güncellendi).
Örnek satır: ["OPEN-02", "Portal 409 yanıtı başarı mı sayılacak?", "3.10, 3.9", "Portal ekibi", "22.05.2026", "Kararlaştırıldı", "Başarı sayılır", "Tasarım/sözleşme açığı"]
Denetim: GEN_001, GEN_002, OPEN_001, CONT_003
İyi pratik: Açık nokta bırakılmış FS geliştirmeye verilmez ya da açık noktanın etkilediği bölüm açıkça işaretlenir; imzalı sürüm arşivlenir.
