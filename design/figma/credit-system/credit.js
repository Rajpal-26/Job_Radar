/* Shared interactions for the Credit System Flow screens */
(function () {
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* inject gauge gradient <defs> once */
  function injectDefs() {
    if ($('#cr-defs')) return;
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '0'); svg.setAttribute('height', '0');
    svg.id = 'cr-defs'; svg.style.position = 'absolute';
    svg.innerHTML = '<defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0%" stop-color="#2a9bff"/><stop offset="100%" stop-color="#0b4fc2"/></linearGradient>' +
      '<linearGradient id="ggok" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0%" stop-color="#43b96a"/><stop offset="100%" stop-color="#1b7a3d"/></linearGradient></defs>';
    document.body.appendChild(svg);
  }

  /* count-up: <b data-count="142">0</b>  or data-count-to */
  function countUp() {
    $$('[data-count]').forEach(function (el) {
      var to = parseFloat(el.getAttribute('data-count'));
      if (isNaN(to)) return;
      var dur = 1200, t0 = null;
      function step(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / dur, 1);
        var e = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(to * e).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = to.toLocaleString();
      }
      requestAnimationFrame(step);
    });
  }

  /* meters fade-in to data-w (%) */
  function meters() {
    setTimeout(function () {
      $$('.meter i').forEach(function (i) {
        var w = i.getAttribute('data-w');
        if (w != null) i.style.width = w + '%';
      });
    }, 180);
  }

  /* gauge fill from data-v (0..100) */
  function gauges() {
    setTimeout(function () {
      $$('.gauge').forEach(function (g) {
        var v = parseFloat(g.getAttribute('data-v') || '0');
        var fg = $('.g-fg', g);
        if (fg) fg.style.strokeDashoffset = (100 - v);
      });
    }, 220);
  }

  /* segmented controls: <div class="seg" data-seg> <button class="on" data-v="m">.. */
  function segments() {
    $$('.seg[data-seg]').forEach(function (seg) {
      var name = seg.getAttribute('data-seg');
      seg.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-v]');
        if (!b || b.classList.contains('on')) return;
        $$('button[data-v]', seg).forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        document.dispatchEvent(new CustomEvent('segchange', { detail: { name: name, value: b.getAttribute('data-v') } }));
      });
    });
  }

  /* toast helper: window.crToast({title,msg,kind,ms}) */
  window.crToast = function (opts) {
    var host = $('#toasts') || document.body;
    var kind = opts.kind || '';
    var t = document.createElement('div');
    t.className = 'toast ' + kind;
    t.style.marginTop = '10px';
    t.innerHTML = '<span class="gem"></span><div><b>' + (opts.title || '') + '</b>' +
      (opts.msg ? '<div class="m">' + opts.msg + '</div>' : '') + '</div>';
    host.appendChild(t);
    setTimeout(function () {
      t.style.transition = 'opacity .4s,transform .4s';
      t.style.opacity = '0'; t.style.transform = 'translateY(8px)';
      setTimeout(function () { t.remove(); }, 420);
    }, opts.ms || 3200);
  };

  /* confetti */
  window.crConfetti = function () {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var box = document.createElement('div'); box.className = 'confetti';
    var colors = ['#2a9bff', '#0b4fc2', '#43b96a', '#f2c14e', '#e0574d', '#7c3aed'];
    for (var i = 0; i < 90; i++) {
      var p = document.createElement('i');
      p.style.left = Math.random() * 100 + 'vw';
      p.style.top = '-24px';
      p.style.background = colors[i % colors.length];
      p.style.animationDuration = (1.6 + Math.random() * 1.4) + 's';
      p.style.animationDelay = (Math.random() * 0.5) + 's';
      p.style.transform = 'rotate(' + Math.random() * 360 + 'deg)';
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(function () { box.remove(); }, 3600);
  };

  /* reveal-on-load stagger */
  function reveals() {
    $$('.reveal').forEach(function (el) { el.style.opacity = '1'; });
  }

  function boot() {
    injectDefs();
    countUp();
    meters();
    gauges();
    segments();
    reveals();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
