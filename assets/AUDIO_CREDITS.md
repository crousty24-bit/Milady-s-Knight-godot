# Audio — provenance et licences

Médias audio intégrés par RUN-010 (30 septembre 2026). Les originaux restent dans la bibliothèque locale déclarée par `.local/asset-paths.md`, non modifiée ; les dérivés de jeu sont produits par `tools/prepare_audio.py`.

## SFX — Helton Yan, *Pixel Combat*

- **Auteur :** Helton Yan.
- **Source :** [FREE Pixel Combat SFX](https://heltonyan.itch.io/pixelcombat), dossier local `SFX/Helton Yan's Pixel Combat - Single Files/`.
- **Licence :** Creative Commons Attribution 4.0 International (CC BY 4.0), selon la page du pack consultée le 30 septembre 2026. Usage commercial, modification et redistribution permis ; **crédit obligatoire**.
- **Attribution à reprendre dans les crédits du jeu :** « Sound effects: Pixel Combat SFX by Helton Yan — CC BY 4.0 ».
- **Transformation :** silence de début/fin retiré (seuil −55 dB), fondu d'entrée de 2 ms, conversion mono 44,1 kHz PCM 16 bits, crête normalisée à −3 dBFS ; pièces tronquées à 0,7 s avec fondu de sortie de 0,15 s.

| Fichier de jeu | Fichier source |
| --- | --- |
| `sounds/sfx_player_jump.wav` | `DSGNMisc_MOVEMENT-Retro Jump_HY_PC-001.wav` |
| `sounds/sfx_player_double_jump.wav` | `DSGNMisc_MOVEMENT-Jump Sparkle_HY_PC-001.wav` |
| `sounds/sfx_player_wall_jump.wav` | `WHSH_MOVEMENT-Simple Whoosh_HY_PC-001.wav` |
| `sounds/sfx_melee_swing_light_01–03.wav` | `DSGNMisc_MELEE-Sword Slash_HY_PC-001–003.wav` |
| `sounds/sfx_melee_hit_01–03.wav` | `DSGNMisc_HIT-Gore Pierce_HY_PC-001–003.wav` |
| `sounds/sfx_player_hit_01–03.wav` | `FGHTImpt_HIT-Strong Smack_HY_PC-001–003.wav` |
| `sounds/sfx_player_death.wav` | `DSGNImpt_EXPLOSION-Thud_HY_PC-001.wav` |
| `sounds/sfx_gold_coin_pickup_01–03.wav` | `DSGNTonl_USABLE-Magic Coin_HY_PC-001, -002, -004.wav` |
| `sounds/sfx_slime_death_01–03.wav` | `DSGNMisc_SKILL RELEASE-Wet Splash_HY_PC-001–003.wav` |

## Musique — Pixabay

- **Fichier de jeu :** `music/music_slice_dark_fantasy_lofi.ogg`, musique provisoire du slice.
- **Source :** `Music/welc0mei0-bgm006-dark-fantasy-lo-fi-retro-game-148338.mp3` ; auteur Pixabay `welc0mei0`, identifiant 148338. La page exacte du morceau reste à relier au fichier.
- **Licence :** [Pixabay Content License](https://pixabay.com/service/license-summary/) — usage gratuit, modification permise, attribution non requise ; vente ou distribution du contenu seul, sous une forme substantiellement identique, interdite.
- **Transformation :** MP3 → Ogg Vorbis q5 44,1 kHz, loudness normalisée à −16 LUFS (true peak −1,5 dBFS), boucle activée à l'import.

## Retour d'écoute (30 septembre 2026)

Première itération validée. À reprendre : musique trop basse et à remplacer par un autre morceau ; SFX globalement trop forts ; impact d'épée (`sfx_melee_hit`) peu agréable, à remplacer ; sons de saut et de double saut à remplacer. Les sélections ci-dessus restent donc provisoires.

## Médias hérités

`coin.wav` (encore utilisé par la porte), `jump.wav`, `hurt.wav`, `tap.wav` et `time_for_adventure.ogg` restent dans le dépôt sans provenance établie ; ce contrôle reste différé à la recette des licences avant distribution.

## Non retenu

*Minifantasy Dungeon SFX* (Leohpaz / Krishna Palacio) convenait au style mais interdit la redistribution des fichiers ; le dépôt GitHub étant public, il n'a pas été intégré.
