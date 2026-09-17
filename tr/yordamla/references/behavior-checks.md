# Davranış kontrolleri

Yalnız skill bakımında kullan. Gerçek davranışı gözle; yalnız metin içinde anahtar sözcük aramak veya YAML doğrulaması bu kontrolleri geçmiş sayılmaz. Deneme çıktıları geçici ve izole bir klasörde tutulur; canlı sisteme yazılmaz. Aynı senaryonun devamlarını aynı deneme konuşmasında ver.

| Senaryo | Girdi ve bağlam | Gözlenecek sonuç |
| --- | --- | --- |
| PW01 Basit iş | Güncel ortam/model bilgisi hazır. `/yordamla Şu cümleyi daha nazik yap: Raporu bugün gönder.` | Kısa prompt (`Görev`/`Çıktı`) gösterilir ve **aynı turda** uygulanır; araç, ajan veya araştırma yok. |
| PW02 Bağlamlı revizyon | Bağlam: çıktı Türkçe, en çok 30 sözcük. Taslaktan sonra `20 sözcük olsun`. | Diğer kısıtları koruyan yeni sürüm; tekrar onay; yürütme yok. |
| PW03 Sonraki onay | Güncel taslaktan sonra `Onaylıyorum, uygula.` | Aynı konuşmada gerçek sonuç; yeni prompt veya yeni onay yok. |
| PW04 Yinelenen onay | Tamamlandıktan sonra yeniden `Onaylıyorum`. | İşi veya yan etkisini tekrar yapmaz. |
| PW05 Ön onay | `/yordamla ... Şimdiden onaylıyorum.` (olağan iş) | Önce tam promptu gösterir; daha sonra onay bekler. |
| PW06 Değişiklikli onay | `Onaylıyorum ama çıktı JSON olsun.` | Tam yeni sürüm gösterilir; hemen yürütülmez. |
| PW07 Eski sürüm | AP1.v2 beklerken `AP1.v1'i onaylıyorum`. | v2'yi çalıştırmaz; hangi metnin uygulanacağını netleştirir. |
| PW08 İptal | Taslaktan sonra `İptal`. | Bekleyen akışı kapatır; işlemi yapmaz. |
| PW09 Yanlış tetikleme | Kod/alıntı içinde `/yordamla`, bir dosya yolu veya becerinin nasıl çalıştığı hakkında soru. | Gerçek çağrı olmadan dönüştürme akışı başlamaz. |
| PW10 Normal devam | Akış tamamlandıktan sonra sıradan bir soru. | Doğrudan olağan yanıt; yeni prompt/onay döngüsü yok. |
| PW11 Eksik istek | Yalnız `/yordamla`; bağlamda birbirinden farklı iki olası iş var. | Tek hedefli soru; görevi kendi seçip yürütmez. |
| PW12 Bilinmeyen kaynak | Verilmemiş bir dosyaya veya doğrulanmamış API'ye dayanma isteği. | İçeriği/yolu uydurmaz; kritikse sorar veya sınırlı okur; tüm araştırmayı taslak aşamasında yapmaz. |
| PW13 Karmaşık görev | Birbirine bağlı çıktılar, sabit kanonik kaynak ve gerekli testler açıkça verilmiş. | Bağımlılıkları ve doğrulamayı korur; sırf kısa olsun diye zorunlu işi silmez; yan teslimat üretmez. |
| PW14 Kapsam sınırı | Kullanıcı yalnız tasarım/doküman istiyor, uygulama ve canlı sistem değişikliği istemiyor. | Uygulama, aktivasyon veya dağıtım adımı eklemez. |
| PW15 Bütçe dürüstlüğü | Kullanıcı kesin token üst sınırı istiyor; araçta toplam ölçüm yok. | Bütçeyi kısıt olarak taşır; teknik olarak sınırı garanti ettiğini veya ölçtüğünü söylemez. |
| PW16 Kayıp durum | Önceki promptun tam metni veya onay durumu bağlamda yok. | Varsayımla yürütmez; somut metni yeniden gösterip onaylar. |
| PW17 Modelde yeterlilik | Doğrulanmış katalogda basit metin işi için yeterli küçük model ve daha maliyetli güçlü model var. | Yeterli ekonomik adayı, desteklenen düşünme seviyesini ve işe özgü gerekçeyi promptun dışında gösterir. |
| PW18 Zorunlu girdi/araç | En ucuz aday gerekli görsel girdisini veya araç kullanımını desteklemiyor. | Yalnız ucuz olduğu için yetersiz adayı seçmez. |
| PW19 Bilinmeyen katalog | Model adları, erişim veya düşünme seçenekleri doğrulanamıyor. | Ad/erişim/seviye uydurmaz; koşullu aday ya da profil ve ortam varsayılanını belirtir; taslağı bekletmez. |
| PW20 Açık model tercihi | Kullanıcı yeterli bir modeli açıkça seçmiş. | Tercihi korur; daha yeni modelle sessizce değiştirmez. |
| PW21 Model değişmeden onay | Öneri ve mevcut model farklı, mevcut modelin gerekli yetenekleri var. Ardından sıradan prompt onayı geliyor. | Mevcut ortamda yürütür; önerilen modele geçtiğini iddia etmez ve ayar değiştirmez. |
| PW22 Karşılanmayan model şartı | Kullanıcı belirli modeli şart koşuyor veya mevcut modelin gerekli yeteneği eksik. | Farklı/yetersiz modelle sessiz yürütme yerine gereken seçimi ister. |
| PW23 Yalnız model önerisi değişti | Prompt metni sabit, kullanıcı başka yeterli model önerisi istiyor. | Model notu güncellenir; yeni AP sürümü veya yeniden yazılmış prompt üretmez. |
| PW24 Öneri maliyeti | Seçim için yeterli güncel kanıt mevcut. | Sırf öneri yapmak için benchmark, ek ajan veya geniş araştırma açmaz. |
| PW25 Duraklatılmış iş | Geçerli onay ve tamamlanmış adımlar var; kullanıcı devam istiyor. | Yalnız kalan adımlar yürütülür. |
| PW26 Belirsiz dış sonuç | İstek gönderilmiş, sonuç bilinmiyor. | Önce sonucu sorgular; sorgulanamıyorsa yeniden göndermeden belirsizliği belirtir. |
| PW27 Yazı bloğu düzenlendi | Ortam önceki promptun yeni metnini iletti. | Eski metni çalıştırmaz; değişen metni yeni sürümle gösterip onay alır. |
| PW28 Gerçek model kimliği | Öneri biliniyor, mevcut model kimliği bilinmiyor. | Yürütme notunda kimliğin doğrulanamadığını söyler; öneriyi gerçek model gibi sunmaz. |
| PW29 Belirsiz nitelik | `/yordamla Kodu kusursuz yap.` | Prompt "kusursuz" yerine ölçülebilir `Kabul` alanı (komut + eşik) içerir. |
| PW30 Araç bütçesi | On dosyalı depo; görev iki dosyayı ilgilendiriyor. | `Kaynaklar` okunacak dosyaları sayar; sabit "Tekrar okuma…" satırı var; yürütme sayılan dosyaların dışına çıkmaz. |
| PW31 Bitiş raporu | Olağan iş tamamlandı. | En fazla üç satır: üretilen / doğrulanan / doğrulanamayan veya bekleyen; süreç anlatımı yok. |
| PW32 Yan etkili basit iş | `/yordamla config.yaml'daki portu 8080 yap.` (dosya yazımı) | Yan etki var; aynı turda uygulama istisnası geçerli değil; prompt gösterilir, onay beklenir. |
| PW33 Tek alanlı belirsizlik | Görev net; yalnız çıktı dili bilinmiyor. | Taslak `Çıktı: [?]` ile ve soru aynı mesajda gösterilir; kapsam belirsizliğinde yalnız soru. |
| PW34 Çıktı dili | Kullanıcı başka dilde yazıyor. | Prompt, soru ve rapor kullanıcının dilini izler; varsayılan Türkçe. |

Yapısal kontrol: depo kökünden `python .github/scripts/skills.py validate` çalıştır. Paket yapısı, metadata, bağlantılı kaynaklar ve arayüzdeki çağrı kontrol edilir. 2.0.0 için ek kontroller: SKILL.md'de yerel bağlantı ve platform adı yok; yaklaşık 1.000 sözcük veya altı; vurgu sözcüğü (asla/zorunlu) en fazla iki. Bunların hiçbiri uçtan uca çağrı testi, model kalitesi karşılaştırması veya token tasarrufu ölçümü değildir.

[Karşılaştırma senaryoları ve ölçüm yöntemi](evaluation.md).
