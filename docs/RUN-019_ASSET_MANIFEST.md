# RUN-019 — Manifeste de la contribution Claude (art, SFX, intégration de présentation)

**5 octobre 2026 — Contribution Claude remise à Codex pour recette, revue Jev et validation humaine.** Branche `feature/run-019-threats-exploration`, base `2a2f2e6` (checkpoint technique Codex). Contrat : [RUN-019_CLAUDE_HANDOFF.md](RUN-019_CLAUDE_HANDOFF.md). La run n'est pas DONE. Aucun push, PR ou merge. RUN-020/021 non commencées.

Orchestration : Opus 5.5 (principal : contrat de frames, intégration Godot, captures, revue visuelle et recette) ; quatre sous-agents Sonnet 5.5 sur fichiers disjoints : undead (`visual_architect`, High), blobs et Skull (`visual_architect`, High), pièges, mécanismes et pickups (`visual_architect`, Medium), sélection audio (`asset_integrator`, Medium). Le niveau de raisonnement des sous-agents a été indiqué dans les consignes ; l'outil n'expose pas de preuve qu'il a été appliqué.

**Statut des assets.** L'humain précise que des assets externes seront fournis plus tard, pendant les runs 0.3.0, puis adaptés au projet. Les visuels et sons ci-dessous sont donc la présentation complète et fonctionnelle de RUN-019, mais pas forcément définitive. L'intégration est pilotée par des tables (feuille, cellule, frames, fps, ancrage) regroupées en tête de chaque bloc « Presentation » des scripts. Remplacer une feuille par un dérivé externe normalisé demande seulement de changer le PNG et sa ligne de table, sans toucher au gameplay.

## Provenance et licences

- **Visuels : tous originaux, générés de façon procédurale** par `tools/art/run019/enemies_undead.py`, `enemies_blobs.py` et `world_run019.py`, sur la palette commune `tools/art/palette.py` et avec `tools/art/pixel.py`. Ces deux fichiers sont importés en lecture seule, non modifiés. Aucun pixel tiers, aucune génération par IA d'image.
  - `enemies_blobs.py` reprend la méthode de `slime_art.py` et de `vfx.py` en lecture seule, sans régénérer leurs sorties.
  - `world_run019.py` lit `assets/sprites/terrain_stone.png` (lecture seule) pour que le mur secret corresponde exactement à la maçonnerie : si cet atlas change, relancer le générateur.
  - Les générateurs sont la source ; `assets/source/run019/` n'est donc pas créé.
- **Sons : Helton Yan, *Pixel Combat* — CC BY 4.0, crédit obligatoire** (« Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 »). Même pack et même attribution qu'aux sections existantes. La bibliothèque locale est lue seulement. *Minifantasy Dungeon SFX* est écarté : sa licence interdit la redistribution.
- **Crédits intégrés par Codex lors de la recette** :
  - une ligne dans `assets/VISUAL_CREDITS.md` : « RUN-019 : `assets/run019/**` généré par `tools/art/run019/` (original, projet) » ;
  - la section Sons ci-dessous dans `assets/AUDIO_CREDITS.md`.

**Régénération** (Python 3 seul, déterministe, MD5 identiques vérifiés) :

```
python3 tools/art/run019/enemies_undead.py [--preview DIR]
python3 tools/art/run019/enemies_blobs.py [--preview DIR]
python3 tools/art/run019/world_run019.py [--preview DIR]
python3 tools/art/run019/prepare_audio_run019.py [LIBRARY_ROOT] [NOMS]
```

## Conventions

- Les feuilles sont des bandes horizontales à cellule fixe ; `mech_door.png` a deux lignes.
- Les ennemis regardent à gauche ; Godot applique `flip_h` quand `direction > 0`.
- Ancrage : pieds sur la dernière ligne de la cellule, colonne `cell_w/2`. Le sprite est placé avec `offset = −ancre` (`centered = false`). Skull : origine au centre.
- Imports Godot 4.7.2 par défaut du projet, comme RUN-018 : sans perte, sans mipmaps, filtre nearest global.
- Le contrat de frames détaillé (contenu attendu de chaque animation) reste dans `work/run019/claude/SPEC.md`, local et non suivi. Les tables ci-dessous en sont l'extrait normatif.

## Ennemis (`assets/run019/enemies/`)

Format des animations : `nom début+nombre@fps`, B = boucle.

| Feuille | Cellule | Animations | Ancre |
| --- | --- | --- | --- |
| `skeleton_warrior.png` 1296×32 | 48×32 | idle 0+4@6 B ; walk 4+6@10 B ; windup 10+3@10 ; attack 13+4@16 ; hit 17+2@16 B ; death 19+8@12 | (24,32) |
| `skeleton_archer.png` 1040×32 | 40×32 | idle 0+4@6 B ; walk 4+6@10 B ; windup 10+3@10 ; shoot 13+3@12 ; hit 16+2@16 B ; death 18+8@12 | (20,32) |
| `blight_sorcerer.png` 1360×36 | 40×36 | idle 0+4@6 B ; walk 4+6@10 B ; cast 10+4@13 ; cast_release 14+3@12 ; swing_windup 17+3@10 ; swing 20+4@16 ; hit 24+2@16 B ; death 26+8@12 | (20,36) |
| `bloated_slime.png` 800×32 | 40×32 | crawl 0+8@8 B ; swell 8+4@14 ; hit 12+2@16 B ; death 14+6@12 | (20,32) |
| `chud_blob.png` 1248×36 | 48×36 | idle 0+4@5 B ; walk 4+6@8 B ; windup 10+3@10 ; slam 13+4@16 ; hit 17+2@16 B ; death 19+7@10 | (24,36) |
| `possessed_skull.png` 460×20 | 20×20 | fly 0+4@10 B ; spawn 4+5@14 ; despawn 9+5@14 ; death 14+6@14 ; bite 20+3@14 | (10,10) centre |
| `enemy_slime_red.png` 336×24 | 24×24 | red 0+8@10 B ; red_hit 8+2@16 B ; red_death 10+4@20 | même mise en page et nœud que Green/Purple |

| Projectile / VFX | Cellule × frames, fps | Ancre / usage |
| --- | --- | --- |
| `proj_bone_arrow.png` | 14×5 × 1 | pointe (13,2) au point de vol, tournée selon `motion` |
| `vfx_bone_arrow_release.png` | 16×12 × 4, 24 | bord gauche (0 ; 0,5) au point de départ réel de la flèche |
| `vfx_bone_arrow_impact.png` | 16×16 × 5, 20 | centre, au point `impacted` |
| `vfx_blight_warning.png` | 56×40 × 8, piloté | point au sol (28,36) ; frame = `elapsed / warning_duration × 8`. La rune de 48 px et le dôme de rayon 24 représentent la zone de contact réelle, figée au sol. |
| `vfx_blight_explosion.png` | 64×56 × 7, 16 | point au sol (32,52), au point `impacted` |
| `vfx_blight_cast.png` | 16×16 × 5, 14 | sur la pierre du bâton au début d'incantation |
| `vfx_slime_splash_red.png` | 40×24 × 6 | même usage que la ligne verte de `vfx_slime_splash.png` |
| `vfx_slime_hit_red.png` | 16×16 × 4 | même usage que la ligne verte de `vfx_slime_hit.png` |
| `vfx_bloated_burst.png` | 64×32 × 6, 14 | bas-centre au sol, à la mort du Bloated |

**Échelle.** Les squelettes mesurent environ 26 px, comme le chevalier ; le Sorcerer est plus haut avec son bâton. Bloated et Chud font environ 30–34 px de large × 26–30 px de haut, nettement plus imposants que le chevalier tout en restant centrés sur leur collision de 20×22.

**Décision physique après audit Codex.** Collisions 20×22 conservées. L'Art Bible définit une taille visuelle, sans imposer une collision proportionnelle. Les contours alpha mesurés (appendices compris) atteignent 34×30 pour Bloated crawl, 34×29 pour Chud idle et 36×29 pour Chud walk ; le débord latéral peut donc atteindre 7–8 px. Aucun défaut physique démontré dans la recette. La validation humaine de la passe en l'état ne justifie pas de changer déplacements, contacts ou accès aux plateformes.

## Pièges, mécanismes, pickups (`assets/run019/world/`)

| Feuille | Cellule | Frames → animations | Ancre |
| --- | --- | --- | --- |
| `trap_spikes_retract.png` | 32×16 | retracted 0 ; warning 1+4@12 B ; extend 5+3@30 ; extended 8+2@6 B ; retract 10+3@24 | (16,16) |
| `trap_trapdoor.png` | 32×20 | closed 0 ; warning 1+4@16 B ; open 5+4@20 ; opened 9 | (16,4) |
| `trap_turret.png` | 24×24 | idle 0+2@2 B ; warning 2+4@12 B ; fire 6+4@20 | centre ; canon vers la droite, tourné selon `direction`, `flip_v` vers la gauche |
| `proj_turret_bolt.png` | 12×6 × 3@12 B | — | pointe (11,3) |
| `vfx_turret_muzzle.png` / `vfx_turret_impact.png` | 12×12 × 4 / 16×16 × 5 | — | bouche / point d'impact |
| `trap_poison_plant.png` | 28×28 | idle 0+6@6 B ; snap 6+3@16 | (14,28) |
| `vfx_poison_spores.png` | 20×16 × 5@14 | — | sur le joueur touché |
| `item_magic_shield.png` / `vfx_shield_pickup.png` | 16×16 × 6@8 B / 32×32 × 6@16 | — | centre |
| `vfx_shield_aura.png` / `vfx_shield_end.png` | 36×40 × 6@10 B / × 5@14 | — | pieds du joueur (18,34) |
| `item_hp_bonus.png` / `vfx_hp_bonus_pickup.png` | 16×16 × 6@8 B / 32×32 × 7@14 | — | centre |
| `mech_pressure_plate.png` | 24×8 | inactive 0 ; press 1+3@20 ; active 4 | (12,8) |
| `mech_button.png` | 16×20 | inactive 0+2@3 B ; press 2+3@20 ; active 5 | (8,20) |
| `mech_door.png` 264×112 | 24×56, 2 lignes | closed 0 ; unlock 1+3@16 ; rise 4+6@16 ; opened 10 | (12,56). Ligne 0 : porte à coins (cadenas or). Ligne 1 : porte à mécanisme (rouage acier pâle), choisie par `coin_locked`. |
| `env_secret_wall.png` | 16×32 × 2 | frame 0 utilisée ; frame 1 (fissure) disponible, non branchée | (8,32) |
| `vfx_secret_crumble.png` / `vfx_door_dust.png` / `vfx_mech_activate.png` | 32×40 × 7 / 32×12 × 5 / 24×16 × 5 | — | au sol |

## Sons (`assets/sounds/run019/`, mono 44,1 kHz 16 bits)

Mesures relues par Claude sur les 37 WAV. Les `.tres` sont des `AudioStreamRandomizer` calqués sur `sfx_slime_death.tres`. « + » désigne une couche (seconde source +0,12 s, −4 dB).

| Fichier | Source Helton Yan *Pixel Combat* | Crête dBFS | Durée | Branchement |
| --- | --- | --- | --- | --- |
| `sfx_skeleton_warrior_attack_01/02` + `.tres` | DSGNMisc_HIT-Hit Rattle 002/004 | −10 | 0,40 | relâche mêlée Warrior (P0) |
| `sfx_skeleton_warrior_death` | Hit Rattle 001 + EXPLOSION-Crunching 005 | −8 | 0,90 | mort Warrior (P0) |
| `sfx_skeleton_archer_shot_01/02` + `.tres` | SWSH_MOVEMENT-Bamboo Whip 001/003 | −10 | 0,21/0,23 | tir Archer (P0) |
| `sfx_skeleton_archer_death` | Hit Rattle 006 + EXPLOSION-Cruncher 005 | −8 | 0,90 | mort Archer (P0) |
| `sfx_sorcerer_spell_cast` | DSGNTonl_SKILL RELEASE-Mind Eraser 005 | −8 | 0,60 | début d'incantation (P0) |
| `sfx_sorcerer_ground_warning` | MAGSpel_CAST-Energy Riser 005 | −8 | 0,91 | avertissement 1 s, attaché à la zone (P0) |
| `sfx_sorcerer_ground_explosion` | EXPLOSION-Bass Hit 003 + Magisplosion 005 | −8 | 1,10 | explosion (P0) |
| `sfx_sorcerer_melee_attack` | DSGNTonl_MOVEMENT-Arcane Slap 001 | −8 | 0,50 | coup de bâton (P0 docs/08) |
| `sfx_sorcerer_death` | DSGNMisc_SKILL IMPACT-Dramatic Finish 005 | −8 | 1,10 | mort Sorcerer (P0) |
| `sfx_skull_spawn` | MAGSpel_CAST-Sharp Summon 005 | −10 | 0,80 | `swarm_started`, une fois par swarm (P0) |
| `sfx_skull_death_01/02/03` + `.tres` | DSGNMisc_SKILL IMPACT-Glassy Sprites 001/002/003 | −10 | 0,40 | mort Skull (P0) |
| `sfx_skull_attack` | Hit Rattle 003 | −10 | 0,12 | contact Skull qui blesse (P1) |
| `sfx_skull_despawn` | DSGNMisc_SKILL IMPACT-Energy Dissipate 005 | −10 | 0,60 | sortie de zone, hors chemin de récompense (P1) |
| `sfx_bloated_slime_attack` | DSGNMisc_CAST-Slime Ball 003 | −8 | 0,60 | contact Bloated qui blesse (P0) |
| `sfx_bloated_slime_death` | EXPLOSION-Thud 004 + Wet Splash 005 | −8 | 1,10 | mort Bloated (P0) |
| `sfx_chud_attack_01/02` + `.tres` | FGHTImpt_MELEE-Gut Kick 003/001 | −10 | 0,37 | relâche du slam Chud (P0) |
| `sfx_chud_death` | DSGNMisc_HIT-Mecha Gore Cruncher 005 | −8 | 0,99 | mort Chud (P0) |
| `sfx_magic_shield_activate` | DSGNSynth_BUFF-Bonus Max Shield 005 | −8 | 0,80 | pickup Shield (P0) |
| `sfx_magic_shield_end` | DSGNSynth_BUFF-Mecha Barrier Fail 004 | −10 | 0,70 | fin naturelle, pas à la mort (P1) |
| `sfx_player_hp_bonus` | DSGNSynth_BUFF-Mecha Level Up 004 | −8 | 0,77 | bonus HP collecté, après écriture réussie (P1) |
| `sfx_trapdoor_trigger` | DSGNSynth_BUFF-Mecha Lock In 004 | −8 | 0,50 | `warning_started` de la trappe (P0) |
| `sfx_turret_fire` | DSGNMisc_SKILL RELEASE-Flame Ball 004 | −10 | 0,50 | `fired` (P0) |
| `sfx_turret_projectile_impact` | EXPLOSION-Small Flare 001 | −10 | 0,40 | impact : −4 dB sur le joueur, −10 dB sur le décor (P0) |
| `sfx_poison_plant_hit` | DSGNMisc_SKILL IMPACT-Bubbly Zaps 005 | −8 | 0,60 | contact plante qui blesse (P0) |
| `sfx_spikes_hit` | DSGNMisc_HIT-Mecha Armor Piercer 006 | −8 | 0,50 | contact piques mobiles qui blesse (P0) |
| `sfx_spikes_extend` | DSGNMisc_SKILL RELEASE-Flying Blades 005 | −8 | 0,40 | sortie des piques, −12 dB (P1) |
| `sfx_door_coin_payment` | DSGNTonl_USABLE-Coin Spend 004 | −8 | 0,60 | ouverture d'une porte `coin_locked` (P0) |
| `sfx_door_unlock` | UIMisc_INTERFACE-Lock 006 + DSGNSynth_BUFF-Mecha Lock In 004 | −8 | 0,76 | toutes portes (P0) |
| `sfx_door_open` | DSGNMisc_MOVEMENT-Mecha Large Takeoff 005 | −8 | 1,10 | toutes portes (P0) |
| `sfx_pressure_plate_activate` | FEETMisc_STEP-Boots on Metal 003 + UIClick Metallic Click 001 | −8 | 0,24 | plaque (P0) |
| `sfx_button_activate` | UIClick_INTERFACE-Strong Click 1 003 | −8 | 0,26 | bouton (P0) |
| `sfx_secret_reveal` | EXPLOSION-Sand Impact 005 + MAGSpel_CAST-Skill Ready 005 | −8 | 1,02 | `revealed`, jamais au rechargement (P0) |

**Réutilisations.**
- Le Red Slime partage la famille Slime existante (`sfx_melee_hit`, `sfx_slime_death`), comme docs/08 le permet.
- Les coups non mortels sur les nouveaux ennemis réutilisent `sfx_melee_hit.tres` : les sons « hit » P1 dédiés ne sont pas livrés.
- L'impact de flèche d'os réutilise `sfx_arrow_impact.wav`.
- Familles reprises avec une prise différente, aucune prise déjà utilisée : Bamboo Whip (le saut utilise la 005), Wet Splash (mort Slime 001–003), Lock (coffre 002/004), Metallic Click (navigation UI 003).

**Substituts approximatifs, à écouter en priorité.**
- Le pack n'a pas de vrai équivalent pour : le tir d'archer (fouet, pas de corde), la trappe, la porte (grondement mécanique), la plante, les piques, la plaque, le bouton (clic d'interface).
- Mort des Skulls (aigu, risque de sifflement si plusieurs meurent ensemble), incantation (très grave), activation du Shield (caractère « cyan » non vérifié).
- **Aucune écoute n'a été faite** : sélection par analyse objective (durée, enveloppe, centroïde, noms de fichier). Notes : `work/run019/claude/audio/selection.md`.

## Fichiers de présentation modifiés (propriété remise par Codex)

Les `_draw` provisoires sont retirés ; les `queue_redraw()` restants n'ont plus d'effet visible. Chaque script reçoit un bloc « Presentation » qui crée son `AnimatedSprite2D` nommé `Art` et ses lecteurs `SFX`, branchés sur les signaux existants. Les effets et sons de mort, d'impact et de pickup sont détachés dans la scène courante (`process_mode` pausable), comme pour les Slimes, sans nouvelle récompense.

- **Nouveau `scripts/run019_art.gd`** (`Run019Art`) : `SpriteFrames` mises en cache depuis les tables, effets détachés (réutilise `OneShotFx`), sons positionnels, et `just_hurt(player)`. Ce dernier vaut vrai juste après un `take_damage` réellement appliqué : il détecte que `invulnerability` vient d'être remise à sa durée.
- **`scripts/run019_enemy.gd`** :
  - Choix de l'animation selon `pending_attack`, l'animation de frappe en cours, `knockback_time` et `velocity`. Pendant la préparation, un coup reçu garde l'animation de préparation et ajoute seulement une teinte : les attaques ne sont pas interrompues.
  - Sons sur `attack_started`/`attack_released`/`health_changed`/`defeated`. Mort détachée, plus l'éclatement du Bloated.
  - Une ligne ajoutée dans `_damage_player`, après l'appel inchangé de `take_damage` : retour visuel et sonore du contact Bloated, seulement si le coup a porté.
- **`scripts/run019_enemy_attack.gd`** :
  - La flèche est un sprite tourné selon le vol. La zone d'avertissement est pilotée par `elapsed`, figée au point engagé, en `z_index −1` pour ne pas masquer les acteurs.
  - Son d'avertissement attaché au nœud, parce que le nœud est positionné après `add_child`.
  - Impact ou explosion et leurs sons sur `impacted`. `cancel()` reste silencieux.
- **`scripts/possessed_skull.gd`** :
  - spawn → fly, morsure à moins de 16 px, mort détachée ;
  - `despawn_art()` est appelé par la swarm ;
  - une ligne ajoutée après `take_damage` : son du contact qui blesse.
- **`scripts/skull_swarm.gd`** : son d'apparition sur `swarm_started`. Dans la branche « joueur sorti », `_despawn_art()` est appelé avant `_clear()` ; `rewarded_slots` et le budget ne sont pas touchés.
- **`scripts/slime.gd`** : Red utilise sa propre feuille, construite au runtime avec les noms `red`/`red_hit`/`red_death`. La teinte provisoire est retirée. Gerbe et éclaboussure rouges. `scenes/slime.tscn` n'est pas modifiée.
- **Pièges** (`retractable_spikes`, `trapdoor`, `turret`, `trap_projectile`, `poison_plant`) :
  - Les animations suivent `phase_changed`/`warning_started`/`opened`/`fired`/`impacted`/`contacted`. La phase initiale est affichée au repos, sans transition.
  - Piques : une ligne ajoutée après `take_damage`, pour le son du contact qui blesse.
  - Tourelle : visée recalculée chaque frame, la direction pouvant changer après l'instanciation ; le lecteur est arrêté dans `_exit_tree`.
- **Pickups et mécanismes** (`magic_shield`, `hp_bonus`, `secret_wall`, `pressure_plate`, `mechanism_button`, `secondary_door`) :
  - Retours visuels et sonores sur `collected`/`revealed`/`activated`/`opened_signal`. Aucun handler E n'est ajouté.
  - Le bonus HP ne produit rien en cas d'échec d'écriture ; le feedback HUD « Save failed. Try again. » est conservé.
  - La porte choisit sa ligne d'art selon `coin_locked`. Le paiement n'est sonorisé que pour une porte à coins. Tous ses sons démarrent dès l'ouverture : aucun ne commence après le balayage audio de fermeture du niveau.
- **`scripts/player.gd`** :
  - L'arc cyan provisoire est remplacé par l'aura `ShieldAura`, visible tant que `magic_shield_time > 0`. Elle clignote pendant les 2 dernières secondes.
  - À la fin naturelle : fragmentation et `sfx_magic_shield_end`, mais pas à la mort.
  - Timers et règles de protection inchangés.
- **Non modifiés** : `scenes/*.tscn` (aucun corps, masque ni forme), `scripts/hud.gd` (le feedback d'erreur existant suffit), `scenes/player.tscn`, `scenes/hud.tscn`, et tous les fichiers de Codex.
- **Ajouté** : `tools/art/run019/capture_run019.gd`, pilote de captures de présentation. Ce n'est pas un test de recette.

## Vérifications réellement exécutées (Godot 4.7.2 Windows, `flock work/.godot.lock`, profils NTFS isolés)

- **Import éditeur** (`work/run019/check.sh claude-import`) : sans erreur ni avertissement ; 37 PNG et 37 WAV importés.
- **Correspondance des chemins** : tous les chemins `res://assets/...` cités par les scripts existent.
- **Régénération** : les trois générateurs produisent des PNG à MD5 identiques.
- **WAV** : les 37 fichiers sont mono 44,1 kHz 16 bits, et les durées comme les crêtes concordent avec le tableau.
- **`tools/test.sh` complet, premier passage** : tous les contrôles réussissent, mais `run019_traps` signale une fuite à la sortie (4 ObjectDB, `sfx_turret_fire.wav`). En verbose : les lectures du tir de tourelle sont encore actives au `quit()`, faute de drainage temps réel en fin de suite. En headless, l'audio avance en temps réel indépendamment de `--fixed-fps` (cas déjà rencontré en RUN-010, 015 et 017).
- **Deuxième passage**, avec le drainage proposé ci-dessous appliqué temporairement : `run019_cold_session prepare` fuyait `sfx_door_open.wav`. C'était un vrai défaut de présentation, corrigé : le son d'ouverture démarrait après l'animation de déverrouillage, donc possiblement après le balayage audio de `WM_CLOSE_REQUEST`.
- **Troisième passage**, avec ce même drainage temporaire : code 0, **31 suites + 8 sessions à froid + 1 isolation, 40 RESULT, 1941 PASS, 0 échec**, aucune ligne FAIL, SCRIPT ERROR, ERROR ni fuite. Logs `work/test-results/run-WLnropyS/`, sortie `work/run019/claude/full-suite-3.log`. Le fichier de test a ensuite été restauré : **sans ce patch, `tools/test.sh` échoue sur la fuite de `run019_traps`.**
- **Pilote rendu `tests/run019_visual.gd`** (non headless, assets intégrés, test non modifié) : **47/47**, code 0, sans erreur ni fuite (`work/run019/claude/render-visual.log`). Les 14 captures de `work/run019/render/` sont régénérées. Inspection représentative : pièges en tir, mécanismes ouverts, secret effacé.
- **Pilote de captures Claude** : **28/28**, code 0 (`work/run019/claude/capture.log`). Les 13 captures 640×360 de `work/run019/claude/render/` ont été inspectées, avec des agrandissements :
  - planche des 6 familles au sol, chevalier en référence ;
  - Skulls, flèche et 4 progressions de zone ;
  - états des pièges et mécanismes, deux lignes de porte, tourelle visant à gauche ;
  - en jeu : préparations Warrior/Archer/Sorcerer, relâches, zone figée sous le joueur puis explosion ;
  - aura de Shield avec la swarm, morts détachées (Chud, Bloated, 4 Skulls), fin du Shield ;
  - piques, plante, plaque → porte à mécanisme, éboulement du secret.
- **Premier essai du pilote** : l'Archer, à 130 px du joueur, n'acquérait pas l'aggro (demi-largeur 120 px). C'était une erreur de placement du pilote, corrigée ; le gameplay n'est pas en cause.

## Proposition de patch pour Codex (fichier de test, propriété Codex)

`work/run019/claude/proposed-run019_traps-drain.patch`. Deux lignes en fin de `tests/run019_traps.gd`, aucune assertion changée :

```
	room.queue_free()
	await frames()
+	# Let the real-time mixer release cues freed by the last fixtures (n1_flow convention).
+	OS.delay_msec(300)
	print("RESULT %d checks; %d failures" % [checks, failures])
```

## Limites et suites

- **Passe Claude validée en l’état par l’humain le 5 octobre 2026**. Les sujets de présentation ci-dessous sont acceptés dans cette passe ; aucun détail d’écoute ou d’essai interactif n’est présumé :
  - rendu et lisibilité en mouvement, ressenti des préparations et de la cadence des animations ;
  - échelle des élites ;
  - distinction spawn/despawn/mort des Skulls à vitesse réelle ;
  - lisibilité de l'aura du Shield et du mur secret dans un vrai mur ;
  - tourelle en pierre sur fond de pierre ;
  - **écoute de tous les sons**, notamment les substituts ci-dessus.
- **Non exécuté** :
  - playtest interactif ;
  - contexte de biome N2–4 réel (fixtures sur fond neutre) : la trappe et le mur secret n'ont été vus que posés sur un sol, pas dans un trou ni un mur ;
  - rendu Linux ;
  - mix en jeu avec la musique.
- **Choix et limites de présentation** :
  - Pas d'indicateur HUD de durée du Shield : seul le clignotement de l'aura annonce la fin.
  - Pas de « hit » dédié par famille : les sons P1 restent à faire, voir Réutilisations.
  - La frame « fissure » du mur secret n'est pas branchée.
  - La herse monte visuellement environ 0,5 s après la désactivation de la barrière (qui reste immédiate en gameplay).
  - Les dernières frames de la mort du Sorcerer, presque plates, sont peu lisibles.
- **Assets externes attendus** : des assets externes seront fournis pendant les runs 0.3.0 et adaptés au projet. Ils pourront remplacer ces feuilles via les tables d'intégration, en respectant le pipeline source → dérivé normalisé.
- **Hors périmètre, non commencé** : placements et habillage N2–4 (RUN-020/021), harmonisation globale.

## Retour à Codex

Les fichiers de présentation listés ci-dessus sont rendus à Codex.

Liste remise à Codex (historique ; voir audit ci-dessous pour les actions exécutées) :
- appliquer ou adapter le drainage de `run019_traps` ;
- intégrer les crédits audio et visuels ;
- décider de l'échelle des élites ;
- recette complète et rendu ;
- journal et learning ;
- revue Jev ;
- validation humaine art, écoute et essai avant DONE.

Aucun push, PR ni merge.

## Audit Codex après retour

Deux revues indépendantes en lecture seule (code et assets), suivies de recette root. Crédits visuels et section audio reportés ; collisions des élites conservées. Un défaut de piques chargées en phase dangereuse est reproduit par un test : `is_node_ready()` ne permet pas de distinguer cette initialisation. Un marqueur explicite affiche l’état initial sans transition/cue, puis autorise les transitions suivantes. Le drainage audio proposé est appliqué à la suite pièges ; ses assertions restent actives.

Les cues de porte simultanés constituent le compromis de présentation documenté pour éviter un démarrage après fermeture ; aucune régression de collision/paiement démontrée. Cette superposition et les cues hit/death combinés sont conservés dans la passe acceptée, sans prétendre à une écoute Codex.

Contrôle ciblé des sources audio : les 43 prises WAV référencées par le générateur existent dans la bibliothèque locale, sans modification de celle-ci. Ce contrôle ne constitue pas une nouvelle analyse juridique des licences ; attribution conservée depuis la provenance établie du pack.

Recette finale Codex après correctifs : import+31 suites+8 processus froids+isolation, **1943 PASS**, code0 sans erreur/fuite (`work/test-results/run-BqKIOkCW/`, `work/run019/audit-full-suite.log`). Pilote rendu47/47, code0 sans erreur/fuite (`work/test-results/run-sHD1FPQq/audit-render.log`), captures représentatives inspectées. RUN-019 VERIFY ; passe Claude validée, essai humain complet non présumé, Jev/inspection avant DONE restent requis.
