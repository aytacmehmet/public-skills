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
2. **AP1.v1** gibi bir kimlikle tek prompt gösterir ve onay ister.
3. Uygulamak için **“Onaylıyorum”** deyin, değişiklik isteyin veya **“İptal”** yazın.
4. Onaylanan iş aynı sohbette devam eder.

Revizyonda yeni sürüm gösterilir ve o sürümün onayı beklenir. Tamamlanan prompta tekrar onay vermek işi yeniden çalıştırmaz. Aktif akış dışındaki sıradan mesajlar normal şekilde ele alınır.

## Gereksiz işi nasıl sınırlar?

Prompt; istenen sonucu, kaynak otoritesini, kısıtları ve yeterli doğrulamayı korur. Kendiliğinden ek rapor, geniş tarama, ek ajan veya başarılı kontrollerin tekrarını istemez. Kısa işlerde kısa prompt üretir; ayrıntılı teslimat istendiğinde gerekli ayrıntıyı korur.

Ölçülmüş token tasarrufu garantisi veya teknik olarak uygulanan kesin token üst sınırı yoktur. Prompt hazırlama ve onaylaşma da tüketim oluşturur; bu yük çok küçük işlerde belirgin olabilir. Modelinizi veya hesap ayarlarınızı kendiliğinden değiştirmez. Onay, gösterilen işi kapsar; ortamın mevcut izin kuralları geçerlidir.

## Dosyalar ve sürümler

- [SKILL.md](SKILL.md): güncel yönerge ve sürüm bilgileri.
- [Arayüz bilgileri](agents/openai.yaml): görünen ad, açıklama ve hazır çağrı.
- [Davranış kontrolleri](references/behavior-checks.md): bakım senaryolarıdır; tüm senaryoların her ortamda geçtiği iddiası değildir.
- [Kaynaklar](references/source-notes.md): tasarım dayanakları ve sınırlar.
- [Değişiklik geçmişi](CHANGELOG.md) ve [arşivlenmiş sürümler](archived/README.md).
- [GPL-3.0 lisansı](LICENSE).

Güncel sürüm `latest/` veya sürüm numaralı bir alt klasörde değil, doğrudan burada bulunur. Önceki yayımlanmış sürümler `archived/` içinde değiştirilmeyen ZIP kopyaları olarak saklanır. Bu ZIP'leri skill keşfi yapılan bir dizinin içinde açmayın.
