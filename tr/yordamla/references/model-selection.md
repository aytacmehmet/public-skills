# Model seçimi notları

Yalnız karmaşık yetenek gereksinimleri, eksik katalog veya önemli model tercihleri değerlendirilirken kullan. Bu dosya bir model/fiyat listesi değildir; model adlarını veya sıralamaları sabitlemez.

## Karar sırası

1. **Kullanıcı tercihi:** Zorunlu model, bütçe, hız ve kalite koşullarını koru. Açık model tercihinin görevle bilinen uyumsuzluğu varsa bunu belirt; başka modele sessizce geçme.
2. **Yapabilirlik:** Gerekli görsel/ses/metin girdisi, dosya ve araç desteği, bağlam sınırı ve ortam erişimi. Bunlar bilinmeden yalnız fiyat veya isim üzerinden seçim yapma. Modeli güçlendirmek eksik bir bağlantıyı ya da izni sağlamaz.
3. **Yeterli kalite:** Belirsizlik, bağımlılıklar, hata etkisi ve yeniden çalışma ihtiyacı. Verilen bir değerlendirme sonucu varsa kullan; sadece model ailesinin adından doğruluk garantisi çıkarma.
4. **Ekonomi:** Yeterli adaylar arasında bilinen maliyet, gecikme ve beklenen tekrar ihtiyacını değerlendir. Fiyat bilgisi yoksa “en ucuz” deme. Her aşama için ayrı model/ajan veya otomatik model yükseltme planı üretme.

## Kaynak ve öneri sınırı

Oturumdaki güncel ortam kataloğu kullanılabilir seçenekleri gösterir; resmî model belgeleri genel yetenekleri açıklar. Birinin kanıtını diğerinin yerine kullanma. Kullanıcının gönderdiği model listesinin dayanağı doğrulanmadıysa bunu kullanıcı beyanı olarak ele al. Eski bir sürüme ait katalog güncelliğini koruyor varsayılmaz.

Katalog eksikse öneriyi koşullu olarak sun veya gerekli yetenek profilini belirt. Gerekli bir kontrol için mevcut `openai-docs` becerisi uygunsa kullan; ek beceri yoksa resmî kaynağı doğrudan kontrol et. Kullanılmış ve hâlâ geçerli kanıtı tekrar toplama; üst düzey doğrulama kurallarını koru.

## Çıktı ve yürütme

Model, desteklenen düşünme seviyesi ve tek cümlelik gerekçe prompt metninin dışında yer alır. Alternatif listeyi ancak birincil öneri kullanılamıyorsa veya kullanıcı karşılaştırma istiyorsa ekle. Belirsizliği ilgili alanın yanında belirt; bir açıklama raporu üretme.

Normal prompt onayı, mevcut ortamda yürütme onayıdır. Önerilen modeli kullanmak isteyen kullanıcı onu arayüzde seçer. Modelin değiştiği doğrulanmadıysa değiştiğini söyleme. Kullanıcı belirli modeli şart koşmuşsa veya bilinen bir yetenek eksikliği varsa, karşılanmayan koşulu açıklayıp gerekli kullanıcı eylemini iste. Model önerisinin değişmesi tek başına yeni AP sürümü veya tekrar prompt onayı gerektirmez.

## Dayanak

2026-09-07 tarihinde kontrol edildi:

- [OpenAI — Model selection](https://developers.openai.com/api/docs/guides/model-selection): kalite gereksinimini karşılayan seçeneklerde maliyet ve gecikmeyi değerlendirme.
- [OpenAI — Models](https://learn.chatgpt.com/docs/models): ortamın model/düşünme seçimi; yüksek düşünme seviyesinin süre ve token tüketimi etkisi.

Bu ilkeler her öneride canlı benchmark yürütme zorunluluğu oluşturmaz. Öneri, mevcut kanıta dayalı bir seçimdir; ölçülmüş evrensel optimum değildir.
