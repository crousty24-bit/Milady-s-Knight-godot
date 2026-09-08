# Astra — La Poterne des cendres

Vertical slice Godot 4.5.1 : chevalier, saut simple, épée, royaume abandonné et corruption. Projet autonome créé à partir des assets du test-1, qui reste intact.

## Jouer sur Windows

Double-cliquer **Lancer-Windows.cmd**. Le lanceur utilise l'installation Godot 4.5.1 déjà présente sur cette machine. Pour une autre installation, définir `GODOT_EXE` avec le chemin de l'exécutable.

On peut aussi importer **project.godot** dans Godot 4.5.1, puis lancer avec **F6** depuis `scenes/vertical_slice.tscn` ou **F5** depuis le projet. Depuis l'Explorateur Windows, le dossier est accessible à :

```text
\\wsl.localhost\Ubuntu\home\allen\mes_projets\astra-test-game-2d
```

La première ouverture importe les assets. Pas besoin de l'ancien projet. Il s'agit d'un projet jouable dans Godot, pas encore d'un export Windows autonome.

## Commandes

| Action | Clavier |
| --- | --- |
| Marcher | Q / D, A / D ou flèches |
| Sauter | Espace ; maintenir pour monter plus haut |
| Épée | J ou X ; une frappe par pression, au sol ou en l'air |
| Offrir l'or à la poterne | E à proximité |
| Pause | Échap |
| Recommencer entièrement | R |

3 PV. Les ronces lumineuses et les slimes blessent ; la fosse tue. Après un coup, une courte invulnérabilité évite les dégâts continus. Aucun double saut, saut mural, checkpoint ou support manette.

## Objectif

Collecter au moins **12 des 18 pièces**, offrir 12 or à la poterne, puis la traverser. Il y a **8 pièces communes**, **5 sur le passage haut** et **5 sur le chemin bas**. Une branche suffit ; les deux branches permettent de revenir et de tout explorer. Les ennemis ne génèrent pas de pièces. R ou la reprise après mort réinitialisent l'ensemble du niveau.

Village abandonné → embranchement → approche corrompue → poterne. Le chariot, la bannière arrachée et le ruban royal suggèrent le passage de la princesse. L'offrande demeure un habillage provisoire, conformément aux décisions.

Le parcours actuel est volontairement compact : le pilote de test connaissant la route termine en moins d'une minute. La durée et le plaisir d'une première découverte restent à mesurer avec des joueurs ; la cible initiale de 5–8 minutes n'est pas présentée comme atteinte.

## Développer et tester

Sous Linux/WSL :

```bash
./tools/run.sh
./tools/test.sh
```

`GODOT_BIN` permet de choisir le moteur. Sur cette machine, le runtime Linux 4.5.1 de validation est disponible dans `work/runtime/` (non versionné). Les tests tournent dans le vrai moteur, avec physique, collisions et actions d'entrée. Les scénarios de traversée ne téléportent pas le joueur et ne modifient pas sa santé ou son or. Les tests ciblés de systèmes isolent certaines positions/valeurs pour vérifier les seuils et les collisions.

Pour rejouer graphiquement les deux routes :

```bash
./tools/run.sh --script res://tests/routes.gd
```

Les résultats sont dans `work/test-results/`. La commande échoue si un test échoue ou si Godot écrit une erreur.

## Structure

- `scenes/vertical_slice.tscn` : niveau éditable, placements et collisions.
- `scenes/player.tscn`, `slime.tscn`, `coin.tscn`, `moving_platform.tscn`, `hazard.tscn`, `gold_gate.tscn`, `hud.tscn` : scènes autonomes.
- `scripts/` : comportements ; le niveau possède le gold et la tentative.
- `assets/kingdom_tileset.tres` : collisions des tuiles.
- `scripts/terrain_skin.gd` : pierre sobre dessinée sur la même grille, à partir des cellules du terrain. Le décor et les surfaces sont prévisualisés dans l'éditeur.
- `scripts/kingdom.gd` : décor pixel art dessiné à coordonnées fixes, sans système de corruption dynamique.
- `docs/IMPLEMENTATION.md` : décisions, ordre et critères.
- `docs/VALIDATION.md` : vérifications réalisées et limites.

Les outils `build_player.py`, `build_scenes.py`, `build_level.gd` et `configure_inputs.py` ont servi à créer les scènes. **Ils réécrivent leurs fichiers de sortie** : ne pas les exécuter après des modifications manuelles sans sauvegarde. Ils ne sont pas nécessaires pour jouer ou lancer les tests.

## Assets

Chevalier, slime, pièces, fonte et sons repris du projet fourni. Musique transcodée en Ogg Vorbis. Décor et habillage de terrain ajoutés dans les scripts de dessin. Les licences des assets d'origine n'étaient pas jointes ; elles restent à documenter avant une diffusion publique.
