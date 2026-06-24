# Teknik SEO Kontrol Listesi — Durum — Dentual Konya

Durum: ✅ tamam · 🟡 kısmen / izlenmeli · ⬜ saha-dışı (sizin yapmanız gereken)

## URL & İndeksleme
- ✅ Gerçek, taranabilir URL mimarisi (19 ayrı sayfa; SPA `#` linkleri kaldırıldı)
- ✅ Pretty URL'ler (trailing-slash klasör yapısı: `/tedaviler/implant/`)
- ✅ Her sayfada self-canonical (mutlak https)
- ✅ Kök-göreli varlık yolları (`/assets`, `/css`, `/js`) — tüm alt klasörlerde çalışır
- ✅ robots.txt doğru (`Allow: /` + sitemap satırı), CSS/JS engellenmiyor
- ✅ sitemap.xml 19 URL (üretici otomatik günceller)
- ✅ 404.html (noindex) oluşturuldu
- ⬜ Google Search Console + Bing Webmaster'a sitemap gönderin
- ⬜ www / non-www tek sürüm + HTTPS 301 (sunucu/host ayarı)

## On-Page
- ✅ Her sayfada tek, anahtar-kelimeli H1 (ana sayfada statik "Konya Diş Kliniği" + daktilo)
- ✅ Sayfa bazlı SEO title (≤60) ve meta description (≤155)
- ✅ Mantıklı H2/H3 hiyerarşisi
- ✅ Açıklayıcı, anahtar kelimeli görsel `alt` metinleri
- ✅ Görünür breadcrumb + BreadcrumbList schema (tüm alt sayfalar)
- ✅ Doğal iç linkleme (tedavi↔şube↔gece-acil↔blog), açıklayıcı anchor metni
- ✅ Dil değişiminde title/description senkronu (`<body data-title/desc-*>`)

## Yapısal Veri (Schema.org)
- ✅ WebSite + Organization/MedicalOrganization (ana sayfa)
- ✅ 3× Dentist düğümü (adres, saat, `medicalSpecialty`, `areaServed`, şube URL'leri)
- ✅ FAQPage (ana sayfa — görünür 8 SSS ile birebir eşleşir)
- ✅ MedicalProcedure (tedavi detayları), MedicalClinic (gece-acil), Dentist+FAQPage (şubeler)
- ✅ BlogPosting (blog yazıları), ContactPage, AboutPage, CollectionPage, Blog
- 🟡 Karatay & Selçuklu için **gerçek `geo` koordinatları** eklenmeli (uydurulmadı; Meram gerçek)
- 🟡 aggregateRating sadece Meram'da (genel Google puanı) — şube bazlı puanlar ayrışınca güncellenir

## Core Web Vitals / Performans
- ✅ İlk hero görseli `preload` + `fetchpriority="high"` (LCP)
- ✅ Google Fonts `preconnect` + `display=swap`
- ✅ Görsellerde `loading="lazy"` ve `width`/`height` (CLS)
- ✅ Google Maps "facade" ile tıklayınca yükleniyor (3rd-party gecikmesi yok)
- ✅ JS tek dosya, `</body>` sonunda; scroll dinleyiciler `passive`
- 🟡 Görselleri **WebP/AVIF**'e çevirin + `<picture>`/`srcset` (asıl dosyalar gerekli)
- 🟡 Preloader 800ms+2500ms — LCP'yi bir miktar geciktirebilir, gözden geçirin
- ⬜ Sunucu: HTTP/2, Brotli/Gzip, uzun cache-control header

## Çok Dillilik (TR/EN)
- ✅ Chrome (nav/footer/SSS/duyuru) TR/EN dil değişimi çalışıyor
- 🟡 Alt sayfa **gövde içerikleri TR** (EN gövde çevirisi ikinci dalga); EN URL olmadığı için
  hreflang eklenmedi — EN sayfalar üretilirse hreflang + x-default eklenmeli

## Doğrulama (bu oturumda yapıldı)
- ✅ Tüm örnek sayfalarda tek H1, doğru title/canonical/schema (DOMParser ile kontrol edildi)
- ✅ Navbar 1280px yatay tek satır, ≤1024px hamburger — sarma yok
- ✅ Statik SSS aç/kapa, iletişim formu, harita facade çalışıyor; konsol hatası yok
