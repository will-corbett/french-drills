#!/usr/bin/env python3
"""Build data/prepositions.json: which preposition (à or de) follows a verb or expression.

Usage: python3 scripts/build_prepositions.py RAW_DIR   (same downloads as build_data.py)

Each entry below is a construction with the preposition it takes. The script finds Tatoeba
sentences where any form of the verb (any tense) is directly followed by that preposition, and
blanks the preposition. Sentences with the other preposition are never used for a single-
preposition entry, so the answer always matches the rule shown in the explanation.
"""
import collections
import random
import sys

from frtools import (DATA, adjacent, load_lexique, load_tatoeba, split_parts, tokens,
                     vowel_start, write_json)

RAW = sys.argv[1]
CAP = 14

# kind: verb | avoir | etre | faire | adj
# comp: "inf" = the preposition must be followed by an infinitive; "any" = any complement
# prep: "à", "de", or "both" (then x is a dict per preposition)
E = []


def v(lemma, prep, comp, x, refl=False, key=None):
    E.append(dict(kind="verb", lemma=lemma, prep=prep, comp=comp, x=x, refl=refl,
                  key=key or (("s'" if lemma[0] in "aeiouéèêh" else "se ") if refl else "") + lemma + " " + (prep if prep != "both" else "à/de")))


def expr(kind, words, prep, comp, x, key):
    E.append(dict(kind=kind, words=words, prep=prep, comp=comp, x=x, key=key))


# ---- verb + à
v("aider", "à", "inf", "aider (qqn) à + infinitive: to help (someone) do something.")
v("apprendre", "à", "inf", "apprendre à + infinitive: to learn to do something (apprendre à qqn à faire: to teach someone to do).")
v("arriver", "à", "inf", "arriver à + infinitive: to manage to do something.")
v("chercher", "à", "inf", "chercher à + infinitive: to try / seek to do something (compare essayer de).")
v("commencer", "à", "inf", "commencer à + infinitive: to start doing (commencer par = to start by).")
v("consister", "à", "inf", "consister à + infinitive: to consist in doing.")
v("encourager", "à", "inf", "encourager qqn à + infinitive: to encourage someone to do.")
v("habituer", "à", "any", "s'habituer à + infinitive or noun: to get used to.", refl=True)
v("hésiter", "à", "inf", "hésiter à + infinitive: to hesitate to do.")
v("inviter", "à", "inf", "inviter qqn à + infinitive: to invite someone to do.")
v("mettre", "à", "inf", "se mettre à + infinitive: to start doing (often suddenly).", refl=True)
v("parvenir", "à", "inf", "parvenir à + infinitive: to manage to (more formal than arriver à).")
v("préparer", "à", "inf", "se préparer à + infinitive: to get ready to do.", refl=True)
v("renoncer", "à", "any", "renoncer à + infinitive or noun: to give up (on).")
v("réussir", "à", "inf", "réussir à + infinitive: to succeed in doing.")
v("servir", "à", "inf", "servir à + infinitive: to be used for doing (servir de = to serve as).")
v("tenir", "à", "inf", "tenir à + infinitive: to be keen on / insist on doing.")
v("attendre", "à", "any", "s'attendre à + infinitive or noun: to expect.", refl=True)
v("intéresser", "à", "any", "s'intéresser à + noun or infinitive: to be interested in.", refl=True)
v("obliger", "à", "inf", "obliger qqn à + infinitive: to force someone to do (but: être obligé de).")
v("forcer", "à", "inf", "forcer qqn à + infinitive: to force someone to do (but: être forcé de).")
v("décider", "à", "inf", "se décider à + infinitive: to make up one's mind to do (décider de = to decide to).", refl=True)
v("amuser", "à", "inf", "s'amuser à + infinitive: to have fun doing.", refl=True)
v("réfléchir", "à", "any", "réfléchir à + noun: to think about, consider.")
v("ressembler", "à", "any", "ressembler à + noun: to look like / resemble.")
v("participer", "à", "any", "participer à + noun: to take part in.")
v("assister", "à", "any", "assister à + noun: to attend (a meeting, a show). Not 'to assist'.")
v("obéir", "à", "any", "obéir à + noun: to obey (indirect object in French).")
v("plaire", "à", "any", "plaire à qqn: to please someone (Ça me plaît = I like it).")
v("répondre", "à", "any", "répondre à + noun: to answer, reply to.")
v("téléphoner", "à", "any", "téléphoner à qqn: to phone someone.")
v("résister", "à", "any", "résister à + noun: to resist.")
v("appartenir", "à", "any", "appartenir à + noun: to belong to.")
v("nuire", "à", "any", "nuire à + noun: to harm, be harmful to.")
v("adresser", "à", "any", "s'adresser à qqn: to speak to / contact someone.", refl=True)
v("songer", "à", "any", "songer à + infinitive or noun: to think of, consider (literary-ish).")
v("pousser", "à", "inf", "pousser qqn à + infinitive: to push / drive someone to do.")
v("autoriser", "à", "inf", "autoriser qqn à + infinitive: to allow someone to do (compare permettre à qqn de).")

# ---- verb + de
v("accepter", "de", "inf", "accepter de + infinitive: to agree to do.")
v("arrêter", "de", "inf", "arrêter de + infinitive: to stop doing.")
v("cesser", "de", "inf", "cesser de + infinitive: to stop / cease doing.")
v("choisir", "de", "inf", "choisir de + infinitive: to choose to do.")
v("conseiller", "de", "inf", "conseiller à qqn de + infinitive: to advise someone to do.")
v("décider", "de", "inf", "décider de + infinitive: to decide to do (se décider à = to make up one's mind to).")
v("demander", "de", "inf", "demander à qqn de + infinitive: to ask someone to do.")
v("dire", "de", "inf", "dire à qqn de + infinitive: to tell someone to do.")
v("empêcher", "de", "inf", "empêcher (qqn) de + infinitive: to prevent (someone) from doing; s'empêcher de = to stop oneself.")
v("envisager", "de", "inf", "envisager de + infinitive: to consider / plan doing.")
v("essayer", "de", "inf", "essayer de + infinitive: to try to do.")
v("éviter", "de", "inf", "éviter de + infinitive: to avoid doing.")
v("finir", "de", "inf", "finir de + infinitive: to finish doing (finir par = to end up doing).")
v("interdire", "de", "inf", "interdire à qqn de + infinitive: to forbid someone to do.")
v("menacer", "de", "inf", "menacer de + infinitive: to threaten to do.")
v("mériter", "de", "inf", "mériter de + infinitive: to deserve to.")
v("oublier", "de", "inf", "oublier de + infinitive: to forget to do.")
v("permettre", "de", "inf", "permettre à qqn de + infinitive: to allow someone to do.")
v("persuader", "de", "inf", "persuader qqn de + infinitive: to persuade someone to do.")
v("promettre", "de", "inf", "promettre (à qqn) de + infinitive: to promise to do.")
v("proposer", "de", "inf", "proposer de + infinitive: to suggest / offer to do.")
v("refuser", "de", "inf", "refuser de + infinitive: to refuse to do.")
v("regretter", "de", "inf", "regretter de + infinitive: to regret doing.")
v("rêver", "de", "any", "rêver de + infinitive or noun: to dream of / about.")
v("risquer", "de", "inf", "risquer de + infinitive: to be likely to / at risk of (Ça risque de pleuvoir).")
v("tenter", "de", "inf", "tenter de + infinitive: to attempt to do.")
v("dépêcher", "de", "inf", "se dépêcher de + infinitive: to hurry to do.", refl=True)
v("occuper", "de", "any", "s'occuper de + noun or infinitive: to take care of, deal with.", refl=True)
v("souvenir", "de", "any", "se souvenir de + noun or infinitive: to remember (se rappeler takes no preposition).", refl=True)
v("moquer", "de", "any", "se moquer de + noun: to make fun of; not to care about.", refl=True)
v("plaindre", "de", "any", "se plaindre de + noun or infinitive: to complain about.", refl=True)
v("méfier", "de", "any", "se méfier de + noun: to be wary of, distrust.", refl=True)
v("servir", "de", "any", "se servir de + noun: to use.", refl=True, key="se servir de")
v("agir", "de", "any", "il s'agit de + noun or infinitive: it is about / it's a matter of.", refl=True)
v("profiter", "de", "any", "profiter de + noun: to take advantage of, make the most of.")
v("dépendre", "de", "any", "dépendre de + noun: to depend on.")
v("venir", "de", "inf", "venir de + infinitive: to have just done (venir + infinitive without de = to come to do).")
v("jurer", "de", "inf", "jurer de + infinitive: to swear to do.")
v("excuser", "de", "any", "s'excuser de + noun or infinitive: to apologise for.", refl=True)
v("contenter", "de", "any", "se contenter de + noun or infinitive: to make do with / just do.", refl=True)
v("changer", "de", "any", "changer de + noun without article: to change (changer d'avis, de train, de vêtements).")
v("approcher", "de", "any", "s'approcher de + noun: to come closer to.", refl=True)
v("charger", "de", "any", "(se) charger de: to be in charge of, take care of.")
v("remercier", "de", "any", "remercier qqn de + noun or infinitive: to thank someone for.")
v("féliciter", "de", "any", "féliciter qqn de + noun or infinitive: to congratulate someone on.")
v("douter", "de", "any", "douter de + noun: to doubt (se douter de = to suspect).")
v("rendre", "de", "any", "se rendre compte de: to realise.", refl=True, key="se rendre compte de")

# ---- verbs whose meaning changes with the preposition
v("penser", "both", "any", {"à": "penser à: to think about / of (someone, something, doing).",
                            "de": "penser de: to have an opinion about (Qu'est-ce que tu penses de… ?)."})
v("manquer", "both", "any", {"à": "manquer à qqn: to be missed by someone (Tu me manques = I miss you).",
                             "de": "manquer de: to lack (Il manque de patience)."})

# ---- avoir / être / faire + noun or adjective
for words, prep, comp, x, key in [
    (["besoin"], "de", "any", "avoir besoin de: to need.", "avoir besoin de"),
    (["envie"], "de", "any", "avoir envie de: to want / feel like.", "avoir envie de"),
    (["peur"], "de", "any", "avoir peur de: to be afraid of.", "avoir peur de"),
    (["honte"], "de", "any", "avoir honte de: to be ashamed of.", "avoir honte de"),
    (["l'", "intention"], "de", "inf", "avoir l'intention de: to intend to.", "avoir l'intention de"),
    (["le", "droit"], "de", "inf", "avoir le droit de: to be allowed to.", "avoir le droit de"),
    (["l'", "habitude"], "de", "any", "avoir l'habitude de: to be used to / in the habit of.", "avoir l'habitude de"),
    (["le", "temps"], "de", "inf", "avoir le temps de: to have time to.", "avoir le temps de"),
    (["hâte"], "de", "any", "avoir hâte de: to look forward to / can't wait to.", "avoir hâte de"),
    (["raison"], "de", "inf", "avoir raison de + infinitive: to be right to.", "avoir raison de"),
    (["tort"], "de", "inf", "avoir tort de + infinitive: to be wrong to.", "avoir tort de"),
    (["du", "mal"], "à", "inf", "avoir du mal à: to have trouble / difficulty doing.", "avoir du mal à"),
    (["tendance"], "à", "inf", "avoir tendance à: to tend to.", "avoir tendance à"),
    (["l'", "air"], "de", "any", "avoir l'air de: to seem / look like.", "avoir l'air de"),
    (["la", "chance"], "de", "inf", "avoir la chance de: to be lucky enough to.", "avoir la chance de"),
]:
    expr("avoir", words, prep, comp, x, key)
expr("etre", ["en", "train"], "de", "inf", "être en train de: to be in the middle of doing.", "être en train de")
expr("faire", ["semblant"], "de", "inf", "faire semblant de: to pretend to.", "faire semblant de")
expr("faire", ["attention"], "à", "any", "faire attention à: to pay attention to / be careful of.", "faire attention à")

for stems, prep, comp, x, key in [
    ("prêt", "à", "inf", "être prêt à + infinitive: to be ready to.", "prêt à"),
    ("obligé", "de", "inf", "être obligé de + infinitive: to have to / be forced to (but: obliger qqn à).", "obligé de"),
    ("forcé", "de", "inf", "être forcé de + infinitive: to be forced to (but: forcer qqn à).", "forcé de"),
    ("capable", "de", "any", "être capable de: to be capable of.", "capable de"),
    ("incapable", "de", "any", "être incapable de: to be incapable of.", "incapable de"),
    ("sûr", "de", "any", "être sûr de: to be sure of.", "sûr de"),
    ("certain", "de", "any", "être certain de: to be certain of.", "certain de"),
    ("content", "de", "any", "être content de: to be pleased with / to.", "content de"),
    ("fier", "de", "any", "être fier de: to be proud of.", "fier de"),
    ("heureux", "de", "inf", "être heureux de + infinitive: to be happy to.", "heureux de"),
    ("désolé", "de", "any", "être désolé de: to be sorry for / to.", "désolé de"),
    ("déterminé", "à", "inf", "être déterminé à: to be determined to.", "déterminé à"),
    ("décidé", "à", "inf", "être décidé à: to be determined to (but: décider de).", "décidé à"),
    ("habitué", "à", "any", "être habitué à: to be used to.", "habitué à"),
    ("fatigué", "de", "any", "être fatigué de: to be tired of.", "fatigué de"),
    ("responsable", "de", "any", "être responsable de: to be responsible for.", "responsable de"),
    ("conscient", "de", "any", "être conscient de: to be aware of.", "conscient de"),
    ("le premier", "à", "inf", "être le premier / la dernière / le seul à + infinitive: to be the first / last / only one to.", "le premier à"),
]:
    expr("adj", stems, prep, comp, x, key)

IMPERSONAL = {"facile", "difficile", "impossible", "dur", "simple", "compliqué", "agréable", "pénible", "amusant"}
IMP_X = {"de": "Il est / C'est + adjective + de + infinitive when the infinitive's object comes after it "
               "(Il est difficile de comprendre ce texte).",
         "à": "Noun or ce + être + adjective + à + infinitive when the subject is what the infinitive acts on "
              "(Ce texte est difficile à comprendre; C'est facile à dire)."}

ADJ_FORMS = {
    "prêt": ["prêt", "prête", "prêts", "prêtes"], "certain": ["certain", "certaine"], "le premier": ["premier", "première", "premiers", "premières",
                                                                   "dernier", "dernière", "derniers", "dernières",
                                                                   "seul", "seule", "seuls", "seules"],
}


def adj_forms(stem):
    if stem in ADJ_FORMS:
        return ADJ_FORMS[stem]
    if stem.endswith("eux"):
        return [stem, stem[:-1] + "se", stem[:-1] + "ses"]
    if stem.endswith("e"):
        return [stem, stem + "s"]
    if stem == "fier":
        return ["fier", "fière", "fiers", "fières"]
    return [stem, stem + "e", stem + "s", stem + "es"]


LEMMAS_OF, FORMS, FREQ, INF = load_lexique(RAW)
AVOIR = {f for f, ls in LEMMAS_OF.items() if "avoir" in ls}
ETRE = {f for f, ls in LEMMAS_OF.items() if "être" in ls} - {"suis", "suivi"}
FAIRE = {f for f, ls in LEMMAS_OF.items() if "faire" in ls}
FAIRE.add("fait")
AVOIR.add("eu")
ETRE.add("été")

PREPS = {"à": "à", "au": "à", "aux": "à", "de": "de", "d'": "de", "du": "de", "des": "de"}
OTHER = {"à": "de", "au": "du", "aux": "des", "de": "à", "d'": "à", "du": "au", "des": "aux"}
DETS = {"le", "la", "les", "l'", "un", "une", "des", "du", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa",
        "ses", "notre", "nos", "votre", "vos", "leur", "leurs", "ce", "cet", "cette", "ces", "au", "aux", "de",
        "d'", "quel", "quelle", "chaque", "aucun", "aucune"}
REFL = {"me", "m'", "te", "t'", "se", "s'", "nous", "vous"}
SKIP_AFTER = {"ne", "n'", "pas", "plus", "jamais", "rien", "le", "la", "les", "l'", "lui", "leur", "me", "m'",
              "te", "t'", "se", "s'", "nous", "vous", "y", "en", "tout", "bien", "mieux", "encore", "vraiment", "trop"}
BETWEEN_AVOIR = {"pas", "plus", "jamais", "vraiment", "toujours", "encore", "très", "si", "tellement", "bien",
                 "un", "peu", "souvent", "parfois", "aussi", "déjà", "absolument", "grand", "trop", "rarement",
                 "beaucoup", "eu", "été", "même"}

VERB_ENTRIES = collections.defaultdict(list)
for e in E:
    if e["kind"] == "verb":
        VERB_ENTRIES[e["lemma"]].append(e)
ADJ = {}
for e in E:
    if e["kind"] == "adj":
        for f in adj_forms(e["words"]):
            ADJ[f] = e
for f in IMPERSONAL:
    for g in adj_forms(f):
        ADJ.setdefault(g, dict(kind="impers", prep="both", comp="inf", x=IMP_X, key="il est facile de / c'est facile à"))


# set phrases after à / de that are not governed by the verb
NOT_GOVERNED = {("haute",), ("nouveau",), ("temps",), ("l'", "heure"), ("pied",), ("cheval",), ("la", "fois"),
                ("peine",), ("moitié",), ("jamais",), ("part",), ("côté",), ("travers",), ("cause",), ("propos",),
                ("peu", "près"), ("la", "main"), ("tout",), ("plus",), ("toute", "façon"), ("bonne", "heure"),
                ("rien",), ("la", "même"), ("même",), ("mon", "avis"), ("ton", "avis"), ("son", "avis"),
                ("votre", "avis"), ("l'", "avance"), ("présent",), ("bientôt",), ("demain",), ("la", "fin"),
                ("plein",), ("partir",), ("l'", "époque"), ("ce", "moment"), ("cette", "époque"), ("la", "place"),
                ("l'", "étranger"), ("la", "maison"), ("l'", "école"), ("midi",), ("minuit",), ("la", "fin")}


def complement_ok(toks, j, comp):
    """toks[j] is the preposition; check what follows."""
    k = j + 1
    for ph in NOT_GOVERNED:
        if tuple(t[0] for t in toks[k:k + len(ph)]) == ph:
            return False
    if toks[j][0] in ("du",) and k < len(toks) and toks[k][0] == "tout":
        return False
    if comp == "inf":
        while k < len(toks) and toks[k][0] in SKIP_AFTER:
            k += 1
        return k < len(toks) and toks[k][0] in INF
    return k < len(toks)


def find(text):
    toks = tokens(text)
    n = len(toks)
    for i in range(n - 1):
        w = toks[i][0]
        nxt = toks[i + 1][0]
        if nxt not in PREPS or not adjacent(text, toks[i], toks[i + 1]):
            continue
        actual = PREPS[nxt]
        cand = []
        # verbs
        for lemma in LEMMAS_OF.get(w, ()):
            for e in VERB_ENTRIES.get(lemma, ()):
                if i > 0 and toks[i - 1][0] in DETS:
                    continue
                window = [t[0] for t in toks[max(0, i - 4):i]]
                is_refl = any(t in REFL for t in window)
                if e["refl"] and not is_refl:
                    continue
                if e["key"] in ("se rendre compte de",):
                    continue
                cand.append(e)
        # se rendre compte de
        if w == "compte" and i > 0 and toks[i - 1][0] in LEMMAS_OF and "rendre" in LEMMAS_OF.get(toks[i - 1][0], ()):
            cand += [e for e in E if e.get("key") == "se rendre compte de"]
        # expressions with avoir / être / faire
        for e in E:
            if e["kind"] not in ("avoir", "etre", "faire"):
                continue
            ws = e["words"]
            if i - len(ws) + 1 < 1 or [t[0] for t in toks[i - len(ws) + 1:i + 1]] != ws:
                continue
            k = i - len(ws)
            while k >= 0 and toks[k][0] in BETWEEN_AVOIR and toks[k][0] not in ("eu", "été"):
                k -= 1
            aux = {"avoir": AVOIR, "etre": ETRE, "faire": FAIRE}[e["kind"]]
            if k >= 0 and toks[k][0] in aux:
                cand.append(e)
        # adjectives
        if w in ADJ:
            cand.append(ADJ[w])
        for e in cand:
            if e["prep"] != "both" and e["prep"] != actual:
                continue
            if not complement_ok(toks, i + 1, e["comp"]):
                continue
            if nxt == "des" and e["comp"] == "inf":
                continue
            x = e["x"][actual] if isinstance(e["x"], dict) else e["x"]
            key = e["key"] if e["prep"] != "both" else e["key"]
            if e["prep"] == "both" and e["kind"] == "verb":
                key = e["lemma"] + " " + actual
            other = OTHER[nxt]
            if nxt == "à" and i + 2 < n and vowel_start(toks[i + 2][0]):
                other = "d'"
            if nxt == "d'":
                other = "à"
            s, en = toks[i + 1][1], toks[i + 1][2]
            surface = text[s:en].replace("’", "'")
            if surface[0].isupper():
                other = other.capitalize()
            return s, en, dict(a=surface, o=[other], x=x, t="a" if actual == "à" else "d", k=key)
    return None


def main():
    random.seed(5)
    found = []
    for sid, text, user, en in load_tatoeba(RAW, 12, 110):
        r = find(text)
        if r:
            found.append((sid, text, user, en, r))
    print("candidates:", len(found))
    random.shuffle(found)
    count = collections.Counter()
    out = []
    for sid, text, user, en, (s, e, b) in found:
        if count[b["k"]] >= CAP:
            continue
        count[b["k"]] += 1
        out.append(dict(id=sid, p=split_parts(text, [(s, e, b)]), en=en, src=dict(id=sid, by=user)))
    out.sort(key=lambda it: it["id"])
    print("entries used:", len(count), "of", len({e["key"] for e in E}))
    print("thin:", sorted(k for k, c in count.items() if c < 4))
    print("à:", sum(1 for it in out if it["p"][1 if isinstance(it["p"][0], str) else 0]["t"] == "a"), "total:", len(out))
    write_json(DATA / "prepositions.json", out)


if __name__ == "__main__":
    main()
