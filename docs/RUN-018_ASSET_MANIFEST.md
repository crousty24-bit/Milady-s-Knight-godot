# RUN-018 — Manifeste de la contribution Claude (assets, intégration visuelle, preuves)

**5 octobre 2026 — Contribution Claude remise à Codex pour recette et revue Jev.** Branche `feature/run-018-standard-equipment`, base `eb6fffc`. Contrat : [RUN-018_CLAUDE_HANDOFF.md](RUN-018_CLAUDE_HANDOFF.md). Contribution présente dans le commit `ff5caa0`, constaté par Codex au retour. Le dépôt est propre au début de la revue ; la run n’est pas DONE. Aucun push ou merge de cette contribution n’a été effectué par Codex. Validation humaine artistique/sonore et essai combat/coffres restent requis.

Orchestration : Opus 5.5 (principal) ; trois sous-agents Sonnet 5.5 sur fichiers disjoints — icônes/UI (`visual_architect`), objets du monde/VFX/couteau (`visual_architect`), sélection audio (`asset_integrator`). Le niveau de raisonnement des sous-agents n’est pas exposé par l’outil : il a été indiqué dans les consignes, sans preuve qu’il a été appliqué. Rig du chevalier, armes tenues, Throwing Knives, intégration Godot et vérifications : agent principal.

## Provenance et licences

- **Visuels : tous originaux, générés de façon procédurale** par les scripts `tools/art/run018/*.py` à partir de la palette commune (`tools/art/palette.py`) et du rig RUN-029 (`tools/art/knight.py`, importé en lecture seule, non modifié et non régénéré). Aucun pixel tiers ; aucune source externe à conserver dans `assets/source/run018/` (les générateurs sont la source).
- **Sons : Helton Yan, *Pixel Combat* — CC BY 4.0, crédit obligatoire** (« Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 »), même pack et même attribution que les sections existantes de `assets/AUDIO_CREDITS.md`. Bibliothèque locale lue seulement. *Minifantasy Dungeon SFX* écarté : ses conditions interdisent la redistribution (déjà consigné dans les crédits), dépôt public.
- **Crédits à intégrer par Codex** (fichiers de crédits non édités pendant le parallèle) : la section « Sons » ci-dessous peut être reprise telle quelle dans `assets/AUDIO_CREDITS.md` ; une ligne « RUN-018 : `assets/run018/**` généré par `tools/art/run018/` (original, projet) » dans `assets/VISUAL_CREDITS.md`.

Régénération : `python3 tools/art/run018/knight_armed.py`, `ui_icons.py`, `world_items.py` (option `--preview DIR`), `python3 tools/art/run018/prepare_audio_run018.py [NOMS]`. Aperçus/contrôles hors jeu : `python3 tools/art/run018/preview_armed.py DIR`.

## Chevalier armé — architecture

Les épées dessinées dans chaque frame ne pouvaient pas suivre RANGE × 24 px (19,2 à 60 px) ni tenir dans le gabarit 64×64 (Halberds jusqu’à ~96 px). Le rig validé est donc rendu sans arme en **trois couches de même mise en page**, et l’arme est dessinée au runtime entre elles, à la portée exacte :

| Couche | Fichiers | Contenu |
| --- | --- | --- |
| body | `assets/run018/knight/knight_body.png` + `knight_body_frames.tres` | tout le chevalier sans arme ni traînée |
| mid | `knight_mid.png` + `knight_mid_frames.tres` | parties peintes après la traînée (bras proche, spalière, main…) |
| over | `knight_over.png` + `knight_over_frames.tres` | parties peintes après l’arme (main proche, poussière…) et leurs contours |

Ordre à l’écran : body → traînée (`Sprite/Smear`) → mid → arme (`Sprite/Weapon`) → over, ce qui restitue l’ordre de peinture d’origine. Atlas 640×2304, **frames 64×64, pieds ligne 60, colonne 32, sprite à (0,−29) : gabarit et ancrage inchangés**. 36 animations, noms existants conservés (idle, run, rise, fall, land, wall, hurt, dead, atk1–3, up1–3, base_*, bow_*, shoot, up_shoot, resurrect, mêmes fps/boucles que RUN-029) + RUN-018 en fin d’atlas : `knife_idle` 6 f 6 fps boucle, `knife_run` 8 f 14 fps boucle, `knife_rise`/`knife_fall` 2 f 8 fps boucle, `knife_land` 2 f 20 fps, `knife_wall` 3 f 7 fps boucle, `knife_hurt` 2 f 10 fps, `throw`/`up_throw` 7 f échantillonnées manuellement (même contrat que `shoot` : 0–3 depuis le lancer, 4–6 armé pendant F maintenu).

`assets/run018/knight/knight_rig.gd` (généré) : par animation/frame `[type, main_x, main_y, angle, angle_hampe, traînée]` en coordonnées joueur (pieds = origine) ; type 0 aucun, 1 tenu, 2 tombé au sol, 3 rangé (Longbow/Knives actifs). Pendant la fenêtre de contact, l’angle est l’angle gameplay `lerp(−1,5 ; 1,2)` du rig d’origine.

Armes (`assets/run018/knight/weapon_strips.png`, 56×136, deux variantes d’éclairage par bande) rasterisées par `scripts/weapon_art.gd` (port exact de `tools/art/run018/weapon_raster.py`) : colonnes = distance depuis la main, tête ancrée à la pointe, milieu répété → **longueur main→pointe = `WeaponCatalog.stats(id).reach`, y compris fractionnaire, sans rééchelonner les pixels**. Contour 1 px, texture en cache par (arme, main, angle, portée). Au sol, rien n’est dessiné sous la ligne des pieds (comme les frames d’origine).

| Arme | Bande (l×h) | Garde/manche derrière la main | Portées dessinées N0→N5 | Traits |
| --- | --- | --- | --- | --- |
| Sword | 28×6 | 3,4 px | 24 → 36 | segments identiques à `draw_sword` (pommeau, fusée, garde 6 px, lame, pointe) |
| Longsword | 36×6 | 6,4 px | 28,8 → 40,8 | fusée longue à deux mains, gouttière |
| Brutal Axe | 23×12 | 3 px | 19,2 → 31,2 | manche bois, fer unique côté tranchant, talon |
| Dark Scythe | 43×18 | 7 px | 36 → 48 | hampe sombre, lame en croissant vers la main, pierre violette discrète |
| Warhammer | 23×10 | 3 px | 19,2 → 31,2 | manche cerclé, tête carrée, pointe sommitale |
| Halberds | 56×12 | 8 px | 48 → 60 | hampe bois, fer de hache, crochet, pique |

Hampes longues (Scythe, Halberds) hors fenêtre de contact : course, réception, glissade murale et première frame de mort portées vers le haut/arrière au lieu de traverser le sol (`angle_hampe`). Armes rangées pendant l’arc/les couteaux : fourreau d’origine (Sword) ou allongé (Longsword), hache/marteau suspendus à la hanche, Scythe/Halberds en travers du dos. Throwing Knives : couteau dessiné dans la main (posture et lancer dédiés), pas d’arme de mêlée tenue.

## UI et objets

| Fichier (`assets/run018/…`) | Taille / cellule | Frames / fps | Ancrage / usage |
| --- | --- | --- | --- |
| `ui/ui_weapon_icons.png` | 108×12, cellules 12×12 | 9 statiques | ordre Sword, Longsword, BrutalAxe, DarkScythe, Warhammer, Halberds, Longbow, ThrowingKnives, vide ; Sword/Longbow identiques pixel à pixel aux icônes validées |
| `ui/ui_weapon_icons_large.png` | 192×24, 24×24 | 8 | cartes de récompense, même ordre |
| `ui/ui_tier_badges.png` | 54×9, 9×9 | niveaux 0–5 | chiffre toujours affiché ; 0 gris, 1 vert, 2 bleu, 3 rouge ; 4/5 = plaque grise du 0 (aucun style inventé) |
| `ui/ui_reward_card.png`, `ui_reward_card_focus.png` | 24×24 | 9-slice marge 8 | carte normale / focalisée (bord or) |
| `ui/ui_chest_kind.png` | 24×12, 12×12 | 2 | glyphe common / rare |
| `world/item_chest_common.png` | 144×20, 24×20 | 6, 14 fps une fois | frame 0 fermé ; offset (−12,−20), origine au sol ; verrou violet (coût en shards) |
| `world/item_chest_rare.png` | 192×24, 32×24 | 6, 14 fps une fois | frame 0 fermé ; offset (−16,−24) ; couvercle bombé, coins acier, gemme bleue : silhouette distincte |
| `world/vfx_chest_vanish_rare.png` | 240×28, 40×28 | 6, 12 fps | dissolution du rare ; le common réutilise `sprites/vfx_chest_vanish.png` |
| `world/item_potion_major.png` | 72×16, 12×16 | 6, 6 fps boucle | offset (−6,−6), pied 10 px sous le centre comme la mineure |
| `world/vfx_heal_kill_minor.png`, `vfx_heal_kill_major.png` | 144×32, 24×32 | 6, 12 fps | aux pieds du joueur, ancre (0,5 ; 1) ; feedback instantané, aucun objet |
| `world/proj_knife.png` | 10×5 | 1 | pointe au point de vol : offset (−10,−2) à droite, (0,−2) à gauche |
| `world/vfx_knife_release.png` | 64×12, 16×12 | 4, 24 fps | ancre (0 ; 0,5), main −4 px |
| `world/vfx_knife_impact.png`, `vfx_knife_hit.png` | 80×16, 16×16 | 5, 20 fps | ancre centre ; décor / ennemi |

## Sons (`assets/sounds/run018/`, mono 44,1 kHz 16 bits, `tools/art/run018/prepare_audio_run018.py`)

| Fichier | Source Helton Yan *Pixel Combat* | Crête | Durée | Usage |
| --- | --- | --- | --- | --- |
| `sfx_chest_open_rare.wav` | `UIMisc_INTERFACE-Lock_HY_PC-004` + `DSGNTonl_USABLE-Magic Item_HY_PC-006` (+120 ms, −4 dB) | −8 | 0,90 s | ouverture rare (common : `sfx_chest_open_common` réutilisé) |
| `sfx_chest_reward_refuse.wav` | `DSGNTonl_USABLE-Failed Item_HY_PC-003` | −12 | 0,37 s | Escape dans la fenêtre payante |
| `sfx_weapon_upgrade.wav` | `DSGNTonl_USABLE-Mecha Upgrade Equip_HY_PC-004` | −8 | 0,69 s | upgrade +1 accepté (item : `sfx_chest_reward_accept` réutilisé) |
| `sfx_heal_kill.wav` | `MAGAngl_BUFF-Simple Heal_HY_PC-005` | −10 | 0,32 s | soin instantané au kill |
| `sfx_major_potion_pickup.wav` | `DSGNTonl_MOVEMENT-Bubble Babbler_HY_PC-005` | −8 | 0,80 s | potion majeure (P1) |
| `sfx_melee_swing_heavy_01–03.wav` + `.tres` | `WHSH_MOVEMENT-Wind Sweep Swish_HY_PC-001, -003, -005` | −8 | 0,60 s | Longsword, Dark Scythe, Warhammer, Halberds (P1, famille partagée) ; Sword/Brutal Axe gardent le swing léger (docs/08) |
| `sfx_weapon_knives_throw_01–03.wav` + `.tres` | `SWSH_MOVEMENT-Reso Swish_HY_PC-001, -002, -004` | −10 | 0,28 s | lancer de couteau (P1) |
| `sfx_knife_impact.wav` | `DSGNMisc_HIT-Zap Metal_HY_PC-002` | −10 | 0,22 s | impact couteau (P1) |

Navigation gauche/droite : `sfx_ui_navigate` réutilisé. Confirmer dans la fenêtre payante ne joue plus le clic générique : le coffre ouvert joue accept ou upgrade. Sélection par analyse objective uniquement (durée, enveloppe, centroïde) : **aucune écoute faite**. Substituts reconnus approximatifs (pas de vrai swing lourd, lancer ni impact métallique dans le pack) → remplacement possible en RUN-027. Notes : `work/run018/claude/audio/selection.md`.

## Fichiers de présentation modifiés (propriété remise par Codex)

- `scenes/player.tscn` : atlas body ; nœuds `Sprite/Smear`, `Sprite/Mid`, `Sprite/Weapon`, `Sprite/Over` (matériau du parent → flash et clignotement conservés).
- `scripts/player.gd` (présentation uniquement) : synchronisation des couches (`_sync_weapon_layers`, sur `frame_changed`/`animation_changed`, fin de physique et `_process`), noms d’animation de tir par ID (`_ranged_anim`), look du projectile capturé au tir, release/son couteau, swing léger/lourd selon l’arme, raccord `kill_healed` cherché parmi les ancêtres (aucune édition de `level.gd`). Physique, hitbox, cadences, dégâts, cooldowns : inchangés.
- `scripts/arrow.gd` : `look`/`set_look()` (texture, impacts, son) ; vol et collisions inchangés. Un couteau lancé garde son look après changement d’arme.
- `scripts/hud.gd` : `set_loadout` écrit les mêmes labels exacts puis transmet les IDs ; `scripts/equipment_slots.gd` : icône par arme, badge de niveau, plaques élargies ensemble selon le texte réel.
- `scripts/keyboard_menu.gd` : choix horizontaux dessinés en cartes (icône 24 px, label exact, badge, glyphe de coffre) ; options, sélection, `opened_frame`, signaux et menus verticaux inchangés ; Escape joue le refus payant.
- `scenes/reward_chest.tscn` + `scripts/reward_chest_art.gd`, `scripts/reward_chest_opened_fx.gd` (nouveaux) ; le `_draw` provisoire de `scripts/reward_chest.gd` est retiré (présentation seule, état/transactions intacts).
- `scenes/major_potion.tscn` → `scripts/major_potion_art.gd` (nouveau). `scripts/major_potion_preview.gd` n’est plus référencé ; suppression laissée à Codex.
- Nouveaux : `scripts/weapon_art.gd`, `tests/run018_equipment_visual.gd`, `tools/art/run018/`, `assets/run018/`, `assets/sounds/run018/`.

## Vérifications réellement exécutées (Godot 4.7.2 Windows, `flock work/.godot.lock`, profils temporaires isolés)

- Import éditeur sans erreur.
- `tools/test.sh` complet, code 0 : **27 suites, 1723 contrôles de jeu + 19 contrôles en sessions à froid (5 processus) + 1 isolation = 1743 PASS, 0 échec**, aucune ligne FAIL/SCRIPT ERROR/ERROR/fuite. Logs `work/test-results/run-13N1WAsl/`, sortie `work/run018/claude/logs/full-suite-1.log`.
- Pilotes rendus existants rejoués : knight_visual 31/31, combat_visual 2/2, hud_visual 11/11, feedback_visual 7/7, reward_transactions 29/29 (logs `work/run018/claude/logs/rendered-*.log`).
- Nouveau pilote rendu `tests/run018_equipment_visual.gd` : **68/68** (`work/run018/claude/logs/visual-3.log`), captures 640×360 dans `work/run018/claude/render/` inspectées : six armes de mêlée N0/N3/N5, couches synchronisées, portée dessinée = portée gameplay ±2,5 px (contour compris), miroir à gauche, attaque aérienne sur le haut du corps superposé, arme rangée avec l’arc ; couteaux posture/lancer/vol et look conservé après échange ; HUD « Throwing Knives 3 » + badge dans la plaque, slot vide ; coffres fermés common/rare, cartes horizontales, focus droite, upgrade accepté (Sword 1), rare à une carte refusé ; potion majeure (+1 HP) ; soins au kill mineur/majeur.
- Hors jeu : composition Python Sword0 vs atlas RUN-029 validé — visuellement équivalente (aperçu `work/run018/claude/knight/sword0_vs_orig_x4.png`), mais pas identique au pixel : 7109 pixels différents sur 61 886 (anti-crénelage de la lame et contour de lame en `OUTLINE` au lieu de `STEEL_DEEP` sur le corps).

## Limites et suites

- **Validation humaine requise** : rendu et lisibilité des armes en mouvement, sensation des gestes (les trois mouvements d’épée sont partagés par toutes les armes de mêlée ; aucune animation dédiée par arme), échelle Halberds/Scythe, icônes 12 px (Warhammer proche de Brutal Axe, Knives chargée), coffres, cartes, soins, et **écoute de tous les sons**.
- Non exécuté : playtest interactif, captures de chaque arme pour chaque animation (échantillon représentatif seulement), niveaux 4/5 en jeu au-delà du contrôle de portée N5, rendu Linux.
- Lame de traînée : couleur neutre identique pour toutes les armes ; Scythe/Halberds peuvent visuellement mordre dans le sol en fin de geste (coupé à la ligne des pieds), sans effet gameplay.
- L’écran titre garde l’atlas `ashen_knight_frames.tres` d’origine (épée dessinée), volontairement.
- Pas de Legendary/Fire Gauntlet, N2–4, buff ni ennemi ; aucun placement de niveau modifié.

## Retour à Codex

Fichiers de présentation listés ci-dessus rendus à Codex. À faire côté Codex : recette après intégration (cadence/portée/collision), crédits audio/visuels, suppression éventuelle de `major_potion_preview.gd`, ajout éventuel du pilote `run018_equipment_visual` aux pilotes rendus, journal/learning, puis revue Jev. Le texte de retour initial annonçait aucun commit ; Git prouve désormais la livraison locale `ff5caa0`. Aucun push, PR ou merge effectué par Codex dans cette reprise.


## Revue de retour Codex — 5 octobre 2026

Baseline propre `ff5caa0` inspectée ; aucun défaut concret du gameplay/transactions trouvé par la revue indépendante. Dimensions des20 PNG et paramètres des12 WAV concordants (mono44,1kHz PCM16bits, durées et crêtes à±0,05dB des cibles). Crédits intégrés dans AUDIO_CREDITS/VISUAL_CREDITS. Marqueur non référencé major_potion_preview.gd et son UID retirés après recherche des références code/scènes/ressources.

Recette Codex réellement relancée : tools/test.sh, Godot Windows4.7.2, profil NTFS isolé et verrou flock, code0 ; **1743 PASS** (1723 jeu,19 froids,1 isolation), aucun FAIL/SCRIPT ERROR/ERROR/fuite. Logs `work/test-results/run-WgV2sBn8/`, sortie `work/run018/codex-return/full-suite.log`. Pilote run018_equipment_visual non headless relancé sous profil NTFS isolé/verrou flock : **68/68**, code0 sans erreur/fuite (`work/run018/codex-return/render.log`). Captures représentatives inspectées à640×360 (Halberds3, Scythe aérienne, couteau en vol après échange, HUD longs, focus upgrade, soin majeur). Aucun playtest humain ni écoute sonore effectués par Codex.

RUN-018 **DONE** localement le 5 octobre 2026 : validation humaine reçue (« J’ai fait vérifications et je valide la run. »), revue Jev READY_FOR_DONE et inspection directe des preuves satisfaisantes. Le retour initial ci-dessus reste historique. Aucun push/PR/merge ni RUN-019 lancée.
