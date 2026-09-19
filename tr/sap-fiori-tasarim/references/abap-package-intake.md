# ABAP paketinden UI sözleşmesi çıkarma

Bu referansı kullanıcı bir ABAP paketi, ADT projesi, abapGit dışa aktarımı veya paket adı üzerinden UI5/Fiori ekranı geliştirilmesini istediğinde oku.

## Amaç ve sınır

Paket kaynaklarını ekran gereksinimi gibi yorumlamadan önce makine-okunur `abap-backend-contract.json` üret. Bu sözleşme paket envanterini, RAP/CDS/OData kabiliyetlerini ve her çıkarımın kaynak dosyasını UI tasarımına bağlar.

Kaynak okumak, backend'in iş amacını tek başına kanıtlamaz. Paket içinde bulunmayan gereksinim, rol, süreç, yayımlanmış servis URI'si, hedef tenant release'i veya runtime yetkisini uydurma. Parser lexical bir kanıt çıkarır; ABAP compiler, ADT activation, service preview veya runtime authorization kanıtı değildir.

## Desteklenen girişler

### Yerel paket

ADT veya abapGit dışa aktarım klasörü ya da ZIP'i için:

```powershell
python -B "<skill kökü>/scripts/inspect_abap_package.py" <paket-klasörü-veya-zip> `
  --output <çıktı>/abap-backend-contract.json `
  --package-name Z_MY_PACKAGE `
  --service-uri /sap/opu/odata4/sap/z_ui_service/srvd/sap/z_ui_service/0001/ `
  --protocol odata-v4
```

`--service-uri` yalnız hedef sistemde gözlenmişse ver. Kaynak dosyadan URI tahmin etme.

Pakette birden fazla service definition varsa inspector ilkini seçmez; `service.definition` değerini `unknown` bırakır ve `gaps` içine yazar. UI servisini `--service-definition <ad>` ile ver. Seçilen servis birden fazla entity expose ediyorsa ve tek bir root entity ayırt edilemiyorsa ana entity set'i `--entity-set <ad>` ile ver. İkisini de kaynak veya `$metadata` kanıtıyla seç.

Service binding protokolü `ODATA V4` gibi tek ifadeden ya da abapGit/ADT export'larındaki ayrı tip + sürüm alanlarından (`<TYPE>ODATA</TYPE><VERSION>V4</VERSION>`, `type="ODATA" version="V2"`) okunur; ikisi de yoksa `unknown` kalır.

### Canlı ADT paketi

Yalnız önceden yapılandırılmış salt-okunur ADT bağlantısı ve araçları mevcutsa (örnek adımlar `sap-cloud-erp` MCP sunucusuna göredir; başka bir host'ta aynı okuma işlemlerinin karşılığını kullan):

1. `load_toolset(profile="source-read")` veya gerekli araçları içeren read-only profil kullan.
2. `list_packages` ile tüm sayfaları oku; `truncated=true` veya `nextOffset` varsa devam et.
3. UI sözleşmesini etkileyen `DDLS`, `DDLX`, `BDEF`, `SRVD`, `SRVB`, `DCLS` ve ilgili `CLAS` kaynaklarını `read_source`, `read_cds_source` veya `read_repository_object` ile **active** sürümden oku.
4. Sayfalı kaynakta her devam çağrısında önceki `sha256` değerini `expectedSha256` olarak geçir. Son sayfaya kadar okumadan kaynağı tam sayma.
5. Sonuçları aşağıdaki normalleştirilmiş snapshot biçiminde, credential/host/client içermeden kaydet ve inspector'a ver.

```json
{
  "packageName": "Z_MY_PACKAGE",
  "objectCount": 3,
  "objects": [
    {
      "name": "Z_I_ORDER",
      "type": "DDLS/DF",
      "uri": "/sap/bc/adt/ddic/ddl/sources/z_i_order",
      "version": "active",
      "truncated": false,
      "source": "define root view entity Z_I_Order ..."
    }
  ]
}
```

Ardından:

```powershell
python -B "<skill kökü>/scripts/inspect_abap_package.py" <adt-snapshot.json> `
  --output <çıktı>/abap-backend-contract.json `
  --service-uri <gözlenen-uri> --protocol odata-v4
```

Skill, SAP bağlantısı yoksa kullanıcıdan parola/RSA/private key istemez. Yerel export ister veya bağlantının proje sahibi tarafından yapılandırılmasını blocker olarak bildirir. Paket okuma isteği yazma, aktivasyon, publish, transport veya deploy yetkisi vermez.

## Okuma önceliği

Paket büyükse önce ince uçtan uca dilim oku:

1. `SRVB` + `SRVD`: protokol, yayımlanan servis ve entity set sınırı
2. Projection `DDLS` + `DDLX`: UI'ya açılan alan, association ve annotation
3. Projection/root `BDEF`: draft, create/update/delete, action, validation ve side effect
4. Interface/root `DDLS`: anahtarlar, composition/association, currency/unit/text/value help
5. `DCLS` ve behavior authorization: backend yetki kanıtı
6. Yalnız UI davranışını etkileyen behavior implementation class/method'ları

Paket envanteri 200 öğeyi aşıyorsa sayfalama ve kapsamlı okuma planını sözleşmede belirt. İsme bakıp ilgili görünmeyen nesneyi sessizce atlama; tür bazında neden kapsam dışı olduğunu kaydet.

## Inspector çıktısını okuma

- `model.entities[].fields/keys`: element listesinden okunan alanlar. `exposedAssociations` alan değildir; navigation adayıdır.
- `model.entities[].unparsedElements`: lexical okuyucunun sınıflandıramadığı elementler (örneğin alias'sız `case` ifadesi). Her biri bir `gap` üretir ve `ready` sonucunu engeller; alanı `$metadata` ile doğrulayıp sözleşmeye elle bağla.
- `behavior.definitions[]`: her `define behavior for` için ayrı kayıt. `create/update/delete`, parantezli yazımı da (`update ( features : instance );`) tanır; `createByAssociation` alt nesne oluşturmayı ayrı tutar.
- `behavior.actions` yalnız iş action'larıdır; `draftActions` (Edit, Activate, Discard, Resume, Prepare) framework'e aittir, buton olarak tasarlanmaz.
- `dynamicFeatureControl`: enablement'ı çalışma zamanında belirlenen işlem ve action'lar. Disabled/hidden durumunu ve testini bunlar için planla.
- `etag` ve `totalEtag` ayrı alanlardır; concurrency senaryosunu ikisine göre yaz.
- `model.entities[].kind`: `view-entity`, `custom-entity`, `abstract-entity` veya `classic-view`. Abstract entity action parametresidir, ekran nesnesi değildir; custom entity'nin sorgusu ABAP sınıfındadır, filtre/sıralama/sayfalama desteğini `$metadata` ve testle doğrula.
- `uiSemantics.fields`: DDLS ve DDLX'ten okunan alan → annotation eşlemesi. Özetleri `lineItemFields`, `selectionFields`, `identificationFields`, `fieldGroupFields`, `hiddenFields`, `valueHelpFields`, `textFields`, `amountFields`, `quantityFields` listeleridir (`Entity.Alan`). List Report kolonlarını, filtreleri ve value help'leri bunlardan türet; annotation değerlerinin kendisi (position, importance, qualifier) için kaynağı oku.
- `uiSemantics.searchableEntities`: `@Search.searchable: true` taşıyan entity'ler. Listede olmayan entity set'e `$search` gönderme.
- `service.bindings[].serviceDefinition`: binding'in gösterdiği tanım. Birden fazla tanım varken okunabilen binding'lerin hepsi aynı tanımı gösteriyorsa inspector onu seçer; bu bir tahmin değil kanıttır. Binding okunamıyorsa (`unknown`) seçim yine sana kalır.
- `source.inventoryVerified` ve `notes`: yalnız nesne sayısını beyan eden ADT snapshot'ı envanterle karşılaştırılabilir. Yerel export'ta değer `false` kalır; eksiksizlik sağlayanın beyanıdır ve doğrulayıcı bunu `info` olarak bildirir.
- ZIP girişinde üye başına 2 MB, toplamda 50 MB ve 200 kat sıkıştırma oranı sınırı vardır; aşan paket okunmadan reddedilir.

## UI kararına dönüştürme

`abap-backend-contract.json` içinden en az şu eşlemeyi kur:

| Backend kanıtı | UI kararı |
|---|---|
| Projection entity ve expose alias | Entity set, route ve sayfa kimliği |
| `@UI.lineItem`, selection field, facet, field group | List Report/Object Page bilgi mimarisi |
| Draft behavior | Edit/save/cancel ve unsaved-change akışı |
| RAP action + feature control | Action placement, enablement ve test |
| Validation/message target | Field/message popover ve hata senaryosu |
| Association/composition | Navigation, section/table ve `$expand` bütçesi |
| Value help/text/currency/unit | Kontrol tipi, display formatı ve request planı |
| DCL/authorization master | Backend enforcement ve no-auth state |
| ETag/lock/side effect | Concurrency, refresh ve stale-data senaryosu |

Her satırı `design-contract.json.traceability` içinde backend nesne/dosya ve test kimliğiyle bağla. Bir action veya alan kaynakta yoksa frontend'de varmış gibi üretme.

## Hazırlık kapısı

Üretim koduna geçmeden:

- Paket/snapshot eksiksiz ve active kaynaklardan mı?
- Service definition ve binding protocol kanıtlandı mı?
- Gerçek servis URI'si ve `$metadata` hedef sistemde görüldü mü?
- Exposed entity set ile projection/BDEF aynı transaction sınırında mı?
- Draft, authorization, value help, message ve side effect durumu açık mı?
- UI annotation'ları tasarım sözleşmesiyle tutarlı mı?
- Hedef release ve kullanılan SAP nesnelerinin release durumu ayrıca doğrulandı mı?

Eksik olanı `gaps` ve `blocked/assumed` olarak koru. Inspector'ın `ready` sonucu dahi gerçek `$metadata`, preview, activation, authorization veya released-object kanıtının yerine geçmez.
