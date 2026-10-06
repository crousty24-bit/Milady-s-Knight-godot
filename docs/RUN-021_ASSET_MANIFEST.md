# RUN-021 — Manifeste Claude de la passe visuelle N1–4

**6 octobre 2026.** Exécution du [contrat visuel](RUN-021_CLAUDE_HANDOFF.md) et du [complément Archer/audio](RUN-021_CLAUDE_HANDOFF_02.md) par Claude Code Opus 5.5 (main), avec trois sous-agents Sonnet 5.5 sur des fichiers disjoints : reproduction Archer (`asset_integrator`, lecture seule en production), musique N4 et audit SFX (`asset_integrator`), bande proche des fonds (`visual_architect`). Branche `feature/run-020-021-campaign`. RUN-021 reste **ACTIVE** : la passe technique Codex, la recette intégrée, la validation artistique et sonore et le playtest humains restent à faire. Aucune validation artistique n’est présumée.

## 1. Baseline humaine

- Les six fichiers gelés correspondent à `work/run021/human-baseline-sha256.json` (vérifié au début, après l’import et à la remise). Pendant la passe, l’humain les a commités sans changer leur contenu (`e28a612`) ; ils restent gelés.
- Aucune scène N1–3 n’a été modifiée. Pour N4, seule la référence `Music` de `scenes/forbidden_graveyard.tscn` est patchée (voir [revue audio](RUN-021_AUDIO_REVIEW.md)). Aucune cellule TileMap, collision, position d’acteur, ID, budget ni valeur de gameplay n’a été touché. Aucun générateur de scène n’a été rejoué.
- `world_tileset.png` et les PNG du chevalier n’ont pas été modifiés.

## 2. Audit avant/après (captures natives 640×360)

Script : `tools/art/run021/capture_levels.gd`. Scènes de production, joueur placé par code (téléportation) et acteurs actifs pendant 40 images. N1 = `eidolon_vale.tscn`, avec `n1_intro_enabled = false` pour la vue. Ces captures **ne prouvent pas** un parcours naturel. Pour chaque passe : 26 vues, 52/52 contrôles.

- Avant : `work/run021/captures/before/` (log `work/test-results/run-YB7eMVfg`).
- Après la peau de terrain et le décor : `work/run021/captures/a1/` (`run-D09i0SHt`).
- Après la bande proche : `work/run021/captures/near/` (`run-wJ8AD1HH`, `run-qyQlU3OM`, `run-7kkbpBPQ`).
- Planches : `work/run021/captures/zoom/` (`board-n1..n4`, `ground-compare`, `cmp-*`) et `work/run021/preview/` (`board-near-*`, `cmp-*`, `stack_n*`).

| Constat (avant) | Niveaux | Traitement |
| --- | --- | --- |
| Colonnes sombres à bords nets sous chaque marche surélevée. L’ombrage dépendait de la seule profondeur verticale. | N1–4 | **Corrigé** : profondeur relâchée d’un cran par cellule le long de chaque rangée, ce qui donne un dégradé doux (`terrain_skin.gd`, `campaign_terrain_skin.gd`). |
| Terre N3 trop proche du fond, masses praticables lues comme des trous | N3 | **Corrigé** : rampe de sol éclaircie d’un cran vers un brun froid désaturé, rangée supérieure de mousse plus claire d’un cran (`terrain_black_forest.png`). Même disposition et mêmes graines. |
| Remplissage plat sous la bande moyenne : vide sans profondeur en vue haute et dans les fosses | N2–4 | **Corrigé** : bande proche par biome, parallaxe 0,42 / 0,2. N2 : façades et charpentes ; N3 : troncs et fougères ; N4 : mur de cimetière, grilles, cryptes et tombes. Elle se fond dans une couleur finale. |
| Décor clairsemé, presque aucun point lumineux, contrairement au village éclairé de N1 | N2–4 | **Traité** : densité accrue (`SPACING_SCALE` 1,0/0,6/0,9 → 0,75/0,6/0,8), poids des lanternes N2 et des bougies N4 portés de 3 à 5, champignons N3 (poids 3 → 4) avec une lueur de spores lente et grisée, distincte du vert de soin. `avoid_margins` inchangé. |
| HUD, modales, télégraphies, objets | N1–4 | Cohérents (HUD et modales partagés). **Aucun changement** dans cette passe ; ils n’ont pas été recapturés pour les modales. |
| Ampleur des niveaux très inférieure à la cible humaine | N1–4 | Écart consigné, sans cible chiffrée. Décor, peau de terrain et fonds sont procéduraux et suivent les futurs agrandissements de terrain sans modification. |

Restes identifiés, non traités : la terre N2 reprend la maçonnerie de N1, avec une identité « rot » discrète ; le fond des fosses N3/N4 reste sombre sur environ 60 px ; dans les fosses N2, les traverses de bois de la bande proche sont des lignes faibles. Aucune d’elles n’a de dessus plat, mais il faut juger en jeu si elles se lisent comme des plateformes.

## 3. Fichiers

| Fichier | Nature | Changement |
| --- | --- | --- |
| `scripts/terrain_skin.gd` (N1) | Présentation (attribué par le contrat) | Ajout de `_depths()`, profondeur relâchée. Aucune autre ligne. |
| `scripts/campaign_terrain_skin.gd` | Présentation | Même `_depths()`. N3 utilise l’atlas `FOREST`, thème 0 pour toutes les entrées de l’atlas. |
| `scripts/campaign_decor.gd` | Présentation | `Light.SPORE`, poids, `SPACING_SCALE`, lueur de spores. Placement, marges et règles d’exclusion inchangés. |
| `scripts/campaign_backdrop.gd` | Présentation (sous-agent) | `NEARS`, bande proche, `LOOKS[b][2]` = couleur finale (`111317`, `0a1012`, `120f17`), `LOOKS[b][6]` = sol de la bande moyenne. |
| `assets/run021/terrain_black_forest.png` | 256×288, 18 rangées × 16 masques de 16 px | SHA-256 `6f28e5ff…f946` |
| `assets/run021/bg_blight_town_near.png` | 512×190 RGBA, raccord horizontal | `882870f4…ae14` |
| `assets/run021/bg_black_forrest_near.png` | 512×190 | `91c4b57d…23cb` |
| `assets/run021/bg_forbidden_graveyard_near.png` | 512×190 | `8167b803…afc4` |
| `tools/art/run021/terrain_run021.py`, `backdrop_run021.py` | Générateurs (sources conservées) | Importent RUN-020 et le projet en lecture seule |
| `tools/art/run021/capture_levels.gd`, `perf_check.gd`, `archer_repro.gd` | Outils de preuve | — |
| `assets/VISUAL_CREDITS.md` | Crédits | Section RUN-021 |

Imports : générés par Godot 4.7.2, identiques aux `.import` RUN-020 hors uid/chemins (lossless, sans mipmaps). Le filtrage nearest est hérité du projet. Aucun agrandissement : la densité de pixels est native. Ce sont des assets de fond et de tuiles, sans pivot d’animation.

## 4. Vérifications exécutées (Godot 4.7.2 Windows, `work/run021/check.sh` : `flock work/.godot.lock`, profil isolé)

- Import éditeur sans erreur, après chaque lot.
- `tests/run020_visual.gd` : **57 render checks, 0 failures** (`run-Io8wqtm7`). `tests/n1_visual.gd` : **11 N1 presentation checks, 0 failures** (`run-h5pLgXez`).
- Coût du décor (`perf_check.gd`, `run-u3i4jk9P`, indicatif, une exécution fenêtrée, vsync) : frame moyenne 5,56 ms sur les quatre niveaux, soit le plafond d’affichage. Pire frame 6,6–7,5 ms. Accessoires : 39 en N2, 50 en N3, 58 en N4. Appels de dessin max : 160 en N1, 88 à 115 en N2–4. 4/4 contrôles réussis.
- Aucune suite de gameplay n’a été relancée par Claude : aucune logique, collision ni scène de terrain n’a changé. La recette complète revient à Codex.

## 5. Skeleton Archer : cause reproduite, transmise à Codex

Rapport complet : `work/run021/archer/REPORT.md`, avec la télémétrie `telemetry.csv`, l’analyse de cellules `cells.txt` et la séquence `flip_sequence_f030-075.png` (log `run-A2Ct0Ycb`).

- **Cause : données de niveau et logique, pas le dessin.** Les six archers de production (Black Forest Enemy05/08/12, Forbidden Graveyard Enemy03/08/13) ont `patrol_left = patrol_right = 0`. `run019_enemy.gd` inverse alors `direction` à chaque traversée de l’origine, c’est-à-dire toutes les 1 à 2 images physiques (x oscille d’environ 0,37 px). `velocity.x` vaut ±22 et `flip_h` bascule à chaque image : la marche est jouée sur place, en miroir, à 30–60 Hz. Le défaut apparaît hors aggro et disparaît pendant l’aggro (idle, windup, shoot stables), d’où son caractère intermittent. J’ai vérifié statiquement les six valeurs dans les scènes.
- Mesures : 150 changements de `flip` sur 150 images pour quatre archers, 75 sur 150 pour deux. Un archer de contrôle avec la patrouille par défaut (−40..40) ne change que 2 fois en 420 images. Les 26 cellules de la feuille sont propres : pieds sur la rangée 31, aucun pixel parasite, centre de masse stable. Le décalage de 0,6 px du corps amplifie légèrement l’effet, mais n’en est pas la cause.
- **Aucune correction de présentation appliquée.** Correction proposée à Codex : retirer les surcharges nulles, ou traiter une patrouille de largeur nulle comme stationnaire (`velocity.x = 0`, direction maintenue). Ce choix (sentinelle fixe ou non) relève du gameplay et du layout. Un atténuement purement visuel (hystérésis de `flip_h` et de `walk`) ne serait à envisager que si Codex refuse la correction logique.
- Limites : une seule exécution. Pas de correspondance image par image avec la vidéo humaine. Coup reçu pendant le windup non exercé. L’humain doit confirmer que ce miroir correspond bien au défaut observé.

## 6. Remise à Codex

Fichiers Claude livrés et éditions arrêtées : les quatre scripts de présentation ci-dessus, `assets/run021/**`, `tools/art/run021/**` et les crédits. L’audio (`forbidden_graveyard.tscn` node `Music`, `assets/run021/audio/**`, `assets/source/run021/**`, `AUDIO_CREDITS.md`) est décrit dans la [revue audio](RUN-021_AUDIO_REVIEW.md). `scripts/run019_enemy.gd` n’a **pas** été modifié par Claude ; il est libre pour la passe Codex.

Risques et points à reprendre :
- Le décor est déterministe mais densifié : les tests ou pilotes qui supposent une absence d’accessoire à un endroit sont à adapter. Aucun test actuel ne lit `_placed`.
- Les tests qui inspectent les couleurs du fond ou de la terre N3 sont à adapter à l’état livré.
- À corriger côté Codex : patrouille nulle des archers (§5), plus les réglages déjà attribués (portée et aggro des tireurs, tir joueur, poursuite de Bloated et Chud).
- Validation humaine requise : ajustement artistique (terre N3, bandes proches, densité et lueurs), lecture en mouvement de la parallaxe, absence de confusion fond/plateforme en jeu réel.
