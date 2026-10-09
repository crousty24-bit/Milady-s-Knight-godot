# RUN-021 — Passe visuelle N4 Forbidden Graveyard (Claude)

**9 octobre 2026.** Demande humaine : « Réalise le même type de passe visuelle que tu as fait pour N2, N3, cette fois-ci pour N4. » Le périmètre reste strictement esthétique : aucun élément de gameplay, mob, piège, collectable, porte, bouton, cellule ni collision modifié. N1, N2 et N3 ne sont pas touchés. Main agent Claude Code Opus 5.5 ; deux sous-agents `visual_architect` en Sonnet 5.5 (High) sur des fichiers disjoints : les fonds (`backdrop_n4.py`) et les accessoires (`props_n4.py`). Brief commun : `work/run021/n4pass/BRIEF.md`. RUN-021 reste **ACTIVE** ; la validation artistique humaine est requise.

## Identité retenue (proposition, validation humaine en attente)

« Une nécropole interdite sur une colline, sous une lune froide, où les morts ne reposent pas ». Dominantes de l'Art Bible : violet désaturé `DUSK_VIOLET` et cyan spectral grisé `SPECTRAL`, toujours sombre et à faible alpha (le cyan saturé reste au Magic Shield, le violet saturé aux shards). Lune gris-violet pâle, plus petite (rayon 18) et plus sombre que l'ancienne lune cyan. Lumières froides : bougies de tombes, lanterne et encensoir, feux follets. Chaleur rare : quelques bougies de deuil. Les cryptes annoncent les catacombes de N5 (Haunted Caves).

## Changements

| Domaine | Résultat |
| --- | --- |
| Fond N4 | Cinq bandes au lieu de trois. `far` : colline de la nécropole, basilique en ruine à flèche brisée, toits de cryptes, obélisques, cyprès. `ridge` (nouvelle) : rangées de cryptes et de mausolées, chapelle-ossuaire, ifs et grilles dans la brume. `mid` : pente du cimetière (stèles, croix, grands mausolées, saules, fosse ouverte). `wisps` (nouvelle) : voiles spectraux très légers qui montent entre les tombes et respirent lentement, à la place des faisceaux de N3. `near` : grandes stèles penchées, angle de mausolée, if noueux, petit ange sur socle, grille. Quatre calques de lumières (bougies, portes de cryptes, fenêtres de chapelle, feux follets), ciel et lune propres à N4. |
| Terrain N4 | Quatre matériaux. Maçonnerie funéraire (grand appareil gris-violet froid, lichen gris, mousse dans les joints) au-dessus de la ligne de sol et en assise de surface ; le rebord clair est conservé pour la lisibilité. Sous la ligne de sol, une assise de fondation qui s'enfonce dans une terre de tombes (texture monde 256×128 sans raccord : strates, pierres enfouies, fragments d'os, planches de cercueil pourries, racines). Les colonnes étroites et hautes deviennent des piliers de crypte cannelés, éclairés du haut à droite comme la lune. Décalques rares : crâne, os, coin de cercueil, champignon de lueur spectrale (terre), plaque d'épitaphe, croix gravée, fissure à racine, case funéraire scellée (maçonnerie). La masse au-dessus de la ligne de sol (tour, blocs de mausolée) reste en maçonnerie, comme en N2. |
| Souterrain | Le mur de fond souterrain de N2/N3 est généralisé à N4 : cryptes en grand appareil sombre avec cases scellées, terre profonde ailleurs. Les cryptes sous la dalle et le couloir de sortie bas ne montrent plus le cimetière ni le ciel. Deux règles propres à N4 : une cellule close reliée au vide du bas reste « crypte » tant qu'il y a du terrain sous elle dans sa colonne, seul le vide sans fond reste noir profond (le danger se lit) ; et sous la ligne de sol, les colonnes hors de la grille comptent comme fermées, pour que le ciel ne descende pas par le bord droit jusqu'au couloir de sortie. Habillage : niche à sarcophage ou mur d'ossuaire au centre des sols larges, loculi à bougie froide aux extrémités, chaînes au plafond. Le puits ouvert à droite (x ≥ 4928, 14 cellules de large) reste un vrai puits à ciel ouvert. |
| Accessoires | 32 accessoires originaux. Au sol (21) : quatre stèles, stèle au corbeau, croix celtique, petit et grand mausolée, obélisque, colonne brisée, ange en pierre sur socle, tombeau bas, tertre à marqueur, if, saule mort, grille basse, bougies froides et chaudes, lanterne à flamme froide, couronne sur piquet, petit tas de crânes. Muraux (4) : case funéraire, vigne morte, chaîne à anneau, plaque au crâne gravé. Suspendus (4) : chaînes, encensoir à flamme froide, racines, bannière funéraire. Souterrains (3). La croix et la bougie de tombe RUN-020 restent ; le mausolée, le saule, la clôture RUN-020, les tombes N1, les os et l'arbre mort laissent la place au nouveau jeu. Densité relevée (espacement 0,8 → 0,55) ; 87 accessoires posés au sol dans la recette finale, 45 muraux, suspendus et toiles d'araignée, 15 éléments de crypte. |
| Atmosphère | Brume des tombes au ras du sol sur les longues surfaces (deux couches lentes, faible alpha, bouffées qui montent), six feux follets lents qui apparaissent et s'effacent, tenus loin des éléments de jeu pour ne jamais passer pour un projectile ou un crâne. Marge de 28 px autour des munitions étendue à N4. Décor à z −1 en N4 aussi, pour que les plateformes mobiles restent devant. |
| Mur secret | Le masque du mur secret (`secret_wall_mask.gd`) dessine désormais ses cellules via le skin N4 (`cell_layers()` partagé) : maçonnerie, décalques et ombrage identiques, sans couture. Les fixtures sans skin N4 gardent l'ancien rendu pierre. Les indices de fissures livrés en parallèle (`4a51873`) restent lisibles sur la nouvelle maçonnerie. |

## Fichiers

- Scripts de présentation (ceux des passes N2/N3), chaque nouveau chemin conditionné à `world_level == 4` :
  - `scripts/campaign_backdrop.gd` : table `N4_BANDS` dans le chemin `_draw_layers` partagé. L'ancien chemin à trois bandes, devenu inaccessible, est retiré ; ses PNG restent sur disque ;
  - `scripts/campaign_decor.gd` : jeu N4, tables murales/suspendues, lumières `SPECTRAL`/`SPECTRAL_LAMP`, brume, feux follets, z −1, `LAYOUT_VERSION` 4 ;
  - `scripts/campaign_terrain_skin.gd` : matériaux N4, piliers, décalques, `cell_layers()` public, souterrain N4 avec un nœud `N4Underground` et l'habillage des cryptes ;
  - `scripts/secret_wall_mask.gd` : rendu délégué au skin N4, ancien chemin conservé en repli.
  - Aucune scène modifiée.
- Générateurs (sources conservées, déterministes, Python sans dépendance) : `tools/art/run021/n4/{backdrop_n4,props_n4,terrain_n4,atmos_n4}.py`.
- Assets :
  - `assets/run021/n4/` : 15 PNG (ciel, cinq bandes, quatre lumières, atlas terrain 256×1152, terre 256×128, mur de fond 96×96, décalques 128×16, brume 256×32) ;
  - `assets/run021/n4/props/` : 32 PNG, plus `props_n4.json` (ancrages, lumières) et `props_n4.sha256` ;
  - empreintes : `work/run021/n4pass/n4_assets.sha256`. Rapports : `work/run021/n4pass/BACKDROP_REPORT.md`, `PROPS_REPORT.md`.
- Halo neutre partagé avec N2 (`assets/run021/n2/n2_glow.png`). Toile d'araignée N2 réutilisée.
- Import Godot 4.7.2 : `.import` générés par l'éditeur (lossless, sans mipmaps), filtrage nearest du projet, densité 1×.

## Vérifications exécutées

Environnement : Godot 4.7.2 Windows, `work/run021/check.sh`, verrou et profil isolé. Recette finale dans un worktree isolé `work/wt-n4-head` = `HEAD` `4a51873` + les seuls fichiers de cette passe ; une partie a d'abord été jouée sur `a77af5f` + la passe, avant le commit parallèle des indices du mur secret.

- **Import** : éditeur sans erreur (`n4pass-import1`, `n4pass-import2`, `v2-import`).
- **Captures** : 17 vues N4 natives 640×360, zoom 1,2×, avant/après. Dossiers `work/run021/n4pass/{before,final}/`, planches `ba_*.png`. Les vues 12, 14 et 17 « avant » viennent du worktree `HEAD` (les premières avaient été prises après le début des modifications et ont été jetées). Joueur téléporté, ennemis figés : cela ne prouve pas un parcours naturel.
- **N2/N3 inchangés** : 29 vues avec `--fixed-fps 60`, scripts de `HEAD` contre ceux de la passe dans le même worktree. 14 vues identiques au pixel ; les autres diffèrent de 7 à 147 pixels, sur la brume, les lucioles et un Chud animé. Le bruit entre deux captures `HEAD` de N3 va jusqu'à 194 pixels (même vue : 194 contre 147).
- **Suites** sur `4a51873` + passe : `run021_backdrop_layers` 9/9, `run020_visual` 57/57, `secret_wall_reveal` 39/39 et ses trois phases à froid dans un même profil 5/5, 4/4, 10/10, `secret_wall_intro` 38/38, `run019_exploration` 27/27, `run019_integration` 42/42, pilote de rendu des indices 21/21.
- **Échecs préexistants, identiques sans la passe** (scripts de `HEAD` dans le même worktree) : `run020_campaign` 178 contrôles avec le seul `native family red_slime` ; `run021_camera_bounds` 20 contrôles avec deux échecs sur le ferry ascendant (réglages récents du ferry vertical) ; `run019_visual` 47 contrôles avec un échec `rendered mechanisms and reveal match gameplay state` (le test attend 30 images, le fondu dure 0,6 s).
- **Mur secret en rendu** : pilote natif `work/secret-wall/render.gd` 16/16 sur `a77af5f` + passe, captures fermé/ouvert inspectées au zoom, sans couture. Sur `4a51873`, ce pilote antérieur à la fenêtre « A Strange Wall » dépasse son délai, sans rapport avec cette passe ; le pilote des indices le remplace (21/21, fissures inspectées). Captures dans `work/run021/n4pass/secret/`.
- **Rechargement à chaud** : `work/run021/n4pass/reload/hot_reload_n4.gd`, des scripts de `HEAD` vers ceux de la passe dans N4, donne 7/7, avec un calque `N4Underground` recréé une seule fois.
- **Durée** : scène N4 en fenêtre pendant 90 s. Mémoire statique stable (54,6 Mo), pire image 9,6 ms.
- **Coût** : `perf_check`, N4 à 5,56 ms en moyenne (plafond vsync), pire 7,30 ms, 224 appels de dessin au maximum, 87 accessoires.

## Limites et validation humaine

- Jugement artistique humain requis : identité N4, lune, densité des bandes lointaines (la bande `far`/`ridge` est chargée en toits et flèches, à éclaircir si elle concurrence les ennemis en jeu), voiles et feux follets en mouvement, maçonnerie violet-gris, piliers, cryptes.
- Silhouettes à juger à l'échelle réelle : l'ange (lisible comme une gargouille ou une chauve-souris ?), la stèle au corbeau, le tombeau bas (lu comme une rampe ?), la plaque au crâne très discrète, le mur d'ossuaire (fond uniquement, jamais en jeu).
- Le placement procédural dépend du Terrain humain : N4 étant dense en ennemis, pièges et mécanismes, les grands accessoires (grand mausolée, saule, ange) sont rares.
- La masse de sol au-dessus de la porte finale devient de la terre de tombes (règle de profondeur commune), plus claire que le mur de fond mais moins contrastée que la maçonnerie.
- Le travail parallèle de la session Codex (indices et introduction du mur secret, `4a51873`) a été préservé et n'est pas modifié par cette passe.
