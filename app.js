(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const KEY = 'imparfait-pc-drill-v1';
  const TENSE = { i: 'imparfait', p: 'passé composé' };
  const REVIEW_CHANCE = 0.35; // how often a previously missed sentence comes back
  const REVIEW_GAP = 4;       // sentences to wait before repeating a missed one
  const CLEAR_AFTER = 2;      // correct answers needed to retire a missed sentence

  const ISSUES = 'https://github.com/will-corbett/french-drills/issues/new';
  let save = { mode: 'choose', contrast: false, stats: { i: [0, 0], p: [0, 0] }, missed: {}, reported: [] };
  try { save = Object.assign(save, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) { /* fresh start */ }
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(save)); } catch (e) { /* private mode */ } };

  let all = [], byId = new Map(), current = null, blanks = [], checked = false, lastInput = null;
  let streak = 0;
  const recent = [];

  const norm = (s) => s.toLowerCase().replace(/[’‘`]/g, "'").replace(/\s*'\s*/g, "'").replace(/\s+/g, ' ').trim();
  const bare = (s) => norm(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const noAgreement = (s) => norm(s).replace(/(e|s|es)$/, '');

  function pickNext() {
    const pool = all.filter((s) => (!save.contrast || s.mixed) && !save.reported.includes(s.id));
    const due = Object.keys(save.missed).map(Number)
      .filter((id) => byId.has(id) && !save.reported.includes(id) && !recent.slice(-REVIEW_GAP).includes(id) && (!save.contrast || byId.get(id).mixed));
    if (due.length && Math.random() < REVIEW_CHANCE) return byId.get(due[Math.floor(Math.random() * due.length)]);
    for (let n = 0; n < 50; n++) {
      const s = pool[Math.floor(Math.random() * pool.length)];
      if (!recent.includes(s.id)) return s;
    }
    return pool[Math.floor(Math.random() * pool.length)];
  }

  function hintHtml(h) {
    return h.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\[(.+?)\]/, '<b>$1</b>');
  }

  function show(item) {
    current = item; checked = false; blanks = []; lastInput = null;
    recent.push(item.id); if (recent.length > 150) recent.shift();
    const el = $('sentence'); el.textContent = '';
    for (const part of item.p) {
      if (typeof part === 'string') { el.append(part); continue; }
      const wrap = document.createElement('span'); wrap.className = 'blank';
      const b = { part, wrap, value: '' };
      if (save.mode === 'choose') {
        const pick = document.createElement('span'); pick.className = 'pick';
        const opts = Math.random() < 0.5 ? [part.a, part.o] : [part.o, part.a];
        for (const o of opts) {
          const btn = document.createElement('button'); btn.type = 'button'; btn.textContent = o;
          btn.onclick = () => {
            if (checked) return;
            b.value = o;
            pick.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === btn));
            refresh();
          };
          pick.append(btn);
        }
        wrap.append(pick);
      } else {
        const input = document.createElement('input');
        input.type = 'text'; input.autocomplete = 'off'; input.autocapitalize = 'off'; input.spellcheck = false;
        input.setAttribute('autocorrect', 'off'); input.setAttribute('aria-label', 'Conjugate: ' + part.h.replace(/[\[\]]/g, ''));
        input.size = Math.max(part.a.length, part.o.length, 8) + 1;
        input.oninput = () => { b.value = input.value; refresh(); };
        input.onfocus = () => { lastInput = input; };
        const hint = document.createElement('small'); hint.innerHTML = hintHtml(part.h);
        wrap.append(input, hint);
        b.input = input;
      }
      blanks.push(b); el.append(wrap);
    }
    $('english').hidden = true; $('english').textContent = item.en.join('  ·  ');
    $('hint').hidden = false; $('hint').textContent = 'Show English';
    $('verdict').hidden = true; $('source').hidden = true;
    $('report').hidden = false; $('reported').hidden = true;
    $('accents').hidden = save.mode !== 'type';
    $('go').textContent = 'Check';
    refresh();
    if (blanks[0] && blanks[0].input) blanks[0].input.focus();
  }

  function refresh() {
    if (!checked) $('go').disabled = !blanks.every((b) => b.value.trim());
  }

  function grade(b) {
    const { a, o, t } = b.part, v = norm(b.value);
    if (v === norm(a)) return { ok: true };
    if (bare(v) === bare(a)) return { ok: true, note: 'watch the accents' };
    if (t === 'p' && / (suis|es|est|sommes|êtes|sont) /.test(' ' + norm(a)) && noAgreement(v) === noAgreement(a))
      return { ok: true, note: 'agreement differs from this sentence' };
    if (save.mode === 'type' && (v === norm(o) || bare(v) === bare(o))) return { ok: false, why: 'tense' };
    return { ok: false, why: save.mode === 'type' ? 'form' : 'tense' };
  }

  function check() {
    checked = true;
    let allOk = true; const notes = new Set(); let formOnly = true;
    for (const b of blanks) {
      const g = grade(b), t = b.part.t;
      save.stats[t][0]++; if (g.ok) save.stats[t][1]++; else { allOk = false; if (g.why !== 'form') formOnly = false; }
      if (g.note) notes.add(g.note);
      b.wrap.textContent = '';
      const ans = document.createElement('span'); ans.className = 'done ' + (g.ok ? 'good' : 'bad'); ans.textContent = b.part.a;
      const tag = document.createElement('small'); tag.className = 't-' + t; tag.textContent = TENSE[t];
      b.wrap.append(ans, tag);
      if (!g.ok && save.mode === 'type') { const s = document.createElement('s'); s.textContent = b.value.trim(); b.wrap.append(s); }
    }
    const id = current.id;
    if (allOk) {
      streak++;
      if (save.missed[id]) { if (--save.missed[id] <= 0) delete save.missed[id]; }
    } else { streak = 0; if (!save.reported.includes(id)) save.missed[id] = CLEAR_AFTER; }
    persist();
    const v = $('verdict'); v.hidden = false; v.className = 'verdict ' + (allOk ? 'good' : 'bad'); v.textContent = '';
    v.append(allOk ? 'Correct' : (formOnly ? 'Not quite — check the form' : 'Not quite'));
    const extra = [...notes];
    if (!allOk) extra.push('this one will come back');
    if (extra.length) { const sp = document.createElement('span'); sp.textContent = ' — ' + extra.join('; '); v.append(sp); }
    $('english').hidden = false; $('hint').hidden = true; $('accents').hidden = true;
    const src = $('source'); src.hidden = false; src.textContent = '';
    const link = document.createElement('a');
    link.href = 'https://tatoeba.org/en/sentences/show/' + id; link.target = '_blank'; link.rel = 'noopener';
    link.textContent = 'Tatoeba #' + id;
    src.append('Source: ', link, ' by ' + current.by);
    const go = $('go'); go.textContent = 'Next'; go.disabled = false; go.focus();
    renderStats();
  }

  function renderStats() {
    const pct = ([n, c]) => (n ? Math.round((100 * c) / n) + '%' : '–');
    const cell = (value, label, cls) => `<div class="stat"><b${cls ? ` class="${cls}"` : ''}>${value}</b><span>${label}</span></div>`;
    const s = save.stats;
    $('stats').innerHTML =
      cell(pct(s.i), `imparfait (${s.i[1]}/${s.i[0]})`, 't-i') +
      cell(pct(s.p), `passé composé (${s.p[1]}/${s.p[0]})`, 't-p') +
      cell(streak, 'current streak') +
      cell(Object.keys(save.missed).length, 'to review');
  }

  function setMode(mode) {
    save.mode = mode; persist();
    document.querySelectorAll('[data-mode]').forEach((b) => b.classList.toggle('on', b.dataset.mode === mode));
    if (all.length) show(checked || !current ? pickNext() : current);
  }

  $('go').onclick = () => { if (checked) show(pickNext()); else if (!$('go').disabled) check(); };
  $('hint').onclick = () => { const e = $('english'); e.hidden = !e.hidden; $('hint').textContent = e.hidden ? 'Show English' : 'Hide English'; };
  $('report').onclick = () => {
    if (!current) return;
    const full = current.p.map((x) => (typeof x === 'string' ? x : x.a)).join('');
    const lines = ['**Sentence:** ' + full, '**English:** ' + current.en.join(' / '), ''];
    for (const x of current.p) {
      if (typeof x === 'string') continue;
      lines.push(`- Original (${TENSE[x.t]}): \`${x.a}\` · generated other tense: \`${x.o}\` · prompt: \`${x.h}\``);
    }
    lines.push('', `Tatoeba: https://tatoeba.org/en/sentences/show/${current.id} · mode: ${save.mode}`, '', "**What's wrong:** ");
    const url = ISSUES + '?title=' + encodeURIComponent('Sentence #' + current.id + ': ') + '&body=' + encodeURIComponent(lines.join('\n'));
    window.open(url, '_blank', 'noopener');
    if (!save.reported.includes(current.id)) save.reported.push(current.id);
    delete save.missed[current.id];
    persist(); renderStats();
    $('report').hidden = true; $('reported').hidden = false;
  };
  $('contrast').checked = save.contrast;
  $('contrast').onchange = (e) => { save.contrast = e.target.checked; persist(); show(pickNext()); };
  $('reset').onclick = () => {
    if (!confirm('Reset your stats and review list?')) return;
    save.stats = { i: [0, 0], p: [0, 0] }; save.missed = {}; streak = 0; persist(); renderStats();
  };
  document.querySelectorAll('[data-mode]').forEach((b) => { b.onclick = () => setMode(b.dataset.mode); });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || e.target.closest('.seg, .rules, footer, .pick, #hint, .report')) return;
    if (e.target.id === 'go') return; // the button handles its own Enter
    e.preventDefault(); $('go').click();
  });
  for (const ch of 'é è ê à â ç î ô ù û ë ï œ'.split(' ')) {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = ch; b.tabIndex = -1;
    b.onmousedown = (e) => e.preventDefault(); // keep focus in the input
    b.onclick = () => {
      const inp = lastInput || (blanks[0] && blanks[0].input); if (!inp || checked) return;
      const s = inp.selectionStart ?? inp.value.length, en = inp.selectionEnd ?? s;
      inp.value = inp.value.slice(0, s) + ch + inp.value.slice(en);
      inp.focus(); inp.setSelectionRange(s + ch.length, s + ch.length);
      inp.dispatchEvent(new Event('input'));
    };
    $('accents').append(b);
  }

  renderStats();
  fetch('data/sentences.json')
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((data) => {
      all = data;
      for (const s of all) {
        s.mixed = new Set(s.p.filter((x) => typeof x !== 'string').map((x) => x.t)).size === 2;
        byId.set(s.id, s);
      }
      setMode(save.mode);
    })
    .catch(() => { $('sentence').textContent = 'Could not load the sentences. If you opened this file directly, serve the folder over HTTP instead.'; });
})();
