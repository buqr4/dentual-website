/* ============================================================================
   DENTUAL KONYA — analytics.js
   Self-hosted analytics + conversion tracking. No inline snippets (keeps CSP
   strict: this file is 'self'; it loads gtag/clarity/sentry from their domains,
   already allow-listed in _headers CSP).

   >>> FILL THESE IN (then redeploy). Leave a value empty to disable that tool. <<<
   ----------------------------------------------------------------------------
   KVKK NOTE: GA4 & Clarity set cookies. For production traffic add a consent
   banner (Consent Mode v2) before relying on this at scale. See docs.
   ============================================================================ */
(function () {
  'use strict';

  var CONFIG = {
    GA4_ID:     'G-XXXXXXXXXX',          // Google Analytics 4 Measurement ID
    CLARITY_ID: 'CLARITY_PROJECT_ID',    // Microsoft Clarity project id
    SENTRY_DSN: '',                      // Sentry DSN (browser). Empty = off.
    SENTRY_LOADER: 'https://js.sentry-cdn.com/PUBLIC_KEY.min.js' // from Sentry > Loader Script
  };
  var isSet = function (v, ph) { return v && v.indexOf(ph) === -1; };

  /* ---------- branch resolver (for conversion labels) ---------- */
  var BRANCHES = {
    '905467332713': 'Karatay', '05467332713': 'Karatay',
    '905513424442': 'Selcuklu', '05513424442': 'Selcuklu',
    '905525994959': 'Meram',    '05525994959': 'Meram',
    '4443442': 'CagriMerkezi'
  };
  function branchOf(raw) {
    var d = (raw || '').replace(/\D/g, '');
    return BRANCHES[d] || BRANCHES[d.replace(/^90/, '0')] || 'Bilinmeyen';
  }

  /* ---------- GA4 (gtag) ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  function loadGA() {
    if (!isSet(CONFIG.GA4_ID, 'XXXXXXXXXX')) return;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.GA4_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', CONFIG.GA4_ID, { anonymize_ip: true });
  }
  // Safe event helper — works even if GA isn't configured yet (no-op push).
  function track(name, params) {
    try { gtag('event', name, params || {}); } catch (e) {}
    try { if (window.clarity) window.clarity('event', name); } catch (e) {}
  }
  window.dentualTrack = track; // expose for forms (script.js can call this)

  /* ---------- Microsoft Clarity ---------- */
  function loadClarity() {
    if (!isSet(CONFIG.CLARITY_ID, 'CLARITY_PROJECT_ID')) return;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CONFIG.CLARITY_ID);
  }

  /* ---------- Sentry (browser error tracking) ---------- */
  function loadSentry() {
    if (!CONFIG.SENTRY_DSN || CONFIG.SENTRY_LOADER.indexOf('PUBLIC_KEY') !== -1) return;
    var s = document.createElement('script');
    s.src = CONFIG.SENTRY_LOADER; s.crossOrigin = 'anonymous'; s.async = true;
    document.head.appendChild(s);
  }

  /* ---------- Conversion tracking (delegated, cheap) ---------- */
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
    } else if (a.classList.contains('map-facade') || a.closest('.map-facade')) {
      track('map_open', {});
    }
  }, true);
  // Map facade is a div[role=button], not an <a> — track it too.
  document.addEventListener('click', function (e) {
    var m = e.target.closest && e.target.closest('.map-facade');
    if (m) track('map_open', { branch: (m.getAttribute('aria-label') || '').replace(/ .*/, '') });
  }, true);

  /* ---------- boot (CWV-friendly ordering) ---------- */
  // GA as early as possible (page_view); Clarity + Sentry deferred to idle/load
  // so they never compete with LCP.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadGA);
  } else { loadGA(); }
  var heavy = function () { loadClarity(); loadSentry(); };
  if ('requestIdleCallback' in window) requestIdleCallback(heavy, { timeout: 4000 });
  else window.addEventListener('load', function () { setTimeout(heavy, 1200); });
})();
