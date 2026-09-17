# Yordamla

[Türkçe katalog](../README.md) · [English: Prompter](../../en/prompter/README.md)

Yordamla, ham isteğinizi mevcut sohbetle tutarlı ve uygulanabilir bir prompta dönüştürür. Gerekli ayrıntı düzeyini seçer, hazırladığı promptu gösterir ve onayınızdan sonra aynı sohbette uygular.

## Kurulum

Skill Installer bulunan Codex ortamında şu mesajı gönderin:

```text
$skill-installer https://github.com/aytacmehmet/public-skills/tree/main/tr/yordamla adresindeki skill'i kur.
```

Alternatif olarak bu skill klasörünü, Codex kurulumunuzun desteklediği bir skill keşif dizinine kopyalayın. Uygun konum için [resmî skill belgesine](https://learn.chatgpt.com/docs/build-skills) bakın. Skill listesinde **Yordamla** göründüğünü kontrol edin; keşif için yeni bir mesaj veya uygulamanın yeniden başlatılması gerekebilir. Kurulu bir kopya varsa değiştirmeden önce koruyun.

## Kullanım

```text
$yordamla Bu sohbette konuştuğumuz geliştirmeyi, onaylı kararları koruyarak ve yalnız gerekli kontrolleri yaparak hazırla.
```

Gönderilen mesajın başındaki `/yordamla` da metinsel takma ad olarak tanınır. Bu, slash menüsüne yeni komut eklemez. Arayüz bu metni kabul etmiyorsa `$yordamla` kullanın veya skill'i seçin.

1. Yordamla isteği ve ilgili sohbet bağlamını değerlendirir.
2. **AP1.v1** gibi bir kimlikle tek prompt ve tek satırlık model notu (model, düşünme seviyesi, gerekçe) gösterir.
3. Yan etkisi olmayan basit iş aynı turda uygulanır. Diğerleri bekler: uygulamak için **“Onaylıyorum”** deyin, değişiklik isteyin veya **“İptal”** yazın.
4. Onaylanan iş aynı sohbette devam eder ve en fazla üç satırlık raporla biter: üretilen, doğrulanan, doğrulanamayan.

Revizyonda yeni sürüm gösterilir ve o sürümün onayı beklenir. Tamamlanan prompta tekrar onay vermek işi yeniden çalıştırmaz. Aktif akış dışındaki sıradan mesajlar normal şekilde ele alınır.

## Model önerisi

Her hazır promptun yanında tek satırlık not bulunur: **model**, **düşünme seviyesi** ve **tek cümlelik gerekçe**; ikinci satır yalnız öneri doğrulanmış mevcut modelden farklıysa eklenir. Seçim önce gereken yetenekleri ve kaliteyi, ardından maliyet ve hızı dikkate alır. Sabit bir model listesi kullanılmaz; model/erişim bilgisi doğrulanamıyorsa öneri koşullu sunulur veya gerekli model profili belirtilir.

Önerilen modeli kullanmak için arayüzden seçin. **“Onaylıyorum” demek modeli otomatik değiştirmez; prompt mevcut ortamda uygulanır.** Belirli bir modeli şart koştuysanız veya mevcut modelin gerekli yeteneği olmadığı biliniyorsa, bu koşul karşılanmadan başka modelle sessizce devam edilmez. Öneri, ölçülmüş bir maliyet veya doğruluk garantisi değildir.

## Gereksiz işi nasıl sınırlar?

2.0.0 tek çalışma zamanı dosyasıdır: `SKILL.md` hiçbir dosyaya bağlantı vermez ve referans yüklemez; her çağrı aynı küçük yönerge kümesine mal olur. Basit/olağan/karmaşık profili açık ölçütlerle seçer (bağımlı çıktı, geri alınamaz yan etki, doğrulanmamış kaynak, birden çok araç).

Prompt alanlı bir şablondan üretilir. Olağan ve karmaşık işlerde her zaman `Kaynaklar` (okunacak dosyalar ve hangisinin yetkili olduğu), `Kapsam dışı`, `Çıktı` (yer, biçim, üst uzunluk), `Kabul` (bir kez çalışan doğrulanabilir tek kontrol) ve `Durma` alanları ile sabit “Tekrar okuma, alt ajan, benchmark veya ek teslimat yok.” satırı bulunur. “Kusursuz” gibi belirsiz nitelikler prompt gösterilmeden ölçülebilir ifadeye çevrilir. Üç maddelik öz-kontrol sonucu değiştirmeyen cümleleri siler. Onaylanan metin yürütmenin tek kapsamıdır; bitiş raporu en fazla üç satırdır.

Ölçülmüş token tasarrufu garantisi veya teknik olarak uygulanan kesin token üst sınırı yoktur. Prompt hazırlama ve onaylaşma da tüketim oluşturur; bu yük çok küçük işlerde belirgin olabilir. Modelinizi veya hesap ayarlarınızı kendiliğinden değiştirmez. Onay, gösterilen işi kapsar; ortamın mevcut izin kuralları geçerlidir.

## Dosyalar ve sürümler

- [SKILL.md](SKILL.md): tek çalışma zamanı dosyası — yönerge, şablon, model notu, onay, uygulama ve kurtarma kuralları — ve sürüm bilgileri.
- [Arayüz bilgileri](agents/openai.yaml): görünen ad, açıklama ve hazır çağrı.
- [Davranış kontrolleri](references/behavior-checks.md): PW01–PW34 bakım senaryolarıdır; tüm senaryoların her ortamda geçtiği iddiası değildir. `references/` altındaki hiçbir dosya çalışma zamanında okunmaz.
- [Kaynaklar](references/source-notes.md): tasarım dayanakları, model seçimi kaynakları ve sınırlar.
- [Değerlendirme](references/evaluation.md): iki sürümü aynı senaryolarla karşılaştırma; eksik ölçümü sıfır saymayan özetleme aracı.
- [Değişiklik geçmişi](CHANGELOG.md) ve [arşivlenmiş sürümler](archived/README.md).
- [GPL-3.0 lisansı](LICENSE).

Güncel sürüm `latest/` veya sürüm numaralı bir alt klasörde değil, doğrudan burada bulunur. Önceki yayımlanmış sürümler `archived/` içinde değiştirilmeyen ZIP kopyaları olarak saklanır. Bu ZIP'leri skill keşfi yapılan bir dizinin içinde açmayın.

Model notu doğrulanmış mevcut modeli veya kimliğin doğrulanamadığını belirtir. Yalnız model notu değişirse prompt yeniden yazılmaz. Duraklatılan iş kalan adımdan sürer; dış işlem sonucu belirsizse yeniden göndermeden önce sonuç kontrol edilir. **Otomatik model geçişi bu sürümde uygulanmış değildir**; ayrı bir entegrasyonun aynı sohbet ve model kimliğini doğrulayarak sınanması gerekir.
