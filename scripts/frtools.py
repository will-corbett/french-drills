"""Shared helpers for the data build scripts: Tatoeba and Lexique loading, tokenising."""
import collections
import json
import re
from pathlib import Path

TOKEN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿœŒ]+(?:-[A-Za-zÀ-ÖØ-öø-ÿœŒ]+)*['’]?")
VOWELS = "aeiouyàâäéèêëîïôöùûüœ"
UNPLEASANT = re.compile(r"viol|prostitu|suicid|tué|tuer|tuai|assassin|meurtr|sexe|sexuel|nazi|merde|putain|"
                        r"baisé|baisai|encul|salop|pédophil|cadavre|poignard|étrangl|tortur", re.I)
DATA = Path(__file__).resolve().parent.parent / "data"


def tokens(text):
    """List of (lowercased token with ' apostrophes, start, end)."""
    return [(m.group(0).lower().replace("’", "'"), m.start(), m.end()) for m in TOKEN.finditer(text)]


def adjacent(text, a, b):
    """True when token a is followed by token b with at most a single space between them."""
    return text[a[2]:b[1]] in ("", " ", " ", " ")


def vowel_start(word, aspirated=()):
    w = word.lower()
    return w[:1] in VOWELS or (w[:1] == "h" and w not in aspirated)


def load_lexique(raw):
    """Return (lemmas_of_form, forms, freq, infinitives).

    lemmas_of_form: form -> set(lemma) for verbs
    forms: lemma -> {tag -> form}, tag like 'ind:imp:3s', 'cnd:pre:1p', 'par:pas', 'inf'
    """
    lemmas_of_form = collections.defaultdict(set)
    forms = collections.defaultdict(dict)
    best = {}
    freq = {}
    infinitives = set()
    with open(Path(raw) / "Lexique383.tsv", encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        for line in f:
            r = line.rstrip("\n").split("\t")
            if r[ix["cgram"]] not in ("VER", "AUX"):
                continue
            form, lemma, info = r[ix["ortho"]], r[ix["lemme"]], r[ix["infover"]]
            if " " in form or "-" in form:
                continue
            lemmas_of_form[form].add(lemma)
            freq[lemma] = max(freq.get(lemma, 0.0), float(r[ix["freqlemfilms2"]] or 0))
            for tag in info.strip(";").split(";"):
                if not tag:
                    continue
                if tag == "inf":
                    infinitives.add(form)
                if tag == "par:pas":
                    # keep the masculine singular
                    g, n = r[ix["genre"]], r[ix["nombre"]]
                    if g == "f" or n == "p":
                        continue
                if not ending_ok(form, tag):
                    continue
                f_form = float(r[ix["freqfilms2"]] or 0) + float(r[ix["freqlivres"]] or 0)
                if (lemma, tag) not in best or f_form > best[(lemma, tag)]:
                    best[(lemma, tag)] = f_form
                    forms[lemma][tag] = form
    return lemmas_of_form, forms, freq, infinitives


ENDINGS = {
    "ind:imp": {"1s": "ais", "2s": "ais", "3s": "ait", "1p": "ions", "2p": "iez", "3p": "aient"},
    "cnd:pre": {"1s": "rais", "2s": "rais", "3s": "rait", "1p": "rions", "2p": "riez", "3p": "raient"},
    "ind:fut": {"1s": "rai", "2s": "ras", "3s": "ra", "1p": "rons", "2p": "rez", "3p": "ront"},
}


def ending_ok(form, tag):
    """Lexique has some mis-tagged rows; reject forms whose ending cannot match the tag."""
    for prefix, ends in ENDINGS.items():
        if tag.startswith(prefix + ":"):
            return form.endswith(ends.get(tag[-2:], ""))
    return True


def load_tatoeba(raw, min_len=15, max_len=120):
    """Yield (id, text, user, english_list) for French sentences by native speakers with an English translation."""
    raw = Path(raw)
    natives = set()
    with open(raw / "user_languages.csv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) >= 3 and r[0] == "fra" and r[1] == "5":
                natives.add(r[2])
    links = collections.defaultdict(list)
    with open(raw / "fra-eng_links.tsv", encoding="utf-8") as f:
        for line in f:
            a, b = line.split()
            links[int(a)].append(int(b))
    rows = []
    with open(raw / "fra_sentences_detailed.tsv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) < 4:
                continue
            sid, text, user = int(r[0]), r[2].strip(), r[3]
            if user not in natives or sid not in links:
                continue
            if not (min_len <= len(text) <= max_len) or any(ord(c) > 0xFFFF for c in text):
                continue
            if re.search(r"[0-9\"«»()\[\]\n]", text) or UNPLEASANT.search(text):
                continue
            rows.append((sid, text, user))
    need = {e for sid, _, _ in rows for e in links[sid]}
    eng = {}
    with open(raw / "eng_sentences.tsv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if int(r[0]) in need:
                eng[int(r[0])] = r[2]
    seen = set()
    for sid, text, user in rows:
        key = re.sub(r"\W+", " ", text.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        en = sorted({eng[e] for e in links[sid] if e in eng}, key=len)[:2]
        if en:
            yield sid, text, user, en


def split_parts(text, blanks):
    """blanks: list of (start, end, blank_dict). Returns the item 'p' list."""
    parts, pos = [], 0
    for s, e, b in sorted(blanks, key=lambda x: x[0]):
        if s > pos:
            parts.append(text[pos:s])
        parts.append(b)
        pos = e
    if pos < len(text):
        parts.append(text[pos:])
    return parts


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", len(data), "items to", path, path.stat().st_size // 1024, "KB")
