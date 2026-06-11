/* ============================================================
   DENTUAL KONYA — SCRIPT.JS
   Vanilla JS · SPA routing · Preloader · Dark mode · Sliders
   ============================================================ */
(function () {
    'use strict';

    /* ---------- I18N STATE ---------- */
    const SUPPORTED_LANGS = ['tr', 'en'];
    const RTL_LANGS = ['ar'];
    let currentLang = localStorage.getItem('dentual-lang') || 'tr';
    if (SUPPORTED_LANGS.indexOf(currentLang) === -1) currentLang = 'tr';

    /* ---------- DATA ---------- */
    const PAGE_TITLES = {
        tr: {
            home: 'Dentual Konya | Güvenle Tedavi Ediyoruz',
            about: 'Hakkımızda - Dentual Konya',
            treatments: 'Tedaviler - Dentual Konya',
            blog: 'Bilgi Merkezi (Blog) - Dentual Konya',
            contact: 'İletişim - Dentual Konya'
        },
        en: {
            home: 'Dentual Konya | We Treat with Confidence',
            about: 'About Us - Dentual Konya',
            treatments: 'Treatments - Dentual Konya',
            blog: 'Blog - Dentual Konya',
            contact: 'Contact - Dentual Konya'
        }
    };

    // Per-page meta descriptions (SEO for SPA navigation)
    const PAGE_DESCS = {
        tr: {
            home: 'Dentual Konya - Karatay, Selçuklu ve Meram şubeleriyle ağız ve diş sağlığı polikliniği. Selçuklu şubemiz dahil pazar günleri de gece 23:30\'a kadar açık nöbetçi diş hekimi.',
            about: 'Dentual Konya hakkında: tecrübeli hekim kadromuz, multidisipliner ve hasta odaklı yaklaşımımızla güvenle tedavi ediyoruz.',
            treatments: 'İmplant, gülüş estetiği, ortodonti, kanal tedavisi, cerrahi ve pedodonti. Dentual Konya tedavi hizmetleri ve detayları.',
            blog: 'Ağız ve diş sağlığı hakkında uzman tavsiyeleri: implant bakımı, çocuk diş sağlığı, gülüş tasarımı ve acil diş ağrısı önerileri.',
            contact: 'Dentual Konya iletişim: Karatay, Selçuklu ve Meram şube telefon numaraları. Çağrı merkezi 444 34 42.'
        },
        en: {
            home: 'Dentual Konya - oral and dental health clinic with Karatay, Selçuklu and Meram branches. Our Selçuklu branch is now open at night, until 23:30 every day including Sundays.',
            about: 'About Dentual Konya: our experienced dentists treat you with confidence through a multidisciplinary, patient-focused approach.',
            treatments: 'Implants, smile aesthetics, orthodontics, root canal, surgery and pedodontics. Dentual Konya treatments and details.',
            blog: 'Expert advice on oral and dental health: implant care, children\'s dental health, smile design and emergency toothache tips.',
            contact: 'Contact Dentual Konya: Karatay, Selçuklu and Meram branch phone numbers. Call center 444 34 42.'
        }
    };

    // Typewriter phrases per language
    const TW_PHRASES = {
        tr: ['Güvenle Tedavi Ediyoruz', 'Sağlıklı Gülüşler Tasarlıyoruz', 'Konya\'da Yanınızdayız'],
        en: ['We Treat with Confidence', 'We Design Healthy Smiles', 'By Your Side in Konya']
    };

    // English dictionary for static UI text (keyed by data-i18n)
    const DICT = {
        en: {
            'nav.home': 'Home', 'nav.about': 'About Us', 'nav.treatments': 'Treatments', 'nav.blog': 'Blog', 'nav.contact': 'Contact', 'nav.book': 'Call Us',
            'ann.text': 'Our Selçuklu branch is now <strong>open at night!</strong>',
            'blog.heroTitle': 'Knowledge Center', 'blog.heroSub': 'Expert advice and up-to-date articles on oral and dental health.',
            'blog.back': '← All Articles', 'blog.ctaText': 'Looking for professional help on this topic?', 'blog.ctaBtn': 'Contact Us',
            'hero.badge': "Konya's Trusted Dental Care Center",
            'hero.night': 'Open Until 23:30 Every Day, Sundays Included',
            'hero.subtitle': 'With modern technology and our expert team, we are here for healthy smiles. At your service with our Karatay, Selçuklu and Meram branches.',
            'hero.cta1': 'Call Us', 'hero.cta2': 'Our Treatments',
            'emergency.title': 'Emergency & Night Dental Care',
            'emergency.sub': "Toothache won't wait. <strong>Every day until 23:30, Sundays included</strong>, we're here for your emergency and planned treatments.",
            'emergency.call': 'Call Now: 444 34 42', 'emergency.wa': 'Message on WhatsApp',
            'stats.doctors': 'Specialist Dentists', 'stats.staff': 'Support Staff', 'stats.patients': 'Happy Patients', 'stats.branches': 'Branches',
            'htreat.tag': 'Our Treatments', 'htreat.title': 'Services We Offer', 'htreat.desc': 'A selection of our treatments that add value to your smile. Click the cards for details.', 'htreat.all': 'See All Treatments',
            'brands.tag': 'Our Brands', 'brands.title': 'The Dentual Family', 'brands.desc': 'From adults to children, we offer oral and dental health solutions for every member of your family.',
            'cocuk.tag': 'Dentual Kids', 'cocuk.title': "Little Ones' Dental Friend", 'cocuk.desc': "With our Dentual Kids clinic — specially designed so children reach healthy teeth while having fun and without fear of the dentist — we are by our little guests' side.",
            'cocuk.f1t': 'Reassuring Approach', 'cocuk.f1d': 'A safe experience with our patient and caring dentists.',
            'cocuk.f2t': 'Pedodontics Experts', 'cocuk.f2d': "Expert team in children's dentistry for ages 0-14.",
            'cocuk.f3t': 'Preventive Care', 'cocuk.f3d': 'Protection against cavities with fluoride and fissure sealants.',
            'cocuk.f4t': 'Fun Environment', 'cocuk.f4d': 'A child-friendly, cheerful and relaxing clinic atmosphere.',
            'cocuk.cta': 'Contact Us',
            'branch.tag': 'Our Branches', 'branch.title': 'The Nearest Dentual to You', 'branch.desc': 'At three central locations in Konya, we serve you with the same quality and trust.',
            'branch.map': 'View Map', 'branch.wa': 'Contact via WhatsApp →',
            'branch.karatay': 'Karatay Branch', 'branch.selcuklu': 'Selçuklu Branch', 'branch.meram': 'Meram Branch',
            'doc.tag': 'Our Dentists', 'doc.title': 'Our Expert Team', 'doc.desc': 'A reliable and comfortable treatment experience with our experienced dentists.',
            'rev.tag': 'Reviews', 'rev.title': 'What Our Patients Say', 'rev.desc': 'Real patient experiences from Google Maps.', 'rev.count': 'Based on 366 Google reviews', 'rev.all': 'See All on Google',
            'faq.tag': 'FAQ', 'faq.title': 'Frequently Asked Questions',
            'hcontact.tag': 'Contact', 'hcontact.title': 'Get in Touch', 'hcontact.desc': "Have questions? Fill out the form and we'll get back to you as soon as possible.",
            'contact.callcenter': 'Call Center: 444 34 42', 'contact.hours': 'Open every day until 23:30 (Sundays included)',
            'form.name': 'Full Name', 'form.namePh': 'Your Full Name', 'form.phone': 'Phone', 'form.phonePh': '05XX XXX XX XX', 'form.email': 'E-mail',
            'form.branch': 'Branch', 'form.message': 'Your Message', 'form.messagePh': 'Write your message...', 'form.send': 'Send Message', 'form.send2': 'Send',
            'about.heroTitle': 'About Us', 'about.heroSub': 'Adding value to smiles in Konya.',
            'about.tag': 'Who Are We?', 'about.title': 'We Treat with Confidence',
            'about.p1': 'The human being, our most valuable asset, is at the center of our organization; trust and happy solutions form our focal point.',
            'about.p2': 'We attach great importance to a multidisciplinary approach with our experienced dentists. In oral and dental health, a versatile approach to diagnosis and treatment, disciplined work, and most importantly what the patient wants are essential.',
            'about.p3': 'We listen to our patients at length; reaching a happy ending with modern, up-to-date treatment methods is our greatest goal.',
            'about.mission': 'Our Mission', 'about.missionTxt': "To become Konya's most trusted dental health center by offering each patient personalized, scientific and ethical treatment plans.",
            'about.vision': 'Our Vision', 'about.visionTxt': 'To become a regional reference point in dentistry by combining technology with a people-focused approach.',
            'about.values': 'Our Values', 'about.valuesTxt': 'Transparency, patient satisfaction, hygiene, continuous education and honesty form the foundation of our work.',
            'why.tag': 'Why Us?', 'why.title': 'The Dentual Difference',
            'why.1': 'State-of-the-art digital imaging and treatment devices',
            'why.2': 'International-standard sterilization',
            'why.3': 'Painless and comfortable treatment methods',
            'why.4': 'Experienced and friendly expert team',
            'why.5': 'Transparent pricing and payment options',
            'why.6': 'Easy access with 3 central branches',
            'tpage.heroTitle': 'Our Treatments', 'tpage.heroSub': 'The services we offer for healthy and aesthetic smiles.',
            'cpage.heroTitle': 'Contact', 'cpage.heroSub': "Get in touch — let's shape your smile together.",
            'cpage.tag': 'Write to Us', 'cpage.title': 'Information Request', 'cpage.desc': 'You can use the form below for all our branches or call our branch numbers directly.',
            'footer.about': "Konya's trusted oral and dental health clinic. We're here for healthy smiles.",
            'footer.quick': 'Quick Links', 'footer.branches': 'Branches', 'footer.contact': 'Contact', 'footer.hours': 'Every day until 23:30 (Sundays included)', 'footer.copyright': '© 2026 Dentual Konya. All rights reserved.',
            'wa.title': 'Choose a Branch', 'wa.sub': 'How can we help you?',
            'tm.tag': 'Treatment', 'tm.candidates': 'Who Is It Suitable For?', 'tm.process': 'Treatment Process', 'tm.advantages': 'Advantages', 'tm.cta': 'Contact Us'
        }
    };

    // Form success messages per language
    const FORM_MSG = {
        tr: '✓ WhatsApp\'a yönlendiriliyorsunuz, lütfen mesajı gönderin.',
        en: '✓ Redirecting you to WhatsApp — please send the message.'
    };

    // Default prefilled message for all WhatsApp link buttons (per language)
    const WA_MSG = {
        tr: 'Merhaba, Dentual\'dan randevu ve bilgi almak istiyorum.',
        en: 'Hello, I would like to get an appointment and information from Dentual.'
    };

    const DOCTORS = [
        { name: 'Dt. M. Yasin Tekpınar', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/yasintekpinar.png' },
        { name: 'Dt. M. Emre Atalay', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/emreatalay.png' },
        { name: 'Uzm. Dt. Zeynep Tuğran', role: 'Pedodonti (Çocuk Diş) Uzmanı', roleEn: 'Pediatric Dentistry Specialist', img: 'assets/doctors/zeyneptugran.png' },
        { name: 'Uzm. Dt. Yahya Çubukçu', role: 'Çene Cerrahisi Uzmanı', roleEn: 'Oral & Maxillofacial Surgery Specialist', img: 'assets/doctors/yahyacubukcu.png' },
        { name: 'Uzm. Dt. Esra Pilancı', role: 'Ortodonti Uzmanı', roleEn: 'Orthodontics Specialist', img: 'assets/doctors/esrapilanci.png' },
        { name: 'Dt. Zuhal Karataş', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/zuhalkaratas.png' },
        { name: 'Dt. Rafet Bayrakçı', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/rafet.png' },
        { name: 'Dt. Bilal Kameroğlu', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/bilalkameroglu.png' },
        { name: 'Dt. Sena Kocabaş', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/senakocabas.png' },
        { name: 'Dt. Emre Alabay', role: 'Diş Hekimi', roleEn: 'Dentist', img: 'assets/doctors/emrealabay.png' }
    ];

    const REVIEWS = [
        { name: 'Ahmet APAK', initials: 'AA', color: '#0d4d4d', stars: 5, tag: 'Aile Diş Sağlığı', tagEn: 'Family Dental Care', text: 'Ailecek diş tedavisi olduğumuz bir hekim ve yer. Eğer diş hekiminize güveniyorsanız hayatınız bir tık kolaylaşır.', textEn: 'A dentist and place where our whole family gets treated. If you trust your dentist, life gets a little easier.' },
        { name: 'M. Raşit TORAMAN', initials: 'MT', color: '#11665f', stars: 5, tag: 'Genel Tedavi', tagEn: 'General Treatment', text: 'Herkese ayrı ayrı teşekkür ediyorum. Çağrı hocamıza ve tüm ekibe başarılar diliyorum.', textEn: 'I thank everyone individually. I wish success to Dr. Çağrı and the whole team.' },
        { name: 'Selin Doğan', initials: 'SD', color: '#14b8a6', stars: 5, tag: 'Gülüş Tasarımı', tagEn: 'Smile Design', text: 'Düğünüm öncesi gülüş tasarımı yaptırdım ve sonuç hayal ettiğimden çok daha iyi oldu! Dişlerimin rengi ve formu artık kusursuz. Hekimime ve tüm ekibe minnettarım, özgüvenim tamamen değişti.', textEn: 'I had a smile design before my wedding and the result was far better than I imagined! The color and shape of my teeth are now flawless. I am grateful to my dentist and the whole team — my confidence has completely changed.' },
        { name: 'Ayşe Vural', initials: 'AV', color: '#0a3f3c', stars: 5, tag: 'Pedodonti', tagEn: 'Pedodontics', text: 'Oğlum diş hekiminden çok korkardı. Pedodonti uzmanı doktor hanım o kadar sabırlı ve sevecen yaklaştı ki, çocuğum artık kontrole gitmek için sabırsızlanıyor. Çocuklarla iletişimleri gerçekten harika.', textEn: 'My son used to be very afraid of the dentist. The pedodontics specialist was so patient and kind that my child now can\'t wait to go for check-ups. Their communication with children is truly wonderful.' },
        { name: 'Büşra Şen', initials: 'BŞ', color: '#11665f', stars: 5, tag: 'Zirkonyum Kaplama', tagEn: 'Zirconium Crown', text: 'Ön dişlerime zirkonyum kaplama yaptırdım. Doğal görünümü inanılmaz, hiç yapay durmuyor ve renk uyumu mükemmel. İşçilik kalitesi çok yüksek. Dentual ekibine sağlıklı gülüşüm için teşekkür ederim.', textEn: 'I had zirconium crowns on my front teeth. The natural look is incredible — it doesn\'t look artificial at all and the color match is perfect. The craftsmanship is very high quality. Thanks to the Dentual team for my healthy smile.' },
        { name: 'Kemal Aslan', initials: 'KA', color: '#0d4d4d', stars: 5, tag: 'Geç Saat Hizmeti', tagEn: 'Late-Hours Service', text: 'Akşam geç saatte ani diş ağrımda açık olmaları beni kurtardı. Gece 23:00 gibi gittim, ilgilendiler ve ağrımı dindirdiler. Konya\'da bu saatte hizmet veren güvenilir bir yer olması çok değerli.', textEn: 'Being open late at night saved me during a sudden toothache. I went around 23:00, they took care of me and relieved my pain. It is invaluable to have a trustworthy place serving at this hour in Konya.' }
    ];

    const TREATMENTS = [
        {
            title: 'Ortodonti (Diş Teli & Şeffaf Plak)',
            img: 'assets/treatments/ortodonti.jpg',
            short: 'Diş çapraşıklıkları, dişler arası boşluklar ve ısırma problemleri için tel ve şeffaf plak tedavileri.',
            desc: 'Ortodonti tedavisi, dişlerin ve çenenin düzgün hizalanmasını sağlamak amacıyla yapılan bir dizi işlemdir. Çapraşık dişlerin düzeltilmesi, boşlukların kapatılması ve ısırık problemlerinin çözülmesini içerir. Tedavide metal teller, seramik aparatlar ve şeffaf plaklar gibi çeşitli araçlar kullanılır. Çocukluk ve ergenlik dönemlerinde başlayabileceği gibi yetişkinler de bu tedaviden faydalanabilir.',
            candidates: 'Çapraşık dişler, ısırık (kapanış) sorunları, dişler arasında anormal boşluklar veya çene pozisyonunda bozukluk olan her yaştan hasta uygun adaydır.',
            process: [
                { t: 'Detaylı Muayene & Planlama', d: 'Ağız muayenesi, panoramik röntgen ve gerektiğinde 3B görüntüleme ile dişlerin ve çenenin durumu değerlendirilir.' },
                { t: 'Aparatların Uygulanması', d: 'Size en uygun yöntem belirlenir; metal, seramik teller veya şeffaf plaklar uygulanır.' },
                { t: 'Düzenli Kontroller', d: 'Tedavi süresince periyodik kontrollerle aparatlar ayarlanır ve ilerleme takip edilir.' },
                { t: 'Pekiştirme (Sonrası Bakım)', d: 'Dişlerin yeni konumunu koruması için genellikle gece takılan pekiştirme apareyleri kullanılır.' }
            ],
            points: ['Metal, seramik ve şeffaf plak seçenekleri', 'Estetik ve daha çekici bir gülüş', 'Düzgün dişlerle kolay temizlik, azalan çürük riski', 'Çiğneme ve konuşmada işlevsel iyileşme'],
            titleEn: 'Orthodontics (Braces & Clear Aligners)',
            shortEn: 'Braces and clear aligner treatments for crooked teeth, gaps between teeth and biting problems.',
            descEn: 'Orthodontic treatment is a series of procedures aimed at properly aligning the teeth and jaw. It includes correcting crooked teeth, closing gaps and resolving bite problems. Various tools such as metal braces, ceramic appliances and clear aligners are used. It can begin in childhood and adolescence, and adults can also benefit from it.',
            candidatesEn: 'Suitable for patients of any age with crooked teeth, bite (occlusion) problems, abnormal gaps between teeth, or jaw position disorders.',
            processEn: [
                { t: 'Detailed Examination & Planning', d: 'The condition of the teeth and jaw is assessed with an oral exam, panoramic X-rays and, when needed, 3D imaging.' },
                { t: 'Fitting the Appliances', d: 'The most suitable method is chosen for you; metal, ceramic braces or clear aligners are applied.' },
                { t: 'Regular Check-ups', d: 'During treatment, the appliances are adjusted and progress is monitored with periodic check-ups.' },
                { t: 'Retention (Aftercare)', d: 'Retainers, usually worn at night, are used to keep the teeth in their new position.' }
            ],
            pointsEn: ['Metal, ceramic and clear aligner options', 'A more aesthetic, attractive smile', 'Easier cleaning with aligned teeth, reduced cavity risk', 'Functional improvement in chewing and speech']
        },
        {
            title: 'İmplant Tedavisi',
            img: 'assets/treatments/implant.jpg',
            short: 'Tek diş eksikliğinden tam dişsizliğe kadar en iyi ve kalıcı çözüm.',
            desc: 'İmplantlar günümüzde tek diş eksikliklerinin giderilmesinde olduğu kadar, tamamen veya kısmi dişsizliği olan bireylerin tedavisinde de en iyi seçenek haline gelmiştir. Çene kemiğine yerleştirilen titanyum yapay kök, kemik dokusuyla kaynaşarak doğal dişe en yakın sağlam bir temel oluşturur.',
            candidates: 'Bir veya birden fazla dişi eksik olan, çene kemiği implant için yeterli olan ve sabit, doğal bir çözüm isteyen yetişkin hastalar için uygundur.',
            process: [
                { t: 'Muayene & Görüntüleme', d: 'Röntgen ve tomografi ile çene kemiği değerlendirilerek kişiye özel tedavi planı oluşturulur.' },
                { t: 'Cerrahi Yerleştirme', d: 'Lokal anestezi altında titanyum implant çene kemiğine konforlu şekilde yerleştirilir.' },
                { t: 'Kaynaşma (Osseointegrasyon)', d: 'İmplantın kemikle kaynaşması için birkaç aylık iyileşme süreci beklenir.' },
                { t: 'Protez Dişin Takılması', d: 'Kaynaşma tamamlanınca, doğal dişlerinizle uyumlu protez diş implant üzerine sabitlenir.' }
            ],
            points: ['Doğal görünüm ve fonksiyon', 'Doğru bakımla ömür boyu kullanım', 'Komşu dişlere zarar vermez', 'Çene kemiği erimesini önler'],
            titleEn: 'Implant Treatment',
            shortEn: 'The best, most permanent solution from a single missing tooth to full toothlessness.',
            descEn: 'Implants have become the best option not only for replacing single missing teeth but also for treating individuals with full or partial toothlessness. The titanium artificial root placed in the jawbone fuses with the bone tissue to form a solid foundation closest to a natural tooth.',
            candidatesEn: 'Suitable for adult patients with one or more missing teeth and sufficient jawbone, who want a fixed, natural solution.',
            processEn: [
                { t: 'Examination & Imaging', d: 'The jawbone is evaluated with X-ray and tomography to create a personalized treatment plan.' },
                { t: 'Surgical Placement', d: 'The titanium implant is comfortably placed into the jawbone under local anesthesia.' },
                { t: 'Fusion (Osseointegration)', d: 'A healing period of a few months is required for the implant to fuse with the bone.' },
                { t: 'Fitting the Prosthetic Tooth', d: 'Once fusion is complete, a prosthetic tooth matching your natural teeth is fixed onto the implant.' }
            ],
            pointsEn: ['Natural look and function', 'Lifelong use with proper care', 'Does not harm neighboring teeth', 'Prevents jawbone loss']
        },
        {
            title: 'Gülüş Estetiği',
            img: 'assets/treatments/gulus-estetigi.jpg',
            short: 'Güldüğünüzde ilk göze çarpan ön dişleriniz için kişiye özel estetik planlama.',
            desc: 'Ön bölge, yani güldüğümüzde ilk göze çarpan dişlerimiz bizim için çok önemlidir. Gülüş estetiği; yüz şekli, dudak yapısı ve diş eti çizgisi göz önünde bulundurularak kişiye özel planlanan bir uygulamadır. Lamina, zirkonyum kaplama ve diş beyazlatma gibi yöntemlerle dişlerin rengi, formu ve dizilimi yeniden tasarlanır.',
            candidates: 'Diş renginden, formundan veya diziliminden memnun olmayan; daha estetik ve simetrik bir gülüş isteyen herkes için planlanabilir.',
            process: [
                { t: 'Analiz & Planlama', d: 'Yüz şekli, dudak yapısı ve diş eti çizgisi incelenerek kişiye özel gülüş planı hazırlanır.' },
                { t: 'Dijital Tasarım', d: 'Yeni gülüşünüz dijital ortamda tasarlanır ve uygulama öncesi sonuç öngörülür.' },
                { t: 'Uygulama', d: 'Lamina, zirkonyum kaplama veya diş beyazlatma yöntemleriyle dişler yeniden şekillendirilir.' },
                { t: 'Son Kontrol', d: 'Uyum ve estetik açısından son rötuşlar yapılarak gülüşünüz tamamlanır.' }
            ],
            points: ['Yüz hatlarına uygun kişisel tasarım', 'Doğal ve simetrik sonuç', 'Renk, form ve dizilim uyumu', 'Özgüven artıran bir gülümseme'],
            titleEn: 'Smile Aesthetics',
            shortEn: 'Personalized aesthetic planning for your front teeth — the first thing seen when you smile.',
            descEn: 'The front area — the teeth that catch the eye first when we smile — is very important to us. Smile aesthetics is a personalized application planned by considering face shape, lip structure and gum line. Methods such as laminate veneers, zirconium crowns and teeth whitening redesign the color, shape and alignment of the teeth.',
            candidatesEn: 'Can be planned for anyone unhappy with the color, shape or alignment of their teeth who wants a more aesthetic, symmetrical smile.',
            processEn: [
                { t: 'Analysis & Planning', d: 'A personalized smile plan is prepared by examining face shape, lip structure and gum line.' },
                { t: 'Digital Design', d: 'Your new smile is designed digitally and the result is previewed before application.' },
                { t: 'Application', d: 'The teeth are reshaped using laminate veneers, zirconium crowns or teeth whitening.' },
                { t: 'Final Check', d: 'Final touch-ups are made for fit and aesthetics, completing your smile.' }
            ],
            pointsEn: ['Personal design suited to facial features', 'Natural and symmetrical result', 'Harmony of color, shape and alignment', 'A confidence-boosting smile']
        },
        {
            title: 'Kanal Tedavisi (Endodonti)',
            img: 'assets/treatments/kanal-tedavisi.jpg',
            short: 'İltihaplı dişleri çekmeden kurtaran modern endodonti uygulamaları.',
            desc: 'Kanal tedavisi, dişin merkezindeki canlı dokunun (pulpa) çıkartılarak yerine uygun dolgu maddeleriyle kanalın doldurulması işlemidir. Çürük veya travma nedeniyle iltihaplanan diş sinirinin temizlenmesiyle, çekilmesi gereken dişler kurtarılır ve ağrı ortadan kaldırılır.',
            candidates: 'Derin çürük, diş ağrısı, sıcak-soğuğa aşırı hassasiyet veya travma nedeniyle siniri iltihaplanan dişe sahip hastalar için uygundur.',
            process: [
                { t: 'Teşhis & Röntgen', d: 'Dişin ve kök kanallarının durumu röntgenle ayrıntılı olarak değerlendirilir.' },
                { t: 'Kanalların Temizlenmesi', d: 'Lokal anestezi altında iltihaplı doku çıkarılır, kanallar şekillendirilerek temizlenir.' },
                { t: 'Kanal Dolgusu', d: 'Temizlenen kanallar uygun dolgu maddesiyle sızdırmaz şekilde doldurulur.' },
                { t: 'Üst Restorasyon', d: 'Diş; dolgu veya kaplama ile fonksiyonuna kavuşacak şekilde restore edilir.' }
            ],
            points: ['Dişin çekilmesini önler', 'Ağrıyı ortadan kaldırır', 'Modern ve konforlu teknikler', 'Uzun ömürlü sonuç'],
            titleEn: 'Root Canal Treatment (Endodontics)',
            shortEn: 'Modern endodontic procedures that save inflamed teeth without extraction.',
            descEn: 'Root canal treatment is the process of removing the living tissue (pulp) at the center of the tooth and filling the canal with suitable materials. By cleaning the tooth nerve inflamed due to decay or trauma, teeth that would otherwise need extraction are saved and pain is eliminated.',
            candidatesEn: 'Suitable for patients with a tooth whose nerve is inflamed due to deep decay, toothache, extreme hot-cold sensitivity or trauma.',
            processEn: [
                { t: 'Diagnosis & X-ray', d: 'The condition of the tooth and root canals is evaluated in detail with X-ray.' },
                { t: 'Cleaning the Canals', d: 'Under local anesthesia, the inflamed tissue is removed and the canals are shaped and cleaned.' },
                { t: 'Canal Filling', d: 'The cleaned canals are filled with a suitable material in a leak-proof manner.' },
                { t: 'Final Restoration', d: 'The tooth is restored with a filling or crown so it regains its function.' }
            ],
            pointsEn: ['Prevents tooth extraction', 'Eliminates pain', 'Modern, comfortable techniques', 'Long-lasting result']
        },
        {
            title: 'Cerrahi Uygulamalar',
            img: 'assets/treatments/cerrahi.jpg',
            short: 'Diş çekiminden gömülü diş ve kist ameliyatlarına kadar ağız-çene cerrahisi.',
            desc: 'Ağız, diş ve çene cerrahisi uygulamalarının kapsamı diş çekimi ile başlayıp; gömülü 20\'lik diş ameliyatları, implant cerrahisi, kist ameliyatları ve çene cerrahisi gibi işlemleri kapsar. Tüm uygulamalar uzman hekimlerimiz tarafından steril koşullarda ve lokal anestezi ile konforlu şekilde gerçekleştirilir.',
            candidates: 'Gömülü 20\'lik dişi olan, çekilmesi gereken dişe veya kist gibi cerrahi müdahale gerektiren bir duruma sahip hastalar için uygundur.',
            process: [
                { t: 'Muayene & Görüntüleme', d: 'Panoramik röntgen ve tomografi ile cerrahi gereken bölge ayrıntılı değerlendirilir.' },
                { t: 'Planlama & Bilgilendirme', d: 'İşlem öncesi ayrıntılı plan yapılır ve hasta süreç hakkında bilgilendirilir.' },
                { t: 'Cerrahi İşlem', d: 'Lokal anestezi altında, steril koşullarda işlem konforlu şekilde gerçekleştirilir.' },
                { t: 'İyileşme Takibi', d: 'İşlem sonrası bakım önerileri verilir ve iyileşme süreci takip edilir.' }
            ],
            points: ['Normal ve gömülü diş çekimi', '20\'lik (yirmi yaş) diş ameliyatları', 'Kist ve çene cerrahisi', 'İmplant cerrahisi uygulamaları'],
            titleEn: 'Surgical Procedures',
            shortEn: 'Oral and maxillofacial surgery, from tooth extraction to impacted teeth and cyst operations.',
            descEn: 'The scope of oral, dental and maxillofacial surgery starts with tooth extraction and covers procedures such as impacted wisdom tooth operations, implant surgery, cyst operations and jaw surgery. All procedures are carried out comfortably by our specialists under sterile conditions and local anesthesia.',
            candidatesEn: 'Suitable for patients with an impacted wisdom tooth, a tooth that needs extraction, or a condition requiring surgical intervention such as a cyst.',
            processEn: [
                { t: 'Examination & Imaging', d: 'The area requiring surgery is evaluated in detail with panoramic X-ray and tomography.' },
                { t: 'Planning & Briefing', d: 'A detailed plan is made before the procedure and the patient is informed about the process.' },
                { t: 'Surgical Procedure', d: 'The procedure is performed comfortably under local anesthesia in sterile conditions.' },
                { t: 'Recovery Follow-up', d: 'Aftercare recommendations are given and the healing process is monitored.' }
            ],
            pointsEn: ['Normal and impacted tooth extraction', 'Wisdom tooth operations', 'Cyst and jaw surgery', 'Implant surgery procedures']
        },
        {
            title: 'Pedodonti (Çocuk Diş Hekimliği)',
            img: 'assets/treatments/pedodonti.jpg',
            short: '0-14 yaş çocukların süt ve daimi dişlerinin sağlığı için özel yaklaşım.',
            desc: 'Pedodonti, 0-14 yaş çocukların süt ve daimi dişlerinin sağlığını korumanın yanı sıra meydana gelen problemleri tedavi etmeyi amaçlayan diş hekimliği dalıdır. Uzman hekimlerimiz, çocukların diş hekimi korkusu yaşamadan sağlıklı dişlere sahip olması için özel teknikler kullanır. Dentual Çocuk kliniğimizde minik hastalarımıza özel bir ortam sunuyoruz.',
            candidates: '0-14 yaş aralığındaki, koruyucu diş hekimliği veya süt/daimi diş tedavisi ihtiyacı olan tüm çocuklar için uygundur.',
            process: [
                { t: 'Tanışma & Muayene', d: 'Çocuğun güven duyması sağlanarak nazik bir şekilde ağız ve diş muayenesi yapılır.' },
                { t: 'Koruyucu Uygulamalar', d: 'Flor ve fissür örtücü gibi koruyucu işlemlerle çürük riski azaltılır.' },
                { t: 'Tedavi', d: 'Gerekli durumlarda süt ve daimi diş dolguları ile uygun tedaviler uygulanır.' },
                { t: 'Düzenli Kontrol', d: 'Diş gelişiminin sağlıklı ilerlemesi için periyodik kontroller planlanır.' }
            ],
            points: ['Ağız hijyeni eğitimi', 'Flor ve fissür örtücü uygulamaları', 'Süt ve daimi diş dolgu/tedavileri', 'Çocuk dostu, korkutmayan yaklaşım'],
            titleEn: 'Pedodontics (Pediatric Dentistry)',
            shortEn: 'A special approach for the health of children\'s primary and permanent teeth (ages 0-14).',
            descEn: 'Pedodontics is the branch of dentistry that aims to protect the health of children\'s primary and permanent teeth (ages 0-14) and to treat problems that arise. Our specialists use special techniques so children can have healthy teeth without fear of the dentist. At our Dentual Kids clinic, we offer a special environment for our little patients.',
            candidatesEn: 'Suitable for all children aged 0-14 who need preventive dentistry or primary/permanent tooth treatment.',
            processEn: [
                { t: 'Introduction & Examination', d: 'An oral and dental examination is performed gently, helping the child feel at ease.' },
                { t: 'Preventive Applications', d: 'Cavity risk is reduced with preventive procedures such as fluoride and fissure sealants.' },
                { t: 'Treatment', d: 'When necessary, appropriate treatments are applied with primary and permanent tooth fillings.' },
                { t: 'Regular Check-ups', d: 'Periodic check-ups are planned for healthy dental development.' }
            ],
            pointsEn: ['Oral hygiene education', 'Fluoride and fissure sealant applications', 'Primary and permanent tooth fillings/treatments', 'Child-friendly, reassuring approach']
        }
    ];

    const FAQS = [
        { q: 'Randevu almadan gelebilir miyim?', a: 'Acil durumlar için kapımız her zaman açık olsa da, bekleme süresini en aza indirmek için gelmeden önce size en yakın şubemizi telefonla aramanızı öneririz. Şube telefon numaralarımıza İletişim sayfamızdan ulaşabilirsiniz.', qEn: 'Can I visit without an appointment?', aEn: 'Although our door is always open for emergencies, we recommend calling your nearest branch by phone before your visit to minimize waiting time. You can find our branch phone numbers on our Contact page.' },
        { q: 'İmplant tedavisi ağrılı mıdır?', a: 'İmplant işlemi lokal anestezi altında yapıldığı için işlem sırasında ağrı hissetmezsiniz. İşlem sonrası oluşabilecek hafif hassasiyet ise basit ağrı kesicilerle kolayca kontrol altına alınır.', qEn: 'Is implant treatment painful?', aEn: 'Because the implant procedure is performed under local anesthesia, you do not feel pain during the procedure. Any mild sensitivity afterwards is easily controlled with simple painkillers.' },
        { q: 'Tedavi ücretlerini taksitlendirebiliyor musunuz?', a: 'Evet. Hastalarımızın tedaviye kolay erişebilmesi için çeşitli ödeme kolaylıkları ve taksit seçenekleri sunuyoruz. Detaylı bilgi için kliniklerimizle iletişime geçebilirsiniz.', qEn: 'Do you offer installment payment options?', aEn: 'Yes. To make treatment easily accessible for our patients, we offer various payment conveniences and installment options. Please contact our clinics for detailed information.' },
        { q: 'Diş beyazlatma dişlere zarar verir mi?', a: 'Profesyonel olarak klinik ortamında uygulanan beyazlatma işlemleri diş minesine zarar vermez. İşlem öncesi diş sağlığınız değerlendirilir ve size en uygun yöntem belirlenir.', qEn: 'Does teeth whitening damage the teeth?', aEn: 'Whitening procedures performed professionally in a clinical setting do not harm tooth enamel. Your dental health is assessed beforehand and the most suitable method is determined for you.' },
        { q: 'Çocuğumu ilk diş kontrolüne ne zaman getirmeliyim?', a: 'İlk diş çıktıktan sonra veya en geç 1 yaşına kadar ilk diş hekimi kontrolünün yapılması önerilir. Erken kontroller, çocuğunuzun diş sağlığı için koruyucu bir temel oluşturur.', qEn: 'When should I bring my child for their first dental check-up?', aEn: 'The first dental check-up is recommended after the first tooth erupts, or by the age of 1 at the latest. Early check-ups build a preventive foundation for your child\'s dental health.' },
        { q: 'Hangi şubeleriniz var ve çalışma saatleriniz nedir?', a: 'Karatay, Selçuklu ve Meram olmak üzere üç şubemiz bulunmaktadır. Pazar günleri dahil her gün gece 23:30\'a kadar hizmet veriyoruz; acil diş tedavileriniz için geç saatlerde de yanınızdayız.', qEn: 'Which branches do you have and what are your hours?', aEn: 'We have three branches: Karatay, Selçuklu and Meram. We serve every day until 23:30, including Sundays; we are by your side at late hours for your emergency dental needs.' }
    ];

    const BLOG = [
        {
            id: 'implant-sonrasi-bakim',
            cat: 'İmplant',
            title: 'İmplant Tedavisi Sonrası Bakım: 7 Altın Kural',
            excerpt: 'İmplantınızın ömrünü uzatmak büyük ölçüde işlem sonrası bakıma bağlı. İlk günlerden uzun vadeye dikkat etmeniz gereken her şey.',
            date: '2026-05-28', readTime: 5, image: 'assets/treatments/implant.jpg',
            body: `<p>Diş implantı, doğru bakıldığında ömür boyu kullanılabilen kalıcı bir çözümdür. Tedavinin başarısı yalnızca cerrahi aşamaya değil, sonrasındaki bakıma da bağlıdır. İşte implant sonrası dikkat etmeniz gereken altın kurallar.</p>
            <h3>İlk 24-48 Saat</h3>
            <p>İşlemden hemen sonra bölgeye soğuk kompres uygulamak şişliği azaltır. İlk gün sigara ve alkolden uzak durun, çok sıcak yiyecek-içeceklerden kaçının ve hekiminizin önerdiği ilaçları düzenli kullanın.</p>
            <h3>Uzun Vadede Dikkat Edilmesi Gerekenler</h3>
            <ul>
                <li>Günde en az iki kez, yumuşak fırça ile nazikçe fırçalama yapın.</li>
                <li>İmplant çevresini ara yüz fırçası veya diş ipi ile temizleyin.</li>
                <li>Çok sert yiyecekleri (ceviz kırma vb.) implant bölgesinde kullanmayın.</li>
                <li>Sigarayı bırakın; sigara implant kaybının en büyük nedenlerindendir.</li>
                <li>6 ayda bir kontrol ve profesyonel temizlik için hekiminize gidin.</li>
            </ul>
            <p>Unutmayın: İmplantlar çürümez ama çevresindeki diş eti hastalanabilir. Düzenli bakım, implantınızın ömrünü doğrudan belirler. Herhangi bir hassasiyet veya kanama fark ederseniz vakit kaybetmeden bizimle iletişime geçin.</p>`
        },
        {
            id: 'cocuk-ilk-dis-kontrolu',
            cat: 'Pedodonti',
            title: 'Çocuğumu İlk Diş Kontrolüne Ne Zaman Götürmeliyim?',
            excerpt: 'Erken başlayan diş kontrolleri, çocuğunuzun ömür boyu sağlıklı dişlere sahip olmasının temelini atar. İşte bilmeniz gerekenler.',
            date: '2026-05-20', readTime: 4, image: 'assets/treatments/pedodonti.jpg',
            body: `<p>Birçok ebeveyn, çocuğunu diş hekimine ne zaman götüreceği konusunda kararsız kalır. Oysa erken tanışma, hem korkuyu önler hem de olası problemleri başlamadan durdurur.</p>
            <h3>İlk Ziyaret: 1 Yaş</h3>
            <p>Uzmanlar, ilk diş çıktıktan sonra ya da en geç 1 yaşına kadar ilk diş hekimi kontrolünün yapılmasını önerir. Bu ziyaret çoğunlukla bir muayene ve ebeveyne yönelik bilgilendirme şeklinde geçer.</p>
            <h3>Neden Bu Kadar Önemli?</h3>
            <ul>
                <li>Çürükler henüz başlamadan koruyucu önlemler alınır (flor, fissür örtücü).</li>
                <li>Çocuk, diş hekimi ortamına korkmadan alışır.</li>
                <li>Çene ve diş gelişimi erkenden takip edilir.</li>
                <li>Doğru fırçalama ve beslenme alışkanlıkları kazandırılır.</li>
            </ul>
            <p>Dentual Çocuk kliniğimizde, minik hastalarımıza özel, neşeli ve korkutmayan bir ortam sunuyoruz. Çocuğunuzun ilk diş deneyimini keyifli bir maceraya dönüştürüyoruz.</p>`
        },
        {
            id: 'gulus-tasarimi-nedir',
            cat: 'Estetik',
            title: 'Gülüş Tasarımı Nedir? Kimler İçin Uygundur?',
            excerpt: 'Gülüş tasarımı sadece beyaz dişler değildir; yüzünüze özel, doğal ve simetrik bir gülümsemenin bütüncül planıdır.',
            date: '2026-05-12', readTime: 6, image: 'assets/treatments/gulus-estetigi.jpg',
            body: `<p>Gülüş tasarımı; diş rengi, formu, dizilimi ve diş eti çizgisinin yüz hatlarınızla uyumlu olacak şekilde yeniden planlanmasıdır. Amaç, "yapay" değil, size en doğal şekilde yakışan gülümsemeyi oluşturmaktır.</p>
            <h3>Hangi Yöntemler Kullanılır?</h3>
            <ul>
                <li><strong>Lamina (Yaprak Porselen):</strong> Dişin ön yüzeyine uygulanan ince porselen tabakalar.</li>
                <li><strong>Zirkonyum Kaplama:</strong> Metal içermeyen, doğal ışık geçirgenliğine sahip kaplamalar.</li>
                <li><strong>Diş Beyazlatma:</strong> Renklenmeleri gidererek daha parlak bir görünüm.</li>
                <li><strong>Diş Eti Estetiği:</strong> Gülümsemede diş eti oranının düzenlenmesi.</li>
            </ul>
            <h3>Kimler İçin Uygundur?</h3>
            <p>Dişlerinin renginden, formundan veya diziliminden memnun olmayan; kırık, aşınmış ya da aralıklı dişleri olan herkes aday olabilir. İşlem öncesi dijital planlama ile sonucu önceden görebilirsiniz.</p>
            <p>Unutmayın, en iyi gülüş tasarımı kişiye özeldir. Hekiminizle yapacağınız ön görüşmede beklentilerinizi paylaşmanız, sonucun memnuniyetini doğrudan etkiler.</p>`
        },
        {
            id: 'gece-dis-agrisi-ne-yapmali',
            cat: 'Acil',
            title: 'Gece Diş Ağrısı Bastırınca Ne Yapmalı?',
            excerpt: 'Diş ağrısı çoğu zaman en kötü anda, gece bastırır. Hekime ulaşana kadar ağrıyı hafifletecek pratik ve güvenli öneriler.',
            date: '2026-05-03', readTime: 4, image: 'assets/treatments/kanal-tedavisi.jpg',
            body: `<p>Ani gelişen diş ağrısı, özellikle gece saatlerinde dayanılmaz olabilir. Kalıcı çözüm mutlaka bir diş hekimi muayenesidir; ancak hekime ulaşana kadar ağrıyı hafifletmek için yapabilecekleriniz var.</p>
            <h3>Evde Yapabilecekleriniz</h3>
            <ul>
                <li>Ilık tuzlu su ile ağzınızı çalkalayın; bu, bölgedeki bakterileri azaltır.</li>
                <li>Yanağınıza dışarıdan soğuk kompres uygulayın (doğrudan dişe değil).</li>
                <li>Hekiminizin daha önce önerdiği bir ağrı kesiciyi kullanabilirsiniz.</li>
                <li>Ağrıyan bölgeyi diş ipiyle nazikçe temizleyin; sıkışmış gıda ağrı yapabilir.</li>
                <li>Aspirini doğrudan diş etine koymayın; dokuya zarar verir.</li>
            </ul>
            <h3>Beklemeyin, Bizi Arayın</h3>
            <p>Bu öneriler geçici rahatlama sağlar; ağrının nedeni devam ediyordur. İyi haber şu: <strong>Dentual olarak Pazar dahil her gün gece 23:30'a kadar açığız.</strong> Geç saatte bastıran diş ağrılarınızda nöbetçi diş hekimi hizmetimizle yanınızdayız. Çağrı merkezi: 444 34 42.</p>`
        }
    ];

    /* ---------- HELPERS ---------- */
    const $ = (s, ctx = document) => ctx.querySelector(s);
    const $$ = (s, ctx = document) => Array.from(ctx.querySelectorAll(s));

    /* ---------- PRELOADER ---------- */
    function initPreloader() {
        const pre = $('#preloader');
        if (!pre) return;
        const hide = () => pre.classList.add('hidden');
        window.addEventListener('load', () => setTimeout(hide, 800));
        // Fallback
        setTimeout(hide, 2500);
    }

    /* ---------- THEME (DARK MODE) ---------- */
    function initTheme() {
        const root = document.documentElement;
        const toggle = $('#themeToggle');
        const saved = localStorage.getItem('dentual-theme');
        if (saved) root.setAttribute('data-theme', saved);
        if (toggle) {
            toggle.addEventListener('click', () => {
                const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                root.setAttribute('data-theme', next);
                localStorage.setItem('dentual-theme', next);
            });
        }
    }

    /* ---------- SCROLL PROGRESS ---------- */
    function initScrollProgress() {
        const bar = $('#scrollProgress');
        const onScroll = () => {
            const h = document.documentElement.scrollHeight - window.innerHeight;
            const pct = h > 0 ? (window.scrollY / h) * 100 : 0;
            if (bar) bar.style.width = pct + '%';
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    /* ---------- NAVBAR STATE ---------- */
    let currentPage = 'home';
    function updateNavbar() {
        const nav = $('#navbar');
        if (!nav) return;
        const scrolled = window.scrollY > 30;
        // Home top => transparent; otherwise solid
        if (currentPage === 'home' && !scrolled) {
            nav.classList.add('transparent');
            nav.classList.remove('solid');
        } else {
            nav.classList.add('solid');
            nav.classList.remove('transparent');
        }
    }

    /* ---------- SPA ROUTING ---------- */
    function pageTitle(page) {
        const set = PAGE_TITLES[currentLang] || PAGE_TITLES.tr;
        return set[page] || set.home;
    }
    function navigate(page) {
        if (!pageTitle(page)) page = 'home';
        if (!(PAGE_TITLES.tr[page])) page = 'home';
        currentPage = page;

        $$('.page').forEach(p => p.classList.remove('active'));
        const target = $('#page-' + page);
        if (target) target.classList.add('active');

        $$('.nav-link').forEach(l => l.classList.toggle('active', l.dataset.page === page));

        // Blog always opens on the list view
        if (page === 'blog') showBlogList();

        document.title = pageTitle(page);
        const descSet = PAGE_DESCS[currentLang] || PAGE_DESCS.tr;
        const metaDesc = $('meta[name="description"]');
        if (metaDesc && descSet[page]) metaDesc.setAttribute('content', descSet[page]);
        window.scrollTo({ top: 0, behavior: 'auto' });
        updateNavbar();
        // Re-trigger reveal for newly shown page
        runReveal();
        if (page === 'home') restartTypewriter();
    }

    function initRouting() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('[data-page]');
            if (link) {
                e.preventDefault();
                navigate(link.dataset.page);
                closeMobileMenu();
            }
        });
    }

    /* ---------- MOBILE MENU ---------- */
    function initMobileMenu() {
        const burger = $('#hamburger');
        const links = $('#navLinks');
        if (!burger || !links) return;
        burger.addEventListener('click', () => {
            burger.classList.toggle('open');
            links.classList.toggle('open');
        });
    }
    function closeMobileMenu() {
        $('#hamburger') && $('#hamburger').classList.remove('open');
        $('#navLinks') && $('#navLinks').classList.remove('open');
    }

    /* ---------- HERO SLIDER ---------- */
    function initHeroSlider() {
        const slides = $$('.hero-slide');
        const dotsWrap = $('#heroDots');
        if (!slides.length) return;
        let idx = 0;
        slides.forEach((_, i) => {
            const b = document.createElement('button');
            b.className = i === 0 ? 'active' : '';
            b.setAttribute('aria-label', 'Slayt ' + (i + 1));
            b.addEventListener('click', () => go(i));
            dotsWrap && dotsWrap.appendChild(b);
        });
        const dots = dotsWrap ? $$('button', dotsWrap) : [];
        function go(n) {
            slides[idx].classList.remove('active');
            dots[idx] && dots[idx].classList.remove('active');
            idx = (n + slides.length) % slides.length;
            slides[idx].classList.add('active');
            dots[idx] && dots[idx].classList.add('active');
        }
        setInterval(() => go(idx + 1), 5500);
    }

    /* ---------- TYPEWRITER ---------- */
    let twTimer = null;
    function startTypewriter() {
        const el = $('#typewriter');
        if (!el) return;
        const words = TW_PHRASES[currentLang] || TW_PHRASES.tr;
        let w = 0, c = 0, deleting = false;
        function tick() {
            const word = words[w];
            if (!deleting) {
                el.textContent = word.slice(0, ++c);
                if (c === word.length) { deleting = true; twTimer = setTimeout(tick, 2000); return; }
            } else {
                el.textContent = word.slice(0, --c);
                if (c === 0) { deleting = false; w = (w + 1) % words.length; }
            }
            twTimer = setTimeout(tick, deleting ? 45 : 90);
        }
        clearTimeout(twTimer);
        tick();
    }
    function restartTypewriter() {
        const el = $('#typewriter');
        if (el && !el.textContent) startTypewriter();
    }
    function restartTypewriterForLang() {
        const el = $('#typewriter');
        if (!el) return;
        clearTimeout(twTimer);
        el.textContent = '';
        startTypewriter();
    }

    /* ---------- COUNTERS ---------- */
    function animateCounter(el) {
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';
        const dur = 1800;
        const start = performance.now();
        function frame(now) {
            const p = Math.min((now - start) / dur, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.floor(eased * target).toLocaleString('tr-TR') + suffix;
            if (p < 1) requestAnimationFrame(frame);
            else el.textContent = target.toLocaleString('tr-TR') + suffix;
        }
        requestAnimationFrame(frame);
    }
    function initCounters() {
        const nums = $$('.stat-number');
        const obs = new IntersectionObserver((entries) => {
            entries.forEach(en => {
                if (en.isIntersecting && !en.target.dataset.done) {
                    en.target.dataset.done = '1';
                    animateCounter(en.target);
                }
            });
        }, { threshold: 0.5 });
        nums.forEach(n => obs.observe(n));
    }

    /* ---------- REVEAL ---------- */
    let revealObs = null;
    function initReveal() {
        revealObs = new IntersectionObserver((entries) => {
            entries.forEach(en => {
                if (en.isIntersecting) {
                    en.target.classList.add('visible');
                    revealObs.unobserve(en.target);
                }
            });
        }, { threshold: 0.12 });
        runReveal();
    }
    function runReveal() {
        if (!revealObs) return;
        $$('.reveal:not(.visible)').forEach((el, i) => {
            // stagger within an active page
            if (el.closest('.page') && !el.closest('.page').classList.contains('active')) return;
            el.style.transitionDelay = (Math.min(i, 6) * 0.06) + 's';
            revealObs.observe(el);
        });
    }

    /* ---------- RENDER DOCTORS ---------- */
    function renderDoctors() {
        const grid = $('#doctorsGrid');
        if (!grid) return;
        const en = currentLang === 'en';
        grid.innerHTML = DOCTORS.map(d => `
            <div class="doctor-card reveal">
                <img src="${d.img}" alt="${d.name}" loading="lazy" />
                <div class="doctor-overlay">
                    <div class="doctor-info">
                        <div class="doctor-name">${d.name}</div>
                        <div class="doctor-role">${en && d.roleEn ? d.roleEn : d.role}</div>
                    </div>
                </div>
            </div>`).join('');
    }

    /* ---------- RENDER REVIEWS ---------- */
    function renderReviews() {
        const track = $('#reviewsTrack');
        if (!track) return;
        const en = currentLang === 'en';
        const verified = en ? 'Verified on Google' : 'Google\'da doğrulandı';
        track.innerHTML = REVIEWS.map(r => `
            <div class="review-card">
                <span class="review-tag">${en && r.tagEn ? r.tagEn : r.tag}</span>
                <div class="review-head">
                    <div class="review-avatar" style="background:${r.color}">${r.initials}</div>
                    <div class="review-meta">
                        <strong>${r.name}</strong>
                        <div class="review-stars">${'★'.repeat(r.stars)}</div>
                    </div>
                </div>
                <p class="review-text">${en && r.textEn ? r.textEn : r.text}</p>
                <div class="review-google">
                    <svg viewBox="0 0 24 24" width="16" height="16"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.26 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/><path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/></svg>
                    ${verified}
                </div>
            </div>`).join('');
    }

    function initReviewCarousel() {
        const track = $('#reviewsTrack');
        const prev = $('#reviewPrev');
        const next = $('#reviewNext');
        if (!track) return;
        const step = 380;
        prev && prev.addEventListener('click', () => track.scrollBy({ left: -step, behavior: 'smooth' }));
        next && next.addEventListener('click', () => track.scrollBy({ left: step, behavior: 'smooth' }));
    }

    /* ---------- RENDER FAQ ---------- */
    function renderFaq() {
        const list = $('#faqList');
        if (!list) return;
        const en = currentLang === 'en';
        list.innerHTML = FAQS.map(f => `
            <div class="faq-item">
                <button class="faq-q">${en && f.qEn ? f.qEn : f.q}<span class="faq-icon">+</span></button>
                <div class="faq-a"><div class="faq-a-inner">${en && f.aEn ? f.aEn : f.a}</div></div>
            </div>`).join('');
        $$('.faq-q', list).forEach(btn => {
            btn.addEventListener('click', () => {
                const item = btn.parentElement;
                const ans = $('.faq-a', item);
                const isOpen = item.classList.contains('open');
                // close all
                $$('.faq-item', list).forEach(i => {
                    i.classList.remove('open');
                    $('.faq-a', i).style.maxHeight = null;
                });
                if (!isOpen) {
                    item.classList.add('open');
                    ans.style.maxHeight = ans.scrollHeight + 'px';
                }
            });
        });
    }

    /* ---------- RENDER TREATMENTS ---------- */
    function treatmentCardHTML(t, i) {
        const en = currentLang === 'en';
        const title = en && t.titleEn ? t.titleEn : t.title;
        const short = en && t.shortEn ? t.shortEn : t.short;
        const more = en ? 'See Details →' : 'Detayları Gör →';
        return `
            <div class="treatment-card reveal" data-treatment="${i}">
                <div class="treatment-img">
                    <img src="${t.img}" alt="${title}" loading="lazy" />
                </div>
                <div class="treatment-body">
                    <h3>${title}</h3>
                    <p>${short}</p>
                    <span class="treatment-more">${more}</span>
                </div>
            </div>`;
    }
    function bindTreatmentCards(grid) {
        $$('.treatment-card', grid).forEach(card => {
            card.addEventListener('click', () => openTreatmentModal(TREATMENTS[card.dataset.treatment]));
        });
    }
    function renderTreatments() {
        const grid = $('#treatmentsGrid');
        if (grid) {
            grid.innerHTML = TREATMENTS.map((t, i) => treatmentCardHTML(t, i)).join('');
            bindTreatmentCards(grid);
        }
        const home = $('#homeTreatmentsGrid');
        if (home) {
            // Feature the first 3 treatments on the home page (indices preserved)
            home.innerHTML = TREATMENTS.slice(0, 3).map((t, i) => treatmentCardHTML(t, i)).join('');
            bindTreatmentCards(home);
        }
    }

    /* ---------- BLOG ---------- */
    const BLOG_MONTHS = {
        tr: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
        en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    };
    function formatDate(iso) {
        const d = new Date(iso);
        const months = BLOG_MONTHS[currentLang] || BLOG_MONTHS.tr;
        return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
    }
    function renderBlog() {
        const grid = $('#blogGrid');
        if (!grid) return;
        const readLbl = currentLang === 'en' ? 'min read' : 'dk okuma';
        const more = currentLang === 'en' ? 'Read More →' : 'Devamını Oku →';
        grid.innerHTML = BLOG.map(b => `
            <article class="blog-card reveal" data-article="${b.id}">
                <div class="blog-card-img">
                    <span class="blog-cat">${b.cat}</span>
                    <img src="${b.image}" alt="${b.title}" loading="lazy" />
                </div>
                <div class="blog-card-body">
                    <div class="blog-card-meta">${formatDate(b.date)} &middot; ${b.readTime} ${readLbl}</div>
                    <h3>${b.title}</h3>
                    <p>${b.excerpt}</p>
                    <span class="blog-more">${more}</span>
                </div>
            </article>`).join('');
        $$('.blog-card', grid).forEach(c => c.addEventListener('click', () => openArticle(c.dataset.article)));
    }
    function openArticle(id) {
        const b = BLOG.find(x => x.id === id);
        if (!b) return;
        const readLbl = currentLang === 'en' ? 'min read' : 'dk okuma';
        $('#articleCat').textContent = b.cat;
        $('#articleTitle').textContent = b.title;
        $('#articleMeta').textContent = formatDate(b.date) + ' · ' + b.readTime + ' ' + readLbl;
        $('#articleImg').style.backgroundImage = `url('${b.image}')`;
        $('#articleBody').innerHTML = b.body;
        $('#blogListView').style.display = 'none';
        $('#blogArticleView').style.display = '';
        window.scrollTo({ top: 0, behavior: 'auto' });
        document.title = b.title + ' - Dentual Konya';
        runReveal();
    }
    function showBlogList() {
        const av = $('#blogArticleView'), lv = $('#blogListView');
        if (av) av.style.display = 'none';
        if (lv) lv.style.display = '';
    }
    function initBlog() {
        renderBlog();
        const back = $('#blogBack');
        if (back) back.addEventListener('click', () => {
            showBlogList();
            window.scrollTo({ top: 0, behavior: 'auto' });
            document.title = pageTitle('blog');
        });
    }

    /* ---------- MODALS ---------- */
    function openModal(id) {
        const m = $('#' + id);
        if (m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
    }
    function closeModal(m) {
        m.classList.remove('open');
        document.body.style.overflow = '';
    }
    function openTreatmentModal(t) {
        const en = currentLang === 'en';
        const pick = (a, b) => (en && b ? b : a);
        $('#tmImg').style.backgroundImage = `url('${t.img}')`;
        $('#tmTag').textContent = en ? 'Treatment' : 'Tedavi';
        $('#tmTitle').textContent = pick(t.title, t.titleEn);
        $('#tmDesc').textContent = pick(t.desc, t.descEn);

        // Candidates callout
        const cand = $('#tmCandidates');
        const candText = pick(t.candidates, t.candidatesEn);
        if (candText) {
            $('#tmCandidatesText').textContent = candText;
            cand.style.display = '';
        } else {
            cand.style.display = 'none';
        }

        // Treatment process steps
        const procWrap = $('#tmProcessWrap');
        const proc = en && t.processEn ? t.processEn : t.process;
        if (proc && proc.length) {
            $('#tmProcess').innerHTML = proc.map(p =>
                `<li><strong>${p.t}</strong><span>${p.d}</span></li>`).join('');
            procWrap.style.display = '';
        } else {
            procWrap.style.display = 'none';
        }

        // Advantages
        const points = en && t.pointsEn ? t.pointsEn : t.points;
        $('#tmList').innerHTML = points.map(p => `<li>${p}</li>`).join('');

        // Reset scroll to top of modal
        const modal = $('#treatmentModal .modal');
        if (modal) modal.scrollTop = 0;

        openModal('treatmentModal');
    }
    function initModals() {
        // Close handlers
        $$('.modal-overlay').forEach(ov => {
            ov.addEventListener('click', (e) => {
                if (e.target === ov || e.target.closest('[data-close-modal]')) closeModal(ov);
            });
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') $$('.modal-overlay.open').forEach(closeModal);
        });
    }

    /* ---------- MAP FACADE (lazy Google Maps) ---------- */
    function loadMap(el) {
        if (el.dataset.loaded) return;
        const url = el.dataset.map;
        if (!url) return;
        el.dataset.loaded = '1';
        const iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.title = el.getAttribute('aria-label') || 'Harita';
        iframe.loading = 'lazy';
        iframe.referrerPolicy = 'no-referrer-when-downgrade';
        el.innerHTML = '';
        el.appendChild(iframe);
        el.classList.add('map-loaded');
    }
    function initMaps() {
        $$('.map-facade').forEach(el => {
            el.addEventListener('click', () => loadMap(el));
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); loadMap(el); }
            });
        });
    }

    /* ---------- WHATSAPP MESSAGES ---------- */
    // Apply a default prefilled message to every WhatsApp link on the site.
    // Links that already carry a custom message (e.g. the emergency band) are preserved.
    function applyWhatsAppMessages() {
        const msg = encodeURIComponent(WA_MSG[currentLang] || WA_MSG.tr);
        $$('a[href*="wa.me/"]').forEach(a => {
            const href = a.getAttribute('href') || '';
            const hasText = /[?&]text=/.test(href);
            if (hasText && a.dataset.waAuto !== '1') return; // keep custom (emergency) message
            const base = href.split('?')[0];
            a.setAttribute('href', base + '?text=' + msg);
            a.dataset.waAuto = '1';
        });
    }

    /* ---------- WHATSAPP WIDGET ---------- */
    function initWhatsApp() {
        const btn = $('#waButton');
        const popup = $('#waPopup');
        if (!btn || !popup) return;
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            popup.classList.toggle('open');
        });
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#waWidget')) popup.classList.remove('open');
        });
    }

    /* ---------- ANNOUNCEMENT BAR (marquee) ---------- */
    // Clone the seed item enough times to fill the viewport seamlessly, then
    // animate the track by -50% at a constant speed. Re-run on resize / lang change.
    function buildAnnounceMarquee() {
        const bar = $('#announceBar');
        if (!bar || document.documentElement.classList.contains('ann-dismissed')) return;
        const track = bar.querySelector('.announce-track');
        const viewport = bar.querySelector('.announce-viewport');
        if (!track || !viewport) return;
        const seed = track.querySelector('.announce-item:not(.announce-clone)');
        if (!seed) return;
        track.querySelectorAll('.announce-clone').forEach(n => n.remove());

        const vw = viewport.getBoundingClientRect().width || window.innerWidth;
        const itemW = seed.getBoundingClientRect().width;
        if (!itemW) return;

        // Each half of the track must be at least as wide as the viewport so the
        // -50% loop never reveals a gap. Track = two identical halves of `perHalf` items.
        const perHalf = Math.max(1, Math.ceil(vw / itemW) + 1);
        const total = perHalf * 2;
        for (let i = 1; i < total; i++) {
            const c = seed.cloneNode(true);
            c.classList.add('announce-clone');
            c.setAttribute('aria-hidden', 'true');
            c.querySelectorAll('[data-i18n-html], [data-i18n], [data-i18n-ph]').forEach(el => {
                el.removeAttribute('data-i18n-html');
                el.removeAttribute('data-i18n');
                el.removeAttribute('data-i18n-ph');
            });
            const tel = c.querySelector('.announce-tel');
            if (tel) tel.setAttribute('tabindex', '-1');
            track.appendChild(c);
        }

        // Constant speed (~70px/s): one loop travels half the track width.
        const dur = Math.max(8, (perHalf * itemW) / 70);
        track.style.animationDuration = dur.toFixed(1) + 's';
        bar.classList.add('marquee-on');
    }
    function initAnnounce() {
        const btn = $('#announceClose');
        if (btn) {
            btn.addEventListener('click', () => {
                document.documentElement.classList.add('ann-dismissed');
                try { localStorage.setItem('dentual-ann-closed', '1'); } catch (e) {}
                const bar = $('#announceBar');
                if (bar) bar.classList.remove('marquee-on');
            });
        }
        let t;
        window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(buildAnnounceMarquee, 200); }, { passive: true });
        // Rebuild once webfonts are ready so item widths are measured accurately.
        if (document.fonts && document.fonts.ready) document.fonts.ready.then(buildAnnounceMarquee);
    }

    /* ---------- SCROLL TOP ---------- */
    function initScrollTop() {
        const btn = $('#scrollTop');
        if (!btn) return;
        window.addEventListener('scroll', () => {
            btn.classList.toggle('show', window.scrollY > 500);
        }, { passive: true });
        btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }

    /* ---------- FORMS ---------- */
    // WhatsApp numbers per branch
    const WA_NUMBERS = {
        'Karatay': '905467332713',
        'Selçuklu': '905513424442',
        'Meram': '905525994959'
    };
    const WA_DEFAULT = '905525994959'; // Meram (gece geç saate kadar açık)
    const FIELD_LABELS = {
        tr: { name: 'Ad Soyad', phone: 'Telefon', email: 'E-posta', branch: 'Şube', message: 'Mesaj' },
        en: { name: 'Full Name', phone: 'Phone', email: 'E-mail', branch: 'Branch', message: 'Message' }
    };
    const FORM_TITLES = {
        contact: { tr: 'Dentual İletişim Formu', en: 'Dentual Contact Form' }
    };

    function initForms() {
        const handle = (formId, statusId, titleKey) => {
            const form = $('#' + formId);
            if (!form) return;
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                if (!form.checkValidity()) { form.reportValidity(); return; }

                const lang = currentLang;
                const labels = FIELD_LABELS[lang] || FIELD_LABELS.tr;

                // Collect named fields
                const data = {};
                $$('input, textarea, select', form).forEach(el => {
                    if (el.name && el.value.trim()) data[el.name] = el.value.trim();
                });

                // Build a readable WhatsApp message
                const lines = ['*' + (FORM_TITLES[titleKey][lang] || FORM_TITLES[titleKey].tr) + '*'];
                Object.keys(labels).forEach(k => {
                    if (data[k]) lines.push(labels[k] + ': ' + data[k]);
                });
                const text = encodeURIComponent(lines.join('\n'));
                const num = WA_NUMBERS[data.branch] || WA_DEFAULT;
                window.open('https://wa.me/' + num + '?text=' + text, '_blank');

                const status = $('#' + statusId);
                if (status) {
                    status.textContent = FORM_MSG[lang] || FORM_MSG.tr;
                    status.classList.add('success');
                }
                form.reset();
                setTimeout(() => { if (status) { status.textContent = ''; status.classList.remove('success'); } }, 6000);
                if (form.closest('.modal-overlay')) {
                    setTimeout(() => closeModal(form.closest('.modal-overlay')), 2000);
                }
            });
        };
        handle('homeContactForm', 'hcStatus', 'contact');
        handle('pageContactForm', 'pcStatus', 'contact');
    }

    /* ---------- I18N ENGINE ---------- */
    function captureBaseText() {
        $$('[data-i18n]').forEach(el => { if (el.dataset.trText === undefined) el.dataset.trText = el.textContent; });
        $$('[data-i18n-html]').forEach(el => { if (el.dataset.trHtml === undefined) el.dataset.trHtml = el.innerHTML; });
        $$('[data-i18n-ph]').forEach(el => { if (el.dataset.trPh === undefined) el.dataset.trPh = el.getAttribute('placeholder') || ''; });
    }
    function translateStatic(lang) {
        const dict = DICT[lang] || {};
        $$('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            el.textContent = lang === 'tr' ? el.dataset.trText : (dict[key] !== undefined ? dict[key] : el.dataset.trText);
        });
        $$('[data-i18n-html]').forEach(el => {
            const key = el.dataset.i18nHtml;
            el.innerHTML = lang === 'tr' ? el.dataset.trHtml : (dict[key] !== undefined ? dict[key] : el.dataset.trHtml);
        });
        $$('[data-i18n-ph]').forEach(el => {
            const key = el.dataset.i18nPh;
            el.setAttribute('placeholder', lang === 'tr' ? el.dataset.trPh : (dict[key] !== undefined ? dict[key] : el.dataset.trPh));
        });
    }
    function applyLangChrome(lang) {
        document.documentElement.lang = lang;
        document.documentElement.dir = RTL_LANGS.indexOf(lang) !== -1 ? 'rtl' : 'ltr';
        const cur = $('#langCurrent'); if (cur) cur.textContent = lang.toUpperCase();
        $$('.lang-option').forEach(o => o.classList.toggle('active', o.dataset.lang === lang));
        document.title = pageTitle(currentPage);
    }
    function setLanguage(lang) {
        if (SUPPORTED_LANGS.indexOf(lang) === -1) lang = 'tr';
        currentLang = lang;
        localStorage.setItem('dentual-lang', lang);
        translateStatic(lang);
        // Re-render dynamic content in the new language
        renderDoctors(); renderReviews(); renderFaq(); renderTreatments(); renderBlog();
        runReveal();
        applyWhatsAppMessages();
        applyLangChrome(lang);
        restartTypewriterForLang();
        buildAnnounceMarquee();
    }
    function initLangSwitcher() {
        const sw = $('#langSwitcher'), btn = $('#langBtn');
        if (btn && sw) {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                sw.classList.toggle('open');
                btn.setAttribute('aria-expanded', sw.classList.contains('open'));
            });
            document.addEventListener('click', (e) => {
                if (!e.target.closest('#langSwitcher')) { sw.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
            });
        }
        $$('.lang-option').forEach(o => o.addEventListener('click', () => {
            setLanguage(o.dataset.lang);
            if (sw) sw.classList.remove('open');
        }));
    }

    /* ---------- INIT ---------- */
    function init() {
        initPreloader();
        initTheme();
        initScrollProgress();
        initMobileMenu();
        initRouting();
        initHeroSlider();
        startTypewriter();
        renderDoctors();
        renderReviews();
        initReviewCarousel();
        renderFaq();
        renderTreatments();
        initBlog();
        initModals();
        initMaps();
        initWhatsApp();
        applyWhatsAppMessages();
        initScrollTop();
        initAnnounce();
        initForms();

        // Internationalization: capture base (TR) text, wire switcher, apply saved language
        captureBaseText();
        initLangSwitcher();
        translateStatic(currentLang);
        applyLangChrome(currentLang);
        buildAnnounceMarquee();

        initCounters();
        initReveal();

        window.addEventListener('scroll', updateNavbar, { passive: true });
        updateNavbar();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
