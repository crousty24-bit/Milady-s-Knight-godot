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

**Version actuelle : 0.1.0, clôturée et validée localement.** L’humain valide toutes les runs réalisées le 2 octobre 2026 ; **RUN-001–014 et RUN-029 sont DONE**. RUN-010 est fusionnée via la PR #15 ; RUN-011, la réorganisation et les quatre passes Claude restent sur `feature/run-011-production-foundation`, dont la PR vers `develop` est autorisée. Le dépôt reste un slice, pas encore N1 conforme.

La roadmap compte **29 identifiants** (limite 30) : **15 DONE et 14 BACKLOG** vers **0.2.0 → 0.3.0 → 0.4.0 → 0.5.0 beta**. Chaque lot conserve son orchestrateur : Codex GPT-6.1 Sol Medium ou Claude Opus 5.5 ; délégation et Jev inchangés.

**Condition restante avant RUN-015 / 0.2.0 : fusion effective de cette branche dans develop.** L’audit final et la validation humaine sont terminés ; cette intervention ouvre la PR sans la fusionner ni lancer 0.2.0. Les catalogues 11–12 restent locaux ; le rattachement des licences aux fichiers hérités reste requis avant distribution en 0.5.0 beta.

### État vérifié

- **Moteur :** Godot **4.7.2 stable** retenu, version centralisée et vérifiée par les lanceurs. `project.godot` conserve **4.7**, renderer GL Compatibility. Windows 4.7.2 testé depuis WSL/UNC et disque local ; le runtime Linux 4.5.1 historique est conservé mais refusé par les lanceurs. Linux 4.7.2 non testé ici.
- **Rendu :** viewport **640×360**, fenêtre initiale 1280×720, stretch viewport/integer, nearest et pixel snapping. Terrain sur grille 16×16. RUN-004 adapte le HUD et le cadrage du slice à cette résolution.
- **Structure :** 11 scènes et 17 scripts dans `scenes/` et `scripts/`, démarrage `scenes/game.tscn` puis `scenes/vertical_slice.tscn`. Un autoload `Progression`. Aucun addon ni preset d’export trouvé lors de l'audit initial. Le TileSet de la scène est embarqué ; le fichier externe `assets/kingdom_tileset.tres` n’était pas référencé par les scènes/scripts de jeu inspectés lors de cet audit.
- **Niveau présent :** un terrain fixe à deux branches avec retours, **18 coins**, **8 Slimes** (5 Green, 3 Purple), deux ronces conservées, des piques fixes solides au sol et sur la limite droite (0,5 DMG), une limite de vide réglable par niveau (`void_y`, 304 px dans le slice), un bac mobile et une porte demandant 12 coins. `tests/fixtures/next_level.tscn` est une fixture héritée du slice, pas un deuxième niveau produit.
- **Joueur :** marche accélérée, saut variable, double saut, coyote/buffer, wall slide/wall jump, épée au sol/en l’air avec déduplication et occlusion ; santé fractionnaire, profils de réactions aux dégâts, mort et reprise automatique après trois secondes puis fondu. Les flèches remplacent Q/D/Z/S ; F répète les frappes tant qu'il est maintenu. Sword 0 inflige 0,5 DMG, avec 1 s entre départs, un geste de 0,28 s et une lame de 24 px depuis la main (1 RANGE = 1,5 bloc) ; une interruption conserve le cooldown. Invulnérabilité de 1,20 s avec flash blanc de 0,10 s puis clignotement ; hit-stun de 0,18 s et recul de 0,16 s conservés après audit. Le saut mural est validé par essai humain pour le slice actuel.
- **Ennemis/pièges :** Green/Purple en patrouille sans aggro, 1/2 HP et 0,5/1 DMG de contact (profils N1–4). Recul de 0,12 s sans immunité de contact ni aux impacts. Ronces traversables de 1 dégât, recul horizontal loin du danger, et vide létal. Les autres ennemis, le Boss et les pièges avancés sont absents.
- **Progression partielle :** coins limités au sceau ; surplus et kills donnent des bonus. Banque validée à la sortie et scène de reprise sauvegardées dans `user://progress.json` v1. Aucune persistance d’équipement, de HP bonus ou d’uniques, aucun coffre ni système de shards conforme.
- **Présentation :** HUD français VIE/SCEAU/BONUS en grappe compacte (cadre et portrait du chevalier, cœurs, icône de pièce, panneaux 9-slice), overlays pause/mort (panneau rouge, voile allégé)/victoire ; plus de bandeau inférieur d’indications : un `DialogueBanner` masqué est réservé aux futurs dialogues de PNJ, et la porte affiche une invite contextuelle (touche E, pièce, 12) au-dessus d’elle. Pas de menu principal, dialogue, slot d’équipement ou UI de récompense. L’essentiel des visuels est généré par `tools/art/` sur une palette commune (RUN-012–014 puis RUN-029) : Ashen Knight sur squelette (frames 64×64, garde de combat, course, sauts, atterrissage, glissade face au mur, dégâts, mort, enchaînement visuel de trois mouvements d’épée maintenu tant que F est tenu, sans changement des dégâts ni de la cadence), terrain en appareil irrégulier sur la `TileMapLayer` intacte, six couches de fond, accessoires enrichis et animés, Slimes, pièce, pièges, bac, porte et leurs VFX ; provenance dans `assets/VISUAL_CREDITS.md`. Audio routé par bus Master/Music/Ambient/SFX/UI : WAV Helton Yan (CC BY 4.0, crédit requis) normalisés à −8 dBFS, musique Pixabay *Dreamer* (nojisuma) à −13 LUFS ; l’ancienne musique est conservée pour un futur menu. Limite restante : sons de saut et double saut encore trop « sci-fi », reportés à RUN-027. Provenance dans `assets/AUDIO_CREDITS.md` ; celle des médias hérités (police, atlas de collision, sons non référencés) reste à établir.
- **Systèmes absents :** équipement/tir/upgrades/capacités, attaque d’atterrissage, grimpe, consommables, paliers/bonus HP, offrandes permanentes, secrets/mécanismes/portes secondaires, PNJ/narration et contenu des niveaux 2–10.
- **Vérification actuelle :** audit final du 2 octobre sur `40fd477`, Godot Windows **4.7.2** : import, isolation `user://`, **16 suites / 377 contrôles de jeu** réussis ; **49 contrôles visuels non headless** (chevalier 31, HUD 11, feedbacks 7), captures représentatives inspectées, 23 WAV valides et 4 tests du routeur réussis. Revue statique indépendante sans défaut concret ; ressources de production référencées présentes. Les 27 contrôles de cadence RUN-029 à 30/60/144 fps sont relus, non rejoués pendant cet audit. Mix RUN-014 sans écrêtage (pic −10,5 dBFS, limiteur coupé), écoute et rendu validés par l’humain. Revue Jev et limites dans `runs-journal.md`.

Les changements préexistants de `project.godot` et du TileSet ont été conservés. Les validations des RUN-001 à RUN-006 concernent leurs périmètres respectifs ; le prototype n'est pas encore conforme à l'ensemble des spécifications de `docs/`.

## Principe directeur

Le projet doit rester volontairement limité.

Une feature ou une modification importante doit servir directement la démo prévue et son expérience de jeu.

## Workflow de développement

Le projet avance par lots cohérents, pouvant durer plusieurs sessions, pour accélérer la production et donner plus d’autonomie aux agents sans multiplier les runs. Le plan compte 29 identifiants, dont 15 runs DONE, dans une limite de 30 ; les tests, corrections et recettes appartiennent au lot concerné. [AGENTS.md](AGENTS.md) définit le routage, la délégation et la protection des changements humains ; [runs-workflow.md](runs-workflow.md) fait autorité pour les lots, versions, dépendances, états et conditions de clôture.
