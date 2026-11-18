/* Shared drill engine for the fill-in-the-blank pages.
 *
 * Item format (one sentence, text or question):
 * {
 *   id: string|number,            unique within the page
 *   ctx?: string,                 instruction or context shown above the item (plain text)
 *   head?: string,                small heading shown above the context (plain text)
 *   en?: [string],                English translation, revealed on demand
 *   src?: {id, by},               Tatoeba source
 *   layout?: 'inline'|'list'|'bank',
 *   bank?: [string],              extra distractor chips for layout 'bank'
 *   p: [ "text", {               the sentence: strings and blanks
 *        a: string,               correct answer as written in the text
 *        alt?: [string],          other accepted answers
 *        o?: [string],            wrong options for choose mode
 *        h?: string,              prompt for type mode, e.g. "je [avoir]"
 *        x?: string,              explanation shown after checking
 *        t?: string,              tag for the stats (a key of config.tags)
 *        k?: string,              review key (defaults to the answer)
 *        cap?: boolean            bank layout: capitalise the chip in this slot
 *      } ]
 * }
 */
window.Drill = (() => {
  'use strict';
  const ISSUES = 'https://github.com/will-corbett/french-drills/issues/new';
  const REVIEW_CHANCE = 0.35, REVIEW_GAP = 4, CLEAR_AFTER = 2;
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const norm = (s) => s.toLowerCase().replace(/[’‘`]/g, "'").replace(/\s*'\s*/g, "'").replace(/[\s  ]+/g, ' ').replace(/\s*([?!;:,.])$/, '').trim();
  const bare = (s) => norm(s).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const capFirst = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const blanksOf = (item) => item.p.filter((x) => typeof x !== 'string');
  const keyOf = (b) => b.k || norm(b.a);

  function start(cfg) {
    const KEY = cfg.storageKey;
    let save = { mode: null, deck: null, onlyMistakes: false, stats: {}, missed: {}, notes: {}, reported: [] };
    try { save = Object.assign(save, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) { /* fresh start */ }
    const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(save)); } catch (e) { /* private mode */ } };

    let decks = [], deck = null, items = [], current = null, slots = [], checked = false, lastInput = null, activeSlot = null;
    let streak = 0;
    const recent = [];

    // ---------- selection
    function poolFor(d) {
      return d.items.filter((it) => !save.reported.includes(String(it.id)));
    }
    function hasMissed(it) { return blanksOf(it).some((b) => save.missed[keyOf(b)]); }
    function pickNext() {
      const pool = items;
      if (!pool.length) return null;
      const missedPool = pool.filter(hasMissed);
      if (save.onlyMistakes) {
        if (!missedPool.length) return null;
        const fresh = missedPool.filter((it) => !recent.slice(-Math.min(REVIEW_GAP, missedPool.length - 1)).includes(it.id));
        return (fresh.length ? fresh : missedPool)[Math.floor(Math.random() * (fresh.length || missedPool.length))];
      }
      const due = missedPool.filter((it) => !recent.slice(-REVIEW_GAP).includes(it.id));
      if (due.length && Math.random() < REVIEW_CHANCE) return due[Math.floor(Math.random() * due.length)];
      const avoid = new Set(recent.slice(-Math.min(150, Math.floor(pool.length * 0.7))));
      for (let n = 0; n < 60; n++) {
        const it = pool[Math.floor(Math.random() * pool.length)];
        if (!avoid.has(it.id)) return it;
      }
      return pool[Math.floor(Math.random() * pool.length)];
    }

    // ---------- rendering
    function modeFor() {
      const modes = deck.modes || ['choose'];
      return modes.includes(save.mode) ? save.mode : modes[0];
    }
    function hintHtml(h) {
      return h.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\[(.+?)\]/, '<b>$1</b>');
    }

    function show(item) {
      current = item; checked = false; slots = []; lastInput = null; activeSlot = null;
      const card = $('card');
      $('explain').hidden = true; $('explain').textContent = '';
      $('verdict').hidden = true; $('source').hidden = true;
      $('reportwrap').hidden = !item; $('report').hidden = false; $('reported').hidden = true;
      const sentence = $('sentence'); sentence.textContent = ''; sentence.className = 'sentence';
      $('ctx').hidden = true; $('head').hidden = true; $('bank').hidden = true; $('bank').textContent = '';
      $('listopts').hidden = true; $('listopts').textContent = '';
      if (!item) {
        sentence.textContent = save.onlyMistakes ? 'Nothing left to review in this set. Untick “Only my mistakes” to carry on.' : 'No items in this set.';
        $('go').disabled = true; $('hint').hidden = true; $('accents').hidden = true;
        return;
      }
      recent.push(item.id); if (recent.length > 400) recent.shift();
      if (item.head) { $('head').hidden = false; $('head').textContent = item.head; }
      if (item.ctx) { $('ctx').hidden = false; $('ctx').textContent = item.ctx; }
      const mode = modeFor();
      const layout = item.layout || 'inline';
      if (layout === 'bank') sentence.classList.add('prose');
      if (layout === 'list') sentence.classList.add('question');
      let n = 0;
      for (const part of item.p) {
        if (typeof part === 'string') { sentence.append(part); continue; }
        n++;
        const wrap = el('span', 'blank');
        const slot = { part, wrap, value: '' };
        if (layout === 'bank') {
          const btn = el('button', 'slot', String(n)); btn.type = 'button';
          btn.onclick = () => {
            if (checked) return;
            if (slot.value) { slot.value = ''; slot.chip.classList.remove('used'); slot.chip = null; renderSlot(slot); }
            setActive(slot); refresh();
          };
          slot.btn = btn; slot.n = n; wrap.append(btn);
        } else if (layout === 'list') {
          wrap.classList.add('gap'); wrap.textContent = '_____';
          const opts = shuffle([part.a, ...(part.o || [])]);
          const box = $('listopts'); box.hidden = false;
          opts.forEach((o, i) => {
            const b = el('button', 'opt'); b.type = 'button';
            b.append(el('kbd', null, String(i + 1)), el('span', null, o));
            b.onclick = () => {
              if (checked) return;
              slot.value = o;
              box.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
              refresh();
            };
            box.append(b);
          });
        } else if (mode === 'type' && part.h) {
          const input = el('input'); input.type = 'text'; input.autocomplete = 'off'; input.autocapitalize = 'off'; input.spellcheck = false;
          input.setAttribute('autocorrect', 'off'); input.setAttribute('aria-label', 'Answer: ' + part.h.replace(/[[\]]/g, ''));
          input.size = Math.max(part.a.length, 6) + 2;
          input.oninput = () => { slot.value = input.value; refresh(); };
          input.onfocus = () => { lastInput = input; };
          const hint = el('small'); hint.innerHTML = hintHtml(part.h);
          wrap.append(input, hint); slot.input = input;
        } else {
          const pick = el('span', 'pick');
          for (const o of shuffle([part.a, ...(part.o || [])])) {
            const b = el('button', null, o); b.type = 'button';
            b.onclick = () => {
              if (checked) return;
              slot.value = o;
              pick.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
              refresh();
            };
            pick.append(b);
          }
          wrap.append(pick);
          if (part.h && cfg.showHintInChoose) { const hint = el('small'); hint.innerHTML = hintHtml(part.h); wrap.append(hint); }
        }
        slots.push(slot); sentence.append(wrap);
      }
      if (layout === 'bank') buildBank(item);
      const en = item.en && item.en.length ? item.en.join('  ·  ') : '';
      $('english').hidden = true; $('english').textContent = en;
      $('hint').hidden = !en; $('hint').textContent = 'Show English';
      $('accents').hidden = !(mode === 'type' && slots.some((s) => s.input));
      $('go').textContent = 'Check';
      refresh();
      if (slots[0] && slots[0].input) slots[0].input.focus();
      if (layout === 'bank') setActive(slots[0]);
      if (card.getBoundingClientRect().top < 0) card.scrollIntoView({ block: 'start' });
    }

    function buildBank(item) {
      const box = $('bank'); box.hidden = false;
      const words = shuffle([...slots.map((s) => s.part.a.toLowerCase()), ...(item.bank || []).map((w) => w.toLowerCase())]);
      for (const w of words) {
        const chip = el('button', 'chip', w); chip.type = 'button';
        chip.onclick = () => {
          if (checked || chip.classList.contains('used')) return;
          const slot = activeSlot && !activeSlot.value ? activeSlot : slots.find((s) => !s.value);
          if (!slot) return;
          slot.value = w; slot.chip = chip; chip.classList.add('used'); renderSlot(slot);
          setActive(slots.find((s, i) => i > slots.indexOf(slot) && !s.value) || slots.find((s) => !s.value) || null);
          refresh();
        };
        box.append(chip);
      }
    }
    function renderSlot(slot) {
      slot.btn.textContent = slot.value ? (slot.part.cap ? capFirst(slot.value) : slot.value) : String(slot.n);
      slot.btn.classList.toggle('filled', !!slot.value);
    }
    function setActive(slot) {
      activeSlot = slot;
      slots.forEach((s) => s.btn && s.btn.classList.toggle('active', s === slot));
    }
    function refresh() {
      if (!checked) $('go').disabled = !slots.length || !slots.every((s) => s.value.trim());
    }

    // ---------- grading
    function grade(slot) {
      const { a, alt = [] } = slot.part, v = norm(slot.value);
      const ok = [a, ...alt].map(norm);
      if (ok.includes(v)) return { ok: true };
      if (ok.map(bare).includes(bare(v))) return { ok: true, note: 'watch the accents' };
      return { ok: false };
    }

    function check() {
      checked = true;
      let allOk = true; const notes = new Set();
      const explain = $('explain'); explain.textContent = '';
      const seenX = new Set();
      slots.forEach((slot, i) => {
        const g = grade(slot), b = slot.part, tag = deck.id + ':' + (b.t || 'all'), k = keyOf(b);
        save.stats[tag] = save.stats[tag] || [0, 0];
        save.stats[tag][0]++; if (g.ok) save.stats[tag][1]++;
        if (g.note) notes.add(g.note);
        if (g.ok) { if (save.missed[k] && --save.missed[k] <= 0) delete save.missed[k]; }
        else { allOk = false; save.missed[k] = CLEAR_AFTER; if (b.x) save.notes[k] = { a: b.a, x: b.x }; }
        // show answer in place
        const layout = current.layout || 'inline';
        slot.wrap.textContent = '';
        const shown = layout === 'bank' && b.cap ? capFirst(b.a) : b.a;
        const ans = el('span', 'done ' + (g.ok ? 'good' : 'bad'), layout === 'bank' ? (slots.length > 1 ? `${i + 1}. ` : '') + (g.ok ? (b.cap ? capFirst(slot.value) : slot.value) : shown) : shown);
        slot.wrap.append(ans);
        if (b.t && cfg.tags && cfg.tags[b.t] && layout !== 'bank' && layout !== 'list' && norm(cfg.tags[b.t]) !== norm(b.a)) { const tg = el('small', 't-' + b.t, cfg.tags[b.t]); slot.wrap.append(tg); }
        if (!g.ok && layout !== 'list') slot.wrap.append(el('s', null, slot.value.trim()));
        // explanation line
        if (b.x && !(seenX.has(b.x) && g.ok)) {
          seenX.add(b.x);
          const li = el('li', g.ok ? 'ok' : 'ko');
          const head = el('b', null, (layout === 'bank' ? `${i + 1}. ` : '') + (b.cap ? capFirst(b.a) : b.a));
          li.append(head);
          if (!g.ok) li.append(el('span', 'yours', ` (you: ${slot.value.trim()})`));
          li.append(' — ' + b.x);
          explain.append(li);
        }
      });
      if (current.layout === 'list') {
        $('listopts').querySelectorAll('button').forEach((btn) => {
          const t = btn.lastChild.textContent, b = slots[0].part;
          if ([b.a, ...(b.alt || [])].map(norm).includes(norm(t))) btn.classList.add('right');
          else if (btn.classList.contains('on')) btn.classList.add('wrong');
        });
      }
      if (current.layout === 'bank') $('bank').hidden = true;
      explain.hidden = !explain.childNodes.length;
      streak = allOk ? streak + 1 : 0;
      persist();
      const v = $('verdict'); v.hidden = false; v.className = 'verdict ' + (allOk ? 'good' : 'bad'); v.textContent = '';
      if (slots.length > 1) {
        const right = slots.filter((s) => grade(s).ok).length;
        v.append(allOk ? `All ${slots.length} correct` : `${right} / ${slots.length} correct`);
      } else v.append(allOk ? 'Correct' : 'Not quite');
      const extra = [...notes];
      if (!allOk) extra.push('the ones you missed will come back');
      if (extra.length) v.append(el('span', null, ' — ' + extra.join('; ')));
      if (current.en && current.en.length) { $('english').hidden = false; $('hint').hidden = true; }
      $('accents').hidden = true;
      if (current.src) {
        const src = $('source'); src.hidden = false; src.textContent = '';
        const link = el('a', null, 'Tatoeba #' + current.src.id);
        link.href = 'https://tatoeba.org/en/sentences/show/' + current.src.id; link.target = '_blank'; link.rel = 'noopener';
        src.append('Source: ', link, ' by ' + current.src.by);
      }
      const go = $('go'); go.textContent = 'Next'; go.disabled = false; go.focus();
      renderStats(); renderMistakes();
    }

    // ---------- side panels
    function renderStats() {
      const pct = ([n, c]) => (n ? Math.round((100 * c) / n) + '%' : '–');
      const cell = (value, label, cls) => {
        const d = el('div', 'stat'); const b = el('b', cls || null, String(value)); d.append(b, el('span', null, label)); return d;
      };
      const box = $('stats'); box.textContent = '';
      const present = new Set(items.flatMap((it) => blanksOf(it).map((b) => b.t || 'all')));
      const tags = Object.keys(cfg.tags || {}).filter((t) => present.has(t));
      if (!tags.length || present.has('all')) tags.unshift('all');
      for (const t of tags) {
        const s = save.stats[deck.id + ':' + t] || [0, 0];
        box.append(cell(pct(s), `${(cfg.tags && cfg.tags[t]) || 'accuracy'} (${s[1]}/${s[0]})`, 't-' + t));
      }
      box.append(cell(streak, 'current streak'));
      const inDeck = new Set(items.flatMap((it) => blanksOf(it).map(keyOf)));
      box.append(cell(Object.keys(save.missed).filter((k) => inDeck.has(k)).length, 'to review in this set'));
    }
    function renderMistakes() {
      const box = $('mistakes'), list = $('mistakelist');
      const inDeck = new Set(items.flatMap((it) => blanksOf(it).map(keyOf)));
      const keys = Object.keys(save.missed).filter((k) => inDeck.has(k) && save.notes[k]);
      box.hidden = !keys.length; list.textContent = '';
      $('mistakecount').textContent = keys.length;
      for (const k of keys.sort()) {
        const li = el('li'); li.append(el('b', null, save.notes[k].a), ' — ' + save.notes[k].x); list.append(li);
      }
    }

    // ---------- controls
    function setDeck(id) {
      deck = decks.find((d) => d.id === id) || decks[0];
      save.deck = deck.id; persist();
      items = poolFor(deck);
      document.querySelectorAll('#decks button').forEach((b) => b.classList.toggle('on', b.dataset.deck === deck.id));
      const modes = deck.modes || ['choose'];
      $('modes').hidden = modes.length < 2;
      document.querySelectorAll('[data-mode]').forEach((b) => b.classList.toggle('on', b.dataset.mode === modeFor()));
      $('deckinfo').hidden = !deck.info; $('deckinfo').textContent = deck.info || '';
      recent.length = 0;
      renderStats(); renderMistakes();
      show(pickNext());
    }
    function renderDecks() {
      const box = $('decks'); box.textContent = '';
      box.hidden = decks.length < 2;
      for (const d of decks) {
        const b = el('button', null, d.label); b.type = 'button'; b.dataset.deck = d.id;
        b.onclick = () => setDeck(d.id); box.append(b);
      }
    }

    $('go').onclick = () => { if (checked) show(pickNext()); else if (!$('go').disabled) check(); };
    $('hint').onclick = () => { const e = $('english'); e.hidden = !e.hidden; $('hint').textContent = e.hidden ? 'Show English' : 'Hide English'; };
    $('only').checked = !!save.onlyMistakes;
    $('only').onchange = (e) => { save.onlyMistakes = e.target.checked; persist(); recent.length = 0; show(pickNext()); };
    document.querySelectorAll('[data-mode]').forEach((b) => {
      b.onclick = () => {
        save.mode = b.dataset.mode; persist();
        document.querySelectorAll('[data-mode]').forEach((x) => x.classList.toggle('on', x === b));
        if (current) show(checked ? pickNext() : current);
      };
    });
    $('reset').onclick = () => {
      if (!confirm('Reset your stats and review list for this page?')) return;
      save.stats = {}; save.missed = {}; save.notes = {}; streak = 0; persist(); renderStats(); renderMistakes();
    };
    $('report').onclick = () => {
      if (!current) return;
      const full = current.p.map((x) => (typeof x === 'string' ? x : `[${x.a}]`)).join('');
      const lines = [`**Page:** ${cfg.title} · ${deck.label}`, ''];
      if (current.ctx) lines.push('**Context:** ' + current.ctx, '');
      lines.push('**Item:** ' + full);
      for (const b of blanksOf(current)) lines.push(`- \`${b.a}\`${b.o ? ' · options: ' + b.o.map((o) => '`' + o + '`').join(', ') : ''}${b.x ? ' · ' + b.x : ''}`);
      if (current.src) lines.push('', `Tatoeba: https://tatoeba.org/en/sentences/show/${current.src.id}`);
      lines.push('', `Item id: ${current.id}`, '', "**What's wrong:** ");
      const url = ISSUES + '?title=' + encodeURIComponent(`${cfg.title} #${current.id}: `) + '&body=' + encodeURIComponent(lines.join('\n'));
      window.open(url, '_blank', 'noopener');
      const id = String(current.id);
      if (!save.reported.includes(id)) save.reported.push(id);
      persist();
      items = poolFor(deck);
      $('report').hidden = true; $('reported').hidden = false;
    };
    document.addEventListener('keydown', (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.key === 'Enter') {
        if (e.target.closest('nav, .seg, .controls, footer, .pick, #hint, .reportwrap, .opt, .chip, .slot, details') || e.target.id === 'go') return;
        e.preventDefault(); $('go').click(); return;
      }
      if (checked || e.target.tagName === 'INPUT') return;
      const n = parseInt(e.key, 10);
      if (!n) return;
      if (current && current.layout === 'list') { const b = $('listopts').querySelectorAll('button')[n - 1]; if (b) b.click(); }
      else if (slots.length === 1 && slots[0].wrap.querySelector('.pick')) { const b = slots[0].wrap.querySelectorAll('.pick button')[n - 1]; if (b) b.click(); }
    });
    for (const ch of 'é è ê à â ç î ô ù û ë ï œ'.split(' ')) {
      const b = el('button', null, ch); b.type = 'button'; b.tabIndex = -1;
      b.onmousedown = (e) => e.preventDefault();
      b.onclick = () => {
        const inp = lastInput || (slots[0] && slots[0].input); if (!inp || checked) return;
        const s = inp.selectionStart ?? inp.value.length, en = inp.selectionEnd ?? s;
        inp.value = inp.value.slice(0, s) + ch + inp.value.slice(en);
        inp.focus(); inp.setSelectionRange(s + ch.length, s + ch.length);
        inp.dispatchEvent(new Event('input'));
      };
      $('accents').append(b);
    }

    // ---------- load
    function load(ds) {
      return Promise.resolve(ds)
        .then((list) => Promise.all(list.map((d) => (d.items ? d : fetch(d.url).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }).then((data) => Object.assign({}, d, { items: data }))))))
        .then((list) => {
          decks = list.map((d) => Object.assign({}, d, { items: (d.filter ? d.items.filter(d.filter) : d.items).map((it) => Object.assign({}, it, { id: String(it.id) })) }));
          renderDecks();
          setDeck(save.deck);
        })
        .catch((err) => { console.error(err); $('sentence').textContent = 'Could not load the drill data. If you opened this file directly, serve the folder over HTTP instead.'; });
    }
    load(typeof cfg.decks === 'function' ? cfg.decks() : cfg.decks);

    return { setDecks: load };
  }

  /* Shared page skeleton: every drill page calls Drill.page(cfg) after its <main> placeholder. */
  function page(cfg) {
    const main = document.querySelector('main');
    main.insertAdjacentHTML('beforeend', `
  <header>
    <h1>${cfg.heading}</h1>
    ${cfg.intro ? `<p class="intro">${cfg.intro}</p>` : ''}
    ${cfg.headerExtra || ''}
    <div class="controls">
      <div class="seg wrap" id="decks" role="group" aria-label="Exercise set"></div>
      <div class="seg" id="modes" role="group" aria-label="Answer mode" hidden>
        <button type="button" data-mode="choose">Choose</button>
        <button type="button" data-mode="type">Type</button>
      </div>
      <label class="check"><input type="checkbox" id="only"> Only my mistakes</label>
    </div>
    <p class="deckinfo" id="deckinfo" hidden></p>
  </header>
  <section class="card" id="card" aria-live="polite">
    <p class="head" id="head" hidden></p>
    <p class="ctx" id="ctx" hidden></p>
    <div class="sentence" id="sentence" lang="fr">Loading…</div>
    <div class="listopts" id="listopts" lang="fr" hidden></div>
    <div class="bank" id="bank" lang="fr" hidden></div>
    <p class="english" id="english" hidden></p>
    <div class="accents" id="accents" hidden></div>
    <div class="actions">
      <button type="button" class="ghost" id="hint" hidden>Show English</button>
      <button type="button" class="primary" id="go" disabled>Check</button>
    </div>
    <p class="verdict" id="verdict" hidden></p>
    <ul class="explain" id="explain" hidden></ul>
    <p class="source" id="source" hidden></p>
    <p class="report reportwrap" id="reportwrap" hidden>
      <button type="button" class="link" id="report">Report a problem with this item</button>
      <span id="reported" hidden>Reported — you won't be shown this item again.</span>
    </p>
  </section>
  <section class="stats" id="stats"></section>
  <details class="rules mistakes" id="mistakes" hidden>
    <summary>Your mistakes to review (<span id="mistakecount">0</span>)</summary>
    <ul id="mistakelist"></ul>
  </details>
  ${cfg.rules ? `<details class="rules"><summary>Rules of thumb</summary>${cfg.rules}</details>` : ''}
  <footer>${cfg.footer || ''} <button type="button" class="link" id="reset">Reset my stats</button></footer>`);
    return start(cfg);
  }

  return { start, page, shuffle };
})();
