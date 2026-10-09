# RUN-021 — Passe visuelle N2 Blight Town (Claude)

**8 octobre 2026.** Demande humaine : enrichir visuellement N2 (décor, accessoires, fonds, parallaxe, textures, nuances, lumières), passe strictement esthétique ; aucun élément de gameplay, mob, piège ou collectable ; N3/N4 intouchés ; N1 facultatif. Main agent Claude Code Opus 5.5 ; deux sous-agents `visual_architect` en Sonnet 5.5 (High) sur fichiers disjoints : fonds (`backdrop_n2.py`) et accessoires (`props_n2.py`). Brief commun : `work/run021/n2pass/BRIEF.md`. RUN-021 reste **ACTIVE** ; validation artistique humaine requise.

## Identité retenue (proposition, validation humaine en attente)

« Un village de peste qui pourrit par le bas » : olive putride `ROT` et brun boue `MUD`, ciel olive-noir vers un ocre grisé, lune maladive voilée ; lumières chaudes `EMBER` (fenêtres, bûchers, torches) et rares accents **bile** jaune-olive, toujours sombres et distincts du vert de soin/Green Slime. Rouges sombres désaturés seulement (croix de peste).

## Changements

| Domaine | Résultat |
| --- | --- |
| Fond N2 | Cinq bandes au lieu de trois : ville de colline et cathédrale de peste avec bûchers et fumées (`far`), rempart à tours et gibets (`rampart`, nouvelle), rue à colombages (`mid`), façades proches (`near`). Quatre calques de fenêtres/bûchers éclairés qui respirent lentement. Ciel et lune propres à N2. |
| Cohérence verticale | Mur de fond souterrain en espace monde, calculé depuis le Terrain authored : remplissage du ciel avec fermeture des passages ≤ 4 cellules sous la ligne de rue. Pièces closes (cave basse, puits) → briques de cave ; vide sous la ville → terre profonde. La cave ne montre plus la ligne d'horizon de la ville. Habillage de cave : arche murée, niches à bougie, cage suspendue. |
| Terrain N2 | Maçonnerie de rue plus boueuse avec coulures de pourriture sous le rebord (rebord clair conservé pour la lisibilité) ; sous la ligne de rue (y ≥ 160) une assise de fondation qui s'enfonce, puis une terre pourrie stratifiée (texture monde 256×128 sans raccord : strates, gravats, éclats de brique, racines, veines de suintement). Décalques rares : soupiraux grillagés (certains éclairés), bouches d'égout, fissures, efflorescences, os/crânes. |
| Accessoires | 13 accessoires au sol (maisons à colombages, ruine de chapelle à cloche, chariot de peste, gibet à cage, bûcher à flamme animée, pilori, cloche de peste, corde à linge, efflorescences, ossements, corbeau), 4 muraux (tuyau d'égout, enseigne, pourriture, chaînes), 4 suspendus (cage, chiffons, lampe bile, lanterne N1) + toiles d'araignée dans les angles. Les tonneaux décoratifs N2 sont retirés : ils se confondaient avec les tonneaux de munitions cassables. |
| Atmosphère | Nappe de miasme au sol sur les rues longues (deux couches lentes, faible alpha), mouches au-dessus des tas pourris, fenêtres et bûchers animés. |

N1 : non modifié (déjà validé ; choix de ne pas risquer sa lecture). N3/N4 : chaque changement des scripts partagés est conditionné à `world_level == 2`.

## Fichiers

- Scripts de présentation (attribués par le contrat RUN-021) : `scripts/campaign_backdrop.gd` (chemin `_draw_n2`), `scripts/campaign_decor.gd` (N2 : tables, accrochage mural/plafond, lumières, miasme, mouches, marge `AmmoSupplies` 28 px, z −1), `scripts/campaign_terrain_skin.gd` (matériaux et décalques N2, nœud enfant `N2Underground` créé à l'exécution, z −60, méthode `is_deep`). Aucune scène modifiée.
- Générateurs (sources conservées, déterministes, Python sans dépendance) : `tools/art/run021/n2/{terrain_n2,atmos_n2,backdrop_n2,props_n2,board}.py`.
- Assets : `assets/run021/n2/` (15 PNG : fonds, lumières, atlas terrain 256×864, terre 256×128, mur de fond 96×96, décalques 128×16, miasme, halo neutre) et `assets/run021/n2/props/` (23 PNG + `props_n2.json` ancrages/lumières + `props_n2.sha256`). Empreintes détaillées : `work/run021/n2pass/BACKDROP_REPORT.md`, `PROPS_REPORT.md`.
- Import Godot 4.7.2 : `.import` générés par l'éditeur (lossless, sans mipmaps), filtrage nearest du projet, densité 1×.

## Vérifications exécutées (Godot 4.7.2 Windows, `work/run021/check.sh`, verrou et profil isolé)

- Import éditeur sans erreur après chaque lot (`n2pass-import4`).
- Captures natives 640×360 avant/après sur 16 vues N2 (sol, tours, fosse, puits, cave, pont haut, arène, porte) : `work/run021/n2pass/{before,t4,t5}/`, planches `ba_*.png`. Joueur téléporté, ennemis figés : ne prouve pas un parcours naturel.
- `tests/run021_backdrop_layers.gd` 9/9 (fond à z −100, ferry N2 visible devant le fond) ; `tests/run020_visual.gd` 57/57 ; `tests/run021_camera_bounds.gd` 20/20.
- `tests/run020_campaign.gd` 178 contrôles, 1 échec `native family red_slime`, reproduit à l'identique sur `HEAD` dans un worktree isolé : préexistant, sans lien.
- Coût (`tools/art/run021/perf_check.gd`, fenêtré, vsync) : N2 5,56 ms moyen (plafond d'affichage), pire 9,9 ms, 138 appels de dessin max. Une première mesure à 10,3 ms / 4519 appels (alternance de textures par cellule) a été corrigée par un dessin en passes par texture.
- N3/N4 : captures `HEAD` vs travail comparées au pixel ; les seules différences sont des éléments animés (nuages, ennemis, pièces, plantes), au même niveau que le bruit `HEAD`/`HEAD`.

## Limites et validation humaine

- Jugement artistique humain requis : identité N2, luminosité du ciel olive, densité, lecture des fenêtres orange à côté des pièces, miasme en mouvement, cave.
- Le placement procédural dépend du Terrain humain : les grands accessoires n'apparaissent que là où la hauteur libre le permet.
- Suivi proposé hors de cette passe : la même marge autour des munitions pour N3/N4 (à traiter dans leurs passes).
