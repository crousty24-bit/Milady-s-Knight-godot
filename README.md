# Milady's Knight

![Godot](https://img.shields.io/badge/Godot-4.7.2-478CBF?logo=godot-engine&logoColor=white)
![Version publiée](https://img.shields.io/badge/Version%20publi%C3%A9e-0.2.0-blue)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)

**Milady's Knight** est un action-platformer 2D en pixel-art Dark Fantasy, développé pour devenir une démo de dix niveaux conçus à la main. Le joueur incarne **The Ashen Knight**, traverse le royaume corrompu et rejoint Darkveil Dungeon pour vaincre **Lupikal The Doombringer** et libérer **Princess Karla**. La durée visée est de 1 à 2 heures, à confirmer par playtests.

## Version et état de la branche

**0.2.0 reste la dernière version publiée et le jalon N1 validé.** La branche `feature/run-020-021-campaign` étend le jeu à la campagne N1–N4 et prépare le contenu de la cible 0.3.0. L’humain a validé toutes les dernières passes Codex et Claude le 9 octobre 2026. L’audit global de la branche est en cours et une PR vers `develop` a été demandée ; le statut final des runs et les résultats consolidés de l’audit seront consignés après cette revue. Cette demande ne promeut pas la version publiée.

La branche contient les niveaux fixes Eidolon Vale, Blight Town, Black Forest et Forbidden Graveyard, leurs transitions, ennemis, pièges, récompenses et zones d’exploration. Elle inclut notamment les armes standard et leurs munitions, les réserves persistantes entre niveaux, les commandes AZERTY/QWERTY/classique/personnalisées avec remappage clavier et souris, le HUD d’équipement et de munitions, ainsi que les Secret Walls avec indices et révélation. Les détails fonctionnels et les limites de vérification sont dans [brief.md](brief.md), [runs-journal.md](runs-journal.md) et les spécifications de [docs/](docs/README.md).

Le viewport est **640×360**, sur une grille de terrain 16×16. La démo finale vise dix niveaux, les capacités et armes légendaires, un boss et une conclusion. Le plan des lots et ses critères d’acceptation font autorité dans [runs-workflow.md](runs-workflow.md).

## Ouvrir le prototype

Le projet utilise GDScript, sans addon tiers identifié.

- **Godot 4.7.2 stable** est la version retenue dans `tools/godot-version.txt`, vérifiée par les lanceurs. `project.godot` conserve sa déclaration compatible **4.7**.
- Importer `project.godot` dans Godot puis lancer **F5** pour le menu principal via `scenes/game.tscn`. **F6** depuis `scenes/vertical_slice.tscn` lance la scène de régression.
- Sous Linux ou WSL, indiquer l’exécutable installé :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/run.sh
```

Sous Windows, `Lancer-Windows.cmd` accepte `GODOT_EXE`. Sous WSL, `tools/run.sh` accepte aussi `GODOT_EXE` et convertit les chemins Windows. Pour ouvrir l’éditeur, ajouter `--editor`. Aucun export autonome n’est configuré dans le dépôt.

## Vérification

La suite disponible se lance avec Bash, `rg`, `timeout` et `mktemp` :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/test.sh
```

La dernière recette consolidée publiée documentée ici reste celle du jalon **0.2.0 (3 octobre 2026)** : 640 contrôles, dont 631 contrôles de jeu, huit contrôles à froid et une vérification d’isolation, plus des rendus N1 et cinématiques. Elle ne décrit pas la branche campagne actuelle. Les preuves de la branche et leurs limites figurent dans [runs-journal.md](runs-journal.md) ; l’audit global demandé est en cours.

## Sources de vérité

- [AGENTS.md](AGENTS.md) : règles de travail du dépôt.
- [brief.md](brief.md) : contexte, systèmes présents et état de la branche.
- [runs-workflow.md](runs-workflow.md) : roadmap, statuts et critères de clôture.
- [runs-journal.md](runs-journal.md) : exécutions et preuves réellement consignées.
- [learning.md](learning.md) : explications pédagogiques des implémentations.
- [docs/README.md](docs/README.md) : index des spécifications et documents de campagne.

Les générateurs d’auteur peuvent écrire des scènes, ressources ou réglages. Ils ne sont nécessaires ni au lancement ni aux tests ; ne pas les exécuter automatiquement après des modifications manuelles.

## Origine du projet

Ce projet d’apprentissage prolonge un premier test Godot issu du tutoriel [The ultimate introduction to Godot 4](https://youtu.be/LOhfqjmasi0?si=tdgg3XWfNvRXQkSV), ensuite remanié en vertical slice. La production suit désormais les spécifications de **Milady’s Knight**.

[Godot Engine](https://godotengine.org/) est le moteur du projet. L’origine pédagogique ne remplace pas les notices de licence et d’attribution des assets.
