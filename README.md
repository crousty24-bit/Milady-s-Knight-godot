# Milady's Knight

![Godot déclaré](https://img.shields.io/badge/Godot-4.7-478CBF?logo=godot-engine&logoColor=white)
![Version cible](https://img.shields.io/badge/Version%20cible-0.1.0-blue)
![Language](https://img.shields.io/badge/Language-GDScript-478CBF)
![Status](https://img.shields.io/badge/Status-Playable%20Prototype-f0ad4e)
[![Tests de l’audit](https://img.shields.io/badge/Tests%20%28audit%29-150%20passing-brightgreen)](#vérification-et-limites-connues)

**Milady's Knight** entre en production pour devenir une démo d’action-platformer 2D en pixel-art Dark Fantasy : dix niveaux conçus à la main, combat mêlée/distance, exploration, progression d’équipement et boss final.

Le joueur incarne **The Ashen Knight**, traverse le royaume corrompu et rejoint Darkveil Dungeon pour vaincre **Lupikal The Doombringer** et libérer **Princess Karla**. L’objectif de durée est de 1 à 2 heures, à confirmer par playtests.

**Le dépôt contient actuellement une scène de test jouable. Les versions, la roadmap et le périmètre de RUN-001 sont validés ; son lancement attend un accord explicite. Aucune run de production n’a commencé.** La cible finale est une démo **0.9.0 beta**, pas une release 1.0.0. Le badge `0.1.0` désigne le prochain jalon ; les 150 contrôles correspondent à l’audit du 21 septembre 2026.

## Ce qui existe aujourd’hui

État inspecté le 21 septembre 2026 :

- Un niveau de test à deux branches avec retours : 18 coins, huit Slimes Green/Purple, ronces, fosse, bac mobile et porte de sortie à 12 coins.
- Marche, saut variable, double saut, wall slide/wall jump et épée au sol/en l’air.
- Santé, dégâts, recul, invulnérabilité, mort, reprise manuelle et pause simple.
- Une banque de bonus sauvegardée après sortie ; elle combine kills et surplus de coins et **n’est pas encore l’économie de shards cible**.
- HUD et messages français, sprites du prototype, décor dessiné en partie par code, quatre sons et une musique.
- Onze suites de tests moteur et des pilotes de parcours.

Le viewport actuel est **320×180**. La référence de production **640×360**, les coffres, le tir, l’équipement, les consommables, les secrets, la narration, le bestiaire avancé et les niveaux 2–10 restent à produire. La fixture de transition dans `tests/fixtures/` ne constitue pas un niveau supplémentaire.

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

- `project.godot` déclare **Godot 4.7** ; le binaire Windows disponible a été vérifié en **4.7.2**.
- Le runtime Linux local et les lanceurs historiques visent encore **4.5.1**. Ce décalage doit être traité en RUN-001 ; le runtime sous `work/` est local et ignoré par Git.
- Importer `project.godot` dans Godot puis lancer **F5** pour la reprise via `scenes/game.tscn`. **F6** depuis `scenes/vertical_slice.tscn` lance directement la scène de test.

Linux / WSL, en indiquant l’exécutable installé :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/run.sh
```

Sous Windows, `Lancer-Windows.cmd` accepte la variable `GODOT_EXE` avec le chemin du moteur. Son chemin par défaut 4.5.1 est historique ; définir explicitement le binaire disponible. Aucun export autonome n’est encore configuré dans le dépôt.

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

Commande historique de la suite complète :

```bash
GODOT_BIN=/chemin/vers/godot ./tools/test.sh
```

Cette commande importe le projet et écrit ses logs dans `work/test-results/`. Pour comparer des moteurs sans toucher aux imports de travail, utiliser une copie du projet comme pendant l’audit. Les pilotes `--script` désactivent la sauvegarde normale ; la suite de persistance utilise des fichiers temporaires dédiés.

Résultats de l’audit du 21 septembre 2026 :

- **150 contrôles réussis sous 4.5.1 Linux**, import sans erreur.
- **150 contrôles réussis sous 4.7.2 Windows** ; cependant, l’import préalable sur copie via WSL/UNC produit trois erreurs moteur `p_position > length` malgré un code de sortie nul. Cause non déterminée ; ne pas considérer l’import Windows comme validé.
- Aucun playtest humain, contrôle graphique ou écoute n’a été réalisé pendant cette passe. Les tests valident les règles actuelles du slice, pas les features de la démo à venir.

Autres limites : dépendances à des coordonnées et tailles fixes du slice, HUD français, sauvegarde limitée à la banque de bonus et au niveau, absence de presets d’export. La provenance et les licences des médias hérités ne sont pas documentées dans le dépôt ; elles devront être établies ou les médias remplacés avant distribution. Les changements manuels présents restent la référence de travail.

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
