# RUN-020 — Recette humaine N1–4

Branche : `feature/run-020-021-campaign`. RUN-020 est VERIFY après la reprise Claude et la recette Codex du 6 octobre. Les points acceptés et refusés du premier playtest sont dans [la review](RUN-020_PLAYTEST_REVIEW.md), les scènes finales dans [le manifeste de reprise](RUN-020_ASSET_MANIFEST_02.md). La validation humaine des scènes finales reste nécessaire avant clôture et passage à RUN-021 sur cette branche.

## Parcours complet

Dans Godot4.7.2, ouvrir le projet puis **F5**. **New Game** remplace la progression active après confirmation (le précédent fichier est sauvegardé en backup) ; **Continue** la conserve. Partir de N1, accepter le Longbow gratuit puis avancer jusqu’à N4. Flèches : mouvement ; Space : saut/double saut ; A : changer d’arme ; F maintenu : attaquer ; E : interagir/confirmer ; Escape : pause. Menus : flèches et E.

| Niveau | Coins placés | Coût de sortie | Points à juger |
| --- | ---: | ---: | --- |
| N1 Eidolon Vale | 18 | 12 | terrain existant, raccord vers N2 |
| N2 Blight Town | 24 | 18 | Red/Bloated, piques rétractables, trappe, première montée de difficulté |
| N3 Black Forest | 32 | 25 | Warrior/Archer, plante/tourelle, rythme combat/plateforme |
| N4 Forbidden Graveyard | 40 | 32 | Sorcerer/Chud, swarm4, secret, porte optionnelle et mécanisme obligatoire |

Les scènes sont aussi accessibles directement : ouvrir `scenes/blight_town.tscn`, `scenes/black_forrest.tscn` ou `scenes/forbidden_graveyard.tscn`, puis **F6**. Elles utilisent l’équipement et les flags de la sauvegarde actuelle ; F6 ne donne pas gratuitement le Longbow ni des shards. Ce raccourci permet de rencontrer réellement les nouveaux ennemis sans refaire N1.

## Repères des scènes finales

Coordonnées monde ; y indique les pieds du chevalier. Chaque niveau présente deux fourches : essayer une route haute puis une route basse, et revenir explorer la route laissée de côté. Un seul chemin par fourche suffit au budget prévu ; ne pas compter sur les récompenses des coffres ou des ennemis pour payer la grille. Les budgets ci-dessous sont ceux du manifeste de level design : vérifier leur collecte au clavier pendant ce playtest. Les collectes isolées du test campagne ne prouvent pas ce parcours.

| Niveau | Première fourche | Passage central | Deuxième fourche | Sortie et budget d’un passage simple |
| --- | --- | --- | --- | --- |
| N2 | Tour (1032,112) : remparts y48–96, ou canal y240 et coffre (1232,240) | Trappe x1728 ; caisses puis toit de halle y64, passage obligatoire | Terrasse (2472,112) : chaussée y48 et potion (2976,48), ou ruelle y176 et trappe x2944 | Bloated x3456 ; grille (3696,144), 20–21 pièces pour coût 18 |
| N3 | Tronc (1224,112) : canopée jusqu’à y16 et Archer x1704, ou sous-bois y176 et coffre (1536,176) | Shield (2176,144) ; ravin sur souches (2288,128), (2368,96), (2448,112) ; tourelle vers l’ouest x2678 | Éperon (2744,96) : couronnes jusqu’à potion (3248,−48), ou ravine y240 et trappe x3088 | Archer sur butte y112 ; grille (4176,144), 27 pièces pour coût 25 |
| N4 | Chapelle y48 et porte payante x1544, ou crypte y240 avec coffre (1824,240) | Shield (2048,144) ; swarm autour de (2368,48), crypte surélevée y96 | Surface y144 et mausolée y80, ou catacombe y240 puis corniche (3520,192) | Clocher et bouton (4048,0), porte x4168, Chud x4480 ; grille (4656,144), 36 pièces pour coût 32 plus porte optionnelle 4 |

Les totaux avec retour sur les deux fourches restent 24/32/40 pièces. Tester particulièrement les doubles sauts de 64 px : halle N2, toit de salle HP N4 et mausolée de la seconde fourche N4. N3 contient un trou mortel de 48 px x832–880 et un ravin à franchir par les souches. Vérifier que le terrain et les dangers annoncent ces passages sans imposer un saut mural.

## Exploration N4

- Monter par la marche (376,112) puis le toit du mausolée (472,64). Frapper/tirer vers le mur secret (568,64) ; potion majeure (640,64 sous les pieds) et rare chest (704,64) derrière. Le secret reste révélé après mort/reprise.
- Première fourche haute : marches (1120,96), (1248,64), chapelle y48. E devant la porte (1544,48) dépense 4 coins ; bonus HP derrière (1640,48), +1 HP actuel et maximum durable. Continuer par le toit y−16 avec un double saut de 64 px. Le passage simple finance cette porte et la sortie sans coffre ni secret.
- Sur le clocher, monter (3808,96) → (3920,48) → bouton (4048,0), puis E. Redescendre vers la porte mécanique (4168,144). Vérifier qu’elle ferme réellement la sortie tant que le bouton reste inactif ; elle ne peut pas être achetée.
- La swarm de zone possède quatre emplacements par tentative, indépendamment du Sorcerer. Sortir puis revenir : seuls les survivants reviennent ; une swarm entièrement vaincue reste vide. Mort/Restart réarme les quatre.
- Mort/Restart : coins, portes, mécanismes, buffs et gains non déposés repartent à zéro ; équipement, banque, secret et HP acquis restent. Tester aussi Continue après fermeture du jeu. La sortie N4 termine ce segment, sans niveau 5.

## Retour attendu

Indiquer les passages trop difficiles/faciles, les temps morts, la lisibilité des attaques/pièges/objets et le confort des sauts. Écouter les trois ambiances avec musique/SFX (volume, timbre, boucle). La musique Dreamer est actuellement partagée par N2–4 ; le choix musical N4 reste un point de la passe visuelle suivante.

La recette automatique et les captures natives sont consignées dans `runs-journal.md`. Elles ne remplacent pas ce playtest. Une validation explicite de RUN-020 permettra sa revue de clôture puis le lancement de RUN-021.

## Retest après correctifs techniques

Vérifier l’aggro plus large et sa perte après2s, la swarm nettoyée qui reste vide malgré sortie/réentrée, le tir plus court/lent et le Shield contre piques/plantes/tourelles (vide mortel). Les scènes et les deux élites reprises sont livrées dans [le manifeste](RUN-020_ASSET_MANIFEST_02.md). Les volumes des élites et le premier plan du chevalier ont été corrigés après la remise Claude. Juger Bloated et Chud au contact : taille, télégraphie, espace de réaction et visibilité du chevalier. Le passage inférieur du mausolée N4 a reçu une ouverture locale au bout de la marche ouest ; vérifier la descente depuis (376,112) vers le chemin y144. Leurs populations fixes sont désormais 10/13/14 ennemis, avec 10/11/10 pièges ; apprécier la difficulté graduelle et les espaces de tir face aux Archers. Mesurer le temps de chaque niveau, préciser les routes choisies et signaler un éventuel raccourci dominant.

Retour nécessaire : acceptation explicite des parcours et de leur variété, du confort des sauts, des nouveaux visuels et de la lisibilité au contact des élites ; ou liste des passages à reprendre avec niveau/repère et symptôme. La recette automatique établit des preuves techniques ; ces jugements humains conditionnent encore la clôture de RUN-020 et l’éligibilité à RUN-021.
