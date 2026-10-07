# Audio — provenance et licences

Médias audio intégrés par RUN-010 (30 septembre 2026), révisés par RUN-014 (2 octobre 2026). Les originaux restent dans la bibliothèque locale déclarée par `.local/asset-paths.md`, non modifiée ; les dérivés de jeu sont produits par `tools/prepare_audio.py`.

## SFX — Helton Yan, *Pixel Combat*

- **Auteur :** Helton Yan.
- **Source :** [FREE Pixel Combat SFX](https://heltonyan.itch.io/pixelcombat), dossier local `SFX/Helton Yan's Pixel Combat - Single Files/`.
- **Licence :** Creative Commons Attribution 4.0 International (CC BY 4.0), selon la page du pack consultée le 30 septembre 2026. Usage commercial, modification et redistribution permis ; **crédit obligatoire**.
- **Attribution à reprendre dans les crédits du jeu :** « Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 ».
- **Transformation :** silence de début/fin retiré (seuil −55 dB), fondu d'entrée de 2 ms, conversion mono 44,1 kHz PCM 16 bits, crête normalisée à **−8 dBFS** depuis RUN-014 (−3 dBFS en RUN-010) ; pièces tronquées à 0,7 s et double saut à 0,3 s, avec fondu de sortie de 0,15 s.

| Fichier de jeu | Fichier source |
| --- | --- |
| `sounds/sfx_player_jump.wav` | `SWSH_MOVEMENT-Bamboo Whip_HY_PC-005.wav` (RUN-014 ; auparavant Retro Jump) |
| `sounds/sfx_player_double_jump.wav` | `DSGNMisc_MOVEMENT-Whoosh Sweep_HY_PC-005.wav` (RUN-014 ; auparavant Jump Sparkle) |
| `sounds/sfx_player_wall_jump.wav` | `WHSH_MOVEMENT-Simple Whoosh_HY_PC-001.wav` |
| `sounds/sfx_melee_swing_light_01–03.wav` | `DSGNMisc_MELEE-Sword Slash_HY_PC-001–003.wav` |
| `sounds/sfx_melee_hit_01–03.wav` | `FGHTImpt_MELEE-Gut Punch_HY_PC-003, -006, -005.wav` (RUN-014 ; auparavant Gore Pierce) |
| `sounds/sfx_player_hit_01–03.wav` | `FGHTImpt_HIT-Strong Smack_HY_PC-001–003.wav` |
| `sounds/sfx_player_death.wav` | `DSGNImpt_EXPLOSION-Thud_HY_PC-001.wav` |
| `sounds/sfx_gold_coin_pickup_01–03.wav` | `DSGNTonl_USABLE-Magic Coin_HY_PC-001, -002, -004.wav` |
| `sounds/sfx_slime_death_01–03.wav` | `DSGNMisc_SKILL RELEASE-Wet Splash_HY_PC-001–003.wav` |

## SFX d'interface — RUN-015 (Helton Yan, *Pixel Combat*)

Même source, auteur, licence (CC BY 4.0) et attribution que la section ci-dessus ; fichiers produits par `python3 tools/prepare_audio.py sfx_ui_navigate sfx_ui_confirm sfx_ui_cancel sfx_ui_error`. **Transformation :** silence de début/fin retiré (seuil −55 dB), fondu d'entrée de 2 ms, mono 44,1 kHz PCM 16 bits, crête normalisée à **−12 dBFS** (sous les SFX de gameplay à −8 dBFS), sans troncature supplémentaire. Sélection faite par analyse objective (durée, spectre, tendance de hauteur) ; l'écoute humaine reste à faire.

| Fichier de jeu | Fichier source | Durée |
| --- | --- | --- |
| `sounds/sfx_ui_navigate.wav` | `UIClick_INTERFACE-Metallic Click_HY_PC-003.wav` | 0,12 s |
| `sounds/sfx_ui_confirm.wav` | `DSGNTonl_INTERFACE-Tonal Click_HY_PC-005.wav` | 0,22 s |
| `sounds/sfx_ui_cancel.wav` | `UIClick_INTERFACE-Strong Click 2_HY_PC-003.wav` | 0,23 s |
| `sounds/sfx_ui_error.wav` | `UIMisc_INTERFACE-Denied_HY_PC-002.wav` | 0,43 s |

## SFX Arc long, coffre, éclats et potion — RUN-016 (Helton Yan, *Pixel Combat*)

Même source, auteur, licence (CC BY 4.0) et attribution que les sections ci-dessus ; fichiers produits par `python3 tools/prepare_audio.py` suivi des noms `sfx_weapon_bow_shot_01` … `sfx_chest_reward_accept` (voir `tools/prepare_audio.py`). **Transformation :** silence de début/fin retiré (seuil −55 dB), fondu d'entrée de 2 ms, mono 44,1 kHz PCM 16 bits, crête normalisée à **−8 dBFS** par défaut, **−10 dBFS** pour les sons répétitifs (tir d'arc, éclats), **−12 dBFS** pour `sfx_weapon_switch` (type interface) ; durée plafonnée avec fondu de sortie de 0,15 s lorsque la source dépasse la cible (colonne « Coupe »). Sélection faite par analyse objective (durée, enveloppe, spectre) ; l'écoute humaine reste à faire, plusieurs choix étant approximatifs (le pack n'offre ni corde d'arc ni bois de coffre).

| Fichier de jeu | Fichier source | Durée | Coupe |
| --- | --- | --- | --- |
| `sounds/sfx_weapon_bow_shot_01–03.wav` | `DSGNMisc_PROJECTILE-High Whoosh_HY_PC-001–003.wav` | 0,38 s | 0,38 s |
| `sounds/sfx_arrow_impact.wav` | `FEETMisc_STEP-Hard Step_HY_PC-002.wav` | 0,19 s | non |
| `sounds/sfx_shard_gain_01–03.wav` | `DSGNTonl_SKILL IMPACT-Star Sparkle_HY_PC-001–003.wav` | 0,55–0,58 s | 0,58 s |
| `sounds/sfx_minor_potion_pickup.wav` | `DSGNTonl_MOVEMENT-Bubble Babbler_HY_PC-001.wav` | 0,50 s | 0,50 s |
| `sounds/sfx_player_heal.wav` | `MAGAngl_BUFF-Simple Heal_HY_PC-002.wav` | 0,78 s | 0,78 s |
| `sounds/sfx_weapon_switch.wav` | `UIClick_INTERFACE-Rattling Click_HY_PC-002.wav` | 0,27 s | non |
| `sounds/sfx_weapon_equip.wav` | `DSGNTonl_USABLE-Metallic Item_HY_PC-002.wav` | 0,60 s | non |
| `sounds/sfx_chest_open_common.wav` | `UIMisc_INTERFACE-Lock_HY_PC-002.wav` | 0,41 s | non |
| `sounds/sfx_chest_reward_reveal.wav` | `SWSH_MOVEMENT-Tiny Chime_HY_PC-002.wav` | 0,75 s | 0,75 s |
| `sounds/sfx_chest_reward_accept.wav` | `DSGNTonl_USABLE-Tonal Item_HY_PC-003.wav` | 0,58 s | 0,58 s |

## SFX dialogue — RUN-017 (Helton Yan, *Pixel Combat*)

Même source, auteur, licence (CC BY 4.0) et attribution que les sections ci-dessus ; produit par `python3 tools/prepare_audio.py sfx_dialogue_open`. Même transformation, crête **−12 dBFS** (niveau UI), coupe à 1,2 s avec fondu de sortie de 0,15 s ; joué sur le bus UI à l'ouverture du bandeau. Sélection par analyse objective (attaque douce, ton chatoyant, sans voix), l'écoute humaine reste à faire.

`sfx_spirit_appear.wav` (RUN-017/2, matérialisation du Spirit, bus SFX) : produit par `python3 tools/prepare_audio.py sfx_spirit_appear`, crête **−10 dBFS**, coupe à 1,3 s avec fondu de sortie ; gonflement grave-médium doux (crête vers 0,8 s), sans attaque percussive. Sélection par analyse objective uniquement, l'écoute humaine reste à faire.

| Fichier de jeu | Fichier source | Durée | Coupe |
| --- | --- | --- | --- |
| `sounds/sfx_dialogue_open.wav` | `MAGAngl_BUFF-Shimmer Tone_HY_PC-001.wav` | 1,2 s | 1,2 s |
| `sounds/sfx_spirit_appear.wav` | `MAGSpel_CAST-Growing Strength_HY_PC-005.wav` | 2,98 s | 1,3 s |

## Limites acceptées et suivi RUN-016 (3 octobre 2026)

La passe Claude est validée par l’humain, avec ces réserves pour RUN-027 : le tir utilise un whoosh, l’impact un pas dur et l’ouverture un verrou, faute de corde d’arc, d’impact de bois et de grincement de coffre dans le pack. Le tableau ci-dessus trace ces substituts actuels ; il ne liste pas encore de nouveaux fichiers de remplacement sélectionnés. Claude devra sélectionner et faire écouter les remplaçants avant leur intégration.

À l’acquisition de Longbow0, confirmation UI, acceptation du coffre et nouvelle arme se superposent. Le mix reste à juger à l’écoute lors de cette passe ; la validation actuelle ne constitue pas une mesure de qualité du mix.

## Musique — Pixabay

- **Fichier de jeu (RUN-014) :** `music/music_slice_dreamer.ogg`, musique du slice.
- **Source :** `Music/nojisuma-dreamer-131011.mp3` ; auteur Pixabay `nojisuma`, identifiant 131011. La page exacte du morceau reste à relier au fichier.
- **Licence :** [Pixabay Content License](https://pixabay.com/service/license-summary/) — usage gratuit, modification permise, attribution non requise ; vente ou distribution du contenu seul, sous une forme substantiellement identique, interdite.
- **Transformation :** coupé à 156,0 s, avant le fondu final et sur une fin de mesure de 4 s, fondus de 30 ms aux bords, loudness normalisée à −13 LUFS (true peak −1,5 dBFS), Ogg Vorbis q5 44,1 kHz, boucle activée à l'import.
- **Remplacé :** `music/music_slice_dark_fantasy_lofi.ogg` (Pixabay `welc0mei0`, identifiant 148338, −16 LUFS) réutilisé comme thème du menu principal en RUN-015 le 3 octobre 2026, à la demande humaine. Sa source est `Music/welc0mei0-bgm006-dark-fantasy-lo-fi-retro-game-148338.mp3` ; le dérivé existant stéréo 44,1 kHz (~132 s), à −16 LUFS, est conservé avec boucle d'import activée. Le lecteur de menu est routé vers Music et supprimé à l'entrée en jeu.

## Retour d'écoute (30 septembre 2026)

Première itération validée. À reprendre (traité par RUN-014, en attente d'écoute humaine) : musique trop basse et à remplacer par un autre morceau ; SFX globalement trop forts ; impact d'épée (`sfx_melee_hit`) peu agréable, à remplacer ; sons de saut et de double saut à remplacer. Les sélections ci-dessus restent donc provisoires.

## Médias hérités

`coin.wav` (encore utilisé par la porte), `jump.wav`, `hurt.wav`, `tap.wav` et `time_for_adventure.ogg` restent dans le dépôt sans provenance établie ; ce contrôle reste différé à la recette des licences avant distribution.

## Non retenu

*Shooter Synthwave Music Pack* (AlkaKrab) : la licence interdit la redistribution des pistes telles quelles et demande une autorisation de l'auteur pour un jeu open source ; non intégré (RUN-014).

*Minifantasy Dungeon SFX* (Leohpaz / Krishna Palacio) convenait au style mais interdit la redistribution des fichiers ; le dépôt GitHub étant public, il n'a pas été intégré.


## SFX équipement standard et coffres — RUN-018 (5 octobre 2026)

Même auteur/source/licence et attribution Helton Yan *Pixel Combat*, CC BY 4.0, que ci-dessus. Dérivés `assets/sounds/run018/`, générateur `tools/art/run018/prepare_audio_run018.py` ; sources lues uniquement dans la bibliothèque locale. Silence retiré, fondu de2ms, conversion mono44,1kHz PCM16bits, crête normalisée selon tableau, durées plafonnées avec fondu final. Le rare mélange deux sources (seconde retardée de120ms et abaissée de4dB).

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


Les cues common/reveal/accept et navigation UI existants sont réutilisés. Sélection Claude par analyse objective uniquement ; écoute humaine pas encore validée pour RUN-018. Familles lourdes/couteaux partagées et substituts approximatifs sont tracés pour RUN-027, sans promettre leur acceptation sonore. Mesure Codex des12 WAV : mono44,1kHz16bits, durées concordantes, crêtes à±0,05dB des cibles ; cela ne remplace ni l’écoute ni la recette du mix en jeu.


## Menaces et exploration — RUN-019 (5 octobre 2026)

37 WAV dans `assets/sounds/run019/`, produits par `tools/art/run019/prepare_audio_run019.py`. Même auteur, source et licence que la section Helton Yan ci-dessus : [Pixel Combat SFX](https://heltonyan.itch.io/pixelcombat), CC BY 4.0. Attribution : « Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 ». Les originaux de la bibliothèque locale sont conservés.

Transformation : pipeline `tools/prepare_audio.py` (trim −55 dB, fondu d’entrée 2 ms, mono 44,1 kHz PCM 16 bits, normalisation aux crêtes ci-dessous, coupe avec fondu de sortie si nécessaire). Les combinaisons superposent une seconde source à +0,12 s et −4 dB. La validation humaine de la passe Claude est reçue ; aucun détail d’écoute ou de playtest n’est présumé.


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
- **Sélection Claude sans écoute** : sélection par analyse objective (durée, enveloppe, centroïde, noms de fichier). Notes : `work/run019/claude/audio/selection.md`.

## Ambiances originales — RUN-020 (5 octobre 2026)

`assets/sounds/run020/amb_{blight_town,black_forrest,forbidden_graveyard}.ogg` : synthèse originale déterministe par `tools/art/run020/ambience_run020.py`, contribution Claude/Sonnet5.5. PCM source mono22,05kHz/16bits/28s conservé dans `assets/source/run020/`; dérivés Vorbis qualité4 produits avec ffmpeg par Codex, boucle au début. Aucun son tiers dans ces trois ambiances. N2–4 réutilisent provisoirement la piste Pixabay *Dreamer* déjà créditée plus haut. [Manifeste RUN-020](../docs/RUN-020_ASSET_MANIFEST.md). Écoute humaine attendue.

## Musique N4 Forbidden Graveyard — RUN-021 (6 octobre 2026)

- **Fichier de jeu :** `run021/audio/music_n4_forbidden_graveyard.ogg`, référencé par le node `Music` de `scenes/forbidden_graveyard.tscn` (choix humain).
- **Morceau :** « Dark Synthwave Retro 80s », auteur Pixabay **DELOSound**, identifiant 453292, 3:24 ; [page officielle](https://pixabay.com/music/dance-dark-synthwave-retro-80s-453292/). La page affiche « Content ID Registered » (signalé aussi par l'humain) : une revendication Content ID reste possible si le jeu est diffusé en vidéo monétisée ; à garder en tête pour la recette des licences.
- **Licence :** [Pixabay Content License](https://pixabay.com/service/license-summary/) (consultée le 6 octobre 2026) — usage gratuit, modification permise, attribution non requise ; vente ou distribution du contenu seul, sous une forme essentiellement inchangée, interdite. Aucun certificat de téléchargement n'est détenu ni inventé.
- **Source conservée :** `assets/source/run021/audio/delosound-dark-synthwave-retro-80s-453292.mp3` (copie inchangée de `Music/…` ; SHA-256 `0eb8ae69cc50a3ab5ac8108d92e2aaf3b3859f9efa7b2e654e1e7b5bb6414c3c`, 6 529 358 octets, MP3 256 kb/s 44,1 kHz stéréo, 204,04 s) ; provenance détaillée dans `provenance.json` du même dossier.
- **Transformation :** coupe à 185,274 s (avant la sortie finale), loudnorm −13 LUFS / TP −1,5 dBFS (résultat mesuré −12,6 LUFS, true peak −0,8 dBFS), fondu croisé de 6 ms entre la fin et les 6 ms précédant le point de boucle, Ogg Vorbis q5 44,1 kHz stéréo ; boucle d'import activée avec `loop_offset` 5,564 s (l'intro de 5,6 s ne se joue qu'une fois). Commandes : `work/run021/audio/prepare_n4.sh`. Détails : [docs/RUN-021_AUDIO_REVIEW.md](../docs/RUN-021_AUDIO_REVIEW.md). Écoute humaine attendue.
- **Statut :** N4 n'utilise plus *Dreamer* ; N2 et N3 le conservent.

## Titrage de niveau — RUN-021 (7 octobre 2026, Helton Yan, *Pixel Combat*, CC BY 4.0)

| Fichier de jeu | Fichiers source | Durée | Transformation |
| --- | --- | --- | --- |
| `sounds/run021/sfx_level_title.wav` | `DSGNImpt_EXPLOSION-Thud_HY_PC-003.wav` (impact à t=0, −2 dB) + `MAGSpel_CAST-Teleport Downer_HY_PC-005.wav` (ton grave descendant, retard 80 ms) | 2,44 s | mix deux couches, mono 44,1 kHz 16 bits, coupe 2,5 s + fondu 0,15 s, pic −12 dBFS (`UI_PEAK_DB`) ; `tools/art/run021/prepare_audio_title.py` |

Choix objectif (contenu grave/aigu mesuré, aucune prise déjà utilisée) ; joué sur le bus UI à l'apparition du nom du niveau, lecteur à −3 dB (retour humain du 7 octobre 2026 : « réduire légèrement »). Écoute humaine attendue (caractère « Dark Souls » contre sci-fi, volume face à la musique).

## Révélation du coffre payant — RUN-021 (7 octobre 2026, Helton Yan, *Pixel Combat*, CC BY 4.0)

| Fichier de jeu | Fichiers source | Pic | Durée | Usage |
| --- | --- | --- | --- | --- |
| `sounds/run021/sfx_chest_reveal_rise.wav` | `MAGSpel_CAST-Aura Up_HY_PC-002.wav` (0–2,4 s, étiré ×1,22) + `MAGSpel_CAST-Growing Strength_HY_PC-004.wav` (inversé, −5 dB) | −10 dBFS | 2,90 s | crescendo du faisceau de lumière, de l'appui sur « Open » jusqu'au flash blanc (~2,9 s) |
| `sounds/run021/sfx_chest_reveal_burst.wav` | `DSGNTonl_SKILL IMPACT-Glistening Shimmers_HY_PC-004.wav` + `DSGNTonl_SKILL IMPACT-Magic Sparkles_HY_PC-002.wav` (−3 dB) | −9 dBFS | 1,20 s | éclat final au flash blanc, ou immédiatement si le joueur passe l'animation |

Transformation : mono 44,1 kHz 16 bits, coupe −55 dB, fondu d'entrée 2 ms, normalisation de crête ; `tools/art/run021/prepare_audio_chest_reveal.py`. Montée : seule la partie ascendante d'« Aura Up » est gardée et étirée sans changer la hauteur (`atempo`), mélangée à un balayage inversé de « Growing Strength », puis une rampe de volume linéaire en dB (−34 dB à t=0, 0 dB à 2,9 s) impose le crescendo ; fondu de sortie de 30 ms (la coupure est masquée par l'éclat). Éclat : deux couches à t=0, coupe 1,2 s + fondu 0,15 s.

Choix objectif (durée, enveloppe RMS, taux de passages par zéro croissant, part de grave, aucune prise déjà utilisée) ; aucun autre pack (notamment pas Minifantasy) n'est utilisé. Attribution : « Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 ». Écoute humaine attendue (caractère « lumière sacrée » contre sci-fi, volume face au SFX d'ouverture du coffre).
