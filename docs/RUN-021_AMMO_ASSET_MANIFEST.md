# RUN-021 — Manifeste Claude : props et munitions (phase 1)

**7 octobre 2026.** Exécution de la phase 1 du [contrat Claude props/munitions](RUN-021_CLAUDE_HANDOFF_03.md) selon le [contrat produit validé](RUN-021_AMMO_SPIKES_PROPOSAL.md) (amendement humain : stocks courants transmis au niveau suivant ; mort/restart/reprise restaurent le snapshot d’entrée, sans effet sur les visuels). Claude Code **Opus 5.5** (`claude-opus-5-5`), main agent seul. Aucun sous-agent lancé : le travail visuel était séquentiel, sans tâche séparable justifiant la coordination. Branche `feature/run-020-021-campaign`.

Périmètre de la phase 1 : assets, icônes et proposition de présentation. **Aucune** scène/script partagé, scène de niveau, HUD, test, workflow, audio ni art des piques n’est modifié. Godot n’a pas été lancé et aucune commande Git modifiant l’état n’a été exécutée. RUN-021 reste ACTIVE ; aucune validation artistique n’est présumée.

> **Amendement du 7 octobre 2026 (retour humain) :** les props ne montrent plus de munitions. Il n’existe plus qu’**une caisse** et **un tonneau** neutres, fermés, sans contenu dépassant ni étiquette de famille : `prop_crate.png`, `prop_barrel.png` et leurs casses `prop_crate_break.png`, `prop_barrel_break.png` (mêmes dimensions, pivot et 6 frames à 12 fps). Animations SpriteFrames uniques `intact` / `break`, lues par `scripts/ammo_prop.gd` quelle que soit `ammo_family`. La famille reste une propriété gameplay inchangée (loot), révélée seulement par le pickup. Les huit planches `prop_{crate,barrel}_{arrows,knives}[_break].png` sont retirées (dérivés du générateur, sans autre référence). Les §2–4 ci-dessous décrivent la version d’origine pour ces props ; pickups, VFX et icônes HUD sont inchangés.

## 1. Source, méthode, provenance

- **Générateur (source conservée) :** `tools/art/run021/ammo/ammo_art.py` ; aperçus seulement : `tools/art/run021/ammo/ammo_preview.py`. Commande : `python3 tools/art/run021/ammo/ammo_art.py [--preview DIR]`.
- **Méthode :** pixel art original dessiné par code avec `tools/art/pixel.py` et `tools/art/palette.py`, importés en lecture seule. C’est le pipeline de tous les sprites du projet. Rampes WOOD/STEEL/BLOOD/STONE/GOLD, rampe locale `TAG` (parchemin pâle, interaction neutre) et `PALE`. Aucun pixel tiers, aucun appel à un outil de génération d’images, aucun crédit Blueprint Studio consommé. Sortie déterministe : deux générations successives donnent des MD5 identiques.
- **Références visuelles (lecture seule, aucun pixel copié) :** `assets/sprites/proj_arrow.png`, avec ses empennes rouges `BLOOD[3]/[2]`, sa hampe bois et sa pointe acier, et `assets/run018/world/proj_knife.png`, avec sa poignée bois, sa garde et sa lame acier à arête claire. Leurs motifs sont redessinés à la main dans le générateur. Le style des icônes à 45° et les variantes vides gris foncé suivent `ui_weapon_icons.png` et `ui_icons.png`.
- **Bibliothèque externe** (`.local/asset-paths.md`, listée en lecture seule) : aucun prop latéral caisse/tonneau adapté. Seul *16x16 Assorted RPG Icons* (Shade, CC0, vérifié dans `assets/VISUAL_CREDITS.md`) est utilisable, mais il s’agit d’icônes RPG frontales sans prop destructible. Raven Fantasy Icons et les packs DantePixels sont marqués non redistribuables. Les flèches de Tiny RPG (Zerie) sont non redistribuables et hors échelle. **Rien n’a été copié.**
- **Audio :** aucun fichier modifié ni ajouté. Proposition seulement (§6).

## 2. Fichiers livrés — `assets/run021/ammo/`

Planches horizontales, frames de gauche à droite et de taille constante, RGBA. Claude n’a pas lancé Godot. Les `*.png.import` présents ont été créés à 14:58 par un import Godot concurrent côté Codex, pas par Claude. Ils portent les réglages par défaut attendus (`compress/mode=0`, `mipmaps/generate=false`, filtre Nearest global `default_texture_filter=0`), et les PNG n’ont pas changé depuis (hashes ci-dessous identiques).

**SpriteFrames prêtes à raccorder** (générées par le même script, chemins sans uid ; **non chargées dans Godot par Claude**) :

| Fichier | Animations |
| --- | --- |
| `ammo_crate_frames.tres`, `ammo_barrel_frames.tres` | `intact_arrows`, `intact_knives` (1 frame) ; `break_arrows`, `break_knives` (6 frames, 12 fps, `loop = false`) |
| `ammo_pickup_frames.tres` | `arrows`, `knives` (4 frames, 6 fps, boucle) ; `collect` (5 frames, 15 fps, une fois) |

Les noms suivent `scripts/ammo_prop.gd` (Codex, lu en lecture seule) : `Art` AnimatedSprite2D, `_family_animation()` en `_arrows`/`_knives`, et `queue_free` sur `animation_finished`, d’où la casse sans boucle. Conséquence : la frame 5 (résidu) n’est visible que 1/12 s, puis le node est libéré. C’est acceptable ; un résidu persistant demanderait une décision Codex.

| Fichier | Taille | Frames | Pivot | Lecture | SHA-256 (préfixe) |
| --- | --- | --- | --- | --- | --- |
| `prop_crate_arrows.png` | 32×32 | 1 | bas-centre (16, 32) | intact | `dd1e5a10` |
| `prop_crate_knives.png` | 32×32 | 1 | bas-centre (16, 32) | intact | `15a51d48` |
| `prop_barrel_arrows.png` | 32×32 | 1 | bas-centre (16, 32) | intact | `d111e94a` |
| `prop_barrel_knives.png` | 32×32 | 1 | bas-centre (16, 32) | intact | `fade014c` |
| `prop_crate_arrows_break.png` | 192×32 | 6 × 32×32 | bas-centre (16, 32) | 12 fps, une fois | `01146258` |
| `prop_crate_knives_break.png` | 192×32 | 6 × 32×32 | bas-centre (16, 32) | 12 fps, une fois | `f56e292c` |
| `prop_barrel_arrows_break.png` | 192×32 | 6 × 32×32 | bas-centre (16, 32) | 12 fps, une fois | `2971a17e` |
| `prop_barrel_knives_break.png` | 192×32 | 6 × 32×32 | bas-centre (16, 32) | 12 fps, une fois | `7ab440e2` |
| `pickup_arrows.png` | 64×16 | 4 × 16×16 | centre (8, 8) | 6 fps en boucle (reflet) | `e62dcee2` |
| `pickup_knives.png` | 64×16 | 4 × 16×16 | centre (8, 8) | 6 fps en boucle (reflet) | `24cecbda` |
| `vfx_ammo_pickup.png` | 80×16 | 5 × 16×16 | centre (8, 8) | 15 fps, une fois (facultatif) | `b902646c` |
| `ui_ammo_icons.png` | 48×12 | 4 × 12×12 | HUD, coin haut-gauche | 0 flèches, 1 couteaux, 2 flèches vides, 3 couteaux vides | `d5909419` |

Les hashes complets figurent dans `work/run021/ammo/claude-assets-result.md`.

**Ancrage Godot :** le pivot bas-centre s’obtient avec `centered = true` et `offset = Vector2(0, -16)`, l’origine du node étant posée sur la surface du sol. Pour un pickup, utiliser `centered = true` sans offset et placer l’origine 8 px au-dessus du sol : le contenu repose sur la rangée 15, ombre de contact comprise.

## 3. Marqueur de famille

Chaque prop existe en **variante cuite par famille** : aucun compositing à l’exécution. Codex choisit la texture selon la famille exportée de l’instance.

- **Flèches :** quatre hampes dépassent du haut avec des empennes **rouges** (même code couleur que `proj_arrow.png`). Une étiquette pâle sur la face porte un glyphe de flèche à empenne rouge.
- **Couteaux :** des poignées bois avec garde acier et des lames claires à pointe blanche dépassent du haut (comme `proj_knife.png`). L’étiquette pâle porte un glyphe de couteau.
- L’étiquette pâle suit la couleur fonctionnelle « interaction neutre ». Or, violet, vert et cyan restent réservés.
- La différenciation avec le décor tient au gabarit plus large (22 px contre 12 px), au contour sombre, aux cercles acier éclairés, au contenu visible et à l’étiquette. Les tonneaux décoratifs de Blight Town (`blight_town_barrels.png`) restent nettement distincts (voir le mock `mock_world_x3.png`).

## 4. Dimensions utiles (indicatives pour Codex, non imposées)

Coordonnées relatives au pivot bas-centre (x vers la droite, y vers le bas), contour compris :

| Prop | Corps | Contenu dépassant | Emprise totale |
| --- | --- | --- | --- |
| Caisse | x −11…+10, y −19…−1 (22×19) | jusqu’à y −29 (flèches) / −28 (couteaux) | 22×29 max |
| Tonneau | x −11…+10, y −20…−1 (22×20) | jusqu’à y −30 (flèches) / −29 (couteaux) | 22×30 max |

Les props sont non bloquants (contrat). Une zone de réception des coups qui couvre le corps, sans les hampes, convient naturellement. Le choix reste à Codex.

**Casse :** la frame 0 est un flash pâle à 40 % avec fissures, sur laquelle le contenu reste visible. Les frames 1–4 montrent l’éclatement : morceaux du corps en appareil décalé, échardes, poussière au sol et bouffée à l’emplacement du contenu. La frame 5 est un résidu bas de 5 px (rangées 27–31), non interactif ; Codex peut le garder ou libérer le node. Volontairement, **aucune munition n’est projetée** pendant la casse, car un prop peut ne rien lâcher (20 %). Seul le pickup réel de Codex matérialise le loot. Les débris sortent du cadre de 32 px dès la frame 2 : c’est voulu, car ils sont rognés au bord de la cellule.

**Pickups :** flèches en faisceau de trois, empennes rouges liées par une corde pâle ; couteaux en X. Les frames 1 et 2 portent un reflet blanc ; les frames 0 et 3 sont sans reflet, et la frame 0 sert de sprite statique. La quantité n’est pas dessinée : elle est indépendante du sprite (contrat).

## 5. Proposition HUD (non intégrée)

`scripts/hud.gd` appartient à Codex. `scenes/hud.tscn` n’est édité qu’après remise exclusive explicite. Proposition détaillée dans `work/run021/ammo/visual-interface.md` :

- dans `Equipment`, à droite de `RangedPlate` : `AmmoPlate` (NinePatchRect `ui_plate.png`, marges 4) en local (94, 17)–(146, 32) ; `AmmoIcon` en (97, 19)–(109, 31) sur `ui_ammo_icons.png` ; label `AmmoCount` « courant/plafond » en (111, 20)–(144, 30) avec le thème HUD existant. Noms alignés sur `scripts/hud.gd` (Codex), qui attend aussi un label `AmmoFeedback` pour « +N ARROWS » et « NO KNIVES » ; position proposée : local (0, 34)–(146, 44), sous les plaques. `hud.gd` produit des comptes à deux chiffres (`%02d/%d`, « 07/15 »), qui tiennent dans 33 px. Aucun autre node n’est déplacé, et les panneaux HP/pièces et shards sont intacts dans le viewport 640×360 ;
- états : normal ; **vide** avec icône grise 2/3 et label `#d8423a` (BLOOD[3]) ; **plein** avec label `#f0d27a` (GOLD[3]) ; **ramassage** avec `+N` pâle au-dessus du joueur pendant ~0,6 s et `vfx_ammo_pickup.png` (N = quantité réellement prise) ; au plafond, le pickup reste au sol, avec en option un texte `FULL` court.

Mock : `work/run021/ammo/preview/mock_hud_x4.png`. Les chiffres du mock utilisent une police 3×5 de substitution, pas PixelOperator8 : seuls la disposition et les couleurs y sont représentatives.

## 6. Audio proposé (non raccordé)

Aucun nouveau système et aucun remplacement. Si Codex veut un retour sonore, réutiliser des fichiers existants déjà crédités (Helton Yan, CC BY 4.0, `assets/AUDIO_CREDITS.md`) : casse → `assets/sounds/sfx_arrow_impact.wav` (« Hard Step », choc sourd) ; ramassage → `assets/sounds/sfx_chest_reward_accept.wav` (« Tonal Item »). Ces choix sont faits sur dossier, sans écoute : l’écoute humaine reste à faire.

## 7. Vérifications effectuées et limites

**Effectué :**

- dimensions et nombre de frames vérifiés par assertion du générateur ;
- boîtes englobantes relevées par frame ;
- MD5 identiques sur deux générations successives ;
- inspection visuelle des aperçus natifs ×1 et agrandis : `work/run021/ammo/preview/contact_sheet_x4.png`, `mock_world_x1.png`/`_x3.png`, avec chevalier idle, tuile de pierre, tonneaux décoratifs N2 et pièce, puis `mock_hud_x1.png`/`_x4.png`, `ui_icons_x10.png`, `check_x5.png` et `refs_x6.png`.

**Non effectué (hors phase 1 ou non autorisé) :**

- import Godot ;
- lecture des animations en jeu ;
- alignement des collisions ;
- rendu en niveau réel ;
- placements N1–4 ;
- intégration HUD ;
- playtest.

Le mock monde est un collage sur un mur de fond simplifié, pas une capture de niveau. La lisibilité sur les fonds N2–4 réels reste à vérifier au rendu. Le sous-agent `asset_integrator` n’a pas été utilisé.

**Validation humaine requise :**

- adéquation artistique ;
- lisibilité des familles en mouvement ;
- échelle perçue (corps ~19–20 px, soit environ la hanche du chevalier) ;
- ressenti de la casse ;
- présentation du compteur.

## 8. Intégration en attente (phase 2, après remise Codex)

1. Codex remet les noms de nodes, chemins et signaux réels des scènes caisse/tonneau/pickup.
2. Claude raccorde uniquement leur présentation (textures, SpriteFrames, offsets) dans un créneau exclusif.
3. Après remise, Claude réalise les placements additifs N1–4 selon les budgets du contrat (N1 2 flèches ; N2 4/2 ; N3 4/4 ; N4 5/5), après relevé de la baseline humaine juste avant édition. Les coordonnées, familles et types seront ajoutés à ce manifeste.
4. Le HUD n’est intégré qu’après remise exclusive de `scenes/hud.tscn`.
5. Captures natives des props, de la casse, des pickups et du HUD en jeu.

Pour les piques, aucun asset n’est modifié tant que Codex ne fournit pas de preuve de rendu montrant une marche visuelle trompeuse.
