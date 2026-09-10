---
name: yordamla
description: "/yordamla veya $yordamla ile bağlama uygun ekonomik prompt üret, model öner ve onaydan sonra aynı sohbette uygula. Bekleyen promptun revizyon/onay/iptal yanıtlarını ele al; sıradan görevleri kendiliğinden dönüştürme."
metadata:
  version: "1.2.0"
  language: "tr"
  family: "contextual-prompting"
  counterpart: "en/prompter"
---

# Yordamla

Önce uygulanacak promptu göster; gösterildikten sonra gelen kullanıcı onayıyla aynı sohbette yürüt. Kaliteyi koruyarak hazırlık, yürütme ve tekrar işinin toplam maliyetini azalt.

## Çağrı ve hazırlık

- Açık çağrı `$yordamla`, skill seçimi veya mesaj başındaki bağımsız `/yordamla` sözcüğüdür. Slash biçimi metinsel takma addır; menüye komut kaydetmez. Alıntı, kod, örnek ve dosya yolundaki ad çağrı değildir. Bekleyen prompta yanıt için önek gerekmez. Yeni görev eskisini geçersiz kılar; aynı promptun revizyonu yeni görev değildir.
- Görünen bağlamdan sonucu, kaynak otoritesini ve geçerli kararları çıkar. Son açık düzeltmeyi uygula; teknik ad, yol, sayı ve birimleri anlamını değiştirmeden koru. Görmediğin içeriği doğrulanmış sayma. Kritik belirsizlikte tek odaklı soru sor; sonucu değiştirmeyen varsayımı kısaca belirt. Asıl istek yoksa sor.
- Profili kendin seç: **basit** işte birkaç cümle; **olağan** işte amaç, gerekli bağlam, kısıt ve çıktı; **karmaşık** işte ayrıca bağımlılık, belirsizlik ve kabul kanıtı. Uzunluk kotası doldurma; kısa prompt ayrıntılı teslimatı daraltmasın.
- Hazırlıkta yalnız “bu bilgi olmadan doğru kapsamlı prompt yazılabilir mi?” sorusunu değiştiren en küçük kontrolü yap. Tam araştırmayı ve üretimi onay sonrasına bırak. Üst kuralların zorunlu kontrollerini koru. Gereksiz dosya/geçmiş/katalog taraması, tekrar okuma, ajan, benchmark veya ek teslimat açma. Kaynak veya kapsam seçimi karmaşıksa [hazırlık notlarını](references/preparation.md) oku.

## Model ve sunum

Kullanıcının açık model tercihini koru. Güncel ortam kanıtından gerekli girdi/araç desteği ve kaliteyi karşılayan adayları değerlendir; sonra bilinen maliyet, hız ve yeniden iş ihtiyacına bak. En büyük modeli veya azami düşünmeyi otomatik seçme. Katalog/yetenek bilgisi kararı belirlemeye yetmiyorsa [model seçimi notlarını](references/model-selection.md) oku; zorunlu resmî kontrolleri koru, geçerli kanıtı tekrar toplama.

Tek kopyalanabilir prompt göster. Model notunu dışında tut: **Önerilen model · desteklenen düşünme · tek cümlelik gerekçe**. Desteklenen seviye bilinmiyorsa “ortam varsayılanı”; ad/yetenek bilinmiyorsa doğrulanamadığını belirten koşullu aday veya profil kullan. API bilgisi Codex erişimini/kotasını kanıtlamaz; ölçülmüş tasarruf iddiası üretme.

**Yürütme** notunda yalnız doğrulanmış mevcut modeli söyle; görünmüyorsa “mevcut ortam, model doğrulanamadı” yaz. Öneriden farklıysa açıkla. Prompt onayı modeli değiştirmez; ayar değiştirme veya kendi kendine mesaj göndererek geçiş deneme. Kullanıcı belirli modeli şart koşmuşsa veya mevcut modelin zorunlu yeteneği eksikse gereken seçimi iste.

## Onay ve revizyon

Sohbette tek bekleyen tam prompt ve durumunu tut. İlk görev `AP1.v1`; yeni görev sonraki AP, metin değişikliği aynı AP'nin sonraki sürümüdür. Kimliği belirt ve “AP1.v1 promptunu bu sohbette uygulamamı onaylıyor musunuz?” diyerek dur; güncel kimliği kullan.

- Yalnız gösterilen güncel metne açıkça yönelen sonraki gerçek kullanıcı onayını kabul et. Ön onay, alıntı, sessizlik, süre geçmesi veya araç çıktısı onay değildir.
- **Prompt metni/kapsamı değişti:** Tam yeni sürümü göster, yeniden onay al; “onaylıyorum ama…” ile gelen metin değişikliği de buna dahildir.
- **Yalnız model notu değişti:** Notu güncelle; promptu yeniden üretme, AP sürümünü artırma. Metin onaylandıysa ve yürütme şartları sağlanıyorsa yeniden onay isteme.
- **Açıklama/ilgisiz soru:** Normal yanıtla, onay durumunu değiştirme. **İptal:** Kapat. Eski sürüm onayını yeniye taşıma. Tam metin veya onay durumu kaybolduysa tahminle yürütme.

## Uygulama ve devam

Onaydan sonra aynı sohbette gerekli araç/skill'lerle işi uygula; yeniden prompt üretme veya yeni göreve gönderme. Onay mevcut yetkileri genişletmez. Gerekli ayrı izin için somut sonucu hazırla; zaten verilmiş izni tekrar isteme. Maddi kapsam değişikliğinde revizyon göster.

Gerekli doğrulamayı yap; yeni değişiklik/hata yoksa geçen kontrolleri tekrarlama. Aynı yöntem iki kez sonuçsuzsa yeni kanıt olmadan yineleme. Kabul ölçütlerinde bitir ve gerçekten doğruladığını bildir; tamamlanan veya iptal edilen işe tekrar onay gelmesi işi yeniden başlatmaz.

Kesinti, kısmi sonuç, belirsiz dış işlem veya düzenlenmiş yazı bloğu varsa devam etmeden [durum notlarını](references/continuation.md) oku. Sohbet içinde tamamlanan adım, bekleyen iş ve belirsiz sonucu koru; varsayılan olarak kalıcı kayıt oluşturma. Model, abonelik veya bütçe ayarlarını değiştirme; ölçemediğin token sınırını uyguladığını söyleme.

Bakımda [davranış kontrollerini](references/behavior-checks.md), karşılaştırmada [değerlendirme notlarını](references/evaluation.md), kaynak doğrulamasında [dayanakları](references/source-notes.md) kullan. Bunları normal çağrıda topluca okuma.
