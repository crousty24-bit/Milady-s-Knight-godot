# Milady's Knight — Brief projet

## Résumé

**Milady's Knight** est un action-platformer 2D rétro pixel-art Dark Fantasy avec des mécaniques inspirées du rogue-lite.

Le joueur incarne **The Ashen Knight**, ramené à la vie pour traverser un royaume corrompu, atteindre Darkveil Dungeon, vaincre Lupikal The Doombringer et libérer Princess Karla.

Le projet vise une **démo jouable courte et complète**, pas un jeu commercial de grande ampleur.

## Scope

- environ 1 à 2 heures de jeu visées ;
- 10 niveaux conçus manuellement ;
- difficulté progressive ;
- combat mêlée et distance ;
- plateforme, exploration, pièges et passages secrets ;
- collecte de Gold Coins ;
- Shards obtenus par le combat ;
- coffres et amélioration d'équipement ;
- progression die-and-retry ;
- Boss final.

La version finale du projet restera une version de démonstration alpha/beta et ne correspond pas nécessairement à `1.0.0`.

## Ce qu'est le projet

- un action-platformer 2D ;
- un jeu à niveaux fixes ;
- une expérience courte orientée maîtrise du niveau ;
- une démo alpha/beta développée par itérations ;
- un projet où gameplay, lisibilité et stabilité priment sur le polish.

## Ce que le projet n'est pas

- un roguelike procédural ;
- un open world ;
- un RPG long ;
- un Metroidvania basé sur un grand système d'ability-gating ;
- un jeu multijoueur ;
- un live-service ;
- un projet visant obligatoirement une version `1.0.0`.

## Direction technique et visuelle

Références actuelles :

- moteur : Godot ;
- pixel-art Dark Fantasy ;
- grille de référence : 16×16 px ;
- résolution interne : 640×360 ;
- ratio : 16:9 ;
- filtrage pixel-art : Nearest / Nearest Neighbor ;
- scaling entier privilégié.

Les détails complets restent dans `docs/`.

## Workflow documentaire

- `README.md` : présentation générale du dépôt ;
- `AGENTS.md` : règles durables pour les agents ;
- `brief.md` : contexte synthétique et état vérifié ;
- `runs-workflow.md` : roadmap agentique par versions et runs ;
- `runs-journal.md` : historique des runs et preuves de validation ;
- `learning.md` : journal pédagogique expliquant à l'humain comment les runs ont été implémentées dans Godot et le code ;
- `docs/` : documentation détaillée du projet.

## État du projet

Audit du **21 septembre 2026**, complété par les vérifications jusqu'au **30 septembre 2026** et l’audit final de clôture du **2 octobre 2026**. Les preuves d’exécution sont dans [runs-journal.md](runs-journal.md) ; l’audit initial et la planification restent dans [runs-workflow.md](runs-workflow.md).

### Jalon atteint et prochaine cible

**Version actuelle : 0.2.0, N1 validé ; cible 0.3.0 autorisée le 5 octobre 2026.** La promotion0.2.0 est présente dans `main` (`9e9847b`) ; `develop` inclut maintenant RUN-018 via PR #21 (`288b518`). RUN-018 lancée en préparation sur `feature/run-018-standard-equipment`, DONE après intégration Claude, recette de retour, validation humaine et revue de clôture : [contrat validé](docs/RUN-018_CONTRACT_REVIEW.md) et [manifeste Claude](docs/RUN-018_ASSET_MANIFEST.md). Contrat validé humainement ; huit armes standard0–5, common/rare, upgrades, potion majeure et drops de soin implémentés et testés en fixture. Retour Claude vérifié :1743 PASS, rendu68/68 ; art/écoute et essai humain validés le 5 octobre 2026 ; revue Jev et inspection de clôture satisfaisantes. Les paragraphes datés ci-dessous conservent les étapes de validation antérieures.

**Historique 0.1.0 : clôturée et validée localement le 2 octobre 2026.** L’humain valide toutes les runs réalisées le 2 octobre 2026 ; **RUN-001–014 et RUN-029 sont DONE**. RUN-010 est fusionnée via la PR #15 ; RUN-011, la réorganisation et les quatre passes Claude sont fusionnées dans `develop` via la PR #16. Le dépôt reste un slice, pas encore N1 conforme.

La roadmap compte **29 identifiants** (limite 30) : **20 DONE (RUN-019 comprise), RUN-020 VERIFY et 8 BACKLOG** vers **0.3.0 → 0.4.0 → 0.5.0 beta** après le jalon 0.2.0. Chaque lot conserve son orchestrateur : Codex GPT-6.1 Sol Medium ou Claude Opus 5.5 ; délégation et Jev inchangés.

**Début 0.2.0 autorisé le 3 octobre 2026.** Fusion de la PR #16 dans `develop` vérifiée (`f997bcb`) ; branche `feature/v0.2.0-reprise-equipment`. RUN-015 DONE : sauvegarde v2, migration explicite, économie coins/shards et menus clavier avec habillage Claude et musique choisie bouclée. RUN-016 DONE après passe Claude validée humainement et revue Jev suivie de l’inspection des preuves : Longbow0, slots, coffre tuto gratuit et potion mineure, art/sons intégrés. Revue globale sans défaut bloquant ; 20 suites / 499 contrôles + isolation, contrôles avec rendu réussis. PR #17 fusionnée dans develop (`420f88b`). RUN-017 sur `feature/run-017-eidolon-vale` : deux passes Claude et correctifs validés humainement, playtest N1 jusqu’à sortie sur les deux chemins confirmé. Dialogue phrase par phrase silencieux (+2 s), résurrection New Game uniquement, Spirit sur la tombe `(140,144)`, apparition/disparition et cue dédiés livrés. Pose idle animée pendant apparition/dialogue corrigée et revue ; gameplay reste bloqué. 640 contrôles (631 jeu + 8 froids + isolation), cinématiques rendues 35/35 et N1 11/11. Revue Jev READY_FOR_DONE suivie de l’inspection des preuves ; RUN-017 DONE et jalon 0.2.0 validé localement. [PR #18](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/18) fusionnée dans develop le 3 octobre 2026 (`3ae7b92`). Limites : sons approximatifs, mix acquisition, mort arc et détail du logo en RUN-027. Les catalogues 11–12 restent locaux ; provenance des médias hérités à établir avant distribution.

### État vérifié

- **Moteur :** Godot **4.7.2 stable** retenu, version centralisée et vérifiée par les lanceurs. `project.godot` conserve **4.7**, renderer GL Compatibility. Windows 4.7.2 testé depuis WSL/UNC et disque local ; le runtime Linux 4.5.1 historique est conservé mais refusé par les lanceurs. Linux 4.7.2 non testé ici.
- **Rendu :** viewport **640×360**, fenêtre initiale 1280×720, stretch viewport/integer, nearest et pixel snapping. Terrain sur grille 16×16. RUN-004 adapte le HUD et le cadrage du slice à cette résolution.
- **Structure :** scènes et scripts dans `scenes/` et `scripts/`, démarrage `scenes/game.tscn` puis `scenes/eidolon_vale.tscn` ; `vertical_slice.tscn` conserve le terrain et les fixtures de régression. Un autoload `Progression`. Aucun addon ni preset d’export trouvé lors de l'audit initial. Le TileSet N1 reste embarqué ; les nouvelles scènes N2–4 utilisent désormais `assets/kingdom_tileset.tres`.
- **N1 préservé :** un terrain fixe à deux branches avec retours, **18 coins**, **8 Slimes** (5 Green, 3 Purple), deux ronces conservées, des piques fixes solides au sol et sur la limite droite (0,5 DMG), une limite de vide réglable par niveau (`void_y`, 304 px dans le slice), un bac mobile et une porte demandant 12 coins. `tests/fixtures/next_level.tscn` est une fixture héritée du slice, pas un deuxième niveau produit.
- **Joueur :** marche accélérée, saut variable, double saut, coyote/buffer, wall slide/wall jump, épée au sol/en l’air avec déduplication et occlusion ; santé fractionnaire, profils de réactions aux dégâts, mort et reprise automatique après trois secondes puis fondu. Les flèches remplacent Q/D/Z/S ; F répète les frappes tant qu'il est maintenu. Sword 0 inflige 0,5 DMG, avec 1 s entre départs, un geste de 0,28 s et une lame de 24 px depuis la main (1 RANGE = 1,5 bloc) ; une interruption conserve le cooldown. Invulnérabilité de 1,20 s avec flash blanc de 0,10 s puis clignotement ; hit-stun de 0,18 s et recul de 0,16 s conservés après audit. Le saut mural est validé par essai humain pour le slice actuel.
- **Ennemis/pièges :** Green/Purple en patrouille sans aggro, 1/2 HP et 0,5/1 DMG de contact (profils N1–4). Recul de 0,12 s sans immunité de contact ni aux impacts. Ronces traversables de 1 dégât, recul horizontal loin du danger, et vide létal. Les autres ennemis, le Boss et les pièges avancés sont absents.
- **Progression RUN-015 :** tous les coins restent des coins ; la porte en dépense 12. Les kills créditent séparément les shards courants, perdus à la mort/restart/fermeture et ajoutés à la banque à la sortie. `user://progress.json` v2 stocke banque/niveau/équipements/flags permanents/dialogues ; acquisitions et débits de banque écrits immédiatement par API transactionnelle. Migration v1 seulement après accord au menu, original conservé. Les équipements/uniques/dialogues sont des contrats de stockage ; Longbow/coffre/potion sont intégrés en RUN-016 ; dialogue Spirit et tutoriels contextuels sont fonctionnels en RUN-017 ; les autres objets restent aux runs suivantes.
- **Présentation :** HUD anglais HP/COINS/SHARDS en grappe compacte (cadre et portrait du chevalier, cœurs, icône de pièce, panneaux 9-slice), overlays pause/mort (panneau rouge, voile allégé)/victoire ; plus de bandeau inférieur d’indications : un `DialogueBanner` masqué hors narration sert au dialogue Spirit, et la porte affiche une invite contextuelle (touche E, pièce, 12) au-dessus d’elle. Menu principal New Game/Continue/Controls/Quit et pause Resume/Restart/Quit to menu fonctionnels ; panneau contextuel exclusif. Les labels HUD santé/coins/shards sont anglais ; la présentation du panneau de menu et les sons UI Claude sont intégrés et validés. Deux slots verticaux, Longbow0, coffre tuto gratuit et potion mineure sont fonctionnels en RUN-016 ; leurs visuels/sons Claude sont intégrés et validés, avec limites tracées au journal. Dialogue Spirit anglais animé, Space pour la phrase suivante sans son, lecture prolongée de 2 s, simulation suspendue et flag écrit après la dernière phrase avant reprise ; quatre explications contextuelles. Art Spirit repos/dialogue/apparition/disparition, portrait/manifestation et cue validés humainement. Résurrection dédiée initiale New Game, apparition après 32 px et disparition après éloignement de 96 px (réglable), chevalier en idle animé sous pause du gameplay ; sol et cadrage stabilisés avant résurrection. L’essentiel des visuels est généré par `tools/art/` sur une palette commune (RUN-012–014 puis RUN-029) : Ashen Knight sur squelette (frames 64×64, garde de combat, course, sauts, atterrissage, glissade face au mur, dégâts, mort, enchaînement visuel de trois mouvements d’épée maintenu tant que F est tenu, sans changement des dégâts ni de la cadence), terrain en appareil irrégulier sur la `TileMapLayer` intacte, six couches de fond, accessoires enrichis et animés, Slimes, pièce, pièges, bac, porte et leurs VFX ; provenance dans `assets/VISUAL_CREDITS.md`. Audio routé par bus Master/Music/Ambient/SFX/UI : WAV Helton Yan (CC BY 4.0, crédit requis) normalisés à −8 dBFS, musique Pixabay *Dreamer* (nojisuma) à −13 LUFS ; l’ancienne musique dark fantasy lo-fi est réutilisée en boucle au menu. Limite restante : sons de saut et double saut encore trop « sci-fi », reportés à RUN-027. Provenance dans `assets/AUDIO_CREDITS.md` ; celle des médias hérités (police, atlas de collision, sons non référencés) reste à établir.
- **RUN-018 technique :** catalogue des huit armes standard et niveaux0–5, deux slots durables v2, dégâts/portées/cadences et cooldowns conservés lors du remplacement ; common/rare payants avec offre figée, upgrade cap3/refus et retry disque ; potion majeure1HP et soins instantanés au kill par profil. Objets nouveaux vérifiés en fixture explicite, sans placement N2–4 ; art livré et validé humainement. Contribution Claude `ff5caa0` intégrée : chevalier en couches, silhouettes à portée exacte, couteaux, UI/coffres/soins et sons. Recette de retour1743 PASS et rendu68/68 ; run DONE, validation humaine artistique/sonore et essai combat/coffres reçue, revue Jev et inspection satisfaisantes.
- **RUN-019 checkpoint technique :** contrat validé, Red/Bloated, Warrior/Archer/Sorcerer/Skulls/Chud et pièges/mécanismes/Shield/secrets/HP bonus implémentés en fixtures. Flags v2 et acquisitions durables, sources de dégâts distinctes pour tourelles et ennemis, budget swarm borné par emplacement et tentative. Présentation Claude livrée et passe validée en l’état ; recette1943 PASS et rendu47/47. Collisions élites20×22 conservées, crédits reportés, phase initiale des piques corrigée. Run DONE, validée humainement avec absence explicite d’essai direct des nouveaux mobs ; Jev/inspection terminée, [PR #22](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/22) fusionnée dans develop (`6a1b279`) ; jalon0.3.0 encore non validé. [Handoff technique](docs/RUN-019_CLAUDE_HANDOFF.md).
- **RUN-020 :** scènes fixes Blight Town/Black Forrest/Forbidden Graveyard, chaîne N1→N4, sorties18/25/32, budgets24/32/40 coins, progression des ennemis/pièges et exploration N4 intégrées. Fonds/décor/ambiances originaux délégués réellement à Claude Opus5.5 avec sous-agent Sonnet5.5, sources et crédits conservés. Parcours physique clavier N1–4 et transactions rendues vérifiés ; recette finale2207 PASS, transactions rendues178/178 et pilote visuel/audio33/33 ; VERIFY, playtest humain difficulté/rythme et jugement art/écoute attendus. Même branche `feature/run-020-021-campaign` pour RUN-021 après clôture020. [Guide de playtest](docs/RUN-020_PLAYTEST.md).

- **Systèmes absents :** Fire Gauntlet/Legendary/capacités, attaque d’atterrissage, grimpe, autres consommables, paliers/bonus HP, offrandes permanentes, secrets/mécanismes/portes secondaires, PNJ/narration et contenu des niveaux 2–10.
- **Vérification 0.2.0 :** clôture RUN-017 du 3 octobre : 24 suites / 631 contrôles de jeu + 8 à froid + 1 isolation = **640 PASS** ; cinématiques rendues **35/35**, N1 **11/11**, passes Claude et playtest humain validés.
- **Vérification historique 0.1.0 :** audit final du 2 octobre sur `40fd477`, Godot Windows **4.7.2** : import, isolation `user://`, **16 suites / 377 contrôles de jeu** réussis ; **49 contrôles visuels non headless** (chevalier 31, HUD 11, feedbacks 7), captures représentatives inspectées, 23 WAV valides et 4 tests du routeur réussis. Revue statique indépendante sans défaut concret ; ressources de production référencées présentes. Les 27 contrôles de cadence RUN-029 à 30/60/144 fps sont relus, non rejoués pendant cet audit. Mix RUN-014 sans écrêtage (pic −10,5 dBFS, limiteur coupé), écoute et rendu validés par l’humain. Revue Jev et limites dans `runs-journal.md`.

Les changements préexistants de `project.godot` et du TileSet ont été conservés. Les validations des RUN-001 à RUN-006 concernent leurs périmètres respectifs ; le prototype n'est pas encore conforme à l'ensemble des spécifications de `docs/`.

## Principe directeur

Le projet doit rester volontairement limité.

Une feature ou une modification importante doit servir directement la démo prévue et son expérience de jeu.

## Workflow de développement

Le projet avance par lots cohérents, pouvant durer plusieurs sessions, pour accélérer la production et donner plus d’autonomie aux agents sans multiplier les runs. Le plan compte 29 identifiants, dont 19 runs DONE et 10 lots BACKLOG, dans une limite de 30 ; les tests, corrections et recettes appartiennent au lot concerné. [AGENTS.md](AGENTS.md) définit le routage, la délégation et la protection des changements humains ; [runs-workflow.md](runs-workflow.md) fait autorité pour les lots, versions, dépendances, états et conditions de clôture.
