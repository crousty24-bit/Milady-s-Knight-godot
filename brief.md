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

Audit du **21 septembre 2026**, complété par les vérifications techniques de **RUN-001 le 22 septembre 2026** sur copies temporaires. Les preuves d’exécution sont dans [runs-journal.md](runs-journal.md) ; l’audit initial et la planification restent dans [runs-workflow.md](runs-workflow.md).

### Version-cible actuelle

**0.1.0 validée comme cible : socle de production vérifié.** La roadmap va jusqu’à **0.9.0 beta**, démo finale. RUN-001 est réalisée techniquement et attend sa validation humaine ; les autres runs n’ont pas commencé. Le dépôt reste une scène de test issue du vertical slice, pas encore le niveau 1 conforme aux nouvelles spécifications.

### État vérifié

- **Moteur :** Godot **4.7.2 stable** retenu, version centralisée et vérifiée par les lanceurs. `project.godot` conserve **4.7**, renderer GL Compatibility. Windows 4.7.2 testé depuis WSL/UNC et disque local ; le runtime Linux 4.5.1 historique est conservé mais refusé par les lanceurs. Linux 4.7.2 non testé ici.
- **Rendu :** viewport **320×180**, fenêtre 1280×720, stretch viewport/integer, nearest et pixel snapping. La cible **640×360** n’est pas encore appliquée. Terrain sur grille 16×16.
- **Structure :** 9 scènes, 12 scripts de jeu, démarrage `scenes/game.tscn` puis `scenes/vertical_slice.tscn`. Un autoload `Progression`. Aucun addon ni preset d’export trouvé. Le TileSet de la scène est embarqué ; le fichier externe `assets/kingdom_tileset.tres` n’est pas référencé par les scènes/scripts de jeu inspectés.
- **Niveau présent :** un terrain fixe à deux branches avec retours, **18 coins**, **8 Slimes** (5 Green, 3 Purple), deux ronces, une fosse, un bac mobile et une porte demandant 12 coins. `tests/fixtures/next_level.tscn` est une fixture héritée du slice, pas un deuxième niveau produit.
- **Joueur :** marche accélérée, saut variable, double saut, coyote/buffer, wall slide/wall jump, épée au sol/en l’air avec déduplication et occlusion ; 3 HP entiers, recul/invulnérabilité, mort et reprise **manuelle** avec R. F attaque à la pression, pas en maintien. Q/D et Z/S sont encore les touches déclarées ; Z/S n’ont pas de déplacement vertical implémenté.
- **Ennemis/pièges :** Green/Purple en patrouille sans aggro, 3/4 HP et 1 dégât de contact ; ces valeurs diffèrent de la cible. Ronces traversables de 1 dégât et vide létal. Les autres ennemis, le Boss et les pièges avancés sont absents.
- **Progression partielle :** coins limités au sceau ; surplus et kills donnent des bonus. Banque validée à la sortie et scène de reprise sauvegardées dans `user://progress.json` v1. Aucune persistance d’équipement, de HP bonus ou d’uniques, aucun coffre ni système de shards conforme.
- **Présentation :** HUD français VIE/SCEAU/BONUS, hints, overlays pause/mort/victoire ; pas de menu principal, dialogue, slot d’équipement ou UI de récompense. 6 PNG, 4 WAV, 1 OGG et 1 police intégrés, plus un TileSet ; décor et épée en partie dessinés par code. Trois WAV ont un remplissage RIFF corrigé sans changer le PCM ; leurs originaux sont conservés dans `assets/source/sounds/`, hors import. Provenance/licences des médias encore à établir.
- **Systèmes absents :** équipement/tir/upgrades/capacités, attaque d’atterrissage, grimpe, consommables, paliers/bonus HP, offrandes permanentes, secrets/mécanismes/portes secondaires, PNJ/narration et contenu des niveaux 2–10.
- **Vérification actuelle :** sous Windows **4.7.2**, imports propres puis **150 contrôles de jeu + 1 contrôle d’isolation réussis** sur chacune des deux copies (WSL/UNC et disque local). Les erreurs `p_position > length` sont résolues par le remplissage RIFF des trois WAV. Sauvegardes de test isolées ; sauvegardes réelles inchangées. Notification de fermeture graphique testée ; F5 et fermeture de l’éditeur restent à confirmer par l’humain. Ces tests couvrent les anciennes règles du slice.

Les changements préexistants de `project.godot` et du TileSet ont été conservés. L’audit ne valide ni les nouvelles features décrites dans `docs/`, ni la conformité finale du prototype à ces spécifications.

## Principe directeur

Le projet doit rester volontairement limité.

Une feature ou une modification importante doit servir directement la démo prévue et son expérience de jeu.

## Workflow de développement

Le projet avance par versions-cibles : 0.1.0 comporte 11 runs détaillées ; les versions suivantes restent des intentions à affiner après chaque jalon, avec une enveloppe totale indicative de 59 à 75 runs. La run active est précisée à partir du dépôt réel. [AGENTS.md](AGENTS.md) définit le routage du contexte, l’autonomie et la protection des changements humains ; [runs-workflow.md](runs-workflow.md#cycle-de-vie) définit les états, les vérifications et la clôture des runs.
