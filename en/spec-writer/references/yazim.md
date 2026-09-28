# Writing rules

Generated file (source: assets/tanim.json).

## Cell and id rules

- Every cell is a non-empty string; `—` means none.
- Ids have the form `PREFIX-nn`, two digits, unique across the document.
- Several ids are listed one by one, comma-separated: `STEP-01, STEP-02`. A range (`STEP-01…06`) is invalid.
- A section refers to another section only by id. Chain: REQ → SC → STEP → OBJ / MAP / MSG → TC.
- In 3.5 a step that uses mappings cites the MAP ids and a step that raises an error cites the MSG id; 4.1 'Kullanıldığı yer' cites STEP / MAP / UI ids. 6.2 is derived from these references.

## Markers

- Missing decision: `KARAR BEKLİYOR (OPEN-nn)` · missing fact: `BİLGİ BEKLİYOR (OPEN-nn)`. Option columns may carry a marker too. An unknown fact is never filled with a default value (`Hayır`, `Must`, an invented date).
- A 7.3 row carries no marker. Owner: a name, or a role when unknown. Target date: when given; otherwise `—`, never invented. Status `Açık`. The row a KARAR marker points to gets the category `Karar bekleyen konu`; other rows get the fitting readiness item or `—`.
- Decision and fact markers tied to the same question may share one OPEN-nn; the row's category is then `Karar bekleyen konu`.
- The known part of a cell is written; only the unknown part gets a marker: `HTTP POST; zaman aşımı KARAR BEKLİYOR (OPEN-03)`.
- When a section that cannot be switched off waits entirely on one decision, write its minimum number of rows; known cells as text, decision-dependent cells as markers. Marker rows are not multiplied.
- An SAP standard object name found neither in the inputs nor in the project catalog is written only in 4.1 with ` [DOĞRULANACAK]` appended; one open point in 7.3 covers all such names.
- Custom (Z/Y) names may be proposed according to the project naming rule.

## Readiness penalty categories (7.3)

| Category | When |
|---|---|
| Yayına alınmamış nesne | Dependency on an SAP object that is not released or whose release state is unverified |
| Açık ATC/CVA bulgusu | Priority 1–2 finding not closed in ATC or CVA |
| Tasarım/sözleşme açığı | Missing design or contract information: counterpart schema, error codes, field list, sample message |
| Geçici çözüm / hardcode | Deliberately left hard-coded value or workaround |
| Karar bekleyen konu | A decision not yet made; every row a KARAR BEKLİYOR marker points to |
| İstisna kaydı yapılmamış bulgu | No approved exemption record for a known deviation (clean core level, ATC exemption) |
| — | None fits (for example only a date or an owner name is awaited) |

## EARS requirement patterns (2.2)

| Pattern | Syntax | Example |
|---|---|---|
| Her zaman geçerli | <Sistem> <tepki> yapar. | Sistem her gönderimi ZPO_SEND_LOG tablosuna yazar. |
| Durum (While) | <Durum> sürerken <sistem> <tepki> yapar. | Status = 'Q' iken sistem 'Yeniden gönder' aksiyonunu pasif tutar. |
| Olay (When) | <Olay> olduğunda <sistem> <tepki> yapar. | Sipariş onayı tamamlandığında sistem siparişi 5 dk içinde portala gönderir. |
| Opsiyon (Where) | <Özellik> varsa <sistem> <tepki> yapar. | Tedarikçide portal kullanıcısı varsa sistem e-posta yerine portala gönderir. |
| İstenmeyen durum (If-then) | <İstenmeyen durum> olursa <sistem> <tepki> yapar. | Portal 5xx dönerse sistem 1, 5 ve 15 dk sonra yeniden dener. |
| Bileşik | <Durum> sürerken, <olay> olduğunda <sistem> <tepki> yapar. | Status = 'E' iken kullanıcı 'Yeniden gönder'e bastığında sistem kaydı 'Q' yapar. |

The acceptance criterion has the form Given – When – Then: precondition and test data · triggering event · observable result and where it is observed.

## Concrete replacement instead of a vague phrase

| Do not write | Write instead |
|---|---|
| gerekli kontroller yapılır | Which field, which condition, which MSG: 'Supplier boşsa MSG-04 (E)' |
| ilgili tablolardan okunur | Object name: 'I_PurchaseOrderAPI01'den PurchaseOrder, Supplier okunur' |
| uygun şekilde / gerektiğinde | Write the condition: 'Status = E iken' |
| hızlı / performanslı | A measure: '500 sipariş ≤ 10 dk' |
| kullanıcı dostu | The behaviour: 'zorunlu alan boşsa alan kırmızı, MSG-05' |
| vb. / gibi / çeşitli | Write the full list |
| sisteme kaydedilir | Where and how: 'ZPO_SEND_LOG'a RAP save sequence içinde' |
| standart süreç işletilir | Application name and step: 'Manage Purchase Orders (F0842A) → Onaya gönder' |
| daha sonra belirlenecek | Write it into 7.3 as OPEN-nn with owner and date |

Patterns the validator looks for: `gerekli kontrol`, `ilgili tablo`, `ilgili alan`, `ilgili yer`, `uygun şekilde`, `gerektiğinde`, `gerekirse`, `mümkünse`, `kullanıcı dostu`, `performanslı`, `hızlı bir şekilde`, `hızlı şekilde`, `sisteme kaydedilir`, `standart süreç`, `daha sonra belirlenecek`, `netleştirilecek`, `çeşitli`, `vb`, `vs.`, `v.b.`, `esnek bir`, `kolayca`, `sorunsuz`.

## Concreteness

- A measure instead of an adjective: duration, count, volume, retention period, retry count are written with a number and a unit.
- Object and field names are written: `I_PurchaseOrderAPI01.PurchaseOrder`; never 'ilgili tablo'.
- Test data has a real format: document number, master data number, company code.
- In RAP, persistence happens inside the save sequence; `COMMIT WORK` is not written.
