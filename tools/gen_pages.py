# -*- coding: utf-8 -*-
"""
Dentual Konya — static page generator (SEO multi-page build).

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
ORIGIN = "https://dentualkonya.com"

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
                h.update(fh.read())
        except OSError:
            pass
    return h.hexdigest()[:8]

ASSET_VER = _asset_ver("css/style.css", "js/script.js", "js/analytics.js")

def _stamp(html):
    """Strip any existing ?v=… then re-append the current fingerprint to the
    shared css/js references. Idempotent (safe to run repeatedly)."""
    html = re.sub(r'(/(?:css/style\.css|js/script\.js|js/analytics\.js))\?v=[0-9a-f]+',
                  r'\1', html)
    for ref in ("/css/style.css", "/js/script.js", "/js/analytics.js"):
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
    <meta name="author" content="Dentual Konya" />
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
    <meta property="og:site_name" content="Dentual Konya" />
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
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="/css/style.css" />
    <script>try{if(localStorage.getItem('dentual-ann-closed')==='1')document.documentElement.classList.add('ann-dismissed');}catch(e){}</script>

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
    html = ("<!DOCTYPE html>\n<html lang=\"tr\">\n" + head + "\n<body " + body_attrs +
            ">\n\n    <a class=\"skip-link\" href=\"#main\">İçeriğe geç</a>\n\n    " + top +
            '<main id="main" tabindex="-1">\n' + content + "\n    " + CHROME_BOTTOM)
    out_dir = os.path.join(ROOT, route.strip("/").replace("/", os.sep))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
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
    "Konya Diş Kliniği Dentual Hakkında",
    "Konya'da gülüşlere değer katıyoruz — tecrübeli kadro, hasta odaklı yaklaşım.",
    [("Ana Sayfa", "/"), ("Hakkımızda", "/hakkimizda/")]
) + """
<div class="section"><div class="container about-intro">
  <div class="about-text reveal">
    <span class="section-tag">Biz Kimiz?</span>
    <h2 class="section-title" style="text-align:left">Güvenle Tedavi Ediyoruz</h2>
    <p>Dentual, Karatay, Selçuklu ve Meram şubeleriyle Konya'nın güvenilir ağız ve diş sağlığı polikliniğidir. En değerli varlık olan insan, kuruluşumuzun merkezinde yer alır; güven ve mutlu çözümler odak noktamızı oluşturur.</p>
    <p>Tecrübeli hekimlerimizle multidisipliner yaklaşıma önem veriyoruz. Ağız ve diş sağlığında teşhis ve tedavide çok yönlü yaklaşım, disiplinli çalışma ve en önemlisi hastanın ne istediği bizim için önceliklidir.</p>
    <p>Hastalarımızı uzun uzun dinler, modern ve güncel tedavi yöntemleriyle mutlu sona ulaşırız. Üstelik <strong>pazar dahil her gün gece 23:00'a kadar</strong> açık olarak, Konya'da gece açık nöbetçi diş hekimi hizmeti sunuyoruz.</p>
  </div>
  <div class="about-image reveal">
    <img src="/assets/hero/about-dentual.webp" alt="Dentual Konya diş kliniğinde hekim ve hasta" loading="lazy" width="600" height="450" />
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
  <div class="section-head reveal"><span class="section-tag">Neden Biz?</span><h2 class="section-title">Dentual Farkı</h2></div>
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
    "Hakkımızda – Konya'nın Güvenilir Diş Kliniği | Dentual",
    "Dentual Konya'nın uzman hekim kadrosu ve hasta odaklı yaklaşımı. 10+ uzman hekim, 9000+ mutlu hasta, 3 şube. Gece açık nöbetçi diş hekimi.",
    "Hakkımızda",
    about_content,
    [breadcrumb([("Ana Sayfa", "/"), ("Hakkımızda", "/hakkimizda/")]),
     {"@type": "AboutPage", "@id": ORIGIN + "/hakkimizda/#webpage", "url": ORIGIN + "/hakkimizda/",
      "name": "Hakkımızda – Dentual Konya", "about": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
    "/hakkimizda/",
    title_en="About Us – Konya's Trusted Dental Clinic | Dentual",
    desc_en="Dentual Konya's expert dentists and patient-focused care. 10+ specialists, 9000+ happy patients, 3 branches. Night-open emergency dentist."))

# ============================================================ TREATMENTS DATA
TREATMENTS = [
    {"slug": "implant", "title": "İmplant Tedavisi",
     "sub": "Tek diş eksikliğinden tam dişsizliğe kadar en iyi ve kalıcı çözüm.",
     "img": "implant.jpg",
     "desc": "İmplantlar günümüzde tek diş eksikliklerinin giderilmesinde olduğu kadar, tamamen veya kısmi dişsizliği olan bireylerin tedavisinde de en iyi seçenektir. Çene kemiğine yerleştirilen titanyum yapay kök, kemik dokusuyla kaynaşarak doğal dişe en yakın sağlam bir temel oluşturur. Konya'da implant tedavisi için Dentual'ın üç şubesinde de uzman kadromuzla hizmetinizdeyiz.",
     "candidates": "Bir veya birden fazla dişi eksik olan, çene kemiği implant için yeterli olan ve sabit, doğal bir çözüm isteyen yetişkin hastalar için uygundur.",
     "process": [("Muayene & Görüntüleme", "Röntgen ve tomografi ile çene kemiği değerlendirilerek kişiye özel tedavi planı oluşturulur."),
                 ("Cerrahi Yerleştirme", "Lokal anestezi altında titanyum implant çene kemiğine konforlu şekilde yerleştirilir."),
                 ("Kaynaşma (Osseointegrasyon)", "İmplantın kemikle kaynaşması için birkaç aylık iyileşme süreci beklenir."),
                 ("Protez Dişin Takılması", "Kaynaşma tamamlanınca doğal dişlerinizle uyumlu protez diş implant üzerine sabitlenir.")],
     "points": ["Doğal görünüm ve fonksiyon", "Doğru bakımla ömür boyu kullanım", "Komşu dişlere zarar vermez", "Çene kemiği erimesini önler"]},
    {"slug": "gulus-estetigi", "title": "Gülüş Estetiği",
     "sub": "Güldüğünüzde ilk göze çarpan ön dişleriniz için kişiye özel estetik planlama.",
     "img": "gulus-estetigi.jpg",
     "desc": "Gülüş estetiği; yüz şekli, dudak yapısı ve diş eti çizgisi göz önünde bulundurularak kişiye özel planlanan bir uygulamadır. Lamina, zirkonyum kaplama ve diş beyazlatma gibi yöntemlerle dişlerin rengi, formu ve dizilimi yeniden tasarlanır. Konya'da gülüş tasarımı için Dentual'da dijital planlama ile sonucu önceden görebilirsiniz.",
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
     "desc": "Kanal tedavisi, dişin merkezindeki canlı dokunun (pulpa) çıkartılarak kanalın uygun dolgu maddeleriyle doldurulması işlemidir. Çürük veya travma nedeniyle iltihaplanan diş sinirinin temizlenmesiyle, çekilmesi gereken dişler kurtarılır ve ağrı ortadan kaldırılır. Gece bastıran şiddetli diş ağrılarında Dentual'ın gece açık şubeleri yanınızdadır.",
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
     "desc": "Pedodonti, 0-14 yaş çocukların süt ve daimi dişlerinin sağlığını korumanın yanı sıra problemleri tedavi etmeyi amaçlar. Uzman hekimlerimiz, çocukların diş hekimi korkusu yaşamadan sağlıklı dişlere sahip olması için özel teknikler kullanır. Dentual Çocuk kliniğimizde minik hastalarımıza özel, neşeli bir ortam sunuyoruz.",
     "candidates": "0-14 yaş aralığındaki, koruyucu diş hekimliği veya süt/daimi diş tedavisi ihtiyacı olan tüm çocuklar için uygundur.",
     "process": [("Tanışma & Muayene", "Çocuğun güven duyması sağlanarak nazik bir şekilde ağız ve diş muayenesi yapılır."),
                 ("Koruyucu Uygulamalar", "Flor ve fissür örtücü gibi koruyucu işlemlerle çürük riski azaltılır."),
                 ("Tedavi", "Gerekli durumlarda süt ve daimi diş dolguları ile uygun tedaviler uygulanır."),
                 ("Düzenli Kontrol", "Diş gelişiminin sağlıklı ilerlemesi için periyodik kontroller planlanır.")],
     "points": ["Ağız hijyeni eğitimi", "Flor ve fissür örtücü uygulamaları", "Süt ve daimi diş dolgu/tedavileri", "Çocuk dostu, korkutmayan yaklaşım"]},
]
T_TITLE = {
    "implant": "İmplant Tedavisi Konya – Diş İmplantı Süreci & Fiyat | Dentual",
    "gulus-estetigi": "Gülüş Estetiği Konya – Zirkonyum, Lamina, Diş Beyazlatma | Dentual",
    "ortodonti": "Ortodonti Konya – Diş Teli & Şeffaf Plak Tedavisi | Dentual",
    "kanal-tedavisi": "Kanal Tedavisi Konya (Endodonti) – Ağrısız Tedavi | Dentual",
    "cerrahi": "Ağız & Çene Cerrahisi Konya – 20'lik Diş Çekimi | Dentual",
    "cocuk-dis-hekimligi": "Çocuk Diş Hekimi Konya (Pedodonti) – Dentual Çocuk",
}
T_DESC = {
    "implant": "Konya'da implant tedavisi: diş implantı süreci, kimlere uygun, avantajları. Dentual'ın uzman kadrosuyla doğal ve kalıcı çözüm. Randevu: 444 34 42.",
    "gulus-estetigi": "Konya gülüş estetiği: zirkonyum kaplama, lamina ve diş beyazlatma ile kişiye özel gülüş tasarımı. Dijital planlama ile Dentual'da. Randevu: 444 34 42.",
    "ortodonti": "Konya ortodonti: diş teli ve şeffaf plak tedavisi ile çapraşık dişler ve kapanış sorunlarına çözüm. Her yaşa uygun. Dentual. Randevu: 444 34 42.",
    "kanal-tedavisi": "Konya kanal tedavisi (endodonti): iltihaplı dişi çekmeden kurtaran ağrısız modern tedavi. Gece açık şubelerle Dentual. Randevu: 444 34 42.",
    "cerrahi": "Konya ağız ve çene cerrahisi: gömülü 20'lik diş çekimi, kist ve implant cerrahisi. Steril koşullarda uzman kadro. Dentual. Randevu: 444 34 42.",
    "cocuk-dis-hekimligi": "Konya çocuk diş hekimi (pedodonti): 0-14 yaş süt ve daimi diş tedavisi, koruyucu uygulamalar. Korkutmayan Dentual Çocuk kliniği. Randevu: 444 34 42.",
}

def treatment_card(t):
    return ('<a href="/tedaviler/%s/" class="treatment-card reveal">'
            '<div class="treatment-img"><img src="/assets/treatments/%s" alt="%s — Konya Dentual diş kliniği" loading="lazy" width="400" height="190" /></div>'
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
    "Diş Tedavileri Konya – İmplant, Gülüş Estetiği, Ortodonti | Dentual",
    "Konya'da implant, gülüş estetiği, ortodonti, kanal tedavisi, cerrahi ve çocuk diş hekimliği. Dentual'da uzman kadroyla güvenli tedavi. Randevu: 444 34 42.",
    "Tedavilerimiz", tindex_content,
    [breadcrumb([("Ana Sayfa", "/"), ("Tedaviler", "/tedaviler/")]),
     {"@type": "CollectionPage", "@id": ORIGIN + "/tedaviler/#webpage", "url": ORIGIN + "/tedaviler/",
      "name": "Diş Tedavileri – Dentual Konya", "isPartOf": {"@id": ORIGIN + "/#website"},
      "about": ORG_REF}],
    "/tedaviler/",
    title_en="Dental Treatments Konya – Implants, Smile, Orthodontics | Dentual",
    desc_en="Implants, smile aesthetics, orthodontics, root canal, surgery and pediatric dentistry in Konya. Expert care at Dentual. Call 444 34 42."))

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
        '<img src="/assets/treatments/%s" alt="%s — Konya Dentual" loading="lazy" width="760" height="360" style="width:100%%;height:auto;border-radius:16px;margin-bottom:1.6rem" />'
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
     "Evet. Dentual olarak Karatay, Selçuklu ve Meram şubelerimizde pazar dahil her gün gece 23:00'a kadar açığız. Gece bastıran diş ağrılarınızda nöbetçi diş hekimimiz size hizmet verir."),
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
  <p>Diş ağrısı çoğu zaman en kötü anda, akşam veya gece bastırır. <strong>Dentual olarak Konya'da gece açık nöbetçi diş hekimi</strong> hizmetiyle yanınızdayız: Karatay, Selçuklu ve Meram şubelerimizde <strong>pazar dahil her gün 09:00–23:00 arası</strong> acil ve planlı diş tedavileriniz için buradayız.</p>
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
      "name": "Dentual Konya – Gece Açık Nöbetçi Diş Kliniği",
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
    "karatay": "Karatay Diş Kliniği Konya – Nöbetçi Diş Hekimi | Dentual",
    "selcuklu": "Selçuklu Diş Kliniği – Gece Açık Nöbetçi Diş Hekimi | Dentual",
    "meram": "Meram Diş Kliniği Konya – Diş Hekimi | Dentual",
}
B_DESC = {
    "karatay": "Karatay diş kliniği Dentual: Çimenlik Mah. Fetih Cad. Pazar dahil her gün 23:00'a kadar açık nöbetçi diş hekimi. Randevu: 0546 733 27 13.",
    "selcuklu": "Selçuklu'da gece açık diş kliniği. Parsana Mah. Kaletaş Cad. Pazar dahil 23:00'a kadar nöbetçi diş hekimi. Randevu ve acil: 0551 342 44 42.",
    "meram": "Meram diş kliniği Dentual: Melikşah Mah. Akkonak Sk. Pazar dahil her gün 23:00'a kadar açık diş hekimi. Randevu: 0552 599 49 59.",
}
B_H1 = {
    "karatay": "Karatay Diş Kliniği — Dentual Konya",
    "selcuklu": "Selçuklu Diş Kliniği — Gece Açık Nöbetçi Diş Hekimi",
    "meram": "Meram Diş Kliniği — Dentual Konya",
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
        '<a href="https://wa.me/%s" class="branch-link" target="_blank" rel="noopener">WhatsApp ile İletişim &rarr;</a></div></div>'
        '<div class="container container-narrow" style="margin-top:2.4rem">'
        '<p>%s şubemiz, Dentual güvencesiyle ağız ve diş sağlığınız için hizmetinizdedir. İmplant, gülüş estetiği, ortodonti, kanal tedavisi ve çocuk diş hekimliği dahil tüm tedavilerimiz bu şubemizde sunulur. %s</p>'
        '<p>Gece bastıran acil durumlar için <a href="/gece-acik-dis-klinigi-konya/">Konya gece açık nöbetçi diş hekimi</a> sayfamıza bakabilirsiniz.</p>'
        '</div></div></div>'
        % (b["map"], b["name"], b["name"], b["addr"], b["telraw"], b["tel"], b["telraw"].replace("+", ""), b["name"],
           ("Selçuklu ve çevresinde gece geç saatte diş hekimi arayanlar için nöbet hizmeti veririz." if b["slug"] == "selcuklu" else "Pazar dahil her gün geç saatlere kadar açığız."))
    ) + bf_html + '<div class="section"><div class="container">' + cta() + '</div></div>'
    dentist_node = {
        "@type": "Dentist", "@id": ORIGIN + "/subeler/%s/#dentist" % b["slug"],
        "name": "Dentual Diş Kliniği - %s" % b["name"], "url": ORIGIN + "/subeler/%s/" % b["slug"],
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
<p><a href="/tedaviler/cocuk-dis-hekimligi/">Dentual Çocuk kliniğimizde</a>, minik hastalarımıza özel, neşeli ve korkutmayan bir ortam sunuyoruz. Çocuğunuzun ilk diş deneyimini keyifli bir maceraya dönüştürüyoruz.</p>"""},
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
<p>Bu öneriler geçici rahatlama sağlar; ağrının nedeni devam ediyordur. İyi haber şu: <strong>Dentual olarak pazar dahil her gün gece 23:00'a kadar açığız.</strong> Geç saatte bastıran diş ağrılarınızda <a href="/gece-acik-dis-klinigi-konya/">nöbetçi diş hekimi</a> hizmetimizle yanınızdayız. Çağrı merkezi: 444 34 42.</p>"""},
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
    "Diş Sağlığı Blogu – Uzman Tavsiyeleri | Dentual Konya",
    "Ağız ve diş sağlığı hakkında uzman yazıları: implant bakımı, çocuk diş sağlığı, gülüş tasarımı ve gece diş ağrısı önerileri. Dentual Konya.",
    "Bilgi Merkezi", blog_index,
    [breadcrumb([("Ana Sayfa", "/"), ("Blog", "/blog/")]),
     {"@type": "Blog", "@id": ORIGIN + "/blog/#blog", "url": ORIGIN + "/blog/",
      "name": "Dentual Konya Blog", "publisher": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
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
        b["title"] + " | Dentual Konya", b["excerpt"], b["title"], content,
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
contact_content = hero("İletişim – Dentual Konya",
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
    "İletişim – Karatay, Selçuklu, Meram Şubeleri | Dentual Konya",
    "Dentual Konya iletişim: 3 şube telefon ve adresleri. Çağrı merkezi 444 34 42. Pazar dahil 23:00'a kadar açığız. Hemen randevu alın.",
    "İletişim", contact_content,
    [breadcrumb([("Ana Sayfa", "/"), ("İletişim", "/iletisim/")]),
     {"@type": "ContactPage", "@id": ORIGIN + "/iletisim/#webpage", "url": ORIGIN + "/iletisim/",
      "name": "İletişim – Dentual Konya", "about": ORG_REF, "isPartOf": {"@id": ORIGIN + "/#website"}}],
    "/iletisim/",
    title_en="Contact – Karatay, Selçuklu, Meram Branches | Dentual Konya",
    desc_en="Contact Dentual Konya: 3 branch phones and addresses. Call center 444 34 42. Open until 23:00 every day, Sundays included."))

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
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
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
           .replace("{{TITLE}}", "Sayfa Bulunamadı – Dentual Konya")
           .replace("{{DESC}}", "Aradığınız sayfa bulunamadı. Ana sayfa, tedaviler veya iletişim sayfamızdan devam edebilirsiniz.")
           .replace("{{CANON}}", ORIGIN + "/404.html")
           .replace("{{OGTYPE}}", "website")
           .replace("{{OGIMG}}", ORIGIN + "/assets/hero/hero1.jpg")
           .replace("{{VERIFY}}", VERIFY_META)
           .replace("{{SCHEMA}}", json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "404 – Sayfa Bulunamadı"}, ensure_ascii=False, indent=2))
           .replace("index, follow", "noindex, follow"))
nf_body = ('data-page="home" data-title-tr="Sayfa Bulunamadı – Dentual Konya" '
           'data-title-en="Page Not Found – Dentual Konya" '
           'data-desc-tr="Aradığınız sayfa bulunamadı." data-desc-en="Page not found."')
nf_top = CHROME_TOP.replace('class="nav-link active"', 'class="nav-link"')
nf_html = ("<!DOCTYPE html>\n<html lang=\"tr\">\n" + nf_head + "\n<body " + nf_body +
           ">\n\n    " + nf_top + '<main id="main">\n' + nf_content + "\n    " + CHROME_BOTTOM)
with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as fh:
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
    with open(_home_path, "w", encoding="utf-8") as fh:
        fh.write(_home_stamped)
    print("   index.html -> css/js fingerprint updated (?v=%s)" % ASSET_VER)

print("Asset fingerprint (?v=) = %s" % ASSET_VER)

print("Generated %d sub-pages + 404 + sitemap (%d urls)." % (len(ROUTES), len(SITEMAP_URLS)))
for r in ROUTES:
    print("  ", r)
