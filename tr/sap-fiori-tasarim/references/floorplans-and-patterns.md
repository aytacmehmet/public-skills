# SAP Fiori floorplan ve UI pattern kararları

Bu referansı bilgi mimarisi, floorplan, tablo/form/filter/dialog, eylem yerleşimi, mesaj ve durum tasarlarken oku.

## İçindekiler

1. Karar sırası
2. Floorplan seçim matrisi
3. Dynamic Page ve Flexible Column Layout
4. List Report ve Object Page
5. Form, tablo ve Filter Bar
6. Dialog ve navigation
7. Eylem yerleşimi
8. State ve messaging
9. Empty, error ve loading
10. Stop/uyarı koşulları

## 1. Karar sırası

1. Rolü, görevi, veri hacmini, işlem sıklığını, nesne yaşam döngüsünü, cihazları ve runtime'ı çıkar.
2. Standart floorplan ara.
3. Standart annotation/OData senaryosunda Fiori elements'i seç.
4. Yalnız desteklenmeyen etkileşim veya gerçekten özgün düzen varsa freestyle seç.
5. Kontrolü estetiğe göre değil veri semantiği, hacmi, görev ve cihaz desteğine göre seç.
6. Koddan önce state ve responsive matrisi oluştur.

Ana kaynak: [When to Use Which Floorplan](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/when-to-use-which-floorplan)

## 2. Floorplan seçim matrisi

| İhtiyaç | Varsayılan seçim | Kaçın |
|---|---|---|
| Rol bazlı KPI, görev ve farklı uygulamalardan özet | Overview Page | Tek veri kümesinde ayrıntılı arama/işleme |
| Büyük veri kümesinde arama, filtre, sıralama ve işlem | List Report | Yoğun chart-table kök neden analizi |
| KPI, görsel filtre, slice-and-dice ve chart/table analizi | Analytical List Page | Yalnız kayıt bulma |
| Önceden belirlenmiş iş öğelerini sırayla işleme | Worklist | Genel kayıt keşfi |
| Tek nesneyi görüntüleme/oluşturma/düzenleme | Object Page | Toplu düzenleme veya kayıt arama |
| Alışılmadık, uzun 3–8 adımlı işlem | Wizard | İki adımdan kısa veya sekizden uzun akış |
| Bilinen kimlikle tek nesneye gitme | Initial Page | Sonucun liste olacağı arama |
| List-detail veya list-detail-detail | Flexible Column Layout + uygun floorplan'ler | Dashboard/workbench/bağımsız sayfalar |

Kaynaklar:

- [List Report](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/list-report-floorplan-sap-fiori-element)
- [Analytical List Page](https://experience.sap.com/fiori-design-web/analytical-list-page/) — eski `experience.sap.com` sayfası; güncel `sap.com/design-system` eşdeğerini hedef sürümde doğrula
- [Object Page](https://experience.sap.com/fiori-design-web/object-page/) — eski `experience.sap.com` sayfası; güncel `sap.com/design-system` eşdeğerini hedef sürümde doğrula
- [Worklist](https://www.sap.com/design-system/fiori-design-web/v1-120/page-types/floorplans/work-list/usage)
- [Initial Page](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/floorplans/initial-page-floorplan/usage)
- [Wizard](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/wizard/usage)

## 3. Dynamic Page ve Flexible Column Layout

### Dynamic Page

Dynamic Page, title/header, content ve isteğe bağlı finalizing footer'dan oluşan temel sayfa layout'udur. Standart floorplan uygunsa onu elle Dynamic Page olarak yeniden kurma.

- Header daraldığında ana başlık ve önemli eylemleri koru.
- Header içeriği yoksa expand/collapse/pin ekleme.
- Footer'ı yalnız workflow'u bitiren eylemler için kullan.
- Object Page'de Dynamic Page Header kullan; eski Object Header kullanma.
- Yeni freestyle sayfada Filter Bar'ı Dynamic Page header content'e koy.
- Floorplan'in tamamını bir Dynamic Page content alanına gömme.

Kaynak: [Dynamic Page Layout](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/dynamic-page-layout/usage)

### Flexible Column Layout

FCL yalnız list-detail veya list-detail-detail için, en fazla üç kolonla kullanılır.

- Doğrudan üç kolonla başlama.
- Boş detail kolonu gösterme.
- Her kolonun kendi header, scroll ve gerekiyorsa footer davranışı olsun.
- Bütün kolonları saran ikinci bir app header/footer üretme.
- S ekranda son drill-down kolonu tam ekran göster; back akışını koru.
- M ekranda sınırlı iki kolon; L/XL'de uygun oranları kullan.
- Dialog'u tek kolon üzerinde sağa hizalama; bütün ekran üzerinde ortala.
- FCL'yi dashboard, workbench, side panel veya aynı nesneyi bölmek için kullanma.

Kaynak: [Flexible Column Layout](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/page-layouts/flexible-column-layout/)

## 4. List Report ve Object Page

### List Report

Kayıt bulma ve veri kümesi üzerinde işlem yapma için kullan.

- Filter Bar'ı header content'e yerleştir.
- Basic Search'ü tablo toolbar'ına değil Filter Bar'a koy.
- Mümkünse canlı filtreleme kullan; `Go` yalnız pahalı sorgu/yoğun trafik/birden çok filtreyi hazırlama gerektiğinde kullan.
- Mandatory filtreye güvenli varsayılan değer ver veya boş başlangıcı açıkça tasarla.
- Page variant ve table variant'ı kopuk iki kişiselleştirme modeli yapma.
- Sıralama, gruplama ve kolon ayarlarını P13n yaklaşımında topla; yalnız gereken personalization özelliklerini aç.
- Rastgele page action için footer kullanma.
- KPI ve chart-table analizi merkezdeyse Analytical List Page'e geç.

### Object Page

Tek business object'in display/create/edit yaşam döngüsü için kullan.

- Section → subsection → form/table/chart hiyerarşisini koru.
- Birden çok bölümde anchor navigation; uzun ve ayrık konularda tab navigation değerlendir.
- Tek bölümde gereksiz navigation gizle.
- Başlıkları içerikte tekrar etme.
- Breadcrumb'ı yalnız gerçek nesne üst-alt hiyerarşisinde kullan.
- Form label'ını top-aligned seçmeyi varsayılan değerlendir.
- Responsive kolon başlangıcı: S=1, M=2, L=3, XL=6; içerik uzunluğuna göre azalt.
- Çok uzun tablo bağlamı bozuyorsa ayrı List Report veya tab tasarla.

Kaynak: [Object Page Content Area](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/frameworks/sap-fiori-elements/object-page/object-page-content-area-sap-fiori-elements)

## 5. Form, tablo ve Filter Bar

### Form

- Field/value verisini görev sırasına göre grupla.
- Tekrar eden kayıt için form değil tablo kullan.
- Label'ı kısa, açık ve kalıcı yap; placeholder'ı label yapma.
- Display modunda display-only; edit içinde değiştirilemeyen önemli değerde read-only kullan. Disabled ile taklit etme.
- Required işaretini edit bağlamında göster.
- Save/Create sırasında bütün doğrulamaları çalıştır; geri bildirimi yalnız finale bırakma.
- Hata metninde alanı, nedeni ve çözümü anlat.

Kaynaklar:

- [Form Layout](https://experience.sap.com/fiori-design-web/explore_group/form-layout-container/) — eski `experience.sap.com` sayfası; güncel `sap.com/design-system` eşdeğerini hedef sürümde doğrula
- [Form Field Validation](https://experience.sap.com/fiori-design-web/form-field-validation/) — eski `experience.sap.com` sayfası; güncel `sap.com/design-system` eşdeğerini hedef sürümde doğrula

### Tablo/list seçimi

| Veri/görev | Kontrol |
|---|---|
| Bağımsız satırlar, tüm cihazlar | Responsive Table |
| Az ayrıntılı basit öğe | List |
| 1000+ satır, hücre karşılaştırma, yoğun masaüstü kullanım | Grid Table + mobil adaptive alternatif |
| Gerçek çok seviyeli grouping, subtotal/grand total | Analytical Table |
| Gerçek hiyerarşik veri, sınırlı seviye | Tree Table + mobil alternatif |

Kurallar:

- Tabloyu field/value formu, küçük seçim listesi veya dashboard görselleştirmesi için kullanma.
- Telefonda key/kimlik alanını koru; düşük önemi pop-in/hide yap.
- Yatay kaydırmayı mobil strateji sayma.
- No-data ve no-results durumlarını ayır; sonraki eylemi söyle.
- Büyük veri için server-side paging/filter/sort kullan.

Kaynaklar:

- [Table Overview](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/ui-elements/tables/table-overview)
- [Responsive Table](https://www.sap.com/design-system/fiori-design-web/v1-96/ui-elements/responsive-table/usage)

### Filter Bar

- List Report ve Overview Page'de standart; ALP'de Visual Filter alternatifi vardır.
- Object Page section table, Wizard veya basit List içine koyma.
- Desktop expanded/collapsed; tablet varsayılan collapsed; telefon filter dialog davranışı tasarla.
- Sık kullanılan, mandatory ve veri hacmini en çok azaltan filtreleri varsayılan görünür yap.
- Basit domain için select/combo/date control kullan; gereksiz value help açma.
- Yeniden filtrelemede eski seçimlerin yanlışlıkla korunmasını engelle.

Kaynak: [Filter Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/filter-bar/)

## 6. Dialog ve navigation

### Dialog

- Geçici, modal ve sınırlı karmaşıklıktaki işlem için kullan.
- Basit mesaj için MessageBox; normal başarı için toast; büyük create/edit için Object Page kullan.
- Nested dialog yapma.
- Dialog içine floorplan koyma.
- Telefonda full-screen davranış seç.
- Genellikle 1–2 action kullan; primary emphasized olabilir, Cancel emphasized olmasın.
- Uzun formda görünmeyen validation hataları için Message Popover sağla.

Kaynak: [Dialog](https://experience.sap.com/fiori-design-web/dialog/) — eski `experience.sap.com` sayfası; güncel `sap.com/design-system` eşdeğerini hedef sürümde doğrula

### Navigation

- Önemli page state'i deep link/bookmark ile yeniden kurulabilir yap.
- Display/edit değişimini gereksiz route state yapma.
- Breadcrumb'ı back veya cross-app navigation yerine kullanma.
- Dynamic Side Content'i kritik içerik, navigation veya list-detail yerine kullanma.
- Icon Tab Bar'ı yalnız gerçekten ayrık içerik görünümleri için kullan.

Kaynaklar:

- [Navigation](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/global-patterns/navigation/navigation)
- [Breadcrumb](https://www.sap.com/design-system/fiori-design-web/ui-elements/breadcrumb/)
- [Icon Tab Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/icontabbar/)
- [Dynamic Side Content](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/dynamic-side-content/usage)

## 7. Eylem yerleşimi

- Navigation action'ını solda; business/page action'ını sağda tut.
- Header + footer toplamında yalnız bir page-level primary action kullan.
- Footer'ı Save/Create/Submit gibi finalizing action için kullan.
- Table/chart toolbar'ını yalnız o içerik üzerindeki local action için kullan.
- Destructive action'a açık metin, uygun semantic treatment ve gerekiyorsa confirmation ver.
- Yetkisiz action'ı yalnız gizlemekle güvenceye alma; backend yetkisini zorunlu kıl.

Kaynak: [Action Placement](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/global-patterns/action-placement)

## 8. State ve messaging

### UI element state

| State | Kullanım |
|---|---|
| Enabled | Kullanılabilir veya neden kullanılamadığı önceden anlaşılmıyor |
| Disabled | Geçici olarak kullanılamıyor ve nasıl açılacağı açık |
| Hidden | Rol/state/mode nedeniyle gerçekten mevcut değil |
| Read-only | Edit modunda önemli ama değiştirilemez |
| Display-only | Display modunda veya hiçbir zaman düzenlenmez |
| Error | Finalize etmeyi engeller |
| Warning | Engellemeyen risk |
| Success | Kalıcı başarı durumu gerçekten önemli |
| Information | Gerçek dikkat gerektiren nötr bilgi |

Bir kontrolü aynı anda birden fazla value state ile işaretleme. Selection checkbox'ını disabled yaparak yetki anlatma.

Kaynak: [UI Element States](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/ui-element-states)

### Mesaj bileşeni

| İhtiyaç | Bileşen |
|---|---|
| Karar/onay gerektiren non-field sorun | MessageBox |
| Birden çok form/table alan mesajı | MessagePopover |
| Action sonucunda birden çok non-field mesaj | MessageView |
| Kısa, kesintisiz başarı | MessageToast |
| Kalıcı genel/object-level bilgi | MessageStrip |
| Page/component empty veya message state | IllustratedMessage/Message Page |
| Field validation | Value State + açıklayıcı metin |

Toast'ı error/warning için kullanma. Navigation sonrası toast'ı hedef sayfada göster. Veri kaybı yaratacak cancel/back/navigation için uyarı ver.

Kaynak: [Messaging](https://www.sap.com/design-system/fiori-design-web/v1-120/foundations/best-practices/global-patterns/messaging/messaging)

## 9. Empty, error ve loading

Şu durumları ayrı tasarla:

- İlk kullanım / henüz veri yok
- Search/filter sonucu yok
- Kullanıcı eylemi sonrası boşalma
- Sistem/servis hatası
- Yetki veya configuration eksikliği

Her durumda başlık, neden ve sonraki adım ver. No-results'ı sistem hatası gibi gösterme.

Kaynak: [Designing for Empty States](https://www.sap.com/design-system/fiori-design-web/v1-96/foundations/best-practices/global-patterns/designing-for-empty-states)

Loading kuralları:

- Yaklaşık bir saniyeden kısa işlemde spinner flaşı üretme.
- Yalnız etkilenen control/region'ı busy yap; shell'i gereksiz bloklama.
- Busy Dialog'u tüm etkileşimin gerçekten kilitleneceği uzun işlemde kullan.
- Skeleton/placeholder'ı ilk app/app-to-app yüklemede, gerçek floorplan yapısını temsil ederek kullan.
- Progress Indicator'ı belirsiz spinner yerine kullanma; yalnız ölçülebilir ilerleme için kullan.
- Hata oluşunca busy state'i kapat, error/retry state'ine geç.

Kaynak: [Busy Handling](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/ui-elements/busy-handling)

## 10. Stop/uyarı koşulları

Şunlardan biri varsa düzelt veya açık blokaj bildir:

- Eski Object Header
- Object Page subsection içinde Filter Bar
- Form amacıyla tablo
- Nested dialog veya dialog içinde floorplan
- Birden fazla page-level primary action
- Semantik rengin dekorasyon/tek anlam kanalı olması
- Grid/Analytical/Tree Table için mobil alternatif olmaması
- Hard-coded renk/ölçü/layout
- Loading/empty/error/no-auth durumunun eksikliği
- Hedef runtime'ın desteklemediği kontrol/API
- Mockup ile kodun alan/eylem/state bakımından ayrışması
