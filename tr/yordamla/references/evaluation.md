# Sınırlı davranış ve maliyet karşılaştırması

Bu dosya yalnız bakım/değerlendirme içindir. Normal prompt üretimi sırasında test veya benchmark çalıştırma.

[Altı eşlenmiş senaryo](evaluation-cases.json), küçük metin, belirsizlik, kod, kaynak otoritesi, yalnız model notu değişikliği ve belirsiz dış işlem sonucunu kapsar. İngilizce karşılıkları aynı kimlik ve kontrol anahtarlarını kullanır. Yeni davranış eklenirken ilgili karşı örnekleri [davranış listesine](behavior-checks.md) de ekle.

İlk eleme için aynı altı girdiyi eski ve yeni yönergeyle değerlendir: 12 yanıt. Her senaryoyu bağımsız kabul et. Yanıtları gözleyerek `checks` alanındaki her ölçütü değerlendir; anahtar sözcük eşleşmesini davranış kanıtı sayma. Toplu konuşma simülasyonu gerçek bağımsız çalışma maliyetini ölçmez.

Karşılaştırma aracı model çağırmaz; dışarıda üretilmiş sonuçları özetler. Depo kökünden:

```text
python .github/scripts/evaluate_prompts.py --cases tr/yordamla/references/evaluation-cases.json --results <sonuclar.json>
```

Sonuç dosyası, her senaryo için `baseline` ve `candidate` kayıtlarını içeren bir JSON dizisidir. Her kayıtta `variant`, `case_id`, `language`, gözlenen tam `response`, senaryonun tüm kontrol adlarını boolean değerlerle içeren `checks` ve `mode` bulunur. `mode`, `simulation` veya `isolated` olur. Eksik/çift kayıt, eksik kontrol veya başarısız davranış başarı sayılmaz. Notları/gözlemleri uydurma.

Gerçek ölçüm için aynı girdiyle ayrı çalışmalarda doğrulanmış `model`, `effort`, `input_digest` ve varsa `total_tokens`, `latency_ms`, `tool_calls` kaydet. Girdi kimliği, skill sürümü dışındaki girdi/bağlamın aynı olduğunu belirtir. Model, düşünme veya girdi farklıysa maliyet karşılaştırması yapılmaz. Bilinmeyen metrikleri atla veya `null` yaz; sıfır uydurma. Toplam tokenı ortamdan al; önbellek ve düşünme kırılımlarını toplama ikinci kez ekleme.

Özetin `null` metrikleri ölçülmemiş/karşılaştırılamaz demektir. Araç, verilen notları veya telemetriyi bağımsız doğrulamaz; fatura veya optimum model garantisi üretmez. Kalite kaybı olan aday, daha az token kullansa da iyileştirme sayılmaz. Değişken çıkan örnekleri tekrarla; her kullanımda geniş model karşılaştırması açma.
