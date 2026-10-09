# Milady's Knight — Roadmap de production

## Statut de cette planification

**7 octobre 2026 — Version actuelle : 0.2.0 ; cible 0.3.0 autorisée.** RUN-001–020 et RUN-029 DONE (21 runs). RUN-019 intégrée dans `develop` par PR #22 (`6a1b279`). RUN-020 validée en l’état par l’humain le 6 octobre après reprise Claude et recette Codex ; clôture locale sur `feature/run-020-021-campaign`. RUN-021 ACTIVE pour la nouvelle passe piques/munitions, après validation humaine de la correction du passage suspendu de Bloated N2 et tests renforcés de Bloated/Chud :651PASS/21RESULT sur la recette ciblée finale,46contrôles rendus. La dernière passe est testée et validée humainement ; le contrat piques/munitions est validé avec transfert des stocks courants au niveau suivant. Sept lots restent BACKLOG. Contrat D01/D06/D07 et budget Skull validés. Les checkpoints datés ci-dessous décrivent leur état historique.

**Clôture du 3 octobre 2026 : RUN-015–017 DONE, jalon 0.2.0 validé localement.** Deux passes Claude et playtest humain N1 validés ; correctif idle, recette finale et revue Jev/inspection terminés. [PR #18](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/18) ouverte de `feature/run-017-eidolon-vale` vers `develop`, sans fusion. Aucune autre run lancée. Les checkpoints antérieurs ci-dessous conservent leur contexte historique.

**Mise à jour du 3 octobre 2026 :** PR #16 fusionnée dans `develop` (`f997bcb`), verrou 0.2.0 levé. RUN-015–016 DONE ; passe Claude RUN-016 validée par l’humain, revue globale terminée sur `feature/v0.2.0-reprise-equipment`. Push et PR vers develop autorisés par la demande humaine de revue puis livraison ; pas de merge autorisé. Les paragraphes datés du 2 octobre conservent le contexte historique.

Audit documentaire et inspection du dépôt effectués le **21 septembre 2026**, à partir de l’état de travail courant, et non du seul commit `0870462`.
**RUN-001 à RUN-014 et RUN-029 DONE. Version 0.1.0 clôturée et validée localement le 2 octobre 2026**, après validation humaine de toutes les passes et audit final. La PR vers `develop` est autorisée ; fusion encore à effectuer. Les PR #1, #2, #4, #5, [#8](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/8) et [#9](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/9) sont fusionnées dans `develop`. RUN-007 est fusionnée via la PR #11 (`260c8a8`), RUN-008 via la PR #12 (`6c4ee22`), RUN-009 via la [PR #14](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/14) (`a2ac33c`) et RUN-010 via la PR #15 (`24213f2`). RUN-011 clôt le socle 0.1.0 localement après recette technique et validation humaine du saut mural ; livraison de cette branche préparée pour la PR autorisée. La validation des onze premières runs et du socle **0.1.0** est confirmée par l’humain le **2 octobre 2026**. La réorganisation ci-dessous reste sur `feature/run-011-production-foundation` ; aucune run 0.2.0 n’est lancée.

Plan réorganisé le **2 octobre 2026** : **29 identifiants au total**, dont 15 runs DONE (001–014 et 029) et 14 lots de production BACKLOG (015–028). La cible finale devient **0.5.0 beta**, toujours une démo de dix niveaux conçus à la main. **0.1.0 est la version actuelle validée localement** ; 0.2.0 est la prochaine cible, soumise au verrou de branche ci-dessous. Les patchs `0.x.1` restent possibles pour des corrections vérifiées, sans créer systématiquement une run ni une version par tâche.

Ce plan couvre les spécifications de `docs/00` à `docs/13`, y compris art, audio, narration et livraison. Les durées de travail ne sont pas estimées. L’objectif de 1–2 heures de jeu reste à mesurer. Le nombre futur de runs est une enveloppe de planification révisable, pas une promesse de calendrier ni une réduction du scope produit.

## Audit vérifié de la base

**Archive du 21 septembre 2026.** Les constats de cette section décrivent la base avant RUN-001, pas l’état actuel ; consulter `brief.md` et les résultats des runs pour le socle 0.1.0.

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
| D01 | RUN-006 : santé stockée en dixièmes entiers, texte HUD exact et cœurs arrondis au demi-cœur supérieur. L'effet immédiat d'un bonus MAX HP sur CURRENT HP reste à préciser. | Santé en 0.1, bonus HP en 0.3. |
| D02 | `01`/`04` : RUN-007 fixe 1 RANGE = 24 px = 1,5 bloc depuis la main pour Sword ; variation des stats selon armes/niveaux, ATK SPEED positif jusqu’au niveau 5 ; timings de hit-stun/recul et seuil/rayon du slam encore ouverts. | Sword en 0.1, tables en 0.3, slam en 0.4. |
| D03 | `03` : « sauvegarde uniquement au passage de niveau » versus équipement/uniques sauvés aussi après fermeture en plein niveau. Choisir les événements de sauvegarde durable et le snapshot de tentative. | Contrat de persistance 0.2 avant tout schéma. |
| D04 | `03`/`04` : ordre de dépense banque/gains, banque après dépense puis mort, base retenue à 20/50 %, croissance des prix/poids/drop soins, gains de swarm/invocations et farm possible, seconde offrande sans première. Migration de l’ancien bonus (qui inclut du surplus de coins) à décider, sans conversion silencieuse. | Contrat 0.2, tables 0.3, swarm 0.3, offrandes 0.4. |
| D05 | `01`/`05`/`10` : Escape ne doit pas ouvrir pause pendant coffre/contexte, mais doit pouvoir annuler/fermer ; priorité exacte des dialogues ; portée de « dialogue non rejouable » après mort/reload ; refus/reprise du coffre tuto, confirmation des actions permanentes et disposition des slots (horizontale dans `04`, verticale dans `05`). | Modales, dialogue et coffre N1 en 0.2. |
| D06 | `02`/`06` : aggro périmètre versus ligne de vue, poursuite/retour autour des bords, nombre de skulls et plafond d’invocations, devenir des invocations à la mort de la source. « niveau 5 et 9 » ambigu pour les profils Skeleton. Les variantes N2 de l’Art Bible sont des exemples, le bestiaire par niveau de `03` reste à respecter. | IA 0.3 puis profils et invocations 0.4. |
| D07 | `01`/`04` : restrictions de grimpe, accumulation/rafraîchissement de Shield et Rage, sort des cooldowns au changement d’arme/reset ; déclenchement de secrets par mêlée/tir/impact. | Secrets/buffs 0.3, grimpe/capacités 0.4. |
| D08 | `04` : durée/annulation de charge Dragon Slayer ; kills éligibles/compteur Obsidian ; portée/relief de Thunderstruck et « one shot n’importe quel mob » face au Boss. | Chaque Legendary 0.4 puis contrat Boss 0.4. |
| D09 | `02`/`09` : 3/5 DMG du Boss non attribués à chaque attaque ; accélération d’attaque enrage non chiffrée ; départ immédiat versus dialogue et spawn AFK sûr ; état de fin/Continue après Karla. | Contrat Boss 0.4, avant l’arène. |
| D10 | `06`/`11`/`13` : comparaison 16/32, gabarits/packs/licences, mapping final des skins et animations ; vocabulaire à harmoniser (Black Forest/Forest, Ancien/Ancient, Fire/Dire Gauntlet). Plateformes distribuées, matériel et budget de performance non définis. | Échantillon 0.1, noms avant contenu, variantes 0.5, export 0.5. |

Autres garde-fous de scope : pas de génération procédurale, checkpoints intra-niveau, sélection de sauvegardes, remapping, support souris/manette ou exploration après Karla. Les offrandes ne doivent pas être confondues avec les paiements de portes. Aucun add-on ni grande réarchitecture n’est nécessaire par défaut.

## Règles d’exécution et de clôture

Les invariants, le routage du contexte, les outils, la délégation et les autorisations Git sont définis dans [AGENTS.md](AGENTS.md). Les repères documentaires de chaque version orientent vers les sources utiles ; ils ne prescrivent pas leur lecture intégrale à chaque run.

Codex et Claude peuvent contribuer en parallèle à la même run ACTIVE si leurs tâches et fichiers sont séparés selon `AGENTS.md`. Le [conseiller de routage Jev `task_router`](tools/jev/task_router/README.md) aide au choix d'un subagent avant délégation. Il reste indépendant de la revue Jev avant `DONE` ci-dessous.

### Terrain et modifications manuelles de l’humain

L’humain édite manuellement les TileMap (terrain) des niveaux pour façonner précisément le level design, y compris hors run, et demandera souvent une review ou un audit de son travail. **Ne jamais effacer ni écraser ces modifications.** Le dépôt courant devient la baseline de chaque passe : inspecter et conserver diffs/empreintes avant intervention. Les scènes manuelles font autorité sur leurs générateurs historiques.

Ne pas rejouer un générateur, réenregistrer/remplacer globalement une scène, restaurer une version antérieure ou ajuster le terrain aux anciennes coordonnées d’un test. Adapter les tests aux scènes conservées. Une review/audit reste en lecture seule par défaut ; une correction de terrain humain nécessite une demande explicite de l’humain et un patch local identifié. Une modification humaine survenue pendant la run impose de rafraîchir la baseline et de coordonner les fichiers avant de poursuivre. L’habillage visuel doit préserver cellules, collisions et placements ; protéger aussi les ressources humaines dont il dépend.

Les gabarits actuels N1–4 ne représentent pas le scope final. L’humain prévoit des niveaux beaucoup plus grands, avec beaucoup plus de mobs, chemins et items ; ne pas déclarer cette ambition satisfaite ni fixer une nouvelle cible chiffrée sans décision.

### Choix et délégation pendant la run ACTIVE

Dès qu'une tâche autonome se présente, le main agent vérifie son périmètre, les fichiers attribués, les modèles disponibles et le nombre de subagents actifs (quatre au maximum). Il choisit un [custom agent du projet](AGENTS.md#delegation) adapté, ou un subagent ordinaire si aucun profil ne convient. Si le propriétaire Codex/Claude, le profil ou le niveau de raisonnement est incertain, il prépare une entrée JSON selon [`task_router/example.json`](tools/jev/task_router/example.json) et lance `tools/jev/task_router/route.py` comme indiqué dans son [README](tools/jev/task_router/README.md). La recommandation et les probabilités Jev sont consultatives : le main agent décide, délègue, intègre et vérifie ; `task_router` ne lance pas de subagent. Si Jev est indisponible, appliquer directement les règles d'[AGENTS.md](AGENTS.md).

| Custom agent | Main agent | Tâche cible | Modèle / raisonnement par défaut |
| --- | --- | --- | --- |
| `mechanical_worker` | Codex | Inventaire et travail mécanique borné | GPT-6 Luna Low |
| `code_worker` | Codex | Implémentation de code ciblée | GPT-6.1 Sol Medium |
| `architecture_reviewer` | Codex | Audit d'architecture complexe et délimité | GPT-6 Astra Medium |
| `visual_architect` | Claude | Cohérence et choix artistiques | Opus 5.5 Medium |
| `asset_integrator` | Claude | Préparation et intégration d'assets cadrées | Sonnet 5.5 Medium |

### Planification

- **Objectif de la réorganisation** : accélérer la production du jeu et donner davantage d’autonomie aux agents, sans surdécouper le travail. Une run porte un lot cohérent, de ses contrats à son intégration et à sa recette ; elle peut durer plusieurs sessions et comporter des checkpoints locaux.
- **Horizon de détail** : les 28 identifiants, résultats, dépendances et orchestrateurs sont prévus ci-dessous. Préciser les fichiers et scénarios de la run au lancement à partir du dépôt réel ; les étapes internes et tâches de subagents ne deviennent pas automatiquement de nouvelles runs.
- **Réévaluation au jalon** : adapter le contenu aux constats réels sans supprimer de critère produit ou de test obligatoire. Préférer les sous-tâches et checkpoints à de nouveaux identifiants ; toute exception justifiée doit garder le total planifié à **30 maximum**, sinon obtenir une révision humaine explicite du plan.
- **Préparation de la run active** : préciser ses fichiers/systèmes, limites, décisions requises et preuves attendues. Les décisions produit ouvertes sont obtenues avant le code dépendant, au sein du lot ; aucun résultat futur n’est présumé implémenté.
- **Priorités** : P0 bloque un jalon ou protège les données ; P1 requis pour le résultat fonctionnel ; P2 présentation requise avant livraison ; P3 polish conditionnel. Aucun regroupement ne réduit le scope produit.
- **Ordre** : une seule run ACTIVE. Chaque jalon attend la validation du précédent ; la 0.2.0 attend en plus le verrou de branche défini ci-dessous. Une fiche BACKLOG n’est pas une autorisation de démarrage.
- **Orchestrateur** : chaque lot futur désigne son main agent en amont. **Codex GPT-6.1 Sol Medium** pilote l’ingénierie ; **Claude Opus 5.5** pilote les lots visuels. Le routage, les profils, la délégation, les limites de concurrence et les deux outils Jev restent ceux d’AGENTS.md et du cycle de vie existant. Cette planification ne change pas le modèle d’un chat déjà ouvert ; signaler une configuration différente.
- **Art/audio pendant les runs** : chaque comportement doit être lisible et testable avec ses feedbacks P0 (`docs/08`, `docs/13`). Le lot final de présentation ne remplace pas ces intégrations. Dans un lot Codex, confier la contribution artistique à Claude selon les règles de propriété existantes ; ne pas éditer ensemble les mêmes fichiers.

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
| READY | Créer ou réutiliser une feature issue de develop pour un lot ou groupe cohérent ; respecter le verrou de branche. |
| ACTIVE | local commits. |
| VERIFY | human review. |
| DONE | Validation locale ; push, PR et fusion restent distincts et soumis à autorisation humaine. |
Une run peut être techniquement terminée et validée localement avant que l'humain ne décide de merger la branche.

#### Revue Jev avant DONE

Pour une run en `VERIFY`, rassembler les critères d'acceptation, les résultats réels des tests obligatoires, le bugtest, les régressions, le journal, le learning, les validations humaines requises et les blocages dans un fichier JSON local. Utiliser le format et la commande de [Run Completion Reviewer](tools/jev/run_completion_reviewer/README.md). Ne pas y placer de secret.

Le reviewer refuse localement les éléments manquants, en attente ou en échec, les blocages déclarés et la validation humaine obligatoire encore attendue. Si ces contrôles passent, Jev examine le dossier textuel avec trois décisions `Noul` indépendantes (couverture des critères, vérifications obligatoires, présence d'un blocage) et un `Choice` (`READY_FOR_DONE`, `VERIFY`, `BLOCKED`). `READY_FOR_DONE` est seulement une proposition pour la revue de clôture ; seul le workflow peut passer à `DONE`. `VERIFY` appelle une inspection supplémentaire ; `BLOCKED` signale un problème concret à traiter. Une erreur API signifie que la revue Jev est indisponible, pas que la run est bloquée.

Examiner les quatre résultats et les preuves originales, sans moyenne ni seuil automatique des probabilités. La sortie terminal est lisible ; `--json` conserve le détail local dans `work/test-results/...`. Consigner dans `runs-journal.md` la date, la run, la commande, les quatre décisions et probabilités utiles, l'inspection humaine déclenchée et sa conclusion, sans recopier le JSON complet ni prétendre que Jev a exécuté les tests. Aucune probabilité ne prouve l'exécution d'un contrôle et l'outil ne change jamais le statut.

La décision `VERIFY → DONE` reste fondée sur les critères de la table ci-dessus, les tests réellement observés et les validations humaines requises. Si TypeSafe est indisponible, consigner cette limite et effectuer la revue des preuves directement ; une panne du service ne modifie pas les critères de clôture. Un défaut constaté suit le retour à `ACTIVE` décrit ci-dessus.

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

## Versions-cibles et lots

| Cible | Résultat | Runs | Orchestrateur principal |
| --- | --- | --- | --- |
| **0.1.0 clôturée** | Socle validé ; compléments visuels et audio réalisés | 001–014 et 029 DONE | Historique conservé ; Claude Opus 5.5 pour les compléments |
| **0.2.0 actuelle** | N1 complet, menus, tutoriel, tir et reprise validés | 015–017 DONE | Codex GPT-6.1 Sol Medium |
| **0.3.0** | Économie et équipement standard, bestiaire et exploration N2–4 | 018–021 : 4 lots | Codex GPT-6.1 Sol Medium ; Claude Opus 5.5 pour 021 |
| **0.4.0** | Capacités, légendaires, N5–10, Boss et conclusion | 022–026 : 5 lots | Codex GPT-6.1 Sol Medium ; Claude Opus 5.5 pour 025 |
| **0.5.0 beta** | Présentation finale, équilibrage, recette et exports | 027–028 : 2 lots | Claude Opus 5.5 pour 027 ; Codex GPT-6.1 Sol Medium pour 028 |

**Total actuel : 19 runs DONE + 10 lots BACKLOG = 29 identifiants**, sous la limite de 30. Les trois passes 012–014 ont été retenues et réalisées ; RUN-029 ajoute la seconde passe visuelle demandée explicitement. Les identifiants futurs restent inchangés. Le plan conserve tous les systèmes, les dix niveaux, les recettes et les validations artistiques/humaines.

### Correspondance avec le plan remplacé

Cette table sert uniquement à relire les anciennes références du journal. Les RUN-001–011 ne sont ni renumérotées ni réinterprétées. Les anciens identifiants 012–021 étaient BACKLOG et n’avaient pas été lancés ; leurs fiches sont remplacées le 2 octobre 2026.

| Ancien périmètre | Nouveau lot / jalon |
| --- | --- |
| Anciennes RUN-012 contrats, 013 modales, 014 sauvegarde, 015 menus | RUN-015, 0.2.0 |
| Anciennes RUN-016 HUD, 017 Longbow, 019 coffre/potion | RUN-016, 0.2.0 |
| Anciennes RUN-018 Spirit, 020 N1, 021 recette | RUN-017, 0.2.0 |
| Ancien 0.3.0 (N2) et 0.4.0 (N3–4) | RUN-018–021, 0.3.0 |
| Ancien 0.5.0 (N5–6), 0.6.0 (N7–9), 0.7.0 (N10/Boss) | RUN-022–026, 0.4.0 |
| Ancien 0.8.0 (présentation) et 0.9.0 beta (livraison) | RUN-027–028, 0.5.0 beta |

### Verrou de la branche actuelle

Les conditions locales sont satisfaites le **2 octobre 2026** : réorganisation et modèles alignés, passes Claude 012–014 et 029 réalisées, recette intégrée réussie, validation humaine finale reçue. L’humain demande l’ouverture de la PR ; le push nécessaire et la PR vers `develop` sont autorisés.

**Verrou levé, vérifié le 3 octobre 2026 :** la [PR #16](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/16) a été fusionnée le 2 octobre dans `develop` (`f997bcb`). La branche `feature/v0.2.0-reprise-equipment` part de ce commit et couvre RUN-015 puis RUN-016, cette dernière uniquement après revue et validation humaine de RUN-015. Le lancement seul n’autorisait aucun push/PR/merge ; la demande humaine ultérieure du 3 octobre autorise désormais push et PR après revue, sans fusion.

## Version 0.1.0 — Socle de production vérifié

**Priorité : P0.** **Statut : DONE, clôturée et validée localement ; PR autorisée vers develop, fusion en attente.**

Rendre la base existante reproductible, fixer son échelle et aligner le combat élémentaire sur les spécifications, dans la scène de test conservée.

**Prérequis :** accord de démarrage ; les décisions d’échelle et de combat restent traitées avant leurs implémentations dépendantes.

**Repères documentaires :** 01, 02, 05, 06, 07, 08, 10, 11, 13 (numéros dans `docs/`).

**Critères de validation du jalon :**

- [x] Moteur et import reproductibles ; erreurs Windows observées pendant l’audit résolues ou isolées avec un contournement validé et testé.
- [x] Comparaison visuelle 16/32 réalisée, décision explicite ; référence 640×360 et caméra lisibles sans réécriture automatique du terrain humain.
- [x] Clavier cible, santé fractionnaire, maintien F, réactions aux dégâts et reset automatique testés dans Godot.
- [x] Les invariants conservés de mobilité, bac, murs, collecte et porte passent ; les anciennes assertions remplacées sont justifiées.

**Runs dans l’ordre prévu :**

### RUN-001 — Stabiliser moteur, import et commandes de vérification

**Priorité : P0 · Statut : DONE · Dépendances : roadmap, périmètre et lancement validés.**

- **Résultat / scope :** Reproduire les trois erreurs d’import 4.7.2 sur copie propre, en rechercher la cause puis choisir et documenter le moteur de production ; aligner les lanceurs et isoler les sauvegardes des tests. Aucun changement gameplay.
- **Acceptation, test et bugtest :** Import depuis zéro et 11 suites sur le moteur retenu, logs sans erreurs ; démarrage F5 et fermeture ; préserver les changements humains de project.godot et du TileSet. Ne pas rétrograder automatiquement.
- **Learning pressenti :** Version du moteur, import Godot, caches générés, différence entre code de sortie et journal d’erreurs.

- **Périmètre inspecté au démarrage :** `tools/run.sh`, `tools/test.sh`, `Lancer-Windows.cmd`, contrat de sauvegarde dans `scripts/progression.gd`, suites `tests/` et métadonnées d’import. Comparer des copies propres sur chemin UNC et disque Windows local, puis tester les commandes corrigées et le lancement depuis l’éditeur. Conserver les scripts gameplay, scènes, sources d’assets et réglages humains ; ne changer une ressource que si sa responsabilité dans l’erreur est démontrée.
- **Résultat vérifié :** Godot 4.7.2 retenu ; trois WAV corrigés pour le remplissage RIFF, originaux et PCM conservés ; lanceurs harmonisés et tests isolés. Deux imports propres puis 150 contrôles de jeu + 1 contrôle d’isolation réussis par copie. Preuves et limites dans [runs-journal.md](runs-journal.md#run-001--stabiliser-moteur-import-et-commandes-de-vérification).
- **Validation humaine reçue le 22 septembre 2026 :** lancement F5 confirmé (« oui fonctionne avec F5 »).
- **Validation humaine reçue le 23 septembre 2026 :** fermeture manuelle du jeu et de l’éditeur confirmée, sans problème signalé. La revue finale du diff et des preuves est satisfaisante. La [PR #1](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/1) a été fusionnée dans `develop` le 23 septembre 2026 (`9f4ecab`) ; tous les critères de RUN-001 sont satisfaits.

### RUN-002 — Inventorier les sources et définir les livrables visuels/sonores

**Priorité : P0 · Statut : DONE · Dépendances : RUN-001 (DONE).**

- **Résultat / scope :** Compléter docs/11–13 et les besoins d’animations/VFX de docs/13 ; inventorier les 12 médias présents, leurs usages, les sources/licences vérifiables et les lacunes. Définir source conservée / dérivé de jeu, sans déplacement massif.
- **Acceptation, test et bugtest :** Médias et références actuels inventoriés ; sources/licences distinguées entre vérifiées et non rattachées ; besoins par jalon attribués ; cohérence des liens, tableaux et diff contrôlée. Les achats éventuels restent une décision humaine. **Décision humaine du 23 septembre 2026 :** faute de correspondance fichier-source, ne pas exiger maintenant une provenance vérifiable ou un remplacement pour chacun des 12 médias. Reporter ce contrôle à l'intégration des assets retenus et à la recette des licences/crédits avant distribution (désormais 0.5.0 beta, RUN-027–028). Cette dérogation ne valide pas juridiquement les médias actuels.
- **Learning pressenti :** Import, spritesheet, licence, ressource référencée versus fichier seulement présent.
- **Résultat validé :** branche `feature/run-002-asset-inventory` ; 12 médias de jeu recensés dans les catalogues locaux 11–12, besoins audio par jalon dans le catalogue 12, matrice visuelle/animations/VFX par jalon dans docs/13 et principe source conservée → dérivé documenté. Les licences des deux packs Zerie candidats ont été vérifiées sur leurs pages officielles ; aucune correspondance avec les 12 médias du prototype n'est établie. Aucun achat ni asset externe intégré. Revue humaine reçue et PR #2 fusionnée le 23 septembre 2026 (`1d176db`). Les catalogues 11–12 sont ensuite retirés du suivi Git à la demande humaine ; leurs copies locales sont conservées.

### RUN-003 — Comparer l’échelle sur un échantillon représentatif

**Priorité : P0 · Statut : DONE · Dépendances : RUN-002 (DONE).**

- **Résultat / scope :** Comparer 16×16 et 32×32 dans Godot avec extrait N1, joueur, Slime, humanoïde, décor, piège et coffre ; conserver 16×16 comme hypothèse jusqu’à décision explicite.
- **Acceptation, test et bugtest :** Captures comparables à 640×360 ; silhouettes, taille des collisions et lisibilité contrôlées ; décision enregistrée avant production des biomes.
- **Learning pressenti :** Tile size, taille de frame, pixels opaques, densité de pixels et collisions indépendantes.
- **Décision humaine du 23 septembre 2026 :** grille 16×16 retenue ; taille opaque des personnages et collisions à réévaluer lors de l'intégration des véritables assets. Comparaison et limites dans `docs/RUN-003_SCALE_COMPARISON.md`. Revue humaine et validation confirmées ; PR #4 fusionnée dans `develop` au commit `1b99bb4`.

### RUN-004 — Adapter la résolution et le cadrage du prototype

**Priorité : P0 · Statut : DONE · Dépendances : RUN-003 (DONE).**

- **Résultat / scope :** Appliquer 640×360, nearest et agrandissement entier ; adapter le cadrage des contrôles existants sans doubler les coordonnées du niveau. Isoler les limites et le réglage vertical spécifiques au slice ; évaluer suivi, smoothing et décalage horizontal avec le terrain réel.
- **Acceptation, test et bugtest :** 640×360, 1280×720 et 1920×1080 ; fenêtres hors ratio, HUD et textes sans découpage ; traversées existantes conservées. Sol, double saut, mur, bac, chute et combat ; absence de zone hors niveau et de tremblement gênant. Les zones spéciales restent locales et justifiées.
- **Learning pressenti :** Viewport, stretch, integer scaling et ancrages Control. Camera2D, limites, offset, smoothing et pixel snapping.
- **Périmètre précisé au lancement :** `project.godot` (viewport), `scenes/hud.tscn` (ancrages et lisibilité), `scenes/player.tscn` et `scripts/level.gd` (caméra du slice). Coordonnées, collisions, contrôles clavier, décoration et règles de jeu restent ceux du slice. Les captures et parcours doivent vérifier les limites, le suivi au sol et dans les deux branches, la pause, la mort, la victoire et les quatre tailles de fenêtre demandées.
- **Résultat validé :** viewport 640×360 ; HUD ancré ; limites et cadrage configurés par le slice ; suivi physique lissé sans oscillation mesurée ; transition verticale locale devenue inutile supprimée. Import et 150 contrôles de jeu plus un contrôle d'isolation réussis sous Godot 4.7.2, captures des overlays et quatre tailles de fenêtre contrôlées. Preuves et limites dans `runs-journal.md` ; validation humaine confirmée et PR #5 fusionnée dans `develop` au commit `846137d`.

### RUN-005 — Adopter les actions clavier de production

**Priorité : P0 · Statut : DONE · Dépendances : RUN-001 (DONE).**

- **Résultat / scope :** Flèches, Space, E, maintien F, G, R spécial, A équipement, Escape ; retirer le reset direct R au profit du futur menu. G/R/A peuvent rester sans effet tant que leur système manque.
- **Acceptation, test et bugtest :** Vrais événements clavier, aucune collision R spécial/reset ; menus et gameplay ne consomment pas le même appui deux fois ; aucun support souris/manette ajouté.
- **Learning pressenti :** Input Map, actions logiques, pressed/just_pressed et propagation des entrées.
- **Périmètre précisé au lancement :** `project.godot`, `scripts/player.gd`, `scripts/level.gd`, tests clavier/intégration/bonus et documentation des commandes. Les flèches remplacent Q/D/Z/S ; F répète les frappes ; G/R/A sont des actions mappées sans capacité nouvelle. La mort et la victoire finale proposent `E` pour rejouer, sans redémarrage volontaire pendant une tentative avant le futur menu de pause. Le dialogue, l'équipement, les capacités et le menu complet restent hors de cette run.
- **Résultat vérifié localement :** import Godot 4.7.2 et 11 suites réussis, 170 contrôles de jeu et un contrôle d'isolation `user://`. Événements clavier réels pour les flèches, Space, E, F maintenu, G/R/A et Escape ; `R` sans reset, `E` bloqué pendant pause puis actionné une seule fois au portail après nouvelle pression. Après validation humaine du premier résultat, ajustement de la réponse horizontale et du cycle F à 0,28 s, avec direction du coup fixée pendant sa fenêtre de contact. Détails et limites dans `runs-journal.md` ; aucun push, PR ni fusion.
- **Validation humaine du 25 septembre 2026 :** ressenti du réglage vérifié et validé pour l’instant ; push de la branche et ouverture d’une PR vers `develop` explicitement autorisés. La cadence reste provisoire jusqu’à l’ATK SPEED des armes.
- **Livraison Git :** branche poussée et [PR #8](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/8) fusionnée dans `develop` au commit `95ec7f9` le 25 septembre 2026. RUN-005 est DONE.

### RUN-006 — Unifier la santé fractionnaire et les réactions aux dégâts

**Priorité : P0 · Statut : DONE · Dépendances : RUN-005 (DONE).**

- **Résultat / scope :** Faire évoluer santé joueur/ennemi et signaux pour 0,5 HP et 0,2 DMG ; fixer la représentation numérique et l’affichage arrondi avant les consommables (D01). Contrat minimal contact/mêlée, projectile, piège solide, flamme, swarm et vide ; appliquer les réactions définies sans construire tout le bestiaire. Bloquer réellement attaque durant hit-stun et saut durant recul ; régler les durées par essai et préserver les décisions de mobilité existantes sauf preuve contraire.
- **Acceptation, test et bugtest :** Suites de dégâts 0,5 et 0,2, zéro exact, soin borné, mort unique ; aucune perte par conversion int et aucun HP négatif. Matrice de sources dans une fixture : invulnérabilité, interruption, hit-stun et knockback conformes ; le vide reste fatal. F/Space maintenus ou pressés pendant impact, mur, atterrissage, plusieurs contacts ; reprise des actions à la fin exacte du blocage.
- **Learning pressenti :** Types numériques, précision, signaux et bornes de santé. Données de dégâts, responsabilité de la source et du receveur. Timers, états concurrents et priorité des actions.
- **Périmètre réalisé :** Santé et dégâts représentés en dixièmes entiers, API et signaux en HP fractionnaires ; HUD numérique exact et cœurs arrondis au demi-cœur supérieur. Profils joueur contact/mêlée, projectile, piège solide, flamme, swarm et vide. L'humain a choisi pour la flamme le profil du piège : invulnérabilité et recul. Le Slime accepte 0,2 DMG sans perte de précision. Aucun nouvel ennemi, projectile ou pouvoir n'est créé.
- **Vérification et clôture :** Godot 4.7.2 : import, isolation `user://`, 12 suites et 243 contrôles de jeu réussis après le correctif du saut variable pendant le recul ; trois captures HUD inspectées. L'humain a validé le correctif et vérifié le ressenti. Les durées de 0,18 s de hit-stun et 0,16 s de recul, notamment au contact d'un Slime et des ronces, restent provisoires et seront équilibrées ultérieurement. [PR #9](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/9) fusionnée dans `develop` au commit `2f3871e` le 25 septembre 2026. Détails dans `runs-journal.md`.

### RUN-007 — Aligner le combat Sword et les Slimes existants

**Priorité : P0 · Statut : DONE · Dépendances : RUN-006.**

- **Résultat / scope :** Appliquer Sword niveau 0, ses dégâts et intervalle de 1 s ; définir RANGE en pixels/blocs (D02) ; un coup par cible, attaques aériennes, interdiction wall slide. Conserver leur patrouille et les sprites ; appliquer PV/dégâts documentés et knockback sans l’actuelle immunité de contact pendant stagger.
- **Acceptation, test et bugtest :** F maintenu plusieurs secondes, relâché/repressé, changement de direction, mur occlusif et interruption ; aucun dégât par frame. Green 1 HP/0,5 DMG, Purple 2 HP/1 DMG ; une mort/une récompense, bords/murs, coups simultanés sans hit-stun ennemi.
- **Learning pressenti :** Cooldown, fenêtre active, déduplication des impacts et requêtes physiques. Paramètres d’ennemi, variantes, patrouille et signal de mort.

- **Préparation du 28 septembre 2026 :** lancement et retrait de `.claude/` de l’index autorisés par l’humain ; branche existante issue de `develop`. `skills-lock.json` modifié avant la run est préservé. Fichiers concernés : `scripts/player.gd`, `scripts/slime.gd`, forme de lame de `scenes/player.tscn` selon D02, tests de combat/clavier/profils/récompenses et parcours si nécessaire. Aucun changement de terrain, sprites, mobilité, économie ou ajout d’arme. Décision RANGE validée par l’humain : 1 RANGE = 24 px = 1,5 bloc depuis la main ; cadence séparée du geste de 0,28 s, interruption sans effacer le cooldown. Recul Slime conservé à 0,12 s sans immunité au contact ni aux impacts. Vérification : import Godot 4.7.2, suites physiques adaptées et régressions, puis essai humain du combat avant clôture.

- **Résultat vérifié :** Sword 0 = 0,5 DMG, RANGE 24 px, départs espacés de 1 s ; geste de 0,28 s conservé et cooldown maintenu après interruption. Green/Purple = 1/2 HP, contact 0,5/1 DMG ; recul et flash de 0,12 s sans immunité. Sprites et terrain conservés ; shader de flash joueur ajouté après l’audit autorisé.
- **Preuves et clôture :** Godot Windows 4.7.2, import, isolation `user://`, 13 suites / 296 contrôles réussis, dont 47 combat et 35 protection ; cinq captures du feedback de dégâts inspectées et 5 contrôles visuels réussis après les deux captures Sword précédentes. Parcours et retours adaptés aux nouveaux combats avec des entrées réelles, sans changer les états du jeu. Logs dans `work/test-results/run-iYLHAGNL/`, journal et learning à jour. Validation humaine obtenue le 28 septembre 2026 : « Je valide la run et les changements. » Revue Jev `READY_FOR_DONE`, puis revue directe des quatre décisions et des preuves originales satisfaisante. Clôture locale DONE ; aucun push, PR ni fusion.

- **Révision après essai humain (28 septembre 2026) :** portée de 16 px jugée trop courte ; nouvelle conversion demandée : 1 RANGE = 24 px = 1,5 bloc de terrain. Dessin et collision étendus ensemble ; test de limite déplacé à la nouvelle pointe. Retest Godot 4.7.2 réussi : 12 suites / 261 contrôles, puis 2 contrôles visuels ; captures gauche/droite actualisées et inspectées. Portée finale validée par l’humain le 28 septembre 2026.

- **Ajustement validé après audit (28 septembre 2026) :** l’humain autorise invulnérabilité joueur 1,20 s (au lieu de 0,85 s), flash blanc 0,10 s puis clignotement alpha 0,25/1 ; recul 0,16 s et hit-stun 0,18 s conservés. Recul des ronces dirigé loin de leur position, repli opposé au regard lorsque les centres sont alignés. Modification complémentaire explicitement autorisée, sans créer les piques de RUN-008. Vérification ajoutée : durée entière et expiration, contacts simultanés, pause/feedback, mort pendant flash, matériau propre à chaque joueur, ronces des deux côtés et au centre. Retest complet réussi : import, isolation, 13 suites / 296 contrôles, plus 5 contrôles visuels. Résultat final validé par l’humain le 28 septembre 2026.

- **Clôture locale (28 septembre 2026) :** critères, tests, bugtest/retest, régressions, journal, learning et validation humaine satisfaits. Commits de gameplay `8e43085`, `b12c4f5`, `e97a526` ; modification humaine `4c7438b` préservée. Aucun nouveau changement de gameplay à la clôture, aucun test relancé pour les seuls documents. RUN-008 reste BACKLOG.

### RUN-008 — Créer les piques fixes solides et borner le vide par niveau

**Priorité : P1 · Statut : DONE · Dépendances : RUN-006 (DONE).**

- **Résultat / scope :** Introduire le piège fixe 0,5 DMG horizontal/vertical ; remplacer le seuil global y>340 par une limite de niveau adaptée. Ne pas supprimer les ronces sans traiter leur usage.
- **Acceptation, test et bugtest :** Contact sur chaque orientation, knockback sans hit-stun/interruption, invulnérabilité ; chute mortelle une fois ; murs grimpables inchangés.
- **Learning pressenti :** Body2D/Area2D, layer/mask et zones létales.
- **Résultat vérifié (28 septembre 2026) :** scène `spikes.tscn` solide sur terrain uniquement, capteur joueur, rotation pour les quatre faces, 0,5 DMG et profil SOLID_TRAP. Deux placements : sol `(1120,224)` et limite droite `(2240,80)`, sans changement des tuiles ni des ronces. `level.gd` possède `void_y=304`, remplaçant la zone Pit et le seuil joueur 340. Import et isolation, 14 suites / 335 contrôles réussis sous Godot 4.7.2 ; deux captures graphiques inspectées. Les parcours et retours restent traversables (vie finale 3 / 2 / 2 / 1,5 HP). **Validation humaine reçue le 28 septembre 2026** : « Ok run 008 vérifiée et validée ». Journal et learning à jour ; RUN-009 non lancée.
- **Périmètre au lancement (28 septembre 2026) :** branche `feature/run-008-solid-spikes` issue de `develop` propre (RUN-007 fusionnée via PR #11). Ajouter une scène de piques fixes orientable et des placements complémentaires sans modifier le terrain ni les ronces. Déplacer la responsabilité du vide vers une limite exportée du niveau, conserver le seuil effectif du slice (304 px, bord supérieur de son ancienne zone Pit). Vérifier contacts et solidité dans quatre orientations, recul/protection/attaque, pause, chute unique et régressions des parcours et murs.

- **Clôture locale (28 septembre 2026) :** gameplay au commit `03f42ba`, 335 contrôles et 2 contrôles graphiques réussis ; journal/learning à jour, validation humaine obtenue. Revue Jev READY_FOR_DONE et inspection directe des critères, logs et limites satisfaisantes. Aucun changement gameplay ni nouveau test requis pour cette clôture documentaire.

### RUN-009 — Automatiser la mort et la reprise

**Priorité : P0 · Statut : DONE · Dépendances : RUN-006, RUN-008 (DONE).**

- **Résultat / scope :** Message anglais « Thou hast perished. », assombrissement 3 s puis fondu/reset ; spawn sûr et vie restaurée, sans appui requis.
- **Acceptation, test et bugtest :** Morts répétées, mort en pause/attaque, aucune double recharge ; attendre au spawn ne tue pas ; gains de tentative actuels perdus une fois.
- **Learning pressenti :** Transitions, timers, rechargement de scène et verrous.
- **Résultat vérifié (30 septembre 2026) :** mort unique, écran assombri « Thou hast perished. » pendant 3 s, fondu noir de 0,4 s puis rechargement automatique. La mort suspend le gameplay, même si elle est déclenchée durant une pause ; la nouvelle scène retire la pause. Gains de tentative perdus, réserve validée conservée. Import, isolation `user://`, 15 suites / 353 contrôles de jeu réussis ; captures de l'écran de mort et du fondu inspectées. Aucune livraison distante autorisée.
- **Périmètre au lancement (30 septembre 2026) :** branche `feature/run-009-auto-respawn` créée depuis `develop` propre. Remplacer uniquement la confirmation manuelle à la mort et ses tests ; conserver la progression validée et le comportement de victoire. Exercices ciblés : délai et fondu, morts répétées, pause/attaque, rechargement unique, retour sûr au spawn, bonus de tentative et régressions clavier/parcours.
- **Clôture locale (30 septembre 2026) :** critères, bugtest/retest, régressions, journal et learning satisfaits ; captures graphiques inspectées. Revue Jev `READY_FOR_DONE` consultative, suivie d'une inspection directe des preuves. Aucune validation humaine explicitement requise pour cette run. Pas de push, PR ni merge.
- **Validation et livraison (30 septembre 2026) :** l'humain confirme « Run validée et PR merged ». La PR #14 contenant `760ad06` est fusionnée dans `develop` au commit `a2ac33c`. RUN-009 reste `DONE` ; aucune run suivante lancée.

### RUN-010 — Installer les bus et les feedbacks élémentaires

**Priorité : P1 · Statut : DONE · Dépendances : RUN-002, RUN-009, RUN-007 (DONE).**

- **Résultat / scope :** Master/Music/Ambient/SFX/UI ; brancher les sons P0 du mouvement, mêlée, dégâts, mort, collecte et mort Slime, en réutilisant provisoirement des sons autorisés.
- **Acceptation, test et bugtest :** Écoute réelle avec actions simultanées, sans clipping ; sons UI non positionnels et sons monde 2D pertinents ; aucun footstep.
- **Learning pressenti :** Bus audio, AudioStreamPlayer2D, formats WAV/OGG et niveaux sonores.
- **Périmètre au lancement (30 septembre 2026) :** branche `feature/run-010-audio-buses` depuis `develop` propre. Sources demandées par l'humain : bibliothèques locales SFX et Music. SFX pris uniquement dans *Pixel Combat* de Helton Yan (CC BY 4.0), compatible avec le dépôt public ; *Minifantasy Dungeon SFX* écarté car sa licence interdit la redistribution des fichiers. Musique Pixabay provisoire pour le slice. Atterrissage, wall slide, sons UI/menu et ambiances restent hors périmètre.
- **Résultat vérifié (30 septembre 2026) :** `default_bus_layout.tres` déclare Master (limiteur −1 dB), Music, Ambient, SFX et UI. Saut, double saut, wall jump, trois swings, trois impacts, trois dégâts joueur, mort, trois pièces et trois morts Slime proviennent de dérivés normalisés par `tools/prepare_audio.py` ; les sons fréquents tournent via `AudioStreamRandomizer`. Joueur non positionnel, Slime et pièces en `AudioStreamPlayer2D`, musique en boucle sur Music. Le son de mort traverse la pause de mort ; l'impact final et l'éclaboussure survivent au Slime supprimé. 16 suites / **377 contrôles** réussis, dont 24 audio. Capture Movie Maker limiteur coupé : pire empilement −5,5 dBFS de crête, aucun écrêtage. Provenance dans `assets/AUDIO_CREDITS.md`.
- **Validation humaine (30 septembre 2026) :** écoute en jeu, « ok pour une première itération ». Bus, routage et branchements validés. **Limites à reprendre dans une run audio ultérieure :** musique trop basse et à remplacer par un autre morceau ; SFX globalement trop forts ; impact d'épée (`sfx_melee_hit`) peu agréable, à remplacer ; sons de saut et de double saut à remplacer. Les bus UI et Ambient existent sans contenu : aucun son UI n'existe encore.
- **Clôture locale (30 septembre 2026) :** critères, tests, bugtest, journal, learning et validation humaine satisfaits ; revue Jev `READY_FOR_DONE` consultative, suivie d'une inspection directe des preuves. Aucune modification après la validation, en dehors de la documentation. Pas de push, PR ni merge.

### RUN-011 — Valider et corriger le socle de production

**Priorité : P0 · Statut : DONE localement · Dépendances : RUN-004, RUN-005, RUN-007, RUN-008, RUN-009, RUN-010 (DONE).**

- **Résultat / scope :** Fermer 0.1.0 après correction des défauts ciblés de ce jalon, sans retouche globale du niveau. Réévaluer le dépôt et détailler les runs de 0.2.0 en fin de recette, en ajustant son enveloppe si nécessaire.
- **Acceptation, test et bugtest :** Import propre, suites adaptées, deux branches et retours, pause/mort ; contrôle graphique 30/60/144 fps et essai humain du saut mural.
- **Learning pressenti :** Tests de physique, différence test ciblé/parcours, reproduction et preuve de régression.
- **Périmètre au lancement (30 septembre 2026) :** branche `feature/run-011-production-foundation` créée depuis `develop` propre à `24213f2`. Vérifier le socle 0.1.0 avec import et suites, parcours aller/retour des deux branches, pause/mort, rendu et comportement à 30/60/144 fps ; corriger seulement les défauts reproduits dans ce périmètre. L'essai humain du saut mural reste requis avant `DONE`. Affiner le découpage de 0.2.0 à partir des constats de la recette.
- **Résultat en VERIFY (30 septembre 2026) :** Godot 4.7.2 : import propre, isolation `user://`, 16 suites / 377 contrôles réussis. Parcours des deux branches, retours et changement de branche, pause, mort et reprise vérifiés. Rendu OpenGL mesuré à 30/60/144 fps, 9 contrôles de comportement et 9 captures 640×360 par cadence ; images représentatives inspectées. Aucun défaut reproduit, donc aucun correctif gameplay. L'humain a essayé le saut mural et répondu « Jouable, je valide ». Le découpage BACKLOG établi à cette date est remplacé par les lots RUN-015–017 le 2 octobre 2026, sans démarrer 0.2.0. Preuves dans `runs-journal.md` et `learning.md`.
- **Clôture locale (30 septembre 2026) :** critères du jalon, bugtest, régressions, journal, learning et essai humain satisfaits. Revue Jev `READY_FOR_DONE` consultative, suivie d'une inspection directe des preuves. Aucun push, PR ni merge de cette branche.

## Compléments réalisés 0.1.0 — Même branche

Les passes **012–014** ont été retenues, réalisées et validées ; la seconde passe **029** est également validée à la clôture finale. Elles améliorent le slice sans implémenter les menus, la progression ou le contenu N1 de 0.2.0. Elles appartiennent toutes à la version **0.1.0**.

### RUN-012 — Personnage et feedbacks visuels du socle

**Lot A · Main agent : Claude Opus 5.5 · Statut : DONE · Dépendances : RUN-011 DONE ; sélection humaine du lot.**

- **Résultat / scope :** Sélection, adaptation et intégration cohérente du chevalier, Sword et animations/feedbacks existants. Conserver sources, licences et contrats gameplay.
- **Décisions avant implémentation dépendante :** Confirmer les assets et le périmètre artistique avant adaptation.
- **Lancement (2 octobre 2026) :** l'humain retient les trois lots 012–014, à exécuter dans l'ordre sur `feature/run-011-production-foundation`, avec validation visuelle et d'écoute groupée en fin de lot C. Aucun chevalier compatible dans la bibliothèque locale (Soldier Zerie ≈ 17×21 px, vue RPG, licence sans redistribution) ; les packs d'effets/icônes inspectés interdisent la redistribution dans un dépôt public, sauf les icônes CC0 de Shade et les fichiers PixelLab de l'humain. **Décision humaine :** générer l'Ashen Knight en pixel art d'après l'artwork du projet (plaques acier, cape rouge, tabard à emblème or), corps ≈ 20×28 px, capsule 10×18, épée (dégâts, portée 24 px, cadence, fenêtre) inchangées. Périmètre : spritesheet idle/course/saut/chute/glissade/attaque/dégâts/mort, épée et traînée pré-rendues, VFX existants (double saut, poussière murale, impact) ; scènes `player.tscn`/`player.gd` côté visuel uniquement.
- **Résultat en VERIFY (2 octobre 2026) :** Ashen Knight généré (`tools/art/knight.py`, 24 frames sur 8 animations), épée en 32 angles avec traînée, étincelle d'impact, anneau de double saut et poussière murale ; animation de mort désormais jouée pendant la pause. Gameplay et collisions inchangés. Import et 16 suites / 377 contrôles réussis ; nouvelle suite `knight_visual` 17/17 et 21 captures inspectées ; suites visuelles existantes réussies. Provenance dans `assets/VISUAL_CREDITS.md`. **Attend la validation visuelle humaine groupée** (choix artistique, ressenti des animations, lisibilité en jeu).
- **Clôture (2 octobre 2026) :** validation humaine groupée « Je valide les 3 runs » ; revue Jev consultative (couverture / vérifications / blocage 0,86 / 0,75 / 0,35 ; Choice READY_FOR_DONE 0,52) puis inspection directe des preuves. **DONE localement** ; pas de push, PR ni merge.
- **Acceptation, tests et bugtest :** Rendu, silhouette, ancrages, transitions d’animation et lisibilité des dégâts ; collisions, portée et mobilité non régressées dans Godot ; validation visuelle humaine.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-013 — Décor et lisibilité du slice

**Lot B · Main agent : Claude Opus 5.5 · Statut : DONE · Dépendances : RUN-012 si retenue, sinon RUN-011 ; sélection humaine du lot.**

- **Résultat / scope :** Harmoniser terrain, décor, Slimes, objets, dangers et HUD existants avec les assets retenus, sans régénération du niveau humain.
- **Décisions avant implémentation dépendante :** Confirmer le choix des ressources, les zones retouchées et la propriété des scènes.
- **Lancement (2 octobre 2026) :** selon la consigne d'enchaînement de l'humain, même principe que RUN-012 : ressources générées par `tools/art/` sur une palette commune (`tools/art/palette.py`), faute de packs redistribuables adaptés. Zones retouchées : habillage du terrain (`terrain_skin.gd`, sans modifier `Terrain`, ses tuiles ni ses collisions), arrière-plan en parallaxe et accessoires narratifs existants (`kingdom.gd`, positions conservées), Slimes, pièce, piques, ronces, bac, porte et HUD. Formes, valeurs et placements de gameplay inchangés. Propriété : sprites des créatures/objets/icônes et des dangers/porte/bac délégués à deux subagents (scripts générateurs distincts, aucune scène) ; intégration des scènes par le main agent.
- **Résultat en VERIFY (2 octobre 2026) :** terrain autotilé sur la `TileMapLayer` intacte (deux thèmes, profondeur), ciel/lune de sang et parallaxe, accessoires narratifs générés aux mêmes positions, Slimes, pièce, piques, ronces, bac, porte et HUD (cœurs, icône de pièce, titre de mort rouge) harmonisés ; gameplay, collisions et textes inchangés. Import et 16 suites / 377 contrôles réussis ; dix cadrages 640×360 capturés et inspectés ; générateurs reproductibles. **Attend la validation visuelle humaine groupée.**
- **Clôture (2 octobre 2026) :** validation humaine groupée « Je valide les 3 runs » ; revue Jev consultative (couverture / vérifications / blocage 0,86 / 0,79 / 0,44 ; Choice READY_FOR_DONE 0,45) puis inspection directe des preuves. **DONE localement** ; pas de push, PR ni merge.
- **Acceptation, tests et bugtest :** Comparer les branches, retours, mur, bac, pièges et overlays à 640×360 ; vérifier contraste, collisions et parcours ; validation visuelle humaine.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-014 — Finition visuelle et raccord sonore du socle

**Lot C · Main agent : Claude Opus 5.5 · Statut : DONE · Dépendances : lots A/B retenus validés ; sélection humaine du lot.**

- **Résultat / scope :** Troisième passe éventuelle de cohérence visuelle/animation et, si retenu, raccord du mix : musique à remplacer et relever, SFX à baisser, impact Sword et sauts à remplacer selon les retours RUN-010. Les défauts audio non traités ici restent obligatoires en RUN-027.
- **Décisions avant implémentation dépendante :** Fixer les retouches complémentaires réellement nécessaires après A/B.
- **Lancement (2 octobre 2026) :** l'humain a demandé d'enchaîner 012–014 avec une validation groupée ; A et B sont en VERIFY, leur validation humaine sera donc obtenue avec C (écart assumé à la dépendance « A/B validés », à confirmer lors de la revue). Retouches retenues après A/B : feedbacks P0 encore absents (éclat de collecte de pièce, éclaboussure de mort des Slimes) et variation des arbres ; audio selon les retours RUN-010 (musique remplacée et relevée, SFX baissés, impact Sword, saut et double saut remplacés), sources CC BY / Pixabay déjà admises, analyse des candidats déléguée à un subagent.
- **Résultat en VERIFY (2 octobre 2026) :** éclat de collecte de pièce, éclaboussure de mort des Slimes, arbres variés. Audio : impact Sword `Gut Punch`, saut `Bamboo Whip`, double saut `Whoosh Sweep`, musique `nojisuma — Dreamer` bouclée à 156 s ; SFX −5 dB (crête −8 dBFS), musique −13 LUFS. Pack Synthwave AlkaKrab exclu (licence). Import et 16 suites / 377 contrôles réussis ; suite `feedback_visual` 4/4 et suites visuelles relancées ; mix mesuré sans écrêtage (crête −10,5 dBFS, musique seule −33 dB RMS). **Attend la validation humaine groupée 012–014 : rendu en jeu et écoute** (point de boucle, timbres, équilibre).
- **Clôture (2 octobre 2026) :** validation humaine groupée « Je valide les 3 runs » ; revue Jev consultative (couverture / vérifications / blocage 0,83 / 0,80 / 0,31 ; Choice READY_FOR_DONE 0,61) puis inspection directe des preuves. **DONE localement** ; pas de push, PR ni merge. Sons de saut et double saut encore jugés trop « sci-fi » : reportés à RUN-027. Ancienne musique conservée pour le futur menu.
- **Acceptation, tests et bugtest :** Inspection intégrée du slice, écoute en jeu si audio modifié, mesure du mix sans écrêtage, provenance et parcours concernés ; validation humaine du rendu et de l’écoute.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-029 — Seconde passe visuelle du socle

**Lot A2 · Main agent : Claude Opus 5.5 · Statut : DONE · Dépendances : RUN-012–014 DONE ; demande humaine du 2 octobre 2026.**

Identifiant pris après la dernière réserve pour ne pas renuméroter les lots suivants ; le plan passe à **29 identifiants** (limite 30). Complément 0.1.0 sur `feature/run-011-production-foundation`, à la demande explicite de l’humain (« toujours sur la même branche »). N’anticipe ni menus, ni dialogues, ni progression 0.2.0.

- **Résultat / scope :** Ashen Knight plus détaillé et plus dynamique (idle en garde de combat, course, sauts, glissade murale refaite, dégâts, mort, animations plus fluides) ; attaque en enchaînement de **trois mouvements d’épée** qui se poursuit tant que F est maintenu ; terrain, décor, parallaxe et accessoires plus riches ; éléments, animations et VFX enrichis (Slimes, pièce, pièges, bac, porte, impacts) ; HUD retravaillé avec icônes générées ou issues de la bibliothèque locale CC0. Suppression du bandeau inférieur d’informations : il ne reste qu’un bandeau de dialogue masqué, réservé aux futures lignes de PNJ. Blueprint Studio utilisé seulement là où il améliore réellement le rendu, avec provenance consignée.
- **Contrats gameplay conservés :** Sword 0,5 DMG, cadence 1 s, geste 0,28 s, fenêtre de contact, lame 24 px depuis la main, déduplication et occlusion inchangées ; chaque coup tenu reste un hit selon ATK SPEED (`docs/01`). Les trois mouvements alternent visuellement à chaque hit et balaient le même arc pendant la même fenêtre de contact. Collisions, valeurs, placements du niveau et textes existants inchangés, sauf retrait des messages du bandeau inférieur ; l’invite de la porte devient une indication contextuelle près de la porte.
- **Propriété :** chevalier (`tools/art/knight.py`, `player.gd`/`player.tscn` côté visuel) et intégration finale par le main agent ; décor (`tools/art/world.py`, `backdrop.gd`, `kingdom.gd`, `terrain_skin.gd`), éléments/VFX (`creatures.py` hors icônes HUD, `hazards.py`, `vfx.py` et scènes d’objets côté visuel) et UI (`hud.tscn`, `hud.gd`, `health_hearts.gd`, messages de `level.gd`, nouveau `tools/art/ui.py`) délégués à trois subagents Sonnet sur fichiers distincts ; `vertical_slice.tscn` réservé au main agent ; appels Godot sérialisés par verrou.
- **Acceptation, tests et bugtest :** les 16 suites existantes réussies sans assouplir d’assertion gameplay ; suites visuelles mises à jour (sélection des animations, enchaînement des trois mouvements pendant le maintien, absence du bandeau hors dialogue) ; captures 640×360 du slice inspectées ; lisibilité joueur/ennemis/dangers, ancrages et filtrage vérifiés ; provenance et licences consignées. **Validation humaine requise** : rendu artistique, ressenti des animations et de l’attaque, lisibilité en jeu.
- **Résultat en VERIFY (2 octobre 2026) :** chevalier redessiné sur squelette (`tools/art/knight.py`, frames 64×64) : garde de combat, course épée traînante, montée, chute, atterrissage avec poussière, glissade face au mur (main contre le mur, pied en appui), dégâts, mort avec épée lâchée ; enchaînement taille / revers fendant / frappe à deux mains, poursuivi tant que F est maintenu, avec haut du corps superposé aux jambes en course et en l’air. Gameplay inchangé. Décor, éléments/VFX et HUD enrichis par trois subagents Sonnet ; bandeau inférieur supprimé, `DialogueBanner` masqué, invite de porte au-dessus du sceau, voile de mort allégé. Blueprint Studio : 0 crédit utilisé. Import propre ; 16 suites / **377 contrôles** réussis ; `knight_visual` 31, `hud_visual` 11, `feedback_visual` 7 et autres suites visuelles réussies ; cadences 30/60/144 fps 9/9 ; générateurs reproductibles (MD5). La validation alors attendue est reçue lors de la clôture finale ci-dessous.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel.

- **Clôture finale (2 octobre 2026) :** l’humain valide toutes les runs réalisées. Audit final sur `40fd477` : import, isolation, 377 contrôles de jeu, 49 contrôles visuels non headless, 23 WAV et 4 tests du routeur réussis ; captures inspectées et revue indépendante sans défaut concret. Jev propose READY_FOR_DONE ; revue directe des preuves satisfaisante, aucun test obligatoire restant ni blocage. RUN-029 **DONE**. Preuves et limites acceptées dans `runs-journal.md` ; 0.1.0 clôturée, PR autorisée.

## Version 0.2.0 — Premier niveau et boucle de reprise

**Statut : validée localement, RUN-015–017 DONE ; PR #18 ouverte vers develop, non fusionnée.** **Prérequis :** fusion dans `develop` vérifiée ; D03–D05 avant leur code. Les critères ci-dessous sont ceux du jalon complet RUN-015–017, pas de RUN-015 seule.

**Repères documentaires :** 01, 03, 04, 05, 07, 08, 09, 10, 13 dans `docs/`.

**Critères de validation du jalon (conservés lors du regroupement) :**

- [x] N1 jouable du menu à la sortie : Spirit, explications, Green/Purple, piques/vide, une potion et coffre gratuit Longbow 0.
- [x] Coins et shards distincts ; équipement acquis persistant selon contrat validé, aucune sauvegarde joueur perdue silencieusement.
- [x] New Game/Continue/Controls/Quit, pause et dialogues entièrement clavier, textes anglais, aucune superposition de modales.
- [x] N1 court et facile, spawn sûr, sortie à 12 coins ; transition testée vers fixture, aucun N2 final revendiqué.

### RUN-015 — Reprise, progression et interface clavier

**Lot D · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-011 DONE et verrou de branche levé.**

- **Préparation (3 octobre 2026) :** lancement autorisé, dépôt initial propre sur `develop` (`f997bcb`), branche commune `feature/v0.2.0-reprise-equipment` créée. D03 (persistance et ordre de dépense) et D05 (interface) sont validés par l’humain le 3 octobre ; le contrat intégral, migration v1 comprise, est ensuite validé le 3 octobre ; passage READY puis ACTIVE ; propositions concrètes dans [RUN-015_CONTRACT_REVIEW.md](docs/RUN-015_CONTRACT_REVIEW.md). Partie technique implémentée et vérifiée ; état BLOCKED sur la contribution artistique/audio Claude requise. Le réglage exact Sol Medium de la session ne peut pas être confirmé avec les informations exposées. Contribution artistique/audio des menus réservée à Claude ; handoff et propriété dans [RUN-015_CLAUDE_HANDOFF.md](docs/RUN-015_CLAUDE_HANDOFF.md).

- **Checkpoint technique (3 octobre 2026) :** sauvegarde v2 et migration explicite avec copie originale, transactions durables, séparation coins/shards, menu principal/pause/contextes clavier. Import + 18 suites / **445 contrôles de jeu + 1 isolation** réussis ; pilote menus non headless **26/26**, sept captures inspectées à 640×360. Corrections/retests : Escape ouvrait/fermait dans la même frame, chargement après victoire héritant de pause, sauvegardes de remplacement successives, mort pendant E tenu. **Pas de DONE ni de VERIFY complet** : habillage/logo/fond et sons UI P0 par Claude, validation artistique/playtest humain et revue Jev de clôture restent dus.

- **Reprise après Claude (3 octobre 2026) :** passe artistique/audio `1a6ffea` inspectée et validée par l’humain. Logo accepté avec retouche de détail reportée à la prochaine passe Claude (RUN-027). Thème de menu demandé : dérivé existant de `welc0mei0 …148338.mp3`, bouclé et routé Music ; tests menus avec rendu **31/31**, dont passage effectif de fin de piste, Controls, entrée niveau et retour menu. Revue Jev READY_FOR_DONE (couverture 0,81, vérification 0,72, blocage 0,37 ; Choice 0,38, distribution 0,59/0,38/0,03), puis inspection des preuves et validation humaine : DONE localement.

- **Résultat / scope :** Regrouper contrats d’état, séparation coins/shards, tentative/état durable, sauvegarde versionnée, exclusivité des modales, New Game/Continue/Controls/Quit et pause Reprendre/Recommencer/Quitter.
- **Décisions avant implémentation dépendante :** D03–D05 : événements de sauvegarde, ancien bonus, banque/gains, uniques/dialogues, priorité et annulation des modales, slots ; décisions humaines avant schéma/code.
- **Acceptation, tests et bugtest :** Matrice mort/sortie/fermeture/rechargement/dépense ; migration v1 explicite, corruption/version inconnue/échec disque ; Continue sans save, reprise à froid, restart ; focus et rendu clavier, aucun input traversant une modale ni double déclenchement.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-016 — Équipement N1, Longbow et récompenses

**Lot E · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-015 DONE.**

- **Checkpoint technique (3 octobre 2026) :** Longbow0 (1 DMG / 1,5 s / 320 px), A/deux slots, projectile balayé, coffre fixe gratuit, refus/fermeture/reset/retry disque, potion 0,5 HP conservée à vie pleine et reprise durable de l’arc implémentés. Import + **20 suites / 495 contrôles + 1 isolation** réussis, puis Longbow final **26/26** avec deux contrôles supplémentaires de glissade murale ; récompenses avec rendu **21/21** et trois captures inspectées. Revue indépendante sans défaut concret. **À ce checkpoint, BLOCKED sur les assets/feedbacks P0 Claude** ; [handoff et propriété](docs/RUN-016_CLAUDE_HANDOFF.md). Labels/repères de test et flèche sans rendu ne valent pas assets livrés ni validation artistique ; pas de DONE/VERIFY complet.
- **Reprise finale (3 octobre 2026) :** passe Claude `2953b37` livrée et validée par l’humain. Revue globale RUN-015–016 et deux revues indépendantes sans défaut bloquant ; assertion shard corrigée ; **20 suites / 499 contrôles + 1 isolation** réussis. Limites acceptées : sons approximatifs et mix acquisition / mort arc à reprendre en RUN-027 ; placement coffre/potion en RUN-017. Rendu : 129 contrôles + pilote visuel 11 PASS, captures inspectées. Revue Jev READY_FOR_DONE (couverture 0,80 ; vérification 0,74 ; blocage 0,27 ; Choice 0,55), inspection des preuves et validation humaine : DONE. Livraison PR autorisée ; fusion séparée.
- **Résultat / scope :** HUD vie/coins/shards, deux slots et touche A, Sword conservée, Longbow 0 effectif, coffre tuto gratuit à récompense fixe et potion mineure.
- **Lancement (3 octobre 2026) :** autorisé par la demande initiale d’enchaînement après RUN-015 revue/validée, conditions satisfaites. Même branche ; ownership gameplay/persistance à Codex, assets/feedbacks à Claude.
- **Décisions avant implémentation dépendante :** Appliquer les contrats RUN-015, y compris persistance et disposition des slots.
- **Acceptation, tests et bugtest :** HUD exact après collecte/dépense/mort/reprise à 640×360 ; F maintenu tire toutes les 1,5 s, 1 DMG, portée 20 blocs, disparition cible/terrain/portée ; gauche/droite, pause, changement d’arme, occlusion et impact unique ; coffre accepter/refuser/fermer sans doublon/upgrade ; potion 0,5 HP conservée si vie pleine.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-017 — The Eidolon Vale et recette 0.2.0

**Lot F · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-015–016 DONE.**

- **Lancement (3 octobre 2026) :** demande humaine « Lancer la run 017 ». Baseline propre `develop` (`420f88b`, PR #17 fusionnée), branche `feature/run-017-eidolon-vale`. Codex possède dialogues/tutoriels fonctionnels, intégration N1 et recette ; contribution artistique Spirit/panneau/feedbacks réservée à Claude avec handoff avant édition. Réglage exact du main agent Sol Medium non exposé. Aucun push/PR/merge autorisé pour ce lot.
- **Checkpoint technique (3 octobre 2026) :** N1 hérité du slice, neuf phrases Spirit animées/skippables, quatre tutoriels contextuels persistants, erreur disque/retry, anciens saves vers N1, coffre/potion séparés des pièces ; terrain humain conservé. Import + 22 suites / **567 contrôles de jeu**, deux processus fermeture/Continue **7 contrôles**, isolation **1** ; total **575**, code 0 sans erreur/fuite. Rendu **11/11**, six captures inspectées ; fermeture graphique après acquisition **4/4**. Bug audio de fermeture corrigé/retesté (arrêt des voix et garde du reveal retardé). **BLOCKED sur contribution artistique Claude** : Spirit/portrait/repos/dialogue et contrôle des feedbacks P0 de N1 ; [handoff](docs/RUN-017_CLAUDE_HANDOFF.md). Après cette passe : recette/rendu, playtest humain N1 et validation artistique, puis Jev avant DONE. 0.2.0 non validée ; aucun push/PR/merge.
- **Seconde passe (3 octobre 2026) :** contribution Claude `1fbb730` validée humainement ; nouvelle passe autorisée sur la même branche, retour ACTIVE puis checkpoint technique terminé. Space avance une phrase sans son ; délai +2 s par phrase ; résurrection New Game uniquement, claim durable avant lecture ; Spirit caché puis apparition après 32 px vers l'avant, dialogue, disparition à 96 px (réglable). Hooks dédiés et fallbacks vérifiés : import + 24 suites **625 contrôles de jeu**, deux processus froids **8**, isolation **1**, total **634 PASS** ; cinématiques rendues **29/29**, N1 rendu **11/11**, sept captures de séquence inspectées. **BLOCKED sur les nouveaux assets/animations et cue Claude**, [contrat de seconde passe](docs/RUN-017_CLAUDE_HANDOFF_02.md). Mort/restart/Continue ne rejouent pas la résurrection. Aucun son skip ; cue final d'apparition encore absent. Revue ciblée indépendante sans défaut concret. Validation de la première contribution ne vaut pas validation de cette nouvelle passe, ni clôture du playtest N1.
- **Reprise finale (3 octobre 2026) :** passes Claude `36a6251` et `b825d11` validées humainement, ainsi que le playtest N1 (difficulté/rythme, deux chemins jusqu’à sortie). Pose de course figée corrigée : idle animé pendant apparition/dialogue, gameplay bloqué ; mode de mort indépendant conservé. Import + 24 suites **631 contrôles de jeu**, deux processus froids **8**, isolation **1**, total **640 PASS**, code 0 sans erreur/fuite ; rendu cinématiques **35/35**, N1 **11/11**, captures inspectées. Revues indépendantes sans défaut résiduel ; ancien code reproduit trois échecs de pose. Revue Jev de clôture puis PR vers `develop` autorisées ; aucune fusion ni autre run autorisée.
- **Revue de clôture (3 octobre 2026) :** Jev READY_FOR_DONE (couverture 0,81 ; vérifications 0,68 ; blocage 0,37 ; Choice READY 0,47 /BLOCKED 0,31 /VERIFY 0,22, confiance 0,20). Probabilités consultatives ; inspection des preuves originales et validation humaine reçue : aucun défaut bloquant, dossier complet. VERIFY pendant livraison PR, puis DONE après sa création.
- **Livraison et clôture (3 octobre 2026) :** correctif/revue `49fa11f`, branche poussée et [PR #18](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/18) ouverte vers develop ; PR OPEN, non draft, mergeable lors du contrôle. Passes Claude, playtest humain, recette, régressions, Jev/inspection, journal et learning complets : DONE ; jalon 0.2.0 validé localement. Aucune fusion ni RUN-018 lancée.
- **Résultat / scope :** Spirit, dialogue anglais animé et avance phrase par phrase via Space, tutoriel contextuel ; adaptation du slice en N1 court et facile avec coffre/potion éloignés des pièces, Slimes, dangers, tir et sortie ; résurrection initiale et apparition/disparition scénarisée ; art/audio P0 et recette complète.
- **Décisions avant implémentation dépendante :** Contrats RUN-015 ; ne pas présenter la fixture comme N2 final.
- **Acceptation, tests et bugtest :** New Game jusqu’à sortie à 12 coins puis fixture ; branches/retours, spawn sûr après mort, dialogue immobilisant sans danger puis reprise, états vus conformes au contrat ; coffre accepté/refusé, potion pleine/blessée, tir, pause, Controls, fermeture/Continue à froid ; aucune perte d’équipement ni modale superposée ; playtest humain N1.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

## Version 0.3.0 — Économie, bestiaire et exploration N2–4

**Statut : RUN-018–020 DONE ; RUN-021 VERIFY après reprise de navigation des élites du 7 octobre ; jalon non validé.** **Prérequis :** 0.2.0 validée (satisfait) ; D01, D02, D04, D06, D07 selon les systèmes.

**Repères documentaires :** 01, 02, 03, 04, 05, 06, 07, 08, 13 dans `docs/`.

**Critères de validation du jalon (conservés lors du regroupement) :**

- [x] Coûts common/rare, récompenses et upgrades conformes à une table validée ; Legendary encore exclu du pool jusqu’à son implémentation.
- [x] Armes standard hors Fire Gauntlet utilisables et persistantes ; soins de terrain et drops de soin testés.
- [ ] N2 terminé à 18 coins, Red/Bloated Slime, piques rétractables et trappes ; N1 reste traversable.

- [ ] Warrior, Archer, Sorcerer, Swarm et Chud ont chacun leurs tests de comportement ; télégraphies et SFX P0 intégrés.
- [ ] Tourelles, plantes, Magic Shield, mécanismes, portes secondaires, secrets permanents et HP bonus opérationnels.
- [ ] N3/N4 jouables à 25/32 coins ; N4 contient son secret, sa potion majeure, son rare chest et son HP bonus ; toutes les dépenses optionnelles restent compatibles avec la sortie.

### RUN-018 — Économie et équipement standard

**Lot G · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-017 DONE ; 0.2.0 validée.**

- **Lancement en préparation (5 octobre 2026) :** demandé par l’humain, baseline propre `develop` `6bb15b4`, branche `feature/run-018-standard-equipment`. Les six critères de 0.3.0 sont vérifiés et répartis entre 018–021 ; ils ne sont pas encore satisfaits. Inspection du code et audit délégué en lecture seule : tables D02/D04 absentes, seuls Sword0/Longbow0, coffre tuto et potion mineure sont intégrés. Proposition complète dans [RUN-018_CONTRACT_REVIEW.md](docs/RUN-018_CONTRACT_REVIEW.md), dont exception explicite au paiement/acquisition atomique de RUN-015 pour l’ouverture payante avant choix. **Condition de reprise : validation humaine du contrat ou corrections des tables/règles proposées**, puis READY → ACTIVE pour le code dépendant. Art/assets réservés à Claude avec [contrat de contribution](docs/RUN-018_CLAUDE_HANDOFF.md), préparé mais non transmis ; fichiers partagés non attribués à deux éditeurs. Aucun changement gameplay, push, PR ou fusion. Le réglage exact Sol Medium du main n’est pas exposé : Je ne sais pas. Luna Medium indisponible (capacité) ; audit repris par un explorateur avec modèle hérité.

- **Reprise (5 octobre 2026) :** contrat complet validé par l’humain (« Je valide le contrat »), exception paiement à l’ouverture comprise. READY puis ACTIVE ; implémentation technique et tests en cours, ownership délégué catalogue/économie et runtime équipement séparé, intégration niveau/UI à Codex. Contrat Claude préparé, APIs à stabiliser avant handoff d’intégration.

- **Checkpoint technique (5 octobre 2026) :** tables huit armes0–5, runtime et slots persistants, common/rare payants et upgrade/refus, prix/poids filtrés, potion majeure et drops de soin implémentés selon contrat. Import +27 suites et cinq sessions froides **1740 PASS**, code0 sans erreur/fuite ; correctif final présentation tir au remplacement couvert par recette ciblée **482 armes +47 combat +26 Longbow**, code0. Transactions avec rendu **29/29**, deux captures inspectées à640×360. Revue indépendante sans défaut concret résiduel. Items nouveaux testés en fixture, placements N2–4 aux runs suivantes. **BLOCKED sur assets/animations/icônes/feedbacks Claude** : [handoff prêt](docs/RUN-018_CLAUDE_HANDOFF.md), APIs et propriété d’intégration explicitement remises ; aucun message à un chat Claude envoyé. Codex cesse d’éditer les fichiers partagés jusqu’au retour. Art/écoute et essai humain armes/coffres, recette après intégration puis Jev restent requis avant DONE. Journal et learning à jour ; aucun push/PR/merge ni019.

- **Retour Claude et recette Codex (5 octobre 2026) :** contribution `ff5caa0` présente sur branche propre, [manifeste relu/corrigé](docs/RUN-018_ASSET_MANIFEST.md). Corps du chevalier en trois couches, armes à portée exacte, Knives, coffres/UI/potion et sons intégrés ; crédits ajoutés, preview potion non référencée retirée. Revue indépendante sans défaut concret du gameplay. Recette Codex Godot4.7.2 : import +27 suites,19 contrôles à froid et isolation, **1743 PASS**, code0 sans erreur/fuite ; pilote rendu **68/68**, captures représentatives inspectées. Tailles20 PNG et format/niveaux12 WAV vérifiés. **VERIFY**, pas DONE : validation humaine du rendu, écoute et essai armes/coffres encore requis puis Jev/inspection de clôture. Gestes de mêlée partagés et sons approximatifs signalés au manifeste ; pas de push/PR/merge ni019.

- **Clôture locale (5 octobre 2026) :** l’humain confirme « J’ai fait vérifications et je valide la run. » Validation artistique/sonore et essai requis acquis, sans inventer les actions détaillées du playtest. Recette1743 PASS et rendu68/68 relus ; revue Jev READY_FOR_DONE, puis inspection directe des critères/preuves satisfaisante. Journal/learning à jour, aucun défaut bloquant identifié : **DONE**. Objets nouveaux en fixtures ; placements N2–4 en RUN-020. Aucun push/PR/merge ni lancement RUN-019 ; jalon0.3.0 encore incomplet.

- **Résultat / scope :** Tables d’armes jusqu’au niveau 5, mêlée standard et Throwing Knives, common/rare chests, coûts/poids, choix/refus/upgrades, potion majeure et drops de soin.
- **Décisions avant implémentation dépendante :** D02/D04 : stats et ATK SPEED positif, croissance prix/poids, base banque/gains, drops/farm.
- **Acceptation, tests et bugtest :** Cadence/portée/dégâts de chaque arme ; tirages reproductibles, coût et refus sans double débit/récompense ; achat puis mort/fermeture, soins pleine/blessée, reprise ; Legendary exclu des pools jusqu’à RUN-023.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-019 — Menaces et exploration N2–4

**Lot H · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-018 DONE.**

- **Préparation autorisée (5 octobre 2026) :** demande humaine « Lancer run 019 ». Baseline propre develop `288b518`, RUN-018 intégrée via PR #21 ; branche `feature/run-019-threats-exploration` créée. Inspection directe et deux audits Luna Medium en lecture seule : nouveaux ennemis/systèmes encore absents, sources de dégâts et flags v2 réutilisables. [Contrat concret proposé](docs/RUN-019_CONTRACT_REVIEW.md) pour D01/D06/D07 : +1 CURRENT en même temps que MAX, aggro avec visibilité et retour sans saut, quatre Skulls et budget de quatre shards par zone/tentative, Shield rafraîchi sans cumul, secrets mêlée/tir, portes/mécanismes de tentative. Ces choix ne sont pas encore validés. **Condition de reprise : validation du contrat ou corrections précises**, puis READY → ACTIVE. [Contribution Claude préparée](docs/RUN-019_CLAUDE_HANDOFF.md), sans message ni remise de fichiers partagés. Aucun changement gameplay/test runtime, push/PR/merge ni RUN-020. Réglage exact Sol Medium du main non exposé : Je ne sais pas.

- **Reprise (5 octobre 2026) :** contrat validé intégralement (« Je valide le contrat décidé pour la run »), D01/D06/D07 et budget Skull compris ; READY puis ACTIVE. Ownership séparé : familles ennemis, pièges, nouveaux objets d’exploration aux workers ; intégration joueur/niveau/persistance et recette finale à Codex root. Aucun message à un chat Claude ni remise de fichiers partagés à ce stade.

- **Checkpoint technique (5 octobre 2026) :** familles ennemis N2–4, swarm bornée, pièges, Shield, secrets/HP durables et accès coins/mécanismes implémentés en fixtures. Recette Godot4.7.2 isolée : import+31 suites+8 processus froids+isolation, **1939 PASS**, code0 sans erreur/fuite. Correctifs de revue couverts ; après distinction des portes et assertion d'occlusion mêlée : intégration **42/42**, reprise froide **15/15**, rendu **47/47**, captures640×360 inspectées. Dessins/Red teinté provisoires, aucun SFX nouveau. **BLOCKED sur contribution Claude P0** : [handoff technique et propriété remis](docs/RUN-019_CLAUDE_HANDOFF.md), sans message envoyé ; Codex cesse les éditions partagées. Après contribution, régression/recette et validation humaine art/écoute/essai puis Jev/inspection restent requis. Journal/learning à jour, aucune construction N2–4 réelle, pas de DONE/push/PR/merge ni020/021.

- **Retour Claude et audit Codex (5 octobre 2026) :** contribution `d42804d` reçue et passe validée en l’état par l’humain. Deux revues indépendantes et recette root : 37 PNG/37 WAV conformes, 43 sources audio présentes, crédits intégrés. Collisions élites20×22 conservées (Art Bible visuelle, aucun défaut physique démontré). État initial dangereux des piques reproduit en échec puis corrigé ; drainage audio de la suite pièges appliqué. Import+31 suites+8 processus froids+isolation : **1943 PASS**, code0 sans erreur/fuite ; rendu **47/47**, captures inspectées. **VERIFY** : aucun blocker technique identifié ; playtest humain requis non présumé par la validation de la seule passe Claude, puis Jev/inspection avant DONE. Journal/learning à jour, aucun push/PR/merge ni020/021.

- **Validation et revue de clôture (5 octobre 2026) :** l’humain valide la run et autorise la PR, en signalant l’absence d’essai direct des nouveaux mobs faute de scène debug accessible. Limite enregistrée ; tests automatisés et rendu ne sont pas présentés comme un essai humain. Jev READY_FOR_DONE (couverture0,70 ; vérification0,59 ; blocage0,51 ; confiance0,08), puis inspection directe des preuves satisfaisante. **VERIFY pendant livraison PR**, aucune fusion ni RUN-020 autorisée.

- **Livraison et clôture (5 octobre 2026) :** branche poussée, [PR #22](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/22) ouverte vers develop. Critères techniques, recette1943 PASS/rendu47, corrections/revue, crédits/journal/learning et validation humaine avec limite acceptée complets : **DONE**. PR non fusionnée ; RUN-020/021 non commencées.

- **Résultat / scope :** Red/Bloated Slime ; Warrior, Archer, Sorcerer, Swarm et Chud ; piques rétractables, trappes, tourelles/plantes, Magic Shield, secrets permanents, mécanismes, portes secondaires et HP bonus. Implémenter par familles testées dans le même lot, avec télégraphies/SFX P0.
- **Décisions avant implémentation dépendante :** D01/D06/D07 : effet bonus MAX HP sur CURRENT HP, aggro/ligne de vue, plafonds et vie des invocations, cumul Shield et déclencheurs de secrets.
- **Acceptation, tests et bugtest :** Tests propres à chaque comportement puis interactions : aggro/bords/retour, invocations bornées et récompenses, pièges cycliques, pause/mort, bouclier, déclencheurs, reset des mécanismes et persistance des secrets/HP ; sorties financièrement accessibles.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-020 — Construction et recette de Blight Town à Forbidden Graveyard

**Lot I · Main agent : Codex GPT-6.1 Sol Medium · Statut : DONE · Dépendances : RUN-018–019 DONE.**

- **Lancement (5 octobre 2026) :** demande humaine d’exécuter RUN-020 puis RUN-021 sur la même feature avec délégation Claude. Baseline propre `develop` `6a1b279`, PR #22 fusionnée ; branche `feature/run-020-021-campaign`. Inspection mécanique et préanalyse Claude Code Opus5.5 en lecture seule réellement exécutées. Noms de docs/03 retenus (Blight Town, Black Forest, Forbidden Graveyard), Ancient Spirit conservé conformément au lore et au N1 existant. Construction scènes N2–4 déléguée ; root possède raccordement, HUD/coût/caméra, tests et docs ; Claude reçoit des fichiers de présentation distincts. Réglage exact Sol Medium du root non exposé : Je ne sais pas. RUN-021 autorisée après clôture020, pas encore active. Aucun push/PR/merge autorisé.

- **Résultat vérifié (5 octobre 2026) :** N2–4 fixes éditables et raccord N1→N4, coins24/32/40, sorties18/25/32 ; exploration N4 et budgets optionnels conformes. Présentation/ambiances livrées réellement par Claude Opus5.5 et sous-agent Sonnet5.5 puis intégrées par root. Recette Godot4.7.2 : **2207 PASS/45 RESULT**, 33 suites +11 sessions froides +isolation, code0 sans erreur/fuite ; transactions rendues178/178 et pilote visuel/audio33/33. Parcours physique complet19/19 inclus dans la recette, sans téléportation ni suppression d’ennemis. Revue Claude des12 captures et audit statique sans défaut bloquant concret. Preuves/corrections au journal, [manifeste](docs/RUN-020_ASSET_MANIFEST.md) et [guide de playtest](docs/RUN-020_PLAYTEST.md).
- **Retours du 6 octobre 2026 :** playtest reçu, validation globale refusée : manque de contenu/linéarité N2–4, aggro/swarm, tir, Shield et silhouettes élites à corriger. Retour ACTIVE. Correctifs techniques et [contrat Claude de reprise](docs/RUN-020_CLAUDE_HANDOFF_02.md) ; [review et proposition munitions](docs/RUN-020_PLAYTEST_REVIEW.md). Aucune modification de layout/visuels par Codex. Validation du nouveau résultat, recette après Claude puis Jev/inspection restent nécessaires ; aucun DONE anticipé. RUN-021 reste autorisée après clôture020 sur cette même branche ; aucun push/PR/merge autorisé.
- **Checkpoint technique du 6 octobre :** aggro/swarm, réduction du tir, Shield universel hors vide et orthographe corrigés ; recette composée **2225 PASS /45 RESULT** (33 suites,11 sessions froides,isolation), plus récompenses rendues21/21. Pilote N1–4 adapté par inputs après un échec documenté, finalement19/19. Aucun layout ni asset d’élite modifié. Contrat Claude prêt mais non exécuté ; munitions retenues uniquement pour un contrat dédié ultérieur. RUN-020 reste ACTIVE en attente de cette contribution et du nouveau playtest.

- **Checkpoint final du 6 octobre : VERIFY.** Reprise Claude intégrée, fixtures et guide adaptés ; corps élites/contact/lisibilité corrigés et raccord sous arche N4 réparé localement. Recette composée **2254 PASS /46 RESULT** (34 suites,11 sessions froides,isolation), variantes basses19/19 et hautes21/21, achat4/HP N4 réellement exercés ; rendu final57/57, élites20/20, N1 rendu11/11. Aucun échec/erreur/fuite dans les logs finaux ; preuves et limites au journal. Le playtest humain des nouvelles routes, du rythme, des sauts et des visuels reste obligatoire ; Jev/inspection de clôture après cette validation. Aucune autre passe technique identifiée actuellement ; RUN-021 attend DONE020, sans lancement anticipé ni push/PR/merge.

- **Clôture humaine (6 octobre 2026) :** « Je valide la run 020 en l’état. Clôturer et lancement run 021. » Résultat du checkpoint `7079124` accepté, sans inventer de détail de parcours humain. Revue Jev exécutée puis preuves originales inspectées : READY_FOR_DONE consultatif à faible confiance, aucune vérification obligatoire restante pour ce résultat accepté. RUN-020 DONE localement. Les remarques sur taille cible, portée/aggro des tireurs, tir joueur, animation Archer, poursuite des élites et audio sont affectées explicitement à RUN-021 ; elles ne sont pas déclarées corrigées. Six fichiers modifiés depuis le checkpoint restent une baseline humaine préservée, hors commit de clôture. Ni 0.3.0, ni push/PR/merge validés par cette clôture.

- **Résultat / scope :** Construire et peupler N2 Blight Town, N3 Black Forest et N4 Forbidden Graveyard ; raccorder N1–4 et toutes les récompenses/ambiances requises.
- **Décisions avant implémentation dépendante :** Harmoniser les noms avant contenu (D10) ; suivre la répartition docs/03–04.
- **Acceptation, tests et bugtest :** Sorties à 18/25/32 coins ; secret, potion majeure, rare chest et HP bonus de N4 ; parcours N1–4, achats/refus, dépenses optionnelles compatibles avec sortie, morts/reset/rechargement et invocations ; playtest humain difficulté/rythme.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-021 — Cohérence visuelle N1–4 et validation 0.3.0

**Lot J · Main agent : Claude Opus 5.5 (visuel), Codex (passe technique) · Statut : ACTIVE · Dépendances : RUN-020 DONE.**

- **Indices et tutoriels Secret Wall (9 octobre) :** révélation précédente validée explicitement après playtest. Nouveau complément demandé : Claude livre trois styles réutilisables (glow discret, fissures, teinte), N4 choisit les fissures. Première approche à64px avec ligne de vue : `A Strange Wall` ; après la fin du fondu : `Hidden Secrets`. Fenêtres anglaises existantes, acquittements durables par partie, reprise des erreurs de sauvegarde, New Game réinitialise. [Contrat et ownership](docs/RUN-021_SECRET_WALL_HINTS_CONTRACT.md). Nouvelle présentation et introduction à valider humainement ; RUN-021 reste ACTIVE.

- **Secret Wall N4 (8 octobre) :** proposition validée puis implémentée : cache masquée par maçonnerie raccordée au terrain, fondu0,6s avec effritement/SFX unique ; passage et récompenses accessibles en fin de fondu. Flag durable avant révélation, échec sans ouverture et reprise acquise sans replay. Placements humains et terrain N4 conservés (trois propriétés ajoutées). Claude Opus5.5 a livré le masque et revu quatre captures640×360/zoom1,2×. Recette isolée793contrôles réussis (143 comportement/froid/rendu,650 progression/coffres). Suite globale arrêtée sur trois échecs Swarm4 N4 reproduits identiquement sur HEAD, hors de ce complément ; elle n'est pas déclarée réussie. [Contrat](docs/RUN-021_SECRET_WALL_CONTRACT.md), preuves/limites au journal. Révélation déclarée fonctionnelle et validée après playtest le9octobre ; cette acceptation ne vaut pas validation du nouveau complément d’indices/tutoriels. RUN-021 reste ACTIVE.

- **Passe visuelle N4 Claude (9 octobre) :** demande humaine, même type de passe que N2/N3, strictement esthétique. Forbidden Graveyard reçoit cinq bandes de fond (nécropole et basilique, rangées de cryptes et chapelle-ossuaire, pente du cimetière, voiles spectraux, stèles proches) avec bougies, portes de cryptes et feux follets, et une lune gris-violet plus petite. Le terrain passe en maçonnerie funéraire, fondation et terre de tombes ; les colonnes étroites deviennent des piliers de crypte. S'ajoutent 32 accessoires dont muraux, suspendus et souterrains, une brume des tombes et des feux follets. Le mur de fond souterrain est étendu à N4 : les cryptes et le couloir de sortie bas ne montrent plus le ciel. Le masque du mur secret suit le nouveau skin, sans couture. N1–N3, scènes et gameplay inchangés (N2/N3 au niveau du bruit `HEAD`/`HEAD`). Recette sur `4a51873` + passe : rendus 9/9 et 57/57, mur secret 39/39 + froid 19/19, intro 38/38, exploration 27/27 et 42/42, indices 21/21 ; échecs préexistants identiques sans la passe (`red_slime`, ferry de la caméra, attente du fondu dans `run019_visual`). Rechargement à chaud 7/7, 90 s sans dérive mémoire, perf au plafond vsync. [Manifeste](docs/RUN-021_N4_VISUAL_MANIFEST.md). Validation artistique humaine requise ; RUN-021 reste ACTIVE.

- **Passe visuelle N3 Claude (8 octobre) :** passe N2 et correctif mémoire validés par l'humain. Black Forest reçoit cinq bandes de fond (crêtes et meules de charbonniers, mur de sapins, troncs, faisceaux de lune, troncs géants) avec lucioles et braises. Le terrain passe en sol forestier, couche de racines et terre profonde ; les colonnes étroites deviennent des troncs d'écorce. S'ajoutent 28 accessoires dont muraux, suspendus et souterrains, un brouillard froid et des lucioles. Le mur de fond souterrain est étendu à N3, donc la grotte basse ne montre plus le ciel. N1, N2 et N4 sont inchangés (N2/N4 comparés au pixel à `HEAD`), comme les scènes et le gameplay. Rendus 9/9, 57/57 et caméra 20/20 ; campagne 178 avec le seul échec préexistant `red_slime` sur `HEAD` + la passe. Un second échec dans le checkout partagé vient d'une édition humaine de N4 survenue pendant la passe, préservée et hors périmètre. Rechargement à chaud 6/6, 90 s sans dérive mémoire, perf au plafond vsync. [Manifeste](docs/RUN-021_N3_VISUAL_MANIFEST.md). Validation artistique humaine requise ; RUN-021 reste ACTIVE.

- **Passe visuelle N2 Claude (8 octobre) :** demande humaine, strictement esthétique. Blight Town reçoit cinq bandes de fond (cathédrale de peste, rempart, rues) avec fenêtres éclairées, un terrain qui s'enfonce dans une terre pourrie, 23 accessoires dont muraux et suspendus, des lumières animées et un miasme. Un mur de fond souterrain calculé depuis le Terrain supprime la ligne d'horizon visible dans la cave basse. N1, N3 et N4 sont inchangés, comme les scènes et le gameplay. Rendus 9/9, 57/57 et caméra 20/20 ; campagne 178 avec un seul échec, `red_slime`, identique sur `HEAD` ; perf au plafond vsync. [Manifeste](docs/RUN-021_N2_VISUAL_MANIFEST.md). Validation artistique humaine requise ; RUN-021 reste ACTIVE.

- **Seconde passe audio Claude (8 octobre) :** passe précédente validée. Le saut mural (aucun son de glissade n'existe) passe de −12 à −23 dB, sous les sauts. Nouvelle ambiance N3 originale, plus grave et plus discrète (−34,9 LUFS contre −29,1), dans l'esprit de N2. `run021_audio_pass` 33/33, mêmes quatre échecs préexistants. Écoute humaine requise ; RUN-021 reste ACTIVE.

- **Passe audio Claude (8 octobre) :** piques rétractables silencieuses ; musique N1 « Shadow of the Blood Thirsty Woodlands » (boucle de 8 phrases) ; saut et double saut Minifantasy `12_human_jump` retouchés, intégrés sur décision humaine malgré une licence non vérifiée (dépôt public) ; rayon d'écoute commun des SFX du monde de 360 px (les impacts étaient entendus jusqu'à 2000 px). `run021_audio_pass` 28/28, 2244 PASS + 15 suites ; quatre échecs préexistants identiques sur `HEAD`. Écoute humaine requise ; RUN-021 reste ACTIVE.

- **HUD/coffres Claude (8 octobre) :** cœurs sans nombre ; récompense à deux slots toujours visibles, icône 48 px, halo de sélection, seul bouton Accept (E) ; coffre centré à l'ouverture. Recette 61RESULT/2781PASS en worktree isolé ; échecs restants identiques sur `HEAD` (campagne red_slime, routes N2, Bloated, caisse N4). Validation humaine requise, RUN-021 reste ACTIVE.

- **Zoom joueur validé le 8 octobre :** changement manuel à **1,2×** sur les deux axes confirmé dans `scenes/player.tscn`, playtests réalisés selon déclaration humaine. Défaut conservé jusqu'à nouvel ordre ; légère hausse de difficulté volontaire. Les prochaines passes de développement et de recette utilisent ce cadrage comme baseline, sans compensation automatique ni retour à 1×. Décision consignée dans docs/01, docs/06 et brief ; elle ne clôture pas RUN-021 ni ne valide les autres compléments en attente.

- **Complément commandes autorisé le 7 octobre :** recommandation acceptée puis implémentation locale des profils clavier + souris AZERTY/QWERTY, classique et personnalisé ; menu Controls depuis titre/pause, remappage et sauvegarde indépendante, aides dynamiques et reprise après relâchement. 767 PASS / 20 RESULT ciblés, dont 80 headless + 80 natifs sur les contrôles et deux sessions à froid ; import propre. Pas de visée au curseur ni d’implémentation des attaques spéciale/impact réservées. Ressenti à valider humainement ; ce complément ne clôture pas RUN-021 et ne remplace pas la recette globale. Détails au journal.

- **Slots d'armes Claude (7 octobre) :** nom seul et badge de niveau 12×12 juste après le nom. Rendu79/79, recette 58RESULT/2842PASS en worktree isolé, quatre échecs préexistants inchangés ; validation humaine de lisibilité requise, RUN-021 reste ACTIVE.

- **Seconde passe UI/HUD Claude (7 octobre) :** nom N1 « The Eidolon Vale », bouclier 24 px en haut à droite, sting −3 dB, avatar trois-quarts au cadre rond ; pop du cœur au bonus HP et gains enchaînés au-dessus du chevalier sans chevauchement. Rendu73/73, recette 57RESULT/2822PASS en worktree isolé, quatre échecs préexistants inchangés. Validation humaine de la lecture/rythme requise ; RUN-021 reste ACTIVE.

- **Passe UI/HUD Claude (7 octobre) :** HUD sans fonds hormis l'avatar, sans libellés, shards à côté des coins ; titrage de niveau 5 s au premier chargement avec sting CC BY ; mort centrée ; effet Magic Shield + secondes en haut à gauche. Rendu61/61 et visuels HUD 199/199 ; recette globale sans régression, quatre échecs gameplay préexistants reproduits à l'identique sur `HEAD` (routes N2 basse/haute, vitesse Bloated). Détails au journal ; validation humaine (lisibilité, sting) requise, RUN-021 reste ACTIVE.

- **Ferry vertical corrigé (7 octobre) :** Ferry2N2 héritait Travel horizontal malgré remplacement manuel du script. Instance verticale explicite `(0,144)` et script commun, positions humaines préservées. Probe avant4/2échecs, après27/27 et plateformes14/14 ;41contrôles ciblés, import vérifié. Deux variantes configurables dans l'inspecteur viaTravelX/Y etPeriod, explication dans specs/learning. Pas de nouveau playtest/rendu/global de campagne ; run ouverte et aucune promotion/clôture implicite.

- **Caméra verticale corrigée (7 octobre) :** Ferry validé explicitement (« Ferry corrigé ok »). Blocage N2 reproduit : limite haute−224, centre bloqué−44 alors que le terrain atteint−336. Limites verticales calculées au chargement depuis Terrain et trajectoires complètes des Ferries, marge256px ; réglages manuels disponibles, scènes humaines préservées. Recette ciblée Godot4.7.2 : caméra20/20 headless et22/22 native (deux captures inspectées), campagne178/178 et cinématiquesN1 35/35, soit255contrôles/4résultats. Aucun nouveau résultat des pilotes de routes ni de recette globale ; validation humaine de ce suivi restant, RUN-021 ACTIVE.

- **Validation et complément mobs du 7 octobre :** « Passe validée » reçu pour les piques/munitions ; validation humaine consignée sans inventer un nouveau PASS des deux anciens pilotes. Correctifs demandés puis livrés : Bloated poursuit à48px/s (60 auparavant), corps/contact/dégâts conservés ; cinq profils terrestres stabilisés à l'alignement2px et pendant leur saut, détour vérifié vers petit toit conservé. Recette ciblée finale557/557 sur6suites et rendu13/13 surArcherN3 réel. Preuves avant/après et limites au journal ; [checklist](docs/RUN-021_PLAYTEST.md). Le complément nécessite son propre playtest ; RUN-021 reste ACTIVE avec les anciens pilotes de campagne non validés. Contrat Claude03 déjà livré, aucun nouveau besoin artistique pour ce correctif.

- **Livraison locale du 7 octobre — piques/munitions : ACTIVE.** Code et assets Claude livrés ; réserve courante transmise au prochain niveau, snapshot d'entrée restauré aux resets. Recette partielle2736contrôles/56résultats réussis,14sessions froides et rendu73/73 ; deux pilotes complets encore en échec sur le dernier code (mort N2 basse, chute/blocage N2 haute), exclus de ces chiffres. Pas de VERIFY avec ces vérifications restantes. Index des logs/hashes, échecs et limites au journal ; playtest d'équilibrage/visuels distinct, aucune validation0.3.0/clôture implicite.

- **Contrat approuvé (7 octobre 2026) :** « Je valide la proposition » avec exception : stock courant conservé au passage au niveau suivant (N2 finit2 → N3 commence2). Snapshot d’entrée de niveau restauré à mort/restart/reprise ; dépenses/loots intra-tentative non durables. Retour ACTIVE pour code/tests et contribution Claude sur ownership séparés ; docs du contrat mises à jour, fichiers humains préservés. Pas de push/PR/merge ni validation humaine du futur résultat présumée.

- **Validation et proposition du 7 octobre 2026 :** l’humain confirme les changements de la passe précédente « testés et validés », puis demande une nouvelle passe piques rétractables/munitions/caisses/tonneaux avec validation préalable. [Proposition produit](docs/RUN-021_AMMO_SPIKES_PROPOSAL.md) et [contrat Claude](docs/RUN-021_CLAUDE_HANDOFF_03.md) préparés après inspection du code, sans implémentation. Réserves humaines10/15 Longbow et12/20 Knives ; reset fixe, taux de drops et budgets/placements restent des propositions à approuver. RUN-021 reste ouverte ; aucune clôture/promotion0.3.0 ni exécution de cette nouvelle passe avant validation du contrat. Les checkpoints précédents décrivent les attentes humaines désormais satisfaites pour cette passe acceptée.

- **Lancement autorisé (6 octobre 2026) :** READY puis ACTIVE sur `feature/run-020-021-campaign`, après clôture020. Claude pilote la première passe visuelle ; Codex prépare le handoff et réserve les correctifs de gameplay/tests. [Contrat principal](docs/RUN-021_CLAUDE_HANDOFF.md), [complément Archer/audio](docs/RUN-021_CLAUDE_HANDOFF_02.md) et [remarques humaines](docs/RUN-021_REVIEW_NOTES.md). Six fichiers humains gelés, dont TileSet, ressources du chevalier et Blight Town ; aucune régénération ni substitution de terrain. Préanalyse initiale Claude Opus5.5 en lecture seule réellement exécutée ; points de sources/ownership N1 résolus dans le contrat. Aucune contribution de production ni nouvelle validation artistique présumée.
- **Passe visuelle Claude livrée (6 octobre 2026) :** terrain N1–4 sans colonnes d’ombrage, terre N3 éclaircie, bande proche N2–4, décor/lueurs N2–4, musique N4 raccordée et audit SFX proposé ; cause Archer reproduite (patrouille nulle, logique → Codex). Rendu 57/57 et N1 11/11 ; [manifeste](docs/RUN-021_ASSET_MANIFEST.md), [revue audio](docs/RUN-021_AUDIO_REVIEW.md). Fichiers remis à Codex ; validation artistique/écoute humaine et recette encore requises.
- **Relais Codex vérifié (6 octobre 2026) :** visuel et ajout musique N4 validés explicitement. Patrouille nulle traitée comme sentinelle (sans modifier les six perchoirs), défaut avant/après reproduit et vidéo qualitativement compatible. Archer/Sorcerer acquisition720×144 et déclenchement240px ; poursuite Bloated60/Chud48px/s ; Longbow0 2,2s/176px, Knives0 1,4s/104px. Recette complète composée2331PASS/48RESULT (36suites,11sessions froides,isolation), routes basses19/19 et hautes21/21 après adaptation des inputs du pilote, rendu68/68, observation six archers6/6. Terrain et dix fichiers protégés identiques à la remise. Logs/échecs intermédiaires et limites au journal. [Playtest des nouveaux réglages](docs/RUN-021_PLAYTEST.md), sélection SFX en attente ; RUN-021 VERIFY, Jev/clôture et0.3.0 après validation finale, pas de RUN-022 anticipée.
- **Reprise après playtest (6 octobre 2026) :** l’humain valide les modifications précédentes après playtest, puis demande des correctifs complémentaires sur la même branche. Retour ACTIVE : poursuite et franchissement physique pour les mobs, Bloated inclus ; seuls Green/Purple/Red exclus. Aggro et perte inchangées. Coffre common limité aux drops directs0–2 ; upgrade possible conservé. Terrain humain préservé. Ces nouveaux correctifs nécessitent leur propre recette et essai humain avant clôture ; la validation précédente ne les couvre pas.
- **Correctifs complémentaires vérifiés (6 octobre 2026) :** poursuite avec sauts physiques des cinq profils terrestres, Bloated inclus ; Green/Purple/Red conservés. Skulls contournent murs et plateformes par balayage de leur cercle ; acquisition/perte inchangées. Common direct0/1/2 =40/30/30 %, upgrade5 % jusqu’à3 conservé. Recette complète composée2375PASS/50RESULT (38suites,11sessions froides,isolation), routes19/19+21/21 et sauts rendus16/16. Tests adaptés aux ajouts humains N2 et à l’overlap du bouton/pièce N4, sans modifier les scènes. Terrain, nouveaux mobs et pièges humains N2 préservés hors commit. Preuves et limites au journal ; RUN-021 VERIFY pour le playtest des nouveaux comportements, sans clôture ni promotion0.3.0 anticipées.
- **Nouvelle reprise du 6 octobre 2026 :** retour humain de la dernière passe : élites bloquées sur un bloc après leur saut, ferry N2 ajouté invisible en jeu, rebond mural à rendre fluide. Retour ACTIVE pour reproduction, corrections et vérifications ; niveaux humains préservés. La demande ne clôture pas RUN-021 et ne valide pas encore le nouveau résultat.
- **Dernière reprise vérifiée (6 octobre 2026) :** Bloated/Chud montent et redescendent les blocs32/64/72px de façon répétée ; marges physiques et occlusion pendant saut corrigées, cible hors portée perdue après2s. Fonds absolus−100 pour conserver visibles ferry et futurs objets ; ligne rouge = axeY=0 de l’éditeur. Coyote mural0,10s, priorité mur et récontact après séparation ; charge aérienne inchangée. Recette composée2476PASS/51RESULT (39suites dont variante haute,11sessions froides,isolation), rendu102/102,37scènes baseline identiques. Commande globale initiale interrompue puis preuves recomposées, sans prétendre à une commande globale réussie. N2 : première fourche basse/haute puis passerelle haute et nouveau tunnel dans les deux pilotes ; sortie directe basse de la seconde fourche non validée. N3/N4 : variantes basses/hautes couvertes. Journal/index/guide mis à jour ; nouvel essai humain du ressenti et des trois correctifs requis, pas de DONE/promotion0.3.0 anticipés.
- **Reprise du 7 octobre 2026 :** « Retours validés après playtest » ; validation de la passe précédente consignée à ce niveau de précision. Bloated N2 reste bloqué lorsque le joueur arrive dans la zone basse par la gauche ; vidéo fournie. Retour ACTIVE pour reproduction selon phase de patrouille et renforcement des tests de Bloated/Chud. Les modifications humaines non committées de `blight_town.tscn` et `eidolon_vale.tscn` forment la nouvelle baseline protégée ; aucun terrain régénéré.
- **Reprise vérifiée du 7 octobre 2026 :** sol praticable sous plateforme prioritaire, recul local vérifié jusqu’à un bord libre lorsque les piques/plafond ferment le passage ou que la cible est sur le toit, puis saut avec arc ascendant du corps vérifié et redescente. Bloated/Chud :188/188 scénarios renforcés, dont huit essais N2 à phases de patrouille différentes (Chud en substitution explicite). Recette ciblée finale651PASS/21RESULT :9suites dont variante haute des parcours,11sessions froides et isolation ; rendu46/46,38scènes baseline identiques. Commande globale initiale et premières reprises interrompues consignées sans les prétendre réussies ; les preuves finales sur le dernier code sont ciblées. Validation antérieure acquise, nouvel essai humain de ce comportement restant ; RUN-021 VERIFY, pas de clôture/promotion0.3.0 anticipées.
- **Passes ajoutées par l’humain :** (A) cohérence visuelle Claude ; (A2) reproduction de l’animation Archer, audit/remplacement/suppression argumentés des SFX et piste N4 `delosound-dark-synthwave-retro-80s-453292` ; (B) Codex augmente aggro/portée Archer/Sorcerer et vitesse d’aggro Bloated/Chud, réduit légèrement cadence/distance du tir joueur, sur valeurs justifiées ; (C) corrections finales, recette complète, rendu et playtest humain. Remise exclusive avant toute édition d’un fichier partagé ; pas de tuning implicitement confié à la passe artistique. Les niveaux actuels restent loin de l’ampleur finale demandée ; les edits de terrain humains sont protégés selon la règle permanente ci-dessus.

- **Résultat / scope :** Habiller les trois niveaux et harmoniser N1–4, sprites/animations des archétypes, VFX, objets et interfaces ; sources et crédits traçables.
- **Décisions avant implémentation dépendante :** Choix d’assets et ownership des scènes avant intégration ; aucune modification implicite des profils gameplay.
- **Acceptation, tests et bugtest :** Rendu des interactions du contenu livré, silhouettes et télégraphies, clavier, animations/collisions, parcours N1 et N4 puis régression des scènes modifiées ; critères 0.3.0 ci-dessus satisfaits et validation artistique humaine.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

## Version 0.4.0 — Capacités et campagne complète N5–10

**Statut : BACKLOG, non lancée.** **Prérequis :** 0.3.0 validée ; D01, D02, D04, D06–D09 avant les comportements concernés.

**Repères documentaires :** 01, 02, 03, 04, 05, 06, 07, 08, 09, 13 dans `docs/`.

**Critères de validation du jalon (conservés lors du regroupement) :**

- [ ] Grimper, attaque d’atterrissage, flammes, Rage et Fire Gauntlet testés séparément puis combinés.
- [ ] Quatre légendaires, golden chest, Enchant Juice et offrande N5 fonctionnels avec sauvegarde cohérente.
- [ ] N5/N6 jouables à 40/50 coins, profils N5–9, palier 5 HP, secrets et récompenses uniques exactement répartis.

- [ ] Chaos Champion et Necromancer conformes, charge et invocations télégraphiées, population bornée.
- [ ] N7/8/9 jouables à 64/82/100 coins ; HP 7 à N8, deuxième offrande 50 % non additive.
- [ ] Total N4–9 : 10 secrets, 3 Golden, 6 Rare secrets, 8 Major secrètes, 1 Enchant ; HP bonus répartis 1/1/2/3 sur N4/5/7/9.

- [ ] N10 dédié au boss, spawn sûr, confrontation puis combat sans aggro/reset exploitable, caméra adaptée.
- [ ] 50 HP, mêlée, quatre zones, boules de feu, charge, invocations et enrage ≤20 HP validés séparément puis ensemble.
- [ ] Victoire puis dialogue Karla et fin de démo ; aucune onzième zone ajoutée pour le Heart of Corruption.
- [ ] Boss vaincu en playtest avec 7 HP de base et armes 2/3 sans Legendary ; 14 HP avantageux sans trivialiser le combat.

### RUN-022 — Verticalité, capacités et consommables spéciaux

**Lot K · Main agent : Codex GPT-6.1 Sol Medium · Statut : BACKLOG · Dépendances : RUN-021 ; 0.3.0 validée.**

- **Résultat / scope :** Grimpe, attaque d’atterrissage, flammes, Rage, Fire Gauntlet et cooldowns visibles ; tests isolés puis combinés sur terrain vertical.
- **Décisions avant implémentation dépendante :** D02/D07 : contraintes de grimpe, seuil/rayon slam, cumul/rafraîchissement buffs et cooldowns.
- **Acceptation, tests et bugtest :** Grimpe et murs/bac, slam seuil/rayon/impact, souffle et flammes cycliques, buffs/cooldowns lors du changement d’arme, pause/mort/reset ; non-régression N1–4.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-023 — Légendaires et progression permanente

**Lot L · Main agent : Codex GPT-6.1 Sol Medium · Statut : BACKLOG · Dépendances : RUN-022.**

- **Résultat / scope :** Dragon Slayer, Obsidian Relic, Thunderstruck, Demonic Crossbow ; Golden Chests, Enchant Juice, uniques, paliers HP N5/N8 et offrandes en fin de N5/N7.
- **Décisions avant implémentation dépendante :** D04/D08 : bases des offrandes 20/50 %, seconde sans première, charge/compteur/portée ; contrat dégâts Boss résolu avant RUN-026.
- **Acceptation, tests et bugtest :** Chaque Legendary testée séparément puis en combinaison ; charge/annulation, kills/compteur, portée/relief ; unicité après mort et fermeture, coffres et Enchant sans doublon, banque après sacrifice, seconde rétention 50 % non additive, paliers 5/7 HP.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-024 — Dernières élites et niveaux N5–9

**Lot M · Main agent : Codex GPT-6.1 Sol Medium · Statut : BACKLOG · Dépendances : RUN-022–023.**

- **Résultat / scope :** Profils N5–9, Chaos Champion et Necromancer ; charge, trois zones et invocations ; construire Haunted Caves, Desolands, Rotbringer Camps, Fallen Temple, Darkveil Dungeon et raccorder N1–9.
- **Décisions avant implémentation dépendante :** D04/D06 : profils Skeleton N5/N9, cycle et disparition des invocations, farm et population.
- **Acceptation, tests et bugtest :** N5–9 à 40/50/64/82/100 coins ; charge annoncée, populations/récompenses bornées, pause/mort/source détruite ; total N4–9 : 10 secrets, 3 Golden, 6 Rare secrets, 8 Major secrètes, 1 Enchant ; HP bonus 1/1/2/3 sur N4/5/7/9 ; parcours N1–9 et saves aux paliers, avec/sans sacrifices ; playtest humain.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-025 — Habillage et lisibilité N5–9

**Lot N · Main agent : Claude Opus 5.5 · Statut : BACKLOG · Dépendances : RUN-024.**

- **Résultat / scope :** Ambiances, décors, animations d’élites, légendaires, capacités et secrets ; harmoniser les neuf niveaux et leur signalétique sans altérer leur distribution.
- **Décisions avant implémentation dépendante :** D10 : palettes, skins, gabarits et contrats techniques à figer avant intégration.
- **Acceptation, tests et bugtest :** Télégraphies charge/invocations, verticalité, secrets, effets de buffs/capacités lisibles ; collisions et parcours des scènes modifiées, contrôles N1 et N9, licences et validation artistique humaine.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-026 — Lupikal, Karla et recette de campagne 0.4.0

**Lot O · Main agent : Codex GPT-6.1 Sol Medium · Statut : BACKLOG · Dépendances : RUN-025.**

- **Résultat / scope :** N10 Darkveil Dungeon Throne, arène et spawn sûr ; Boss 50 HP avec mêlée/quatre zones/boules de feu/charge/invocations/enrage ≤20 HP ; introduction, HUD, télégraphies, art/audio P0, libération de Karla et conclusion.
- **Décisions avant implémentation dépendante :** D08/D09 : effets Legendary face au Boss, attribution 3/5 DMG, accélération enrage, séquence dialogue/combat et état final.
- **Acceptation, tests et bugtest :** Chaque attaque puis ordonnancement complet ; mort simultanée, aggro/reset non exploitable, Continue après victoire ; Boss vaincu en playtest humain à 7 HP avec armes 2/3 sans Legendary ; 14 HP avantageux sans trivialisation ; parcours complet N1–10 et persistance ; aucune onzième zone.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

## Version 0.5.0 — Démo beta finale distribuable

**Statut : BACKLOG, non lancée.** **Prérequis :** 0.4.0 validée ; plateformes et budget de performance D10 décidés avant les exports.

**Repères documentaires :** 00 à 13 ; catalogues 11–12 locaux si disponibles dans `docs/`.

**Critères de validation du jalon (conservés lors du regroupement) :**

- [ ] Palette, échelle, animation et contraste cohérents dans les dix biomes ; variantes avancées retenues reconnaissables sans changer leur gameplay.
- [ ] Toutes les lignes requises de docs/08 et docs/13 ont un asset intégré/testé ou une décision de scope validée ; aucun P0 manquant.
- [ ] HUD, menus, artwork, logo, dialogues et audio final testés au clavier à 640×360 ; tous les textes visibles sont anglais.
- [ ] Sources originales intactes, dérivés identifiables et crédits/licences complets pour les assets distribués.

- [ ] Dix niveaux, boss et conclusion terminables ; sessions humaines couvrent l’objectif de 1–2 h et les retries, sans prétendre garantir une durée non mesurée.
- [ ] Aucun bug bloquant/critique ouvert ; toutes les règles persistantes, coûts, uniques et interactions testés après corrections.
- [ ] Build autonome vérifié sur chaque plateforme de livraison retenue ; import propre, installation vierge, sauvegarde/reprise et fermeture corrects.
- [ ] Version 0.5.0 beta affichée et documentée, licences/crédits et limites connues livrés ; aucune publication automatique.

### RUN-027 — Présentation finale et cohérence de la démo

**Lot P · Main agent : Claude Opus 5.5 · Statut : BACKLOG · Dépendances : RUN-026 ; 0.4.0 validée.**

- **Résultat / scope :** Harmoniser dix biomes et variantes avancées retenues, HUD/menus/logo/artwork/dialogues anglais ; compléter animations/VFX et audio requis, résoudre les retours RUN-010 restants (dont sons de saut et double saut encore trop « sci-fi » après RUN-014), mixer et intégrer volumes/préférences persistantes avec contribution technique cadrée. Améliorer le détail du logo de menu selon le retour humain du 3 octobre 2026, en conservant sa référence. Reprendre les approximations tir/impact/ouverture de RUN-016, juger le mix des trois sons d’acquisition à l’écoute et ajouter une variante de mort avec arc (l’animation actuelle lâche l’épée).
- **Décisions avant implémentation dépendante :** D10 : variantes retenues et licences ; validation artistique et sonore humaine.
- **Acceptation, tests et bugtest :** Toutes exigences docs/08 et docs/13 intégrées/testées ou décision de scope validée, aucun P0 absent ; rendu/clavier à 640×360, transitions d’animation/collisions, écoute humaine et mix, réglages après reprise, sources/dérivés et licences/crédits complets ; effets caméra facultatifs seulement si lisibles.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

### RUN-028 — Équilibrage, robustesse et livraison 0.5.0 beta

**Lot Q · Main agent : Codex GPT-6.1 Sol Medium · Statut : BACKLOG · Dépendances : RUN-027.**

- **Résultat / scope :** Playtests complets, équilibrage économie/difficulté/durée, corrections ciblées, robustesse sauvegardes/transitions, profilage, exports reproductibles et recette hors éditeur.
- **Décisions avant implémentation dépendante :** D10 : plateformes, matériel et budget performance ; validation humaine finale avant livraison autorisée.
- **Acceptation, tests et bugtest :** Sessions humaines mesurant objectif 1–2 h et retries ; aucun bug bloquant/critique ; règles/coûts/uniques testés après corrections ; build autonome sur chaque plateforme retenue, installation vierge, import/save/reprise/fermeture ; version beta, crédits et limites livrés ; publication uniquement sur autorisation.
- **Clôture :** corrections et régressions du périmètre, revue Jev selon le cycle existant, preuves au journal et learning fondé sur le résultat réel ; validation humaine des choix artistiques ou playtests requis.

## Point d’arrêt

**3 octobre 2026 : RUN-015 DONE localement**, contribution Claude validée humainement, thème de menu choisi intégré et testé, revue Jev et inspection des preuves satisfaisantes. Le logo plus détaillé reste une retouche Claude de RUN-027, sans remettre en cause la passe validée.

**RUN-016 DONE**, passe Claude validée, revue globale sans défaut bloquant, suite complète (499 + 1 isolation), rendu et revue Jev suivie de l’inspection des preuves terminés. PR vers develop autorisée par la demande humaine du 3 octobre 2026. PR #17 présente fusionnée dans develop (`420f88b`). RUN-017 DONE : deux passes Claude/correctifs et playtest N1 validés humainement ; idle testé, revue globale sans défaut bloquant, 640 contrôles et rendu 35/35 + 11/11, Jev READY_FOR_DONE suivi de l’inspection. [PR #18](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/18) ouverte vers develop ; jalon 0.2.0 validé localement. Aucune autre run ni fusion autorisée. Aucune fusion autorisée.
