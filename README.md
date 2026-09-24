# Milady's Knight

![Godot](https://img.shields.io/badge/Godot-4.7.2-478CBF?logo=godot-engine&logoColor=white)
![Version cible](https://img.shields.io/badge/Version%20cible-0.1.0-blue)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)
[![Tests RUN-001](https://img.shields.io/badge/Tests-150%20%2B%201%20passing-brightgreen)](#vérification-et-limites-connues)

**Milady's Knight** entre en production pour devenir une démo d’action-platformer 2D en pixel-art Dark Fantasy : dix niveaux conçus à la main, combat mêlée/distance, exploration, progression d’équipement et boss final.

Le joueur incarne **The Ashen Knight**, traverse le royaume corrompu et rejoint Darkveil Dungeon pour vaincre **Lupikal The Doombringer** et libérer **Princess Karla**. L’objectif de durée est de 1 à 2 heures, à confirmer par playtests.

**Le dépôt contient actuellement une scène de test jouable. RUN-001 a stabilisé le moteur, l’import et les tests ; le lancement F5 et la fermeture ont été confirmés par l’humain. RUN-002 a inventorié les assets et sa PR est fusionnée.** La cible finale est une démo **0.9.0 beta**, pas une release 1.0.0. Le badge `0.1.0` désigne le prochain jalon ; les tests couvrent les règles actuelles du prototype.

## Ce qui existe aujourd’hui

État inspecté le 21 septembre 2026 :

- Un niveau de test à deux branches avec retours : 18 coins, huit Slimes Green/Purple, ronces, fosse, bac mobile et porte de sortie à 12 coins.
- Marche, saut variable, double saut, wall slide/wall jump et épée au sol/en l’air.
- Santé, dégâts, recul, invulnérabilité, mort, reprise manuelle et pause simple.
- Une banque de bonus sauvegardée après sortie ; elle combine kills et surplus de coins et **n’est pas encore l’économie de shards cible**.
- HUD et messages français, sprites du prototype, décor dessiné en partie par code, quatre sons et une musique.
- Onze suites de tests moteur et des pilotes de parcours.

Le viewport actuel est **640×360** sur une grille de terrain 16×16. Les coffres, le tir, l’équipement, les consommables, les secrets, la narration, le bestiaire avancé et les niveaux 2–10 restent à produire. La fixture de transition dans `tests/fixtures/` ne constitue pas un niveau supplémentaire.

## Direction et roadmap

La boucle cible est : exploration → Gold Coins → combat → Shards → coffres → équipement → sortie → niveau suivant. Les niveaux restent fixes et la mort relance le niveau courant, avec les règles de persistance détaillées dans les spécifications.

| Version-cible validée | Résultat attendu | Runs (indicatives après 0.1.0) |
| --- | --- | ---: |
| 0.1.0 | Socle technique et combat élémentaire vérifiés | 11 |
| 0.2.0 | The Eidolon Vale, tutoriel, menus et reprise | 9–11 |
| 0.3.0 | Économie de coffres, armes standard et Blight Town | 6–8 |
| 0.4.0 | Ennemis avancés, secrets, niveaux 3–4 | 7–9 |
| 0.5.0 | Verticalité, capacités, légendaires, niveaux 5–6 | 8–10 |
| 0.6.0 | Dernières élites et niveaux 7–9 | 6–8 |
| 0.7.0 | Lupikal, niveau 10 et conclusion | 5–7 |
| 0.8.0 | Cohérence visuelle et sonore | 3–5 |
| 0.9.0 beta | Équilibrage, recette et builds de la démo finale | 4–6 |

La roadmap prévoit une **enveloppe indicative de 59 à 75 runs**, dont **11 détaillées pour 0.1.0** dans [runs-workflow.md](runs-workflow.md). Les versions suivantes restent décrites par objectifs et critères de jalon ; leur découpage sera réévalué après la version précédente. La première run conserve le moteur, l’import et la reproductibilité des tests comme périmètre.

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
| Aller à gauche / droite | Q / D |
| Sauter / double saut / saut mural | Space |
| Attaquer, une frappe par pression | F |
| Interagir avec la porte | E |
| Recommencer la tentative | R |
| Pause / reprendre | Escape |

Z/S sont déclarés mais sans grimpe. Les contrôles **cibles**, distincts de ceux actuellement implémentés, sont dans [docs/10_CONTROLS_KEYBINDS.md](docs/10_CONTROLS_KEYBINDS.md).

## Vérification et limites connues

Suite complète (Bash, `rg`, `timeout` et `mktemp` requis) :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/test.sh
```

Cette commande importe le projet, vérifie le chemin effectif de `user://`, puis exécute les onze suites. Chaque invocation écrit ses logs dans `work/test-results/run-*`. Les erreurs moteur, un échec, un timeout ou une fin de suite absente font échouer la commande, même si Godot retourne 0.

Les données utilisateur et la configuration sont isolées dès l’import : profil XDG sous Linux ; profil NTFS temporaire transmis à `APPDATA`/`LOCALAPPDATA` sous Windows via WSL. Ce dernier mode requiert `wslpath` et PowerShell Windows. Le profil est supprimé après succès et conservé après échec ; les logs restent disponibles. Le lancement normal via `run.sh` conserve la sauvegarde habituelle. Pour un import depuis zéro sans toucher au cache de travail, lancer la suite dans une copie du dépôt dépourvue de `.godot/` et `work/`.

Résultats RUN-001 du 22 septembre 2026 :

- Import depuis zéro sans erreur sous **4.7.2 Windows**, sur copies WSL/UNC et disque Windows local ; **150 contrôles de jeu + 1 contrôle d’isolation réussis par copie**. Sauvegardes réelles inchangées.
- Les trois erreurs d’import de l’audit provenaient d’un octet de remplissage RIFF manquant dans `coin.wav`, `jump.wav` et `tap.wav`. Les originaux sont conservés dans `assets/source/sounds/`, ignorés par l’import Godot ; les variantes compatibles restent dans `assets/sounds/`, aux chemins déjà utilisés. Les échantillons PCM sont identiques. Vérification indépendante : `python3 tests/wav_import.py`.
- Lancement **F5 confirmé par l’humain** le 22 septembre 2026 ; fermeture manuelle du jeu et de l’éditeur confirmée le 23 septembre. Le test graphique de notification de fermeture a aussi réussi. Les preuves et limites sont dans [runs-journal.md](runs-journal.md). Le binaire Linux 4.7.2 n’a pas été testé sur cette machine.

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
