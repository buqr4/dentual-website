# -*- coding: utf-8 -*-
"""
Konya Diş Hekimi — static page generator (SEO multi-page build).

WHY THIS EXISTS
---------------
The site is a set of plain static HTML files (no runtime build). To keep the
shared chrome (announcement bar, navbar, footer, WhatsApp widget) identical and
maintenance-friendly across every URL, this one-off generator reads the canonical
chrome straight out of index.html and stamps it onto each sub-page, swapping only:
  - the <head> SEO block (title / description / canonical / OG / JSON-LD),
  - the <body> data-* attributes (page id + localized title/description),
  - the active nav-link state,
  - the <main> content.

Run:  python tools/gen_pages.py
Output: real .html files at /<route>/index.html  (pretty trailing-slash URLs)

It is safe to re-run; it overwrites generated pages only. index.html (home) is
NOT touched. Editing a generated page by hand is fine — just don't re-run the
generator afterwards, or re-apply your edit here.
"""
import json, os, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = "https://konyadishekimi.com"

# ---------------------------------------------------------------- config / env
# Search-engine ownership tokens. Paste tokens here (or leave empty to omit the
# meta entirely). Single source of truth for every generated page + the home page.
GSC_TOKEN = ""   # Google Search Console "HTML tag" verification token
BING_TOKEN = ""  # Bing Webmaster Tools verification token

def _verify_meta():
    out = []
    if GSC_TOKEN:
        out.append('<meta name="google-site-verification" content="%s" />' % GSC_TOKEN)
    if BING_TOKEN:
        out.append('<meta name="msvalidate.01" content="%s" />' % BING_TOKEN)
    # Always leave a fill-in hint when a token is missing (cheap, easy handover).
    if not out:
        return ('<!-- Search-engine verification: set GSC_TOKEN / BING_TOKEN in '
                'tools/gen_pages.py (and index.html) to emit these tags. -->')
    return "\n    ".join(out)

VERIFY_META = _verify_meta()

# Cache-busting fingerprint: a short content hash of the shared CSS/JS. Appended
# as ?v=<hash> to every css/js reference so a new deploy is never served stale.
# Changes ONLY when one of these files changes → long-cache friendly.
def _asset_ver(*rel_paths):
    h = hashlib.sha1()
    for p in rel_paths:
        try:
            with open(os.path.join(ROOT, p), "rb") as fh:
                # Normalise CRLF→LF so the hash is identical on Windows and Linux CI.
                h.update(fh.read().replace(b"\r\n", b"\n"))
        except OSError:
            pass
    return h.hexdigest()[:8]

ASSET_VER = _asset_ver("css/style.css", "css/theme-navy.css", "js/script.js", "js/analytics.js")

def _stamp(html):
    """Strip any existing ?v=… then re-append the current fingerprint to the
    shared css/js references. Idempotent (safe to run repeatedly)."""
    html = re.sub(r'(/(?:css/style\.css|js/script\.js|js/analytics\.js))\?v=[0-9a-f]+',
                  r'\1', html)
    for ref in ("/css/style.css", "/css/theme-navy.css", "/js/script.js", "/js/analytics.js"):
        html = html.replace(ref + '"', ref + '?v=' + ASSET_VER + '"')
    return html

# Photographic assets are served as WebP for <img> tags (huge size win); the
# original .jpg is kept for og:image / schema image (broadest social support).
def web(fn):
    return fn.rsplit(".", 1)[0] + ".webp"

# ---------------------------------------------------------------- chrome reuse
with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    HOME = f.read()

CHROME_TOP = HOME[HOME.index("<!-- ============ ANNOUNCEMENT BAR"):HOME.index('<main id="main"')]
CHROME_BOTTOM = HOME[HOME.index("</main>"):]  # footer + widget + scroll-top + script + </body></html>

# ---------------------------------------------------------------- head template
HEAD_TMPL = """<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{TITLE}}</title>
    <meta name="description" content="{{DESC}}" />
    <meta name="author" content="Konya Diş Hekimi" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{{CANON}}" />
    <!-- hreflang: TR is the only published language today; x-default self-refs.
         When an EN edition ships, add its English alternate link here. -->
    <link rel="alternate" hreflang="tr" href="{{CANON}}" />
    <link rel="alternate" hreflang="x-default" href="{{CANON}}" />

    <!-- Geo -->
    <meta name="geo.region" content="TR-42" />
    <meta name="geo.placename" content="Konya" />

    <!-- Open Graph -->
    <meta property="og:type" content="{{OGTYPE}}" />
    <meta property="og:site_name" content="Konya Diş Hekimi" />
    <meta property="og:locale" content="tr_TR" />
    <meta property="og:title" content="{{TITLE}}" />
    <meta property="og:description" content="{{DESC}}" />
    <meta property="og:url" content="{{CANON}}" />
    <meta property="og:image" content="{{OGIMG}}" />

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{{TITLE}}" />
    <meta name="twitter:description" content="{{DESC}}" />
    <meta name="twitter:image" content="{{OGIMG}}" />

    <meta name="theme-color" content="#0d4d4d" />

    <!-- Favicons -->
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png" />
    <link rel="icon" type="image/png" sizes="64x64" href="/assets/favicon-64.png" />
    <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/css/style.css" />
    <link rel="stylesheet" href="/css/theme-navy.css" />
    <script>try{if(localStorage.getItem('konyadishekimi-ann-closed')==='1')document.documentElement.classList.add('ann-dismissed');}catch(e){}</script>

    <!-- Structured Data -->
    <script type="application/ld+json">
{{SCHEMA}}
    </script>

    <!-- Search-engine verification (managed centrally in gen_pages.py) -->
    {{VERIFY}}
    <!-- Analytics + conversion tracking -->
    <script defer src="/js/analytics.js"></script>
</head>"""

ORG_REF = {"@id": ORIGIN + "/#organization"}

def breadcrumb(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": ORIGIN + u}
            for i, (n, u) in enumerate(items)
        ],
    }

def crumb_html(items):
    parts = []
    for i, (n, u) in enumerate(items):
        if i < len(items) - 1:
            parts.append('<a href="%s">%s</a>' % (u, n))
        else:
            parts.append('<span>%s</span>' % n)
    sep = ' <span aria-hidden="true">&rsaquo;</span> '
    return ('<nav class="crumb" aria-label="breadcrumb" style="font-size:.85rem;'
            'opacity:.75;margin-bottom:.7rem;display:flex;flex-wrap:wrap;gap:.4rem;'
            'align-items:center">' + sep.join(parts) + '</nav>')

def faq_block(title, qa):
    """Static, accessible FAQ accordion that reuses existing .faq-* styling and
    the site's faq toggle JS (it binds any .faq-q). Returns (html, schema_node)."""
    items = "".join(
        '<div class="faq-item"><button class="faq-q">%s<span class="faq-icon">+</span></button>'
        '<div class="faq-a"><div class="faq-a-inner">%s</div></div></div>' % (q, a)
        for q, a in qa
    )
    html = (
        '<div class="section section-alt"><div class="container container-narrow">'
        '<div class="section-head reveal"><span class="section-tag">S.S.S.</span>'
        '<h2 class="section-title">%s</h2></div>'
        '<div class="faq-list" data-static-faq>%s</div></div></div>' % (title, items)
    )
    node = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa
        ],
    }
    return html, node

def page(route, page_id, title_tr, desc_tr, h1, content, schema_graph,
         active_href, title_en=None, desc_en=None, og_img=None, og_type="website"):
    title_en = title_en or title_tr
    desc_en = desc_en or desc_tr
    og_img = og_img or (ORIGIN + "/assets/hero/hero1.jpg")
    canon = ORIGIN + route
    head = (HEAD_TMPL
            .replace("{{TITLE}}", title_tr)
            .replace("{{DESC}}", desc_tr)
            .replace("{{CANON}}", canon)
            .replace("{{OGTYPE}}", og_type)
            .replace("{{OGIMG}}", og_img)
            .replace("{{VERIFY}}", VERIFY_META)
            .replace("{{SCHEMA}}", json.dumps(
                {"@context": "https://schema.org", "@graph": schema_graph},
                ensure_ascii=False, indent=2)))
    body_attrs = (
        'data-page="%s"\n      data-title-tr="%s"\n      data-title-en="%s"'
        '\n      data-desc-tr="%s"\n      data-desc-en="%s"'
        % (page_id, title_tr, title_en, desc_tr, desc_en)
    )
    top = CHROME_TOP.replace('class="nav-link active"', 'class="nav-link"')
    if active_href:
        top = top.replace('href="%s" class="nav-link"' % active_href,
                          'href="%s" class="nav-link active"' % active_href, 1)
    html = ("<!DOCTYPE html>\n<html lang=\"tr\" data-skin=\"navy\">\n" + head + "\n<body " + body_attrs +
            ">\n\n    <a class=\"skip-link\" href=\"#main\">İçeriğe geç</a>\n\n    " + top +
            '<main id="main" tabindex="-1">\n' + content + "\n    " + CHROME_BOTTOM)
    out_dir = os.path.join(ROOT, route.strip("/").replace("/", os.sep))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_stamp(html))
    return route

def hero(h1, sub, crumbs):
    return ('<div class="page-hero"><div class="container">' + crumb_html(crumbs) +
            '<h1 class="page-hero-title reveal">%s</h1>'
            '<p class="page-hero-sub reveal">%s</p></div></div>' % (h1, sub))

def cta(text="Bu konuda profesyonel destek mi arıyorsunuz? Gülüşünüze birlikte yön verelim."):
    return ('<div class="blog-article-cta"><p>%s</p>'
            '<a href="/iletisim/" class="btn btn-primary btn-lg">Bize Ulaşın</a></div>' % text)

ROUTES = []  # (route, priority) for sitemap

# ============================================================ HAKKIMIZDA
about_content = hero(
    "Konya Diş Kliniği Konya Diş Hekimi Hakkında",
    "Konya'da gülüşlere değer katıyoruz — tecrübeli kadro, hasta odaklı yaklaşım.",
    [("Ana Sayfa", "/"), ("Hakkımızda", "/hakkimizda/")]
) + """
<div class="section"><div class="container about-intro">
  <div class="about-text reveal">
    <span class="section-tag">Biz Kimiz?</span>
    <h2 class="section-title" style="text-align:left">Güvenle Tedavi Ediyoruz</h2>
    <p>Konya Diş Hekimi, Karatay, Selçuklu ve Meram şubeleriyle Konya'nın güvenilir ağız ve diş sağlığı polikliniğidir. En değerli varlık olan insan, kuruluşumuzun merkezinde yer alır; güven ve mutlu çözümler odak noktamızı oluşturur.</p>
    <p>Tecrübeli hekimlerimizle multidisipliner yaklaşıma önem veriyoruz. Ağız ve diş sağlığında teşhis ve tedavide çok yönlü yaklaşım, disiplinli çalışma ve en önemlisi hastanın ne istediği bizim için önceliklidir.</p>
    <p>Hastalarımızı uzun uzun dinler, modern ve güncel tedavi yöntemleriyle mutlu sona ulaşırız. Üstelik <strong>pazar dahil her gün gece 23:00'a kadar</strong> açık olarak, Konya'da gece açık nöbetçi diş hekimi hizmeti sunuyoruz.</p>
  </div>
  <div class="about-image reveal">
    <img src="/assets/hero/about-dentual.webp" alt="Konya Diş Hekimi diş kliniğinde hekim ve hasta" loading="lazy" width="600" height="450" />
  </div>
</div></div>
<div class="section section-alt"><div class="container">
  <div class="values-grid">
    <div class="value-card reveal"><h3>Misyonumuz</h3><p>Her hastamıza kişiye özel, bilimsel ve etik tedavi planları sunarak Konya'nın en güvenilir diş sağlığı merkezi olmak.</p></div>
    <div class="value-card reveal"><h3>Vizyonumuz</h3><p>Teknolojiyi ve insan odaklı yaklaşımı birleştirerek diş hekimliğinde bölgesel bir referans noktası haline gelmek.</p></div>
    <div class="value-card reveal"><h3>Değerlerimiz</h3><p>Şeffaflık, hasta memnuniyeti, hijyen, sürekli eğitim ve dürüstlük çalışmalarımızın temelini oluşturur.</p></div>
  </div>
</div></div>
<div class="section"><div class="container">
  <div class="section-head reveal"><span class="section-tag">Neden Biz?</span><h2 class="section-title">Konya Diş Hekimi Farkı</h2></div>
  <div class="why-grid">
    <div class="why-item reveal"><span>&#10003;</span> <span>Son teknoloji dijital görüntüleme ve tedavi cihazları</span></div>
    <div class="why-item reveal"><span>&#10003;</span> <span>Uluslararası standartlarda sterilizasyon</span></div>
    <div class="why-item reveal"><span>&#10003;</span> <span>Ağrısız ve konforlu tedavi yöntemleri</span></div>
    <div class="why-item reveal"><span>&#10003;</span> <span>Deneyimli ve güler yüzlü uzman kadro</span></div>
    <div class="why-item reveal"><span>&#10003;</span> <span>Şeffaf fiyatlandırma ve ödeme kolaylıkları</span></div>
    <div class="why-item reveal"><span>&#10003;</span> <span><a href="/gece-acik-dis-klinigi-konya/">Gece açık &amp; acil diş hizmeti</a> ile 3 merkezi şube</span></div>
  </div>
</div></div>
""" + '<div class="section"><div class="container">' + cta() + '</div></div>'
ROUTES.append(page(
    "/hakkimizda/", "about",
    "Hakkımızda – Konya'nın Güvenilir Diş Kliniği | Konya Diş Hekimi",
    "Konya Diş Hekimi'nın uzman hekim kadrosu ve hasta odaklı yaklaşımı. 10+ uzman hekim, 9000+ mutlu hasta, 3 şube. Gece açık nöbetçi diş hekimi.",
    "Hakkımızda",
    about_content,
    [breadcrumb([("Ana Sayfa", "/"), ("Hakkımızda", "/hakkimizda/")]),
     {"@type": "AboutPage", "@id": ORIGIN + "/hakkimizda/#webpage", "url": ORIGIN + "/hakkimizda/",
      "name": "Hakkımızda – Konya Diş Hekimi", "about": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
    "/hakkimizda/",
    title_en="About Us – Konya's Trusted Dental Clinic | Konya Diş Hekimi",
    desc_en="Konya Diş Hekimi's expert dentists and patient-focused care. 10+ specialists, 9000+ happy patients, 3 branches. Night-open emergency dentist."))

# ============================================================ TREATMENTS DATA
TREATMENTS = [
    {"slug": "implant", "title": "İmplant Tedavisi",
     "sub": "Tek diş eksikliğinden tam dişsizliğe kadar en iyi ve kalıcı çözüm.",
     "img": "implant.jpg",
     "desc": "İmplantlar günümüzde tek diş eksikliklerinin giderilmesinde olduğu kadar, tamamen veya kısmi dişsizliği olan bireylerin tedavisinde de en iyi seçenektir. Çene kemiğine yerleştirilen titanyum yapay kök, kemik dokusuyla kaynaşarak doğal dişe en yakın sağlam bir temel oluşturur. Konya'da implant tedavisi için kliniğimizin üç şubesinde de uzman kadromuzla hizmetinizdeyiz.",
     "candidates": "Bir veya birden fazla dişi eksik olan, çene kemiği implant için yeterli olan ve sabit, doğal bir çözüm isteyen yetişkin hastalar için uygundur.",
     "process": [("Muayene & Görüntüleme", "Röntgen ve tomografi ile çene kemiği değerlendirilerek kişiye özel tedavi planı oluşturulur."),
                 ("Cerrahi Yerleştirme", "Lokal anestezi altında titanyum implant çene kemiğine konforlu şekilde yerleştirilir."),
                 ("Kaynaşma (Osseointegrasyon)", "İmplantın kemikle kaynaşması için birkaç aylık iyileşme süreci beklenir."),
                 ("Protez Dişin Takılması", "Kaynaşma tamamlanınca doğal dişlerinizle uyumlu protez diş implant üzerine sabitlenir.")],
     "points": ["Doğal görünüm ve fonksiyon", "Doğru bakımla ömür boyu kullanım", "Komşu dişlere zarar vermez", "Çene kemiği erimesini önler"]},
    {"slug": "gulus-estetigi", "title": "Gülüş Estetiği",
     "sub": "Güldüğünüzde ilk göze çarpan ön dişleriniz için kişiye özel estetik planlama.",
     "img": "gulus-estetigi.jpg",
     "desc": "Gülüş estetiği; yüz şekli, dudak yapısı ve diş eti çizgisi göz önünde bulundurularak kişiye özel planlanan bir uygulamadır. Lamina, zirkonyum kaplama ve diş beyazlatma gibi yöntemlerle dişlerin rengi, formu ve dizilimi yeniden tasarlanır. Konya'da gülüş tasarımı için kliniğimizde dijital planlama ile sonucu önceden görebilirsiniz.",
     "candidates": "Diş renginden, formundan veya diziliminden memnun olmayan; daha estetik ve simetrik bir gülüş isteyen herkes için planlanabilir.",
     "process": [("Analiz & Planlama", "Yüz şekli, dudak yapısı ve diş eti çizgisi incelenerek kişiye özel gülüş planı hazırlanır."),
                 ("Dijital Tasarım", "Yeni gülüşünüz dijital ortamda tasarlanır ve uygulama öncesi sonuç öngörülür."),
                 ("Uygulama", "Lamina, zirkonyum kaplama veya diş beyazlatma yöntemleriyle dişler yeniden şekillendirilir."),
                 ("Son Kontrol", "Uyum ve estetik açısından son rötuşlar yapılarak gülüşünüz tamamlanır.")],
     "points": ["Yüz hatlarına uygun kişisel tasarım", "Doğal ve simetrik sonuç", "Renk, form ve dizilim uyumu", "Özgüven artıran bir gülümseme"]},
    {"slug": "ortodonti", "title": "Ortodonti (Diş Teli & Şeffaf Plak)",
     "sub": "Diş çapraşıklıkları, boşluklar ve ısırma problemleri için tel ve şeffaf plak tedavileri.",
     "img": "ortodonti.jpg",
     "desc": "Ortodonti tedavisi, dişlerin ve çenenin düzgün hizalanmasını sağlamak amacıyla yapılan bir dizi işlemdir. Çapraşık dişlerin düzeltilmesi, boşlukların kapatılması ve ısırık problemlerinin çözülmesini içerir. Metal teller, seramik aparatlar ve şeffaf plaklar kullanılır; çocukluk döneminde başlayabileceği gibi yetişkinler de faydalanabilir.",
     "candidates": "Çapraşık dişler, ısırık (kapanış) sorunları, dişler arasında anormal boşluklar veya çene pozisyonunda bozukluk olan her yaştan hasta uygun adaydır.",
     "process": [("Detaylı Muayene & Planlama", "Ağız muayenesi, panoramik röntgen ve gerektiğinde 3B görüntüleme ile durum değerlendirilir."),
                 ("Aparatların Uygulanması", "Size en uygun yöntem belirlenir; metal, seramik teller veya şeffaf plaklar uygulanır."),
                 ("Düzenli Kontroller", "Tedavi süresince periyodik kontrollerle aparatlar ayarlanır ve ilerleme takip edilir."),
                 ("Pekiştirme (Sonrası Bakım)", "Dişlerin yeni konumunu koruması için genellikle gece takılan pekiştirme apareyleri kullanılır.")],
     "points": ["Metal, seramik ve şeffaf plak seçenekleri", "Estetik ve daha çekici bir gülüş", "Düzgün dişlerle kolay temizlik, azalan çürük riski", "Çiğneme ve konuşmada işlevsel iyileşme"]},
    {"slug": "kanal-tedavisi", "title": "Kanal Tedavisi (Endodonti)",
     "sub": "İltihaplı dişleri çekmeden kurtaran modern endodonti uygulamaları.",
     "img": "kanal-tedavisi.jpg",
     "desc": "Kanal tedavisi, dişin merkezindeki canlı dokunun (pulpa) çıkartılarak kanalın uygun dolgu maddeleriyle doldurulması işlemidir. Çürük veya travma nedeniyle iltihaplanan diş sinirinin temizlenmesiyle, çekilmesi gereken dişler kurtarılır ve ağrı ortadan kaldırılır. Gece bastıran şiddetli diş ağrılarında kliniğimizin gece açık şubeleri yanınızdadır.",
     "candidates": "Derin çürük, diş ağrısı, sıcak-soğuğa aşırı hassasiyet veya travma nedeniyle siniri iltihaplanan dişe sahip hastalar için uygundur.",
     "process": [("Teşhis & Röntgen", "Dişin ve kök kanallarının durumu röntgenle ayrıntılı olarak değerlendirilir."),
                 ("Kanalların Temizlenmesi", "Lokal anestezi altında iltihaplı doku çıkarılır, kanallar şekillendirilerek temizlenir."),
                 ("Kanal Dolgusu", "Temizlenen kanallar uygun dolgu maddesiyle sızdırmaz şekilde doldurulur."),
                 ("Üst Restorasyon", "Diş; dolgu veya kaplama ile fonksiyonuna kavuşacak şekilde restore edilir.")],
     "points": ["Dişin çekilmesini önler", "Ağrıyı ortadan kaldırır", "Modern ve konforlu teknikler", "Uzun ömürlü sonuç"]},
    {"slug": "cerrahi", "title": "Cerrahi Uygulamalar (Ağız & Çene Cerrahisi)",
     "sub": "Diş çekiminden gömülü diş ve kist ameliyatlarına kadar ağız-çene cerrahisi.",
     "img": "cerrahi.jpg",
     "desc": "Ağız, diş ve çene cerrahisi; diş çekimi ile başlayıp gömülü 20'lik diş ameliyatları, implant cerrahisi, kist ameliyatları ve çene cerrahisi gibi işlemleri kapsar. Tüm uygulamalar uzman hekimlerimiz tarafından steril koşullarda ve lokal anestezi ile konforlu şekilde gerçekleştirilir.",
     "candidates": "Gömülü 20'lik dişi olan, çekilmesi gereken dişe veya kist gibi cerrahi müdahale gerektiren bir duruma sahip hastalar için uygundur.",
     "process": [("Muayene & Görüntüleme", "Panoramik röntgen ve tomografi ile cerrahi gereken bölge ayrıntılı değerlendirilir."),
                 ("Planlama & Bilgilendirme", "İşlem öncesi ayrıntılı plan yapılır ve hasta süreç hakkında bilgilendirilir."),
                 ("Cerrahi İşlem", "Lokal anestezi altında, steril koşullarda işlem konforlu şekilde gerçekleştirilir."),
                 ("İyileşme Takibi", "İşlem sonrası bakım önerileri verilir ve iyileşme süreci takip edilir.")],
     "points": ["Normal ve gömülü diş çekimi", "20'lik (yirmi yaş) diş ameliyatları", "Kist ve çene cerrahisi", "İmplant cerrahisi uygulamaları"]},
    {"slug": "cocuk-dis-hekimligi", "title": "Pedodonti (Çocuk Diş Hekimliği)",
     "sub": "0-14 yaş çocukların süt ve daimi dişlerinin sağlığı için özel yaklaşım.",
     "img": "pedodonti.jpg",
     "desc": "Pedodonti, 0-14 yaş çocukların süt ve daimi dişlerinin sağlığını korumanın yanı sıra problemleri tedavi etmeyi amaçlar. Uzman hekimlerimiz, çocukların diş hekimi korkusu yaşamadan sağlıklı dişlere sahip olması için özel teknikler kullanır. KDH Çocuk kliniğimizde minik hastalarımıza özel, neşeli bir ortam sunuyoruz.",
     "candidates": "0-14 yaş aralığındaki, koruyucu diş hekimliği veya süt/daimi diş tedavisi ihtiyacı olan tüm çocuklar için uygundur.",
     "process": [("Tanışma & Muayene", "Çocuğun güven duyması sağlanarak nazik bir şekilde ağız ve diş muayenesi yapılır."),
                 ("Koruyucu Uygulamalar", "Flor ve fissür örtücü gibi koruyucu işlemlerle çürük riski azaltılır."),
                 ("Tedavi", "Gerekli durumlarda süt ve daimi diş dolguları ile uygun tedaviler uygulanır."),
                 ("Düzenli Kontrol", "Diş gelişiminin sağlıklı ilerlemesi için periyodik kontroller planlanır.")],
     "points": ["Ağız hijyeni eğitimi", "Flor ve fissür örtücü uygulamaları", "Süt ve daimi diş dolgu/tedavileri", "Çocuk dostu, korkutmayan yaklaşım"]},
]
T_TITLE = {
    "implant": "İmplant Tedavisi Konya – Diş İmplantı Süreci & Fiyat | Konya Diş Hekimi",
    "gulus-estetigi": "Gülüş Estetiği Konya – Zirkonyum, Lamina, Diş Beyazlatma | Konya Diş Hekimi",
    "ortodonti": "Ortodonti Konya – Diş Teli & Şeffaf Plak Tedavisi | Konya Diş Hekimi",
    "kanal-tedavisi": "Kanal Tedavisi Konya (Endodonti) – Ağrısız Tedavi | Konya Diş Hekimi",
    "cerrahi": "Ağız & Çene Cerrahisi Konya – 20'lik Diş Çekimi | Konya Diş Hekimi",
    "cocuk-dis-hekimligi": "Çocuk Diş Hekimi Konya (Pedodonti) – KDH Çocuk",
}
T_DESC = {
    "implant": "Konya'da implant tedavisi: diş implantı süreci, kimlere uygun, avantajları. kliniğimizin uzman kadrosuyla doğal ve kalıcı çözüm. Randevu: 444 34 42.",
    "gulus-estetigi": "Konya gülüş estetiği: zirkonyum kaplama, lamina ve diş beyazlatma ile kişiye özel gülüş tasarımı. Dijital planlama ile kliniğimizde. Randevu: 444 34 42.",
    "ortodonti": "Konya ortodonti: diş teli ve şeffaf plak tedavisi ile çapraşık dişler ve kapanış sorunlarına çözüm. Her yaşa uygun. Konya Diş Hekimi. Randevu: 444 34 42.",
    "kanal-tedavisi": "Konya kanal tedavisi (endodonti): iltihaplı dişi çekmeden kurtaran ağrısız modern tedavi. Gece açık şubelerle Konya Diş Hekimi. Randevu: 444 34 42.",
    "cerrahi": "Konya ağız ve çene cerrahisi: gömülü 20'lik diş çekimi, kist ve implant cerrahisi. Steril koşullarda uzman kadro. Konya Diş Hekimi. Randevu: 444 34 42.",
    "cocuk-dis-hekimligi": "Konya çocuk diş hekimi (pedodonti): 0-14 yaş süt ve daimi diş tedavisi, koruyucu uygulamalar. Korkutmayan KDH Çocuk kliniği. Randevu: 444 34 42.",
}

def treatment_card(t):
    return ('<a href="/tedaviler/%s/" class="treatment-card reveal">'
            '<div class="treatment-img"><img src="/assets/treatments/%s" alt="%s — Konya Konya Diş Hekimi diş kliniği" loading="lazy" width="400" height="190" /></div>'
            '<div class="treatment-body"><h3>%s</h3><p>%s</p>'
            '<span class="treatment-more">Detayları Gör &rarr;</span></div></a>'
            % (t["slug"], web(t["img"]), t["title"], t["title"], t["sub"]))

# tedaviler index
tindex_content = hero(
    "Konya Diş Tedavileri",
    "Sağlıklı ve estetik gülüşler için sunduğumuz hizmetler. Detay için tedaviye tıklayın.",
    [("Ana Sayfa", "/"), ("Tedaviler", "/tedaviler/")]
) + '<div class="section"><div class="container"><div class="treatments-grid">' + \
    "".join(treatment_card(t) for t in TREATMENTS) + '</div>' + cta() + '</div></div>'
ROUTES.append(page(
    "/tedaviler/", "treatments",
    "Diş Tedavileri Konya – İmplant, Gülüş Estetiği, Ortodonti | Konya Diş Hekimi",
    "Konya'da implant, gülüş estetiği, ortodonti, kanal tedavisi, cerrahi ve çocuk diş hekimliği. kliniğimizde uzman kadroyla güvenli tedavi. Randevu: 444 34 42.",
    "Tedavilerimiz", tindex_content,
    [breadcrumb([("Ana Sayfa", "/"), ("Tedaviler", "/tedaviler/")]),
     {"@type": "CollectionPage", "@id": ORIGIN + "/tedaviler/#webpage", "url": ORIGIN + "/tedaviler/",
      "name": "Diş Tedavileri – Konya Diş Hekimi", "isPartOf": {"@id": ORIGIN + "/#website"},
      "about": ORG_REF}],
    "/tedaviler/",
    title_en="Dental Treatments Konya – Implants, Smile, Orthodontics | Konya Diş Hekimi",
    desc_en="Implants, smile aesthetics, orthodontics, root canal, surgery and pediatric dentistry in Konya. Expert care at our clinic. Call 444 34 42."))

# treatment detail pages
others = TREATMENTS
for t in TREATMENTS:
    related = [x for x in others if x["slug"] != t["slug"]][:3]
    related_html = " ".join('<a href="/tedaviler/%s/">%s</a>' % (r["slug"], r["title"]) for r in related)
    proc = "".join('<li><strong>%s</strong><span>%s</span></li>' % (s[0], s[1]) for s in t["process"])
    pts = "".join('<li>%s</li>' % p for p in t["points"])
    content = hero(t["title"], t["sub"],
                   [("Ana Sayfa", "/"), ("Tedaviler", "/tedaviler/"), (t["title"], "/tedaviler/%s/" % t["slug"])]) + (
        '<div class="section"><div class="container container-narrow">'
        '<img src="/assets/treatments/%s" alt="%s — Konya Konya Diş Hekimi" loading="lazy" width="760" height="360" style="width:100%%;height:auto;border-radius:16px;margin-bottom:1.6rem" />'
        '<p>%s</p>'
        '<div class="tm-callout" style="margin:1.4rem 0"><strong>Kimler İçin Uygun?</strong> <span>%s</span></div>'
        '<h2 class="section-title" style="text-align:left;margin-top:2rem">Tedavi Süreci</h2>'
        '<ol class="tm-process">%s</ol>'
        '<h2 class="section-title" style="text-align:left;margin-top:2rem">Avantajları</h2>'
        '<ul class="tm-list">%s</ul>'
        '<h2 class="section-title" style="text-align:left;margin-top:2rem">İlgili Tedaviler</h2>'
        '<p style="display:flex;flex-wrap:wrap;gap:1rem">%s</p>'
        '<p style="margin-top:1.4rem">Gece bastıran diş ağrısı veya acil bir durumda <a href="/gece-acik-dis-klinigi-konya/">Konya gece açık nöbetçi diş hekimi</a> hizmetimizden yararlanabilirsiniz.</p>'
        '%s</div></div>'
        % (web(t["img"]), t["title"], t["desc"], t["candidates"], proc, pts, related_html, cta())
    )
    ROUTES.append(page(
        "/tedaviler/%s/" % t["slug"], "treatments",
        T_TITLE[t["slug"]], T_DESC[t["slug"]], t["title"], content,
        [breadcrumb([("Ana Sayfa", "/"), ("Tedaviler", "/tedaviler/"), (t["title"], "/tedaviler/%s/" % t["slug"])]),
         {"@type": "MedicalProcedure", "@id": ORIGIN + "/tedaviler/%s/#procedure" % t["slug"],
          "name": t["title"], "description": t["desc"],
          "url": ORIGIN + "/tedaviler/%s/" % t["slug"],
          "provider": ORG_REF, "howPerformed": " ".join(s[0] for s in t["process"])}],
        "/tedaviler/",
        og_img=ORIGIN + "/assets/treatments/" + t["img"], og_type="article"))

# ============================================================ GECE AÇIK / ACİL
BRANCHES = [
    {"slug": "karatay", "name": "Karatay", "tel": "0546 733 27 13", "telraw": "+905467332713",
     "addr": "Çimenlik Mah. Fetih Cad. No:268A, Karatay / Konya",
     "street": "Çimenlik Mah. Fetih Cad. No:268A", "locality": "Karatay",
     "map": "https://www.google.com/maps?q=%C3%87imenlik+Mah.+Fetih+Cad.+No:268A+Karatay+Konya&output=embed"},
    {"slug": "selcuklu", "name": "Selçuklu", "tel": "0551 342 44 42", "telraw": "+905513424442",
     "addr": "Parsana Mah. Kaletaş Cad. Selçuker İş Merkezi D:2N-20, Selçuklu / Konya",
     "street": "Parsana Mah. Kaletaş Cad. Selçuker İş Merkezi D:2N-20", "locality": "Selçuklu",
     "map": "https://www.google.com/maps?q=Parsana+Mah.+Kaleta%C5%9F+Cad.+Sel%C3%A7uker+%C4%B0%C5%9F+Merkezi+Sel%C3%A7uklu+Konya&output=embed"},
    {"slug": "meram", "name": "Meram", "tel": "0552 599 49 59", "telraw": "+905525994959",
     "addr": "Melikşah Mah. Akkonak Sk. No:4/1, Meram / Konya",
     "street": "Melikşah Mah. Akkonak Sk. No:4/1", "locality": "Meram",
     "map": "https://www.google.com/maps?q=Melik%C5%9Fah+Mah.+Akkonak+Sk.+No:4+Meram+Konya&output=embed"},
]

def call_card(b, note=""):
    return ('<a href="tel:%s" class="btn btn-emergency emergency-branch-btn">'
            '<span class="ebb-label"><small>%s%s</small><strong>%s</strong></span></a>'
            % (b["telraw"], b["name"], note, b["tel"]))

WA_SVG = ('<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 .5C7.4.5.5 7.4.5 16c0 2.8.7 5.5 2.1 7.9L.5 31.5l7.8-2c2.3 1.3 4.9 1.9 7.7 1.9 8.6 0 15.5-6.9 15.5-15.5S24.6.5 16 .5zm0 28.3c-2.5 0-4.9-.7-7-1.9l-.5-.3-4.6 1.2 1.2-4.5-.3-.5c-1.4-2.2-2.1-4.7-2.1-7.3C2.6 8.6 8.6 2.6 16 2.6c3.6 0 6.9 1.4 9.5 3.9 2.5 2.5 3.9 5.9 3.9 9.5 0 7.4-6 13.4-13.4 13.4zm7.4-9.9c-.4-.2-2.4-1.2-2.7-1.3-.4-.1-.6-.2-.9.2-.3.4-1 1.3-1.2 1.5-.2.2-.4.3-.8.1-.4-.2-1.7-.6-3.3-2-1.2-1.1-2-2.4-2.3-2.8-.2-.4 0-.6.2-.8.2-.2.4-.4.6-.7.2-.2.3-.4.4-.7.1-.3.1-.5 0-.7-.1-.2-.9-2.2-1.3-3-.3-.8-.7-.7-.9-.7h-.8c-.3 0-.7.1-1 .5-.4.4-1.3 1.3-1.3 3.2s1.4 3.7 1.5 3.9c.2.2 2.7 4.2 6.6 5.9.9.4 1.6.6 2.2.8.9.3 1.7.2 2.4.1.7-.1 2.4-1 2.7-1.9.3-.9.3-1.7.2-1.9-.1-.2-.3-.3-.7-.5z"/></svg>')
WA_TEXT = "?text=Merhaba%2C%20acil%20di%C5%9F%20tedavisi%20i%C3%A7in%20bilgi%20almak%20istiyorum."
WA_TEXT_GENERAL = "?text=Merhaba%2C%20randevu%20almak%20istiyorum."

def wa_card(b):
    # Per-branch WhatsApp button — routes only to this branch's number.
    return ('<a href="https://wa.me/%s%s" target="_blank" rel="noopener" '
            'class="btn btn-wa emergency-branch-btn" aria-label="%s şubesi WhatsApp">%s'
            '<span class="ebb-label"><small>%s</small><strong>WhatsApp</strong></span></a>'
            % (b["telraw"].replace("+", ""), WA_TEXT, b["name"], WA_SVG, b["name"]))

CALL_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 '
            '19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 '
            '4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 '
            '6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')

def branch_cta_group(b, note=""):
    # One branch block: name header + phone button + WhatsApp button (stacked vertically).
    # Phone and WhatsApp always belong to the SAME branch number → no cross-branch mixups.
    return ('<div class="ebb-group">'
            '<span class="ebb-branch">%s Şubesi%s</span>'
            '<a href="tel:%s" class="btn btn-emergency emergency-branch-btn">%s'
            '<span class="ebb-label"><strong>%s</strong></span></a>'
            '<a href="https://wa.me/%s%s" target="_blank" rel="noopener" '
            'class="btn btn-wa emergency-branch-btn" aria-label="%s şubesi WhatsApp">%s'
            '<span class="ebb-label"><strong>WhatsApp</strong></span></a>'
            '</div>'
            % (b["name"], note, b["telraw"], CALL_SVG, b["tel"],
               b["telraw"].replace("+", ""), WA_TEXT, b["name"], WA_SVG))

gece_faq_qa = [
    ("Konya'da gece açık diş kliniği var mı?",
     "Evet. Konya Diş Hekimi olarak Karatay, Selçuklu ve Meram şubelerimizde pazar dahil her gün gece 23:00'a kadar açığız. Gece bastıran diş ağrılarınızda nöbetçi diş hekimimiz size hizmet verir."),
    ("Gece diş ağrısı için hemen ne yapmalıyım?",
     "Ilık tuzlu su ile gargara yapın, yanağınıza dışarıdan soğuk kompres uygulayın ve hekiminizin önerdiği bir ağrı kesici alın. Kalıcı çözüm için 23:00'a kadar açık şubemizi arayın."),
    ("Acil diş tedavisi için randevu gerekir mi?",
     "Acil durumlarda kapımız açıktır; ancak bekleme süresini en aza indirmek için gelmeden önce size en yakın şubeyi aramanızı öneririz."),
    ("Hafta sonu ve pazar günü açık mısınız?",
     "Evet, cumartesi ve pazar dahil her gün 09:00–23:00 arası hizmet veriyoruz."),
]
gf_html, gf_node = faq_block("Gece Açık & Acil Diş — Sıkça Sorulanlar", gece_faq_qa)
gece_content = hero(
    "Konya Gece Açık Diş Kliniği — Nöbetçi & Acil Diş Hekimi",
    "Diş ağrısı beklemez. Pazar dahil her gün gece 23:00'a kadar acil diş tedavisi.",
    [("Ana Sayfa", "/"), ("Gece Açık & Acil", "/gece-acik-dis-klinigi-konya/")]
) + """
<div class="section"><div class="container container-narrow">
  <p>Diş ağrısı çoğu zaman en kötü anda, akşam veya gece bastırır. <strong>Konya Diş Hekimi olarak Konya'da gece açık nöbetçi diş hekimi</strong> hizmetiyle yanınızdayız: Karatay, Selçuklu ve Meram şubelerimizde <strong>pazar dahil her gün 09:00–23:00 arası</strong> acil ve planlı diş tedavileriniz için buradayız.</p>
  <h2 class="section-title" style="text-align:left;margin-top:2rem">Hangi Durumlar Acildir?</h2>
  <ul class="tm-list">
    <li>Şiddetli ve geçmeyen diş ağrısı</li>
    <li>Kırık, çatlak veya düşmüş diş</li>
    <li>Diş apsesi, şişlik ve iltihap</li>
    <li>Dolgu veya kaplamanın düşmesi</li>
    <li>Diş eti kanaması ve travma sonrası yaralanmalar</li>
  </ul>
  <h2 class="section-title" style="text-align:left;margin-top:2rem">Gece Hemen Arayın</h2>
  <div class="emergency-actions" style="margin-top:1rem">
""" + branch_cta_group(BRANCHES[1], " (Gece Nöbetçi)") + branch_cta_group(BRANCHES[0]) + branch_cta_group(BRANCHES[2]) + """
  </div>
  <p style="margin-top:1.2rem"><strong>Selçuklu şubemiz artık gece nöbetinde!</strong> Selçuklu ve çevresinde gece açık nöbetçi diş hekimi için <a href="/subeler/selcuklu/">Selçuklu Diş Kliniği</a> sayfamıza göz atın. Çağrı merkezi: <a href="tel:+904443442">444 34 42</a>.</p>
  <p>Geç saatte bastıran ağrılarda evde yapabileceklerinizi <a href="/blog/gece-dis-agrisi-ne-yapmali/">Gece Diş Ağrısı Bastığında Ne Yapmalı?</a> yazımızda anlattık.</p>
</div></div>
""" + gf_html + '<div class="section"><div class="container">' + cta("Gece geç saatte de olsa diş ağrınız mı var? Hemen arayın, yanınızdayız.") + '</div></div>'
ROUTES.append(page(
    "/gece-acik-dis-klinigi-konya/", "emergency",
    "Konya Gece Açık Diş Kliniği – 24'e Kadar Nöbetçi Diş Hekimi",
    "Konya'da gece açık nöbetçi diş hekimi. Pazar dahil her gün 23:00'a kadar acil diş tedavisi. Selçuklu, Karatay, Meram. Gece diş ağrısında hemen arayın: 444 34 42.",
    "Gece Açık & Acil Diş", gece_content,
    [breadcrumb([("Ana Sayfa", "/"), ("Gece Açık & Acil", "/gece-acik-dis-klinigi-konya/")]),
     {"@type": "MedicalClinic", "@id": ORIGIN + "/gece-acik-dis-klinigi-konya/#clinic",
      "name": "Konya Diş Hekimi – Gece Açık Nöbetçi Diş Kliniği",
      "url": ORIGIN + "/gece-acik-dis-klinigi-konya/",
      "description": "Konya'da pazar dahil her gün gece 23:00'a kadar açık nöbetçi ve acil diş hekimi hizmeti.",
      "parentOrganization": ORG_REF, "telephone": "+90-444-34-42", "priceRange": "₺₺",
      "areaServed": [{"@type": "City", "name": "Konya"}, {"@type": "AdministrativeArea", "name": "Selçuklu"}],
      "availableService": {"@type": "MedicalProcedure", "name": "Acil Diş Tedavisi"},
      "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "09:00", "closes": "23:00"}]},
     gf_node],
    "/gece-acik-dis-klinigi-konya/",
    title_en="Konya Night-Open Dental Clinic – Emergency Dentist Until Late",
    desc_en="Night-open emergency dentist in Konya. Open until 23:00 every day, Sundays included. Selçuklu, Karatay, Meram. Call now: 444 34 42."))

# ============================================================ ŞUBELER
B_TITLE = {
    "karatay": "Karatay Diş Kliniği Konya – Nöbetçi Diş Hekimi | Konya Diş Hekimi",
    "selcuklu": "Selçuklu Diş Kliniği – Gece Açık Nöbetçi Diş Hekimi | Konya Diş Hekimi",
    "meram": "Meram Diş Kliniği Konya – Diş Hekimi | Konya Diş Hekimi",
}
B_DESC = {
    "karatay": "Karatay diş kliniği Konya Diş Hekimi: Çimenlik Mah. Fetih Cad. Pazar dahil her gün 23:00'a kadar açık nöbetçi diş hekimi. Randevu: 0546 733 27 13.",
    "selcuklu": "Selçuklu'da gece açık diş kliniği. Parsana Mah. Kaletaş Cad. Pazar dahil 23:00'a kadar nöbetçi diş hekimi. Randevu ve acil: 0551 342 44 42.",
    "meram": "Meram diş kliniği Konya Diş Hekimi: Melikşah Mah. Akkonak Sk. Pazar dahil her gün 23:00'a kadar açık diş hekimi. Randevu: 0552 599 49 59.",
}
B_H1 = {
    "karatay": "Karatay Diş Kliniği — Konya Diş Hekimi",
    "selcuklu": "Selçuklu Diş Kliniği — Gece Açık Nöbetçi Diş Hekimi",
    "meram": "Meram Diş Kliniği — Konya Diş Hekimi",
}
B_SUB = {
    "karatay": "Karatay'da ağız ve diş sağlığı; pazar dahil her gün gece 23:00'a kadar açık.",
    "selcuklu": "Selçuklu'da gece nöbetçi diş hekimi; pazar dahil her gün 23:00'a kadar açık.",
    "meram": "Meram'da ağız ve diş sağlığı; pazar dahil her gün gece 23:00'a kadar açık.",
}
for b in BRANCHES:
    night = " Selçuklu şubemiz gece nöbetindedir." if b["slug"] == "selcuklu" else ""
    bfaq = [
        ("%s şubeniz kaça kadar açık?" % b["name"],
         "%s şubemiz pazar dahil her gün 09:00–23:00 arası açıktır.%s" % (b["name"], night)),
        ("%s diş kliniği randevu numarası nedir?" % b["name"],
         "%s şubemize %s numarasından ulaşabilir, randevu ve acil diş için arayabilirsiniz." % (b["name"], b["tel"])),
        ("Adresiniz ve yol tarifi nasıl?",
         "Adresimiz: %s. Sayfadaki haritadan yol tarifi alabilirsiniz." % b["addr"]),
    ]
    bf_html, bf_node = faq_block("%s Şubesi — Sıkça Sorulanlar" % b["name"], bfaq)
    content = hero(B_H1[b["slug"]], B_SUB[b["slug"]],
                   [("Ana Sayfa", "/"), ("Şubeler", "/iletisim/"), (b["name"], "/subeler/%s/" % b["slug"])]) + (
        '<div class="section"><div class="container">'
        '<div class="branch-card reveal" style="max-width:760px;margin:0 auto">'
        '<div class="branch-map map-facade" data-map="%s" role="button" tabindex="0" aria-label="%s Şubesi haritasını görüntüle">'
        '<div class="map-facade-content"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg><span>Haritayı Görüntüle</span></div></div>'
        '<div class="branch-body">'
        '<h2 style="margin-bottom:1rem">%s Şubesi</h2>'
        '<p class="branch-addr"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>%s</p>'
        '<p class="branch-phone"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg><a href="tel:%s">%s</a></p>'
        '<p class="branch-addr"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>Pazar dahil her gün 09:00 – 23:00</p>'
        '<a href="https://wa.me/%s%s" class="branch-link" target="_blank" rel="noopener">WhatsApp ile İletişim &rarr;</a></div></div>'
        '<div class="container container-narrow" style="margin-top:2.4rem">'
        '<p>%s şubemiz, güvenle ağız ve diş sağlığınız için hizmetinizdedir. İmplant, gülüş estetiği, ortodonti, kanal tedavisi ve çocuk diş hekimliği dahil tüm tedavilerimiz bu şubemizde sunulur. %s</p>'
        '<p>Gece bastıran acil durumlar için <a href="/gece-acik-dis-klinigi-konya/">Konya gece açık nöbetçi diş hekimi</a> sayfamıza bakabilirsiniz.</p>'
        '</div></div></div>'
        % (b["map"], b["name"], b["name"], b["addr"], b["telraw"], b["tel"], b["telraw"].replace("+", ""), WA_TEXT_GENERAL, b["name"],
           ("Selçuklu ve çevresinde gece geç saatte diş hekimi arayanlar için nöbet hizmeti veririz." if b["slug"] == "selcuklu" else "Pazar dahil her gün geç saatlere kadar açığız."))
    ) + bf_html + '<div class="section"><div class="container">' + cta() + '</div></div>'
    dentist_node = {
        "@type": "Dentist", "@id": ORIGIN + "/subeler/%s/#dentist" % b["slug"],
        "name": "Konya Diş Hekimi Kliniği - %s" % b["name"], "url": ORIGIN + "/subeler/%s/" % b["slug"],
        "telephone": b["telraw"], "priceRange": "₺₺", "parentOrganization": ORG_REF,
        "image": ORIGIN + "/assets/hero/hero1.jpg",
        "medicalSpecialty": "Dentistry",
        "address": {"@type": "PostalAddress", "streetAddress": b["street"],
                    "addressLocality": b["locality"], "addressRegion": "Konya", "addressCountry": "TR"},
        "areaServed": {"@type": "AdministrativeArea", "name": b["locality"]},
        "hasMap": b["map"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "09:00", "closes": "23:00"}],
    }
    if b["slug"] == "selcuklu":
        dentist_node["description"] = "Selçuklu'da gece açık nöbetçi diş hekimi. Pazar dahil her gün 23:00'a kadar acil ve planlı diş tedavisi."
    ROUTES.append(page(
        "/subeler/%s/" % b["slug"], "contact",
        B_TITLE[b["slug"]], B_DESC[b["slug"]], B_H1[b["slug"]], content,
        [breadcrumb([("Ana Sayfa", "/"), ("Şubeler", "/iletisim/"), (b["name"], "/subeler/%s/" % b["slug"])]),
         dentist_node, bf_node],
        None))

# ============================================================ BLOG
BLOG = [
    {"slug": "konya-gece-acik-dis-klinigi-nasil-bulunur", "cat": "Gece & Acil",
     "title": "Konya'da Gece Açık Diş Kliniği Nasıl Bulunur?",
     "kw": "Konya gece açık diş kliniği",
     "excerpt": "Gece bastıran diş ağrısında Konya'da açık klinik aramak zaman kaybettirir. Doğru kliniği hızlıca bulmanın yolları ve dikkat etmeniz gerekenler.",
     "date": "2026-06-26", "read": 5, "img": "kanal-tedavisi.jpg",
     "body": """<p>Diş ağrısı çoğunlukla mesai saatleri dışında, akşam ve gece bastırır. Bu saatlerde Konya'da açık bir diş kliniği bulmak hem zor hem de stresli olabilir. Doğru yeri hızlı bulmak, ağrının uzamasını ve durumun ciddileşmesini önler.</p>
<h2>Gece Açık Klinik Ararken Nelere Dikkat Etmeli?</h2>
<ul>
<li><strong>Çalışma saatlerini doğrulayın:</strong> "Gece açık" ifadesi her klinikte aynı saati ifade etmez. Kliniğin kaça kadar açık olduğunu telefonla teyit edin.</li>
<li><strong>Hafta sonu durumunu sorun:</strong> Pazar günü açık olup olmadığı acil durumlarda kritiktir.</li>
<li><strong>Konum ve şube sayısı:</strong> Size en yakın şube, geç saatte ulaşımı kolaylaştırır.</li>
<li><strong>Acil müdahale kapasitesi:</strong> Kanal, çekim, apse drenajı gibi işlemlerin yapılabildiğini öğrenin.</li>
</ul>
<h2>Konya Diş Hekimi: Pazar Dahil Her Gün 23:00'a Kadar</h2>
<p>Konya Diş Hekimi olarak Karatay, Selçuklu ve Meram şubelerimizde <strong>pazar dahil her gün gece 23:00'a kadar</strong> hizmet veriyoruz. Geç saatte bastıran ağrılarda <a href="/gece-acik-dis-klinigi-konya/">Konya gece açık nöbetçi diş hekimi</a> hizmetimizle yanınızdayız. Ağrı dayanılmazsa beklemeyin; önce <a href="/blog/gece-dis-agrisi-ne-yapmali/">gece diş ağrısı bastığında ne yapmalı</a> yazımızdaki pratik önerilere göz atın, ardından bizi arayın. Çağrı merkezi: 444 34 42.</p>"""},
    {"slug": "acil-dis-tedavisi-gerektiren-durumlar", "cat": "Gece & Acil",
     "title": "Acil Diş Tedavisi Gerektiren 7 Durum",
     "kw": "acil diş tedavisi Konya",
     "excerpt": "Her diş problemi acil değildir; ancak bazı durumlar saatler içinde müdahale ister. Vakit kaybetmeden hekime başvurmanız gereken 7 belirti.",
     "date": "2026-06-22", "read": 5, "img": "cerrahi.jpg",
     "body": """<p>Bazı diş sorunları birkaç gün bekleyebilirken, bazıları saatler içinde müdahale gerektirir. Aşağıdaki durumlardan biriyle karşılaşıyorsanız vakit kaybetmeden bir diş hekimine başvurmalısınız.</p>
<h2>Hemen Hekime Gitmeniz Gereken Durumlar</h2>
<ul>
<li><strong>Şiddetli, geçmeyen diş ağrısı:</strong> Ağrı kesiciye yanıt vermeyen ağrı, iltihabın ilerlediğine işaret olabilir.</li>
<li><strong>Yüzde veya yanakta şişlik:</strong> Apse belirtisi olabilir; ciddiye alınmalıdır.</li>
<li><strong>Diş kırılması veya yerinden çıkması:</strong> İlk saatler tedavi başarısı için kritiktir.</li>
<li><strong>Durmayan diş eti veya soket kanaması:</strong> Özellikle çekim sonrası uzun süren kanama.</li>
<li><strong>Dolgu veya kaplamanın düşmesi:</strong> Açıkta kalan diş hızla hassaslaşır ve enfekte olabilir.</li>
<li><strong>Çenede kilitlenme veya açma-kapama güçlüğü:</strong> Eklem veya enfeksiyon kaynaklı olabilir.</li>
<li><strong>Ateşle birlikte diş ağrısı:</strong> Yayılan enfeksiyon işareti olabilir.</li>
</ul>
<h2>Geciktirmek Neden Riskli?</h2>
<p>Diş enfeksiyonları kendiliğinden geçmez; tedavi edilmediğinde komşu dokulara ve hatta çene kemiğine yayılabilir. Bu durumlarda <a href="/gece-acik-dis-klinigi-konya/">gece açık diş kliniği</a> hizmetimizden yararlanabilirsiniz. Diş kırığında ne yapmanız gerektiğini <a href="/blog/dis-kirildiginda-ilk-bir-saat/">diş kırıldığında ilk 1 saat</a> yazımızda anlattık. Acil durumda <a href="/iletisim/">bize ulaşın</a>.</p>"""},
    {"slug": "nobetci-dis-hekimi-ne-zaman-aranmali", "cat": "Gece & Acil",
     "title": "Nöbetçi Diş Hekimi Ne Zaman Aranmalı?",
     "kw": "nöbetçi diş hekimi Konya",
     "excerpt": "Nöbetçi diş hekimi her durumda gerekli midir? Hangi şikâyetlerde geceyi beklemeden aramalı, hangilerinde sabahı bekleyebilirsiniz?",
     "date": "2026-06-18", "read": 4, "img": "kanal-tedavisi.jpg",
     "body": """<p>Diş sorunları gece de gündüz de ortaya çıkabilir. Peki hangi durumlarda nöbetçi/gece açık bir diş hekimini aramak gerekir, hangilerinde ertesi günü beklemek güvenlidir?</p>
<h2>Geceyi Beklemeden Aramanız Gereken Durumlar</h2>
<ul>
<li>Uyku düzeninizi bozan, dinmeyen şiddetli ağrı</li>
<li>Hızla büyüyen şişlik veya apse</li>
<li>Travma sonrası kırılan ya da yerinden oynayan diş</li>
<li>Durmayan kanama</li>
</ul>
<h2>Sabahı Bekleyebilecek Durumlar</h2>
<p>Hafif hassasiyet, küçük bir çatlak, takılıp kalan yemek artığı gibi sorunlar genellikle ertesi gün planlı muayene ile çözülebilir. Yine de emin değilseniz aramaktan çekinmeyin; doğru yönlendirmeyi telefonda alabilirsiniz.</p>
<p>kliniğimizde <strong>pazar dahil her gün 23:00'a kadar</strong> hizmet veriyoruz. Şüpheniz olduğunda <a href="/gece-acik-dis-klinigi-konya/">nöbetçi diş hekimi</a> hattımızı arayın; durumunuz acil değilse de size en uygun randevu saatini ayarlayalım. <a href="/iletisim/">İletişim bilgilerimize buradan</a> ulaşabilirsiniz.</p>"""},
    {"slug": "pazar-acik-dis-hekimi-konya", "cat": "Gece & Acil",
     "title": "Hafta Sonu ve Pazar Açık Diş Hekimi (Konya)",
     "kw": "pazar açık diş hekimi Konya",
     "excerpt": "Hafta sonu bastıran diş ağrısı için Konya'da pazar günü açık diş hekimi arıyorsanız, bilmeniz gereken her şey bu yazıda.",
     "date": "2026-06-14", "read": 4, "img": "implant.jpg",
     "body": """<p>Diş ağrısı hafta sonu tanımaz. Birçok klinik cumartesi öğleden sonra ve pazar günü kapalıdır; bu da hafta sonu bastıran ağrılarda hasta için zor saatler demektir.</p>
<h2>Hafta Sonu Diş Hekimi Neden Önemli?</h2>
<p>Cuma akşamı başlayan bir ağrı, pazartesiye kadar beklediğinde küçük bir çürük büyük bir enfeksiyona dönüşebilir. Erken müdahale hem ağrıyı kısaltır hem de daha kapsamlı (ve maliyetli) tedavilerin önüne geçer.</p>
<h2>kliniğimizde Hafta Sonu</h2>
<ul>
<li>Cumartesi ve <strong>pazar dahil</strong> her gün açığız.</li>
<li>Çalışma saatimiz gece <strong>23:00</strong>'a kadar uzar.</li>
<li>Karatay, Selçuklu ve Meram şubelerimizle şehrin farklı noktalarından kolay ulaşım.</li>
</ul>
<p>Hafta sonu acil bir durumda <a href="/gece-acik-dis-klinigi-konya/">gece açık diş kliniği</a> sayfamızı inceleyebilir, size en yakın <a href="/subeler/selcuklu/">şubemize</a> ulaşabilirsiniz. Detaylı bilgi için <a href="/iletisim/">bizi arayın</a>: 444 34 42.</p>"""},
    {"slug": "dis-kirildiginda-ilk-bir-saat", "cat": "Gece & Acil",
     "title": "Diş Kırıldığında İlk 1 Saatte Yapılması Gerekenler",
     "kw": "kırık diş acil ne yapmalı",
     "excerpt": "Düşme veya darbe sonrası kırılan dişte ilk bir saat, dişin kurtarılması için en kritik zamandır. Adım adım ne yapmanız gerektiği burada.",
     "date": "2026-06-10", "read": 5, "img": "cerrahi.jpg",
     "body": """<p>Spor, düşme veya sert bir gıda; diş kırıkları beklenmedik anda olur. İyi haber şu: hızlı ve doğru davranırsanız kırılan ya da yerinden çıkan dişin kurtulma şansı yüksektir. İlk bir saat belirleyicidir.</p>
<h2>Diş Tamamen Yerinden Çıktıysa</h2>
<ul>
<li>Dişi <strong>kron (taç) kısmından</strong> tutun, köküne dokunmayın.</li>
<li>Kirliyse sadece süt veya tuzlu su ile nazikçe durulayın, ovalamayın.</li>
<li>Mümkünse dişi <strong>yerine yerleştirmeyi</strong> deneyin; olmuyorsa süt içinde veya yanağınızın iç kısmında saklayın.</li>
<li>En geç 1 saat içinde diş hekimine ulaşın.</li>
</ul>
<h2>Diş Sadece Kırıldıysa</h2>
<p>Kırılan parçayı saklayın, bölgeyi ılık suyla durulayın, şişlik için yanağa dışarıdan soğuk uygulayın. Keskin kenar dilinizi rahatsız ediyorsa eczane mumu ile geçici olarak kapatabilirsiniz.</p>
<p>Her iki durumda da kalıcı çözüm hekim müdahalesidir. <strong>Pazar dahil her gün 23:00'a kadar</strong> açık olduğumuz için travma sonrası <a href="/gece-acik-dis-klinigi-konya/">nöbetçi diş hekimi</a> hizmetimizle hemen yanınızdayız. Diğer <a href="/blog/acil-dis-tedavisi-gerektiren-durumlar/">acil durumları</a> da inceleyin; gerektiğinde <a href="/iletisim/">bizi arayın</a>.</p>"""},
    {"slug": "dis-apsesi-tehlikeli-mi", "cat": "Gece & Acil",
     "title": "Diş Apsesi Tehlikeli mi? Belirtiler ve Acil Müdahale",
     "kw": "diş apsesi acil",
     "excerpt": "Diş apsesi yalnızca ağrı değil, yayılabilen ciddi bir enfeksiyondur. Belirtilerini tanıyın ve ne zaman acil müdahale gerektiğini öğrenin.",
     "date": "2026-06-06", "read": 5, "img": "kanal-tedavisi.jpg",
     "body": """<p>Diş apsesi, diş ya da diş eti çevresinde biriken iltihaplı bir enfeksiyondur. Göz ardı edildiğinde komşu dokulara, çeneye ve nadiren tüm vücuda yayılabilir. Bu yüzden ciddiye alınması gereken bir durumdur.</p>
<h2>Apse Belirtileri</h2>
<ul>
<li>Zonklayıcı, yayılan şiddetli diş ağrısı</li>
<li>Yüz, yanak veya diş etinde şişlik</li>
<li>Sıcak-soğuğa ve çiğnemeye karşı hassasiyet</li>
<li>Ağızda kötü tat, ağız kokusu</li>
<li>Ateş ve halsizlik (yayılan enfeksiyon işareti)</li>
</ul>
<h2>Ne Zaman Acil?</h2>
<p>Ateş, yutkunma veya nefes almada güçlük, hızla büyüyen şişlik varsa bu <strong>acil</strong> bir durumdur ve beklemeden müdahale gerektirir. Apse kendiliğinden patlasa bile enfeksiyon devam eder; mutlaka tedavi edilmelidir.</p>
<p>Tedavi genellikle drenaj ve ardından <a href="/tedaviler/kanal-tedavisi/">kanal tedavisi</a> ya da gerekiyorsa çekimle yapılır. Apse şüphesinde <strong>pazar dahil her gün 23:00'a kadar</strong> açık olan kliniğimize başvurabilirsiniz. <a href="/gece-acik-dis-klinigi-konya/">Gece açık diş kliniği</a> hizmetimiz için <a href="/iletisim/">bize ulaşın</a>.</p>"""},
    {"slug": "selcuklu-dis-hekimi-secimi", "cat": "Yerel Rehber",
     "title": "Selçuklu'da Diş Hekimi Seçerken Dikkat Edilmesi Gerekenler",
     "kw": "Selçuklu diş hekimi",
     "excerpt": "Selçuklu'da doğru diş hekimini seçmek, tedavi başarısı kadar güveni de belirler. Karar verirken göz önünde bulundurmanız gereken kriterler.",
     "date": "2026-06-02", "read": 5, "img": "gulus-estetigi.jpg",
     "body": """<p>Selçuklu, Konya'nın en yoğun ilçelerinden biri ve diş hekimi seçeneği oldukça fazla. Doğru tercih, hem tedavinin kalitesini hem de uzun vadeli ağız sağlığınızı etkiler.</p>
<h2>Karar Verirken Bakmanız Gerekenler</h2>
<ul>
<li><strong>Hekim ve klinik deneyimi:</strong> Uygulanan tedavi çeşitliliği ve uzmanlık alanları.</li>
<li><strong>Hijyen ve sterilizasyon:</strong> Klinik temizliği pazarlık konusu olmamalı.</li>
<li><strong>Şeffaf bilgilendirme:</strong> Tedavi planı, alternatifler ve süreç açıkça anlatılmalı.</li>
<li><strong>Ulaşım ve çalışma saatleri:</strong> Acil durumda geç saatte açık olması büyük avantaj.</li>
<li><strong>Hasta yorumları:</strong> Gerçek hasta deneyimleri fikir verir.</li>
</ul>
<h2>Selçuklu Şubemiz</h2>
<p>Konya Diş Hekimi Selçuklu şubemizde implanttan ortodontiye, gülüş estetiğinden çocuk diş hekimliğine kadar tüm tedaviler tek çatı altında sunulur. Üstelik <strong>pazar dahil her gün 23:00'a kadar</strong> açığız. <a href="/subeler/selcuklu/">Selçuklu şubemizin</a> konum ve iletişim bilgilerine ulaşabilir, <a href="/iletisim/">bizimle iletişime geçebilirsiniz</a>. Kliniğimiz hakkında daha fazlası için <a href="/hakkimizda/">Hakkımızda</a> sayfamıza bakın.</p>"""},
    {"slug": "24-saat-gec-saat-dis-hekimi-sss", "cat": "Gece & Acil",
     "title": "Geç Saat Açık Diş Hekimi Hakkında Merak Edilenler",
     "kw": "24 saat diş hekimi Konya",
     "excerpt": "Geç saatte açık diş hekimi hizmeti nasıl işler, hangi tedaviler yapılır, ücretlendirme farklı mıdır? Sık sorulan soruları yanıtladık.",
     "date": "2026-05-30", "read": 4, "img": "implant.jpg",
     "body": """<p>Geç saatte açık diş hekimi hizmeti, mesai sonrası ve hafta sonu bastıran problemlerde büyük rahatlık sağlar. Bu hizmetle ilgili en sık sorulan soruları yanıtladık.</p>
<h2>Sık Sorulan Sorular</h2>
<ul>
<li><strong>Geç saatte hangi işlemler yapılır?</strong> Ağrı kontrolü, apse drenajı, kanal tedavisi, çekim, geçici dolgu gibi acil müdahalelerin çoğu yapılabilir.</li>
<li><strong>Randevusuz gidebilir miyim?</strong> Acil durumda önce aramanız, hem hekimin hazır olmasını hem de bekleme süresini kısaltır.</li>
<li><strong>Gece ücreti farklı mı?</strong> Tedavi ücretleri işlemin türüne göre belirlenir; süreç öncesinde net bilgilendirme yapılır.</li>
<li><strong>Çocuğum için de geçerli mi?</strong> Evet, çocuk acil diş durumlarında da hizmet veriyoruz.</li>
</ul>
<p>Konya Diş Hekimi olarak <strong>pazar dahil her gün 23:00'a kadar</strong> açığız. Tedavi ücretlerinin neye göre belirlendiğini <a href="/blog/konya-dis-tedavi-fiyatlari/">Konya'da diş tedavisi fiyatları</a> yazımızda anlattık. Acil bir durumunuzda <a href="/gece-acik-dis-klinigi-konya/">gece açık diş kliniği</a> hattımızı arayın ya da <a href="/iletisim/">iletişim sayfamızdan</a> bize ulaşın.</p>"""},
    {"slug": "implant-sonrasi-bakim", "cat": "İmplant",
     "title": "İmplant Tedavisi Sonrası Bakım: 7 Altın Kural",
     "kw": "implant sonrası bakım",
     "excerpt": "İmplantınızın ömrünü uzatmak büyük ölçüde işlem sonrası bakıma bağlı. İlk günlerden uzun vadeye dikkat etmeniz gereken her şey.",
     "date": "2026-05-28", "read": 5, "img": "implant.jpg",
     "body": """<p>Diş implantı, doğru bakıldığında ömür boyu kullanılabilen kalıcı bir çözümdür. Tedavinin başarısı yalnızca cerrahi aşamaya değil, sonrasındaki bakıma da bağlıdır. İşte implant sonrası dikkat etmeniz gereken altın kurallar.</p>
<h2>İlk 24-48 Saat</h2>
<p>İşlemden hemen sonra bölgeye soğuk kompres uygulamak şişliği azaltır. İlk gün sigara ve alkolden uzak durun, çok sıcak yiyecek-içeceklerden kaçının ve hekiminizin önerdiği ilaçları düzenli kullanın.</p>
<h2>Uzun Vadede Dikkat Edilmesi Gerekenler</h2>
<ul>
<li>Günde en az iki kez, yumuşak fırça ile nazikçe fırçalama yapın.</li>
<li>İmplant çevresini ara yüz fırçası veya diş ipi ile temizleyin.</li>
<li>Çok sert yiyecekleri (ceviz kırma vb.) implant bölgesinde kullanmayın.</li>
<li>Sigarayı bırakın; sigara implant kaybının en büyük nedenlerindendir.</li>
<li>6 ayda bir kontrol ve profesyonel temizlik için hekiminize gidin.</li>
</ul>
<p>Unutmayın: İmplantlar çürümez ama çevresindeki diş eti hastalanabilir. Düzenli bakım, implantınızın ömrünü doğrudan belirler. Herhangi bir hassasiyet veya kanama fark ederseniz vakit kaybetmeden <a href="/iletisim/">bizimle iletişime geçin</a>. <a href="/tedaviler/implant/">İmplant tedavisi</a> hakkında daha fazla bilgi alabilirsiniz.</p>"""},
    {"slug": "cocuk-ilk-dis-kontrolu", "cat": "Pedodonti",
     "title": "Çocuğumu İlk Diş Kontrolüne Ne Zaman Götürmeliyim?",
     "kw": "çocuk ilk diş kontrolü",
     "excerpt": "Erken başlayan diş kontrolleri, çocuğunuzun ömür boyu sağlıklı dişlere sahip olmasının temelini atar. İşte bilmeniz gerekenler.",
     "date": "2026-05-20", "read": 4, "img": "pedodonti.jpg",
     "body": """<p>Birçok ebeveyn, çocuğunu diş hekimine ne zaman götüreceği konusunda kararsız kalır. Oysa erken tanışma, hem korkuyu önler hem de olası problemleri başlamadan durdurur.</p>
<h2>İlk Ziyaret: 1 Yaş</h2>
<p>Uzmanlar, ilk diş çıktıktan sonra ya da en geç 1 yaşına kadar ilk diş hekimi kontrolünün yapılmasını önerir. Bu ziyaret çoğunlukla bir muayene ve ebeveyne yönelik bilgilendirme şeklinde geçer.</p>
<h2>Neden Bu Kadar Önemli?</h2>
<ul>
<li>Çürükler henüz başlamadan koruyucu önlemler alınır (flor, fissür örtücü).</li>
<li>Çocuk, diş hekimi ortamına korkmadan alışır.</li>
<li>Çene ve diş gelişimi erkenden takip edilir.</li>
<li>Doğru fırçalama ve beslenme alışkanlıkları kazandırılır.</li>
</ul>
<p><a href="/tedaviler/cocuk-dis-hekimligi/">KDH Çocuk kliniğimizde</a>, minik hastalarımıza özel, neşeli ve korkutmayan bir ortam sunuyoruz. Çocuğunuzun ilk diş deneyimini keyifli bir maceraya dönüştürüyoruz.</p>"""},
    {"slug": "gulus-tasarimi-nedir", "cat": "Estetik",
     "title": "Gülüş Tasarımı Nedir? Kimler İçin Uygundur?",
     "kw": "gülüş tasarımı Konya",
     "excerpt": "Gülüş tasarımı sadece beyaz dişler değildir; yüzünüze özel, doğal ve simetrik bir gülümsemenin bütüncül planıdır.",
     "date": "2026-05-12", "read": 6, "img": "gulus-estetigi.jpg",
     "body": """<p>Gülüş tasarımı; diş rengi, formu, dizilimi ve diş eti çizgisinin yüz hatlarınızla uyumlu olacak şekilde yeniden planlanmasıdır. Amaç, "yapay" değil, size en doğal şekilde yakışan gülümsemeyi oluşturmaktır.</p>
<h2>Hangi Yöntemler Kullanılır?</h2>
<ul>
<li><strong>Lamina (Yaprak Porselen):</strong> Dişin ön yüzeyine uygulanan ince porselen tabakalar.</li>
<li><strong>Zirkonyum Kaplama:</strong> Metal içermeyen, doğal ışık geçirgenliğine sahip kaplamalar.</li>
<li><strong>Diş Beyazlatma:</strong> Renklenmeleri gidererek daha parlak bir görünüm.</li>
<li><strong>Diş Eti Estetiği:</strong> Gülümsemede diş eti oranının düzenlenmesi.</li>
</ul>
<h2>Kimler İçin Uygundur?</h2>
<p>Dişlerinin renginden, formundan veya diziliminden memnun olmayan; kırık, aşınmış ya da aralıklı dişleri olan herkes aday olabilir. İşlem öncesi dijital planlama ile sonucu önceden görebilirsiniz. Detaylar için <a href="/tedaviler/gulus-estetigi/">gülüş estetiği</a> sayfamıza göz atın.</p>
<p>Unutmayın, en iyi gülüş tasarımı kişiye özeldir. Hekiminizle yapacağınız ön görüşmede beklentilerinizi paylaşmanız, sonucun memnuniyetini doğrudan etkiler.</p>"""},
    {"slug": "gece-dis-agrisi-ne-yapmali", "cat": "Acil",
     "title": "Gece Diş Ağrısı Bastığında Ne Yapmalı?",
     "kw": "gece diş ağrısı tedavisi Konya",
     "excerpt": "Diş ağrısı çoğu zaman en kötü anda, gece bastırır. Hekime ulaşana kadar ağrıyı hafifletecek pratik ve güvenli öneriler.",
     "date": "2026-05-03", "read": 4, "img": "kanal-tedavisi.jpg",
     "body": """<p>Ani gelişen diş ağrısı, özellikle gece saatlerinde dayanılmaz olabilir. Kalıcı çözüm mutlaka bir diş hekimi muayenesidir; ancak hekime ulaşana kadar ağrıyı hafifletmek için yapabilecekleriniz var.</p>
<h2>Evde Yapabilecekleriniz</h2>
<ul>
<li>Ilık tuzlu su ile ağzınızı çalkalayın; bu, bölgedeki bakterileri azaltır.</li>
<li>Yanağınıza dışarıdan soğuk kompres uygulayın (doğrudan dişe değil).</li>
<li>Hekiminizin daha önce önerdiği bir ağrı kesiciyi kullanabilirsiniz.</li>
<li>Ağrıyan bölgeyi diş ipiyle nazikçe temizleyin; sıkışmış gıda ağrı yapabilir.</li>
<li>Aspirini doğrudan diş etine koymayın; dokuya zarar verir.</li>
</ul>
<h2>Beklemeyin, Bizi Arayın</h2>
<p>Bu öneriler geçici rahatlama sağlar; ağrının nedeni devam ediyordur. İyi haber şu: <strong>Konya Diş Hekimi olarak pazar dahil her gün gece 23:00'a kadar açığız.</strong> Geç saatte bastıran diş ağrılarınızda <a href="/gece-acik-dis-klinigi-konya/">nöbetçi diş hekimi</a> hizmetimizle yanınızdayız. Çağrı merkezi: 444 34 42.</p>"""},
    {"slug": "dis-implanti-kimlere-uygun", "cat": "İmplant",
     "title": "Diş İmplantı Kimlere Uygundur?",
     "kw": "implant Konya",
     "excerpt": "Diş implantı eksik dişlerin en kalıcı çözümüdür; peki herkese uygulanabilir mi? İmplant için uygunluğu belirleyen faktörler.",
     "date": "2026-04-28", "read": 5, "img": "implant.jpg",
     "body": """<p>Diş implantı, eksik dişin yerine çene kemiğine yerleştirilen titanyum bir vida ve üzerine yapılan protezden oluşur. Doğal dişe en yakın çözüm olması nedeniyle giderek daha çok tercih edilir. Ancak her hasta için planlama bireyseldir.</p>
<h2>İmplant İçin Genellikle Uygun Adaylar</h2>
<ul>
<li>Bir veya birden fazla dişi eksik olan yetişkinler</li>
<li>Çene kemiği gelişimini tamamlamış kişiler</li>
<li>Genel sağlığı implant cerrahisine uygun olanlar</li>
<li>Ağız hijyenine özen gösterebilecek hastalar</li>
</ul>
<h2>Dikkat Gerektiren Durumlar</h2>
<p>Kontrolsüz diyabet, ağır diş eti hastalığı, yoğun sigara kullanımı ve yetersiz kemik hacmi süreci etkileyebilir. Bu durumlarda ön hazırlık (örneğin kemik grefti) veya alternatif planlar değerlendirilir. Yani "uygun değilim" demek için acele etmeyin; doğru muayene ile çoğu engel aşılabilir.</p>
<p>Sizin için en doğru planı belirlemek üzere <a href="/tedaviler/implant/">implant tedavisi</a> sayfamızı inceleyebilir, <a href="/iletisim/">ücretsiz değerlendirme için bize ulaşabilirsiniz</a>. İmplant ve köprü arasında kararsızsanız <a href="/blog/implant-mi-kopru-mu/">implant mı köprü mü</a> yazımız yardımcı olacaktır.</p>"""},
    {"slug": "implant-mi-kopru-mu", "cat": "İmplant",
     "title": "İmplant mı Köprü mü? Avantaj ve Dezavantajlar",
     "kw": "implant mı köprü mü",
     "excerpt": "Eksik diş için implant ve köprü en sık önerilen iki çözümdür. Hangisinin size daha uygun olduğunu belirleyen farkları karşılaştırdık.",
     "date": "2026-04-21", "read": 6, "img": "implant.jpg",
     "body": """<p>Eksik bir dişi tamamlamanın iki yaygın yolu vardır: implant ve köprü. İkisi de işlevseldir, ancak uzun vadeli sonuçları ve gereksinimleri farklıdır.</p>
<h2>İmplantın Avantajları</h2>
<ul>
<li>Komşu sağlam dişlere dokunulmaz.</li>
<li>Çene kemiğini uyararak erimeyi önler.</li>
<li>Doğru bakımla ömür boyu kullanılabilir.</li>
</ul>
<h2>Köprünün Avantajları</h2>
<ul>
<li>Daha kısa sürede tamamlanır.</li>
<li>Cerrahi işlem gerektirmez.</li>
<li>Başlangıç maliyeti genellikle daha düşüktür.</li>
</ul>
<p>Köprünün en önemli dezavantajı, iki yanındaki sağlam dişlerin küçültülmesi gerekliliğidir. İmplant ise daha yüksek başlangıç yatırımı ister ama uzun vadede genellikle daha avantajlıdır. Karar; kemik durumu, komşu dişlerin sağlığı ve beklentilerinize göre verilir.</p>
<p>Hangisinin size uygun olduğunu netleştirmek için <a href="/tedaviler/implant/">implant tedavisi</a> sayfamıza göz atın ve <a href="/iletisim/">muayene için bize ulaşın</a>. İmplantın kimlere uygun olduğunu <a href="/blog/dis-implanti-kimlere-uygun/">bu yazıda</a> ele aldık.</p>"""},
    {"slug": "implant-tedavisi-ne-kadar-surer", "cat": "İmplant",
     "title": "İmplant Tedavisi Ne Kadar Sürer?",
     "kw": "implant tedavi süresi",
     "excerpt": "İmplant tedavisi tek seansta bitmez; iyileşme süreci dişin sağlamlığını belirler. Aşama aşama implant tedavisinin süresi.",
     "date": "2026-04-14", "read": 5, "img": "implant.jpg",
     "body": """<p>İmplant tedavisinin toplam süresi kişiden kişiye değişir. Cerrahi aşama kısa sürse de, implantın kemiğe kaynaması (osseointegrasyon) zaman ister ve tedavinin başarısı büyük ölçüde bu sürece bağlıdır.</p>
<h2>Tedavi Aşamaları</h2>
<ul>
<li><strong>Planlama ve muayene:</strong> Radyografi ve ölçümlerle 1 randevu.</li>
<li><strong>İmplant yerleştirme:</strong> Genellikle 30-60 dakikalık tek seans.</li>
<li><strong>İyileşme (kaynama):</strong> Alt çenede ~2-3 ay, üst çenede ~3-4 ay.</li>
<li><strong>Protez aşaması:</strong> Ölçü alınıp kron hazırlanması 1-2 hafta.</li>
</ul>
<p>Kemik grefti gerekiyorsa süreç birkaç ay uzayabilir. Bazı uygun vakalarda "hemen yükleme" ile geçici diş aynı gün takılabilir; bu kararı hekiminiz verir.</p>
<p>Süreç uzun görünse de sonuç kalıcıdır. <a href="/tedaviler/implant/">İmplant tedavisi</a> hakkında detaylı bilgi alabilir, kişisel zaman planınız için <a href="/iletisim/">bize ulaşabilirsiniz</a>. Tedavi sonrası bakımı <a href="/blog/implant-sonrasi-bakim/">implant sonrası bakım</a> yazımızda anlattık.</p>"""},
    {"slug": "all-on-4-nedir", "cat": "İmplant",
     "title": "All-on-4 Nedir? Tam Dişsizlikte Sabit Çözüm",
     "kw": "all on 4 Konya",
     "excerpt": "Tüm dişleri eksik hastalar için All-on-4, yalnızca 4 implantla sabit diş imkânı sunar. Yöntemin nasıl çalıştığını ve kimlere uygun olduğunu anlattık.",
     "date": "2026-04-07", "read": 6, "img": "implant.jpg",
     "body": """<p>All-on-4, tam dişsizlik yaşayan hastalarda tek bir çenedeki tüm dişlerin yalnızca dört implant üzerine sabitlenmesini sağlayan bir tedavi yaklaşımıdır. Hareketli protez kullanmak istemeyen hastalar için konforlu, sabit bir alternatiftir.</p>
<h2>All-on-4'ün Avantajları</h2>
<ul>
<li>Az sayıda implantla tüm çeneye sabit diş.</li>
<li>Çoğu uygun vakada kemik grefti ihtiyacını azaltır.</li>
<li>Hareketli protezin oynama, düşme sorunu yaşanmaz.</li>
<li>Çiğneme ve konuşma konforu doğal dişe yakındır.</li>
</ul>
<h2>Kimler İçin Uygun?</h2>
<p>Çok sayıda dişi eksik olan, mevcut protezinden memnun olmayan veya yeni protez yapılacak hastalar aday olabilir. Uygunluk; kemik yoğunluğu ve genel sağlık durumuna göre tomografiyle değerlendirilir.</p>
<p>Sabit ve konforlu bir gülüşe kavuşmak için <a href="/tedaviler/implant/">implant tedavisi</a> seçeneklerimizi inceleyin, kişisel planlama için <a href="/iletisim/">bizimle iletişime geçin</a>. Tek diş eksikliğinde alternatifleri <a href="/blog/implant-mi-kopru-mu/">implant mı köprü mü</a> yazımızda karşılaştırdık.</p>"""},
    {"slug": "zirkonyum-mu-lamina-mi", "cat": "Estetik",
     "title": "Zirkonyum mu Lamina mı? Hangisi Size Uygun?",
     "kw": "zirkonyum kaplama Konya",
     "excerpt": "Gülüş estetiğinde en çok karşılaştırılan iki seçenek: zirkonyum ve lamina. Aralarındaki farkları ve hangisinin size uygun olduğunu açıkladık.",
     "date": "2026-03-31", "read": 6, "img": "gulus-estetigi.jpg",
     "body": """<p>Estetik diş tedavisinde en sık sorulan sorulardan biri zirkonyum ile lamina (yaprak porselen) arasındaki farktır. İkisi de doğal ve estetik sonuçlar verir; ancak uygulama ve endikasyonları farklıdır.</p>
<h2>Lamina (Yaprak Porselen)</h2>
<p>Dişin yalnızca ön yüzeyine yapıştırılan ince porselen tabakalardır. Dişten çok az aşındırma gerektirir, oldukça doğal görünür. Renk ve şekil sorunları olan, dişleri büyük oranda sağlam hastalar için idealdir.</p>
<h2>Zirkonyum Kaplama</h2>
<p>Dişin tamamını çevreleyen, metal içermeyen sağlam kaplamalardır. Daha fazla aşındırma gerektirir ama dayanıklılığı yüksektir. Kanal tedavili, kırık veya büyük dolgulu dişlerde tercih edilir.</p>
<p>Kısaca: minimal müdahale ve estetik için lamina, dayanıklılık ve büyük restorasyon için zirkonyum öne çıkar. Doğru seçim, dişlerinizin mevcut durumuna bağlıdır. <a href="/tedaviler/gulus-estetigi/">Gülüş estetiği</a> sayfamızı inceleyin, kişisel öneri için <a href="/iletisim/">bize ulaşın</a>. Bütüncül planı <a href="/blog/gulus-tasarimi-nedir/">gülüş tasarımı nedir</a> yazımızda anlattık.</p>"""},
    {"slug": "dis-beyazlatma-zararli-mi", "cat": "Estetik",
     "title": "Diş Beyazlatma Zararlı mı? Doğru Bilinen Yanlışlar",
     "kw": "diş beyazlatma",
     "excerpt": "Diş beyazlatma dişe zarar verir mi, kalıcı mıdır? Profesyonel beyazlatma hakkında en çok merak edilenleri ve yanlış bilinenleri yanıtladık.",
     "date": "2026-03-24", "read": 5, "img": "gulus-estetigi.jpg",
     "body": """<p>Diş beyazlatma, doğru yapıldığında güvenli ve etkili bir işlemdir. Ancak internetteki "evde" yöntemler ve yanlış bilgiler kafa karıştırır. Gerçekleri netleştirelim.</p>
<h2>Doğru Bilinen Yanlışlar</h2>
<ul>
<li><strong>"Beyazlatma minenizi aşındırır":</strong> Hekim kontrolünde uygulanan jeller mineyi aşındırmaz; geçici hassasiyet olabilir, kalıcı hasar beklenmez.</li>
<li><strong>"Bir kez yaptırınca ömür boyu beyaz kalır":</strong> Sonuç kalıcı değildir; kahve, çay, sigara renklenmeyi hızlandırır.</li>
<li><strong>"Karbonat veya limon işe yarar":</strong> Bu yöntemler mineye zarar verir, asla önerilmez.</li>
</ul>
<h2>Güvenli Yöntem</h2>
<p>En güvenli sonuç, klinikte hekim kontrolünde yapılan profesyonel beyazlatmadır. Öncesinde diş taşı temizliği ve çürük kontrolü yapılır. Hassasiyeti olanlar için özel protokoller mevcuttur.</p>
<p>Daha parlak bir gülüş için <a href="/tedaviler/gulus-estetigi/">gülüş estetiği</a> seçeneklerimizi inceleyin ve <a href="/iletisim/">bize ulaşın</a>. Renklenmeyle ilgili <a href="/blog/dis-tasi-temizligi-zararli-mi/">diş taşı temizliği</a> yazımız da ilginizi çekebilir.</p>"""},
    {"slug": "hollywood-smile-nedir", "cat": "Estetik",
     "title": "Hollywood Smile Hakkında Bilmeniz Gereken Her Şey",
     "kw": "hollywood smile Konya",
     "excerpt": "Hollywood Smile yalnızca beyaz dişler değil; simetri, oran ve doğallık üzerine kurulu bir gülüş tasarımıdır. Sürecin tüm detayları.",
     "date": "2026-03-17", "read": 6, "img": "gulus-estetigi.jpg",
     "body": """<p>Hollywood Smile (Hollywood gülüşü), dişlerin rengini, formunu ve dizilimini yüz hatlarıyla uyumlu, simetrik ve doğal bir bütüne dönüştüren kapsamlı bir estetik tedavidir. Amaç abartılı değil, kişiye yakışan kusursuz bir gülümsemedir.</p>
<h2>Hangi Uygulamaları Kapsar?</h2>
<ul>
<li>Lamina veya zirkonyum kaplamalar</li>
<li>Diş beyazlatma</li>
<li>Gerektiğinde diş eti estetiği</li>
<li>Bazı durumlarda ortodonti ile ön hazırlık</li>
</ul>
<h2>Süreç Nasıl İşler?</h2>
<p>Önce dijital gülüş tasarımı yapılır ve sonucu önceden görürsünüz. Ardından prova ve uygulama aşamalarıyla tedavi tamamlanır. Doğru planlama, hem estetik hem de çiğneme fonksiyonunu birlikte gözetir.</p>
<p>Size özel bir gülüş için <a href="/tedaviler/gulus-estetigi/">gülüş estetiği</a> sayfamızı inceleyin, ön görüşme için <a href="/iletisim/">bize ulaşın</a>. Zirkonyum ve lamina arasındaki farkı <a href="/blog/zirkonyum-mu-lamina-mi/">bu yazıda</a> karşılaştırdık.</p>"""},
    {"slug": "seffaf-plak-mi-dis-teli-mi", "cat": "Ortodonti",
     "title": "Şeffaf Plak mı Diş Teli mi? Karşılaştırma",
     "kw": "şeffaf plak Konya",
     "excerpt": "Çapraşık dişler için şeffaf plak ve klasik diş teli en çok tercih edilen iki yöntem. Konfor, estetik ve süre açısından karşılaştırdık.",
     "date": "2026-03-10", "read": 6, "img": "ortodonti.jpg",
     "body": """<p>Diş düzensizliklerinin tedavisinde iki ana yol vardır: geleneksel diş teli (braket) ve şeffaf plaklar. Hangisinin uygun olduğu, dişlerin durumuna ve beklentilerinize bağlıdır.</p>
<h2>Şeffaf Plak</h2>
<ul>
<li>Neredeyse görünmez, estetik açıdan avantajlı.</li>
<li>Çıkarılabilir; yemek ve fırçalama kolay.</li>
<li>Hafif-orta düzensizliklerde çok etkili.</li>
</ul>
<h2>Diş Teli</h2>
<ul>
<li>Karmaşık vakalarda daha güçlü kontrol sağlar.</li>
<li>Hastaya bağlı kullanım hatası riski azdır (sabittir).</li>
<li>Maliyeti genellikle daha uygundur.</li>
</ul>
<p>Şeffaf plak günde ~20-22 saat takılmalıdır; disiplin gerektirir. Diş teli ise sürekli takılı olduğundan kullanım sorumluluğu daha azdır. Doğru seçim için ortodontik muayene şarttır. <a href="/tedaviler/ortodonti/">Ortodonti</a> seçeneklerimizi inceleyin, <a href="/iletisim/">değerlendirme için bize ulaşın</a>. Yetişkinlikte tedaviyi merak ediyorsanız <a href="/blog/yetiskinlerde-dis-teli/">yetişkinlerde diş teli</a> yazımıza bakın.</p>"""},
    {"slug": "yetiskinlerde-dis-teli", "cat": "Ortodonti",
     "title": "Yetişkinlerde Diş Teli Geç mi Kalındı?",
     "kw": "yetişkin ortodonti",
     "excerpt": "Ortodonti yalnızca çocuklara özgü değildir. Yetişkinlikte diş teli tedavisinin mümkün olup olmadığını ve avantajlarını anlattık.",
     "date": "2026-03-03", "read": 5, "img": "ortodonti.jpg",
     "body": """<p>"Bu yaştan sonra diş teli olur mu?" sorusu çok yaygındır. Cevap nettir: ortodontik tedavi için yaş sınırı yoktur. Dişler ve çevre dokular sağlıklı olduğu sürece her yaşta diş hareketi mümkündür.</p>
<h2>Yetişkinlikte Ortodontinin Faydaları</h2>
<ul>
<li>Çapraşıklık giderildiğinde fırçalama kolaylaşır, çürük ve diş eti hastalığı riski azalır.</li>
<li>Kapanış bozuklukları düzelir; çene ve diş aşınması azalır.</li>
<li>Estetik iyileşmeyle birlikte özgüven artar.</li>
</ul>
<h2>Estetik Kaygı Varsa</h2>
<p>Metal braketlerden çekinen yetişkinler için şeffaf plak veya estetik braketler iyi bir seçenektir. İş ve sosyal hayatı aksatmadan tedavi mümkündür.</p>
<p>Tedavi süresi vakanın karmaşıklığına göre değişir; muayenede net bilgi verilir. <a href="/tedaviler/ortodonti/">Ortodonti</a> sayfamızı inceleyin ve <a href="/iletisim/">bize ulaşın</a>. Şeffaf plak ile diş teli arasındaki farkları <a href="/blog/seffaf-plak-mi-dis-teli-mi/">bu yazıda</a> karşılaştırdık.</p>"""},
    {"slug": "dis-teli-beslenme-rehberi", "cat": "Ortodonti",
     "title": "Diş Teli Takanlar İçin Beslenme Rehberi",
     "kw": "diş teli beslenme",
     "excerpt": "Diş teli tedavisinde doğru beslenme, braketlerin zarar görmesini önler ve tedaviyi hızlandırır. Yenebilecek ve kaçınılması gereken besinler.",
     "date": "2026-02-24", "read": 4, "img": "ortodonti.jpg",
     "body": """<p>Diş teli tedavisi sırasında beslenme alışkanlıkları, braketlerin sağlamlığı ve ağız hijyeni açısından önemlidir. Yanlış besinler braket kopmasına ve tedavinin uzamasına yol açabilir.</p>
<h2>Kaçınılması Gerekenler</h2>
<ul>
<li>Sert kabuklu yemişler, buz, sert şeker</li>
<li>Yapışkan gıdalar (sakız, lokum, karamel)</li>
<li>Bütün elma/havuç gibi sert meyve-sebzeleri ısırarak yemek (parçalayarak yiyin)</li>
<li>Aşırı asitli ve şekerli içecekler</li>
</ul>
<h2>Rahatlıkla Tüketebilecekleriniz</h2>
<ul>
<li>Yumuşak pişmiş sebzeler, makarna, pilav</li>
<li>Yoğurt, peynir, süt ürünleri</li>
<li>Yumuşak meyveler (muz, çilek)</li>
<li>Yumurta, köfte, balık gibi yumuşak protein kaynakları</li>
</ul>
<p>Tel takılmasının ardından ilk günler hassasiyet olabilir; bu dönemde yumuşak gıdalar tercih edin. Her öğün sonrası fırçalama braket çevresinde leke ve çürüğü önler. <a href="/tedaviler/ortodonti/">Ortodonti tedavisi</a> hakkında daha fazlası için <a href="/iletisim/">bize ulaşın</a>.</p>"""},
    {"slug": "sut-disi-curugu-onemli-mi", "cat": "Pedodonti",
     "title": "Süt Dişi Çürüğü Önemli mi?",
     "kw": "süt dişi çürüğü",
     "excerpt": "\"Nasılsa düşecek\" düşüncesi süt dişi çürüklerini önemsizleştirir. Oysa süt dişleri kalıcı dişlerin sağlığını doğrudan etkiler.",
     "date": "2026-02-17", "read": 4, "img": "pedodonti.jpg",
     "body": """<p>Birçok ebeveyn süt dişi çürüklerini "nasılsa düşecek" diyerek önemsemez. Oysa süt dişleri yalnızca çiğneme için değil; konuşma, çene gelişimi ve kalıcı dişlere yer tutma açısından da kritiktir.</p>
<h2>Süt Dişi Çürüğü Neden Önemli?</h2>
<ul>
<li>Çürük ilerleyerek ağrı ve enfeksiyona dönüşebilir.</li>
<li>Erken kaybedilen süt dişi, kalıcı dişin yanlış sürmesine yol açabilir.</li>
<li>Çiğneme zorluğu beslenmeyi olumsuz etkiler.</li>
<li>Ön diş çürükleri çocuğun konuşmasını ve özgüvenini etkileyebilir.</li>
</ul>
<h2>Korunma</h2>
<p>Düzenli fırçalama, şekerli atıştırmalıkların sınırlanması, flor ve fissür örtücü uygulamaları çürükleri büyük ölçüde önler. Erken kontrol, küçük çürüğün büyümeden çözülmesini sağlar.</p>
<p><a href="/tedaviler/cocuk-dis-hekimligi/">KDH Çocuk kliniğimizde</a> minik hastalarımıza korkutmadan, oyunlaştırarak yaklaşıyoruz. İlk kontrolün zamanlamasını <a href="/blog/cocuk-ilk-dis-kontrolu/">bu yazıda</a> anlattık. Randevu için <a href="/iletisim/">bize ulaşın</a>.</p>"""},
    {"slug": "cocuk-dis-hekimi-korkusu", "cat": "Pedodonti",
     "title": "Çocuklarda Diş Hekimi Korkusu Nasıl Yenilir?",
     "kw": "çocuk diş hekimi korkusu",
     "excerpt": "Diş hekimi korkusu çoğu çocukta görülür ve doğru yaklaşımla aşılabilir. Ebeveynlere ve kliniğe düşen görevleri anlattık.",
     "date": "2026-02-10", "read": 5, "img": "pedodonti.jpg",
     "body": """<p>Diş hekimi korkusu çocuklarda yaygındır ve genellikle bilinmezlikten kaynaklanır. Doğru yaklaşımla bu korku kolayca aşılabilir; üstelik erken yaşta kazanılan olumlu deneyim ömür boyu sürer.</p>
<h2>Ebeveynlere Öneriler</h2>
<ul>
<li>"Acımayacak", "iğne yok" gibi olumsuz çağrışım yapan ifadelerden kaçının.</li>
<li>Diş hekimini bir ceza değil, rutin bir bakım gibi anlatın.</li>
<li>İlk ziyareti acil bir durum yerine tanışma amaçlı planlayın.</li>
<li>Kendi kaygınızı çocuğa yansıtmamaya özen gösterin.</li>
</ul>
<h2>Kliniğin Rolü</h2>
<p>Çocuk diş hekimliği (pedodonti), çocuğun yaşına uygun iletişim, oyunlaştırma ve sabırlı bir yaklaşım gerektirir. Doğru ortamda çocuk, tedaviyi bir korku değil, keyifli bir deneyim olarak hatırlar.</p>
<p><a href="/tedaviler/cocuk-dis-hekimligi/">KDH Çocuk</a> kliniğimiz tam da bunun için tasarlandı. Çocuğunuzun ilk diş deneyimini olumlu kılmak için <a href="/iletisim/">bize ulaşın</a>. İlk kontrol zamanını <a href="/blog/cocuk-ilk-dis-kontrolu/">bu yazıda</a> bulabilirsiniz.</p>"""},
    {"slug": "fissur-ortucu-ve-flor", "cat": "Pedodonti",
     "title": "Fissür Örtücü ve Flor Uygulaması Nedir?",
     "kw": "fissür örtücü",
     "excerpt": "Fissür örtücü ve flor, çocuklarda çürüğü daha başlamadan önleyen koruyucu uygulamalardır. Nasıl yapıldığını ve kimlere uygun olduğunu anlattık.",
     "date": "2026-02-03", "read": 4, "img": "pedodonti.jpg",
     "body": """<p>Çürükle mücadelede en etkili yol, çürük oluşmadan önlem almaktır. Fissür örtücü ve flor uygulaması, özellikle çocuklarda çürüğü daha başlamadan engelleyen basit ama güçlü koruyucu yöntemlerdir.</p>
<h2>Fissür Örtücü</h2>
<p>Azı dişlerinin çiğneyici yüzeyindeki derin oluklar (fissürler), fırçanın ulaşamadığı, bakteri ve gıda artıklarının biriktiği bölgelerdir. Fissür örtücü, bu oluklar ince bir akışkan dolgu ile kapatarak çürük riskini ciddi oranda azaltır. Ağrısızdır ve birkaç dakika sürer.</p>
<h2>Flor Uygulaması</h2>
<p>Flor, diş minesini güçlendirerek asit ataklarına karşı dirençli hale getirir. Klinikte uygulanan flor jeli/vernik, ev bakımına ek bir koruma sağlar.</p>
<p>Bu uygulamalar genellikle daimî azı dişleri sürdükten sonra önerilir. <a href="/tedaviler/cocuk-dis-hekimligi/">Çocuk diş hekimliği</a> hizmetlerimiz kapsamında uygulanır. Çocuğunuzun dişlerini korumak için <a href="/iletisim/">bize ulaşın</a>. Süt dişi çürüklerinin önemini <a href="/blog/sut-disi-curugu-onemli-mi/">bu yazıda</a> ele aldık.</p>"""},
    {"slug": "kanal-tedavisi-agrili-mi", "cat": "Endodonti",
     "title": "Kanal Tedavisi Ağrılı mı? Mitler ve Gerçekler",
     "kw": "kanal tedavisi Konya",
     "excerpt": "Kanal tedavisi denince akla ağrı gelir; oysa modern yöntemlerle işlem konforludur. Kanal tedavisi hakkında doğru bilinen yanlışları yanıtladık.",
     "date": "2026-01-27", "read": 5, "img": "kanal-tedavisi.jpg",
     "body": """<p>Kanal tedavisi, halk arasında en çok korkulan işlemlerden biridir. Oysa bu korku büyük ölçüde eski yöntemlerden ve yanlış bilgilerden kaynaklanır. Gerçek şu: kanal tedavisi ağrıyı bitiren işlemdir, başlatan değil.</p>
<h2>Yaygın Yanlışlar</h2>
<ul>
<li><strong>"Çok ağrılıdır":</strong> Modern anestezi ve aletlerle işlem genellikle bir dolgu kadar konforludur.</li>
<li><strong>"Diş zaten ölmüş, çekilse daha iyi":</strong> Doğal dişi korumak her zaman en iyi seçenektir.</li>
<li><strong>"Tedaviden sonra diş kırılır":</strong> Uygun restorasyon (genellikle kaplama) ile diş uzun yıllar dayanır.</li>
</ul>
<h2>Neden Gerekir?</h2>
<p>Çürük veya travma diş sinirine ulaştığında iltihap oluşur ve şiddetli ağrı yapar. Kanal tedavisi, enfekte dokuyu temizleyip kanalları doldurarak dişi kurtarır.</p>
<p>İşlem sonrası birkaç gün hafif hassasiyet normaldir. <a href="/tedaviler/kanal-tedavisi/">Kanal tedavisi</a> hakkında bilgi alabilir, ağrınız varsa <strong>pazar dahil her gün 23:00'a kadar</strong> açık olan kliniğimize <a href="/iletisim/">başvurabilirsiniz</a>. Apse şüphesinde <a href="/blog/dis-apsesi-tehlikeli-mi/">diş apsesi</a> yazımıza bakın.</p>"""},
    {"slug": "yirmi-yas-disi-cekimi", "cat": "Cerrahi",
     "title": "20'lik (Yirmi Yaş) Diş Ne Zaman Çekilmeli?",
     "kw": "20lik diş çekimi Konya",
     "excerpt": "Her yirmi yaş dişi çekilmek zorunda değildir. Hangi durumlarda çekim gerektiğini ve sürecin nasıl ilerlediğini açıkladık.",
     "date": "2026-01-20", "read": 5, "img": "cerrahi.jpg",
     "body": """<p>Yirmi yaş dişleri (üçüncü büyük azılar) genellikle 17-25 yaş arasında sürer. Her zaman çekilmeleri gerekmez; ancak yer darlığı ve yanlış konumlanma sık sorun yaratır.</p>
<h2>Çekim Gerektiren Durumlar</h2>
<ul>
<li>Gömülü kalıp ağrı, şişlik veya enfeksiyona yol açması</li>
<li>Komşu dişe baskı yapıp çürük veya hasar oluşturması</li>
<li>Tekrarlayan diş eti iltihabı (perikoronit)</li>
<li>Kist veya çene problemine neden olması</li>
</ul>
<h2>Çekilmesi Gerekmeyen Durumlar</h2>
<p>Tam ve doğru sürmüş, karşıt dişiyle kapanışı olan, temizlenebilen ve sorun yaratmayan yirmi yaş dişleri korunabilir. Karar, radyografik değerlendirme ile verilir.</p>
<p>İşlem öncesi tomografi/röntgen ile dişin kök ve sinir ilişkisi incelenir. <a href="/tedaviler/cerrahi/">Cerrahi uygulamalar</a> sayfamızı inceleyin, değerlendirme için <a href="/iletisim/">bize ulaşın</a>. Çekim sonrası bakımı <a href="/blog/dis-cekimi-sonrasi-bakim/">bu yazıda</a> anlattık.</p>"""},
    {"slug": "dis-cekimi-sonrasi-bakim", "cat": "Cerrahi",
     "title": "Diş Çekimi Sonrası Nelere Dikkat Edilmeli?",
     "kw": "diş çekimi sonrası bakım",
     "excerpt": "Diş çekimi sonrası ilk 24 saat iyileşmenin temelini atar. Kanamayı durdurmak ve kuru soketi önlemek için yapmanız ve yapmamanız gerekenler.",
     "date": "2026-01-13", "read": 5, "img": "cerrahi.jpg",
     "body": """<p>Diş çekimi sonrası doğru bakım, iyileşmeyi hızlandırır ve "kuru soket" gibi ağrılı komplikasyonları önler. İlk 24 saat özellikle önemlidir.</p>
<h2>İlk 24 Saat</h2>
<ul>
<li>Hekimin koyduğu tamponu 30-45 dakika sıkıca ısırın.</li>
<li>İlk gün tükürmeyin, çalkalamayın ve pipetle içecek tüketmeyin (pıhtı yerinden oynar).</li>
<li>Sigara ve alkolden kaçının; iyileşmeyi geciktirir.</li>
<li>Şişlik için yanağa dışarıdan soğuk uygulayın.</li>
<li>Yumuşak ve ılık gıdalar tercih edin, çekim bölgesini kullanmayın.</li>
</ul>
<h2>Sonraki Günler</h2>
<p>İkinci günden itibaren ılık tuzlu su ile nazik gargara yapabilirsiniz. Hafif ağrı ve şişlik normaldir; ancak artan ağrı, kötü koku veya durmayan kanama varsa hekiminize başvurun.</p>
<p>Çekim sonrası uzun süren kanama <a href="/blog/acil-dis-tedavisi-gerektiren-durumlar/">acil durum</a> olabilir; <strong>pazar dahil her gün 23:00'a kadar</strong> açığız. <a href="/tedaviler/cerrahi/">Cerrahi uygulamalar</a> hakkında bilgi için <a href="/iletisim/">bize ulaşın</a>.</p>"""},
    {"slug": "dis-eti-kanamasi-nedenleri", "cat": "Diş Eti Sağlığı",
     "title": "Diş Eti Kanaması Neden Olur, Nasıl Geçer?",
     "kw": "diş eti kanaması",
     "excerpt": "Fırçalarken diş eti kanaması çoğu zaman göz ardı edilir; oysa diş eti hastalığının ilk işareti olabilir. Nedenleri ve çözümü.",
     "date": "2026-01-06", "read": 5, "img": "kanal-tedavisi.jpg",
     "body": """<p>Fırçalama sırasında diş etinden kan gelmesi sık görülür ve çoğu zaman önemsenmez. Oysa sağlıklı diş eti kanamaz; kanama, çoğunlukla diş eti iltihabının (gingivitis) ilk habercisidir.</p>
<h2>Diş Eti Kanamasının Nedenleri</h2>
<ul>
<li>Diş taşı ve plak birikimi (en yaygın neden)</li>
<li>Yetersiz veya yanlış fırçalama</li>
<li>Hormonal değişiklikler (hamilelik, ergenlik)</li>
<li>Sigara kullanımı</li>
<li>Bazı sistemik hastalıklar ve vitamin eksiklikleri</li>
</ul>
<h2>Nasıl Geçer?</h2>
<p>Erken aşamada çözüm genellikle basittir: profesyonel diş taşı temizliği ve doğru ağız bakımı. İhmal edilirse iltihap, dişi tutan kemiğe ilerleyerek diş kaybına (periodontitis) yol açabilir.</p>
<p>Kanamayı görmezden gelmeyin. <a href="/tedaviler/gulus-estetigi/">Ağız ve diş sağlığı</a> hizmetlerimiz kapsamında diş eti değerlendirmesi yapılır. Düzenli kontrol için <a href="/iletisim/">bize ulaşın</a>. Diş taşı temizliği hakkında <a href="/blog/dis-tasi-temizligi-zararli-mi/">bu yazıyı</a> okuyabilirsiniz.</p>"""},
    {"slug": "dis-tasi-temizligi-zararli-mi", "cat": "Koruyucu",
     "title": "Diş Taşı Temizliği Zararlı mı? Dişleri Aşındırır mı?",
     "kw": "diş taşı temizliği Konya",
     "excerpt": "\"Diş taşı temizliği dişleri aşındırır, aralık açar\" inancı çok yaygın ama yanlış. Diş taşı temizliği hakkındaki gerçekleri anlattık.",
     "date": "2025-12-23", "read": 4, "img": "gulus-estetigi.jpg",
     "body": """<p>Diş taşı temizliği (detertraj) hakkında en sık duyulan kaygı, işlemin dişlere zarar verdiği yönündedir. Gerçek tam tersidir: diş taşı temizliği, diş ve diş eti sağlığını korumanın en temel adımıdır.</p>
<h2>Doğru Bilinen Yanlışlar</h2>
<ul>
<li><strong>"Dişleri aşındırır":</strong> İşlem mineye zarar vermez; yalnızca sertleşmiş plak (taş) temizlenir.</li>
<li><strong>"Dişlerde aralık açar":</strong> Aralık zaten taşın altındaydı; taş kaldırılınca ortaya çıkar, temizlik açmaz.</li>
<li><strong>"Dişleri hassaslaştırır":</strong> Geçici hassasiyet olabilir, birkaç günde geçer.</li>
</ul>
<h2>Neden Gereklidir?</h2>
<p>Diş taşı, fırçayla çıkmayan, bakteri barındıran sert bir tabakadır. Temizlenmediğinde diş eti iltihabı, kanama ve ilerleyen evrede diş kaybına yol açar. Genellikle 6 ayda bir kontrol ve gerektiğinde temizlik önerilir.</p>
<p>Diş eti kanamasının nedenlerini <a href="/blog/dis-eti-kanamasi-nedenleri/">bu yazıda</a> ele aldık. Düzenli kontrol ve temizlik için <a href="/iletisim/">bize ulaşın</a>; <a href="/subeler/karatay/">şubelerimizden</a> size en yakın olanı seçebilirsiniz.</p>"""},
    {"slug": "hassas-disler-icin-oneriler", "cat": "Koruyucu",
     "title": "Hassas Dişler İçin 8 Pratik Öneri",
     "kw": "diş hassasiyeti",
     "excerpt": "Soğuk-sıcak veya tatlıda zonklayan dişler günlük yaşamı zorlaştırır. Diş hassasiyetini azaltmak için uygulayabileceğiniz 8 pratik öneri.",
     "date": "2025-12-16", "read": 4, "img": "kanal-tedavisi.jpg",
     "body": """<p>Soğuk bir içecekte ya da tatlıda dişlerinizde keskin bir hassasiyet hissediyorsanız yalnız değilsiniz. Diş hassasiyeti, mine aşınması veya diş eti çekilmesiyle açığa çıkan dentin nedeniyle oluşur.</p>
<h2>Hassasiyeti Azaltmak İçin</h2>
<ul>
<li>Hassasiyet giderici diş macunu kullanın (düzenli kullanımda etkilidir).</li>
<li>Yumuşak fırça tercih edin, sert ovalamaktan kaçının.</li>
<li>Asitli yiyecek-içecekleri (turunçgil, gazlı içecek) sınırlayın.</li>
<li>Diş gıcırdatıyorsanız gece plağı kullanın.</li>
<li>Beyazlatma ürünlerini hekim önerisi olmadan abartmayın.</li>
<li>Fırçalamayı asitli gıdadan hemen sonra değil, 30 dk sonra yapın.</li>
<li>Diş eti çekilmesini önlemek için doğru fırçalama tekniğini öğrenin.</li>
<li>Geçmeyen hassasiyette mutlaka hekime başvurun; altta çürük olabilir.</li>
</ul>
<p>Sürekli ve şiddetli hassasiyet, çürük veya çatlak gibi bir sorunun işareti olabilir. <a href="/tedaviler/kanal-tedavisi/">Tedavi seçeneklerimiz</a> için <a href="/iletisim/">bize ulaşın</a>. Diş gıcırdatma sorununu ayrı bir yazıda da ele alıyoruz.</p>"""},
    {"slug": "agiz-kokusu-halitozis", "cat": "Genel",
     "title": "Ağız Kokusu (Halitozis) Neden Olur, Nasıl Geçer?",
     "kw": "ağız kokusu tedavisi",
     "excerpt": "Ağız kokusu sosyal hayatı etkileyen, çoğu zaman kaynağı ağızda olan bir sorundur. Nedenlerini ve kalıcı çözüm yollarını anlattık.",
     "date": "2025-12-09", "read": 5, "img": "gulus-estetigi.jpg",
     "body": """<p>Ağız kokusu (halitozis) yaygın ve çoğu zaman çözülebilir bir sorundur. Vakaların büyük bölümünde kaynak ağız içindedir ve doğru bakımla giderilebilir.</p>
<h2>Sık Görülen Nedenler</h2>
<ul>
<li>Dil üzerindeki bakteri tabakası ve yetersiz ağız hijyeni</li>
<li>Diş taşı, çürük ve diş eti hastalıkları</li>
<li>Ağız kuruluğu (tükürük azlığı)</li>
<li>Sigara ve bazı besinler</li>
<li>Daha az sıklıkla sindirim veya sinüs kaynaklı sorunlar</li>
</ul>
<h2>Kalıcı Çözüm İçin</h2>
<p>Günde iki kez fırçalama, diş ipi ve dil temizliği temel adımlardır. Düzenli diş taşı temizliği ve çürük tedavisi kokunun ağızdaki kaynaklarını ortadan kaldırır. Bol su tüketimi ağız kuruluğunu azaltır.</p>
<p>Bakıma rağmen geçmeyen ağız kokusunda mutlaka değerlendirme yapılmalıdır. <a href="/tedaviler/gulus-estetigi/">Ağız ve diş sağlığı</a> kontrolü için <a href="/iletisim/">bize ulaşın</a>. Diş eti kanamanız da varsa <a href="/blog/dis-eti-kanamasi-nedenleri/">diş eti kanaması</a> yazımıza göz atın.</p>"""},
    {"slug": "dis-kontrolu-ne-siklikla", "cat": "Koruyucu",
     "title": "Diş Hekimi Kontrolü Ne Sıklıkla Yapılmalı?",
     "kw": "diş kontrolü ne sıklıkla",
     "excerpt": "Şikâyet olmadan diş hekimine gitmek gereksiz mi? Düzenli kontrolün neden önemli olduğunu ve ideal sıklığı açıkladık.",
     "date": "2025-12-02", "read": 4, "img": "ortodonti.jpg",
     "body": """<p>Birçok kişi yalnızca ağrı olduğunda diş hekimine gider. Oysa düzenli kontrol, sorunları daha küçük ve ucuzken yakalamanın en etkili yoludur. Önleyici bakım, tedaviden her zaman kolaydır.</p>
<h2>İdeal Kontrol Sıklığı</h2>
<ul>
<li><strong>Genel öneri:</strong> 6 ayda bir kontrol ve gerektiğinde diş taşı temizliği.</li>
<li><strong>Yüksek risk gruplarında</strong> (diş eti hastalığı, sık çürük, sigara) daha sık takip gerekebilir.</li>
<li><strong>Çocuklarda</strong> gelişimi izlemek için düzenli kontrol önemlidir.</li>
</ul>
<h2>Neden Önemli?</h2>
<p>Çürük ve diş eti hastalıkları erken evrede çoğu zaman belirti vermez. Düzenli kontrolde küçük bir çürük basit bir dolguyla çözülürken, ihmal edildiğinde kanal tedavisi ya da çekime kadar ilerleyebilir.</p>
<p>Henüz şikâyetiniz yokken bir kontrol randevusu almak en akıllıca yatırımdır. <a href="/iletisim/">Bize ulaşın</a>, size en yakın <a href="/subeler/meram/">şubemizde</a> sizi ağırlayalım. Çocuğunuzun ilk kontrolü için <a href="/blog/cocuk-ilk-dis-kontrolu/">bu yazıya</a> bakın.</p>"""},
    {"slug": "konya-dis-tedavi-fiyatlari", "cat": "Yerel Rehber",
     "title": "Konya'da Diş Tedavisi Fiyatları Neye Göre Belirlenir?",
     "kw": "Konya diş tedavi fiyatları",
     "excerpt": "Diş tedavisi fiyatları neden klinikten kliniğe değişir? Fiyatı belirleyen faktörleri ve doğru kliniği seçerken nelere bakmanız gerektiğini anlattık.",
     "date": "2025-11-25", "read": 5, "img": "implant.jpg",
     "body": """<p>"Diş tedavisi ne kadar?" sorusunun tek bir cevabı yoktur; çünkü fiyat, tedavinin türüne ve birçok değişkene bağlıdır. Şeffaf bir klinik, planlamadan önce size net bilgi verir.</p>
<h2>Fiyatı Belirleyen Faktörler</h2>
<ul>
<li><strong>Tedavi türü:</strong> Dolgu, kanal, implant, ortodonti farklı emek ve malzeme gerektirir.</li>
<li><strong>Kullanılan malzeme:</strong> Örneğin implant markası veya kaplama türü (zirkonyum/lamina).</li>
<li><strong>Vakanın karmaşıklığı:</strong> Ek işlem (kemik grefti, diş eti tedavisi) gerekip gerekmemesi.</li>
<li><strong>Klinik teknolojisi ve hekim deneyimi.</strong></li>
</ul>
<h2>Sadece Fiyata Göre Karar Vermeyin</h2>
<p>En düşük fiyat her zaman en iyi seçenek değildir. Yanlış veya eksik tedavi, uzun vadede daha yüksek maliyet doğurabilir. Hijyen, hekim deneyimi, malzeme kalitesi ve sonrası takip de en az fiyat kadar önemlidir.</p>
<p>Konya Diş Hekimi olarak tedavi öncesi net ve şeffaf bilgilendirme yapıyoruz. Size özel tedavi planı ve fiyat bilgisi için <a href="/iletisim/">bize ulaşın</a>. Doğru kliniği seçerken <a href="/blog/selcuklu-dis-hekimi-secimi/">nelere dikkat etmeniz gerektiğini</a> de okuyabilirsiniz.</p>"""},
]
BLOG_MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
def fmt_date(iso):
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), BLOG_MONTHS[int(m) - 1], y)

def blog_card(b):
    return ('<a class="blog-card reveal" href="/blog/%s/">'
            '<div class="blog-card-img"><span class="blog-cat">%s</span>'
            '<img src="/assets/treatments/%s" alt="%s" loading="lazy" width="400" height="220" /></div>'
            '<div class="blog-card-body"><div class="blog-card-meta">%s &middot; %d dk okuma</div>'
            '<h3>%s</h3><p>%s</p><span class="blog-more">Devamını Oku &rarr;</span></div></a>'
            % (b["slug"], b["cat"], web(b["img"]), b["title"], fmt_date(b["date"]), b["read"], b["title"], b["excerpt"]))

blog_index = hero("Diş Sağlığı Blogu — Bilgi Merkezi",
                  "Ağız ve diş sağlığı hakkında uzman tavsiyeleri ve güncel yazılar.",
                  [("Ana Sayfa", "/"), ("Blog", "/blog/")]) + \
    '<div class="section"><div class="container"><div class="blog-grid">' + \
    "".join(blog_card(b) for b in BLOG) + '</div></div></div>'
ROUTES.append(page(
    "/blog/", "blog",
    "Diş Sağlığı Blogu – Uzman Tavsiyeleri | Konya Diş Hekimi",
    "Ağız ve diş sağlığı hakkında uzman yazıları: implant bakımı, çocuk diş sağlığı, gülüş tasarımı ve gece diş ağrısı önerileri. Konya Diş Hekimi.",
    "Bilgi Merkezi", blog_index,
    [breadcrumb([("Ana Sayfa", "/"), ("Blog", "/blog/")]),
     {"@type": "Blog", "@id": ORIGIN + "/blog/#blog", "url": ORIGIN + "/blog/",
      "name": "Konya Diş Hekimi Blog", "publisher": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
    "/blog/"))

for b in BLOG:
    content = ('<div class="page-hero"><div class="container">' +
               crumb_html([("Ana Sayfa", "/"), ("Blog", "/blog/"), (b["title"], "/blog/%s/" % b["slug"])]) +
               '<span class="blog-cat" style="position:static;display:inline-block;margin-bottom:1rem">%s</span>'
               '<h1 class="page-hero-title reveal">%s</h1>'
               '<p class="page-hero-sub reveal">%s &middot; %d dk okuma</p></div></div>'
               % (b["cat"], b["title"], fmt_date(b["date"]), b["read"])) + (
        '<div class="section"><div class="container container-narrow">'
        '<img src="/assets/treatments/%s" alt="%s" loading="lazy" width="760" height="380" style="width:100%%;height:auto;border-radius:16px;margin-bottom:1.6rem" />'
        '<div class="blog-article-body">%s</div>%s</div></div>'
        % (web(b["img"]), b["title"], b["body"], cta()))
    ROUTES.append(page(
        "/blog/%s/" % b["slug"], "blog",
        b["title"] + " | Konya Diş Hekimi", b["excerpt"], b["title"], content,
        [breadcrumb([("Ana Sayfa", "/"), ("Blog", "/blog/"), (b["title"], "/blog/%s/" % b["slug"])]),
         {"@type": "BlogPosting", "@id": ORIGIN + "/blog/%s/#post" % b["slug"],
          "headline": b["title"], "description": b["excerpt"],
          "url": ORIGIN + "/blog/%s/" % b["slug"],
          "image": ORIGIN + "/assets/treatments/" + b["img"],
          "datePublished": b["date"], "dateModified": b["date"],
          "inLanguage": "tr-TR", "keywords": b["kw"],
          "author": ORG_REF, "publisher": ORG_REF,
          "mainEntityOfPage": {"@type": "WebPage", "@id": ORIGIN + "/blog/%s/" % b["slug"]}}],
        "/blog/", og_img=ORIGIN + "/assets/treatments/" + b["img"], og_type="article"))

# ============================================================ İLETİŞİM
contact_content = hero("İletişim – Konya Diş Hekimi",
                       "Bize ulaşın, gülüşünüze birlikte yön verelim. Çağrı merkezi: 444 34 42.",
                       [("Ana Sayfa", "/"), ("İletişim", "/iletisim/")]) + """
<div class="section"><div class="container">
  <div class="contact-wrap">
    <div class="contact-info reveal">
      <span class="section-tag">Bize Yazın</span>
      <h2 class="section-title" style="text-align:left">Bilgi Talebi</h2>
      <p class="section-desc">Tüm şubelerimiz için aşağıdaki formu kullanabilir veya doğrudan şube numaralarımızdan arayabilirsiniz. Pazar dahil her gün 23:00'a kadar açığız.</p>
      <ul class="contact-list">
        <li><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span> <a href="/subeler/karatay/">Karatay</a>: Çimenlik Mah. Fetih Cad. No:268A — <a href="tel:+905467332713">0546 733 27 13</a></li>
        <li><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span> <a href="/subeler/selcuklu/">Selçuklu</a>: Parsana Mah. Kaletaş Cad. Selçuker İş Merkezi — <a href="tel:+905513424442">0551 342 44 42</a></li>
        <li><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></span> <a href="/subeler/meram/">Meram</a>: Melikşah Mah. Akkonak Sk. No:4/1 — <a href="tel:+905525994959">0552 599 49 59</a></li>
        <li><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span> Çağrı Merkezi: 444 34 42</li>
      </ul>
    </div>
    <form class="contact-form reveal" id="pageContactForm">
      <div class="hp-field" aria-hidden="true"><label>Bu alanı boş bırakın<input type="text" name="company_url" tabindex="-1" autocomplete="off" /></label></div>
      <div class="form-row">
        <div class="form-group"><label for="pc-name">Ad Soyad</label><input type="text" id="pc-name" name="name" required placeholder="Adınız Soyadınız" /></div>
        <div class="form-group"><label for="pc-phone">Telefon</label><input type="tel" id="pc-phone" name="phone" required placeholder="05XX XXX XX XX" /></div>
      </div>
      <div class="form-group"><label for="pc-branch">Şube</label><select id="pc-branch" name="branch"><option value="Karatay">Karatay</option><option value="Selçuklu">Selçuklu</option><option value="Meram">Meram</option></select></div>
      <div class="form-group"><label for="pc-msg">Mesajınız</label><textarea id="pc-msg" name="message" rows="4" required placeholder="Mesajınızı yazın..."></textarea></div>
      <button type="submit" class="btn btn-primary btn-block">Gönder</button>
      <p class="form-status" id="pcStatus" role="status" aria-live="polite"></p>
    </form>
  </div>
</div></div>
"""
ROUTES.append(page(
    "/iletisim/", "contact",
    "İletişim – Karatay, Selçuklu, Meram Şubeleri | Konya Diş Hekimi",
    "Konya Diş Hekimi iletişim: 3 şube telefon ve adresleri. Çağrı merkezi 444 34 42. Pazar dahil 23:00'a kadar açığız. Hemen randevu alın.",
    "İletişim", contact_content,
    [breadcrumb([("Ana Sayfa", "/"), ("İletişim", "/iletisim/")]),
     {"@type": "ContactPage", "@id": ORIGIN + "/iletisim/#webpage", "url": ORIGIN + "/iletisim/",
      "name": "İletişim – Konya Diş Hekimi", "about": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
    "/iletisim/",
    title_en="Contact – Karatay, Selçuklu, Meram Branches | Konya Diş Hekimi",
    desc_en="Contact Konya Diş Hekimi: 3 branch phones and addresses. Call center 444 34 42. Open until 23:00 every day, Sundays included."))

# ============================================================ SITEMAP
SITEMAP_URLS = [("/", "1.0", "2026-06-11")]
for r in ROUTES:
    pr = "0.9" if (r.count("/") <= 2) else "0.7"
    if r == "/gece-acik-dis-klinigi-konya/":
        pr = "0.9"
    SITEMAP_URLS.append((r, pr, "2026-06-11"))
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pr, lm in SITEMAP_URLS:
    sm.append("  <url>")
    sm.append("    <loc>%s%s</loc>" % (ORIGIN, u))
    sm.append("    <lastmod>%s</lastmod>" % lm)
    sm.append("    <changefreq>%s</changefreq>" % ("weekly" if u == "/" else "monthly"))
    sm.append("    <priority>%s</priority>" % pr)
    sm.append("  </url>")
sm.append("</urlset>")
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(sm) + "\n")

# ============================================================ 404
nf_content = hero(
    "Sayfa Bulunamadı (404)",
    "Aradığınız sayfa taşınmış veya kaldırılmış olabilir.",
    [("Ana Sayfa", "/"), ("404", "/404.html")]
) + ('<div class="section"><div class="container container-narrow">'
     '<p>Üzgünüz, aradığınız sayfaya ulaşılamadı. Aşağıdaki bağlantılardan devam edebilirsiniz:</p>'
     '<ul class="tm-list">'
     '<li><a href="/">Ana Sayfa</a></li>'
     '<li><a href="/tedaviler/">Tedavilerimiz</a></li>'
     '<li><a href="/gece-acik-dis-klinigi-konya/">Gece Açık &amp; Acil Diş</a></li>'
     '<li><a href="/blog/">Blog</a></li>'
     '<li><a href="/iletisim/">İletişim</a></li></ul>' + cta() + '</div></div>')
nf_head = (HEAD_TMPL
           .replace("{{TITLE}}", "Sayfa Bulunamadı – Konya Diş Hekimi")
           .replace("{{DESC}}", "Aradığınız sayfa bulunamadı. Ana sayfa, tedaviler veya iletişim sayfamızdan devam edebilirsiniz.")
           .replace("{{CANON}}", ORIGIN + "/404.html")
           .replace("{{OGTYPE}}", "website")
           .replace("{{OGIMG}}", ORIGIN + "/assets/hero/hero1.jpg")
           .replace("{{VERIFY}}", VERIFY_META)
           .replace("{{SCHEMA}}", json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "404 – Sayfa Bulunamadı"}, ensure_ascii=False, indent=2))
           .replace("index, follow", "noindex, follow"))
nf_body = ('data-page="home" data-title-tr="Sayfa Bulunamadı – Konya Diş Hekimi" '
           'data-title-en="Page Not Found – Konya Diş Hekimi" '
           'data-desc-tr="Aradığınız sayfa bulunamadı." data-desc-en="Page not found."')
nf_top = CHROME_TOP.replace('class="nav-link active"', 'class="nav-link"')
nf_html = ("<!DOCTYPE html>\n<html lang=\"tr\" data-skin=\"navy\">\n" + nf_head + "\n<body " + nf_body +
           ">\n\n    " + nf_top + '<main id="main">\n' + nf_content + "\n    " + CHROME_BOTTOM)
with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(_stamp(nf_html))

# ============================================================ home (index.html)
# The home page is hand-maintained, but its shared css/js references still need
# the cache-busting fingerprint. Re-stamp index.html in place (idempotent).
_home_path = os.path.join(ROOT, "index.html")
with open(_home_path, encoding="utf-8") as fh:
    _home = fh.read()
# Inject centrally-managed verification tokens between the home <head> markers.
_home = re.sub(r'<!--VERIFY:START-->.*?<!--VERIFY:END-->',
               '<!--VERIFY:START-->' + VERIFY_META + '<!--VERIFY:END-->',
               _home, flags=re.S)
_home_stamped = _stamp(_home)
if _home_stamped != _home:
    with open(_home_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_home_stamped)
    print("   index.html -> css/js fingerprint updated (?v=%s)" % ASSET_VER)

print("Asset fingerprint (?v=) = %s" % ASSET_VER)

print("Generated %d sub-pages + 404 + sitemap (%d urls)." % (len(ROUTES), len(SITEMAP_URLS)))
for r in ROUTES:
    print("  ", r)
