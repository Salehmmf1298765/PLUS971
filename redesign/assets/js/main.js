(function () {
  var root = document.documentElement;

  // Mobile menu
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = root.classList.toggle('menu-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    document.querySelectorAll('.mobile-menu a').forEach(function (a) {
      a.addEventListener('click', function () {
        root.classList.remove('menu-open');
        document.body.style.overflow = '';
      });
    });
  }

  // Accordion (Our Approach)
  document.querySelectorAll('.acc-item').forEach(function (item) {
    var btn = item.querySelector('.acc-btn');
    btn.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.acc-item').forEach(function (i) {
        i.classList.remove('open');
        i.querySelector('.acc-btn').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Contact form: no backend yet, so hand the message to email (Info@plus971re.ae)
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var d = new FormData(form);
      var body =
        'Full Name: ' + d.get('name') + '\n' +
        'Phone: ' + d.get('phone') + '\n' +
        'Email: ' + d.get('email') + '\n\n' +
        d.get('message');
      window.location.href = 'mailto:Info@plus971re.ae?subject=' +
        encodeURIComponent('Website enquiry - ' + d.get('name')) +
        '&body=' + encodeURIComponent(body);
      form.classList.add('sent');
    });
  }

  // Footer year
  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
