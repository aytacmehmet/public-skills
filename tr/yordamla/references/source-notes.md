# Kaynak ve tasarım notları

Kaynak kontrol tarihi: 2026-09-05. Bu dosya bakım içindir; her prompt üretiminde okunmaz veya web'den yenilenmez.

- [OpenAI — Prompting](https://learn.chatgpt.com/docs/prompting): hedefi, sonucu değiştiren bağlamı, çıktı biçimini ve sınırları belirtmek; sırf şablon doldurmak için alan eklememek. Kod işlerinde ilgili kaynak ve doğrulama beklentisini tanımlamak.
- [OpenAI — Cost optimization](https://developers.openai.com/api/docs/guides/cost-optimization): gerekli istek sayısını ve giriş/çıkış miktarını azaltırken doğruluğu korumak. Bu skill prompt boyuyla birlikte yürütme ve tekrar iş maliyetini sınırlamayı hedefler; API önerilerini masaüstü aboneliği için ölçülmüş kota kazancı olarak sunmaz.
- [OpenAI — Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization): daha az istek, ilgili bağlamı seçme ve gereksiz üretimi azaltma. Gecikme, token, ücret ve kota kazancı eşit kabul edilmez. Bağımsız araç okumalarını birleştirmek çoklu ajan zorunluluğu oluşturmaz.
- [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills): ayırt edici açıklama, gerektiğinde yüklenen yönerge ve isteğe bağlı referanslar. `$yordamla` açık skill çağrısıdır; `/yordamla` açıklamaya göre eşleştirilen bir metinsel takma addır ve uygulama menüsüne özel komut kaydetmez.

Keşif ve kurulum yolları Codex yüzeyine ve sürümüne göre değişebilir. Kurulum için [skill tanıtımını](../README.md) izleyin ve kendi ortamınızda keşfi kontrol edin. Arşiv ZIP'lerini kurulum klasörü içinde açmayın: eski `SKILL.md` dosyaları ayrıca keşfedilebilir.

`agents/openai.yaml` varsayılan keşif politikasını korur. `allow_implicit_invocation: false`, `$` ile açık çağrıyı korurken `/yordamla` metinsel takma adının keşfini zayıflatabilir. Kullanım sınırı SKILL.md içindedir.

AP kimlikleri, sürüme bağlı onay, iş profilleri ve iki sonuçsuz denemeden sonra yeniden teşhis bu skill'in tasarım tercihleridir; resmî ürün garantisi değildir. İş profillerinin optimum olduğu veya belirli oranda token tasarrufu sağlandığı ölçülmüş değildir. Bir skill tek başına kesin toplam token sınırı uygulayamaz.

1.1.0 model önerisi için 2026-09-07 tarihinde kontrol edilen kaynaklar ve seçim sınırları [model seçimi notlarında](model-selection.md) bulunur. Sabit model listesi tutulmaz; öneri ile gerçek model seçimi ayrı ele alınır.
