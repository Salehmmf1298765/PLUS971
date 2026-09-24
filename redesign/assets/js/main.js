/* PLUS971 — interactions. No dependencies. */
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Page enter / leave (curtain) ---- */
  window.addEventListener('pageshow', function () { root.classList.remove('leaving'); });
  requestAnimationFrame(function () { setTimeout(function () { root.classList.add('ready'); }, reduce ? 0 : 120); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a || reduce) return;
    var href = a.getAttribute('href') || '';
    if (a.target === '_blank' || href.charAt(0) === '#' || /^(mailto|tel|https?):/.test(href) || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    root.classList.remove('menu-open'); root.classList.remove('lock');
    root.classList.add('leaving');
    setTimeout(function () { window.location.href = href; }, 560);
  });

  /* ---- Header: solid on scroll, hide on scroll down, progress bar ---- */
  var header = document.querySelector('.header');
  var prog = document.querySelector('.progress i');
  var lastY = 0, ticking = false;
  function onScroll() {
    var y = window.scrollY || 0;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if (header) {
      header.classList.toggle('solid', y > 40);
      header.classList.toggle('hide', y > 500 && y > lastY && !root.classList.contains('menu-open'));
    }
    if (prog) prog.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, y / h) : 0) + ')';
    lastY = y; ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  onScroll();

  /* ---- Menu ---- */
  function setMenu(open) {
    root.classList.toggle('menu-open', open);
    root.classList.toggle('lock', open);
    document.querySelectorAll('.burger, .tab-menu').forEach(function (b) { b.setAttribute('aria-expanded', open ? 'true' : 'false'); });
  }
  document.querySelectorAll('.burger, .tab-menu').forEach(function (b) {
    b.addEventListener('click', function () { setMenu(!root.classList.contains('menu-open')); });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* ---- Accordion ---- */
  document.querySelectorAll('.acc-item').forEach(function (item) {
    var btn = item.querySelector('.acc-btn');
    btn.addEventListener('click', function () {
      var open = item.classList.contains('open');
      item.parentElement.querySelectorAll('.acc-item').forEach(function (i) {
        i.classList.remove('open'); i.querySelector('.acc-btn').setAttribute('aria-expanded', 'false');
      });
      if (!open) { item.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); }
    });
  });

  /* ---- Reveal on scroll ---- */
  var targets = document.querySelectorAll('.rv, .rv-line, .img');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) { el.classList.add('in'); });
  }
  document.querySelectorAll('[data-stagger]').forEach(function (p) {
    Array.prototype.forEach.call(p.children, function (c, i) { c.style.setProperty('--i', i); });
  });

  /* ---- Statement: words light up as you scroll ---- */
  document.querySelectorAll('.statement').forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map(function (w) { return '<span class="w">' + w + '</span>'; }).join(' ');
    var ws = el.querySelectorAll('.w');
    function upd() {
      var r = el.getBoundingClientRect();
      var vh = window.innerHeight;
      var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.25)));
      var n = Math.round(p * ws.length);
      ws.forEach(function (w, i) { w.classList.toggle('lit', i < n); });
    }
    window.addEventListener('scroll', upd, { passive: true }); upd();
    if (reduce) ws.forEach(function (w) { w.classList.add('lit'); });
  });

  /* ---- Counters ---- */
  document.querySelectorAll('.count').forEach(function (el) {
    var end = parseFloat(el.getAttribute('data-to')), suffix = el.getAttribute('data-suffix') || '';
    if (isNaN(end)) return;
    var done = false;
    function run() {
      if (done) return; done = true;
      var t0 = performance.now(), dur = 1400;
      (function step(t) {
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(end * e) + suffix;
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    }
    if ('IntersectionObserver' in window && !reduce) {
      new IntersectionObserver(function (en, o) { if (en[0].isIntersecting) { run(); o.disconnect(); } }, { threshold: .5 }).observe(el);
    } else { el.textContent = end + suffix; }
  });

  /* ---- Rails: dots for horizontal snap carousels (mobile) ---- */
  document.querySelectorAll('.rail').forEach(function (rail) {
    var dots = rail.parentElement.querySelector('.rail-dots');
    if (!dots) return;
    var kids = rail.children;
    dots.innerHTML = Array.prototype.map.call(kids, function () { return '<i></i>'; }).join('');
    var ds = dots.querySelectorAll('i');
    function upd() {
      var idx = 0, min = Infinity, x = rail.scrollLeft + rail.clientWidth * 0.1;
      Array.prototype.forEach.call(kids, function (k, i) { var d = Math.abs(k.offsetLeft - x); if (d < min) { min = d; idx = i; } });
      ds.forEach(function (d, i) { d.classList.toggle('on', i === idx); });
    }
    rail.addEventListener('scroll', upd, { passive: true }); upd();
  });

  /* ---- Magnetic buttons (pointer devices only) ---- */
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches && !reduce) {
    document.querySelectorAll('.btn, .tile-cap .c, .burger').forEach(function (b) {
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.18, y = (e.clientY - r.top - r.height / 2) * 0.18;
        b.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
    /* Parallax on hero + band images */
    var px = document.querySelectorAll('.hero-media img, .band-bg img, .cta-bg img');
    window.addEventListener('scroll', function () {
      px.forEach(function (im) {
        var r = im.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) return;
        var p = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight;
        im.style.translate = '0 ' + (p * -40) + 'px';
      });
    }, { passive: true });
  }

  /* ---- Contact form: no backend yet, open the visitor's mail app ---- */
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var d = new FormData(form);
      var body = 'Full Name: ' + d.get('name') + '\nPhone: ' + d.get('phone') + '\nEmail: ' + d.get('email') + '\n\n' + d.get('message');
      window.location.href = 'mailto:Info@plus971re.ae?subject=' + encodeURIComponent('Website enquiry - ' + d.get('name')) + '&body=' + encodeURIComponent(body);
      form.classList.add('sent');
    });
  }

  /* ---- Footer year ---- */
  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
