#!/usr/bin/env python3
"""Build the Édito B2 review drills in data/edito/.

Usage: python3 scripts/build_edito.py

Each lesson is a function returning its decks. To add a lesson, write a new function and list
it in LESSONS. The exercise sentences are written for this site; only the functional
expressions themselves come from the textbook's summary tables.
"""
import random
import re

from frtools import DATA, write_json

OUT = DATA / "edito"
rng = random.Random(3)


def classify_item(iid, expr, answer, x, labels, alt=()):
    """'Which function does this expression have?' with 4 options."""
    others = [l for l in labels if l != answer and l not in alt]
    wrong = rng.sample(others, 3)
    return dict(id=iid, layout="list", ctx="Quelle est la fonction de cette expression ?",
                p=[f"« {expr} »  → ", dict(a=answer, alt=list(alt), o=wrong, x=x, k=expr)])


# --------------------------------------------------------------------------- unit 1, lesson 1
def u1_opinions():
    L = {
        "ask": "Demander son avis",
        "give": "Donner son avis",
        "imp": "Exprimer ses impressions",
        "cert": "Exprimer la certitude",
        "doute": "Exprimer le doute",
        "poss": "Exprimer la possibilité",
        "imposs": "Exprimer l'impossibilité",
        "prob": "Exprimer la probabilité",
        "improb": "Exprimer l'improbabilité",
        "acc": "Exprimer son accord",
        "res": "Approuver avec des réserves",
        "des": "Exprimer son désaccord",
        "imp2": "Désapprouver de manière directe, voire impolie",
    }
    labels = list(L.values())
    E = [  # expression, function, English / note, other accepted functions
        ("Pouvez-vous me donner votre point de vue ?", "ask", "Could you give me your point of view? (formal)"),
        ("Quel est votre avis ?", "ask", "What is your opinion?"),
        ("Qu'en pensez-vous ?", "ask", "What do you think (of it)? En replaces 'de ça'."),
        ("Vous croyez que ça en vaut la peine ?", "ask", "Do you think it's worth it?"),
        ("Qu'est-ce que tu dis de ça ?", "ask", "What do you say to that? (informal)"),
        ("À ce qu'il me semble, …", "give", "As far as I can tell…"),
        ("À la réflexion, …", "give", "On reflection, having thought about it…"),
        ("À ma connaissance, …", "give", "As far as I know… (cautious opinion)"),
        ("À mes yeux, …", "give", "In my eyes, in my view…"),
        ("D'après moi, …", "give", "In my opinion…"),
        ("Selon moi, …", "give", "In my view…"),
        ("Quant à moi, …", "give", "As for me… (sets your view against others')"),
        ("En ce qui me concerne, …", "give", "As far as I'm concerned…"),
        ("De mon point de vue, …", "give", "From my point of view…"),
        ("Sauf erreur de ma part, …", "give", "Unless I'm mistaken…"),
        ("Il me semble que… (+ indicatif)", "give", "It seems to me that… — followed by the indicatif."),
        ("Ça ne m'étonnerait pas que… (+ subjonctif)", "give", "I wouldn't be surprised if… — followed by the subjonctif."),
        ("J'estime que…", "give", "I consider / reckon that… (+ indicatif)"),
        ("Personnellement, …", "give", "Personally…"),
        ("Je tiens à préciser que…", "give", "I'd like to make it clear that… (tenir à + infinitive = to be keen to)"),
        ("J'ai l'impression que…", "imp", "I have the impression / I get the feeling that… (+ indicatif)"),
        ("On dirait que…", "imp", "It looks as if… (+ indicatif)"),
        ("Il semble que… (+ subjonctif)", "imp", "It seems that… — followed by the subjonctif (unlike il me semble que)."),
        ("Il semblerait que…", "imp", "It would seem that… (+ subjonctif)"),
        ("Ça a l'air + adjectif", "imp", "It looks / seems (+ adjective): Ça a l'air compliqué."),
        ("Je vous assure.", "cert", "I assure you."),
        ("J'ai la conviction que…", "cert", "I am convinced that… (+ indicatif)"),
        ("J'en suis persuadé(e).", "cert", "I'm convinced of it."),
        ("J'en suis convaincu(e).", "cert", "I'm convinced of it."),
        ("J'en mettrais ma main au feu.", "cert", "I'd swear to it (lit. I'd put my hand in the fire)."),
        ("J'en mettrais ma main à couper.", "cert", "I'd bet my life on it (lit. I'd have my hand cut off)."),
        ("Ça dépend.", "doute", "It depends."),
        ("Pas forcément.", "doute", "Not necessarily."),
        ("J'en doute.", "doute", "I doubt it. (Also listed as a way to disagree.)", ("des",)),
        ("Je n'y crois pas trop.", "doute", "I don't really believe it."),
        ("Cela me laisse perplexe.", "doute", "That leaves me puzzled / unconvinced."),
        ("Je n'arrive pas à me faire à cette idée.", "doute", "I can't get used to / accept that idea."),
        ("Ça me paraît invraisemblable.", "doute", "That seems unlikely / hard to believe to me."),
        ("Ça m'étonnerait.", "doute", "I'd be surprised. (= I doubt it)"),
        ("Il se pourrait bien que…", "poss", "It could well be that… (+ subjonctif)"),
        ("Éventuellement.", "poss", "Possibly, if need be. False friend: not 'eventually' (= finalement)."),
        ("Peut-être que…", "poss", "Maybe… (peut-être que + indicatif)"),
        ("C'est faisable.", "poss", "It's doable."),
        ("Il y a des chances que…", "poss", "There's a chance that… (+ subjonctif)"),
        ("Ça se pourrait.", "poss", "That could be."),
        ("C'est exclu.", "imposs", "That's out of the question."),
        ("C'est hors de question.", "imposs", "It's out of the question."),
        ("Impossible.", "imposs", "Impossible."),
        ("Je n'y crois pas un seul instant.", "imposs", "I don't believe it for a second."),
        ("Quand les poules auront des dents.", "imposs", "When pigs fly (lit. when hens have teeth)."),
        ("Probablement.", "prob", "Probably."),
        ("Je risque de…", "prob", "I'm likely to… (risquer de + infinitive, often for something unwelcome)."),
        ("Il est probable que…", "prob", "It's likely that… (+ indicatif, unlike il est peu probable que)."),
        ("Il y a de fortes chances que…", "prob", "There's a good chance that… (+ subjonctif)"),
        ("C'est peu probable.", "improb", "It's unlikely."),
        ("Il y a peu de chances que…", "improb", "There's little chance that… (+ subjonctif)"),
        ("Il est peu probable que…", "improb", "It's unlikely that… (+ subjonctif)"),
        ("Absolument.", "acc", "Absolutely."),
        ("Bien sûr que oui.", "acc", "Of course."),
        ("C'est une vraie question.", "acc", "That's a real issue (I agree it deserves attention)."),
        ("Ça ne fait aucun doute.", "acc", "There's no doubt about it."),
        ("Je vous approuve sans réserve.", "acc", "I fully agree with you."),
        ("Je suis d'accord avec le fait que…", "acc", "I agree that…"),
        ("Sans le moindre doute.", "acc", "Without the slightest doubt."),
        ("Vous avez bien raison.", "acc", "You're quite right."),
        ("C'est ça.", "acc", "That's it, exactly."),
        ("J'accepte l'idée que…", "acc", "I accept the idea that…"),
        ("Admettons.", "res", "Let's say so / granted (but…)."),
        ("Ça se peut.", "res", "Maybe; could be (a lukewarm yes). Also a way to express possibility.", ("poss",)),
        ("C'est à voir.", "res", "That remains to be seen."),
        ("Je n'ai rien contre.", "res", "I have nothing against it."),
        ("Mouais…", "res", "Yeah, I suppose… (sceptical, informal)."),
        ("Certes, mais…", "res", "Admittedly, but…"),
        ("Je ne partage pas votre avis.", "des", "I don't share your opinion."),
        ("Vous avez tort.", "des", "You're wrong."),
        ("Je ne pense absolument pas que…", "des", "I absolutely don't think that… (+ subjonctif)"),
        ("C'est une plaisanterie ?", "imp2", "Is this a joke? (sarcastic dismissal)"),
        ("Bla bla bla.", "imp2", "Blah blah blah (dismissive)."),
        ("Bref, à part ça ?", "imp2", "Right, anything else? (brushing the point aside)"),
        ("Tu rigoles ?", "imp2", "Are you kidding? (familiar)"),
        ("Et puis quoi encore ?", "imp2", "What next?! (indignant refusal)"),
        ("Jamais de la vie.", "imp2", "Not on your life."),
        ("Non mais tu veux rire !", "imp2", "You can't be serious!"),
        ("N'importe quoi !", "imp2", "Rubbish! Nonsense!"),
    ]
    fonctions = []
    for i, e in enumerate(E):
        expr, f, x = e[:3]
        alt = [L[a] for a in (e[3] if len(e) > 3 else ())]
        fonctions.append(classify_item(f"u1-f{i}", expr, L[f], x, labels, alt))

    # ---- mood after opinion expressions
    R = {
        "aff": "Opinion verbs in the affirmative (croire, penser, trouver, estimer, être sûr / convaincu que) take the indicatif.",
        "neg": "Opinion verbs in the negative (je ne crois pas que, je ne pense pas que, je ne suis pas sûr que) take the subjonctif.",
        "inv": "An inverted question with an opinion verb (Pensez-vous que… ? Crois-tu que… ?) takes the subjonctif.",
        "adj": "Je trouve + adjective + que expresses a feeling, so it takes the subjonctif (Je trouve bizarre qu'il fasse cela).",
        "semble": "Il me semble que takes the indicatif; il semble que / il semblerait que take the subjonctif.",
        "etonne": "Ça m'étonnerait que / ça ne m'étonnerait pas que express surprise, a feeling: subjonctif.",
        "poss": "Possibility (il se pourrait que, il est possible que, il y a des chances que) takes the subjonctif.",
        "prob": "Il est probable que takes the indicatif (likely is close to certain); il est peu probable que takes the subjonctif.",
        "doute": "Douter que takes the subjonctif.",
        "dirait": "On dirait que, il paraît que, j'ai l'impression que, peut-être que take the indicatif.",
        "cert": "Certainty (je suis sûr / certain / persuadé que, il est certain que) takes the indicatif; its negation takes the subjonctif.",
    }
    M = [  # sentence with {}, correct, wrong, mood of correct, rule
        ("Je crois que les voitures électriques {} bientôt moins chères.", "seront", "soient", "ind", "aff"),
        ("Je ne crois pas que le recyclage {} à sauver la planète.", "suffise", "suffit", "subj", "neg"),
        ("Penses-tu que nous {} vraiment changer nos habitudes ?", "puissions", "pouvons", "subj", "inv"),
        ("Je pense que le bio {} meilleur pour la santé.", "est", "soit", "ind", "aff"),
        ("Je ne pense pas que ce {} une bonne idée.", "soit", "est", "subj", "neg"),
        ("Je trouve que tu {} raison.", "as", "aies", "ind", "aff"),
        ("Je trouve dommage que les gens ne {} pas plus d'efforts.", "fassent", "font", "subj", "adj"),
        ("Je trouve étrange qu'il {} encore l'avion pour aller à Lyon.", "prenne", "prend", "subj", "adj"),
        ("Il me semble que les jeunes {} plus sensibles à l'écologie qu'avant.", "sont", "soient", "ind", "semble"),
        ("Il semble que la situation {} en train de changer.", "soit", "est", "subj", "semble"),
        ("Ça m'étonnerait qu'il {} à la manifestation.", "vienne", "vient", "subj", "etonne"),
        ("Ça ne m'étonnerait pas que le gouvernement {} marche arrière.", "fasse", "fait", "subj", "etonne"),
        ("Il se pourrait bien que la mairie {} les voitures dans le centre.", "interdise", "interdit", "subj", "poss"),
        ("Il est probable que les températures {} continuer à augmenter.", "vont", "aillent", "ind", "prob"),
        ("Il est peu probable que tout le monde {} végétarien.", "devienne", "devient", "subj", "prob"),
        ("Il y a des chances que nous {} le train cet été plutôt que l'avion.", "prenions", "prenons", "subj", "poss"),
        ("Je doute que les gouvernements {} vraiment quoi faire.", "sachent", "savent", "subj", "doute"),
        ("On dirait qu'il {} pleuvoir.", "va", "aille", "ind", "dirait"),
        ("Il paraît que les épiceries en vrac {} beaucoup de succès.", "ont", "aient", "ind", "dirait"),
        ("Je suis convaincu que nous {} réduire nos déchets.", "pouvons", "puissions", "ind", "cert"),
        ("Je ne suis pas sûr que ce {} la meilleure solution.", "soit", "est", "subj", "cert"),
        ("Je suis sûre qu'elle {} ton choix.", "comprendra", "comprenne", "ind", "cert"),
        ("Croyez-vous que ces mesures {} efficaces ?", "soient", "sont", "subj", "inv"),
        ("J'estime que chacun {} faire sa part.", "doit", "doive", "ind", "aff"),
        ("Je ne trouve pas que ce film {} si écologique.", "soit", "est", "subj", "neg"),
        ("Peut-être que les mentalités {} évoluer.", "vont", "aillent", "ind", "dirait"),
        ("Il est possible que la recyclerie {} fermer.", "doive", "doit", "subj", "poss"),
        ("J'ai l'impression que les gens {} plus attention qu'avant.", "font", "fassent", "ind", "dirait"),
        ("Il est certain que le climat {}.", "a changé", "ait changé", "ind", "cert"),
        ("Je ne pense pas qu'elle {} tort.", "ait", "a", "subj", "neg"),
        ("Pensez-vous qu'il {} trop tard pour agir ?", "soit", "est", "subj", "inv"),
        ("Je trouve normal que chacun {} donner son avis.", "puisse", "peut", "subj", "adj"),
        ("Je trouve que ce documentaire {} très bien fait.", "est", "soit", "ind", "aff"),
        ("Il n'est pas certain que le projet {}.", "aboutisse", "aboutit", "subj", "cert"),
        ("Je suis persuadée qu'il {} à l'heure.", "viendra", "vienne", "ind", "cert"),
        ("Je doute qu'on {} tout recycler.", "puisse", "peut", "subj", "doute"),
        ("Il me semble que tu {} bien le sujet.", "connais", "connaisses", "ind", "semble"),
        ("Trouvez-vous que les jeunes {} assez informés ?", "soient", "sont", "subj", "inv"),
        ("Il semblerait que les ventes de vélos {} fortement augmenté.", "aient", "ont", "subj", "semble"),
        ("Je ne suis pas convaincu qu'il {} la vérité.", "dise", "dit", "subj", "cert"),
        ("Il est probable qu'il {} demain.", "pleuvra", "pleuve", "ind", "prob"),
        ("Crois-tu qu'on {} vivre sans plastique ?", "puisse", "peut", "subj", "inv"),
    ]
    LABEL = {"aff": "verbe d'opinion affirmatif", "neg": "verbe d'opinion négatif", "inv": "question avec inversion",
             "adj": "je trouve + adjectif + que", "semble": "il (me) semble que", "etonne": "ça (ne) m'étonnerait (pas) que",
             "poss": "possibilité", "prob": "(peu) probable", "doute": "douter que", "dirait": "on dirait / il paraît / peut-être que",
             "cert": "certitude"}
    modes = []
    for i, (sent, a, o, mood, rule) in enumerate(M):
        before, after = sent.split("{}")
        modes.append(dict(id=f"u1-m{i}", p=[before, dict(a=a, o=[o], x=R[rule], t=mood, k="mode: " + LABEL[rule]), after]))

    # ---- react: find an equivalent expression
    Q = [  # statement, reaction, equivalent, wrong options, function
        ("Trier ses déchets ne sert à rien.", "Vous avez tort.", "Je ne partage pas votre avis.",
         ["Vous avez bien raison.", "Admettons.", "Ça ne fait aucun doute."], "des"),
        ("Il faut manger local et de saison.", "Ça ne fait aucun doute.", "Sans le moindre doute.",
         ["J'en doute.", "Mouais…", "Tu rigoles ?"], "acc"),
        ("Cette année, je deviens complètement zéro déchet !", "Je n'y crois pas trop.", "Ça m'étonnerait.",
         ["J'en mettrais ma main au feu.", "Bien sûr que oui.", "Je vous approuve sans réserve."], "doute"),
        ("On pourrait fabriquer nous-mêmes notre lessive.", "Non mais tu veux rire !", "Et puis quoi encore ?",
         ["Je n'ai rien contre.", "Vous avez bien raison.", "C'est une vraie question."], "imp2"),
        ("Tout le monde fait de son mieux pour la planète.", "Je n'en suis pas si sûr.", "Pas forcément.",
         ["Je vous assure.", "Absolument.", "J'en suis convaincu."], "doute"),
        ("Et si on tricotait tous nos propres pulls ?", "N'importe quoi !", "Bla bla bla.",
         ["C'est faisable.", "Admettons.", "J'accepte l'idée."], "imp2"),
        ("Le bio, c'est meilleur pour la planète.", "Certes, mais c'est plus cher.", "Admettons, mais…",
         ["Sans aucun doute.", "Vous avez tort.", "Quand les poules auront des dents."], "res"),
        ("On pourrait installer un composteur dans la cour de l'immeuble.", "Je n'ai rien contre.", "Admettons.",
         ["C'est hors de question.", "Tu rigoles ?", "J'en doute."], "res"),
        ("Un jour, plus personne ne prendra l'avion.", "Quand les poules auront des dents !", "Je n'y crois pas un seul instant.",
         ["Probablement.", "J'en mettrais ma main au feu.", "C'est ça."], "imposs"),
        ("Les vélos électriques vont remplacer les voitures en ville.", "Il y a de fortes chances.", "Probablement.",
         ["C'est exclu.", "C'est peu probable.", "Et puis quoi encore ?"], "prob"),
        ("Le gouvernement va interdire les SUV l'an prochain.", "C'est peu probable.", "Il y a peu de chances.",
         ["Il y a de fortes chances.", "J'en suis persuadé.", "Bien sûr que oui."], "improb"),
        ("Tu penses qu'on peut vivre sans voiture à la campagne ?", "Ça dépend.", "Pas forcément.",
         ["Absolument.", "C'est exclu.", "Et puis quoi encore ?"], "doute"),
        ("Est-ce que tu viendras à la manifestation pour le climat ?", "Ça se pourrait.", "Éventuellement.",
         ["Jamais de la vie.", "Je vous assure.", "C'est hors de question."], "poss"),
        ("La mode jetable est une catastrophe écologique.", "Vous avez bien raison.", "Je vous approuve sans réserve.",
         ["Je ne partage pas votre avis.", "C'est à voir.", "Ça me paraît invraisemblable."], "acc"),
        ("Ce nouveau magasin bio va fermer dans six mois.", "Ça m'étonnerait.", "Ça me paraît invraisemblable.",
         ["J'en mettrais ma main à couper.", "C'est ça.", "Il y a de fortes chances."], "doute"),
        ("Le recyclage du plastique est vraiment efficace.", "Je ne partage pas votre avis.", "Vous avez tort.",
         ["Vous avez bien raison.", "C'est une vraie question.", "Absolument."], "des"),
        ("Ma sœur va devenir végétarienne, c'est sûr.", "J'en mettrais ma main au feu !", "J'en suis convaincu.",
         ["Ça dépend.", "Ça m'étonnerait.", "Admettons."], "cert"),
        ("On pourrait organiser une journée sans écrans au bureau.", "C'est faisable.", "Ça se pourrait.",
         ["C'est exclu.", "Tu rigoles ?", "Jamais de la vie."], "poss"),
        ("Supprimer tous les emballages d'ici l'an prochain ?", "C'est hors de question.", "C'est exclu.",
         ["C'est faisable.", "Ça se pourrait.", "Probablement."], "imposs"),
        ("Le covoiturage, c'est l'avenir.", "Mouais…", "C'est à voir.",
         ["Ça ne fait aucun doute.", "N'importe quoi !", "Je vous assure."], "res"),
    ]
    reagir = []
    for i, (stmt, react, eq, wrong, f) in enumerate(Q):
        reagir.append(dict(id=f"u1-r{i}", layout="list", ctx=f"— {stmt}\n— {react}",
                           p=[f"Une réaction équivalente à « {react} » :  ", dict(
                               a=eq, o=wrong, k=react,
                               x=f"« {react} » and « {eq} » both belong to « {L[f]} ».")]))
    return dict(id="u1-opinions", unit="Unité 1", title="Échanger des opinions (p. 14–15)", decks=[
        dict(id="fonctions", label="Fonctions", modes=["choose"], items=fonctions,
             info="Which function does each expression from the tables have?"),
        dict(id="modes", label="Indicatif ou subjonctif ?", modes=["choose"], items=modes,
             info="Rappel: the mood after verbs and expressions of opinion."),
        dict(id="reagir", label="Réagir", modes=["choose"], items=reagir,
             info="Pick a reaction with the same function."),
    ])


# --------------------------------------------------------------------------- unit 1, lesson 2
BANK_BLANK = re.compile(r"\[\[([^\]]+)\]\]")


def bank_parts(text, explain):
    """Parse [[answer|alt|alt]] blanks; explain(key) gives the explanation."""
    parts, pos = [], 0
    for m in BANK_BLANK.finditer(text):
        if m.start() > pos:
            parts.append(text[pos:m.start()])
        opts = m.group(1).split("|")
        before = text[:m.start()].rstrip(" ")
        cap = before == "" or before[-1] in ".!?\n"
        parts.append(dict(a=opts[0], alt=opts[1:], x=explain(opts[0]), k=opts[0], cap=cap))
        pos = m.end()
    if pos < len(text):
        parts.append(text[pos:])
    return parts


def u1_argumenter():
    L = {
        "idee": "Introduire une idée",
        "cause": "Introduire un argument par une cause",
        "cons": "Introduire un argument par une conséquence",
        "ajout": "Ajouter un argument",
        "ex": "Introduire un exemple",
        "adm": "Admettre l'argument contraire avant de le réfuter",
        "opp": "Marquer l'opposition",
        "prec": "Préciser",
        "ref": "Reformuler",
        "soul": "Souligner, mettre en évidence",
        "gen": "Généraliser",
        "res": "Résumer",
        "concl": "Conclure",
        "indig": "Exprimer son indignation",
    }
    labels = list(L.values())
    E = [
        ("pour commencer", "idee", "to begin with"),
        ("avant toute chose", "idee", "first and foremost"),
        ("tout d'abord", "idee", "first of all"),
        ("d'abord", "idee", "first"),
        ("premièrement", "idee", "firstly"),
        ("en premier lieu", "idee", "in the first place (formal)"),
        ("car", "cause", "because, for: in the middle of the sentence, never at the start in careful writing"),
        ("parce que", "cause", "because: + clause (à cause de + noun)"),
        ("puisque", "cause", "since: the cause is presented as obvious or already known"),
        ("en effet", "cause", "indeed, the fact is: explains or justifies the previous sentence"),
        ("à cause de", "cause", "because of: + noun, usually for a negative cause (grâce à for a positive one)"),
        ("donc", "cons", "so, therefore"),
        ("de manière à", "cons", "so as to: + infinitive, the intended result"),
        ("ainsi", "cons", "thus, in this way"),
        ("par conséquent", "cons", "consequently (formal)"),
        ("pour cela", "cons", "for that (purpose), to do so"),
        ("de plus", "ajout", "moreover, in addition"),
        ("en outre", "ajout", "furthermore (formal)"),
        ("par ailleurs", "ajout", "besides, in another respect: adds a point about a different aspect"),
        ("ensuite", "ajout", "next: adds the following argument"),
        ("d'une part… d'autre part", "ajout", "on the one hand… on the other hand: two complementary arguments, not a contrast"),
        ("non seulement… mais aussi", "ajout", "not only… but also"),
        ("comme on peut le voir…", "ex", "as can be seen (in)…"),
        ("en particulier", "ex", "in particular"),
        ("tel que", "ex", "such as: agrees with the noun (tel, telle, tels, telles que)"),
        ("par exemple", "ex", "for example"),
        ("notamment", "ex", "notably, in particular"),
        ("certes", "adm", "admittedly: concede, then refute with mais"),
        ("bien que (+ subjonctif)", "adm", "although: always followed by the subjonctif"),
        ("même si (+ indicatif)", "adm", "even if, even though: followed by the indicatif, never the subjonctif"),
        ("mais", "opp", "but"),
        ("alors que", "opp", "whereas, while: contrasts two facts"),
        ("tandis que", "opp", "whereas, while: contrast, or two things happening at the same time"),
        ("au contraire", "opp", "on the contrary: states the opposite of what precedes"),
        ("pourtant", "opp", "yet, and yet: a surprising contradiction"),
        ("en revanche", "opp", "on the other hand, by contrast"),
        ("par contre", "opp", "on the other hand (informal equivalent of en revanche)"),
        ("cependant", "opp", "however"),
        ("néanmoins", "opp", "nevertheless (formal)"),
        ("toutefois", "opp", "however, nonetheless (formal)"),
        ("tout de même", "opp", "all the same, still"),
        ("quand même", "opp", "all the same, still (more informal than tout de même)"),
        ("à l'inverse", "opp", "conversely: presents the opposite case"),
        ("à ce propos, il faut ajouter que", "prec", "in this regard, it should be added that"),
        ("à ce sujet, on peut préciser que", "prec", "on this subject, we can specify that"),
        ("en d'autres termes", "ref", "in other words"),
        ("autrement dit", "ref", "in other words"),
        ("c'est-à-dire", "ref", "that is (to say)"),
        ("soulignons", "soul", "let us stress"),
        ("il faut souligner", "soul", "it must be stressed (that)"),
        ("remarquons", "soul", "let us note"),
        ("il faut remarquer", "soul", "it should be noted (that)"),
        ("on peut insister sur le fait que", "soul", "we can emphasise the fact that"),
        ("d'une façon générale", "gen", "generally speaking"),
        ("en général", "gen", "in general"),
        ("globalement", "gen", "overall, on the whole"),
        ("en règle générale", "gen", "as a general rule"),
        ("en un mot", "res", "in a word"),
        ("en résumé", "res", "in summary"),
        ("pour résumer", "res", "to sum up"),
        ("en bref", "res", "in short"),
        ("en définitive", "concl", "ultimately, when all is said and done"),
        ("finalement", "concl", "in the end, finally"),
        ("en fin de compte", "concl", "all things considered, in the end"),
        ("en conclusion", "concl", "in conclusion"),
        ("pour terminer", "concl", "to finish, to end with"),
        ("Je suis choqué(e). / Cela me choque. / C'est choquant !", "indig", "I'm shocked. / That shocks me. / It's shocking!"),
        ("Je suis révolté(e) / indigné(e) / exaspéré(e) / outré(e) !", "indig", "I'm appalled / outraged / exasperated / scandalised!"),
        ("Quel scandale !", "indig", "What a scandal! / It's outrageous!"),
        ("Cela dépasse les limites !", "indig", "That goes too far!"),
        ("C'en est trop !", "indig", "That's the last straw! / Enough is enough!"),
        ("C'est inacceptable / révoltant / exaspérant !", "indig", "It's unacceptable / appalling / infuriating!"),
    ]
    fonctions = [classify_item(f"u1a-f{i}", expr, L[f], f"{L[f]}: {x}.", labels)
                 for i, (expr, f, x) in enumerate(E)]

    # explanations for blanks, keyed by the connector as written in the text
    X = {e[0].split(" (")[0].split("…")[0]: f"{L[e[1]]}: {e[2]}." for e in E}
    X.update({
        "non seulement": X["non seulement"] if "non seulement" in X else
        "Ajouter un argument: non seulement… mais aussi = not only… but also.",
        "mais aussi": "Ajouter un argument: non seulement… mais aussi = not only… but also.",
        "d'une part": "Ajouter un argument: d'une part… d'autre part = on the one hand… on the other; two complementary points.",
        "d'autre part": "Ajouter un argument: second half of d'une part… d'autre part; it adds, it does not contrast.",
        "tels que": "Introduire un exemple: tel que agrees with the noun it follows (tel, telle, tels, telles que).",
        "révolté": "Exprimer son indignation: je suis révolté(e) / indigné(e) / outré(e) = I'm appalled, outraged.",
        "c'est inacceptable": "Exprimer son indignation: c'est inacceptable / révoltant / choquant !",
        "bien que": X["bien que"],
    })

    def explain(k):
        k2 = k.lower()
        if k2 not in X:
            raise SystemExit(f"no explanation for {k!r}")
        return X[k2]

    T = [
        ("Les pollinisateurs", ["tandis que", "à cause de"],
         "[[avant toute chose|tout d'abord|pour commencer|en premier lieu]], rappelons que les insectes pollinisateurs, dont "
         "les abeilles, contribuent à près des trois quarts des cultures alimentaires. Leur déclin menace [[donc|par conséquent|ainsi]] "
         "directement notre alimentation. Les pesticides, [[en particulier|notamment]] les néonicotinoïdes, en sont l'une des "
         "principales causes. [[certes]], les agriculteurs doivent protéger leurs récoltes, [[mais]] des solutions existent : "
         "on peut [[par exemple|notamment]] planter des haies fleuries [[de manière à]] offrir aux insectes refuge et nourriture. "
         "[[en définitive|en conclusion|finalement|en fin de compte]], protéger les pollinisateurs, c'est nous protéger nous-mêmes."),
        ("Les zones humides", ["de manière à", "tel que"],
         "Les zones humides sont souvent considérées comme des terrains inutiles. [[pourtant|cependant|toutefois|néanmoins]], "
         "elles rendent des services essentiels. [[d'une part]], elles filtrent l'eau et la purifient ; [[d'autre part]], "
         "elles limitent les inondations [[car|parce que|puisque]] elles absorbent l'eau comme des éponges. "
         "[[en d'autres termes|autrement dit]], les détruire revient à supprimer une protection naturelle et gratuite. "
         "[[soulignons|remarquons|il faut souligner|il faut remarquer]] qu'une grande partie d'entre elles a disparu en France "
         "au cours du XXe siècle."),
        ("Les forêts", ["de manière à", "tel que"],
         "[[à cause de]] la déforestation, de nombreuses espèces perdent leur habitat. [[alors que|tandis que]] les forêts "
         "tropicales couvrent une petite partie des terres émergées, elles abritent plus de la moitié des espèces terrestres "
         "connues. [[bien que]] des programmes de reboisement existent, ils ne remplacent pas les forêts anciennes. "
         "[[en effet]], une plantation récente n'offre pas la même diversité qu'une forêt primaire. "
         "[[à l'inverse|en revanche]], protéger les forêts existantes coûte moins cher et donne des résultats immédiats. "
         "[[en résumé|en bref|en un mot|pour résumer]] : mieux vaut préserver que replanter."),
        ("La pêche", ["bien que", "à cause de"],
         "[[en règle générale|en général|d'une façon générale|globalement]], les poissons que nous mangeons proviennent de "
         "stocks de plus en plus fragiles. La pêche industrielle vide les océans, [[car|puisque|parce que]] les bateaux "
         "capturent plus de poissons que les espèces ne peuvent en renouveler. [[à ce propos, il faut ajouter que|à ce sujet, "
         "on peut préciser que]] de nombreux animaux sont pris par erreur dans les filets, [[tels que]] les dauphins ou les "
         "tortues. Ces captures menacent [[non seulement]] des espèces protégées, [[mais aussi]] l'équilibre de tout "
         "l'écosystème. [[en conclusion|en définitive|pour terminer|finalement|en fin de compte]], consommer moins de "
         "poisson, et mieux le choisir, devient une nécessité."),
        ("Prise de parole · Journée mondiale de la biodiversité", ["à cause de", "de manière à"],
         "Mesdames et Messieurs, [[pour commencer|tout d'abord|avant toute chose]], je voudrais vous dire à quel point je suis "
         "[[révolté]] par l'indifférence face au déclin de la biodiversité. On nous répète que la situation s'améliore. "
         "[[pourtant|cependant|toutefois|néanmoins]], environ un million d'espèces sont aujourd'hui menacées d'extinction. "
         "[[c'est inacceptable]] ! [[certes]], chacun fait des petits gestes, [[mais]] cela ne suffit pas : il faut "
         "[[en outre|de plus|par ailleurs]] que les États prennent des décisions fortes. [[en un mot|en bref|en résumé|pour résumer]], "
         "il est temps d'agir."),
    ]
    textes = [dict(id=f"u1a-t{i}", layout="bank", ctx="Placez les mots manquants.", head=title, bank=bank,
                   p=bank_parts(text, explain)) for i, (title, bank, text) in enumerate(T)]

    P = [  # sentence with ___, answer, wrong options, explanation key or text, review key
        ("___ les arbres absorbent du CO2, la déforestation aggrave le réchauffement.", "Puisque",
         ["Bien que", "De manière à"], "puisque", None),
        ("Bien que cette espèce ___ protégée, elle continue de décliner.", "soit", ["est", "sera"],
         "Bien que is always followed by the subjonctif.", "bien que + subjonctif"),
        ("Même si cette espèce ___ protégée, elle continue de décliner.", "est", ["soit", "serait"],
         "Même si is followed by the indicatif, never the subjonctif.", "même si + indicatif"),
        ("Bien que les ONG ___ l'alerte depuis des années, rien ne change.", "aient donné", ["ont donné", "donneront"],
         "Bien que + subjonctif, here the subjonctif passé (aient donné).", "bien que + subjonctif"),
        ("Même si les scientifiques ___ l'alerte depuis des années, rien ne change.", "donnent", ["aient donné", "donneraient"],
         "Même si + indicatif (here the présent).", "même si + indicatif"),
        ("Il faut réduire les pesticides ___ protéger les pollinisateurs.", "de manière à", ["bien que", "à cause de"],
         "de manière à", None),
        ("Certains animaux, ___ le loup ou le lynx, reviennent dans nos montagnes.", "tels que", ["tel que", "telles que"],
         "Tel que agrees with the noun: animaux is masculine plural, so tels que.", "tel que (accord)"),
        ("Certaines espèces, ___ la loutre, sont réapparues dans nos rivières.", "telles que", ["tels que", "telle que"],
         "Tel que agrees with the noun it follows: espèces is feminine plural, so telles que.", "tel que (accord)"),
        ("La ville a planté des arbres dans les rues ; ___, la température y a baissé en été.", "par conséquent",
         ["certes", "en revanche"], "par conséquent", None),
        ("Les villes s'étendent, ___ les espaces naturels reculent.", "tandis que", ["car", "de manière à"], "tandis que", None),
        ("Le loup est protégé dans l'Union européenne. ___, certains éleveurs demandent le droit de l'abattre.", "Toutefois",
         ["Par conséquent", "Par exemple"], "toutefois", None),
        ("___, le recyclage ne suffit pas, mais il reste utile.", "Certes", ["Car", "Par exemple"], "certes", None),
        ("Les haies abritent ___ des oiseaux, mais aussi des insectes et des petits mammifères.", "non seulement",
         ["en revanche", "à cause de"], "non seulement", None),
        ("La biodiversité, ___ la diversité du vivant sur Terre, est menacée.", "c'est-à-dire", ["par conséquent", "car"],
         "c'est-à-dire", None),
        ("___ la pollution, de nombreux poissons meurent.", "À cause de", ["Parce que", "De manière à"],
         "À cause de + noun; parce que + clause.", "à cause de / parce que"),
        ("De nombreux poissons meurent ___ l'eau est polluée.", "parce que", ["à cause de", "tel que"],
         "Parce que + clause; à cause de + noun.", "à cause de / parce que"),
        ("Les zones humides limitent les inondations. ___, elles absorbent l'eau comme des éponges.", "En effet",
         ["Ainsi", "Certes"], "en effet", None),
        ("___, les espèces menacées vivent dans des milieux fragiles.", "En règle générale", ["Par conséquent", "Certes"],
         "en règle générale", None),
        ("Nous avons parlé des forêts, des océans et des sols. ___ : tout est lié.", "En un mot", ["En effet", "Par exemple"],
         "en un mot", None),
        ("Voilà pour mes arguments. ___, je dirais que chacun peut agir à son échelle.", "Pour terminer",
         ["Avant toute chose", "En particulier"], "pour terminer", None),
        ("Les chats domestiques chassent beaucoup d'oiseaux. ___, il faut ajouter qu'ils chassent aussi les lézards.",
         "À ce propos", ["Bien que", "Par contre"], "à ce propos, il faut ajouter que", None),
        ("Le projet a été très critiqué ; il a ___ été adopté.", "tout de même", ["car", "tel que"], "tout de même", None),
        ("La forêt amazonienne recule, ___ certaines forêts européennes progressent.", "alors que",
         ["car", "de manière à"], "alors que", None),
        ("Les insectes sont menacés ; ___, les abeilles sauvages disparaissent à un rythme inquiétant.", "en particulier",
         ["à l'inverse", "bien que"], "en particulier", None),
        ("Les sols sont vivants ; il faut ___ éviter de les tasser et de les polluer.", "donc", ["certes", "pourtant"],
         "donc", None),
        ("Les grandes cultures appauvrissent les sols. ___, les prairies naturelles les enrichissent.", "À l'inverse",
         ["Ensuite", "En effet"], "à l'inverse", None),
        ("La chasse est réglementée ; ___, des braconniers tuent encore des animaux protégés.", "néanmoins",
         ["ainsi", "en général"], "néanmoins", None),
        ("Les abeilles disparaissent. ___, sans elles, beaucoup de fruits ne pourraient plus pousser.", "Soulignons que",
         ["Bien que", "À cause de"], "soulignons", None),
    ]
    phrases = []
    for i, (sent, a, wrong, xk, key) in enumerate(P):
        before, after = sent.split("___")
        x = X.get(xk.lower(), xk) if xk.lower() in X else xk
        phrases.append(dict(id=f"u1a-p{i}", layout="list", p=[before, dict(a=a, o=wrong, x=x, k=key or a.lower()), after]))

    return dict(id="u1-argumenter", unit="Unité 1", title="Argumenter (p. 20)", decks=[
        dict(id="fonctions", label="Fonctions", items=fonctions,
             info="What does each connector do in an argument? Includes the « Exprimer son indignation » box."),
        dict(id="textes", label="Placez les mots", items=textes,
             info="Fill the blanks from the word bank. Some blanks accept more than one connector."),
        dict(id="phrases", label="Quel connecteur ?", items=phrases,
             info="One blank per sentence, including bien que / même si, à cause de / parce que and tel que."),
    ])


LESSONS = [u1_opinions, u1_argumenter]


def main():
    index = []
    for f in LESSONS:
        lesson = f()
        path = OUT / f"{lesson['id']}.json"
        write_json(path, lesson["decks"])
        index.append(dict(id=lesson["id"], unit=lesson["unit"], title=lesson["title"], file=f"data/edito/{path.name}",
                          decks=[dict(id=d["id"], label=d["label"]) for d in lesson["decks"]]))
    write_json(OUT / "index.json", index)


if __name__ == "__main__":
    main()
