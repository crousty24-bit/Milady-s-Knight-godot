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

## Musique — Pixabay

- **Fichier de jeu (RUN-014) :** `music/music_slice_dreamer.ogg`, musique du slice.
- **Source :** `Music/nojisuma-dreamer-131011.mp3` ; auteur Pixabay `nojisuma`, identifiant 131011. La page exacte du morceau reste à relier au fichier.
- **Licence :** [Pixabay Content License](https://pixabay.com/service/license-summary/) — usage gratuit, modification permise, attribution non requise ; vente ou distribution du contenu seul, sous une forme substantiellement identique, interdite.
- **Transformation :** coupé à 156,0 s, avant le fondu final et sur une fin de mesure de 4 s, fondus de 30 ms aux bords, loudness normalisée à −13 LUFS (true peak −1,5 dBFS), Ogg Vorbis q5 44,1 kHz, boucle activée à l'import.
- **Remplacé :** `music/music_slice_dark_fantasy_lofi.ogg` (Pixabay `welc0mei0`, identifiant 148338, −16 LUFS) n'est plus référencé ; le fichier reste dans le dépôt en attendant la décision humaine.

## Retour d'écoute (30 septembre 2026)

Première itération validée. À reprendre (traité par RUN-014, en attente d'écoute humaine) : musique trop basse et à remplacer par un autre morceau ; SFX globalement trop forts ; impact d'épée (`sfx_melee_hit`) peu agréable, à remplacer ; sons de saut et de double saut à remplacer. Les sélections ci-dessus restent donc provisoires.

## Médias hérités

`coin.wav` (encore utilisé par la porte), `jump.wav`, `hurt.wav`, `tap.wav` et `time_for_adventure.ogg` restent dans le dépôt sans provenance établie ; ce contrôle reste différé à la recette des licences avant distribution.

## Non retenu

*Shooter Synthwave Music Pack* (AlkaKrab) : la licence interdit la redistribution des pistes telles quelles et demande une autorisation de l'auteur pour un jeu open source ; non intégré (RUN-014).

*Minifantasy Dungeon SFX* (Leohpaz / Krishna Palacio) convenait au style mais interdit la redistribution des fichiers ; le dépôt GitHub étant public, il n'a pas été intégré.
