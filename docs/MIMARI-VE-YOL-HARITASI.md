# Dentual Konya — Mimari Denetim & Teknik Yol Haritası

> Senior Software Architect / CTO / DevOps bakış açısıyla mevcut projenin denetimi ve
> üretim ortamına/kurumsal ölçeğe taşınması için uygulanabilir yol haritası.
> Tarih: 2026-06. Kapsam: mevcut **statik çok-sayfalı** site + hedef evrim mimarisi.

---

## 🎯 Yönetici Özeti (CTO Verdict)

**Mevcut gerçeklik:** Proje şu an **statik, çok-sayfalı bir pazarlama sitesi** — vanilla
HTML/CSS/JS, Python ile üretilen sayfalar (`tools/gen_pages.py`), **backend yok, veritabanı
yok, hosting yok (sadece local `python http.server`)**, CI/CD yok, test yok, monitoring yok.
Buna karşılık **SEO ve Core Web Vitals tarafı sektör-üstü** (gerçek URL mimarisi, schema,
sitemap, WebP, LCP/CLS düzeltmeleri).

**En önemli mesaj:** Bir diş kliniği sitesi için **şu an backend/DB eklemek erken olur** —
çözülmemiş bir problem için karmaşıklık ve saldırı yüzeyi eklemektir. Doğru strateji **fazlı evrim**:

| Faz | Ne | Ne zaman |
|---|---|---|
| **Faz 0 (şimdi)** | Statik site + host-seviyesi güvenlik/CDN + form backend (serverless) + analytics | 0–30 gün |
| **Faz 1** | Profesyonel SSG'ye geçiş (Astro) + Headless CMS | 1–3 ay |
| **Faz 2** | Online randevu (DB + API + admin panel + auth + bildirim) | 3–6 ay |

**İki en acil eksik:** (1) sitenin **henüz canlıda olmaması**, (2) **formların sadece
WhatsApp'a yönlenip hiçbir yere kayıt edilmemesi**.

---

## 1. Frontend Mimarisi

| Madde | Olması gereken | Profesyonel yöntem | Bu projede? | Eksik / Öneri |
|---|---|---|---|---|
| Dosya yapısı | Modüler `src/`, partial/component | SSG (Astro/Next) | 🟡 Düz statik + Python generator | Ortak header/footer partial yok → 19 dosyada tekrar; Astro `layouts/` |
| Component yapısı | Yeniden kullanılabilir | `.astro`/`.tsx` | ❌ HTML tekrarı | Navbar/Footer/TreatmentCard/FAQ/BranchCard component'leştir |
| Responsive | Mobile-first, breakpoint sistemi | Tailwind/token | ✅ İyi (custom CSS, nav 1024px) | Breakpoint'ler dağınık → token'a bağla |
| Accessibility (WCAG 2.1 AA) | Landmark, focus, kontrast, ARIA | axe + manuel | 🟡 92/100 | Skip-link yok, focus-visible zayıf, form `aria-live` yok → axe-core CI |
| UI/UX standartları | Tutarlı spacing/typografi ölçeği | Design tokens | 🟡 CSS değişkenleri | Token dokümantasyonu + Storybook yok |
| Tasarım sistemi | Renk/tipografi/komponent kütüphanesi | Figma↔kod token | 🟡 Yarı | Resmi sistem/Storybook kur |
| Tailwind | Build + purge | PostCSS/CLI JIT | ❌ Kararı verildi, kullanılmıyor | Astro'da build ile entegre (CDN değil) |
| State management | Minimal, öngörülebilir | Nano-store/Context | 🟡 DOM + localStorage | Şimdilik yeterli |
| Form yönetimi | Şema validation + backend | Zod + API | 🔴 Sadece client + WhatsApp, kayıt yok | **Acil:** serverless endpoint + Zod + honeypot/captcha |
| Hata yönetimi | Error boundary + logging | Sentry + UI state | 🔴 Yok | Sentry (browser) + form hata state'leri |
| Performans | LCP/CLS/INP hedef + bütçe | CI budget | ✅ Bu oturumda büyük iyileştirme | Lighthouse CI + budget |
| Code splitting | Route/komponent bazlı | Vite/Next | ❌ Tek script.js (74KB) | Astro/Vite split |
| Lazy loading | Görsel/iframe/komponent | loading=lazy, IO, dynamic import | ✅ Görsel + hero slayt 2-4 + map facade | İyi |
| Görsel optimizasyonu | WebP/AVIF + responsive srcset | `<picture>`/build | 🟡 WebP var, srcset yok | Astro `<Image>` ile responsive + AVIF |
| Font optimizasyonu | Self-host, subset, preload, swap | woff2 subset | 🟡 Google Fonts CDN + preconnect + swap | Self-host + Latin-subset + preload |
| Core Web Vitals | LCP<2.5/CLS<0.1/INP<200 | Field + lab | ✅ Lab'de hedefe yakın | RUM (web-vitals.js → GA4) ekle |

**Karar:** Kısa vadede yapı iyi. Orta vadede **Astro'ya geçiş** (sıfır-JS varsayılan, islands,
built-in image/SEO, layout/partial) — `gen_pages.py` + `script.js` **veri tekrarını** çözer.

---

## 2. Backend Mimarisi

**Mevcut: backend YOK.** Aşağıdaki, dinamik özellik eklendiğinde önerilen hedef mimari.
**Önerilen yığın:** Node.js 22 + TypeScript + **NestJS** (katmanlı) veya hafif **Fastify + Prisma**.
İçerik için **Headless CMS** (Payload/Strapi/Directus). Başlangıçta serverless.

| Başlık | Endüstri standardı | Bu proje için öneri | Öncelik |
|---|---|---|---|
| API tasarımı | REST(OpenAPI)/tRPC + versiyon | `/api/v1`, OpenAPI, DTO | Yüksek |
| Katmanlı mimari | Controller→Service→Repository | NestJS modülleri | Yüksek |
| Servis yapısı | İş mantığı serviste | Appointment/Lead/Notification servisleri | Yüksek |
| İş mantığı | Domain kuralları izole | Randevu çakışma + çalışma saati | Yüksek |
| Validation | Şema bazlı, kenarda | Zod/class-validator (FE+BE) | **Kritik** |
| Logging | Yapılandırılmış JSON | pino + correlation-id | Yüksek |
| Error handling | Merkezî filter + standart gövde | NestJS ExceptionFilter + Problem+JSON | Yüksek |
| Authentication | JWT/session, OAuth | JWT+refresh / Auth.js / Clerk | Orta |
| Authorization | RBAC | admin/editor/reception | Orta |
| Rate limiting | IP/kullanıcı | @nestjs/throttler + Cloudflare WAF | **Kritik** |
| Queue | Async işler | BullMQ (Redis) — bildirimler | Orta |
| Caching | Çok katmanlı | CDN + Redis + HTTP cache header | Orta |

**Form için ACİL minimal çözüm (backend kurmadan):** Cloudflare Worker / Vercel Function +
**Turnstile** + **Resend/Postmark** + Sheets/Airtable/KV kaydı. Her talep kayıt altına alınır.

---

## 3. Veritabanı Mimarisi

**Öneri:** PostgreSQL 16 + **Prisma ORM**. 3NF; M:N ara tablolar; UUID PK; `created_at/updated_at`;
soft-delete (`deleted_at`).

**İlişkiler:** branches 1—N doctors / appointments / leads · doctors N—M treatments ·
treatments 1—N appointments · blog_categories 1—N blog_posts · users 1—N blog_posts ·
leads / appointments / appointment_slots · users + audit_log.

```sql
create table branches (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null, name text not null,
  address text not null, district text not null, phone text not null,
  lat numeric(9,6), lng numeric(9,6),
  is_night_shift boolean default false,
  opens time default '09:00', closes time default '23:30',
  created_at timestamptz default now(), updated_at timestamptz default now()
);
create table doctors (
  id uuid primary key default gen_random_uuid(),
  full_name text not null, title text, specialty text, photo_url text,
  branch_id uuid references branches(id) on delete set null,
  is_active boolean default true, sort_order int default 0
);
create table treatments (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null, title text not null, excerpt text, body text,
  hero_image text, meta_title text, meta_description text, is_published boolean default true
);
create table doctor_treatments (
  doctor_id uuid references doctors(id) on delete cascade,
  treatment_id uuid references treatments(id) on delete cascade,
  primary key (doctor_id, treatment_id)
);
create table blog_categories (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null, name text not null
);
create table blog_posts (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null, title text not null, excerpt text, body text not null,
  cover_image text, read_minutes int,
  category_id uuid references blog_categories(id), author_id uuid references users(id),
  target_keyword text, meta_title text, meta_description text,
  status text default 'draft', published_at timestamptz,
  created_at timestamptz default now(), updated_at timestamptz default now()
);
create table leads (
  id uuid primary key default gen_random_uuid(),
  name text not null, phone text not null, email text,
  branch_id uuid references branches(id), message text,
  source text default 'web_form', utm jsonb, status text default 'new',
  ip inet, user_agent text, created_at timestamptz default now()
);
create table appointment_slots (
  id uuid primary key default gen_random_uuid(),
  branch_id uuid references branches(id) on delete cascade,
  doctor_id uuid references doctors(id) on delete cascade,
  starts_at timestamptz not null, ends_at timestamptz not null,
  is_booked boolean default false, unique (doctor_id, starts_at)
);
create table appointments (
  id uuid primary key default gen_random_uuid(),
  slot_id uuid references appointment_slots(id),
  branch_id uuid references branches(id), doctor_id uuid references doctors(id),
  treatment_id uuid references treatments(id),
  patient_name text not null, patient_phone text not null, patient_email text, note text,
  status text default 'requested', created_at timestamptz default now()
);
create table users (
  id uuid primary key default gen_random_uuid(),
  email citext unique not null, password_hash text not null,
  role text not null default 'editor', is_active boolean default true
);
create table audit_log (
  id bigserial primary key, user_id uuid, action text, entity text,
  entity_id uuid, diff jsonb, created_at timestamptz default now()
);

-- Index & optimizasyon
create index on leads (status, created_at desc);
create index on appointments (branch_id, status, created_at desc);
create index on appointment_slots (doctor_id, starts_at) where is_booked = false;
create index on blog_posts (status, published_at desc);
```

**Backup:** managed Postgres (Neon/Supabase/RDS) PITR + günlük snapshot (30 gün).
**Migration:** Prisma Migrate (versiyonlu, CI'da). **KVKK:** PII minimumda, açık rıza, saklama
süresi, silme hakkı, pgcrypto ile şifreleme.

---

## 4. Güvenlik Denetimi

| Önlem | Risk | Uygulama | Bu projede gereklilik |
|---|---|---|---|
| HTTPS/HSTS | 🔴 | Cloudflare/Let's Encrypt + HSTS | **Kritik** (şu an local http) |
| CSP | 🟠 | nonce/hash + default-src 'self' | **Yüksek** — inline script/style var → hash gerekli |
| XSS | 🟠 | escape, CSP, innerHTML denetimi | 🟡 Düşük (kullanıcı girdisi basılmıyor); form backend gelince şart |
| CSRF | 🟠 | SameSite + token | Oturum gelince gerekli |
| SQL Injection | 🔴 | Parametreli/ORM | DB yok → Prisma kullan |
| Input validation | 🔴 | Zod (FE+BE) | **Kritik** (form) |
| Rate limiting | 🟠 | Cloudflare + throttle | Form gelince kritik |
| reCAPTCHA/Turnstile | 🟠 | Cloudflare Turnstile | **Yüksek** (spam/bot) |
| Brute force | 🟠 | Login throttle + lockout | Admin gelince |
| Secret management | 🔴 | .env + vault, repoya commit etme | Backend gelince kritik |
| Env variables | — | Ortam bazlı config | Backend gelince |
| Güvenlik header'ları | 🟠 | X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-Frame-Options | **Yüksek** (host 5 dk) |

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=()
Content-Security-Policy: default-src 'self'; img-src 'self' https://www.google.com data:;
  style-src 'self' https://fonts.googleapis.com 'unsafe-inline';
  font-src https://fonts.gstatic.com; frame-src https://www.google.com; script-src 'self' 'sha256-...'
```
> Sitedeki inline `<script>` (ann-dismissed) ve inline `style`'lar CSP'yi zorlaştırır → hash ekle
> veya dışarı taşı (Astro geçişinde doğal çözülür).

---

## 5. SEO & Teknik SEO — Kontrol Listesi (en güçlü alan)

| Alan | Durum |
|---|---|
| On-page (title/desc/H1/alt) | ✅ Her sayfa optimize |
| Technical (canonical/robots/sitemap) | ✅ 19 URL sitemap, robots, self-canonical |
| Local SEO | ✅ Şube sayfaları + Dentist schema + areaServed (🟡 Karatay/Selçuklu gerçek geo eksik) |
| Schema markup | ✅ WebSite/MedicalOrg/Dentist/FAQPage/MedicalProcedure/BlogPosting/Breadcrumb |
| URL mimarisi | ✅ Pretty, hiyerarşik |
| Internal linking | ✅ Tedavi↔şube↔gece-acil↔blog |
| Blog mimarisi | ✅ Gerçek URL'ler (🟡 içerik üretimi devam etmeli — 30 konu takvimi hazır) |
| CWV | ✅ Bu oturumda düzeltildi |
| Eksik | 🟡 hreflang/EN gövde, gerçek geo, GSC/Bing gönderimi (canlı olunca), RUM |

Tek gerçek blocker: **siteyi canlıya alıp GSC'ye eklemek.**

---

## 6. Sunucu & DevOps

**Mevcut: sadece local `python http.server`. Canlı altyapı yok.**

**A) Statik (şu an DOĞRU seçim) — Cloudflare Pages / Netlify / Vercel:** global CDN, otomatik
SSL, Brotli+Gzip, sınırsız ölçek, ucuz, Git push → otomatik deploy. Cloudflare önünde WAF +
rate-limit + Turnstile + güvenlik header'ları. **100k kullanıcıya kadar ekstra mimari gerekmez.**

**B) VPS yolu (yalnızca backend/CMS gelince):** Ubuntu + Docker + Nginx reverse proxy +
Let's Encrypt, Cloudflare önde.

```nginx
server {
  listen 443 ssl http2; server_name dentualkonya.com;
  gzip on; gzip_types text/css application/javascript image/svg+xml;
  brotli on; brotli_types text/css application/javascript;   # ngx_brotli
  location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
  location /api/    { proxy_pass http://api:3000; }
  location /        { root /var/www/dentual; try_files $uri $uri/ /404.html; }
}
```

**CI/CD (şu an YOK — kritik):** push → `python tools/gen_pages.py` → HTML/link lint →
Lighthouse CI (perf bütçesi) → Cloudflare Pages deploy. Manuel deploy ve "unutulan regenerate"
riskini kaldırır.

---

## 7. Monitoring & Analitik (şu an %0)

| Araç | Amaç | Öncelik |
|---|---|---|
| GA4 | Trafik + dönüşüm (arama/WhatsApp tık) | **Kritik** |
| Search Console + Bing | Indeksleme, sorgu, CWV (CrUX) | **Kritik** |
| Microsoft Clarity | Ücretsiz heatmap + session replay | Yüksek |
| Sentry | JS/backend hata takibi | Yüksek |
| UptimeRobot / Better Uptime | Erişim + SSL bitiş uyarısı | Yüksek |
| web-vitals.js → GA4 | Gerçek kullanıcı (RUM) LCP/CLS/INP | Orta |
| Cloudflare Analytics | Edge trafik/saldırı | Orta |

**Dönüşüm event'leri eklenmeli:** `tel:` tık, WhatsApp tık, form gönderim, harita aç.
KPI = arama + WhatsApp dönüşümü; şu an ölçülmüyor.

---

## 8. Ölçeklenebilirlik

| Seviye | Statik site | Dinamik (backend) |
|---|---|---|
| 1.000 | CDN ile sorunsuz | Serverless function + managed Postgres yeterli |
| 10.000 | Değişiklik yok | API'yi container'a al, Redis cache, PgBouncer, queue (BullMQ) |
| 100.000 | CDN hâlâ yeter | DB read-replica, Redis cluster, API yatay autoscale (Cloud Run/K8s), WAF, async kuyruk, tracing |

Statik içerik "sınırsız" ölçeklenir (CDN). Darboğaz **yalnızca backend eklenince** başlar →
dinamik özellikleri serverless/managed servisle başlat, erken K8s'ten kaçın.

---

## 9. Nihai Teknik Yol Haritası

### Sınıflandırma
**🔴 Kritik (production blocker)**
1. Gerçek hosting + HTTPS + CDN (Cloudflare Pages)
2. GSC/Bing + GA4 kurulumu
3. Form backend + Turnstile + e-posta/kayıt
4. CI/CD (push→generate→deploy)
5. Güvenlik header'ları + CSP

**🟠 Yüksek**
6. Sentry + UptimeRobot
7. Karatay/Selçuklu gerçek geo; hreflang/EN stratejisi
8. Veri tekrarını (script.js ↔ gen_pages.py) tek kaynağa indir
9. Font self-host + responsive srcset/AVIF
10. A11y (skip-link, focus, aria-live) + axe CI

**🟡 Orta**
11. Astro'ya geçiş + Headless CMS
12. Tailwind build entegrasyonu, tasarım sistemi/Storybook
13. Microsoft Clarity + dönüşüm event'leri + RUM
14. Test altyapısı (Playwright e2e, Vitest)

**🟢 Düşük**
15. Online randevu (DB + API + admin + auth)
16. Tam çok-dilli içerik, PWA, blog şema genişletme

### Uygulama planı
**İlk 7 gün (canlıya çık + görünür ol):** Cloudflare Pages deploy + domain + SSL + Brotli ·
güvenlik header'ları + temel CSP · GA4 + GSC + Bing + sitemap gönderimi · form → Worker +
Turnstile + Resend + kayıt · UptimeRobot + Sentry.

**İlk 30 gün (sağlamlaştır + ölç):** GitHub Actions CI/CD (generate→lint→Lighthouse CI→deploy) ·
geo + font self-host + srcset/AVIF + a11y · Clarity + dönüşüm event'leri · veri tekrarını tek
JSON kaynağa indir · blog A-grubu içerik üretimi.

**İlk 90 gün (ürünleştir):** Astro + Headless CMS migrasyonu (component/layout, Tailwind build,
CSP nonce) · test piramidi + performance budget gate · (iş kararıysa) online randevu modülü
(Postgres+Prisma + NestJS + admin Auth.js/RBAC + BullMQ bildirim + KVKK).

---

## Önerilen Hedef Teknoloji Yığını
- **Frontend/SSG:** Astro + Tailwind (build) + TypeScript + `@astrojs/image`
- **İçerik:** Payload CMS / Directus (self-host) veya Sanity (managed)
- **Backend (Faz 2):** NestJS + Prisma + PostgreSQL + Redis + BullMQ
- **Auth:** Auth.js / Clerk · **Validation:** Zod
- **Infra:** Cloudflare (Pages+Workers+WAF+Turnstile) → büyürse Cloud Run/Fly.io + Neon/Supabase
- **Gözlem:** GA4 + GSC + Clarity + Sentry + UptimeRobot + Lighthouse CI
