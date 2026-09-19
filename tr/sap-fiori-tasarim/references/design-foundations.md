# SAP Fiori görsel ve etkileşim temelleri

Bu referansı görsel tasarım, tema, token, tipografi, ikon, responsive davranış veya erişilebilirlik kararı verirken oku.

## İçindekiler

1. Sürüm ve kanıt kuralı
2. Tasarım ilkeleri
3. Tema ve design token
4. Renk ve semantik
5. Tipografi
6. İkonografi ve illüstrasyon
7. Responsive ve adaptive tasarım
8. Content density
9. Erişilebilirlik
10. UX metni ve yerelleştirme
11. Görsel kalite guardrail'leri

## 1. Sürüm ve kanıt kuralı

Bu özet 12 Ağustos 2026 tarihinde SAP Fiori for Web guideline v1.148 ve SAPUI5 Demo Kit 1.151.0 gözlenerek hazırlanmıştır. Bu iki sürüm aynı olmak zorunda değildir. Her işte hedef runtime'ı doğrula, ardından o runtime'a uygun versioned Fiori guideline ve UI5 API dokümanını kullan.

- [Guideline versioning](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/versioning)
- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web)
- [SAPUI5 Demo Kit](https://ui5.sap.com/)

SAP'nin resmî `sap-fiori-guidelines` AI skill'i v1.145 (Mayıs 2026) tabanlı ve deneysel olarak işaretlidir. Onu yararlı bir indeks say; hedef sürümün canlı dokümanının yerine koyma.

- [SAP AI Skill for Fiori Guidelines](https://www.sap.com/design-system/fiori-design-web/v1-145/resources/ai-skills/sap-fiori-guidelines)
- [SAP AI Skills Library kaynağı](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines)

## 2. Tasarım ilkeleri

Her ekranı şu beş ilkeye karşı değerlendir:

- **Role-based:** Belirli rolün kararını ve günlük görevini destekle; tüm veriyi göstermek yerine karar için gerekli veriyi öne çıkar.
- **Adaptive:** Cihaz, giriş yöntemi ve çalışma koşuluna uyum sağla; yalnız masaüstünü küçültme.
- **Coherent:** SAP genelindeki kontrol, eylem, mesaj ve navigasyon davranışını koru.
- **Simple:** Gereksiz alan, eylem, dekorasyon ve aşamayı kaldır; ilerlemeli açıklama kullan.
- **Delightful:** Hızlı, öngörülebilir ve güven veren geri bildirim üret; görsel gösterişi görev başarısının önüne koyma.

Kaynak: [SAP Design Principles](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/design-principles)

Kanonik mockup referansı olarak SAP Fiori for Web UI Kit'i kullan. Kontrolü serbestçe yeniden çizmek yerine UI Kit/SAPUI5 karşılığını seç.

Kaynak: [SAP Fiori for Web UI Kit](https://www.sap.com/design-system/fiori-design-web/v1-148/resources/libraries/sap-fiori-for-web-ui-kit)

## 3. Tema ve design token

Varsayılan modern görsel dil Horizon'dır. Hedef sistem farklı bir temaya sabitlenmişse o temayı koru.

- Morning Horizon: açık tema
- Evening Horizon: koyu tema
- High Contrast Black / High Contrast White: yüksek kontrast
- Quartz Light / Quartz Dark: hedef sistem gerektirirse

Morning/Evening Horizon WCAG 2.2 AA; Horizon yüksek kontrast temaları WCAG 2.2 AAA hedefler. Tema desteğini uygulama CSS'iyle yeniden üretme.

Kaynak: [Theming](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/theming)

Token kuralları:

1. Hard-coded renk, font, gölge, radius ve kontrol ölçüsü yazma.
2. Hızlı markalama için uygun main/base token; kontrol uygulaması için kararlı semantik component token kullan.
3. Reference palette değerini doğrudan kontrol CSS'ine bağlama.
4. Figma/prototip ve kod kararında aynı semantik token adını kaydet.
5. Müşteri markalamasını tekil CSS yamalarıyla değil UI Theme Designer/token zinciriyle çöz.
6. Hover, focus, active, selected, disabled ve high-contrast durumlarını birlikte doğrula.

Kaynak: [Design Tokens](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/design-tokens)

Özel CSS gerçekten gerekirse:

- Önce standart control property, aggregation, layout data, utility class ve theme parameter ara.
- CSS'i küçük, scoped ve tema bağımlılığından arındırılmış tut.
- Private DOM/class selector kullanma; patch release ile kırılabilir.
- Inline style ve XML içinde native HTML/SVG kullanma.

## 4. Renk ve semantik

Morning Horizon görsel referansında vurgu mavisi `#0070F2`, uygulama zemini `#F5F6F7`, ana metin `#131E29`, ikincil metin `#556B82` görülür. Bu değerleri koda doğrudan yazma; tema parametresinden getir.

Kaynak: [Morning Horizon Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/colors/morning-horizon)

Semantik eşleme:

| Semantik | Anlam | Uygun kullanım |
|---|---|---|
| Neutral | Normal/yorum gerektirmeyen | Düzenli durum |
| Positive | İyi/başarılı kalıcı durum | Tamamlandı, uygun |
| Critical | Dikkat, engellemeyen risk | Yaklaşan son tarih, inceleme gerekli |
| Negative/Error | Hata veya kötü durum | Engelleyici sorun, reddedildi |
| Information | Gerçek bilgilendirme | Dikkat gerektiren nötr bilgi |

Semantik rengi dekorasyon için kullanma. Renk tek başına anlam taşımasın; metin, status ve/veya ikonla destekle. Industry/indication rengi yalnız alanın yerleşik renk sözleşmesi varsa kullan ve semantik palette aynı kontrol içinde karıştırma.

Kaynak: [Using Semantic and Industry-Specific Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/how-to-use-semantic-colors)

Kontrast hedefleri:

- Normal metin ve metin benzeri ikon: en az 4.5:1
- Büyük metin, kalın metin benzeri ikon ve anlamlı grafik: en az 3:1
- Odak göstergesi ve durum farkı: renkten bağımsız algılanabilir

## 5. Tipografi

- `72` ailesini kullan; yüklenemezse `72full`, Arial, Helvetica, sans-serif fallback sırasını koru.
- Kontrolün hazır typographic style'ını kullan; başlığı salt font büyüklüğüyle taklit etme.
- Semantik heading hiyerarşisini sayfa → bölüm → alt bölüm düzeyinde koru.
- Küçük metni ana içerik yapma; düşük ağırlığı küçük etiketlerde kullanma.
- Uzun/satır kırılan içerikte yaklaşık 1.5 satır yüksekliği kullan.
- Kullanıcının locale'ine göre sayı, tarih, saat, para ve birim formatla.

Kaynak: [Typography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/typography/typography-horizon)

## 6. İkonografi ve illüstrasyon

Önce mevcut SAP Horizon ikonunu ara. İkonu:

- İşlevsel ipucu, yerleşik metafor veya dar toolbar alanı için kullan.
- Temel metin etiketinin yerine kullanma.
- Süs ve kalabalık yaratmak için ekleme.
- Karmaşık veya kültüre özgü kavramı tek başına taşımaya zorlama.

Boyut rehberi:

- Standart: 16 px
- Mutlak önerilen alt sınır: 12 px
- Standart component içindeki üst sınır: 48 px
- SVG varsayılan; icon font desteklenir

Erişilebilirlik:

- Icon-only etkileşime erişilebilir ad ve tooltip ver.
- Dekoratif ikonu yardımcı teknolojiden gizle.
- Anlamlı ikonu metin/etiketle destekle.
- LTR/RTL yön değişimi ve kültürel metaforu kontrol et.

Kaynak: [Iconography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/iconography/iconography-horizon)

Üretken görsel modeli, SAP kontrolü veya yazılı UI ekranı çizmek için kullanma. Dekoratif illüstrasyon gerekiyorsa ayrı asset üret, illüstrasyon stilini ve erişilebilir alternatif metni doğrula; UI öğelerini gerçek SAPUI5 ile render et.

## 7. Responsive ve adaptive tasarım

Responsive: Aynı işlev ve bilgiyi alan değiştikçe yeniden akıtmak. Adaptive: Cihaz kabiliyeti, bağlamı veya görev amacı değiştiğinde farklı sunum/etkileşim sağlamak.

Breakpoints:

| Sınıf | Genişlik |
|---|---:|
| S | ≤ 599 px |
| M | 600–1023 px |
| L | 1024–1439 px |
| XL | ≥ 1440 px |

Kaynaklar:

- [Responsiveness and Adaptiveness](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/responsiveness-adaptiveness)
- [Responsive Spacing](https://www.sap.com/design-system/fiori-design-web/v1-148/page-types/page-layouts/spacing)

Kurallar:

- Mobile-first bilgi önceliği belirle.
- 12 sütunlu responsive grid'i uygun layout ile kullan.
- Sabit width/height ile yerleşim kurma.
- Grid/Analytical/Tree Table'ın telefonda tam responsive olmadığını kabul et; Responsive Table, kart/liste veya ayrı adaptive görünüm tasarla.
- Telefonda kimlik ve karar alanlarını koru; düşük önemi pop-in/hide ile azalt.
- Uzun çeviri, RTL ve browser zoom ile taşmayı test et.

## 8. Content density

- Touch için cozy, mouse/keyboard yoğun kullanım için compact seç.
- Hibrit cihazda kullanıcı/ortam seçimini koru.
- Cozy hedef alanı yaklaşık 2.75 rem / 44 px'tir.
- Aynı sayfa ve navigasyon hiyerarşisinde cozy ile compact'ı karıştırma.
- Daha çok veri göstermek için fontu küçültme; bilgi önceliği ve layout seçimini düzelt.

Kaynak: [Cozy and Compact](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/cozy-compact)

## 9. Erişilebilirlik

Framework erişilebilirliği başlangıçtır; uygulama bağlamı yine doğrulanmalıdır.

Her teslimde:

- Açık ve kalıcı label kullan; placeholder'ı label yapma.
- İlk odağı mantıklı yere koy; tab sırası ve F6 gruplarını doğrula.
- Tüm eylemlere klavye eşdeğeri ve görünür focus ver.
- Heading, landmark, role, state ve property ilişkilerini koru.
- Hata mesajında yer, neden ve düzeltme yolunu anlat.
- Görsel/ikon alternatif metnini bağlama göre üret.
- Screen reader, keyboard-only, zoom/text resize ve high-contrast kontrolü yap.
- Custom control'ü son çare yap; seçersen ARIA, keyboard, theme, zoom, RTL, security, performance ve bakım sorumluluğunu üstlen.

Kaynaklar:

- [Accessibility in SAP Fiori](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/product-standards/accessibility-in-sap-fiori)
- [Keyboard Support](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/interaction/keyboard-support)
- [UI5 ARIA Labeling](https://ui5.sap.com/#/topic/f38c21c2f71e455e8d4a959522035a1f)

UI5 ARIA önceliklerini karıştırma: `labelFor`, `aria-label` ve `aria-labelledby` seçeneklerini bağlama göre seç; birbiriyle gelişigüzel birleştirme.

## 10. UX metni ve yerelleştirme

- Eylem metnini kısa ve fiille başlat: Create, Save, Approve gibi.
- Teknik hata kodunu tek başına gösterme; kullanıcı etkisi ve çözüm yolunu açıkla.
- Status metnini tutarlı terminolojiyle kullan.
- Çevrilebilir metni controller/XML içine hard-code etme; i18n'e taşı.
- Çoğul, parametre, tarih, saat, sayı, para ve birim için framework formatter/type kullan.
- Uzun Almanca benzeri metin, Türkçe karakterler ve RTL ile layout'u test et.

Kaynak: [Accessible UX Writing](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/writing-and-wording/ux-writing/ux-writing-guidelines/accessibility)

## 11. Görsel kalite guardrail'leri

Şunlardan biri varsa tasarımı düzeltmeden teslim etme:

- SAP kontrolünü taklit eden özel HTML/CSS
- Hard-coded marka/semantik renk veya font
- Aynı page/dialog içinde birden çok emphasized primary action
- Renkle tek başına status anlatımı
- Placeholder ile label yerine geçme
- Masaüstü tablosuna mobil alternatif olmaması
- Focus görünmemesi veya keyboard trap
- Empty/error/loading/no-auth durumunun atlanması
- PNG'nin interaktif prototipten farklı alan/eylem/durum göstermesi
- Custom control için erişilebilirlik ve tema testinin olmaması
