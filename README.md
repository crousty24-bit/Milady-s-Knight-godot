# Milady's Knight

![Godot](https://img.shields.io/badge/Godot-4.7.2-478CBF?logo=godot-engine&logoColor=white)
![Version actuelle](https://img.shields.io/badge/Version-0.1.0-blue)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)
[![Tests RUN-011](https://img.shields.io/badge/Tests-377%20%2B%201%20passing-brightgreen)](#vérification-et-limites-connues)

**Milady's Knight** entre en production pour devenir une démo d’action-platformer 2D en pixel-art Dark Fantasy : dix niveaux conçus à la main, combat mêlée/distance, exploration, progression d’équipement et boss final.

Le joueur incarne **The Ashen Knight**, traverse le royaume corrompu et rejoint Darkveil Dungeon pour vaincre **Lupikal The Doombringer** et libérer **Princess Karla**. L’objectif de durée est de 1 à 2 heures, à confirmer par playtests.

**Version actuelle : 0.1.0, socle validé localement ; RUN-001–011 DONE.** Le dépôt contient encore un slice jouable. La prochaine cible est **0.2.0** (N1 complet) et la démo finale vise **0.5.0 beta**. La branche RUN-011 reste ouverte pour la réorganisation et d’éventuelles passes Claude avant validation finale et fusion.

## Ce qui existe aujourd’hui

État vérifié par RUN-011 le 30 septembre 2026, validation confirmée le 2 octobre :

- Un niveau de test à deux branches avec retours : 18 coins, huit Slimes Green/Purple, ronces, fosse, bac mobile et porte de sortie à 12 coins.
- Marche, saut variable, double saut, wall slide/wall jump et épée au sol/en l’air.
- Santé fractionnaire, dégâts, recul, invulnérabilité, mort puis reprise automatique et pause simple.
- Une banque de bonus sauvegardée après sortie ; elle combine kills et surplus de coins et **n’est pas encore l’économie de shards cible**.
- HUD et messages français, sprites du prototype, décor dessiné en partie par code, sons de feedback par bus audio et musique provisoire (provenance : `assets/AUDIO_CREDITS.md`).
- Seize suites de tests moteur et des pilotes de parcours.

Le viewport actuel est **640×360** sur une grille de terrain 16×16. Les coffres, le tir, l’équipement, les consommables, les secrets, la narration, le bestiaire avancé et les niveaux 2–10 restent à produire. La fixture de transition dans `tests/fixtures/` ne constitue pas un niveau supplémentaire.

## Direction et roadmap

La boucle cible est : exploration → Gold Coins → combat → Shards → coffres → équipement → sortie → niveau suivant. Les niveaux restent fixes et la mort relance le niveau courant, avec les règles de persistance détaillées dans les spécifications.

| Version | Résultat attendu | Runs |
| --- | --- | --- |
| **0.1.0 actuelle** | Socle validé ; compléments visuels conditionnels sur la branche ouverte | 001–011 DONE ; 012–014 réservées |
| 0.2.0 | N1, tutoriel, équipement, menus et reprise | 015–017 |
| 0.3.0 | Économie, armes standard, bestiaire, secrets et N2–4 | 018–021 |
| 0.4.0 | Capacités, légendaires, N5–10, Boss et conclusion | 022–026 |
| 0.5.0 beta | Présentation finale, équilibrage, recette et exports | 027–028 |

**28 identifiants au total, dont 11 déjà validés et trois réserves conditionnelles.** Chaque lot comprend intégration, tests et corrections, avec son orchestrateur désigné à l’avance dans [runs-workflow.md](runs-workflow.md) : Codex GPT-6.1 Sol Medium ou Claude Opus 5.5 selon le travail. La délégation et Jev restent inchangés hors remplacement ciblé du modèle Codex et de `code_worker`.

**Avant 0.2.0 :** validation de la réorganisation, choix des éventuelles passes Claude, achèvement et validation des travaux retenus sur `feature/run-011-production-foundation`, puis validation finale et fusion autorisée dans `develop`. RUN-015 ne démarre qu’après cette fusion effective.

Le scope ne prévoit pas de génération procédurale, multijoueur, checkpoint intra-niveau, remapping, support souris/manette ni contenu jouable après la libération de Karla.

## Ouvrir le prototype

Le projet utilise GDScript, sans addon tiers identifié.

- **Godot 4.7.2 stable** est la version retenue dans `tools/godot-version.txt`, vérifiée par les lanceurs avant ouverture. `project.godot` conserve sa déclaration compatible **4.7**.
- Le vieux runtime Linux **4.5.1** sous `work/` est conservé mais n’est plus sélectionné automatiquement. Utiliser un binaire **4.7.2** natif ou le binaire Windows depuis WSL.
- Importer `project.godot` dans Godot puis lancer **F5** pour la reprise via `scenes/game.tscn`. **F6** depuis `scenes/vertical_slice.tscn` lance directement la scène de test.

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
| Attaquer, frappes répétées en maintien | F |
| Interagir avec la porte | E |
| Confirmer le redémarrage après victoire finale | E |
| Attaque d'atterrissage / spéciale / équipement (actions réservées) | G / R / A |
| Pause / reprendre | Escape |

Les flèches haut/bas et G/R/A sont mappées mais sans effet de gameplay pour l'instant. Il n'y a pas encore de menu de pause à trois choix ni de redémarrage volontaire en cours de tentative. La liste complète des touches est dans [docs/10_CONTROLS_KEYBINDS.md](docs/10_CONTROLS_KEYBINDS.md).

## Vérification et limites connues

Suite complète (Bash, `rg`, `timeout` et `mktemp` requis) :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/test.sh
```

Cette commande importe le projet, vérifie le chemin effectif de `user://`, puis exécute les seize suites. Chaque invocation écrit ses logs dans `work/test-results/run-*`. Les erreurs moteur, un échec, un timeout ou une fin de suite absente font échouer la commande, même si Godot retourne 0.

Les données utilisateur et la configuration sont isolées dès l’import : profil XDG sous Linux ; profil NTFS temporaire transmis à `APPDATA`/`LOCALAPPDATA` sous Windows via WSL. Ce dernier mode requiert `wslpath` et PowerShell Windows. Le profil est supprimé après succès et conservé après échec ; les logs restent disponibles. Le lancement normal via `run.sh` conserve la sauvegarde habituelle. Pour un import depuis zéro sans toucher au cache de travail, lancer la suite dans une copie du dépôt dépourvue de `.godot/` et `work/`.

Dernière recette : **RUN-011, 30 septembre 2026**, sous Godot 4.7.2 Windows : import, **377 contrôles de jeu / 16 suites**, plus isolation des sauvegardes ; 27 contrôles de cadence et 27 captures à 30/60/144 fps. Parcours des deux branches et retours, pause/mort et reprise vérifiés ; saut mural validé par essai humain. Aucun défaut reproduit dans ce périmètre. Ces contrôles n’ont pas été rejoués pour la réorganisation documentaire du 2 octobre.

RUN-001 avait également vérifié deux imports propres (WSL/UNC et disque Windows) après correction du remplissage RIFF de trois WAV, avec PCM et originaux conservés. Les preuves détaillées restent dans [runs-journal.md](runs-journal.md). Le binaire Linux 4.7.2 n’a pas été testé sur cette machine.

Autres limites : dépendances à des coordonnées et tailles fixes du slice, HUD français, sauvegarde limitée à la banque de bonus et au niveau, absence de presets d’export. Les médias hérités ont été inventoriés dans des catalogues locaux, non suivis par Git ; leur correspondance avec les sources et licences n'est pas établie. Ce contrôle est différé à la sélection finale des assets et devra être résolu avant distribution. Les changements manuels présents restent la référence de travail.

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
