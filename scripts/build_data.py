#!/usr/bin/env python3
"""Build data/sentences.json for the imparfait / passé composé drill.

Inputs (download into one directory, see README):
  fra_sentences_detailed.tsv, fra-eng_links.tsv, eng_sentences.tsv,
  user_languages.csv            -- Tatoeba exports (CC BY 2.0 FR)
  Lexique383.tsv                -- Lexique 3.83 (CC BY-SA 4.0), verb forms

Usage: python3 scripts/build_data.py RAW_DIR [OUT_JSON]

The script finds verbs in the imparfait or passé composé, blanks them, and
generates the same verb in the other tense as the wrong option. It is
deliberately strict: anything it cannot convert cleanly is left unblanked,
and sentences with no clean blank are dropped.
"""
import collections
import json
import random
import re
import sys
from pathlib import Path

RAW = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "data" / "sentences.json"

TARGET_TOTAL = 2400
CAP_PER_VERB = 22       # per (lemma, tense) among single-blank sentences
CAP_PER_VERB_MIXED = 60

AVOIR = {"ai": "1s", "as": "2s", "a": "3s", "avons": "1p", "avez": "2p", "ont": "3p"}
ETRE = {"suis": "1s", "es": "2s", "est": "3s", "sommes": "1p", "êtes": "2p", "sont": "3p"}
AVOIR_BY_P = {v: k for k, v in AVOIR.items()}
ETRE_BY_P = {v: k for k, v in ETRE.items()}

ETRE_ALWAYS = {"aller", "venir", "arriver", "partir", "rester", "tomber", "naître", "mourir",
               "devenir", "revenir", "entrer", "repartir", "parvenir", "intervenir", "décéder",
               "retomber", "survenir"}
ETRE_MIXED = {"monter", "descendre", "sortir", "rentrer", "retourner", "passer", "remonter",
              "redescendre", "ressortir"}
ASPIRATED_H = {"haïr", "heurter", "hurler", "hausser", "hanter", "harceler", "hâter", "hocher",
               "hisser", "happer", "hennir", "hacher", "haleter", "hasarder", "héler", "huer"}

CLITICS = {"ne", "n'", "me", "m'", "te", "t'", "se", "s'", "y", "en", "lui", "leur",
           "nous", "vous", "le", "la", "les", "l'"}
OBJ_BLOCK = {"le", "la", "les", "l'"}
FULL = {"n'": "ne", "m'": "me", "t'": "te", "s'": "se", "j'": "je", "c'": "ce"}
ELIDABLE = {"je", "ne", "me", "te", "se"}
NEG = {"pas", "plus", "jamais", "rien", "guère"}
# words allowed between auxiliary and participle in an existing passé composé
PC_MID = NEG | {"déjà", "toujours", "souvent", "rarement", "vraiment", "bien", "mal", "beaucoup",
                "trop", "tout", "presque", "encore", "enfin", "aussi", "peu", "probablement",
                "sûrement", "certainement", "simplement", "juste", "longtemps", "vite", "même",
                "donc", "tous", "finalement", "complètement", "toutes"}
# adverbs that move between auxiliary and participle when imparfait -> passé composé
MOVE_ADV = {"déjà", "toujours", "souvent", "rarement", "vraiment"}
MOVE_ADV_FULLVERB = {"bien", "mal", "beaucoup", "trop", "tout"}  # only clause-final, not être/avoir
DETERMINERS = {"le", "la", "les", "l'", "un", "une", "des", "du", "mon", "ma", "mes", "ton", "ta",
               "tes", "son", "sa", "ses", "notre", "nos", "votre", "vos", "leur", "leurs", "ce",
               "cet", "cette", "ces", "deux", "trois", "quelques", "plusieurs"}
AGREE = {"je": "", "tu": "", "il": "", "on": "", "tom": "", "vous": "", "elle": "e", "marie": "e",
         "mary": "e", "ils": "s", "nous": "s", "elles": "es"}

IMP_END = {"1s": "ais", "2s": "ais", "3s": "ait", "1p": "ions", "2p": "iez", "3p": "aient"}
# keep the drill pleasant: skip sentences about violence, sex, etc.
UNPLEASANT = re.compile(r"viol|prostitu|suicid|tué|tuer|tuai|assassin|meurtr|sexe|sexuel|nazi|merde|putain|"
                        r"baisé|baisai|encul|salop|pédophil|cadavre|poignard|étrangl|tortur", re.I)
TOKEN = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿœŒ]+(?:-[A-Za-zÀ-ÖØ-öø-ÿœŒ]+)*['’]?")
VOWELS = "aeiouyàâäéèêëîïôöùûüœ"


def load_lexique():
    imp = collections.defaultdict(dict)      # form -> lemma -> set(persons)
    imp_by = collections.defaultdict(dict)   # lemma -> person -> form
    pp = collections.defaultdict(set)        # form -> lemmas
    pp_base = {}                             # lemma -> masc sing participle
    freq = {}
    with open(RAW / "Lexique383.tsv", encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        for line in f:
            r = line.rstrip("\n").split("\t")
            if r[ix["cgram"]] not in ("VER", "AUX"):
                continue
            form, lemma, info = r[ix["ortho"]], r[ix["lemme"]], r[ix["infover"]]
            if " " in form or "-" in form:
                continue
            freq[lemma] = max(freq.get(lemma, 0.0), float(r[ix["freqlemfilms2"]] or 0))
            for p in re.findall(r"ind:imp:([123][sp])", info):
                if not form.endswith(IMP_END[p]):
                    continue  # Lexique has some mis-tagged rows
                imp[form].setdefault(lemma, set()).add(p)
                imp_by[lemma][p] = form
            if "par:pas" in info:
                pp[form].add(lemma)
                g, n = r[ix["genre"]], r[ix["nombre"]]
                rank = (g == "f", n == "p", len(form))
                if lemma not in pp_base or rank < pp_base[lemma][0]:
                    pp_base[lemma] = (rank, form)
    pp_base = {k: v[1] for k, v in pp_base.items()}
    return imp, imp_by, pp, pp_base, freq


IMP, IMP_BY, PP, PP_BASE, FREQ = load_lexique()


def best(lemmas):
    return max(lemmas, key=lambda l: FREQ.get(l, 0))


def agree(base, suffix):
    out = base
    if "e" in suffix:
        out += "e"
    if "s" in suffix and not out.endswith(("s", "x")):
        out += "s"
    return out


def join_elide(words, lemma):
    """Join words, eliding je/ne/me/te/se/ce before a vowel sound."""
    out = ""
    for i, w in enumerate(words):
        nxt = words[i + 1] if i + 1 < len(words) else ""
        vowel = nxt[:1].lower() in VOWELS or (nxt[:1].lower() == "h" and lemma not in ASPIRATED_H)
        if w in ELIDABLE and nxt and vowel:
            out += w[:-1] + "'"
        elif w == "ce" and nxt[:1].lower() in "eé":
            out += "c'"
        else:
            out += w + " "
    return out.strip()


def analyse(text):
    """Return list of blanks: dict(start, end, tense, lemma, other, hint)."""
    toks = [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(text)]
    low = [t[0].lower().replace("’", "'") for t in toks]
    n = len(toks)

    def adjacent(a, b):  # token a directly followed by token b
        gap = text[toks[a][2]:toks[b][1]]
        return gap in ("", " ", " ", " ")

    def clause_end(j):  # nothing but punctuation follows token j before the next token
        if j + 1 >= n:
            return True
        return bool(re.search(r"[,.;:!?…]", text[toks[j][2]:toks[j + 1][1]]))

    blanks = []
    used_until = -1
    for i in range(n):
        if i <= used_until:
            continue
        w = low[i]
        tense = lemma = person = aux = None
        mids = []
        end = i
        if w in AVOIR or w in ETRE:
            j = i + 1
            while j < n and len(mids) < 3 and low[j] in PC_MID and adjacent(j - 1, j) and low[j] not in PP:
                mids.append(low[j])
                j += 1
            if j < n and low[j] in PP and adjacent(j - 1, j):
                lemma = best(PP[low[j]])
                aux = "avoir" if w in AVOIR else "être"
                person = (AVOIR if aux == "avoir" else ETRE)[w]
                tense, end = "pc", j
        if tense is None and w in IMP:
            lemma = best(IMP[w])
            persons = IMP[w][lemma]
            # plus-que-parfait or similar: avait/était + participle
            j = i + 1
            k = 0
            while j < n and k < 3 and low[j] in PC_MID and low[j] not in PP:
                j += 1
                k += 1
            if j < n and low[j] in PP and adjacent(i, i + 1):
                if lemma == "avoir":
                    used_until = j
                    continue
                if lemma == "être":
                    used_until = j
                    continue  # était allé / était fatigué: ambiguous, leave as context
            tense = "imp"
        if tense is None:
            continue

        # ---- scan left over clitics and subject
        k = i - 1
        clitics = []
        while k >= 0 and low[k] in CLITICS and adjacent(k, k + 1):
            clitics.insert(0, low[k])
            k -= 1
        start = k + 1
        subj = low[k] if k >= 0 and adjacent(k, k + 1) else None
        subj_in_span = False
        if tense == "imp":
            ps = IMP[low[i]][lemma]
            if ps <= {"1s", "2s"}:
                person = "1s" if subj in ("je", "j'") else "2s" if subj == "tu" else None
            elif len(ps) == 1:
                person = next(iter(ps))
            if person is None:
                continue
        # nous/vous: subject or object?
        if person in ("1p", "2p"):
            pro = "nous" if person == "1p" else "vous"
            if clitics and clitics[0] == pro:
                clitics.pop(0)
                start += 1
                subj = pro
            elif tense == "imp":
                continue  # -ions/-iez without a clear subject: noun or subjunctive risk
            if tense == "imp" and any(x in ("que", "qu'") for x in low[:i]):
                continue  # could be subjunctive
        if any(c in OBJ_BLOCK for c in clitics):
            continue  # direct-object pronoun: participle agreement unknown
        if subj in ("je", "j'"):
            subj_in_span, start = True, k
            lead = ["je"]
        elif lemma == "être" and subj in ("c'", "ce", "ça") and not [c for c in clitics if c not in ("ne", "n'")]:
            subj_in_span, start = True, k
            lead = ["ce"]
        else:
            lead = []
            if subj and subj.endswith("'"):
                continue  # qu'a, l'on ... : elision we do not model
        if start > 0 and not subj_in_span and low[start - 1].endswith("'") and adjacent(start - 1, start):
            continue
        cl = [FULL.get(c, c) for c in clitics]
        reflexive = "se" in cl or (subj in ("je", "j'") and "me" in cl) or (subj == "tu" and "te" in cl) \
            or (subj in ("nous", "vous") and subj in cl)
        if not reflexive and ("nous" in cl or "vous" in cl):
            continue  # object nous/vous: participle agreement unknown
        if tense == "imp" and "ne" in cl and i + 1 < n and low[i + 1] not in NEG \
                and any(x in NEG for x in low[i + 2:i + 4]):
            continue  # ne ... <adverb> pas: word order differs between the tenses
        if tense == "pc" and aux == "être" and not (reflexive or lemma in ETRE_ALWAYS or lemma in ETRE_MIXED):
            continue  # passive or adjective, not a passé composé

        # ---- generate the other tense
        if tense == "pc":
            form = IMP_BY.get(lemma, {}).get(person)
            if not form:
                continue
            if lead == ["ce"]:
                other_words = ["ce"] + cl + [form] + mids
            else:
                other_words = lead + cl + [form] + mids
            hint_words = lead + cl + ["[" + lemma + "]"] + mids
        else:
            base = PP_BASE.get(lemma)
            if not base:
                continue
            # trailing negation / adverbs that would sit inside the passé composé
            j = i + 1
            has_ne = "ne" in cl
            while j < n and adjacent(j - 1, j) and len(mids) < 2:
                x = low[j]
                if (x in NEG and (has_ne or x == "pas")) or x in MOVE_ADV or \
                        (x in MOVE_ADV_FULLVERB and lemma not in ("être", "avoir") and clause_end(j)):
                    mids.append(x)
                    j += 1
                else:
                    break
            end = j - 1
            nxt = low[end + 1] if end + 1 < n and not clause_end(end) else None
            if reflexive or lemma in ETRE_ALWAYS:
                use_etre = True
            elif lemma in ETRE_MIXED:
                use_etre = nxt not in DETERMINERS
            else:
                use_etre = False
            if use_etre:
                if subj and subj.replace("j'", "je") in AGREE:
                    suffix = AGREE[subj.replace("j'", "je")]
                else:
                    continue  # unknown gender/number: cannot agree the participle
                if reflexive and nxt in DETERMINERS:
                    suffix = ""
                part = agree(base, suffix)
                auxw = ETRE_BY_P[person]
            else:
                part = base
                auxw = AVOIR_BY_P[person]
            if lead == ["ce"]:
                other_words = ["ça"] + cl + [auxw] + mids + [part]
            else:
                other_words = lead + cl + [auxw] + mids + [part]
            hint_words = lead + cl + ["[" + lemma + "]"] + mids
        if lead == ["ce"] and tense == "pc" and subj != "ça":
            continue
        hint = " ".join(hint_words)
        if lemma[0] in VOWELS or (lemma[0] == "h" and lemma not in ASPIRATED_H):
            hint = re.sub(r"\b([mts])e \[", r"\1'[", hint)
        other = join_elide(other_words, lemma)
        s, e = toks[start][1], toks[end][2]
        if text[s].isupper():
            other = other[0].upper() + other[1:]
        blanks.append({"s": s, "e": e, "t": tense, "l": lemma, "o": other, "h": hint})
        used_until = end
    return blanks


def main():
    random.seed(7)
    natives = set()
    with open(RAW / "user_languages.csv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) >= 3 and r[0] == "fra" and r[1] == "5":
                natives.add(r[2])
    links = collections.defaultdict(list)
    with open(RAW / "fra-eng_links.tsv", encoding="utf-8") as f:
        for line in f:
            a, b = line.split()
            links[int(a)].append(int(b))

    cands = []
    seen = set()
    with open(RAW / "fra_sentences_detailed.tsv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if len(r) < 4:
                continue
            sid, text, user = int(r[0]), r[2].strip(), r[3]
            if user not in natives or sid not in links:
                continue
            if not (15 <= len(text) <= 110) or any(ord(c) > 0xFFFF for c in text):
                continue
            if re.search(r"[0-9\"«»()\[\]]|\b[Ss]i\b|\b[Ss]['’]ils?\b|\n", text) or UNPLEASANT.search(text):
                continue
            words = TOKEN.findall(text)
            if not (4 <= len(words) <= 17):
                continue
            key = re.sub(r"\W+", " ", text.lower()).strip()
            if key in seen:
                continue
            blanks = analyse(text)
            if not blanks or len(blanks) > 3:
                continue
            seen.add(key)
            cands.append((sid, text, user, blanks))
    print("candidates:", len(cands))

    need = {e for c in cands for e in links[c[0]]}
    eng = {}
    with open(RAW / "eng_sentences.tsv", encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            if int(r[0]) in need:
                eng[int(r[0])] = r[2]

    random.shuffle(cands)
    mixed, imp_only, pc_only = [], [], []
    count = collections.Counter()
    for c in cands:
        tenses = {b["t"] for b in c[3]}
        is_mixed = len(tenses) == 2
        cap = CAP_PER_VERB_MIXED if is_mixed else CAP_PER_VERB
        keys = [(b["l"], b["t"], is_mixed) for b in c[3]]
        if any(count[k] >= cap for k in keys):
            continue
        for k in keys:
            count[k] += 1
        (mixed if is_mixed else imp_only if tenses == {"imp"} else pc_only).append(c)
    print("mixed", len(mixed), "imp", len(imp_only), "pc", len(pc_only))
    mixed = mixed[: TARGET_TOTAL // 3]
    half = min((TARGET_TOTAL - len(mixed)) // 2, len(imp_only), len(pc_only))
    chosen = mixed + imp_only[:half] + pc_only[:half]
    chosen.sort(key=lambda c: c[0])

    out = []
    for sid, text, user, blanks in chosen:
        trs = sorted({eng[e] for e in links[sid] if e in eng}, key=len)[:2]
        if not trs:
            continue
        parts, pos = [], 0
        for b in blanks:
            if b["s"] > pos:
                parts.append(text[pos:b["s"]])
            parts.append({"a": text[b["s"]:b["e"]].replace("’", "'"), "o": b["o"],
                          "t": "i" if b["t"] == "imp" else "p", "h": b["h"]})
            pos = b["e"]
        if pos < len(text):
            parts.append(text[pos:])
        out.append({"id": sid, "by": user, "en": trs, "p": parts})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", len(out), "sentences to", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
