#!/usr/bin/env python3
"""Build data/si.json: hypotheses with si + imparfait -> conditionnel présent.

Usage: python3 scripts/build_si.py RAW_DIR   (same downloads as build_data.py)

Finds Tatoeba sentences with one si-clause whose verb is in the imparfait and a main-clause verb
in the conditionnel présent, and blanks both. Wrong options are the same verb and person in other
tenses (si-clause: conditionnel, présent; main clause: futur, imparfait).
"""
import collections
import random
import sys

from frtools import DATA, adjacent, load_lexique, load_tatoeba, split_parts, tokens, vowel_start, write_json

RAW = sys.argv[1]
CAP_PER_LEMMA = 45

LEMMAS_OF, FORMS, FREQ, INF = load_lexique(RAW)
PARTICIPLES = {f for l, tags in FORMS.items() for t, f in tags.items() if t == "par:pas"}
FORM_TAGS = collections.defaultdict(list)  # form -> [(lemma, tag)]
for lemma, tags in FORMS.items():
    for tag, form in tags.items():
        FORM_TAGS[form].append((lemma, tag))

SUBJ = {"je": "1s", "j'": "1s", "tu": "2s", "il": "3s", "elle": "3s", "on": "3s", "c'": "3s", "ça": "3s",
        "cela": "3s", "nous": "1p", "vous": "2p", "ils": "3p", "elles": "3p"}
CLITICS = {"ne", "n'", "me", "m'", "te", "t'", "se", "s'", "y", "en", "le", "la", "les", "l'", "lui", "leur",
           "nous", "vous"}
DETS = {"le", "la", "les", "l'", "un", "une", "des", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses",
        "notre", "nos", "votre", "vos", "leur", "leurs", "ce", "cet", "cette", "ces", "quelqu'un", "personne",
        "tout", "tous", "chacun"}
FULL = {"j'": "je", "n'": "ne", "m'": "me", "t'": "te", "s'": "se", "l'": "le", "c'": "ce"}
ELIDABLE = {"je", "ne", "me", "te", "se", "le", "ce"}
NEG = {"pas", "plus", "jamais", "déjà", "rien"}
# verbs that make "si" an indirect question ("je voudrais savoir si…")
QUESTION_VERBS = {"savoir", "demander", "dire", "voir", "vérifier", "ignorer", "regarder", "comprendre",
                  "deviner", "douter", "décider", "imaginer", "écouter", "sentir", "chercher", "examiner"}
PERSON_TEXT = {"1s": "je", "2s": "tu", "3s": "il/elle", "1p": "nous", "2p": "vous", "3p": "ils/elles"}


def tags_of(form, prefix):
    return [(l, t) for l, t in FORM_TAGS.get(form, []) if t.startswith(prefix)]


def join_elide(words):
    out = ""
    for i, w in enumerate(words):
        nxt = words[i + 1] if i + 1 < len(words) else ""
        if w in ELIDABLE and nxt and vowel_start(nxt):
            out += w[:-1] + "'"
        else:
            out += w + " "
    return out.strip()


def blank_for(text, toks, vi, lemma, person, tense):
    """Blank token vi (verb), absorbing a directly preceding elided word. Returns (start, end, dict)."""
    start = vi
    if vi > 0 and toks[vi - 1][0].endswith("'") and adjacent(text, toks[vi - 1], toks[vi]):
        start = vi - 1
    lead = [FULL.get(toks[start][0], toks[start][0])] if start < vi else []
    p = person
    form_imp = FORMS[lemma].get("ind:imp:" + p)
    form_cnd = FORMS[lemma].get("cnd:pre:" + p)
    form_fut = FORMS[lemma].get("ind:fut:" + p)
    form_pre = FORMS[lemma].get("ind:pre:" + p)
    if tense == "si":
        wrong = [form_cnd, form_pre]
    else:
        wrong = [form_fut, form_imp]
    if not all(wrong) or not form_imp or not form_cnd:
        return None
    s, e = toks[start][1], toks[vi][2]
    surface = text[s:e].replace("’", "'")
    opts = [join_elide(lead + [w]) for w in wrong]
    if surface[0].isupper():
        opts = [o[0].upper() + o[1:] for o in opts]
    if len({surface.lower(), *[o.lower() for o in opts]}) < 3:
        return None
    hint = " ".join(lead + ["[" + lemma + "]"])
    if lead and vowel_start(lemma):
        hint = lead[0][:-1] + "'[" + lemma + "]"
    if tense == "si":
        stem = "ét-" if lemma == "être" else (FORMS[lemma]["ind:imp:3s"][:-3] + "-" if "ind:imp:3s" in FORMS[lemma] else form_imp[:-len({"1s": "ais", "2s": "ais", "3s": "ait", "1p": "ions", "2p": "iez", "3p": "aient"}[p])] + "-")
        x = (f"After si (hypothesis), use the imparfait — never the conditionnel. "
             f"{lemma}: stem {stem} + -ais, -ais, -ait, -ions, -iez, -aient.")
        key = lemma + " (imparfait)"
    else:
        stem = form_cnd[:-len({"1s": "ais", "2s": "ais", "3s": "ait", "1p": "ions", "2p": "iez", "3p": "aient"}[p])] + "-"
        examples = ", ".join(join_elide([PERSON_TEXT[q].split('/')[0], FORMS[lemma]['cnd:pre:' + q]])
                             for q in ("1s", "3s", "3p") if "cnd:pre:" + q in FORMS[lemma])
        x = (f"The consequence of an imparfait si-clause takes the conditionnel présent: "
             f"future stem + imparfait endings. {lemma}: stem {stem} ({examples}).")
        key = lemma + " (conditionnel)"
    return s, e, dict(a=surface, o=opts, h=hint, x=x, t=tense, k=key)


def subject_before(toks, i):
    """Person of the subject pronoun directly before verb i (skipping clitics), if any."""
    k = i - 1
    while k >= 0 and toks[k][0] in CLITICS and toks[k][0] not in ("nous", "vous"):
        k -= 1
    if k >= 0 and toks[k][0] in SUBJ:
        return SUBJ[toks[k][0]]
    # nous / vous as subject followed by clitic nous / vous
    return None


def analyse(text):
    toks = tokens(text)
    n = len(toks)
    words = [t[0] for t in toks]
    si_pos = [i for i, w in enumerate(words) if w == "si" or (w == "s'" and i + 1 < n and words[i + 1] in ("il", "ils"))]
    if len(si_pos) != 1:
        return None
    i = si_pos[0]
    if i > 0 and words[i - 1] in ("comme", "que", "qu'"):
        return None
    for k in range(max(0, i - 3), i):
        if any(l in QUESTION_VERBS for l in LEMMAS_OF.get(words[k], ())):
            return None
    # subject
    j = i + 1
    if j >= n:
        return None
    person = None
    if words[j] in SUBJ:
        person = SUBJ[words[j]]
        j += 1
    elif words[j] in DETS or toks[j][0][0].isalpha() and text[toks[j][1]].isupper():
        k = j
        while k < min(n, j + 4) and not tags_of(words[k], "ind:imp"):
            k += 1
        j = k
    else:
        return None
    while j < n and words[j] in CLITICS:
        j += 1
    if j >= n:
        return None
    imps = tags_of(words[j], "ind:imp")
    if person:
        imps = [(l, t) for l, t in imps if t.endswith(person)]
    if not imps:
        return None
    lemma, tag = max(imps, key=lambda x: FREQ.get(x[0], 0))
    p_si = tag[-2:]
    if p_si in ("1s", "2s") and not person:
        return None
    # pluperfect: avait / était + participle
    k = j + 1
    while k < n and words[k] in NEG:
        k += 1
    if k < n and words[k] in PARTICIPLES and lemma in ("avoir", "être"):
        return None
    vi_si = j
    # main-clause conditionnel
    conds = []
    for m in range(n):
        if i <= m <= vi_si:
            continue
        c = tags_of(words[m], "cnd:pre")
        if not c:
            continue
        l2, t2 = max(c, key=lambda x: FREQ.get(x[0], 0))
        p2 = t2[-2:]
        if p2 in ("1s", "2s"):
            p2 = subject_before(toks, m)
            if p2 not in ("1s", "2s"):
                return None
        k = m + 1
        while k < n and words[k] in NEG:
            k += 1
        if k < n and words[k] in PARTICIPLES and l2 in ("avoir", "être"):
            return None  # conditionnel passé
        conds.append((m, l2, p2))
    if not conds or len(conds) > 2:
        return None
    blanks = []
    b = blank_for(text, toks, vi_si, lemma, p_si, "si")
    if not b:
        return None
    blanks.append(b)
    for m, l2, p2 in conds:
        b = blank_for(text, toks, m, l2, p2, "cond")
        if not b:
            return None
        blanks.append(b)
    return blanks


def main():
    random.seed(4)
    found = []
    for sid, text, user, en in load_tatoeba(RAW, 18, 120):
        if "si" not in text.lower() and "s'il" not in text.lower():
            continue
        r = analyse(text)
        if r:
            found.append((sid, text, user, en, r))
    print("candidates:", len(found))
    random.shuffle(found)
    count = collections.Counter()
    out = []
    for sid, text, user, en, blanks in found:
        lemmas = [b[2]["k"] for b in blanks]
        if any(count[l] >= CAP_PER_LEMMA for l in lemmas):
            continue
        count.update(lemmas)
        out.append(dict(id=sid, p=split_parts(text, blanks), en=en, src=dict(id=sid, by=user)))
    out.sort(key=lambda it: it["id"])
    write_json(DATA / "si.json", out)


if __name__ == "__main__":
    main()
