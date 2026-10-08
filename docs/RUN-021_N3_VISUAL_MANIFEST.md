# RUN-021 — Passe visuelle N3 Black Forest (Claude)

**8 octobre 2026.** Demande humaine, après validation de la passe N2 et du correctif mémoire : réaliser le même type de passe visuelle pour N3. Le périmètre reste strictement esthétique : aucun élément de gameplay, mob, piège, collectable, cellule ni collision modifié. N1, N2 et N4 ne sont pas touchés. Main agent Claude Code Opus 5.5 ; deux sous-agents `visual_architect` en Sonnet 5.5 (High) sur des fichiers disjoints : les fonds (`backdrop_n3.py`) et les accessoires (`props_n3.py`). Brief commun : `work/run021/n3pass/BRIEF.md`. RUN-021 reste **ACTIVE** ; la validation artistique humaine est requise.

## Identité retenue (proposition, validation humaine en attente)

« Une forêt ancienne de nuit qui avale la vieille route et ses morts oubliés ». Dominantes de l'Art Bible : bleu nuit `NIGHT` et vert froid `PINE`. Lumière de lune froide (rampe `MOON`), venant du haut à droite comme la lune. Lucioles et champignons en blanc menthe froid (`FIREFLY`), distincts du vert de soin et du cyan spectral de N4. Chaleur rare : meules de charbonniers au loin, feu de camp, chandelle de sanctuaire, lanterne de chasseur.

## Changements

| Domaine | Résultat |
| --- | --- |
| Fond N3 | Cinq bandes et des faisceaux au lieu de trois bandes. `far` : crêtes, tour de guet en ruine et quatre meules fumantes. `ridge` (nouvelle) : mur de sapins dans le brouillard. `mid` : troncs, cercle de pierres levées et camp. `beams` (nouveau) : cinq faisceaux de lune très légers qui respirent lentement. `near` : quatre troncs géants noueux. S'y ajoutent quatre calques de lumières (braises, lucioles, champignons), plus un ciel et une lune propres à N3. |
| Terrain N3 | Quatre matériaux selon la profondeur. Sol forestier sous le rebord de mousse clair (conservé pour la lisibilité), avec litière et aiguilles. Couche de racines. Terre profonde froide (texture monde 256×128 sans raccord : blocs d'ardoise, racines, fils de mycélium). Écorce sur les colonnes d'au plus 3 cellules de large et d'au moins 5 de haut, ce qui fait lire la grande colonne et les piliers de la fosse comme des troncs et racines géants. Décalques rares : crâne, os, heaume rouillé, mycélium faiblement lumineux, terrier, nœud de racine, ardoise, pierre runique. |
| Souterrain | Le mur de fond souterrain de N2 est généralisé à N3 : grottes de racines (pièces closes) et terre profonde. La grotte basse ne montre plus le ciel ni la forêt. La fosse mortelle ouverte reste un vide, avec le fond visible. Habillage : creux de racines, niches à champignons lumineux, racines suspendues. |
| Accessoires | 28 accessoires originaux. Au sol (18) : tronc ancien, chêne noueux, deux sapins, bouleau mort, arche de racines, rondin, deux fougères, champignons, menhir, cairn, totem à crâne de cerf, camp de charbonnier, sanctuaire, souche à racines, chicot à chouette, rocher moussu. Muraux (4) : racines, champignons-consoles, mousse, lierre. Suspendus (4) : racines, lichen, amulette de brindilles, lanterne de chasseur. Souterrains (2). La souche RUN-020 est retirée de N3 : trop carrée, elle se lisait comme une caisse de munitions. Le tronc ancien, coupé en haut, n'est posé que sous un plafond de terrain. |
| Atmosphère | Brouillard froid au sol sur les longues surfaces (deux couches lentes, faible alpha). Lucioles clignotantes en essaims. Feu animé, chandelle et lueurs de champignons. Marge de 28 px autour des munitions étendue à N3 (suivi proposé par la passe N2). |

## Fichiers

- Scripts de présentation (ceux de la passe N2) :
  - `scripts/campaign_backdrop.gd` : le chemin `_draw_n2` devient `_draw_layers`, partagé N2/N3, avec les tables `N2_BANDS` et `N3_BANDS` ;
  - `scripts/campaign_decor.gd` : tables N3, accroches mur/plafond paramétrées, lumières `FUNGUS`/`SHRINE`, brouillard, lucioles, z −1 et `LAYOUT_VERSION` 3 ;
  - `scripts/campaign_terrain_skin.gd` : matériaux N3, cellules d'écorce, décalques, souterrain pour N2 et N3 avec un nœud `N3Underground`.
  - Chaque nouveau chemin est conditionné à `world_level == 3`. Aucune scène modifiée.
- Générateurs (sources conservées, déterministes, Python sans dépendance) : `tools/art/run021/n3/{backdrop_n3,props_n3,terrain_n3,atmos_n3}.py`. La lune a été réduite par le main agent après les premières captures (rayon 26 → 19, un cran plus sombre).
- Assets :
  - `assets/run021/n3/` : 15 PNG (ciel, cinq bandes, quatre lumières, faisceaux, atlas terrain 256×1152, terre 256×128, mur de fond 96×96, décalques 128×16, brouillard) ;
  - `assets/run021/n3/props/` : 28 PNG, plus `props_n3.json` (ancrages, lumières) et `props_n3.sha256` ;
  - empreintes : `work/run021/n3pass/n3_assets.sha256`. Rapports : `work/run021/n3pass/BACKDROP_REPORT.md`, `PROPS_REPORT.md`.
- Halo neutre partagé avec N2 (`assets/run021/n2/n2_glow.png`). Toile d'araignée N2 réutilisée.
- Import Godot 4.7.2 : `.import` générés par l'éditeur (lossless, sans mipmaps), filtrage nearest du projet, densité 1×.

## Vérifications exécutées

Environnement : Godot 4.7.2 Windows, `work/run021/check.sh`, verrou et profil isolé.

- **Import** : éditeur sans erreur (`n3pass-import1` à `3`).
- **Captures** : 15 vues N3 natives 640×360, zoom 1,2×, `--fixed-fps 60`, avant/après. Dossiers `work/run021/n3pass/{before,t4}/`, planches `ba_*.png`. Joueur téléporté, ennemis figés : cela ne prouve pas un parcours naturel.
- **N2/N4 inchangés** : captures `HEAD` (worktree isolé) contre travail, 14 vues N2 et 3 vues N4.
  - 12 vues sont identiques au pixel ; les autres diffèrent de 5 à 40 pixels.
  - Ces écarts sont localisés sur les flammes de torches de la porte, le compteur et les reflets des piques. Le bruit entre deux captures de `HEAD` va jusqu'à 71 pixels.
- **Suites** : `run021_backdrop_layers` 9/9, `run020_visual` 57/57, `run021_camera_bounds` 20/20.
- **Campagne** (`run020_campaign`, 178 contrôles) :
  - Sur `HEAD` + cette passe seule (worktree isolé) : un seul échec, `native family red_slime`, identique sur `HEAD`.
  - Dans le checkout partagé, un second échec apparaît : `physical E opens exit within optional spending budget`. Il vient d'une modification de `scenes/forbidden_graveyard.tscn` survenue pendant la passe (22:25) : porte, pièces et crânes déplacés, `SkullSwarm8` ajouté. Ce fichier est hors de ce périmètre, il n'a pas été touché et il est exclu du commit.
- **Rechargement à chaud** : `work/run021/n3pass/reload/hot_reload_n3.gd`, des scripts de `HEAD` vers ceux de la passe dans N3, donne 6/6, avec un calque `N3Underground` recréé une seule fois. Le scénario N2 existant donne 5/5.
- **Durée** : scène N3 en fenêtre pendant 90 s, au-delà du seuil de 48 s du défaut N2. Mémoire statique stable (50,1 → 50,0 Mo), pire image 8,4 ms.
- **Coût** : `perf_check`, N3 à 5,56 ms en moyenne (plafond vsync), pire 7,05 ms, 168 appels de dessin au maximum, 70 accessoires.

## Limites et validation humaine

- Jugement artistique humain requis : identité N3, taille et clarté de la lune, faisceaux, densité, troncs en écorce, lecture des totems et du brouillard en mouvement.
- Le placement procédural dépend du Terrain humain. Les grands accessoires n'apparaissent que là où la hauteur libre et les marges de gameplay le permettent. N3 étant dense en ennemis et pièges, les plus grands sont rares, et le tronc ancien n'a trouvé aucune place sous plafond dans la scène actuelle.
- La lumière des accessoires a été dessinée depuis le haut-gauche par le sous-agent, alors que la lune, les fonds et l'écorce l'ont depuis le haut-droit. Les reflets concernés sont de rares pixels ; à revoir si l'écart se voit en jeu.
- Suivi hors de cette passe : adapter `tests/run020_campaign.gd` (sortie N4) aux nouveaux placements humains de N4, ce qui relève de Codex/gameplay.
