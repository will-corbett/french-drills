/* Colour scheme and light/dark preference, applied before the page paints. */
(function () {
  var root = document.documentElement, theme = 'house', mode = 'auto';
  try { theme = localStorage.getItem('fd-theme') || 'house'; mode = localStorage.getItem('fd-mode') || 'auto'; } catch (e) { /* defaults */ }
  function apply() {
    root.setAttribute('data-theme', theme);
    if (mode === 'auto') root.removeAttribute('data-mode'); else root.setAttribute('data-mode', mode);
  }
  apply();
  function select(label, value, options, onchange) {
    var s = document.createElement('select');
    s.setAttribute('aria-label', label);
    options.forEach(function (o) { var op = document.createElement('option'); op.value = o[0]; op.textContent = o[1]; s.appendChild(op); });
    s.value = value;
    s.onchange = function () { onchange(s.value); apply(); };
    return s;
  }
  document.addEventListener('DOMContentLoaded', function () {
    var nav = document.querySelector('nav.site');
    if (!nav) return;
    var box = document.createElement('span'); box.className = 'prefs';
    box.appendChild(select('Colour scheme', theme, [['house', 'House'], ['classic', 'Classic']], function (v) {
      theme = v; try { localStorage.setItem('fd-theme', v); } catch (e) { /* ignore */ }
    }));
    box.appendChild(select('Light or dark', mode, [['auto', 'Auto'], ['light', 'Light'], ['dark', 'Dark']], function (v) {
      mode = v; try { localStorage.setItem('fd-mode', v); } catch (e) { /* ignore */ }
    }));
    nav.appendChild(box);
  });
})();
