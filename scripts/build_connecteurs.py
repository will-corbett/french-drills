#!/usr/bin/env python3
"""Build data/connecteurs-textes.json and data/connecteurs-phrases.json from the content below.

Usage: python3 scripts/build_connecteurs.py

Texts are model answers to TCF Expression écrite tasks, written for this site. In a text,
[[key]] marks a blank whose answer is that glossary entry; [[key|alt|alt]] lists other
connectors that would also be correct in that slot.
"""
import random
import re

from frtools import DATA, write_json

G = {}  # key -> (group, explanation)


def g(group, *entries):
    for key, x, phrase in entries:
        G[key] = dict(group=group, x=x, phrase=phrase)


g("ordre",
  ("tout d'abord", "First of all: opens the first point of an argument.",
   "Bonjour à tous. [[tout d'abord]], je voudrais vous remercier de votre accueil."),
  ("ensuite", "Next, then: introduces the following point or step.",
   "Il faut d'abord réserver les billets ; [[ensuite]], on cherchera un hôtel."),
  ("enfin", "Finally, lastly: the last item of a list (it can also mean 'at last').",
   "Je vois trois raisons : le prix, la qualité et, [[enfin]], la proximité."),
  ("d'une part", "On the one hand: announces the first of two complementary points (paired with d'autre part).",
   "[[d'une part]], le projet coûte cher ; d'autre part, il prendra des années."),
  ("d'autre part", "On the other hand, moreover: the second point after d'une part. It adds; unlike en revanche, it does not contrast.",
   "D'une part, ce métier est mal payé ; [[d'autre part]], les horaires sont difficiles."),
  ("d'un côté", "On one side: the first of two contrasting sides (paired with de l'autre).",
   "[[d'un côté]], la grande ville offre plus d'emplois ; de l'autre, la vie y est plus chère."),
  ("de l'autre", "On the other (side): the second of two contrasting sides after d'un côté.",
   "D'un côté, j'aime mon travail ; [[de l'autre]], je rêve de voyager."),
  ("au début", "At first: sets up a change described afterwards (puis, ensuite, peu à peu).",
   "[[au début]], je ne comprenais rien ; maintenant, je suis presque bilingue."),
  ("puis", "Then: the next step in a sequence; more narrative than ensuite.",
   "Nous avons visité le musée, [[puis]] nous avons déjeuné au bord du lac."),
  ("désormais", "From now on: a new situation that will last.",
   "J'ai trouvé un appartement près du bureau : [[désormais]], je vais au travail à pied."),
  ("finalement", "In the end, eventually: the outcome after events or hesitation; less formal than en définitive.",
   "J'ai longtemps hésité, mais [[finalement]], j'ai accepté le poste."),
  )
g("ajout",
  ("de plus", "Moreover, in addition: adds a further argument; neutral register.",
   "Ce téléphone est trop cher. [[de plus]], sa batterie ne dure pas longtemps."),
  ("en outre", "Furthermore: formal equivalent of de plus, typical of written argument.",
   "Le projet réduira la pollution. Il créera [[en outre]] plusieurs centaines d'emplois."),
  ("par ailleurs", "Besides, in another respect: adds a point about a different aspect of the topic.",
   "La réforme simplifie les démarches. [[par ailleurs]], elle prévoit une aide pour les familles."),
  ("d'ailleurs", "Besides, in fact: adds a remark that backs up what was just said, often as an aside.",
   "Ce restaurant est excellent ; [[d'ailleurs]], il est toujours complet le week-end."),
  ("qui plus est", "What's more: adds a stronger, often clinching argument; slightly literary.",
   "Ce vélo est léger et, [[qui plus est]], il ne coûte que deux cents euros."),
  ("en plus", "On top of that: informal de plus; fine in a message to a friend, too casual for formal writing.",
   "Il pleuvait et, [[en plus]], j'avais oublié mon parapluie !"),
  ("d'autant plus que", "All the more so since: adds a reason that strengthens the previous statement.",
   "Je dois finir ce dossier ce soir, [[d'autant plus que]] je pars en vacances demain."),
  )
g("exemple",
  ("par exemple", "For example.",
   "Beaucoup de fruits poussent ici : les pommes, [[par exemple]], ou les poires."),
  ("notamment", "In particular, notably: singles out a prominent example inside the sentence.",
   "Plusieurs pays, [[notamment]] le Danemark, ont développé le vélo en ville."),
  )
g("cause",
  ("en effet", "Indeed, the fact is: justifies or explains the previous sentence. It does not mean 'in effect'.",
   "Je ne prends plus l'avion. [[en effet]], c'est le moyen de transport le plus polluant."),
  ("car", "Because, for: coordinating conjunction in the middle of a sentence; it does not start a sentence in careful writing.",
   "Je reste à la maison ce soir, [[car]] je suis épuisé."),
  ("puisque", "Since: the cause is presented as obvious or already known to the reader.",
   "[[puisque]] tu as fini tes devoirs, tu peux aller jouer."),
  ("comme", "As, since: a cause placed at the start of the sentence.",
   "[[comme]] il faisait beau, nous avons mangé dehors."),
  ("étant donné que", "Given that: formal cause, followed by the indicatif.",
   "[[étant donné que]] les prix augmentent, il faut revoir notre budget."),
  ("grâce à", "Thanks to + noun: a cause with a positive result.",
   "[[grâce à]] ton aide, j'ai réussi mon examen."),
  ("à cause de", "Because of + noun: a cause with a negative (or neutral) result.",
   "Le match a été annulé [[à cause de]] la pluie."),
  ("en raison de", "Owing to, due to + noun: formal and neutral, typical of announcements and reports.",
   "Le musée sera fermé lundi [[en raison de]] travaux."),
  )
g("conséquence",
  ("donc", "So, therefore: the basic consequence connector.",
   "Il n'y avait plus de bus, j'ai [[donc]] pris un taxi."),
  ("c'est pourquoi", "That's why: introduces a consequence at the start of a clause.",
   "Je travaille tôt demain ; [[c'est pourquoi]] je ne sortirai pas ce soir."),
  ("par conséquent", "Consequently: formal consequence.",
   "Les inscriptions sont complètes ; [[par conséquent]], aucune nouvelle demande ne sera acceptée."),
  ("si bien que", "So that, with the result that (+ indicatif): links a cause and its result in one sentence.",
   "Il a beaucoup neigé, [[si bien que]] les écoles sont restées fermées."),
  ("ainsi", "Thus, in this way: consequence or illustration; it can go in the middle of the sentence.",
   "Le tram a été prolongé ; les habitants peuvent [[ainsi]] rejoindre le centre en dix minutes."),
  ("du coup", "So, as a result: very common in speech; informal, avoid it in formal writing.",
   "Mon train était en retard, [[du coup]] j'ai raté le début du film."),
  )
g("but",
  ("afin de", "In order to + infinitive: purpose; more formal than pour.",
   "La mairie a créé des pistes cyclables [[afin de]] réduire la circulation."),
  )
g("opposition",
  ("cependant", "However: introduces an opposing point; standard written register.",
   "Le projet est ambitieux. [[cependant]], son financement reste incertain."),
  ("pourtant", "Yet, and yet: stresses a surprising contradiction with what precedes.",
   "Il a beaucoup révisé ; [[pourtant]], il a raté l'examen."),
  ("néanmoins", "Nevertheless: concedes, then maintains the opposing point; formal.",
   "Le voyage a été fatigant. Il a [[néanmoins]] été très enrichissant."),
  ("toutefois", "However, nonetheless: formal; often limits or qualifies what precedes.",
   "L'entrée est gratuite ; il est [[toutefois]] conseillé de réserver."),
  ("en revanche", "On the other hand, by contrast: contrasts two facts or two sides.",
   "Le premier film m'a ennuyé ; le second, [[en revanche]], m'a passionné."),
  ("par contre", "On the other hand: informal equivalent of en revanche; prefer en revanche in formal writing.",
   "Le quartier est sympa. [[par contre]], il n'y a aucun parking."),
  ("au contraire", "On the contrary: states the opposite of what was just said or expected.",
   "Le télétravail ne m'isole pas ; [[au contraire]], j'ai plus de temps pour voir mes amis."),
  ("alors que", "Whereas, while (+ indicatif): contrasts two facts in one sentence.",
   "Mon frère adore la montagne, [[alors que]] moi, je préfère la mer."),
  ("malgré", "Despite + noun.",
   "Ils sont sortis [[malgré]] la tempête."),
  ("malgré tout", "All the same, even so: acknowledges the difficulties but maintains the point.",
   "Le chemin était long et difficile ; [[malgré tout]], nous sommes arrivés à temps."),
  ("malheureusement", "Unfortunately: presents bad news or a regret.",
   "J'aurais aimé venir ; [[malheureusement]], je travaille ce jour-là."),
  )
g("concession",
  ("certes", "Admittedly: concedes a point before a counter-argument (mais, néanmoins).",
   "[[certes]], ce logement est petit, mais il est très bien situé."),
  ("il est vrai que", "It is true that: concedes a point before a counter-argument.",
   "[[il est vrai que]] les transports en commun sont parfois bondés, mais ils restent pratiques."),
  ("bien que", "Although + subjonctif.",
   "[[bien qu']]il soit fatigué, il continue à travailler."),
  )
g("insistance",
  ("il faut souligner que", "It should be stressed that: highlights an important fact in your argument.",
   "[[il faut souligner que]] cette mesure a déjà fait ses preuves dans d'autres pays."),
  ("il convient de rappeler que", "It is worth recalling that: formal; brings back a known fact relevant to the argument.",
   "[[il convient de rappeler que]] l'accès à l'éducation est un droit fondamental."),
  ("surtout", "Above all, especially.",
   "J'aime voyager, [[surtout]] en train."),
  )
g("opinion",
  ("à mon avis", "In my opinion.",
   "Vous me demandez ce que je pense de cette loi. [[à mon avis]], elle ne changera pas grand-chose."),
  ("selon", "According to: attributes a view to a source (selon l'auteur, selon le premier document).",
   "[[selon]] l'auteur de l'article, le télétravail améliore la productivité."),
  ("personnellement", "Personally: introduces your own position.",
   "On me demande souvent si la ville me manque. [[personnellement]], je préfère vivre à la campagne."),
  ("pour ma part", "As for me: your own view, often set against other people's.",
   "Mes amis adorent ce film ; [[pour ma part]], je l'ai trouvé trop long."),
  )
g("reformulation",
  ("autrement dit", "In other words: restates the idea more simply or more precisely.",
   "Le magasin ouvre sept jours sur sept : [[autrement dit]], il ne ferme jamais."),
  ("c'est-à-dire", "That is (to say): clarifies or specifies what has just been said.",
   "Je pars le week-end prochain, [[c'est-à-dire]] le 14 et le 15 mai."),
  )
g("conclusion",
  ("en conclusion", "In conclusion: formal, opens the final paragraph.",
   "[[en conclusion]], les avantages de ce projet l'emportent sur ses inconvénients."),
  ("pour conclure", "To conclude: same as en conclusion.",
   "Voilà les principaux arguments. [[pour conclure]], je dirais que chacun doit faire sa part."),
  ("en fin de compte", "All things considered, in the end: gives the final assessment after weighing the arguments.",
   "Les billets étaient chers, mais [[en fin de compte]], ce concert valait vraiment le coup."),
  ("en définitive", "Ultimately, when all is said and done: formal final assessment.",
   "Les experts ne sont pas d'accord, les politiques non plus : [[en définitive]], c'est au citoyen de décider."),
  ("somme toute", "All in all: formal, slightly literary summing-up.",
   "Quelques retards, un hôtel moyen, mais, [[somme toute]], un séjour réussi."),
  ("en somme", "In short, all in all: sums up what has been said.",
   "Il est poli, travailleur et ponctuel : [[en somme]], le stagiaire idéal."),
  ("bref", "In short, anyway: informal summing-up; good in a message, too casual for a formal essay.",
   "Le train était en retard, il pleuvait, j'ai perdu mes clés… [[bref]], une journée horrible !"),
  ("en tout cas", "In any case, anyway: moves on to what matters most.",
   "Je ne sais pas encore si je pourrai venir. [[en tout cas]], je t'appelle demain."),
  ("sinon", "Otherwise, alternatively: proposes another option.",
   "On pourrait aller au cinéma ; [[sinon]], on reste à la maison et on commande une pizza."),
  )

# groups whose connectors make clearly wrong distractors for a given group
INCOMPAT = {
    "ordre": ["cause", "opposition", "reformulation"],
    "ajout": ["opposition", "conclusion", "cause"],
    "exemple": ["opposition", "conclusion", "conséquence"],
    "cause": ["conséquence", "opposition", "conclusion"],
    "conséquence": ["cause", "opposition", "concession"],
    "but": ["cause", "opposition"],
    "opposition": ["ajout", "conséquence", "cause"],
    "concession": ["cause", "conséquence", "ajout"],
    "insistance": ["opposition", "conclusion", "conséquence"],
    "opinion": ["conséquence", "opposition", "cause"],
    "reformulation": ["opposition", "cause", "ordre"],
    "conclusion": ["ordre", "cause", "ajout"],
}
# hand-picked confusable pairs used as the first distractor when available
CONFUSE = {
    "grâce à": "à cause de", "à cause de": "grâce à", "bien que": "alors que", "alors que": "bien que",
    "car": "donc", "donc": "car", "en effet": "en revanche", "en revanche": "en effet", "puisque": "bien que",
    "d'autre part": "en revanche", "cependant": "c'est pourquoi", "pourtant": "donc", "malgré": "grâce à",
    "afin de": "à cause de", "c'est pourquoi": "en effet", "au contraire": "par exemple",
    "d'ailleurs": "pourtant", "par ailleurs": "par conséquent",
}

TEXTS = [
    dict(task="Tâche 1 · message à un ami", consigne=(
        "Vous venez d'emménager dans une nouvelle ville. Écrivez un message à un(e) ami(e) pour lui décrire "
        "votre nouveau quartier et l'inviter à venir vous voir. (60 à 120 mots)"), text="""Salut Camille,
Ça y est, je suis enfin installée à Lyon ! [[comme]] tu le sais, j'avais un peu peur de quitter Paris. [[pourtant|malgré tout]], je ne regrette rien. Mon quartier, la Croix-Rousse, est calme et très vivant à la fois. Il y a un marché tous les matins et, [[en plus|de plus]], les loyers sont moins chers qu'à Paris. [[par contre|en revanche]], il faut monter beaucoup d'escaliers ! [[d'ailleurs]], c'est devenu mon nouveau sport. J'ai une chambre d'amis, tu peux [[donc]] venir quand tu veux et rester aussi longtemps que tu le souhaites. [[bref|en tout cas]], j'attends ta visite avec impatience !
Bises,
Léa"""),
    dict(task="Tâche 1 · réponse à une invitation", consigne=(
        "Un ami vous propose de partir en vacances avec lui en juillet, mais vous ne pouvez pas. Répondez-lui "
        "pour refuser, expliquer pourquoi et proposer une autre solution. (60 à 120 mots)"), text="""Coucou Hugo,
Merci pour ton message, ton projet de road trip en Bretagne me tente beaucoup ! [[malheureusement]], je ne vais pas pouvoir venir en juillet. [[en effet]], je commence un nouveau travail le premier juillet et je n'aurai pas de congés avant la fin de l'été. [[du coup|donc]], je me demandais si on pourrait décaler le voyage en septembre : il y aura moins de monde sur les routes et les prix seront plus bas. [[sinon]], on pourrait faire un week-end prolongé à la Toussaint. [[en tout cas]], je ne veux pas rater ça ! Dis-moi ce que tu en penses.
À bientôt,
Sam"""),
    dict(task="Tâche 2 · article de blog", consigne=(
        "Vous écrivez un article pour le blog de votre quartier : racontez une initiative écologique à laquelle "
        "vous avez participé et dites ce que vous en avez retiré. (120 à 150 mots)"), text="""Le mois dernier, j'ai participé à la première « journée zéro déchet » organisée par l'association de mon quartier. [[tout d'abord]], nous avons ramassé les déchets dans le parc et le long du canal : en trois heures, nous avons rempli plus de quarante sacs ! [[ensuite|puis]], des bénévoles nous ont appris à fabriquer nos propres produits ménagers, [[notamment]] une lessive à base de savon de Marseille.
J'avoue que j'étais un peu sceptique. [[pourtant|cependant]], l'ambiance m'a surpris : plus de soixante habitants de tous âges étaient présents. [[il faut souligner que|il convient de rappeler que]] la mairie avait prêté le matériel gratuitement, ce qui a beaucoup aidé.
[[en fin de compte|finalement|en définitive]], cette journée m'a montré que de petits gestes collectifs peuvent changer le visage d'un quartier. [[c'est pourquoi]] je vous invite à nous rejoindre lors de la prochaine édition, en juin !"""),
    dict(task="Tâche 2 · article pour un magazine", consigne=(
        "Vous avez testé le télétravail pendant un an. Écrivez un article pour le magazine de votre entreprise "
        "pour présenter votre expérience, avec ses avantages et ses inconvénients. (120 à 150 mots)"), text="""Depuis un an, je travaille de chez moi trois jours par semaine, et le bilan est plutôt positif. [[d'une part]], je gagne près de deux heures par jour en évitant les transports. [[d'autre part]], je suis beaucoup plus concentré sans les interruptions de l'open space. [[de plus|en outre|par ailleurs]], mes dépenses ont nettement baissé : plus de déjeuners au restaurant ni de cafés à emporter.
[[cependant|toutefois|néanmoins]], tout n'est pas parfait. Les échanges informels avec mes collègues me manquent, et il m'arrive de me sentir isolé. [[par ailleurs|de plus|en outre]], la frontière entre vie professionnelle et vie privée devient floue : j'ai parfois du mal à éteindre mon ordinateur le soir.
[[somme toute|en définitive|en fin de compte|en somme]], le télétravail me convient, à condition de garder au moins deux jours au bureau pour préserver le lien avec l'équipe."""),
    dict(task="Tâche 2 · courrier des lecteurs", consigne=(
        "Vous écrivez au courrier des lecteurs d'un journal local pour réagir à la fermeture annoncée de la "
        "bibliothèque de votre ville. (120 à 150 mots)"), text="""Madame, Monsieur,
J'ai appris avec tristesse la fermeture prochaine de la bibliothèque municipale, et je tiens à exprimer mon désaccord. [[certes|il est vrai que]], la ville doit faire des économies, mais la culture ne devrait pas être la première sacrifiée. [[en effet]], la bibliothèque n'est pas seulement un lieu de prêt de livres : c'est un espace de rencontre, [[notamment|surtout]] pour les personnes âgées et pour les étudiants qui n'ont pas de lieu calme pour travailler. [[de plus|en outre|par ailleurs]], les animations pour enfants y attirent chaque samedi des dizaines de familles. [[à mon avis|personnellement]], d'autres solutions existent : réduire les horaires d'ouverture ou faire appel à des bénévoles, [[par exemple]]. [[c'est pourquoi]] je demande au conseil municipal de revenir sur sa décision.
Veuillez agréer, Madame, Monsieur, mes salutations distinguées."""),
    dict(task="Tâche 2 · récit sur un blog", consigne=(
        "Racontez sur votre blog un voyage qui ne s'est pas passé comme prévu, et dites ce que vous en avez "
        "retenu. (120 à 150 mots)"), text="""L'été dernier, j'avais tout organisé pour mon voyage en Écosse : billets, hôtels, itinéraire. [[pourtant]], rien ne s'est passé comme prévu ! Le jour du départ, mon vol a été annulé [[à cause de|en raison de]] la grève des contrôleurs aériens. J'ai [[donc|ainsi]] dû prendre le train jusqu'à Londres, puis un bus de nuit jusqu'à Édimbourg. [[alors que]] j'avais imaginé un voyage reposant, je me suis retrouvé à courir d'une gare à l'autre !
[[malgré]] la fatigue, j'ai adoré la ville dès le premier soir. [[grâce à]] ce détour imprévu, j'ai rencontré deux voyageurs avec qui je suis toujours en contact. [[finalement|en fin de compte]], ce voyage raté reste l'un de mes meilleurs souvenirs : il m'a appris qu'on ne peut pas tout contrôler, et que ce n'est pas grave."""),
    dict(task="Tâche 2 · témoignage", consigne=(
        "Vous avez arrêté d'utiliser les réseaux sociaux pendant un mois. Racontez votre expérience sur votre "
        "blog. (120 à 150 mots)"), text="""Il y a un mois, j'ai décidé de supprimer toutes les applications de réseaux sociaux de mon téléphone. [[au début]], c'était difficile : je prenais mon téléphone par réflexe toutes les cinq minutes. [[puis|ensuite]], peu à peu, ce réflexe a disparu, [[si bien que]] je ne pensais presque plus à mes comptes au bout de deux semaines.
J'ai [[ainsi|donc]] retrouvé du temps pour lire et pour voir mes amis en vrai. [[qui plus est|de plus|en outre|en plus]], je dors beaucoup mieux depuis que je ne regarde plus d'écran avant de me coucher. [[il est vrai que|certes]] je me suis parfois senti exclu de certaines conversations entre amis, qui se déroulaient en ligne. [[malgré tout|néanmoins]], je ne regrette pas cette pause. [[désormais]], je compte limiter mon usage à vingt minutes par jour."""),
    dict(task="Tâche 3 · deux points de vue", consigne=(
        "Document 1 — Pour une ville sans voitures : les centres-villes devraient être réservés aux piétons, "
        "aux vélos et aux transports en commun, pour réduire la pollution et le bruit.\n"
        "Document 2 — Les commerçants inquiets : selon eux, interdire les voitures ferait fuir les clients vers "
        "les centres commerciaux de périphérie.\n"
        "Résumez les deux points de vue (40 à 60 mots), puis donnez votre opinion (80 à 120 mots)."), text="""Les deux documents s'intéressent à la place de la voiture en centre-ville. [[selon]] le premier, il faudrait la bannir pour réduire la pollution et le bruit. Les commerçants, [[en revanche|quant à eux]], craignent qu'une telle mesure ne fasse fuir leurs clients vers la périphérie.
[[personnellement|pour ma part|à mon avis]], je suis favorable aux centres-villes piétons. [[en effet]], la pollution de l'air provoque chaque année des milliers de décès prématurés, et le bruit nuit à notre santé. [[il faut souligner que|il convient de rappeler que]] plusieurs villes qui ont fait ce choix, comme Pontevedra en Espagne, sont devenues plus attractives. [[certes|il est vrai que]], la transition demande des efforts : il faut créer des parkings relais et des transports en commun efficaces. [[néanmoins|toutefois|cependant]], ces investissements profitent à tous. [[en définitive|en fin de compte|en conclusion]], une ville sans voitures n'est pas une ville morte, mais une ville plus agréable à vivre."""),
    dict(task="Tâche 3 · deux points de vue", consigne=(
        "Document 1 — Le livre papier résiste : les lecteurs restent attachés à l'objet et au plaisir de tourner "
        "les pages ; de plus, lire sur écran fatigue les yeux.\n"
        "Document 2 — La liseuse, une révolution : légère et économique à l'usage, elle permet d'emporter des "
        "centaines de livres partout.\n"
        "Résumez les deux points de vue (40 à 60 mots), puis donnez votre opinion (80 à 120 mots)."), text="""Ces deux documents comparent le livre papier et la liseuse électronique. Le premier affirme que les lecteurs restent attachés à l'objet, [[d'autant plus que]] la lecture sur écran fatigue les yeux. Le second, [[au contraire|en revanche]], présente la liseuse comme une révolution : légère et économique, elle permet d'emporter toute une bibliothèque.
[[à mon avis|personnellement|pour ma part]], ces deux supports ne s'opposent pas. [[d'un côté]], la liseuse est idéale en voyage ou pour lire la presse. [[de l'autre]], rien ne remplace le plaisir d'offrir un beau livre ou de le prêter à un ami. [[il convient de rappeler que|il faut souligner que]] la liseuse a aussi un coût écologique : sa fabrication nécessite des métaux rares, et elle n'est rentable pour la planète qu'après un grand nombre de livres lus. [[autrement dit]], elle n'a de sens que pour les grands lecteurs. [[pour conclure|en conclusion]], chacun devrait choisir selon ses habitudes, sans opposer l'ancien et le nouveau."""),
    dict(task="Tâche 3 · deux points de vue", consigne=(
        "Document 1 — Un service civique pour tous : certains proposent que chaque jeune de 18 ans consacre six "
        "mois à une mission d'intérêt général, pour renforcer la cohésion sociale.\n"
        "Document 2 — Une contrainte inutile : pour d'autres, l'engagement doit rester volontaire ; l'imposer "
        "coûterait cher et démotiverait les jeunes.\n"
        "Résumez les deux points de vue (40 à 60 mots), puis donnez votre opinion (80 à 120 mots)."), text="""Le premier document défend l'idée d'un service civique obligatoire pour tous les jeunes de dix-huit ans, [[afin de]] renforcer la cohésion sociale. Le second estime [[au contraire|en revanche]] qu'un engagement imposé perd son sens et coûterait cher à l'État.
[[pour ma part|personnellement]], je partage plutôt le second point de vue. [[tout d'abord]], obliger quelqu'un à s'engager me paraît contradictoire : l'engagement suppose un choix. [[ensuite]], organiser des missions pour des centaines de milliers de jeunes chaque année représenterait un coût énorme, [[alors que]] les associations manquent déjà de moyens pour encadrer les volontaires actuels. [[toutefois|cependant|néanmoins]], je reconnais que le service civique peut être une expérience très formatrice. [[c'est pourquoi|par conséquent]] je proposerais plutôt de mieux le faire connaître et de le valoriser dans les études ou sur le CV. [[en somme|bref|en définitive]] : encourager plutôt qu'obliger."""),
]

G.setdefault("quant à eux", dict(group="opposition", x="As for them: shifts to another person or group, often to contrast their view.",
                                 phrase="Les parents sont favorables à la réforme ; les enseignants, [[quant à eux]], restent sceptiques."))

# hand-picked wrong options where the automatic choice could also have been right
OVERRIDE = {
    "de l'autre": ["autrement dit", "par conséquent", "par exemple"],
    "néanmoins": ["en effet", "par conséquent", "d'autant plus que"],
    "au contraire": ["pourtant", "grâce à", "en revanche"],
    "malheureusement": ["c'est pourquoi", "comme", "par exemple"],
    "en définitive": ["d'un côté", "d'une part", "tout d'abord"],
    "pour conclure": ["tout d'abord", "d'une part", "au début"],
    "personnellement": ["en raison de", "malgré", "car"],
    "à mon avis": ["quant à eux", "malgré", "car"],
    "pour ma part": ["puisque", "comme", "c'est-à-dire"],
    "désormais": ["à cause de", "par contre", "pourtant"],
    "finalement": ["comme", "quant à eux", "d'une part"],
    "somme toute": ["étant donné que", "d'autant plus que", "par exemple"],
    "cependant": ["c'est pourquoi", "grâce à", "par exemple"],
    "il convient de rappeler que": ["bien que", "malgré", "quant à eux"],
    "il faut souligner que": ["bien que", "malgré", "quant à eux"],
}

BLANK = re.compile(r"\[\[([^\]]+)\]\]")


def capital_slot(text, pos):
    before = text[:pos].rstrip(" ")
    return before == "" or before[-1] in ".!?\n:" and not before.endswith(" :") and before[-1] != ":"


def parse(text, item_id, extra_bank=0, rng=None):
    parts, pos, keys = [], 0, []
    for m in BLANK.finditer(text):
        if m.start() > pos:
            parts.append(text[pos:m.start()])
        options = m.group(1).split("|")
        key = options[0]
        surface = key
        if key == "bien qu'":
            key = "bien que"
        if key not in G:
            raise SystemExit(f"{item_id}: unknown connector {key!r}")
        cap = capital_slot(text, m.start())
        alts = [a for a in options[1:]]
        for a in alts:
            if a not in G:
                raise SystemExit(f"{item_id}: unknown alternative {a!r}")
        parts.append(dict(a=surface, alt=alts, x=G[key]["x"], k=key, cap=cap, t="all"))
        keys.append(key)
        pos = m.end()
    if pos < len(text):
        parts.append(text[pos:])
    return parts, keys


def main():
    rng = random.Random(8)
    textes = []
    for i, t in enumerate(TEXTS, 1):
        parts, keys = parse(t["text"], i)
        accepted = {k for p in parts if isinstance(p, dict) for k in [p["k"], *p["alt"]]}
        # distractors that need a noun, infinitive or subordinate clause, so they cannot stand in for an adverb
        pool = [k for k in ("grâce à", "à cause de", "en raison de", "malgré", "afin de", "bien que",
                            "étant donné que", "si bien que", "d'autant plus que", "selon")
                if k not in accepted]
        bank = rng.sample(sorted(pool), 2)
        textes.append(dict(id=f"t{i}", head=t["task"], ctx=t["consigne"], layout="bank", bank=bank, p=parts))
    phrases = []
    for key, v in G.items():
        parts, _ = parse(v["phrase"], key)
        b = next(p for p in parts if isinstance(p, dict))
        wrong = list(OVERRIDE.get(key, []))
        conf = None if wrong else CONFUSE.get(key)
        if conf:
            wrong.append(conf)
        pool = sorted(k for k, w in G.items() if w["group"] in INCOMPAT[v["group"]] and k not in wrong and k != key)
        wrong += rng.sample(pool, 3 - len(wrong))
        if b["cap"]:
            b["a"] = b["a"][0].upper() + b["a"][1:]
            wrong = [w[0].upper() + w[1:] for w in wrong]
        b["o"] = wrong
        b.pop("alt", None)
        b.pop("cap", None)
        phrases.append(dict(id="p-" + key, layout="list", p=parts))
    write_json(DATA / "connecteurs-textes.json", textes)
    write_json(DATA / "connecteurs-phrases.json", phrases)
    print("connectors:", len(G), "text blanks:", sum(len([p for p in t["p"] if isinstance(p, dict)]) for t in textes))
    unused = sorted(k for k in G if not any(isinstance(p, dict) and p["k"] == k for t in textes for p in t["p"]))
    print("only in phrases:", unused)


if __name__ == "__main__":
    main()
