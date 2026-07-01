# Konya Diş Hekimi — CLAUDE.md

Her yeni oturumda bu dosya otomatik yüklenir. Projeyi yeniden analiz ettirme.

---

## Proje Kimliği

| Alan | Değer |
|------|-------|
| Site adı | **Konya Diş Hekimi** (kısaca **KDH**) |
| Domain | `konyadishekimi.com` |
| Eski marka | `Dentual Konya` / `dentualkonya.com` (tümüyle kaldırıldı) |
| İnstagram | `@konyadishekimi` |
| Klinik e-posta | `info@konyadishekimi.com` |
| Telefon | `+90-444-34-42` |
| Şubeler | Meram · Selçuklu · Karatay |

---

## Teknoloji Stack

- **Tamamen statik** — framework yok, build tool yok
- Vanilla HTML / CSS / JS
- **`tools/gen_pages.py`** — tüm alt sayfaları + 404 + sitemap üreten Python generator
- Netlify üzerinden deploy (Git push → otomatik `python3 tools/gen_pages.py` → yayın)
- CI: `.github/workflows/ci.yml` — generator çalıştırır, uncommitted diff varsa fail verir

---

## KRITIK KURALLAR

```
1. Oluşturulan /<route>/index.html dosyalarını EL İLE DÜZENLEME.
   Generator her çalıştığında üzerine yazar. Değişiklik yapmak istiyorsan
   tools/gen_pages.py içinde ilgili içeriği düzenle.

2. gen_pages.py veya index.html'nin chrome bölümlerini değiştirince
   MUTLAKA python tools/gen_pages.py çalıştır.

3. Generator çalıştıktan sonra CI'nın geçmesi için tüm üretilen dosyaları
   commit etmek zorundasın.
```

---

## Dosya Mimarisi

```
Dentual/
├── index.html              ← Ana sayfa (ELLE düzenlenir, generator DOKUNMAZ)
├── tools/gen_pages.py      ← Master generator (tüm alt sayfaları üretir)
├── css/
│   ├── style.css           ← Base stil (her şey burada)
│   ├── theme-navy.css      ← AKTİF tema (html[data-skin="navy"])
│   └── theme-premium.css   ← Pasif tema (bağlı değil, kolay devreye alınabilir)
├── js/
│   ├── script.js           ← Ana JS (i18n, tema, WhatsApp, form, analytics bridge)
│   └── analytics.js        ← GA4 / Clarity / Sentry + kdTrack / kdConsent
├── assets/                 ← Görseller (webp/jpg/png) — generator dokunmaz
├── _headers                ← Netlify/CDN güvenlik + cache header'ları
├── _redirects              ← www→apex canonical yönlendirme
├── robots.txt
├── sitemap.xml             ← generator tarafından üretilir
├── netlify.toml
├── .gitattributes          ← LF zorunluluğu (CRLF/LF CI uyumsuzluğunu önler)
└── .github/workflows/ci.yml
```

### Generator'ın ürettiği sayfalar (elle düzenleme)
```
hakkimizda/           gece-acik-dis-klinigi-konya/   iletisim/
tedaviler/            tedaviler/implant/              tedaviler/gulus-estetigi/
tedaviler/ortodonti/  tedaviler/kanal-tedavisi/       tedaviler/cerrahi/
tedaviler/cocuk-dis-hekimligi/
subeler/karatay/      subeler/selcuklu/               subeler/meram/
blog/                 blog/<30 makale>/
404.html              sitemap.xml
```

---

## Generator: gen_pages.py

### Nasıl çalışır

1. `index.html`'den `CHROME_TOP` ve `CHROME_BOTTOM` kesip alır  
   (duyuru çubuğu→navbar → `<!-- CHROME_TOP -->` başlangıcından `<main>` başına kadar;  
   `</main>`'den dosya sonuna kadar footer+widget+script)
2. Her route için `HEAD_TMPL` ile sayfayı oluşturur
3. Asset fingerprint'i (`?v=<sha1[:8]>`) CSS/JS dosyalarının **LF normalize edilmiş** hash'inden hesaplar
4. Tüm `open(..., "w")` çağrıları `newline="\n"` ile LF yazar (CI uyumluluğu)

### Temel sabitler

```python
ORIGIN = "https://konyadishekimi.com"    # tüm canonical/OG/schema URL'leri
ASSET_VER = _asset_ver(...)              # ?v= fingerprint (otomatik)
```

### Çalıştırma

```bash
python tools/gen_pages.py
```

---

## Marka & Teknik Değişkenler

### localStorage / sessionStorage anahtarları
```
konyadishekimi-lang          # dil tercihi (tr/en)
konyadishekimi-theme         # tema (light/dark)
konyadishekimi-ann-closed    # duyuru çubuğu kapatıldı mı
konyadishekimi-consent       # KVKK cookie onayı
konyadishekimi-last-submit   # form spam koruması (timestamp)
konyadishekimi-last-sig      # form spam koruması (imza, sessionStorage)
```

### JS Window Globals
```javascript
window.kdTrack(event, data)  // form dönüşüm takibi (analytics.js'de tanımlı)
window.kdConsent             // KVKK consent API {get, set, reset}
```

### Tema Sistemi
- `html[data-skin="navy"]` → theme-navy.css aktif (şu anki)
- `html[data-skin="premium"]` → theme-premium.css (Petrol & Altın, bağlı değil)
- Geçiş: `<html>` tag'ine `data-skin` ekle + `<link>` tag'i bağla + generator'ı yeniden çalıştır

### i18n
- `data-i18n`, `data-i18n-html`, `data-i18n-ph` attribute'ları
- TR: DOM'dan alınır (varsayılan)
- EN: `js/script.js` içindeki `DICT.en` sözlüğünden

---

## SEO Hedef Keyword'leri

| Keyword | Öncelik |
|---------|---------|
| Konya Diş Hekimi | ⭐⭐⭐ Birincil |
| Konya Diş Kliniği | ⭐⭐⭐ Birincil |
| Konya İmplant | ⭐⭐ İkincil |
| Konya Ortodonti | ⭐⭐ İkincil |
| Konya Gülüş Tasarımı / Hollywood Smile | ⭐⭐ İkincil |
| Nöbetçi / Gece Açık Diş Hekimi Konya | ⭐⭐ İkincil |
| Karatay / Selçuklu / Meram Diş Hekimi | ⭐ Uzun kuyruk |

---

## Structured Data (JSON-LD)

`index.html` içinde `@graph` ile:
- `WebSite` — `konyadishekimi.com/#website`
- `Organization + MedicalOrganization` — `/#organization`  
  `sameAs: ["https://www.instagram.com/konyadishekimi/"]`
- `Dentist` × 3 — `/#meram`, `/#selcuklu`, `/#karatay`

Alt sayfalarda (gen_pages.py üretir):
- `BreadcrumbList` — her sayfada
- `FAQPage` — `iletisim/`, `gece-acik-dis-klinigi-konya/`
- `MedicalWebPage` — tedavi sayfaları
- `BlogPosting` — blog makaleleri

---

## CI / Deploy

```
Git push → GitHub Actions (ci.yml) → python tools/gen_pages.py
                                    → git diff --quiet  ← burası fail olursa
                                                           üretilen dosyaları
                                                           commit etmemişsindir
→ Netlify build → yayın
```

**CI geçmesi için:** Her gen_pages.py çalıştırmasından sonra üretilen tüm dosyaları commit et.

```bash
python tools/gen_pages.py
git add 404.html sitemap.xml index.html tedaviler/ hakkimizda/ blog/ \
        iletisim/ gece-acik-dis-klinigi-konya/ subeler/
git commit -m "chore: regenerate pages"
git push origin main
```

---

## Güvenlik / Header'lar (_headers)

- HSTS, X-Frame-Options, CSP, Permissions-Policy — `_headers` dosyasında
- CSP'de `sha256-...` hash'i: `index.html` içindeki inline `ann-dismissed` script'i için
- Görseller: `/assets/*` → `max-age=31536000, immutable`
- CSS/JS: `max-age=3600` (fingerprint ile cache-bust edilir)
- HTML: `max-age=0, must-revalidate`

---

## Sık Yapılan Görevler

### Yeni blog makalesi ekle
→ `tools/gen_pages.py` içinde `blog_post(...)` fonksiyonunu kullanarak ekle  
→ `python tools/gen_pages.py` çalıştır → commit → push

### Hizmet sayfası güncelle
→ `tools/gen_pages.py` içinde ilgili `page(...)` veya `ROUTES["/tedaviler/..."]` bloğunu düzenle  
→ `python tools/gen_pages.py` çalıştır → commit → push

### Ana sayfa güncelle
→ `index.html` elle düzenlenir (generator dokunmaz)  
→ Chrome (navbar/footer) değişirse `python tools/gen_pages.py` çalıştır

### Yeni şube ekle
→ `tools/gen_pages.py` içinde şube verilerini güncelle  
→ `index.html` içinde JSON-LD Dentist bloğu ekle  
→ Generator çalıştır → commit → push

### Tema değiştir (navy → premium)
1. `index.html` ve `gen_pages.py HEAD_TMPL` içinde `data-skin="navy"` → `"premium"` yap  
2. `<link rel="stylesheet" href="/css/theme-premium.css" />` bağla  
3. `python tools/gen_pages.py` çalıştır → commit → push

---

## Kalan Notlar

- `assets/hero/about-dentual.webp` ve `about-dentual.jpg` — dosya adında "dentual" var.  
  Kullanıcıya görünmez, SEO'ya etkisi yok. Yeniden adlandırmak istersen: dosyaları rename et,  
  `gen_pages.py` ve `index.html`'deki referansları güncelle.
- `scratchpad/rebrand.py` — bir defaya mahsus rebrand scripti, artık işlevi kalmadı.
