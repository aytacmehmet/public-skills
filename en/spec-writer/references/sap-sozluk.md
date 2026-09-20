# SAP Cloud ERP terim sözlüğü

Doğru sınıflandırma ve doğru sütuna doğru bilgiyi yazmak içindir; tavsiye içermez. Hangi seçeneğin kullanılacağı danışmanın kararıdır.

## Genişletme yaklaşımları (1.1 `yaklasim`)

| Terim | Anlamı | Belgede tipik izleri |
|---|---|---|
| Key user extensibility | Kod yazmadan uyarlama: özel alan, özel mantık, form şablonu | 4.3'te özel alan / özel mantık; 7.2'de software collection |
| Developer extensibility (on-stack, ABAP Cloud) | Sistem içinde ABAP Cloud ile geliştirme | 4.1'de DDLS, BDEF, SRVD, SRVB, CLAS; dil versiyonu "ABAP for Cloud Development" |
| Side-by-side (SAP BTP) | Sistemden ayrık, API ve olaylarla bağlı uygulama | 3.10'da API / olay sözleşmesi; 3.4'te gelen-giden eşleme |

## Clean core seviyeleri (1.1 `clean_core`)

| Seviye | Tanım |
|---|---|
| A | Yalnız released API ve genişletme noktaları |
| B | A + classic API'ler (belgelenmiş, genelde yükseltmeye dayanıklı) |
| C | SAP dahili nesnelerine erişim; yükseltme riski |
| D | Modifikasyon, SAP tablolarına yazma, implicit enhancement |

A dışındaki seviye için 1.1 `cc_gerekce` doldurulur ve risk 7.3'e yazılır.

## Release contract (1.2 tablosu, 4.1 "Dil versiyonu / release contract")

| Contract | Anlamı |
|---|---|
| C0 | Extend: nesne genişletilebilir (örn. CDS view extension) |
| C1 | Use system-internally: ABAP Cloud kodundan kullanılabilir |
| C2 | Use as remote API: dışarıdan OData / SOAP ile tüketilebilir |
| C3 / C4 | Configuration content yönetimi / AMDP içinde kullanım |

## RAP ve servis terimleri (1.2, 3.5, 4.1)

| Terim | Not |
|---|---|
| Managed / unmanaged | Kalıcılığı çerçevenin mi, özel kodun mu yaptığı |
| Save sequence | Kalıcılığın gerçekleştiği aşama; 3.5 "Commit / rollback" sütununda buna atıf yapılır, `COMMIT WORK` yazılmaz |
| Draft | Kaydedilmemiş verinin sunucuda tutulması; 1.2 `draft` |
| Determination / validation / action | Davranış tanımı öğeleri; 3.5 adımlarında ve 3.3 aksiyonlarında adlarıyla geçer |
| Service definition / binding | SRVD / SRVB; binding tipi 1.2 `binding_tipi` |
| Fiori elements floorplan | List report, worklist, object page, analytical list page, overview page; 3.3 `floorplan` |

## Public Cloud işletim terimleri

| Terim | Nerede yazılır |
|---|---|
| Communication scenario → arrangement → system | 3.4 `comm_scenario`, 3.10; arrangement her sistemde elle kurulur → 3.1 ve 7.2 |
| IAM app → business catalog → business role | 5.3 |
| Restriction type / field; Read, Write, Value help erişimi | 5.2, 5.3 |
| Transport request (geliştirici nesneleri), software collection (key user nesneleri) | 7.2 |
| Geliştirme (development + customizing tenant), test, üretim sistemleri | 3.1 "Sistem / tenant", 7.2 "Sistem" |
| Application job (catalog entry, template) | 3.4 `tetikleyici`, 4.1 tipi Application job |
| Application log (nesne / alt nesne) | 7.1 "Hedef" |
| ABAP Test Cockpit (ATC); öncelik 1–2 bulgu | 6.3 |

## 4.1 "SAP tipi" sütununda kullanılacak değerler

Kod olarak: TABL tablo · DDLS CDS view entity · DDLX metadata extension · DCLS access control · BDEF behavior definition · SRVD service definition · SRVB service binding · CLAS sınıf · INTF arayüz · DTEL veri elemanı · DOMA domain · MSAG mesaj sınıfı · SUSO yetki nesnesi · ENHO genişletme uygulaması · DEVC paket

Adıyla: BAdI · API · Business event · Fiori app · UI5 app · IAM app · Business catalog · Application job · Communication scenario · Outbound service · Inbound service · Software component · Custom field · Form template · Application log object · Number range · Business role template · Launchpad space / page

Aynı adı taşıyan nesneler (örneğin bir CDS view entity ile onun BDEF ve DCLS nesnesi) ayrı satırlara yazılır. Parantez içinde açıklama eklenebilir: `CLAS (behavior implementation)`.
