# Milady's Knight

![Godot](https://img.shields.io/badge/Godot-4.7.2-478CBF?logo=godot-engine&logoColor=white)
![Version actuelle](https://img.shields.io/badge/Version-0.2.0-blue)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)
[![Tests clôture 0.2.0](https://img.shields.io/badge/Tests-640%20passing-brightgreen)](#vérification-et-limites-connues)

**Milady's Knight** entre en production pour devenir une démo d’action-platformer 2D en pixel-art Dark Fantasy : dix niveaux conçus à la main, combat mêlée/distance, exploration, progression d’équipement et boss final.

Le joueur incarne **The Ashen Knight**, traverse le royaume corrompu et rejoint Darkveil Dungeon pour vaincre **Lupikal The Doombringer** et libérer **Princess Karla**. L’objectif de durée est de 1 à 2 heures, à confirmer par playtests.

**Version actuelle : 0.2.0, jalon N1 validé. RUN-001–017 et RUN-029 DONE.** Les lots de la 0.2.0 sont intégrés dans `develop`, dont la PR #18 fusionnée le 3 octobre 2026. La livraison du jalon sur `main` suit la promotion autorisée le 5 octobre 2026. La prochaine cible est **0.3.0** ; la démo finale vise **0.5.0 beta**.

## Ce qui existe aujourd’hui

État vérifié à la clôture de RUN-017 le 3 octobre 2026 :

- **Eidolon Vale (N1)**, niveau fixe à deux branches avec retours, Slimes Green/Purple, coins, piques, vide, bac mobile et sortie à 12 coins.
- Marche, saut variable, double saut, wall slide/wall jump, Sword0 et Longbow0 ; changement d’arme avec A.
- Santé fractionnaire, dégâts, recul, invulnérabilité, mort puis reprise automatique.
- Coins et shards séparés ; banque de shards, équipements, flags et dialogues persistants dans une sauvegarde v2, migration v1 explicite.
- Menu New Game / Continue / Controls / Quit et pause Resume / Restart / Quit to menu ; HUD anglais avec slots d’équipement.
- Coffre tutoriel gratuit, potion mineure, tutoriels contextuels et dialogue avec l’Ancient Spirit ; résurrection initiale uniquement lors de New Game.
- Visuels, animations, VFX et audio intégrés et validés humainement. Provenance : `assets/VISUAL_CREDITS.md` et `assets/AUDIO_CREDITS.md`.
- Vingt-quatre suites moteur, deux sessions N1 à froid et des pilotes avec rendu.

Le viewport actuel est **640×360** sur une grille de terrain 16×16. Les autres armes et améliorations, capacités, secrets, bestiaire avancé, boss et niveaux 2–10 restent à produire. `vertical_slice.tscn` et `tests/fixtures/` restent des supports de régression.

## Direction et roadmap

La boucle cible est : exploration → Gold Coins → combat → Shards → coffres → équipement → sortie → niveau suivant. Les niveaux restent fixes et la mort relance le niveau courant, avec les règles de persistance détaillées dans les spécifications.

| Version | Résultat attendu | Runs |
| --- | --- | --- |
| 0.1.0 clôturée | Socle et passes visuelles/audio validés | 001–014 et 029 DONE |
| **0.2.0 actuelle** | N1, tutoriel, équipement, menus et reprise validés | 015–017 DONE |
| 0.3.0 | Économie, armes standard, bestiaire, secrets et N2–4 | 018–021 |
| 0.4.0 | Capacités, légendaires, N5–10, Boss et conclusion | 022–026 |
| 0.5.0 beta | Présentation finale, équilibrage, recette et exports | 027–028 |

**29 identifiants au total : 18 runs DONE et 11 lots BACKLOG.** Chaque lot comprend intégration, tests et corrections, avec son orchestrateur désigné à l’avance dans [runs-workflow.md](runs-workflow.md) : Codex GPT-6.1 Sol Medium ou Claude Opus 5.5 selon le travail. La délégation et Jev restent inchangés hors remplacement ciblé du modèle Codex et de `code_worker`.

**Jalon 0.2.0 :** passes Claude, playtest humain N1 sur les deux chemins, recette et revue de clôture terminés. RUN-018 reste BACKLOG ; sa présence dans la roadmap ne lance pas le lot suivant.

Le scope ne prévoit pas de génération procédurale, multijoueur, checkpoint intra-niveau, remapping, support souris/manette ni contenu jouable après la libération de Karla.

## Ouvrir le prototype

Le projet utilise GDScript, sans addon tiers identifié.

- **Godot 4.7.2 stable** est la version retenue dans `tools/godot-version.txt`, vérifiée par les lanceurs avant ouverture. `project.godot` conserve sa déclaration compatible **4.7**.
- Le vieux runtime Linux **4.5.1** sous `work/` est conservé mais n’est plus sélectionné automatiquement. Utiliser un binaire **4.7.2** natif ou le binaire Windows depuis WSL.
- Importer `project.godot` dans Godot puis lancer **F5** pour le menu principal via `scenes/game.tscn`, puis N1 (`scenes/eidolon_vale.tscn`). **F6** depuis `scenes/vertical_slice.tscn` lance directement la scène de test.

Linux / WSL, en indiquant l’exécutable installé :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/run.sh
```

Sous Windows, `Lancer-Windows.cmd` accepte la variable `GODOT_EXE` ; son chemin par défaut vise Godot 4.7.2 dans `%USERPROFILE%\OneDrive\Documents\Godot Engine`. Sous WSL, `tools/run.sh` accepte aussi `GODOT_EXE` et convertit les chemins Windows. Pour ouvrir l’éditeur, ajouter `--editor`. Aucun export autonome n’est encore configuré dans le dépôt.

### Commandes actuellement jouables

| Action | Touche actuelle |
| --- | --- |
| Aller à gauche / droite | Flèches gauche / droite |
| Monter / descendre (action réservée) | Flèches haut / bas |
| Sauter / double saut / saut mural | Space |
| Attaquer / tirer, répétition en maintien | F |
| Interagir / confirmer | E |
| Confirmer le redémarrage après victoire finale | E |
| Changer d’équipement | A |
| Phrase suivante du dialogue | Space |
| Attaque d’atterrissage / spéciale (actions réservées) | G / R |
| Pause / reprendre | Escape |

Les flèches haut/bas et G/R restent réservées. Les menus se parcourent au clavier ; Escape ferme les panneaux ou ouvre la pause. La liste complète des touches est dans [docs/10_CONTROLS_KEYBINDS.md](docs/10_CONTROLS_KEYBINDS.md).

## Vérification et limites connues

Suite complète (Bash, `rg`, `timeout` et `mktemp` requis) :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/test.sh
```

Cette commande importe le projet, vérifie le chemin effectif de `user://`, puis exécute les vingt-quatre suites et deux sessions N1 à froid. Chaque invocation écrit ses logs dans `work/test-results/run-*`. Les erreurs moteur, un échec, un timeout ou une fin de suite absente font échouer la commande, même si Godot retourne 0.

Les données utilisateur et la configuration sont isolées dès l’import : profil XDG sous Linux ; profil NTFS temporaire transmis à `APPDATA`/`LOCALAPPDATA` sous Windows via WSL. Ce dernier mode requiert `wslpath` et PowerShell Windows. Le profil est supprimé après succès et conservé après échec ; les logs restent disponibles. Le lancement normal via `run.sh` conserve la sauvegarde habituelle. Pour un import depuis zéro sans toucher au cache de travail, lancer la suite dans une copie du dépôt dépourvue de `.godot/` et `work/`.

Dernière recette de clôture : **0.2.0, 3 octobre 2026**, Godot Windows 4.7.2 : **631 contrôles de jeu / 24 suites + 8 contrôles à froid + 1 isolation = 640 PASS** ; cinématiques avec rendu **35/35** et N1 **11/11**, captures inspectées. Passes artistiques et playtest N1 validés par l’humain. Les preuves détaillées sont dans [runs-journal.md](runs-journal.md).

Recette historique : **clôture 0.1.0, 2 octobre 2026**, Godot 4.7.2 Windows, état `40fd477` : import normal et isolation des sauvegardes, **377 contrôles / 16 suites**, puis **49 contrôles visuels non headless** (chevalier, HUD, feedbacks) ; captures représentatives inspectées. Les 23 WAV et quatre tests du routeur passent. Aucun défaut reproduit ; les validations visuelles et de ressenti sont reçues. Les 27 contrôles de cadence RUN-029 à 30/60/144 fps ont été relus sans être rejoués lors de cette clôture.

RUN-001 avait également vérifié deux imports propres (WSL/UNC et disque Windows) après correction du remplissage RIFF de trois WAV, avec PCM et originaux conservés. Les preuves détaillées restent dans [runs-journal.md](runs-journal.md). Le binaire Linux 4.7.2 n’a pas été testé sur cette machine.

Autres limites : dépendances à des coordonnées et tailles fixes du slice, sons de tir/impact/coffre et mix d’acquisition à reprendre, mort avec arc et détail du logo reportés à RUN-027, absence de presets d’export. Les médias hérités ont été inventoriés dans des catalogues locaux, non suivis par Git ; leur correspondance avec les sources et licences n'est pas établie. Ce contrôle est différé à la sélection finale des assets et devra être résolu avant distribution. Les changements manuels présents restent la référence de travail.

## Structure du dépôt

```text
assets/          Sprites, sons, musique, police, TileSet et imports
scenes/          Démarrage, slice, joueur, Slime, coin, piège, bac, porte, HUD
scripts/         Gameplay, présentation et autoload Progression
tests/           Tests moteur, pilotes de parcours et fixture de transition
tools/           Lanceurs, tests et générateurs d’auteur
docs/           Spécifications du produit cible
```

Les générateurs d’auteur écrivent des fichiers de scènes, ressources ou configuration. Ils ne sont nécessaires ni au lancement ni aux tests ; ne pas les exécuter automatiquement après des modifications manuelles.

## Sources de vérité

- [AGENTS.md](AGENTS.md) : règles de travail du dépôt.
- [brief.md](brief.md) : contexte, scope et état vérifié.
- [runs-workflow.md](runs-workflow.md) : audit et roadmap par versions/runs.
- [runs-journal.md](runs-journal.md) : résultats des runs réellement exécutées.
- [learning.md](learning.md) : explications après implémentation, fondées sur les changements vérifiés.
- [docs/README.md](docs/README.md) : index des spécifications. Elles décrivent la cible, sans prouver son implémentation.

Les anciennes docs de `docs/old` ont été lues puis retirées lors de la passe d’audit, à la demande du propriétaire du projet.

## Origine du projet

Ce projet d’apprentissage prolonge un premier test Godot issu du tutoriel [The ultimate introduction to Godot 4](https://youtu.be/LOhfqjmasi0?si=tdgg3XWfNvRXQkSV), ensuite remanié avec Astra GPT-6 en vertical slice. La production réutilise cette base tout en suivant désormais les spécifications de **Milady’s Knight**.

[Godot Engine](https://godotengine.org/) est le moteur du projet. L’origine pédagogique ne remplace pas les notices de licence et d’attribution des assets.
