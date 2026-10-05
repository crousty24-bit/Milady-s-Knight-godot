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
