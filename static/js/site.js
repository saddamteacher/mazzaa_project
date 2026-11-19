/* MAZZAA: согласие на cookie, аналитика, анимации главной. Без зависимостей. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  root.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function json(id) { try { return JSON.parse(doc.getElementById(id).textContent); } catch (e) { return null; } }
  function store(key, value) {
    try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch (e) { return null; }
  }

  /* ---------- Аналитика (включается только после согласия) ---------- */
  var cfg = json('mz-config') || {}, loaded = false, queue = [];
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' });

  function script(src) { var s = doc.createElement('script'); s.async = true; s.src = src; doc.head.appendChild(s); }
  function loadAnalytics() {
    if (loaded) return; loaded = true;
    gtag('consent', 'update', { ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted' });
    if (cfg.gtm) {
      window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
      script('https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(cfg.gtm));
    } else if (cfg.ga4 || cfg.ads) {
      script('https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(cfg.ga4 || cfg.ads));
      gtag('js', new Date());
      if (cfg.ga4) gtag('config', cfg.ga4);
      if (cfg.ads) gtag('config', cfg.ads);
    }
    if (cfg.pixel) {
      var fbq = window.fbq = function () { fbq.callMethod ? fbq.callMethod.apply(fbq, arguments) : fbq.queue.push(arguments); };
      fbq.queue = []; fbq.loaded = true; fbq.version = '2.0'; window._fbq = fbq;
      script('https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', cfg.pixel); fbq('track', 'PageView');
    }
    queue.splice(0).forEach(function (e) { send(e[0], e[1]); });
  }
  var META = { generate_lead: 'Lead', order_submit: 'SubmitApplication', view_price_list: 'ViewContent', click_whatsapp: 'Contact', click_telegram: 'Contact' };
  function send(name, params) {
    if (!cfg.gtm && (cfg.ga4 || cfg.ads)) {
      gtag('event', name, params);
      var label = name === 'generate_lead' ? cfg.adsLead : name === 'order_submit' ? cfg.adsOrder : '';
      if (cfg.ads && label) gtag('event', 'conversion', { send_to: cfg.ads + '/' + label, value: params.value, currency: params.currency });
    }
    if (window.fbq) META[name] ? window.fbq('track', META[name], params) : window.fbq('trackCustom', name, params);
  }
  function track(name, params) {
    params = params || {};
    var item = { event: name }; for (var k in params) item[k] = params[k];
    window.dataLayer.push(item);               // GTM получает событие всегда (с учётом Consent Mode)
    loaded ? send(name, params) : queue.push([name, params]);
  }
  window.mzTrack = track;

  var banner = doc.getElementById('cookie'), consent = store('mz_consent');
  if (consent === 'granted') loadAnalytics(); else if (!consent && banner) banner.hidden = false;
  doc.addEventListener('click', function (e) {
    var c = e.target.closest('[data-consent]');
    if (c) { store('mz_consent', c.dataset.consent); banner.hidden = true; if (c.dataset.consent === 'granted') loadAnalytics(); return; }
    if (e.target.closest('#cookie-reset')) { try { localStorage.removeItem('mz_consent'); } catch (err) {} location.reload(); return; }
    var t = e.target.closest('[data-track]');
    if (t) track(t.dataset.track, { link: t.getAttribute('href') || '' });
  });
  (json('mz-events') || []).forEach(function (e) { var n = e.event; delete e.event; track(n, e); });
  var viewed = doc.querySelector('[data-track-view]'); if (viewed) track(viewed.dataset.trackView);

  /* ---------- Шапка и меню ---------- */
  var hdr = doc.getElementById('hdr'), burger = doc.getElementById('burger'), nav = doc.getElementById('nav');
  if (burger) burger.addEventListener('click', function () {
    burger.setAttribute('aria-expanded', nav.classList.toggle('is-open'));
  });

  /* ---------- Появление блоков ---------- */
  var reveals = doc.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el, i) { el.style.transitionDelay = (i % 4) * 70 + 'ms'; io.observe(el); });
  } else reveals.forEach(function (el) { el.classList.add('in'); });

  /* ---------- 3D-параллакс: чипсы летят при прокрутке и движении мыши ---------- */
  var scene = doc.querySelector('.scene'), depth = doc.getElementById('depth');
  var heroFlies = scene ? [].slice.call(scene.querySelectorAll('.fly')) : [];
  var depthFlies = depth ? [].slice.call(depth.querySelectorAll('[data-depth]')) : [];
  var mx = 0, my = 0, tx = 0, ty = 0, ticking = false;
  function frame() {
    ticking = false;
    var y = window.scrollY, vh = window.innerHeight;
    if (hdr) hdr.classList.toggle('is-stuck', y > 40);
    if (reduce) return;
    tx += (mx - tx) * 0.08; ty += (my - ty) * 0.08;
    if (y < vh * 1.3) heroFlies.forEach(function (el) {
      var d = +el.dataset.depth, r = +el.dataset.rot || 0, p = y / vh;
      el.style.transform = 'translate3d(' + (tx * d * 46) + 'px,' + (ty * d * 30 - y * d * 0.55) + 'px,' + (d * 120 * p) + 'px) ' +
        'rotateX(' + (p * r * 0.6) + 'deg) rotateY(' + (tx * d * 14) + 'deg) rotate(' + (r * 0.25 + p * r) + 'deg)';
    });
    if (depth) {
      var rect = depth.getBoundingClientRect(), total = rect.height - vh;
      if (rect.top < vh && rect.bottom > 0) {
        var p2 = Math.min(1.2, Math.max(-0.2, -rect.top / (total || 1)));
        depthFlies.forEach(function (el) {
          var d2 = +el.dataset.depth, r2 = +el.dataset.rot || 0, c = p2 - 0.5;
          if (el.classList.contains('depth__word')) {
            el.style.transform = 'scale(' + (0.7 + p2 * 0.6) + ')'; el.style.opacity = 1 - Math.abs(c) * 1.1; return;
          }
          el.style.transform = 'translate3d(' + (tx * d2 * 30) + 'px,' + (c * d2 * vh * 0.42) + 'px,' + (c * -d2 * 260) + 'px) ' +
            'rotateX(' + (c * r2) + 'deg) rotateY(' + (c * r2 * 0.7) + 'deg) rotate(' + (r2 * p2) + 'deg)';
        });
      }
    }
    if (Math.abs(mx - tx) > 0.002 || Math.abs(my - ty) > 0.002) request();
  }
  function request() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request);
  window.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    mx = e.clientX / window.innerWidth - 0.5; my = e.clientY / window.innerHeight - 0.5; request();
  }, { passive: true });
  request();

  /* ---------- Наклон баннеров ---------- */
  if (!reduce) doc.querySelectorAll('.tilt').forEach(function (el) {
    el.addEventListener('pointermove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.transform = 'rotateY(' + ((e.clientX - r.left) / r.width - 0.5) * 14 + 'deg) rotateX(' + ((e.clientY - r.top) / r.height - 0.5) * -12 + 'deg)';
    });
    el.addEventListener('pointerleave', function () { el.style.transform = ''; });
  });

  /* ---------- Искры над огнём ---------- */
  var canvas = doc.getElementById('embers');
  if (canvas && !reduce) {
    var ctx = canvas.getContext('2d'), sparks = [], W, H, visible = true;
    function size() { W = canvas.width = canvas.offsetWidth; H = canvas.height = canvas.offsetHeight; }
    function spawn(any) {
      return { x: Math.random() * W, y: any ? Math.random() * H : H + 10, r: 0.8 + Math.random() * 2.6,
        vy: 0.5 + Math.random() * 1.9, vx: (Math.random() - 0.5) * 0.8, life: 0, max: 220 + Math.random() * 320, ph: Math.random() * 6.28 };
    }
    size(); window.addEventListener('resize', size);
    for (var i = 0; i < Math.min(90, W / 14); i++) sparks.push(spawn(true));
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) loop(); }).observe(canvas);
    function loop() {
      if (!visible) return;
      ctx.clearRect(0, 0, W, H);
      for (var j = 0; j < sparks.length; j++) {
        var s = sparks[j]; s.life++; s.y -= s.vy; s.x += s.vx + Math.sin(s.life / 22 + s.ph) * 0.6;
        var a = Math.max(0, 1 - s.life / s.max);
        if (a <= 0 || s.y < -10) { sparks[j] = spawn(false); continue; }
        var g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
        g.addColorStop(0, 'rgba(255,230,140,' + a + ')'); g.addColorStop(0.35, 'rgba(255,122,0,' + a * 0.7 + ')'); g.addColorStop(1, 'rgba(229,23,30,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s.x, s.y, s.r * 4, 0, 6.2832); ctx.fill();
      }
      requestAnimationFrame(loop);
    }
  }
})();
