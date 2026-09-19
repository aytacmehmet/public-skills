# RAP, OData ve ABAP Cloud UI sözleşmesi

Bu referansı Fiori ekranı RAP/OData/ABAP backend'e bağlanacaksa veya “ABAP için optimize” tasarım isteniyorsa oku.

## İçindekiler

1. İlke ve kapsam
2. Hedef sistem ve Clean Core
3. RAP/Fiori elements kararları
4. UI annotation sözleşmesi
5. Veri ve performans sözleşmesi
6. Transaction, draft ve side effect
7. Validation, message ve authorization
8. Service/versioning güvenliği
9. Kabul kontrol listesi

## 1. İlke ve kapsam

“ABAP için optimize Fiori tasarımı” yalnız az frontend kodu demek değildir. Şunları birlikte sağla:

- UI görevi ile business object sınırını eşleştir.
- Metadata/annotation ile standard UI davranışını backend-driven yap.
- Filtre, sıralama, paging, aggregate ve business validation'ı uygun biçimde server'a taşı.
- Minimal payload ve az request üret.
- Draft, action, side effect, message ve authorization semantiğini uçtan uca tasarla.
- Released API ve extension point dışına çıkma.

RAP, CDS tabanlı model, behavior ve service exposure ile Fiori UI için doğal sözleşme sunar.

Kaynak: [ABAP RESTful Application Programming Model](https://help.sap.com/docs/abap-cloud/abap-rap)

## 2. Hedef sistem ve Clean Core

Önce hedefi ayır:

- SAP S/4HANA Cloud Public Edition
- SAP S/4HANA Cloud Private Edition
- SAP S/4HANA on-premise
- SAP BTP ABAP Environment

Public Edition developer extensibility için:

- ABAP Cloud language version kullan.
- Yalnız hedef release'te released SAP object/API kullan.
- Yalnız released/predefined extension point kullan.
- Yeni transactional servis için RAP tercih et.
- Internal table, CDS, class, function module veya BAPI adını tahmin etme.
- Released API bulunamazsa bunu gap/blocker olarak raporla; unreleased nesneye otomatik düşme.

Release contract özeti:

| Contract | Amaç |
|---|---|
| C0 | Extend |
| C1 | Sistem içinde kararlı kullanım |
| C2 | Remote API |
| C3 | Configuration content |

Kullanılabilirliği ADT Released Objects ve hedef ürün/release dokümanında doğrula. Başka release'te released olması yeterli değildir.

Kaynaklar:

- [Released APIs](https://help.sap.com/docs/ABAP_Cloud/abap-development-tools-user-guide/released-apis)
- [Public Released APIs](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis)
- [Developer Extensibility](https://help.sap.com/docs/SAP_S4HANA_CLOUD/6aa39f1ac05441e5a23f484f31e477e7/657285a09f7148d894c27bb8e17827cf.html)
- [Clean Core Extensibility](https://help.sap.com/docs/abap-cloud/developer-guide-from-classic-abap-to-abap-cloud/clean-core-extensibility-and-abap-based-extensions)

## 3. RAP/Fiori elements kararları

Standard transactional UI için:

1. CDS data model ve projection oluştur.
2. Behavior definition/projection ile transactional contract tanımla.
3. UI'ya yalnız gerekli projection entity/action'larını service definition'da expose et.
4. OData V4 UI service binding oluştur.
5. Fiori elements preview ile annotation ve behavior'ı erken doğrula.

Kaynaklar:

- [Defining Business Service for Fiori UI](https://help.sap.com/docs/abap-cloud/abap-rap/defining-business-service-for-fiori-ui?version=s4hana_cloud)
- [Service Binding](https://help.sap.com/docs/abap-cloud/abap-rap/service-binding)

OData V4'ü geleceğe dönük default değerlendir. Hedef sistem/kapsam V2 gerektiriyorsa bilinçli V2 tasarla; V2 servisi V4 modelle taklit etme.

Fiori elements V4 için güncel resmî dokümana göre:

- Framework control'leri için bir ana servis varsay.
- Servisin `$count`, `$skip`, `$top` ve gerekli filter/sort davranışını desteklemesini doğrula.
- Edit senaryosunda draft gereksinimini hedef framework dokümanında doğrula.
- Custom page/building block'un aynı servis ve transaction sınırına uyduğunu kontrol et.

Kaynak: [Fiori Elements V4 Prerequisites](https://ui5.sap.com/docs/topics/f2344b5e78164b2b9c27ef8b068f295c.html)

## 4. UI annotation sözleşmesi

Mümkün olduğunca standard UI davranışını annotation ile tanımla:

- `@UI.lineItem`: liste/table alanı ve row action
- `@UI.identification`: nesne tanımlama ve object-level action
- `@UI.headerInfo`: başlık, type name ve image/icon semantiği
- `@UI.fieldGroup`: form alan grubu
- `@UI.facet`: Object Page section/subsection yapısı
- `@UI.selectionField`: başlangıç filter'ları
- Value help, text association, currency/unit ve semantic object ilişkileri
- Criticality/status semantiği

Annotation'ı yalnız teknik kolaylık için doldurma. Bilgi mimarisi ve `design-contract.json` ile eşleştir. Aynı label/visibility/criticality mantığını frontend'de tekrar etme.

Projection katmanında UI'ya özgü semantiği, interface view'da reusable domain semantiğini tutmayı değerlendir. Mevcut proje standardına uy.

Kaynak: [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)

## 5. Veri ve performans sözleşmesi

Her sayfa için veri bütçesi çıkar:

- İlk render'da hangi alanlar zorunlu?
- Hangi navigation yalnız drill-down'da yüklenebilir?
- Hangi aggregate/KPI server'da hesaplanmalı?
- Hangi filtre index/partition ve selectivity açısından önemlidir?
- Kaç satır hedeflenir ve page size nedir?

Kurallar:

- Projection'da UI'ya gerekmeyen alan/association expose etme.
- `$select` ve dar `$expand` için metadata/navigation tasarımını destekle.
- N+1 request üretme; row başına action/lookup tasarlama.
- Büyük entity set için server-side paging/filter/sort zorunlu yap.
- Client'a bütün veri çekip filtreleme/aggregate yapma.
- CDS/HANA pushdown'a uygun expression/association kullan; ABAP loop ile hesaplamayı varsayılan yapma.
- Value help'i küçük ve arama/filter destekli tasarla; bütün domain'i eager yükleme.
- Currency/unit ve text association'ı ayrı elle roundtrip gerektirmeyecek biçimde modelle.
- Fiori elements `autoExpandSelect` davranışıyla controller'ın gizli alan ihtiyacını çakıştırma; controller alanını açık contract yap.

Kaynaklar:

- [OData V4 Performance](https://ui5.sap.com/docs/topics/5a0d286c5606424b8e0d663c87445733.html)
- [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html)

## 6. Transaction, draft ve side effect

UI edit akışını behavior model ile aynı yap:

- Managed/unmanaged seçimini mevcut business logic ve persistence ownership'e göre yap.
- Create/Edit/Save/Cancel state'ini draft/non-draft contract'la eşleştir.
- Backend action'ını kullanıcı niyetine göre adlandır; generic “Process” kullanma.
- Action enablement/feature control'ü backend state ve yetkiye bağla.
- Bir alan değişince başka alan, permission veya message değişiyorsa RAP side effect tanımla.
- Determination ve validation zamanını UI beklentisiyle eşleştir.
- Concurrency/ETag ve lock davranışını açıkça tasarla.
- Long-running action için async/job pattern ve progress/refresh stratejisi belirle; HTTP isteğini gereksiz uzun tutma.

Kaynak: [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)

## 7. Validation, message ve authorization

Validation:

- Client-side validation'ı hızlı UX için kullan; aynı kuralı backend'de zorunlu uygula.
- Cross-field ve business validation'ı RAP behavior'da yap.
- Mesajı entity/field target ile ilişkilendir; kullanıcıya yer, neden ve çözüm ver.
- Teknik exception metnini doğrudan UI'ya sızdırma.
- Error finalize etmeyi engellesin; warning karar akışını gereksiz bloklamasın.

Authorization:

- Data access ve action authorization'ı backend'de uygula.
- UI visibility/enabled state'i yalnız yardımcı gösterim say.
- Yetkisiz field/action'ı metadata/feature control ile yansıt, fakat backend kontrolünü kaldırma.
- Projection/service'te hassas alanı gereksiz expose etme.
- Log, trace ve message içinde hassas veri yayınlama.

## 8. Service/versioning güvenliği

- UI service ve remote Web API amacını ayır.
- Service definition'ı client'a gereken projection ile sınırla.
- Breaking değişiklikte versioning ve backward compatibility planla.
- Entity/property/action adını bir kez yayınlandıktan sonra rastgele değiştirme.
- Annotation ve service metadata'yı target UI5/Fiori elements sürümünde test et.
- Local publish/preview sonucunu dış sistem erişilebilirliği sanma.
- Destination, authentication ve network trust'i kod içine gömme.

Kaynak: [Service Binding](https://help.sap.com/docs/ABAP_Cloud/f055b8bf582d4f34b91da667bc1fcce6/service-binding?version=s4hana_cloud)

## 9. Kabul kontrol listesi

- [ ] Hedef sistem/release ve ABAP language version doğrulandı
- [ ] Kullanılan SAP object/API release durumu hedef sistemde doğrulandı
- [ ] Floorplan ile RAP business object sınırı uyumlu
- [ ] OData V4/V2 kararı gerekçeli
- [ ] Projection yalnız gerekli alan/action/navigation'ı expose ediyor
- [ ] Annotation, design contract ile eşleşiyor
- [ ] `$count/$skip/$top`, filter, sort ve paging desteği doğrulandı
- [ ] Payload minimal; N+1 ve client-side full-set işlem yok
- [ ] Draft/non-draft, save/cancel, ETag/lock ve side effect tasarlandı
- [ ] Validation/message target'ı kullanıcıya anlaşılır
- [ ] Authorization backend'de uygulanıyor
- [ ] Unit/integration/service preview ve UI testleri çalıştırıldı
- [ ] Released olmadığı doğrulanmamış hiçbir nesne “released” diye raporlanmadı
