# Visuels — provenance et licences

Les visuels hérités du prototype (`sprites/knight.png`, `slime_*.png`, `coin.png`, `world_tileset.png`, `platforms.png`, police `PixelOperator8.ttf`) restent sans provenance établie. Après RUN-012/013, seuls la police et `world_tileset.png` (atlas de collision du `TileSet`, recouvert par l'habillage) restent utilisés en jeu ; `knight.png` et `slime_green.png` servent encore à la comparaison d'échelle RUN-003 ; ce contrôle est différé à la recette des licences avant distribution (RUN-027–028).

## Générés pour le projet (RUN-012, 2 octobre 2026)

Pixel art produit par code, sans asset tiers ni génération par IA, à partir de l'artwork du projet (`artwork & logo/concept art 1.png` de la bibliothèque locale) : plaques acier, cape rouge, tabard sombre à emblème or. Le script est la source : relancer `python3 tools/art/knight.py` régénère les fichiers ci-dessous à l'identique (Python 3 seul, aucune dépendance).

| Fichier de jeu | Contenu |
| --- | --- |
| `sprites/ashen_knight.png` + `ashen_knight_frames.tres` | Ashen Knight, frames 32×32 (pieds en bas de la ligne 30, corps centré) : idle 4, run 6, rise 2, fall 2, wall 2, attack 3, hurt 1, dead 4. |
| `sprites/ashen_sword.png` | Épée en 32 angles, cases 64×64, pivot au centre (main du joueur). |
| `sprites/ashen_sword_smear.png` | Traînée en croissant pour la fenêtre de contact, mêmes angles. |
| `sprites/vfx_hit_spark.png` | Étincelle d'impact, 5 × 16×16. |
| `sprites/vfx_air_puff.png` | Anneau d'air du double saut, 5 × 24×10. |
| `sprites/vfx_wall_dust.png` | Poussière de glissade murale, 3 × 6×8. |

## Générés pour le projet (RUN-013, 2 octobre 2026)

Même méthode, sur la palette commune `tools/art/palette.py`. Générateurs : `tools/art/world.py` (terrain, décor, accessoires ; main agent), `tools/art/creatures.py` (Slimes, pièce, icônes HUD) et `tools/art/hazards.py` (piques, ronces, bac, porte), ces deux derniers écrits par des subagents délégués puis revus et intégrés. Chaque script régénère ses fichiers à l'identique (contrôle par empreinte MD5).

| Fichiers de jeu | Contenu |
| --- | --- |
| `sprites/terrain_stone.png`, `terrain_tufts.png` | Tuiles 16×16 par masque d'exposition (16) × 3 variantes × 2 thèmes (village, corruption) ; herbes et vrilles de surface. |
| `sprites/bg_sky.png`, `bg_far.png`, `bg_mid.png`, `bg_mist.png` | Ciel nocturne et lune de sang fixes à l'écran ; citadelle lointaine, forêt morte et brume en parallaxe. |
| `sprites/prop_*.png` (house, house_ruined, tree_a/b, tree_dead_a/b, cart, signpost, banner, blight_a/b/c, far_tower_a/b, ribbon_spear) | Accessoires narratifs du slice. |
| `sprites/prop_ferry.png`, `prop_gold_gate.png` | Bac ; cadre de porte et panneau scellé/ouvert. |
| `sprites/trap_spikes.png`, `trap_thorns.png` | Piques fixes, ronces corrompues. |
| `sprites/enemy_slime_green.png`, `enemy_slime_purple.png` | Slimes, 6 frames 24×24. |
| `sprites/item_gold_coin.png`, `hud_icons.png` | Pièce, 8 frames 16×16 ; cœurs plein/demi/vide, pièce et sceau en 12×12. |

## Bibliothèque locale examinée et non retenue (RUN-012)

Le dépôt est public : un pack dont la licence interdit la redistribution des fichiers, même modifiés, ne peut pas y être intégré. Les pages itch.io n'ont pas pu être lues automatiquement (protection Cloudflare) ; ces verdicts proviennent de résumés de recherche et doivent être confirmés par l'humain avant toute réutilisation.

| Pack | Auteur | Verdict |
| --- | --- | --- |
| Tiny RPG Character Asset Pack 01/02 | Zerie | Redistribution interdite ; Soldier ≈ 17×21 px en vue RPG, hors échelle Art Bible. |
| RPG Effects free | BDragon1727 | Non commercial, redistribution interdite (non vérifié). |
| Weapons / Tools Asset 16x16 | DantePixels | Distribution directe interdite (non vérifié). |
| Free - Raven Fantasy Icons | Clockwork Raven | Redistribution interdite (non vérifié). |
| 16x16 Assorted RPG Icons | Shade | **CC0, vérifié** sur OpenGameArt ; utilisable. |
| Fichiers `pixellab-*.png` | Humain, via PixelLab | Propriété de l'utilisateur selon les conditions PixelLab (vérifiées) ; noter prompt et date si intégrés. |
