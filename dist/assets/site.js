/* Site chrome: theme toggle, reading-progress bar, reveal buttons, glossary filter.
   No framework, no dependencies — the whole point is that a lesson page is a
   document that happens to have three interactions bolted on. */
(function () {
  'use strict';

  /* ---- theme -------------------------------------------------------- */
  var root = document.documentElement;
  try {
    var saved = localStorage.getItem('ai4s-theme');
    if (saved) root.setAttribute('data-theme', saved);
  } catch (e) { /* private mode: fall back to the OS preference */ }

  var btn = document.getElementById('theme');
  if (btn) {
    btn.addEventListener('click', function () {
      var cur = root.getAttribute('data-theme');
      if (!cur) {
        cur = matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
      }
      var next = cur === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('ai4s-theme', next); } catch (e) {}
    });
  }

  /* ---- reading progress --------------------------------------------- */
  var bar = document.getElementById('bar');
  if (bar) {
    var tick = function () {
      var h = document.documentElement;
      var span = Math.max(1, h.scrollHeight - h.clientHeight);
      bar.style.width = ((h.scrollTop / span) * 100).toFixed(1) + '%';
    };
    addEventListener('scroll', tick, { passive: true });
    addEventListener('resize', tick, { passive: true });
    tick();
  }

  /* ---- reveal --------------------------------------------------------- */
  document.querySelectorAll('.reveal').forEach(function (b) {
    b.addEventListener('click', function () {
      var a = b.nextElementSibling;
      if (!a) return;
      a.classList.toggle('show');
      b.textContent = a.classList.contains('show') ? '收起' : '看答案';
    });
  });

  /* ---- glossary filter ------------------------------------------------ */
  var gf = document.getElementById('gfilter');
  if (gf) {
    var terms = [].slice.call(document.querySelectorAll('.gterm'));
    var groups = [].slice.call(document.querySelectorAll('.ggroup'));
    var count = document.getElementById('gcount');
    gf.addEventListener('input', function () {
      var q = gf.value.trim().toLowerCase();
      var shown = 0;
      terms.forEach(function (t) {
        var hit = !q || t.textContent.toLowerCase().indexOf(q) !== -1;
        t.hidden = !hit;
        if (hit) shown++;
      });
      // hide a whole section once every term inside it is filtered out
      groups.forEach(function (g) {
        g.hidden = !g.querySelector('.gterm:not([hidden])');
      });
      if (count) count.textContent = q ? '匹配 ' + shown + ' 条' : '共 ' + terms.length + ' 条';
    });
  }

  /* ---- deep-link highlight ------------------------------------------- */
  if (location.hash) {
    var el = document.getElementById(location.hash.slice(1));
    if (el) el.style.background = 'var(--gold-soft)';
  }
})();

/* ---- click-to-load video ------------------------------------------------
   The player is not embedded until someone asks for it: no third-party frame,
   no cookies and no extra requests for the majority of visitors who never
   press play, and the page still renders instantly on a slow connection. */
(function () {
  'use strict';
  document.querySelectorAll('.embed[data-yt]').forEach(function (box) {
    var btn = box.querySelector('.embed-play');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var id = box.getAttribute('data-yt');
      var f = document.createElement('iframe');
      // nocookie host, and autoplay only because the click was the consent
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
              '?autoplay=1&rel=0&cc_load_policy=1';
      f.title = box.getAttribute('data-title') || '视频';
      f.allow = 'accelerometer; autoplay; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      f.loading = 'lazy';
      box.innerHTML = '';
      box.appendChild(f);
    });
  });
})();
