# Milady's Knight — Roadmap de production

## Statut de cette planification

Audit documentaire et inspection du dépôt effectués le **21 septembre 2026**, à partir de l’état de travail courant, et non du seul commit `0870462`.
**RUN-001 VERIFY : contrôles automatisés, F5, fermeture manuelle et revue finale satisfaits ; intégration par PR en attente. RUN-002 démarre par l’inventaire des assets.** Travail sur `feature/run-001-engine-import`, créée depuis `develop` au commit `04f1f05`. RUN-003 à RUN-011 restent `BACKLOG` ; les versions suivantes seront affinées après chaque jalon. Le push, la PR et le merge attendent leur autorisation distincte.

La cible finale validée est **0.9.0 beta**, une démo de dix niveaux conçus à la main. `0.1.0` est un premier jalon technique de production, pas une étiquette affirmant que le dépôt actuel satisfait déjà les nouvelles règles. Les numéros sont des cibles validées ; des patchs `0.x.1`, etc., pourront contenir des corrections vérifiées sans renommer arbitrairement les runs.

Ce plan couvre les spécifications de `docs/00` à `docs/13`, y compris art, audio, narration et livraison. Les durées de travail ne sont pas estimées. L’objectif de 1–2 heures de jeu reste à mesurer. Le nombre futur de runs est une enveloppe de planification révisable, pas une promesse de calendrier ni une réduction du scope produit.

## Audit vérifié de la base

### Moteur, réglages et changements humains

- `project.godot` déclare `4.7` et `GL Compatibility`. L’exécutable Windows associé dans les métadonnées locales répond **4.7.2.stable.official.ed1daf0bf** ; le runtime Linux disponible répond **4.5.1.stable.official.f62fdbde1**. Les lanceurs ciblent encore 4.5.1, et le chemin Windows par défaut ne correspond pas au binaire 4.7.2 disponible. Il faut stabiliser ces références ; aucun retour forcé à 4.5 n’est proposé.
- Réglages actuels : identifiant `miladys_knight`, démarrage `scenes/game.tscn`, viewport **320×180**, fenêtre 1280×720, stretch `viewport`/`integer`, filtrage nearest, pixel snapping des transforms 2D, fond sombre. Aucun preset d’export, addon ou bus audio personnalisé trouvé dans les fichiers du projet. Les scripts utilisent leur propre gravité ; pas de réglage physique de production supplémentaire déclaré dans `project.godot`.
- Les modifications préexistantes de `project.godot` portent notamment sur la version déclarée, une option de compatibilité d’animation et la sérialisation des touches. `assets/kingdom_tileset.tres` possède des UID ajoutés. Elles ont été préservées. Les anciens documents à la racine de `docs/` étaient déjà supprimés du working tree ; les nouvelles spécifications, AGENTS/brief/workflow/journal/learning étaient non suivis par Git. Ce statut Git ne les rend pas moins légitimes.

### Structure et responsabilités réelles

| Fichier / scène | Responsabilité observée |
| --- | --- |
| `scenes/game.tscn`, `scripts/game.gd` | Charge la scène mémorisée par Progression, avec repli sur le slice ; aucun menu principal. |
| `scripts/progression.gd` — unique autoload `Progression` | Banque de bonus et chemin de reprise ; JSON v1 `user://progress.json`, fichier temporaire puis remplacement, protection contre fichier corrompu/version inconnue. |
| `scenes/vertical_slice.tscn`, `scripts/level.gd` | Une scène de jeu ; raccorde signaux, coins/bonus, offrande, sortie, pause, overlays, musique et caméra. Couplages aux noms de nodes et à des coordonnées précises. |
| `scenes/player.tscn`, `scripts/player.gd` | CharacterBody2D, états sol/air/wall slide/mort, déplacements, épée, santé et réactions ; Camera2D enfant. |
| `scenes/slime.tscn`, `scripts/slime.gd` | Patrouille avec détection de bord, variantes Green/Purple, contact, santé, recul/stagger et signal de récompense. |
| `scenes/coin.tscn`, `scripts/coin.gd` | Ramassage unique ; même scène utilisée comme feedback non ramassable de bonus de kill. |
| `scenes/gold_gate.tscn`, `scripts/gold_gate.gd` | Barrière de 12 coins, zone E, ouverture animée et signal d’offrande. |
| `scenes/hazard.tscn`, `scripts/hazard.gd` | Ronces dessinées par code, Area2D de dégâts ; option lethal pour la fosse. |
| `scenes/moving_platform.tscn`, `scripts/moving_platform.gd` | Bac AnimatableBody2D, déplacement sinusoïdal, collision unidirectionnelle. |
| `scenes/hud.tscn`, `scripts/hud.gd` | CanvasLayer, labels VIE/SCEAU/BONUS, hints et overlay pause/mort/victoire ; textes français. |
| `scripts/kingdom.gd`, `scripts/terrain_skin.gd` | Décor et habillage des tuiles dessinés par `_draw()`, avec positions/couleurs du slice. Pas de système de biomes/parallax dynamique. |
| `tests/` | 11 suites lancées par `tools/test.sh`, pilote de parcours, scénarios de rendu/capture ; `fixtures/next_level.tscn` hérite du slice pour tester une transition, ce n’est pas un niveau 2. |
| `tools/` | Lanceurs, tests et générateurs d’auteur ; `build_player.py`, `build_scenes.py`, `build_level.gd`, `configure_inputs.py` écrivent des scènes/ressources/réglages. Ne pas les rejouer sur les changements humains par défaut. |

Inventaire : **9 scènes dans `scenes/`, 12 scripts de jeu**, plus la fixture et les tests. Le TileSet utilisé par `Terrain` est **embarqué dans `vertical_slice.tscn`** ; aucune référence depuis les scènes/scripts de jeu à `assets/kingdom_tileset.tres` n’a été trouvée. Modifier ce fichier externe ne prouve donc pas que le niveau utilisera les nouvelles tuiles. Cela justifie un contrôle de référence, pas sa suppression.

### Input Map actuel

| Action | Touche actuelle | Écart avec la cible |
| --- | --- | --- |
| `move_left` / `move_right` | Q / D | Cible flèches gauche/droite. |
| `move_up` / `move_down` | Z / S | Déclarées sans grimpe ; cible flèches haut/bas. |
| `jump` | Space | Saut/double saut ; pas encore de skip narratif. |
| `attack` | F | `is_action_just_pressed`, pas de cadence en maintien. |
| `interact` | E | Porte et bilan de fin seulement. |
| `restart` | R | Conflit futur avec la capacité Dragon Slayer ; reset à déplacer dans le menu. |
| `pause` | Escape | Bascule pause simple ; pas de menu à trois choix. |
| — | A / G | Aucune action équipement/attaque d’atterrissage déclarée. |

### Layers / masks de collision actuels

Les numéros de couches et leurs valeurs binaires sont distincts : terrain = couche 1/valeur **1**, joueur = couche 2/**2**, ennemis = couche 3/**4**, grippable = couche 4/**8**.

| Élément | Layer | Mask / requête |
| --- | --- | --- |
| Terrain TileSet embarqué | 9 = terrain + grippable | Collisions de tiles 16×16. |
| Joueur | 2 | 1, terrain ; capsule 10×18, pieds à l’origine. |
| Slime | 4 | 1, terrain ; corps 14×12. |
| Contact Slime | 0 | 2, joueur ; volume 12×10. |
| Épée | 0 | 4, ennemis ; rectangle 22×4 interrogé explicitement (`monitoring=false`). Rayon d’occlusion contre terrain 1. |
| Sondes murales joueur | — | 8 uniquement, exclut les surfaces lisses. |
| Coins, ronces, fosse, zone d’offrande, sortie | 0 | 2, joueur. |
| Bac | 1 | 0 ; forme 34×6 unidirectionnelle. |
| Barrière et limites extérieures | 1 | Mask non surchargé dans leur scène ; pas de grippable. |

Les ronces actuelles sont des Area2D traversables, pas les piques/plantes solides décrits pour la démo. Elles infligent 1 HP ; un nouveau profil de piège doit respecter sa propre spécification.

### Niveau réellement présent

- Spawn `(48,140)`, terrain en `TileMapLayer` sur grille 16 ; largeur bornée de 0 à 2240. Caméra : limites gauche/droite 0/2240, haut/bas −224/304, offset `(32,-38)`, smoothing 7 ; levée locale à −54 dans le passage mural.
- Village commun, bifurcation haute/basse, réunion vers zone corrompue et porte à `(2072,144)`, sortie centrée `(2160,96)`.
- **18 coins** : 8 communs, 5 hauts, 5 bas. **8 Slimes** : 5 Green et 3 Purple. Deux ronces, une fosse et un bac à `(816,51)`, course 144 px/période 4 s. Branche haute avec escalade, double saut et bac ; branche basse orientée combat.
- Ce tracé peut amorcer N1. Il n’est pas encore The Eidolon Vale conforme : ni Spirit, ni coffre Longbow, ni potion, ni tutoriel modal. Son adaptation doit préserver les éléments utiles, sans régénération globale ni réintégration aveugle d’un ancien état.

### Systèmes complets pour le slice, partiels pour la démo, absents

| État | Constats dans les fichiers et tests |
| --- | --- |
| Fonctionnels pour les règles du slice | Marche avec accélération, saut variable, coyote/buffer, double saut, wall slide/jump, bac, épée aérienne avec hit unique et occlusion, patrouilles Slime, collecte/offrande/sortie, santé/mort/reset manuel, pause et sauvegarde de bonus. |
| Écarts de règles à traiter | Joueur 3 HP entiers ; épée 1 DMG, animation 0,32 s par pression. Green/Purple 3/4 HP, contact 1 DMG. Slime inoffensif pendant stagger 0,12 s. Réaction joueur uniforme, saut/attaque pas effectivement bloqués pendant tout recul/hit-stun. Le surplus de coins devient bonus ; ce bonus combine exploration et kills, contrairement aux shards cibles. |
| Partiels | Progression : banque et scène uniquement, pas équipement/uniques. UI : texte français et positions 320×180, pas cœurs fractionnaires/slots. Audio : quelques sons et une musique, pas de mix par bus. Caméra/décor/seuil de chute global `y>340` liés au slice. |
| Absents | Tir/équipement/upgrades/coffres, attaque d’atterrissage et capacités, grimpe, consommables, HP bonus/paliers/offrandes permanentes, secrets et portes secondaires, autres pièges, Red/avancés/élites/Boss, PNJ/dialogues, menu principal/pause complet/Controls, contenu N2–10, exports. |

La règle actuelle « wall jump interdit le double saut jusqu’au sol » et les paramètres de mobilité ont des tests. Leur absence de détail dans la nouvelle spec n’autorise pas à les supprimer ; les conserver comme référence et réévaluer par playtest.

### Assets et limites de présentation

- 6 PNG présents : `knight` 256×256 (frames 32×32), `slime_green`/`slime_purple` 96×72 (frames 24×24), `coin` 192×16, `world_tileset` 256×256, `platforms` 64×64. `platforms.png` n’est pas référencé par les scènes/scripts de jeu inspectés.
- 4 WAV utilisés : jump, hurt, coin, tap ; 1 OGG bouclé `time_for_adventure` ; 1 police `PixelOperator8.ttf`. Ces 12 médias et le TileSet font **13 fichiers d’assets hors `.import`**. Les scènes audio emploient des AudioStreamPlayer non positionnels, sans bus spécifique déclaré.
- Le sprite joueur dispose d’animations idle/run/jump/dead. Épée, effets et une grande part du monde sont dessinés en code. Aucun ensemble complet d’animations Ashen Knight, élites, Boss ou PNJ final n’est présent.
- Aucun fichier de licence/attribution des médias trouvé dans le dépôt inspecté. L’ancien README reconnaissait déjà ce manque ; cette mention est conservée dans le nouveau README. Les listes d’assets candidats/téléchargés de `docs/11` ne prouvent pas leur présence dans ce dépôt. Aucun achat ni téléchargement effectué pendant l’audit.
- Les wireframes `![[...png]]` cités par `docs/05` ne sont pas présents dans `docs/` ; leur rendu exact ne peut pas être audité à partir de ces fichiers. Les règles textuelles restent exploitables.

### Vérifications exécutées pendant l’audit

Des copies temporaires séparées ont été utilisées pour éviter que l’import change les fichiers de projet. Aucun générateur d’auteur n’a été exécuté. Les tests `--script` désactivent la vraie sauvegarde ; les tests disque emploient des noms temporaires dédiés.

| Contrôle | Résultat observé le 21 septembre 2026 |
| --- | --- |
| Références `res://` des scripts/scènes/ressources inspectés | Aucun fichier manquant parmi les références statiques relevées. |
| Import propre Linux 4.5.1 + `tools/test.sh` | **150 PASS**, 11 suites, code 0 ; aucune erreur/FAIL/fuite signalée dans leurs logs. |
| Import propre Windows natif 4.7.2 sur copie temporaire accessible via WSL/UNC | Code 0 **mais trois `ERROR: Condition "p_position > length" is true.`**, `core/io/file_access_memory.cpp:101`. Cause exacte : **Je ne sais pas.** Ni corruption de police ni défaut de version affirmés. À reproduire aussi sur chemin Windows local en RUN-001. |
| 11 suites Windows 4.7.2, lancées séparément après cet import | **150 PASS**, codes 0, aucune erreur/FAIL/fuite signalée dans ces logs de tests. Cela ne rend pas l’import exempt d’erreurs. |
| Gameplay graphique, écoute et playtest humain | **Non exécutés dans cette passe**. Les anciennes captures/mesures ne valent pas validation actuelle. |

Répartition par moteur : movement 6, physics 6, mobility 25, combat 18, platform 14, boundaries 6, keyboard 9, integration 23, bonus 39, routes 2, backtracking 2. Les parcours ont testé les deux branches et les retours avec la physique réelle. Certaines suites ciblées positionnent des fixtures ou appellent directement des méthodes ; ce ne sont pas toutes des parties humaines.

Preuves temporaires de cet audit : `/tmp/milady-audit-uplrztby/project/work/test-results/` et `/tmp/milady-audit-uplrztby/windows-logs/`. Ces chemins sont locaux et non durables ; les résultats utiles sont résumés ici car ce travail n’est pas une run de production. Les reproductions futures doivent être enregistrées dans `runs-journal.md` avec leur run.

Les quatre anciennes docs de `docs/old` ont été lues puis supprimées sur demande. Elles décrivaient les règles du slice, non le scope cible. `runs-journal.md` et `learning.md` restent inchangés pendant cette passe.

## Décisions à résoudre avant les runs dépendantes

Aucune valeur non définie ci-dessous n’est implicitement décidée par la roadmap. Un choix purement technique peut être documenté par la run après vérification ; une contradiction de règles ou un arbitrage produit doit être validé avec l’humain avant le code dépendant. Les exemples graphiques n’ajoutent pas de bestiaire aux niveaux.

| ID | Question concrète / source | Jalon qui doit la résoudre |
| --- | --- | --- |
| D01 | `01`/`04`/`05` : PV joueur affichés en demi-cœurs, dégâts Fire Gauntlet de 0,2 sur les ennemis : représentation numérique adaptée aux deux, sans inventer de dégâts joueur à 0,2 ; effet immédiat d’un bonus MAX HP sur CURRENT HP à préciser. | Santé en 0.1, bonus HP en 0.4. |
| D02 | `01`/`04` : RANGE en unités à relier aux tiles ; variation des stats selon armes/niveaux, ATK SPEED positif jusqu’au niveau 5 ; timings de hit-stun/recul et seuil/rayon du slam encore ouverts. | Sword en 0.1, tables en 0.3, slam en 0.5. |
| D03 | `03` : « sauvegarde uniquement au passage de niveau » versus équipement/uniques sauvés aussi après fermeture en plein niveau. Choisir les événements de sauvegarde durable et le snapshot de tentative. | Contrat de persistance 0.2 avant tout schéma. |
| D04 | `03`/`04` : ordre de dépense banque/gains, banque après dépense puis mort, base retenue à 20/50 %, croissance des prix/poids/drop soins, gains de swarm/invocations et farm possible, seconde offrande sans première. Migration de l’ancien bonus (qui inclut du surplus de coins) à décider, sans conversion silencieuse. | Contrat 0.2, tables 0.3, swarm 0.4, offrandes 0.5/0.6. |
| D05 | `01`/`05`/`10` : Escape ne doit pas ouvrir pause pendant coffre/contexte, mais doit pouvoir annuler/fermer ; priorité exacte des dialogues ; portée de « dialogue non rejouable » après mort/reload ; refus/reprise du coffre tuto, confirmation des actions permanentes et disposition des slots (horizontale dans `04`, verticale dans `05`). | Modales, dialogue et coffre N1 en 0.2. |
| D06 | `02`/`06` : aggro périmètre versus ligne de vue, poursuite/retour autour des bords, nombre de skulls et plafond d’invocations, devenir des invocations à la mort de la source. « niveau 5 et 9 » ambigu pour les profils Skeleton. Les variantes N2 de l’Art Bible sont des exemples, le bestiaire par niveau de `03` reste à respecter. | IA 0.3/0.4 puis profils et invocations 0.5/0.6. |
| D07 | `01`/`04` : restrictions de grimpe, accumulation/rafraîchissement de Shield et Rage, sort des cooldowns au changement d’arme/reset ; déclenchement de secrets par mêlée/tir/impact. | Secrets/buffs 0.4, grimpe/capacités 0.5. |
| D08 | `04` : durée/annulation de charge Dragon Slayer ; kills éligibles/compteur Obsidian ; portée/relief de Thunderstruck et « one shot n’importe quel mob » face au Boss. | Chaque Legendary 0.5 puis contrat Boss 0.7. |
| D09 | `02`/`09` : 3/5 DMG du Boss non attribués à chaque attaque ; accélération d’attaque enrage non chiffrée ; départ immédiat versus dialogue et spawn AFK sûr ; état de fin/Continue après Karla. | Contrat Boss 0.7, avant l’arène. |
| D10 | `06`/`11`/`13` : comparaison 16/32, gabarits/packs/licences, mapping final des skins et animations ; vocabulaire à harmoniser (Black Forrest/Forest, Ancien/Ancient, Fire/Dire Gauntlet). Plateformes distribuées, matériel et budget de performance non définis. | Échantillon 0.1, noms avant contenu, variantes 0.8, export 0.9. |

Autres garde-fous de scope : pas de génération procédurale, checkpoints intra-niveau, sélection de sauvegardes, remapping, support souris/manette ou exploration après Karla. Les offrandes ne doivent pas être confondues avec les paiements de portes. Aucun add-on ni grande réarchitecture n’est nécessaire par défaut.

## Règles d’exécution et de clôture

Les invariants, le routage du contexte, les outils, la délégation et les autorisations Git sont définis dans [AGENTS.md](AGENTS.md). Les repères documentaires de chaque version orientent vers les sources utiles ; ils ne prescrivent pas leur lecture intégrale à chaque run.

### Planification

- **Horizon de détail** : roadmap lointaine = objectifs, dépendances et critères de jalon ; prochaine version = runs détaillées ; run active = périmètre et preuve attendue très précis. Seule 0.1.0 est détaillée aujourd’hui. Les axes futurs ne sont pas des runs monolithiques à exécuter tels quels.
- **Réévaluation au jalon** : après la recette de chaque version, inspecter le nouvel état réel et les changements humains, puis détailler seulement la suivante à partir des spécifications pertinentes et des défauts observés. Fusionner les tâches qui partagent un résultat testable ; séparer celles qui ont des risques ou décisions indépendants. Mettre à jour l’enveloppe et les dépendances sans créer une run de planification supplémentaire par défaut.
- **Préparation de la run active** : préciser dans sa fiche les fichiers/systèmes réellement concernés, les limites du changement, les décisions requises et les scénarios de vérification. Cette précision repose sur l’inspection du moment, pas sur une architecture supposée des mois à l’avance.
- **Priorités** : P0 bloque un jalon ou protège les données ; P1 requis pour le résultat fonctionnel prévu ; P2 présentation/complément reportable dans l’ordre mais à traiter si exigé par les specs ; P3 polish conditionnel. Un report de feature requise hors de la démo exige une décision de scope explicite.
- **Ordre** : une seule run ACTIVE. Le tableau de versions donne l’ordre prévu ; les fiches détaillées ajoutent les dépendances techniques utiles. Chaque version commence après la recette de la précédente. Les dépendances implicites de version s’ajoutent aux dépendances nommées.
- **Granularité** : résultat observable dans une fixture ou un niveau, pas nécessairement un nouveau niveau complet. Les runs de layout produisent un trajet traversable ; contenu et habillage viennent séparément. Une run d’intégration raccorde des systèmes déjà testés. Si un asset ou une correction exige plusieurs chantiers, scinder la run avant de l’exécuter, conserver sa traçabilité et mettre le compte à jour.
- **Art/audio pendant les runs** : chaque nouveau comportement doit être visible et testable, et avoir ses feedbacks P0 (`docs/08`, `docs/13`), éventuellement partagés provisoirement et sous licence vérifiée. Les runs d’habillage améliorent les ressources intégrées ; elles ne repoussent pas toute la télégraphie ou les sons essentiels à 0.8.

### Cycle de vie

Parcours normal : `BACKLOG → READY → ACTIVE → VERIFY → DONE`.

| État | Signification et sortie |
| --- | --- |
| BACKLOG | Run planifiée. Son inscription dans la roadmap n’autorise pas son lancement. |
| READY | Périmètre autorisé, dépendances satisfaites et décisions nécessaires prises ; l’implémentation peut commencer. |
| ACTIVE | Implémentation, corrections et vérifications de l’agent en cours. Passer à VERIFY quand le résultat est terminé et les contrôles pertinents de l’agent sont exécutés et satisfaisants. |
| VERIFY | Résultat vérifié, preuves disponibles, prêt pour revue ou validation humaine si requise. Ce n’est pas un stockage de tests techniques oubliés ou en échec. |
| DONE | Critères d’acceptation satisfaits, tests obligatoires réellement exécutés et réussis, bugtest/retest et régressions pertinents terminés, journal et learning à jour, validations humaines requises obtenues. |
| BLOCKED | Un prérequis, une décision ou un moyen de vérification indispensable manque et empêche de poursuivre utilement. Consigner le blocage et la condition de reprise ; revenir à READY, ACTIVE ou VERIFY selon le travail restant. |
| CANCELLED | Run abandonnée par décision explicite, avec motif conservé. |

La revue humaine intervient en VERIFY si la demande ou les critères l’exigent, par exemple pour un playtest humain ou un choix artistique. Nommer précisément ce qui attend son jugement. Une décision produit nécessaire à l’implémentation se tranche en amont. Sans validation humaine requise, VERIFY peut être bref et suivi de DONE dans la même intervention, sans nouvel accord systématique.

Un défaut découvert en VERIFY renvoie à ACTIVE pour correction ; un test technique obligatoire impossible à exécuter conduit à BLOCKED. Un playtest explicitement confié à l’humain peut rester en attente en VERIFY, mais interdit DONE tant qu’il n’a pas eu lieu.

Les commits locaux peuvent matérialiser des checkpoints vérifiés pendant ACTIVE ou en VERIFY, ainsi que la clôture documentaire. Aucun commit n’est exigé par simple changement d’état. Si un push ou une PR est demandé, préparer le résultat et son résumé vérifié en VERIFY, obtenir l’autorisation prévue par AGENTS.md si elle manque, puis effectuer l’action. Si cette livraison fait partie de la run, elle précède DONE ; sinon la clôture locale ne dépend pas d’un push ou d’une PR. Ne pas en proposer systématiquement pour une tâche simple.

| État | Détail opérationnel Git Flow |
| --- | --- |
| READY | create/switch feature branch from develop. |
| ACTIVE | local commits. |
| VERIFY | human review. |
| DONE | push + PR ; merge into develop. |
Une run peut être techniquement terminée et validée localement avant que l'humain ne décide de merger la branche.

### Vérification proportionnée

Les critères de chaque fiche restent obligatoires. Choisir les contrôles supplémentaires selon le risque et les interactions touchées :

| Modification | Preuve pertinente |
| --- | --- |
| Gameplay, collision ou interaction | Exécuter le comportement dans Godot, avec les cas limites concernés ; l’inspection statique seule ne suffit pas. |
| UI | Vérifier le rendu et les interactions clavier concernées, notamment focus, pause ou modales lorsque touchés. |
| Persistance ou économie | Exercer les transactions et cycles de sauvegarde/rechargement concernés, avec données de test isolées. |
| Bugfix | Reproduire si possible, corriger, tenter à nouveau la reproduction et contrôler les interactions voisines. |
| Documentation seule | Relire la cohérence, les références et le diff ; pas de suite de jeu sans lien avec le changement. |

La régression commune s’applique à toutes les fiches **selon leur impact** : mobilité/collisions après modification du joueur ou terrain ; économie/saves après transaction ; clavier/pause après UI ; mort/reset/transition pour la persistance touchée. Aux recettes de version, reprendre N1 et le dernier niveau livré, ainsi que le parcours explicitement demandé par la fiche. Ces recettes complètent les contrôles des runs, elles ne les remplacent pas.

Conserver les invariants utiles des 150 contrôles existants ; réécrire explicitement les assertions obsolètes (Q/D, R, PV Slime, bonus) plutôt que les supprimer pour faire passer la suite. Une fois les critères et contrôles pertinents satisfaits, arrêter de les étendre ou répéter sans modification, échec ou incertitude concrète qui le justifie.

Corriger et retester les bugs du scope avant clôture. Un défaut indépendant alimente une petite run corrective liée, sans élargissement silencieux de la run courante. Consigner les vérifications effectuées, résultats et limites dans [runs-journal.md](runs-journal.md), en distinguant un contrôle exécuté d’un contrôle restant. Les pistes Learning des fiches ne deviennent des entrées dans [learning.md](learning.md) qu’après réalisation vérifiée.

Références de la révision du workflow du **22 septembre 2026** : recommandations OpenAI sur [AGENTS.md et les skills avec Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [l’autonomie et le calibrage des tests](https://developers.openai.com/api/docs/guides/latest-model), [les skills](https://learn.chatgpt.com/docs/build-skills) et [les subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Les frontières Git et les validations propres au projet suivent les choix de l’utilisateur.

## Versions-cibles validées

| Cible | Objectif | Priorité | Runs prévues | Prérequis principaux |
| --- | --- | --- | --- | --- |
| 0.1.0 | Socle de production vérifié | P0 | 11 détaillées | Accord de démarrage |
| 0.2.0 | Premier niveau et boucle de reprise | P0 | 9–11 indicatives | 0.1.0 validée ; D03–D05 |
| 0.3.0 | Économie de coffres et niveau 2 | P1 | 6–8 indicatives | 0.2.0 validée ; D02/D04/D06 |
| 0.4.0 | Ennemis avancés, secrets et niveaux 3–4 | P1 | 7–9 indicatives | 0.3.0 validée ; D01/D04/D06/D07 |
| 0.5.0 | Verticalité, capacités et niveaux 5–6 | P1 | 8–10 indicatives | 0.4.0 validée ; D02/D04/D06–D08 |
| 0.6.0 | Derniers niveaux d’exploration | P1 | 6–8 indicatives | 0.5.0 validée ; D04/D06 |
| 0.7.0 | Boss final et conclusion jouable | P1 | 5–7 indicatives | 0.6.0 validée ; D08/D09 |
| 0.8.0 | Cohérence visuelle et sonore de la démo | P2 | 3–5 indicatives | 0.7.0 validée ; D10 |
| 0.9.0 beta | Démo beta finale distribuable | P0 | 4–6 indicatives | 0.8.0 validée ; plateformes et budget D10 |

**Enveloppe indicative : 59 à 75 runs au total, dont 11 seulement définies aujourd’hui.** Les fourchettes incluent intégration, bugtest, corrections ciblées et recette de chaque version. Elles seront réévaluées au jalon précédent ; un dépassement justifié vaut mieux qu’une run monolithique ou des tests supprimés pour tenir un quota. Les variantes et leurs interactions simples peuvent rejoindre leur système ; un nouveau comportement risqué garde une run propre.

Les 138 fiches initiales sont remplacées par cette planification progressive. Aucune n’avait été exécutée : RUN-001 est conservée ; les autres identifiants de 0.1.0 sont réattribués ci-dessous. Les identifiants suivants seront attribués lors de l’affinage, puis resteront stables après lancement. Les critères de jalon et les spécifications produit restent la référence pour détailler les futurs tests.

## Version 0.1.0 — Socle de production vérifié

**Priorité : P0.** **Statut : planifiée, non atteinte.**

Rendre la base existante reproductible, fixer son échelle et aligner le combat élémentaire sur les spécifications, dans la scène de test conservée.

**Prérequis :** accord de démarrage ; les décisions d’échelle et de combat restent traitées avant leurs implémentations dépendantes.

**Repères documentaires :** 01, 02, 05, 06, 07, 08, 10, 11, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Moteur et import reproductibles ; erreurs Windows observées pendant l’audit résolues ou isolées avec un contournement validé et testé.
- [ ] Comparaison visuelle 16/32 réalisée, décision explicite ; référence 640×360 et caméra lisibles sans réécriture automatique du terrain humain.
- [ ] Clavier cible, santé fractionnaire, maintien F, réactions aux dégâts et reset automatique testés dans Godot.
- [ ] Les invariants conservés de mobilité, bac, murs, collecte et porte passent ; les anciennes assertions remplacées sont justifiées.

**Runs dans l’ordre prévu :**

### RUN-001 — Stabiliser moteur, import et commandes de vérification

**Priorité : P0 · Statut : VERIFY · Dépendances : roadmap, périmètre et lancement validés.**

- **Résultat / scope :** Reproduire les trois erreurs d’import 4.7.2 sur copie propre, en rechercher la cause puis choisir et documenter le moteur de production ; aligner les lanceurs et isoler les sauvegardes des tests. Aucun changement gameplay.
- **Acceptation, test et bugtest :** Import depuis zéro et 11 suites sur le moteur retenu, logs sans erreurs ; démarrage F5 et fermeture ; préserver les changements humains de project.godot et du TileSet. Ne pas rétrograder automatiquement.
- **Learning pressenti :** Version du moteur, import Godot, caches générés, différence entre code de sortie et journal d’erreurs.

- **Périmètre inspecté au démarrage :** `tools/run.sh`, `tools/test.sh`, `Lancer-Windows.cmd`, contrat de sauvegarde dans `scripts/progression.gd`, suites `tests/` et métadonnées d’import. Comparer des copies propres sur chemin UNC et disque Windows local, puis tester les commandes corrigées et le lancement depuis l’éditeur. Conserver les scripts gameplay, scènes, sources d’assets et réglages humains ; ne changer une ressource que si sa responsabilité dans l’erreur est démontrée.
- **Résultat vérifié :** Godot 4.7.2 retenu ; trois WAV corrigés pour le remplissage RIFF, originaux et PCM conservés ; lanceurs harmonisés et tests isolés. Deux imports propres puis 150 contrôles de jeu + 1 contrôle d’isolation réussis par copie. Preuves et limites dans [runs-journal.md](runs-journal.md#run-001--stabiliser-moteur-import-et-commandes-de-vérification).
- **Validation humaine reçue le 22 septembre 2026 :** lancement F5 confirmé (« oui fonctionne avec F5 »).
- **Validation humaine reçue le 23 septembre 2026 :** fermeture manuelle du jeu et de l’éditeur confirmée, sans problème signalé. La revue finale du diff et des preuves est satisfaisante. Une PR vers `develop` est retenue selon le Git Flow du dépôt ; push, création de PR et merge restent soumis à autorisation. RUN-001 demeure VERIFY jusqu’à son intégration.

### RUN-002 — Inventorier les sources et définir les livrables visuels/sonores

**Priorité : P0 · Statut : ACTIVE · Dépendances : RUN-001 (contrôles et validation humaine satisfaits ; intégration par PR en attente).**

- **Résultat / scope :** Compléter docs/11–13 et les besoins d’animations/VFX de docs/13 ; retracer les 12 médias présents, leurs licences et les manques. Définir source conservée / dérivé de jeu, sans déplacement massif.
- **Acceptation, test et bugtest :** Chaque média utilisé a une provenance vérifiable ou un remplacement identifié ; les besoins par jalon sont attribués, les achats éventuels restent une décision humaine.
- **Learning pressenti :** Import, spritesheet, licence, ressource référencée versus fichier seulement présent.

### RUN-003 — Comparer l’échelle sur un échantillon représentatif

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-002.**

- **Résultat / scope :** Comparer 16×16 et 32×32 dans Godot avec extrait N1, joueur, Slime, humanoïde, décor, piège et coffre ; conserver 16×16 comme hypothèse jusqu’à décision explicite.
- **Acceptation, test et bugtest :** Captures comparables à 640×360 ; silhouettes, taille des collisions et lisibilité contrôlées ; décision enregistrée avant production des biomes.
- **Learning pressenti :** Tile size, taille de frame, pixels opaques, densité de pixels et collisions indépendantes.

### RUN-004 — Adapter la résolution et le cadrage du prototype

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-003.**

- **Résultat / scope :** Appliquer 640×360, nearest et agrandissement entier ; adapter le cadrage des contrôles existants sans doubler les coordonnées du niveau. Isoler les limites et le réglage vertical spécifiques au slice ; évaluer suivi, smoothing et décalage horizontal avec le terrain réel.
- **Acceptation, test et bugtest :** 640×360, 1280×720 et 1920×1080 ; fenêtres hors ratio, HUD et textes sans découpage ; traversées existantes conservées. Sol, double saut, mur, bac, chute et combat ; absence de zone hors niveau et de tremblement gênant. Les zones spéciales restent locales et justifiées.
- **Learning pressenti :** Viewport, stretch, integer scaling et ancrages Control. Camera2D, limites, offset, smoothing et pixel snapping.

### RUN-005 — Adopter les actions clavier de production

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-001.**

- **Résultat / scope :** Flèches, Space, E, maintien F, G, R spécial, A équipement, Escape ; retirer le reset direct R au profit du futur menu. G/R/A peuvent rester sans effet tant que leur système manque.
- **Acceptation, test et bugtest :** Vrais événements clavier, aucune collision R spécial/reset ; menus et gameplay ne consomment pas le même appui deux fois ; aucun support souris/manette ajouté.
- **Learning pressenti :** Input Map, actions logiques, pressed/just_pressed et propagation des entrées.

### RUN-006 — Unifier la santé fractionnaire et les réactions aux dégâts

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-005.**

- **Résultat / scope :** Faire évoluer santé joueur/ennemi et signaux pour 0,5 HP et 0,2 DMG ; fixer la représentation numérique et l’affichage arrondi avant les consommables (D01). Contrat minimal contact/mêlée, projectile, piège solide, flamme, swarm et vide ; appliquer les réactions définies sans construire tout le bestiaire. Bloquer réellement attaque durant hit-stun et saut durant recul ; régler les durées par essai et préserver les décisions de mobilité existantes sauf preuve contraire.
- **Acceptation, test et bugtest :** Suites de dégâts 0,5 et 0,2, zéro exact, soin borné, mort unique ; aucune perte par conversion int et aucun HP négatif. Matrice de sources dans une fixture : invulnérabilité, interruption, hit-stun et knockback conformes ; le vide reste fatal. F/Space maintenus ou pressés pendant impact, mur, atterrissage, plusieurs contacts ; reprise des actions à la fin exacte du blocage.
- **Learning pressenti :** Types numériques, précision, signaux et bornes de santé. Données de dégâts, responsabilité de la source et du receveur. Timers, états concurrents et priorité des actions.

### RUN-007 — Aligner le combat Sword et les Slimes existants

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-006.**

- **Résultat / scope :** Appliquer Sword niveau 0, ses dégâts et intervalle de 1 s ; définir RANGE en pixels/blocs (D02) ; un coup par cible, attaques aériennes, interdiction wall slide. Conserver leur patrouille et les sprites ; appliquer PV/dégâts documentés et knockback sans l’actuelle immunité de contact pendant stagger.
- **Acceptation, test et bugtest :** F maintenu plusieurs secondes, relâché/repressé, changement de direction, mur occlusif et interruption ; aucun dégât par frame. Green 1 HP/0,5 DMG, Purple 2 HP/1 DMG ; une mort/une récompense, bords/murs, coups simultanés sans hit-stun ennemi.
- **Learning pressenti :** Cooldown, fenêtre active, déduplication des impacts et requêtes physiques. Paramètres d’ennemi, variantes, patrouille et signal de mort.

### RUN-008 — Créer les piques fixes solides et borner le vide par niveau

**Priorité : P1 · Statut : BACKLOG · Dépendances : RUN-006.**

- **Résultat / scope :** Introduire le piège fixe 0,5 DMG horizontal/vertical ; remplacer le seuil global y>340 par une limite de niveau adaptée. Ne pas supprimer les ronces sans traiter leur usage.
- **Acceptation, test et bugtest :** Contact sur chaque orientation, knockback sans hit-stun/interruption, invulnérabilité ; chute mortelle une fois ; murs grimpables inchangés.
- **Learning pressenti :** Body2D/Area2D, layer/mask et zones létales.

### RUN-009 — Automatiser la mort et la reprise

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-006, RUN-008.**

- **Résultat / scope :** Message anglais « Thou hast perished. », assombrissement 3 s puis fondu/reset ; spawn sûr et vie restaurée, sans appui requis.
- **Acceptation, test et bugtest :** Morts répétées, mort en pause/attaque, aucune double recharge ; attendre au spawn ne tue pas ; gains de tentative actuels perdus une fois.
- **Learning pressenti :** Transitions, timers, rechargement de scène et verrous.

### RUN-010 — Installer les bus et les feedbacks élémentaires

**Priorité : P1 · Statut : BACKLOG · Dépendances : RUN-002, RUN-009, RUN-007.**

- **Résultat / scope :** Master/Music/Ambient/SFX/UI ; brancher les sons P0 du mouvement, mêlée, dégâts, mort, collecte et mort Slime, en réutilisant provisoirement des sons autorisés.
- **Acceptation, test et bugtest :** Écoute réelle avec actions simultanées, sans clipping ; sons UI non positionnels et sons monde 2D pertinents ; aucun footstep.
- **Learning pressenti :** Bus audio, AudioStreamPlayer2D, formats WAV/OGG et niveaux sonores.

### RUN-011 — Valider et corriger le socle de production

**Priorité : P0 · Statut : BACKLOG · Dépendances : RUN-004, RUN-005, RUN-007, RUN-008, RUN-009, RUN-010.**

- **Résultat / scope :** Fermer 0.1.0 après correction des défauts ciblés de ce jalon, sans retouche globale du niveau. Réévaluer le dépôt et détailler les runs de 0.2.0 en fin de recette, en ajustant son enveloppe si nécessaire.
- **Acceptation, test et bugtest :** Import propre, suites adaptées, deux branches et retours, pause/mort ; contrôle graphique 30/60/144 fps et essai humain du saut mural.
- **Learning pressenti :** Tests de physique, différence test ciblé/parcours, reproduction et preuve de régression.

## Version 0.2.0 — Premier niveau et boucle de reprise

**Priorité : P0.** **Statut : intention de jalon, découpage à affiner.**

Transformer la scène actuelle en point de départ de The Eidolon Vale et livrer son tutoriel avec sauvegarde, interface clavier et Longbow.

**Prérequis :** version 0.1.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 01, 03, 04, 05, 07, 08, 09, 10, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] N1 jouable du menu à la sortie : Spirit, explications, Green/Purple, piques/vide, une potion et coffre gratuit Longbow 0.
- [ ] Coins et shards distincts ; équipement acquis persistant selon contrat validé, aucune sauvegarde joueur perdue silencieusement.
- [ ] New Game/Continue/Controls/Quit, pause et dialogues entièrement clavier, textes anglais, aucune superposition de modales.
- [ ] N1 court et facile, spawn sûr, sortie à 12 coins ; transition testée vers fixture, aucun N2 final revendiqué.

**Enveloppe : 9–11 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Contrats de reprise et progression :** trancher D03/D04/D05 avant le schéma : banque/tentative, dépenses, v1, dialogues vus et refus du coffre. Définir les identifiants de niveaux, transitions et séparation coins/shards.
- **Équipement et persistance :** introduire les deux slots et Longbow, puis raccorder sauvegarde versionnée et reprise aux événements validés ; tester migration, corruption, échec disque et absence de double attribution.
- **Interface et tutoriel :** arbitrer focus/modales avant HUD et menus clavier ; Controls, dialogue de The Ancient Spirit, coffre gratuit, potion mineure et messages contextuels s’intègrent au parcours.
- **Niveau et recette :** adapter le slice à The Eidolon Vale, intégrer présentation et audio, puis parcourir New Game → sortie, mort/reprise et Continue à froid. Réserver des runs distinctes aux fondations et à cette intégration.

**Learning à décliner lors de l’affinage :** sauvegardes versionnées, transactions, scènes de projectile, focus clavier, dialogues et parcours introductif.

## Version 0.3.0 — Économie de coffres et niveau 2

**Priorité : P1.** **Statut : intention de jalon, découpage à affiner.**

Rendre la progression d’équipement opérationnelle et livrer Blight Town avec ses premières menaces supplémentaires.

**Prérequis :** version 0.2.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 02, 03, 04, 05, 07, 08, 11, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Coûts common/rare, récompenses et upgrades conformes à une table validée ; Legendary encore exclu du pool jusqu’à son implémentation.
- [ ] Armes standard hors Fire Gauntlet utilisables et persistantes ; soins de terrain et drops de soin testés.
- [ ] N2 terminé à 18 coins, Red/Bloated Slime, piques rétractables et trappes ; N1 reste traversable.

**Enveloppe : 6–8 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Équipement et économie :** valider tables, coûts, poids et soins ; décliner les armes de mêlée standard et Throwing Knives depuis les contrats existants, puis coffres common/rare, choix/refus et upgrades.
- **Menaces et soins :** Red et Bloated Slime avec aggro bornée, piques rétractables, trappes, potion majeure et soins sur kill ; leurs comportements restent vérifiés séparément.
- **Niveau et recette :** construire et habiller Blight Town, connecter N1 → N2 ; bugtester mauvais tirages, dépenses/refus, reset/rechargement et régression N1.

**Learning à décliner lors de l’affinage :** ressources paramétrées, pondération reproductible, transactions de récompenses, aggro et cycles de pièges.

## Version 0.4.0 — Ennemis avancés, secrets et niveaux 3–4

**Priorité : P1.** **Statut : intention de jalon, découpage à affiner.**

Construire les quatre archétypes avancés séparément, introduire les secrets et livrer Black Forrest et Forbidden Graveyard.

**Prérequis :** version 0.3.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 01, 02, 03, 04, 05, 06, 07, 08, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Warrior, Archer, Sorcerer, Swarm et Chud ont chacun leurs tests de comportement ; télégraphies et SFX P0 intégrés.
- [ ] Tourelles, plantes, Magic Shield, mécanismes, portes secondaires, secrets permanents et HP bonus opérationnels.
- [ ] N3/N4 jouables à 25/32 coins ; N4 contient son secret, sa potion majeure, son rare chest et son HP bonus ; toutes les dépenses optionnelles restent compatibles avec la sortie.

**Enveloppe : 7–9 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Bestiaire avancé :** fixer le contrat d’aggro, puis réaliser et tester Warrior, Archer, Blight Sorcerer et Possessed Skulls ; inclure Chud Blob et les télégraphies sans regrouper tout le bestiaire en une seule run.
- **Exploration et progression :** tourelles, plantes dangereuses, Magic Shield, secrets permanents, portes payantes, plaques/boutons et HP bonus ; coûts et persistance reposent sur les contrats précédents.
- **Niveaux et recette :** livrer Black Forrest et Forbidden Graveyard avec leurs récompenses et ambiances ; contrôler N1–4, dépenses optionnelles, invocations et reset des mécanismes.

**Learning à décliner lors de l’affinage :** machines à états, attaques télégraphiées, groupes d’ennemis, mécanismes de niveau et état permanent.

## Version 0.5.0 — Verticalité, capacités et niveaux 5–6

**Priorité : P1.** **Statut : intention de jalon, découpage à affiner.**

Compléter l’équipement, les consommables spéciaux et la persistance unique avant Haunted Caves et Desolands.

**Prérequis :** version 0.4.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 01, 02, 03, 04, 05, 06, 07, 08, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Grimper, attaque d’atterrissage, flammes, Rage et Fire Gauntlet testés séparément puis combinés.
- [ ] Quatre légendaires, golden chest, Enchant Juice et offrande N5 fonctionnels avec sauvegarde cohérente.
- [ ] N5/N6 jouables à 40/50 coins, profils N5–9, palier 5 HP, secrets et récompenses uniques exactement répartis.

**Enveloppe : 8–10 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Verticalité et capacités :** grimpe, attaque d’atterrissage et flammes ; Rage, Fire Gauntlet et affichage des cooldowns. Régler les interactions avant l’intégration au terrain vertical.
- **Équipement unique :** Dragon Slayer, Obsidian Relic, Thunderstruck et Demonic Crossbow gardent des validations propres ; Golden Chests, Enchant Juice et unicité persistante s’appuient sur l’économie existante.
- **Progression et niveaux :** paliers HP N5/N8, première offrande N5 et profils ennemis N5–9 ; construire et habiller Haunted Caves et Desolands avec leurs secrets et uniques.
- **Recette :** vérifier N1–6, combinaisons d’armes/capacités, cooldowns après reset, dépense/offrande et fermeture après récompense unique.

**Learning à décliner lors de l’affinage :** états de locomotion, détection d’impact, cooldowns, buffs, capacités spécifiques et sauvegarde des uniques.

## Version 0.6.0 — Derniers niveaux d’exploration

**Priorité : P1.** **Statut : intention de jalon, découpage à affiner.**

Livrer Rotbringer Camps, Fallen Temple et Darkveil Dungeon avec les dernières élites et la seconde offrande.

**Prérequis :** version 0.5.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 02, 03, 04, 05, 06, 07, 08, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Chaos Champion et Necromancer conformes, charge et invocations télégraphiées, population bornée.
- [ ] N7/8/9 jouables à 64/82/100 coins ; HP 7 à N8, deuxième offrande 50 % non additive.
- [ ] Total N4–9 : 10 secrets, 3 Golden, 6 Rare secrets, 8 Major secrètes, 1 Enchant ; HP bonus répartis 1/1/2/3 sur N4/5/7/9.

**Enveloppe : 6–8 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Dernières élites :** charge de Chaos Champion, invocations et trois zones de Necromancer ; borner les populations et les récompenses, vérifier pause/mort et disparition des invocations.
- **Derniers niveaux :** construire, peupler et habiller Rotbringer Camps, Fallen Temple et Darkveil Dungeon avec les systèmes déjà éprouvés ; deuxième offrande, palier N8 et répartition des secrets/uniques.
- **Recette :** parcourir N1–9, tester densité de rencontres et économie avec/sans bonus HP ou sacrifices ; recharger aux paliers et contrôler les uniques.

**Learning à décliner lors de l’affinage :** charge télégraphiée, cycle d’invocation, composition de niveaux et stress des interactions.

## Version 0.7.0 — Boss final et conclusion jouable

**Priorité : P1.** **Statut : intention de jalon, découpage à affiner.**

Terminer Darkveil Dungeon Throne, le combat Lupikal et la libération de Karla ; la démo devient jouable de bout en bout.

**Prérequis :** version 0.6.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 01, 02, 03, 04, 05, 06, 07, 08, 09, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] N10 dédié au boss, spawn sûr, confrontation puis combat sans aggro/reset exploitable, caméra adaptée.
- [ ] 50 HP, mêlée, quatre zones, boules de feu, charge, invocations et enrage ≤20 HP validés séparément puis ensemble.
- [ ] Victoire puis dialogue Karla et fin de démo ; aucune onzième zone ajoutée pour le Heart of Corruption.
- [ ] Boss vaincu en playtest avec 7 HP de base et armes 2/3 sans Legendary ; 14 HP avantageux sans trivialiser le combat.

**Enveloppe : 5–7 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Contrat et arène :** trancher D08/D09, construire le trône et son spawn sûr avant l’intégration du boss.
- **Combat Lupikal :** développer les attaques par familles testables : mêlée, explosions au sol, projectiles, charge et invocations ; intégrer ensuite l’ordonnancement, les télégraphies et l’enrage.
- **Conclusion et recette :** relier HUD boss, introduction, art/audio du trône et libération de Karla ; tester le parcours complet, la mort simultanée, Continue après victoire et le combat sans Legendary.

**Learning à décliner lors de l’affinage :** phases de boss, ordonnancement d’attaques, télégraphies, séquences narratives et état de fin.

## Version 0.8.0 — Cohérence visuelle et sonore de la démo

**Priorité : P2.** **Statut : intention de jalon, découpage à affiner.**

Achever la présentation et la variété prévues ; aucun système gameplay essentiel ne doit être reporté à cette version.

**Prérequis :** version 0.7.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** 05, 06, 07, 08, 09, 11, 12, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [ ] Palette, échelle, animation et contraste cohérents dans les dix biomes ; variantes avancées retenues reconnaissables sans changer leur gameplay.
- [ ] Toutes les lignes requises de docs/08 et docs/13 ont un asset intégré/testé ou une décision de scope validée ; aucun P0 manquant.
- [ ] HUD, menus, artwork, logo, dialogues et audio final testés au clavier à 640×360 ; tous les textes visibles sont anglais.
- [ ] Sources originales intactes, dérivés identifiables et crédits/licences complets pour les assets distribués.

**Enveloppe : 3–5 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Présentation cohérente :** compléter les variantes Warrior/Archer/Caster/Skulls/Bats retenues sans altérer leurs profils ; finaliser HUD, menus, artwork, logo et feedbacks contextuels.
- **Audio et caméra :** compléter/mixer le catalogue requis, exposer les volumes et conserver leurs préférences ; ne retenir les effets facultatifs de caméra que s’ils améliorent la lisibilité (P3).
- **Recette :** contrôler dix biomes, clavier, animations/collisions, anglais, mix et inventaires d’assets/licences ; conserver les sources et tester les dérivés.

**Learning à décliner lors de l’affinage :** pipeline de variantes, ancrages d’animation, lisibilité, mix audio, réglages persistants et crédits.

## Version 0.9.0 — Démo beta finale distribuable

**Priorité : P0.** **Statut : intention de jalon, découpage à affiner.**

Livrer une démo 0.9.0 beta complète, équilibrée et testée, avec une distribution reproductible sur les plateformes retenues.

**Prérequis :** version 0.8.0 validée et contrats nécessaires résolus avant leur implémentation.

**Repères documentaires :** `docs/00` à `docs/13`, `brief.md` et résultats du `runs-journal.md`.

**Critères de validation du jalon :**

- [ ] Dix niveaux, boss et conclusion terminables ; sessions humaines couvrent l’objectif de 1–2 h et les retries, sans prétendre garantir une durée non mesurée.
- [ ] Aucun bug bloquant/critique ouvert ; toutes les règles persistantes, coûts, uniques et interactions testés après corrections.
- [ ] Build autonome vérifié sur chaque plateforme de livraison retenue ; import propre, installation vierge, sauvegarde/reprise et fermeture corrects.
- [ ] Version 0.9.0 beta affichée et documentée, licences/crédits et limites connues livrés ; aucune publication automatique.

**Enveloppe : 4–6 runs**, recette et corrections ciblées incluses. Aucun identifiant n’est réservé à ce stade.

**Axes dans l’ordre de dépendance :**

- **Playtests et corrections :** mesurer difficulté, économie et durée sur de vrais parcours ; corriger les problèmes observés, retester les situations et les interactions adjacentes.
- **Robustesse :** durcir sauvegardes et transitions, mesurer les performances sur le matériel retenu, puis corriger les défauts reproductibles.
- **Livraison et recette :** préparer exports et version beta, vérifier les builds autonomes sur les plateformes retenues, refaire la régression après les dernières corrections et livrer crédits/limites connues ; publication soumise à autorisation.

**Learning à décliner lors de l’affinage :** observation de joueurs, matrices de régression, profilage, exports reproductibles et recette hors éditeur.

## Point d’arrêt

RUN-001 attend son intégration par PR en VERIFY. RUN-002 commence par l’inventaire et la documentation des assets, sur branche distincte. Aucun push, PR ou merge sans autorisation. Après 0.1.0, détailler 0.2.0 à partir du résultat réel.
