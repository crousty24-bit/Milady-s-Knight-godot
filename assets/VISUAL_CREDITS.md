# Visuels — provenance et licences

Les visuels hérités du prototype (`sprites/knight.png`, `slime_*.png`, `coin.png`, `world_tileset.png`, `platforms.png`, police `PixelOperator8.ttf`) restent sans provenance établie. Après RUN-012/013, seuls la police et `world_tileset.png` (atlas de collision du `TileSet`, recouvert par l'habillage) restent utilisés en jeu ; `knight.png` et `slime_green.png` servent encore à la comparaison d'échelle RUN-003 ; ce contrôle est différé à la recette des licences avant distribution (RUN-027–028).

## Générés pour le projet (RUN-012, 2 octobre 2026)

Pixel art produit par code, sans asset tiers ni génération par IA, à partir de l'artwork du projet (`artwork & logo/concept art 1.png` de la bibliothèque locale) : plaques acier, cape rouge, tabard sombre à emblème or. Le script est la source : relancer `python3 tools/art/knight.py` régénère les fichiers ci-dessous à l'identique (Python 3 seul, aucune dépendance).

| Fichier de jeu | Contenu |
| --- | --- |
| `sprites/ashen_knight.png` + `ashen_knight_frames.tres` | Ashen Knight, frames 32×32 (pieds en bas de la ligne 30, corps centré) : idle 4, run 6, rise 2, fall 2, wall 2, attack 3, hurt 1, dead 4. |
| `sprites/ashen_sword.png`, `ashen_sword_smear.png` | Épée en 32 angles et traînée ; supprimées en RUN-029 (épée dessinée dans les frames du chevalier). |
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

## Générés pour le projet (RUN-014, 2 octobre 2026)

| Fichier de jeu | Contenu |
| --- | --- |
| `sprites/vfx_coin_sparkle.png` | Éclat de collecte de pièce, 5 × 16×16 (`tools/art/vfx.py`). |
| `sprites/vfx_slime_splash.png` | Éclaboussure de mort, Green puis Purple, 5 × 32×20 (`tools/art/vfx.py`). |

## Générés pour le projet (RUN-029, 2 octobre 2026)

Seconde passe, même méthode : pixel art produit par code sur la palette commune, **sans asset tiers ni génération par IA**. Les générateurs sont la source et régénèrent tous les PNG à l'identique (contrôle MD5 de l'ensemble de `sprites/*.png`).

| Générateur | Fichiers de jeu | Contenu |
| --- | --- | --- |
| `tools/art/knight.py` (main agent) | `sprites/ashen_knight.png` + `ashen_knight_frames.tres`, `vfx_land_dust.png` ; `vfx_hit_spark.png`, `vfx_air_puff.png`, `vfx_wall_dust.png` régénérés | Ashen Knight sur squelette (IK jambes/bras, cape en ruban, contours sélectifs), frames 64×64, pieds en bas de la ligne 60 : idle en garde 6, run 8, rise 2, fall 2, land 2, wall 3, hurt 2, dead 6, trois mouvements d'attaque `atk1–3` de 10 frames, hauts du corps `up1–3` et bases `base_run/rise/fall` pour attaquer en mouvement. L'épée est dessinée dans chaque frame : `ashen_sword.png` et `ashen_sword_smear.png` sont supprimés. Poussière d'atterrissage 4 × 32×8. |
| `tools/art/world.py`, `world_terrain.py`, `world_bg.py`, `world_props.py`, `world_narrative.py` (subagent) | `terrain_stone.png`, `terrain_tufts.png`, `env_vines.png`, `bg_sky/clouds/far/arches/mist/mid.png`, `prop_*.png` (hors bac et porte) | Maçonnerie en appareil irrégulier, mousse/corruption, vrilles ; ciel, nuages, citadelle, viaduc, brume, ruines ; accessoires narratifs enrichis et nouveaux (piliers, lanternes, braseros, appliques, flammes, tombes, clôture, buissons, gravats, os, gibet, sanctuaire, corbeau, bannières, racines, cosses). |
| `tools/art/slime_art.py`, `coin_art.py`, `creatures.py`, `hazards.py`, `vfx.py` (subagent) | `enemy_slime_green/purple.png`, `item_gold_coin.png`, `trap_spikes.png`, `trap_thorns.png`, `prop_ferry.png`, `prop_gold_gate.png`, `vfx_coin_sparkle.png`, `vfx_slime_splash.png`, `vfx_slime_hit.png`, `vfx_gate_dust.png` | Slimes 14 frames (patrouille, recul, effondrement), pièce 12 frames, éclat de collecte, éclaboussure, gerbe d'impact, piques et ronces animées, bac à lanterne, porte avec appliques, éclat du sceau et poussière d'ouverture. |
| `tools/art/ui.py` (subagent, portrait retouché par le main agent) | `ui_icons.png`, `ui_panel.png`, `ui_panel_red.png`, `ui_plate.png`, `ui_keycap.png`, `ui_avatar_frame.png`, `ui_portrait_knight.png` | Icônes cœur/pièce, panneaux 9-slice or et rouge, plaque, touche, cadre et portrait du chevalier. |

`hud_icons.png` (RUN-013) reste généré à l'identique par `creatures.py` mais n'est plus utilisé par le HUD. Blueprint Studio était connecté : aucune génération n'a été lancée (0 crédit), les couches de fond procédurales suffisant à l'échelle 1× ; aucun fichier de cette source n'est donc à déclarer. Le pack CC0 *16x16 Assorted RPG Icons* (Shade) a été examiné pour le HUD mais ne contenait pas d'icône cœur, pièce ou touche adaptée : rien n'en a été copié.

## Générés pour le projet (RUN-015, 3 octobre 2026)

Même méthode : pixel art produit par code sur la palette commune, **sans asset tiers ni génération par IA**, régénéré à l'identique (MD5 vérifié).

| Générateur | Fichiers de jeu | Contenu |
| --- | --- | --- |
| `tools/art/menu_art.py` (main agent) | `ui_logo.png` 300×112, `ui_menu_ledge.png` 220×70, `ui_menu_focus.png` 12×12, `ui_menu_cursor.png` 7×9, `ui_menu_lock.png` 7×8 | Logo « Milady's / Knight » en textura dorée tracée par simulation de plume large, épée couronnée et bannière rouge déchirée ; rempart du premier plan ; plaque de focus 9-slice ; curseur ; cadenas d'option indisponible. |

Le logo reprend la **composition** de la référence de marque locale `artwork & logo/MK logo 1.png` (lettrage or sur bannière rouge, épée couronnée), sans en copier un pixel : la référence est une image haute résolution non native, d'origine non documentée, et porte la coquille « Milaay's ». L'artwork de fond du menu réutilise à l'exécution les couches acceptées de RUN-029 (`scripts/backdrop.gd`), le chevalier `ashen_knight_frames.tres` (idle) et `prop_brazier/flame/glow.png` ; aucun nouveau fond n'est produit.

## Générés pour le projet (RUN-016, 3 octobre 2026)

Même méthode : pixel art produit par code sur la palette commune, **sans asset tiers ni génération par IA** ; régénération identique vérifiée (MD5 de `sprites/*.png`).

| Générateur | Fichiers de jeu | Contenu |
| --- | --- | --- |
| `tools/art/knight.py` (main agent) | `ashen_knight.png` + `ashen_knight_frames.tres` (lignes ajoutées, 17 animations existantes identiques au pixel) | Longbow 0 sur le rig, épée au fourreau : `bow_idle` 6, `bow_run` 8, `bow_rise`/`bow_fall`/`bow_land` 2, `bow_wall` 3, `bow_hurt` 2 ; `shoot` 7 (relâche 4 + encoche/armement 3) et `up_shoot` (haut du corps sur `base_run/rise/fall`). Flèche encochée sur la ligne de la bouche (+4, −10). |
| `tools/art/items.py` (subagent, retouche de l'aura de soin par le main agent) | `proj_arrow.png`, `vfx_arrow_release.png`, `vfx_arrow_impact.png`, `vfx_arrow_hit.png`, `item_shard.png`, `vfx_shard_burst.png`, `ui_shard_icon.png`, `ui_slot_icons.png`, `item_chest.png`, `vfx_chest_vanish.png`, `item_potion_minor.png`, `vfx_heal.png` | Flèche, départ, impacts terrain/ennemi, shard et éclat violets, icônes HUD shard et slots, coffre tuto fermé→ouvert et dissolution, potion mineure verte et soin. Rampe verte locale `POTION` (soin, distincte du Slime vert). |

## Générés pour le projet (RUN-017, 3 octobre 2026)

Même méthode : pixel art produit par code sur la palette commune, **sans asset tiers ni génération par IA** ; régénération identique vérifiée (MD5). Silhouette encapuchonnée inspirée de la statue en robe du concept art du projet (`artwork & logo/concept art 1.png`), sans en reprendre un pixel.

| Générateur | Fichiers de jeu | Contenu |
| --- | --- | --- |
| `tools/art/spirit.py` (main agent) | `npc_spirit_idle.png`, `npc_spirit_talk.png` (8 × 32×48 chacun), `ui_portrait_spirit.png` 24×24, `vfx_spirit_aura.png` 48×56 | The Ancient Spirit : sage spectral encapuchonné à barbe, bâton de lumière, robe se dissolvant en traîne ; repos (flottement, particules) et dialogue (main ouverte vers l'interlocuteur, yeux et bâton plus vifs) ; portrait du bandeau ; halo froid tramé. Rampe pâle froide locale `SPIRIT`, yeux et cœur du bâton en jaune pâle (interaction neutre). |

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
