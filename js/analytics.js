/* ============================================================================
   KONYA DİŞ HEKİMİ — analytics.js
   Self-hosted analytics + conversion tracking. No inline snippets (keeps CSP
   strict: this file is 'self'; it loads gtag/clarity/sentry from their domains,
   already allow-listed in _headers CSP).

   ┌──────────────────────────────────────────────────────────────────────────┐
   │  CONFIG IS THE SINGLE SOURCE OF TRUTH. To go live, edit only the CONFIG    │
   │  object below (paste IDs/DSN). Leave a value as its placeholder/empty to   │
   │  keep that tool disabled. No other code needs to change.                   │
   └──────────────────────────────────────────────────────────────────────────┘

   KVKK / Google Consent Mode v2:
   - Consent defaults to DENIED for all storage before any tag loads.
   - With CONSENT_REQUIRED = true (default), GA4 + Clarity do NOT load until the
     user explicitly accepts via the cookie banner (window.kdConsent.set).
   - First-party conversion events (tel/WhatsApp/map clicks) are cookieless and
     run regardless — they only push to dataLayer (no network until GA loads).
   ============================================================================ */
(function () {
  'use strict';

  /* ====================== CONFIG (edit IDs here only) ====================== */
  var CONFIG = {
    GA4_ID:           'G-XXXXXXXXXX',          // Google Analytics 4 Measurement ID
    CLARITY_ID:       'CLARITY_PROJECT_ID',    // Microsoft Clarity project id
    SENTRY_DSN:       '',                      // Sentry DSN (browser). Empty = off.
    SENTRY_LOADER:    'https://js.sentry-cdn.com/PUBLIC_KEY.min.js', // Sentry > Loader Script
    SENTRY_ENV:       'production',            // Sentry environment tag
    ANONYMIZE_IP:     true,                    // GA4 IP anonymization
    CONSENT_REQUIRED: true                     // KVKK: wait for explicit consent (recommended)
  };
  var CONSENT_KEY = 'konyadishekimi-consent';         // localStorage: 'granted' | 'denied'

  var isSet = function (v, ph) { return v && v.indexOf(ph) === -1; };

  /* ---------- branch resolver (for conversion labels) ---------- */
  var BRANCHES = {
    '905467332713': 'Karatay',  '05467332713': 'Karatay',
    '905513424442': 'Selcuklu', '05513424442': 'Selcuklu',
    '905525994959': 'Meram',    '05525994959': 'Meram',
    '4443442': 'CagriMerkezi'
  };
  function branchOf(raw) {
    var d = (raw || '').replace(/\D/g, '');
    return BRANCHES[d] || BRANCHES[d.replace(/^90/, '0')] || 'Bilinmeyen';
  }

  /* ---------- gtag bootstrap + Consent Mode v2 default (denied) ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  // MUST run before any tag: default every storage to denied (Consent Mode v2).
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'granted',
    security_storage: 'granted',
    wait_for_update: 500
  });

  /* ---------- tag loaders (idempotent) ---------- */
  var gaLoaded = false, clarityLoaded = false, sentryLoaded = false;

  function loadGA() {
    if (gaLoaded || !isSet(CONFIG.GA4_ID, 'XXXXXXXXXX')) return;
    gaLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.GA4_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', CONFIG.GA4_ID, { anonymize_ip: CONFIG.ANONYMIZE_IP });
  }

  function loadClarity() {
    if (clarityLoaded || !isSet(CONFIG.CLARITY_ID, 'CLARITY_PROJECT_ID')) return;
    clarityLoaded = true;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CONFIG.CLARITY_ID);
  }

  function loadSentry() {
    if (sentryLoaded || !CONFIG.SENTRY_DSN || CONFIG.SENTRY_LOADER.indexOf('PUBLIC_KEY') !== -1) return;
    sentryLoaded = true;
    var s = document.createElement('script');
    s.src = CONFIG.SENTRY_LOADER; s.crossOrigin = 'anonymous'; s.async = true;
    document.head.appendChild(s);
  }

  // Safe event helper — works even if GA isn't loaded yet (queues to dataLayer).
  function track(name, params) {
    try { gtag('event', name, params || {}); } catch (e) {}
    try { if (window.clarity) window.clarity('event', name); } catch (e) {}
  }
  window.kdTrack = track; // forms (script.js) call this

  /* ====================== CONSENT MANAGEMENT (KVKK) ====================== */
  function getConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }
  function startAnalytics() {
    // GA as early as possible (page_view); Clarity + Sentry deferred to idle/load
    // so they never compete with LCP.
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', loadGA);
    } else { loadGA(); }
    var heavy = function () { loadClarity(); loadSentry(); };
    if ('requestIdleCallback' in window) requestIdleCallback(heavy, { timeout: 4000 });
    else window.addEventListener('load', function () { setTimeout(heavy, 1200); });
  }
  function applyConsent(state) {
    if (state === 'granted') {
      gtag('consent', 'update', { analytics_storage: 'granted' });
      startAnalytics();
    } else {
      gtag('consent', 'update', { analytics_storage: 'denied' });
    }
  }
  // Public API used by the cookie banner (script.js → initCookieConsent).
  window.kdConsent = {
    get: getConsent,
    set: function (state) {
      state = (state === 'granted') ? 'granted' : 'denied';
      try { localStorage.setItem(CONSENT_KEY, state); } catch (e) {}
      applyConsent(state);
    },
    reset: function () { try { localStorage.removeItem(CONSENT_KEY); } catch (e) {} }
  };

  /* ============= Conversion tracking (delegated, cookieless) ============= */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('wa.me/') !== -1 || href.indexOf('api.whatsapp.com') !== -1) {
      // Extract ONLY the phone number (not digits inside the ?text= query).
      var wnum = (href.match(/(?:wa\.me\/|phone=)(\d+)/) || [])[1] || '';
      track('whatsapp_click', { branch: branchOf(wnum), link_url: href.split('?')[0], transport_type: 'beacon' });
    } else if (href.indexOf('tel:') === 0) {
      var tnum = href.replace('tel:', '');
      track('phone_call_click', { branch: branchOf(tnum), phone: tnum });
    }
  }, true);
  // Map facade is a div[role=button], not an <a> — track it too.
  document.addEventListener('click', function (e) {
    var m = e.target.closest && e.target.closest('.map-facade');
    if (m) track('map_open', { branch: (m.getAttribute('aria-label') || '').replace(/ .*/, '') });
  }, true);

  /* ====================== BOOT ====================== */
  if (!CONFIG.CONSENT_REQUIRED) {
    // Consent not required (e.g. you run your own banner elsewhere): load now.
    gtag('consent', 'update', { analytics_storage: 'granted' });
    startAnalytics();
  } else if (getConsent() === 'granted') {
    // Returning visitor who already accepted.
    applyConsent('granted');
  }
  // Otherwise: stay dormant until the cookie banner calls kdConsent.set().
})();
