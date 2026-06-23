# Dentual Konya — Teknik Dokümantasyon

> **Sürüm:** 1.0 · **Tarih:** 23 Haziran 2026
> **Depo:** `github.com/buqr4/dentual-website` (branch: `main`)
> **Canlı:** `https://dentualkonya.netlify.app` · **Hedef alan adı (henüz alınmadı):** `dentualkonya.com`
> **Amaç:** Projeyi devralacak geliştiriciler için sistemin tam teknik fotoğrafı.

> ⚠️ **Doğruluk notu:** Bu doküman, kodun **gerçek mevcut durumunu** belgeler — pazarlama/ön-tasarım niyetlerini değil. Örn. proje **Tailwind kullanmaz** (el yazımı CSS), hosting **Netlify**'dır (Cloudflare Pages değil), analytics ID'leri henüz **placeholder**'dır, `dentualkonya.com` henüz **satın alınmamıştır**. Bu farklar ilgili bölümlerde açıkça işaretlidir.

---

## İçindekiler
1. [Proje Genel Özeti](#1-proje-genel-özeti)
2. [Kullanılan Teknolojiler](#2-kullanılan-teknolojiler)
3. [Site Mimarisi](#3-site-mimarisi)
4. [Site Haritası](#4-site-haritası)
5. [SEO Raporu](#5-seo-raporu)
6. [Lighthouse ve Performans Çalışmaları](#6-lighthouse-ve-performans-çalışmaları)
7. [Tasarım Sistemi](#7-tasarım-sistemi)
8. [Dönüşüm ve Pazarlama Altyapısı](#8-dönüşüm-ve-pazarlama-altyapısı)
9. [Güvenlik ve Altyapı](#9-güvenlik-ve-altyapı)
10. [Dosya ve Klasör Yapısı](#10-dosya-ve-klasör-yapısı)
11. [Eksik ve Geliştirilebilir Alanlar](#11-eksik-ve-geliştirilebilir-alanlar)

---

## 1. Proje Genel Özeti

### Amaç
Dentual Konya ağız ve diş sağlığı polikliniğinin **kurumsal tanıtım ve yerel SEO odaklı** web sitesi. Birincil iş hedefi: Konya/Selçuklu/Karatay/Meram bölgesinde organik aramalarda üst sıralara çıkıp, ziyaretçiyi **telefon veya WhatsApp üzerinden** kliniğe yönlendirmek.

### Hedef Kitle
- Konya ve ilçelerinde (özellikle Selçuklu, Karatay, Meram) diş hekimi arayan hastalar
- **Acil / gece diş ağrısı** yaşayan kullanıcılar (öne çıkan farklılaştırıcı: "pazar dahil her gün 23:00'a kadar açık")
- Çocuk diş hekimliği (pedodonti), implant, gülüş tasarımı, ortodonti arayanlar

### Temel İşlevler
- Çok sayfalı statik tanıtım sitesi (hizmetler, şubeler, blog, iletişim)
- **Şube bazlı telefon + WhatsApp CTA'ları** (her şube kendi numarasına yönlenir)
- Hizmet detay sayfaları (modal + ayrı URL'ler)
- Bilgi merkezi / blog (4 yazı)
- TR/EN dil desteği (istemci tarafı i18n)
- Açık/koyu tema
- İletişim formu (WhatsApp'a yönlendiren)
- Dentual Çocuk tanıtım videosu

> **Açık mimari kararı:** Bu projede **online randevu sistemi YOKTUR**. Dönüşüm tamamen telefon/WhatsApp üzerinden ilerler (bkz. [Bölüm 8](#8-dönüşüm-ve-pazarlama-altyapısı)).

### Kullanıcı Akışları (özet)
1. **Arama → Ana sayfa → Acil bant → WhatsApp/Telefon** (en kısa dönüşüm)
2. **Arama → Hizmet sayfası → İletişim/WhatsApp**
3. **Arama → "gece açık diş" sayfası → Nöbetçi şube (Selçuklu) → WhatsApp**
4. **Arama → Şube sayfası → Harita + o şubenin WhatsApp/telefon**
5. **Blog → İçerik → CTA → İletişim**

### Dönüşüm Hedefleri
| Hedef | Ölçüm noktası |
|---|---|
| Telefon araması | `tel:` tıklamaları (`phone_call_click`) |
| WhatsApp görüşmesi | `wa.me` tıklamaları (`whatsapp_click`, şube etiketli) |
| Form gönderimi | İletişim formu (`lead_form_submit`) → WhatsApp'a yönlendirir |
| Yol tarifi | Harita açılışı (`map_open`) |

### WhatsApp Yönlendirme Sistemi
Her şube **kendi** WhatsApp numarasına yönlenir; numaralar birbirine karışmaz:

| Şube | Telefon | WhatsApp (wa.me) |
|---|---|---|
| Karatay | 0546 733 27 13 | `905467332713` |
| Selçuklu (gece nöbetçi) | 0551 342 44 42 | `905513424442` |
| Meram | 0552 599 49 59 | `905525994959` |
| Çağrı Merkezi | 444 34 42 | — |

WhatsApp linkleri ön-doldurulmuş mesaj içerir; analytics tarafında şube etiketiyle (`branchOf()`) ayrıştırılır.

### Şube Yapısı
3 fiziksel şube. Veri kaynağı tektir: `tools/gen_pages.py` içindeki `BRANCHES` dizisi (slug, ad, telefon, adres, harita embed). Tüm şube sayfaları ve şema bu diziden üretilir.

---

## 2. Kullanılan Teknolojiler

### Frontend
| Teknoloji | Durum | Amaç |
|---|---|---|
| **HTML5 (semantik)** | ✅ Kullanımda | `header/nav/main/section/article/footer`, ARIA, skip-link |
| **CSS (el yazımı, tek dosya)** | ✅ Kullanımda | `css/style.css` (~935 satır), CSS değişkenleri ile tasarım sistemi |
| **Tailwind CSS** | ❌ **Kullanılmıyor** | Başta düşünülmüş ancak uygulanmamış. Stil tamamen özel CSS ile yazılı. Build adımı yok. |
| **Vanilla JavaScript (IIFE)** | ✅ Kullanımda | `js/script.js` (~1220 satır), framework yok, tek IIFE modül |
| **Harici JS kütüphanesi** | ❌ Yok | jQuery/React/Vue yok — sıfır bağımlılık. SVG ikonlar inline. |
| **Google Fonts** | ✅ | `Poppins` (gövde) + `Plus Jakarta Sans` (başlık), `display=swap` |

**Mimari tarzı:** Çok sayfalı (MPA) statik site. Her rota gerçek bir `index.html` dosyasıdır (SPA değil). JS, "progressive enhancement" olarak çalışır (sayfa JS olmadan da içerik sunar).

### Sayfa Üretimi (Build)
- **`tools/gen_pages.py`** (~770 satır, yalnız Python `json, os` — stdlib): `index.html`'in "chrome"unu (announcement bar → nav → footer/script) kaynak alır, her alt sayfaya başlık/açıklama/şema/içerik damgalar. 18 alt sayfa + `404.html` + `sitemap.xml` üretir.
- **`tools/convert_webp.py`**: Görsel optimizasyon yardımcı betiği (WebP/AVIF üretimi).
- HTML için **derleme zinciri yok**; üretilen dosyalar repoda işlenir (committed). Netlify build'i de aynı betiği çalıştırır (`netlify.toml`).

### SEO Teknolojileri
| Yapı | Detay |
|---|---|
| **Schema.org (JSON-LD)** | 20+ tip: `WebSite, MedicalClinic, Dentist, FAQPage, BreadcrumbList, MedicalProcedure, BlogPosting, ContactPage, AboutPage, CollectionPage, Blog, OpeningHoursSpecification, PostalAddress, GeoCoordinates, AggregateRating, City/AdministrativeArea` |
| **Meta yapısı** | `description, keywords, robots, author, canonical, theme-color`, tam **Open Graph** + **Twitter Card** seti |
| **Sitemap** | `sitemap.xml` (19 URL, `gen_pages.py` üretir) |
| **Robots** | `robots.txt` → `Allow: /` + sitemap referansı |
| **Çok dilli** | `hreflang` yapısı i18n ile TR/EN (istemci tarafı) |

### Performans Teknolojileri
| Alan | Uygulama |
|---|---|
| **Görsel** | WebP + **AVIF** (hero), `image-set()` iki-katman fallback; tüm fotoğraflar WebP |
| **Hero LCP** | İlk slide preload (`<link rel=preload as=image>` AVIF, `fetchpriority=high`); slide 2-7 `data-bg` ile lazy (`requestIdleCallback`) |
| **Video** | HEVC `.MOV` → H.264 MP4 (faststart); `preload="none"` + poster → oynatılana kadar inmez |
| **Font** | `preconnect` + `display=swap`; sınırlı ağırlık seti |
| **CLS** | Hero typewriter satırı sabit yükseklik; tüm medya konteynerlerinde `aspect-ratio` |
| **Önbellek** | `_headers` ile asset'ler `immutable` 1 yıl, HTML `no-cache` |

### Hosting & Dağıtım — **GERÇEK DURUM**
| Katman | Gerçek | Not |
|---|---|---|
| **Kaynak kontrol** | GitHub (`buqr4/dentual-website`) | ✅ |
| **Hosting** | **Netlify** (`dentualkonya.netlify.app`) | ✅ Aktif. Git'e bağlı, `main`'e push → otomatik deploy (`netlify.toml`: `python3 tools/gen_pages.py`, publish kök) |
| **Cloudflare Pages** | ❌ **Kullanılmıyor** | Denendi; `*.pages.dev` Türkiye'de ISP SNI filtresiyle erişilemediği için terk edildi. `_headers`/`_redirects` formatı yine de Cloudflare/Netlify uyumludur. |
| **CDN** | Netlify Edge CDN | Otomatik |
| **GitHub Actions** (`.github/workflows/deploy.yml`) | ⚠️ **Legacy/atıl** | Cloudflare Pages'e deploy için yazılmış, artık kullanılmıyor (Netlify Git entegrasyonu devrede). Temizlenebilir. |

### Analytics & İzleme — **ALTYAPI HAZIR, ID'LER BEKLİYOR**
| Araç | Durum | Not |
|---|---|---|
| **GA4** | ⚠️ Placeholder (`G-XXXXXXXXXX`) | `js/analytics.js`'te yükleyici hazır; ID girilince aktif |
| **Microsoft Clarity** | ⚠️ Placeholder (`CLARITY_PROJECT_ID`) | Aynı dosyada guard'lı yükleyici |
| **Sentry** | ⚠️ Kapalı (boş DSN) | Hata izleme; DSN girilince aktif |
| **Google Search Console** | ⚠️ Doğrulama meta'sı placeholder | Alan adı alınınca doğrulanacak |
| **Bing Webmaster** | ⚠️ Doğrulama meta'sı placeholder | Aynı |

`js/analytics.js`: CSP-dostu, self-hosted yükleyici. Her aracın ID'si boş/placeholder ise o araç **yüklenmez** (`isSet()` guard). Dönüşüm event'leri delegasyonla yakalanır (bkz. Bölüm 8).

---

## 3. Site Mimarisi

### Sayfa Listesi (19 sayfa)
| # | Sayfa | URL | Üretim |
|---|---|---|---|
| 1 | Ana Sayfa | `/` | Elle (`index.html`) |
| 2 | Hakkımızda | `/hakkimizda/` | `gen_pages.py` |
| 3 | Tedaviler (genel) | `/tedaviler/` | `gen_pages.py` |
| 4 | İmplant | `/tedaviler/implant/` | `gen_pages.py` |
| 5 | Gülüş Estetiği | `/tedaviler/gulus-estetigi/` | `gen_pages.py` |
| 6 | Ortodonti | `/tedaviler/ortodonti/` | `gen_pages.py` |
| 7 | Kanal Tedavisi | `/tedaviler/kanal-tedavisi/` | `gen_pages.py` |
| 8 | Cerrahi | `/tedaviler/cerrahi/` | `gen_pages.py` |
| 9 | Çocuk Diş Hekimliği | `/tedaviler/cocuk-dis-hekimligi/` | `gen_pages.py` |
| 10 | **Gece Açık Klinik** | `/gece-acik-dis-klinigi-konya/` | `gen_pages.py` |
| 11 | Karatay Şubesi | `/subeler/karatay/` | `gen_pages.py` |
| 12 | Selçuklu Şubesi | `/subeler/selcuklu/` | `gen_pages.py` |
| 13 | Meram Şubesi | `/subeler/meram/` | `gen_pages.py` |
| 14 | Blog (liste) | `/blog/` | `gen_pages.py` |
| 15 | Blog: İmplant Sonrası Bakım | `/blog/implant-sonrasi-bakim/` | `gen_pages.py` |
| 16 | Blog: Çocuk İlk Diş Kontrolü | `/blog/cocuk-ilk-dis-kontrolu/` | `gen_pages.py` |
| 17 | Blog: Gülüş Tasarımı Nedir | `/blog/gulus-tasarimi-nedir/` | `gen_pages.py` |
| 18 | Blog: Gece Diş Ağrısı | `/blog/gece-dis-agrisi-ne-yapmali/` | `gen_pages.py` |
| 19 | İletişim | `/iletisim/` | `gen_pages.py` |
| + | 404 | `/404.html` | `gen_pages.py` |

### Sayfalar Arası Bağlantı Yapısı (Internal Linking)
- **Global nav** (her sayfada): Ana Sayfa, Hakkımızda, Tedaviler, Blog, İletişim + "Bizi Arayın" CTA. ("Gece & Acil" navdan çıkarılmış, içerikten linklenir.)
- **Footer**: Hızlı linkler + 3 şube + iletişim — her sayfada.
- **Hub-and-spoke**: `/tedaviler/` → 6 tedavi alt sayfası; `/blog/` → 4 yazı; ana sayfa → tüm şube/tedavi/gece sayfaları.
- **Bağlamsal linkler**: Blog yazıları ↔ ilgili tedavi sayfaları ↔ gece sayfası ↔ şube sayfaları (örn. gece sayfası → Selçuklu şubesi + gece ağrısı blogu).
- **Breadcrumb**: Tüm alt sayfalarda görünür kırıntı + `BreadcrumbList` şeması.

---

## 4. Site Haritası

```
/                                         (Ana Sayfa)
├── hakkimizda/
├── tedaviler/                            (Hizmetler hub)
│   ├── implant/
│   ├── gulus-estetigi/
│   ├── ortodonti/
│   ├── kanal-tedavisi/
│   ├── cerrahi/
│   └── cocuk-dis-hekimligi/
├── gece-acik-dis-klinigi-konya/          (Gece/Acil — yerel SEO landing)
├── subeler/
│   ├── karatay/
│   ├── selcuklu/                         (gece nöbetçi)
│   └── meram/
├── blog/                                 (Bilgi merkezi hub)
│   ├── implant-sonrasi-bakim/
│   ├── cocuk-ilk-dis-kontrolu/
│   ├── gulus-tasarimi-nedir/
│   └── gece-dis-agrisi-ne-yapmali/
├── iletisim/
├── 404.html
├── sitemap.xml
└── robots.txt
```

> Not: `/subeler/` ve `/blog/`... URL'leri "pretty" (trailing-slash) dizin yapısındadır — her rota fiziksel `<rota>/index.html` dosyasıdır.

---

## 5. SEO Raporu

### URL Mimarisi
- Temiz, anahtar-kelime içeren, trailing-slash dizin URL'leri (`/tedaviler/implant/`).
- Yerel niyet URL'i: `/gece-acik-dis-klinigi-konya/` (yüksek değerli yerel arama).
- Tek kanonik host: `https://dentualkonya.com` (`<link rel=canonical>` + `_redirects` ile www→apex 301).

### Meta Yapıları
- Her sayfada benzersiz `title` + `description` (`gen_pages.py`'de `PAGE_DESCS`).
- Tam **Open Graph** + **Twitter Card** seti, `og:image` = hero1.
- `theme-color`, `author`, `robots: index, follow`, `keywords`.
- TR/EN için i18n; sayfa başlık/açıklamaları dile göre değişir (`applyLangChrome`).

### Başlık (Heading) Yapısı
- Sayfa başına tek `<h1>` (ana sayfada "Konya Diş Kliniği" + animasyonlu tagline).
- Bölüm başlıkları `<h2>`, alt kırılımlar `<h3>` — semantik hiyerarşi korunur.

### Internal Linking
- Hub-and-spoke + bağlamsal çapraz linkleme (bkz. Bölüm 3). Breadcrumb her alt sayfada.

### Schema Kullanımı (JSON-LD)
- **Kurumsal:** `MedicalClinic` + `Dentist` (her şube için), `OpeningHoursSpecification` (09:00–23:00), `PostalAddress`, `GeoCoordinates`, `AggregateRating` (4.9 / 366).
- **Sayfa tipleri:** `WebSite, WebPage, AboutPage, ContactPage, CollectionPage`.
- **İçerik:** `MedicalProcedure` (tedaviler), `BlogPosting` (yazılar), `FAQPage` (SSS), `BreadcrumbList`.
- **Yerel:** `City`/`AdministrativeArea` (Konya + ilçeler).

### Local SEO
- İlçe bazlı landing'ler (Selçuklu vurgusu), şube sayfalarında NAP (isim-adres-telefon) tutarlılığı, harita embed, `geo`/`areaServed`.
- "Gece açık / nöbetçi diş hekimi" farklılaştırıcısı site genelinde tutarlı (23:00).

### FAQ Yapıları
- Ana sayfa + gece sayfası + tedavi sayfalarında görünür SSS akordeonları, her biri `FAQPage` şemasıyla (toplam 21 Q&A).

### Şube SEO
- 3 ayrı şube sayfası, her biri kendi `Dentist` şeması, adresi, haritası, telefon/WhatsApp'ı.

### Blog SEO
- 4 yazı, her biri `BlogPosting` şeması, breadcrumb, ilgili tedavi/şubeye çapraz link, CTA.

### Durum Sınıflandırması
**✅ Tamamlananlar**
- Tüm sayfalarda benzersiz meta + OG/Twitter
- Kapsamlı JSON-LD şema
- Sitemap + robots
- Internal linking + breadcrumb
- Yerel SEO landing + şube NAP tutarlılığı
- FAQ şemaları, blog şemaları

**⚠️ Eksik kalanlar**
- **Alan adı `dentualkonya.com` alınmadı** → kanonik/OG/sitemap'teki tüm URL'ler henüz canlı host (`netlify.app`) ile uyuşmuyor. **En kritik SEO açığı.**
- Google Search Console / Bing doğrulaması yapılmadı (placeholder meta).
- Google Business Profile entegrasyonu/iyileştirmesi (doküman var: `SEO-LOCAL-GBP.md`).
- Gerçek `hreflang` `<link>` çiftleri (i18n istemci tarafı; sunucu seviyesinde hreflang yok).

**🔮 Gelecekte yapılabilecekler**
- Blog içerik takvimi (`SEO-BLOG-TAKVIMI.md`) uygulanarak içerik genişletme
- Daha fazla ilçe/semt landing'i
- Görsel `ImageObject` şeması, hekim `Person` şeması (altyapı hazır)
- İç arama, breadcrumb zenginleştirme

> İlgili dokümanlar: `docs/SEO-TEKNIK-KONTROL.md`, `docs/SEO-LOCAL-GBP.md`, `docs/SEO-BLOG-TAKVIMI.md`.

---

## 6. Lighthouse ve Performans Çalışmaları

### Yapılan Optimizasyonlar ve Gerekçeleri

| Optimizasyon | Dosya(lar) | Neden | Beklenen Etki |
|---|---|---|---|
| **Preloader'ı `DOMContentLoaded`'da gizle** | `js/script.js` (`initPreloader`) | Eski kod `window.load`'da gizliyordu → mobil LCP'yi ~9s'ye çıkarıyordu (anti-pattern) | **LCP ~9.0s → ~2.3s** |
| **Tüm fotoğraflar WebP** | `assets/**`, `tools/convert_webp.py` | 6.2MB JPG yükü | **−89% (6.2MB → ~709KB)** |
| **Hero AVIF + image-set** | `index.html`, `css/style.css` | AVIF, WebP'den de küçük; iki-katman fallback | Hero bayt ↓, LCP ↓ |
| **İlk hero preload + fetchpriority** | `index.html` `<head>` | LCP görseli erken boyansın | LCP ↓ |
| **Hero slide 2-7 lazy (`data-bg` + `requestIdleCallback`)** | `js/script.js` (`initHeroSlider`) | İlk boyamada yalnız 1 görsel insin | LCP yarışı yok, TBT ↓ |
| **Typewriter satırı sabit yükseklik** | `css/style.css` (`.hero-tw`) | Animasyon/font swap sırasında başlık kaymasın | **CLS = 0** |
| **Tüm medyada `aspect-ratio`** | `css/style.css` (hero, çocuk video, kartlar) | Yükleme öncesi yer rezerve | **CLS = 0** |
| **Video `preload="none"` + poster** | `index.html`, `css`, `js` | Oynatılana kadar 3.6MB inmesin | İlk yük etkisi ~0, TBT/ağ ↓ |
| **Font `display=swap` + `preconnect` + ağırlık kırpma** | `index.html` | FOIT önle, bağlantı erken aç | FCP ↓, CLS ↓ |
| **Asset'lerde immutable 1 yıl önbellek** | `_headers` | Tekrar ziyaret hızlı | Tekrar yük ↓ |
| **Lighthouse bütçesi** | `lighthouse-budget.json` | Regresyon koruması (CI) | Performans sabitliği |

### Çekirdek Web Vitalleri (Core Web Vitals)
- **LCP:** Preloader düzeltmesi + WebP/AVIF + preload ile mobilde ~9s → ~2.3s seviyesine çekildi.
- **CLS:** Hero başlık satırı rezervasyonu + tüm `aspect-ratio` konteynerleri ile ölçümlenen kayma **0** (eval ile doğrulandı).
- **TBT:** Tek IIFE, framework yok, lazy medya → düşük ana-iş-parçacığı bloklaması.
- **FCP:** Erken preconnect + swap font + hafif kritik yol.
- **Speed Index:** Lazy slide/video + sıkıştırılmış görseller ile iyileştirildi.

> Not: Sayısal Lighthouse skorları, **alan adı alınıp prod CDN'de** ölçülünce kesinleşir. Şu an `netlify.app` üzerinde test edilebilir.

---

## 7. Tasarım Sistemi

Tamamı `css/style.css` `:root` değişkenleriyle tanımlı (tek kaynak).

### Renk Paleti
| Token | Değer | Kullanım |
|---|---|---|
| `--green-900 … 600` | `#06302e → #11665f` | Marka koyu yeşil tonları |
| `--teal-500 / 400 / 300` | `#14b8a6 / #2dd4bf / #5eead4` | Vurgu / aksiyon / açık vurgu |
| `--mint-100` | `#e6fbf6` | Yumuşak zemin |
| `--bg / --bg-alt / --surface` | `#f4f9f8 / #fff / #fff` | Zemin yüzeyleri |
| `--text / --text-soft / --text-muted` | `#0f2826 / #4a615f / #7c918f` | Metin hiyerarşisi |
| `--grad-brand` | yeşil→teal 135° | Marka gradyanı |

Ayrıca **koyu tema** (`html[data-theme="dark"]`) tüm token'ları yeniden tanımlar.

### Yazı Tipleri
- **Başlık:** `Plus Jakarta Sans` (`--font-head`)
- **Gövde:** `Poppins` (`--font-body`)
- Ağırlıklar: 400–800 (kırpılmış set), `display=swap`.

### Buton Yapıları
- `.btn` temel + varyantlar: `.btn-primary`, `.btn-ghost`, `.btn-lg`, `.btn-block`, `.btn-emergency` (beyaz/yeşil), `.btn-wa` (WhatsApp yeşili `#25d366`).
- Şube CTA grupları: `.emergency-branch-btn` + `.ebb-group` (şube adı → telefon → WhatsApp dikey).

### Kart Yapıları
- `.review-card` (yorum + avatar + yıldız + Google rozeti), `.doctor-card` (foto + gövde, baş-harf fallback'li), `.treatment` kartları, `.cocuk-logo-card`, glassmorphism token'ları (`--glass-*`).

### Grid Sistemi
- `--maxw: 1200px` konteyner; CSS Grid tabanlı bölümler (`.cocuk-inner`, `.contact-wrap` = 2 sütun; `.cocuk-features` = 2 sütun).
- Yarıçap ölçeği: `--radius-sm/​-/-lg/-pill`; gölge ölçeği: `--shadow-sm/md/lg/glow`.

### Responsive Strateji
- Akışkan tipografi: `clamp()` (başlık, bölüm boşluğu `--space-section`).
- Kırılma noktaları: nav ~1024px; ana grid'ler ≤900px'te tek sütuna iner (`.contact-wrap, .cocuk-inner` → 1fr).
- Mobil-öncelikli aksiyonlar: şube CTA'ları mobilde dikey tam genişlik.
- Erişilebilirlik: skip-link, `:focus-visible`, `aria-live`, ARIA etiketleri.

---

## 8. Dönüşüm ve Pazarlama Altyapısı

### Telefon CTA'ları
- Header "Bizi Arayın", acil bant şube telefonları, footer, iletişim sayfası, şube sayfaları.
- `tel:` linkleri; numaralar `white-space:nowrap` ile tek satır (iletişim sayfası düzeltmesi).
- İzleme: `phone_call_click` (şube etiketli).

### WhatsApp CTA'ları
- Sağ-alt yüzen WhatsApp butonu (şube seçici), ana sayfa acil bandı (3 şube), gece sayfası (3 şube), şube sayfaları, form sonrası yönlendirme.
- Her buton **kendi şubesinin** numarasına; ön-doldurulmuş mesaj.
- İzleme: `whatsapp_click` (şube etiketli, `branchOf()`).

### Şube Bazlı Yönlendirmeler
- Acil bant ve gece sayfasında **şube grupları**: Şube Adı → Telefon → WhatsApp (yan yana 3 sütun masaüstü, dikey mobil).

### Dönüşüm Noktaları (event haritası)
| Event | Tetikleyici |
|---|---|
| `phone_call_click` | herhangi `tel:` tıklaması |
| `whatsapp_click` | herhangi `wa.me` tıklaması |
| `lead_form_submit` | iletişim formu gönderimi |
| `map_open` | harita/yol tarifi açılışı |

Tümü `js/analytics.js`'te **delegasyonla** yakalanır (tek listener, GA4 + Clarity'ye iletir).

### Kullanıcı Yolculuğu (giriş → WhatsApp)
```
Google araması ("konya gece açık diş")
   → Landing (ana sayfa veya /gece-acik-dis-klinigi-konya/)
   → Acil bant görülür ("23:00'a kadar açık")
   → Kullanıcı şubesini seçer (Karatay/Selçuklu/Meram)
   → "WhatsApp" butonu (o şubenin numarası, hazır mesaj)
   → wa.me → WhatsApp görüşmesi başlar
   → (paralel) whatsapp_click event'i GA4'e şube etiketiyle düşer
```
Alternatif: Form doldur → gönder → WhatsApp'a yönlendirilir (form da WhatsApp'a akar).

---

## 9. Güvenlik ve Altyapı

| Katman | Durum | Detay |
|---|---|---|
| **SSL/TLS** | ✅ | Netlify otomatik HTTPS; HTTP→HTTPS yönlendirme |
| **HSTS** | ✅ | `max-age=63072000; includeSubDomains; preload` |
| **CSP** | ✅ | Sıkı `default-src 'self'`; gtag/clarity/sentry domain'leri allow-list; inline script için `sha256` hash; `upgrade-insecure-requests` |
| **X-Content-Type-Options** | ✅ | `nosniff` |
| **X-Frame-Options** | ✅ | `SAMEORIGIN` (clickjacking) |
| **Referrer-Policy** | ✅ | `strict-origin-when-cross-origin` |
| **Permissions-Policy** | ✅ | geolocation/camera/microphone/payment/usb = kapalı |
| **COOP** | ✅ | `Cross-Origin-Opener-Policy: same-origin` |
| **www→apex 301** | ✅ | `_redirects` |
| **Form güvenliği** | ⚠️ Kısmi | Form WhatsApp'a yönlenir (sunucu yok); `required` doğrulama var, **CAPTCHA/honeypot yok** |
| **Spam koruması** | ⚠️ Eksik | Backend olmadığından sunucu-taraflı spam filtresi yok |
| **Gizli anahtar** | ✅ Temiz | Repoda API anahtarı/şifre yok; `.env` gitignore'da, yalnız `.env.example` |
| **KVKK / Çerez onayı** | ⚠️ Eksik | GA4 & Clarity çerez kurar; **Consent Mode v2 / çerez banner'ı yok** (prod öncesi gerekli) |

> Güvenlik başlıkları CDN kenarında (`_headers`) uygulanır — uygulama/sunucu kodu yok. CSP, `js/analytics.js`'in self-hosted olmasını gerektirir (inline snippet yok).

---

## 10. Dosya ve Klasör Yapısı

```
dentual-website/
├── index.html                      # Ana sayfa (elle bakım) + chrome kaynağı
├── 404.html                        # (üretilir)
├── sitemap.xml                     # (üretilir)
├── robots.txt
├── netlify.toml                    # Build: python3 gen_pages.py, publish: kök
├── _headers                        # Güvenlik başlıkları + CSP + önbellek (CDN)
├── _redirects                      # www→apex 301
├── .gitignore  /  .env.example
│
├── css/
│   └── style.css                   # ~935 satır — tüm tasarım sistemi (el yazımı)
│
├── js/
│   ├── script.js                   # ~1220 satır — tek IIFE (UI, i18n, slider, vs.)
│   └── analytics.js                # ~104 satır — GA4/Clarity/Sentry + dönüşüm izleme
│
├── tools/
│   ├── gen_pages.py                # ~770 satır — statik sayfa üreteci (stdlib)
│   └── convert_webp.py             # görsel optimizasyon yardımcı betiği
│
├── assets/
│   ├── hero/                       # hero1-7 {webp,avif} + hero1.jpg (OG) + about*
│   ├── doctors/                    # 10 hekim {webp,png}
│   ├── treatments/                 # 6 tedavi {webp,jpg}
│   ├── video/                      # cocuk.mp4 + cocuk-poster.webp
│   ├── logo*.png  /  favicon*.png  /  apple-touch-icon.png
│
├── hakkimizda/index.html           # (üretilir)
├── iletisim/index.html             # (üretilir)
├── gece-acik-dis-klinigi-konya/index.html
├── tedaviler/
│   ├── index.html
│   ├── implant/  gulus-estetigi/  ortodonti/
│   ├── kanal-tedavisi/  cerrahi/  cocuk-dis-hekimligi/
├── subeler/
│   ├── karatay/  selcuklu/  meram/   (her biri index.html)
├── blog/
│   ├── index.html
│   ├── implant-sonrasi-bakim/  cocuk-ilk-dis-kontrolu/
│   ├── gulus-tasarimi-nedir/  gece-dis-agrisi-ne-yapmali/
│
├── .github/workflows/deploy.yml    # ⚠️ Legacy (Cloudflare) — atıl
├── lighthouse-budget.json          # CI performans bütçesi
├── .claude/launch.json             # Yerel önizleme sunucusu (python http.server)
│
└── docs/
    ├── PROJE-TEKNIK-DOKUMANTASYON.md   # (bu dosya)
    ├── MIMARI-VE-YOL-HARITASI.md
    ├── SEO-TEKNIK-KONTROL.md
    ├── SEO-LOCAL-GBP.md
    ├── SEO-BLOG-TAKVIMI.md
    └── URETIM-KURULUM.md
```

> **Üretilen vs. elle bakılan:** `index.html`, `css/`, `js/`, `tools/`, `assets/` elle bakılır. Tüm alt-sayfa `index.html`'leri + `sitemap.xml` + `404.html` `gen_pages.py` tarafından üretilir → **doğrudan elle düzenlenmemeli**, kaynak `gen_pages.py`'dir.

---

## 11. Eksik ve Geliştirilebilir Alanlar

### 🔴 Kritik
1. **Alan adı alınmamış (`dentualkonya.com`).** Tüm kanonik/OG/sitemap URL'leri bu alana işaret ediyor ama site `netlify.app`'te. SEO indekslemesi ve sosyal paylaşımlar bu yüzden tutarsız. → Alan adını al, Netlify'a bağla.
2. **Search Console / Bing doğrulaması yok.** İndeksleme takip edilemiyor, sitemap gönderilemiyor.
3. **KVKK çerez onayı yok.** GA4/Clarity çerezleri için Consent Mode v2 / banner prod trafiği öncesi yasal gereklilik.

### 🟠 Yüksek Öncelik
4. **Analytics ID'leri placeholder.** GA4/Clarity/Sentry değerleri girilmeli (`js/analytics.js`) — şu an hiçbir veri toplanmıyor.
5. **Form spam koruması yok.** Honeypot alanı veya basit oran sınırı eklenmeli (backend olmadığından istemci-taraflı + WhatsApp akışı).
6. **Legacy CI temizliği.** `.github/workflows/deploy.yml` Cloudflare'e deploy ediyor (atıl); Netlify ile çakışmaması için kaldırılmalı/güncellenmeli.
7. **CSS/JS fingerprint'lenmiyor.** `_headers`'taki `TODO` — `style.[hash].css` ile cache-busting; aksi halde her güncellemede kullanıcılar 1 saate kadar eski dosya görebilir (geliştirme sırasında defalarca yaşandı).

### 🟡 Orta Öncelik
8. **Hekim verisi boş altyapı.** `renderDoctors` foto+bio+sosyal alanlarını destekliyor ama içerik (bio/sosyal) doldurulmadı; `Person` şeması eklenebilir.
9. **Gerçek `hreflang` linkleri.** i18n istemci tarafı; sunucu seviyesinde `hreflang` `<link>` çiftleri yok.
10. **Görsel/SEO zenginleştirme.** `ImageObject` şeması, blog yazarı, daha fazla iç link.
11. **Erişilebilirlik denetimi.** Temel ARIA var; tam WCAG kontrastı/klavye turu denetimi yapılmadı.

### 🟢 Düşük Öncelik
12. **Blog içerik genişlemesi** (`SEO-BLOG-TAKVIMI.md` takvimi).
13. **Görsel `srcset` (boyut bazlı responsive)** — şu an format bazlı (`image-set`) var, genişlik bazlı `srcset` yok.
14. **Video çoklu kaynak** (WebM/VP9) — şu an yalnız MP4 (evrensel, yeterli).
15. **PWA / manifest** — `theme-color` var, tam manifest/service worker yok.
16. **Mikro-etkileşim/animasyon cilası**, ek ilçe landing'leri.

---

## Hızlı Başlangıç (Devralan Geliştirici İçin)

```bash
# 1. Klonla
git clone https://github.com/buqr4/dentual-website.git && cd dentual-website

# 2. Yerel önizleme (Python 3 yeterli, bağımlılık yok)
python -m http.server 5500        # → http://localhost:5500

# 3. Alt sayfaları yeniden üret (index.html chrome'unu değiştirdiysen)
python tools/gen_pages.py         # 18 sayfa + sitemap + 404

# 4. Yayınla — main'e push yeter (Netlify otomatik build alır)
git add -A && git commit -m "..." && git push origin main
```

**Altın kurallar:**
- Alt-sayfa `index.html`'lerini **elle düzenleme** → `tools/gen_pages.py`'yi düzenle, yeniden üret.
- Ana sayfa (`/index.html`) **elle** bakılır ve `gen_pages.py` için "chrome" kaynağıdır.
- Şube verisi tek yerde: `gen_pages.py` `BRANCHES`.
- Görsel eklerken WebP/AVIF üret (`tools/convert_webp.py` veya Pillow).
- Çalışma saati site genelinde **23:00**; değişirse metin + şema + meta + FAQ hepsinde güncelle.
