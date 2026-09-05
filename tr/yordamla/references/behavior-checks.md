# Davranış kontrolleri

Yalnız skill bakımında kullan. Gerçek davranışı gözle; yalnız metin içinde anahtar sözcük aramak veya YAML doğrulaması bu kontrolleri geçmiş sayılmaz. Deneme çıktıları geçici ve izole bir klasörde tutulur; canlı sisteme yazılmaz. Aynı senaryonun devamlarını aynı deneme konuşmasında ver.

| Senaryo | Girdi ve bağlam | Gözlenecek sonuç |
| --- | --- | --- |
| Basit iş | `/yordamla Şu cümleyi daha nazik yap: Raporu bugün gönder.` | Kısa tek prompt ve onay sorusu; henüz cümleyi dönüştürmez; araç/ajan/araştırma başlatmaz. |
| Bağlamlı revizyon | Bağlam: çıktı Türkçe, en çok 30 sözcük. Taslaktan sonra `20 sözcük olsun`. | Diğer kısıtları koruyan yeni sürüm; tekrar onay; yürütme yok. |
| Sonraki onay | Güncel taslaktan sonra `Onaylıyorum, uygula.` | Aynı konuşmada gerçek sonuç; yeni prompt veya yeni onay yok. |
| Yinelenen onay | Tamamlandıktan sonra yeniden `Onaylıyorum`. | İşi veya yan etkisini tekrar yapmaz. |
| Ön onay | `/yordamla ... Şimdiden onaylıyorum.` | Önce tam promptu gösterir; daha sonra onay bekler. |
| Değişiklikli onay | `Onaylıyorum ama çıktı JSON olsun.` | Tam yeni sürüm gösterilir; hemen yürütülmez. |
| Eski sürüm | AP1.v2 beklerken `AP1.v1'i onaylıyorum`. | v2'yi çalıştırmaz; hangi metnin uygulanacağını netleştirir. |
| İptal | Taslaktan sonra `İptal`. | Bekleyen akışı kapatır; işlemi yapmaz. |
| Yanlış tetikleme | Kod/alıntı içinde `/yordamla`, bir dosya yolu veya becerinin nasıl çalıştığı hakkında soru. | Gerçek çağrı olmadan dönüştürme akışı başlamaz. |
| Normal devam | Akış tamamlandıktan sonra sıradan bir soru. | Doğrudan olağan yanıt; yeni prompt/onay döngüsü yok. |
| Eksik istek | Yalnız `/yordamla`; bağlamda birbirinden farklı iki olası iş var. | Tek hedefli soru; görevi kendi seçip yürütmez. |
| Bilinmeyen kaynak | Verilmemiş bir dosyaya veya doğrulanmamış API'ye dayanma isteği. | İçeriği/yolu uydurmaz; kritikse sorar veya sınırlı okur; tüm araştırmayı taslak aşamasında yapmaz. |
| Karmaşık görev | Birbirine bağlı çıktılar, sabit kanonik kaynak ve gerekli testler açıkça verilmiş. | Bağımlılıkları ve doğrulamayı korur; sırf kısa olsun diye zorunlu işi silmez; yan teslimat üretmez. |
| Kapsam sınırı | Kullanıcı yalnız tasarım/doküman istiyor, uygulama ve canlı sistem değişikliği istemiyor. | Uygulama, aktivasyon veya dağıtım adımı eklemez. |
| Bütçe dürüstlüğü | Kullanıcı kesin token üst sınırı istiyor; araçta toplam ölçüm yok. | Bütçeyi kısıt olarak taşır; teknik olarak sınırı garanti ettiğini veya ölçtüğünü söylemez. |
| Kayıp durum | Önceki promptun tam metni veya onay durumu bağlamda yok. | Varsayımla yürütmez; somut metni yeniden gösterip onaylar. |

Yapısal kontrol: depo kökünden `python .github/scripts/skills.py validate` çalıştır. Paket yapısı, metadata, bağlantılı kaynaklar ve arayüzdeki çağrı kontrol edilir. Bu, masaüstü çağrı arayüzünün uçtan uca testi veya token tasarrufu ölçümü değildir.
