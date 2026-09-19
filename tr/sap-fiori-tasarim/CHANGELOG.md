# Değişiklik geçmişi

## 1.0.0 — 2026-09-19

- İngilizce SAP Fiori Design ile eşleştirilmiş ilk herkese açık yayın.
- Sözleşme odaklı akış: ABAP paketinden `abap-backend-contract.json`, ondan `design-contract.json`; aynı sözleşmeden interaktif UI5 prototipi, prototipten alınan PNG ve TypeScript freestyle veya Fiori elements OData V4 üretim iskeleti.
- Uyarıda da başarısız olan statik teslim doğrulayıcısı: strict JSON, paket içi şema, SHA-256 kanıt zinciri, sözleşme ↔ manifest tutarlılığı, deprecated/güvensiz kalıplar.
- Service binding protokolü, abapGit ve ADT export'larındaki ayrı tip + sürüm alanlarından da okunur; XML namespace URL'leri artık yorum sanılıp kesilmez.
- Behavior definition her entity için ayrı ve ifade bazında okunur: parantezli `create/update/delete`, association üzerinden create, dinamik feature control, function'lar; draft action'lar iş action'larından ayrılır; `etag` ile `total etag` ayrı tutulur.
- CDS element listesi iç içe ve çok satırlı annotation'ları, virgül içeren ifadeleri ve tırnak içindeki `//` dizgisini doğru okur; sınıflandıramadığı elementi düşürmek yerine `unparsedElements` ve `gaps` içine yazar.
- Birden fazla service definition veya entity set adayı varsa ilkini seçmez; `--service-definition` ve `--entity-set` ile açık seçim ister.
- Scaffold profili artık hedef sistem runtime'ı olarak raporlanmaz: `--target-ui5-runtime` ayrı verilir, verilmezse `unknown` kalır; doğrulayıcı `minUI5Version` değerinin runtime'dan yeni olmamasını denetler. Varsayılan profil `version-profiles.json` içindeki `defaultProfile` alanından okunur.
- Renk ve sabit metin denetimleri daraltıldı: route hash'i, ID seçicisi, ikon URI'si ve harf içermeyen değerler bulgu üretmez.
- Betikler çalışma dizininden bağımsız `<skill kökü>` yoluyla ve `python -B` ile çağrılır.

Önceki herkese açık sürüm: yok.
