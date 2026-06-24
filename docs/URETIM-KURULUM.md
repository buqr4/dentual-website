# Üretim Kurulum & Operasyon Rehberi — Dentual Konya

Bu rehber, siteyi canlıya almak ve dönüşüm takibini aktifleştirmek için yapılması gereken
**elle adımları** listeler. Kod tarafı (header'lar, CSP, analytics iskeleti, CI/CD) hazır.

---

## 1) Hosting — Cloudflare Pages (önerilen)
İki yol var, **A daha basit**:

**A) Cloudflare Pages — Git entegrasyonu (build aracı yok)**
1. Cloudflare → Workers & Pages → Create → Pages → Connect to Git → repoyu seç.
2. **Build command:** `python tools/gen_pages.py` · **Build output directory:** `/` (kök).
3. Deploy. Her `git push` otomatik yayınlanır. `_headers` ve `_redirects` otomatik uygulanır.

**B) GitHub Actions** (zaten `.github/workflows/deploy.yml` hazır)
- Repo → Settings → Secrets → `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` ekleyin.
- `deploy.yml` içindeki `PROJECT_NAME`'i Pages proje adınızla değiştirin.

**Custom domain:** Pages → Custom domains → `dentualkonya.com` + `www` ekleyin (www → apex
yönlendirmesi `_redirects` ile zaten tanımlı). SSL otomatik. Brotli/Gzip otomatik.

> `_headers` dosyası HSTS, CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy,
> X-Frame-Options ve cache kurallarını edge'de uygular. Canlıda
> https://securityheaders.com ve https://csp-evaluator.withgoogle.com ile doğrulayın.

---

## 2) Analitik & Dönüşüm — ID'leri girin
`js/analytics.js` → `CONFIG` bloğu:
```js
GA4_ID:     'G-XXXXXXXXXX',        // GA4 → Yönetici → Veri Akışları → Ölçüm Kimliği
CLARITY_ID: 'CLARITY_PROJECT_ID',  // clarity.microsoft.com → proje → Settings → Project ID
SENTRY_DSN: '',                    // sentry.io → proje → Client Keys (DSN); boş = kapalı
SENTRY_LOADER: 'https://js.sentry-cdn.com/PUBLIC_KEY.min.js'  // Sentry → Loader Script
```
**Otomatik ölçülen dönüşüm event'leri** (kod hazır):
- `whatsapp_click` (şube etiketli) · `phone_call_click` (şube etiketli) · `map_open` · `lead_form_submit`

GA4'te bu event'leri **"Anahtar Etkinlik" (conversion)** olarak işaretleyin
(Yönetici → Etkinlikler). Google Ads'e bağlanacaksa oradan da import edin.

---

## 3) Google Search Console + Bing doğrulama
**Tercih: DNS TXT** (tüm site + alt alan adları için geçerli, kod gerekmez):
- GSC → Mülk ekle → Domain → verilen TXT kaydını DNS'e ekleyin.
- Bing Webmaster → "GSC'den içe aktar" (en hızlısı) veya DNS TXT.

**Alternatif: meta etiket** — `index.html` ve `tools/gen_pages.py` (HEAD_TMPL) içindeki yorum
satırlarını açıp token'ı yapıştırın, `python tools/gen_pages.py` çalıştırıp yeniden deploy edin.

Doğrulamadan sonra: GSC'ye **`https://dentualkonya.com/sitemap.xml`** gönderin.

---

## 4) Uptime izleme (UptimeRobot — ücretsiz)
- uptimerobot.com → Add Monitor → HTTP(s) → `https://dentualkonya.com/` → 5 dk aralık.
- İkinci monitör: `https://dentualkonya.com/gece-acik-dis-klinigi-konya/` (kritik dönüşüm sayfası).
- Keyword monitor: sayfada "Dentual" geçmesini kontrol et (boş/hatalı deploy yakalar).
- Alarm: e-posta + (opsiyonel) SMS. SSL bitiş uyarısını aç.

---

## 5) KVKK / Çerez Onayı (production öncesi öneri)
GA4 ve Clarity çerez kullanır. Yoğun trafik öncesi bir **çerez onay çözümü** ekleyin
(Cookiebot / Osano / basit Consent Mode v2 banner'ı) ve `analytics.js` yüklemesini onaya
bağlayın. KVKK aydınlatma metni + gizlilik politikası sayfası ekleyin.

---

## 6) Canlı sonrası kontrol listesi
- [ ] securityheaders.com skoru A/A+
- [ ] GSC + Bing doğrulandı, sitemap gönderildi
- [ ] GA4 Realtime'da event'ler görünüyor (tel/WhatsApp tıkla, test et)
- [ ] Clarity kayıt alıyor
- [ ] UptimeRobot yeşil
- [ ] Lighthouse mobil ≥90 (Ctrl+F5 sonrası), CWV yeşil
- [ ] www → apex 301 çalışıyor, HTTPS zorunlu
