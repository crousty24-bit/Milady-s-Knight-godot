
**Liste SFX à intégrer :**

| Nom | Type | Catégorie | Liens | Prix | Rating | DL  |
| --- | ---- | --------- | ----- | ---- | ------ | --- |
|     |      |           |       |      |        |     |

**Liste Ambiant à intégrer :**

| Nom | Type | Catégorie | Liens | Prix | Rating | DL  |
| --- | ---- | --------- | ----- | ---- | ------ | --- |
|     |      |           |       |      |        |     |


**Liste Music à intégrer :**

| Nom                                                                                                                 | Type                    | Catégorie  | Liens | Prix | Rating | DL  |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------- | ---------- | ----: | ---- | ------ | --- |
| delosound-dark-synthwave-retro-80s-453292![[delosound-dark-synthwave-retro-80s-453292.mp3]]                         | `music_graveyard_caves` | Music Loop |    __ | Free | 🟠     | ✅   |
| echoes_of_lumen-video-games-584898![[echoes_of_lumen-video-games-584898.mp3]]                                       | `music_boss_final`      | Music Loop |       | Free | 🔴     | ✅   |
| kiravale-gaming-music-593659![[kiravale-gaming-music-593659.mp3]]                                                   | `music_early_kingdom`   | Music Loop |       | Free | 🔴     | ✅   |
| mondamusic-retro-arcade-game-music-512837![[mondamusic-retro-arcade-game-music-512837.mp3]]                         | __                      | __         |       |      | 🟡     | ✅   |
| turtlebeats-dark-synthwave-black-neon-251690![[turtlebeats-dark-synthwave-black-neon-251690.mp3]]                   | `music_graveyard_caves` | Music Loop |       | Free | 🟠     | ✅   |
| turtlebeats-dark-synthwave-obilivion-echo-251687![[turtlebeats-dark-synthwave-obilivion-echo-251687.mp3]]           | `music_desolands_camps` | Music Loop |       | Free | 🟠     | ✅   |
| turtlebeats-dark-synthwave-spectral-251688![[turtlebeats-dark-synthwave-spectral-251688.mp3]]                       | `music_temple_dungeon`  | Music Loop |       | Free | 🟠     | ✅   |
| welc0mei0-bgm006-dark-fantasy-lo-fi-retro-game-148338![[welc0mei0-bgm006-dark-fantasy-lo-fi-retro-game-148338.mp3]] | `music_main_theme`      | Music Loop |       | Free | 🔴     | ✅   |
|                                                                                                                     |                         |            |       |      |        |     |
|                                                                                                                     |                         |            |       |      |        |     |

---

## RUN-002 — Médias audio présents dans le dépôt (23 septembre 2026)

La liste de candidats ci-dessus n'est pas une preuve de source ni de licence pour les fichiers effectivement intégrés. Les fichiers ci-dessous complètent les sept médias visuels inventoriés dans [11_GAME_ASSETS_LIBRARY.md](11_GAME_ASSETS_LIBRARY.md#run-002--médias-visuels-présents-dans-le-dépôt-23-septembre-2026), soit **12 médias présents** au total (6 PNG, 4 WAV, 1 OGG, 1 TTF). La liste fonctionnelle cible des événements sonores reste dans [08_AUDIO_REQUIREMENTS.md](08_AUDIO_REQUIREMENTS.md).

| Fichier présent | Référence vérifiée | Usage actuel | Provenance et licence du fichier présent |
| --- | --- | --- | --- |
| `assets/sounds/coin.wav` | `scenes/coin.tscn`, `scenes/gold_gate.tscn` | Collecte et porte du slice. | À établir par une source et une licence rattachées au fichier exact. |
| `assets/sounds/jump.wav` | `scenes/player.tscn` | Saut du joueur. | À établir. |
| `assets/sounds/hurt.wav` | `scenes/player.tscn`, `scenes/slime.tscn` | Dégâts joueur/Slime. | À établir. |
| `assets/sounds/tap.wav` | `scenes/player.tscn` | Son d'attaque actuel. | À établir. |
| `assets/music/time_for_adventure.ogg` | `scenes/vertical_slice.tscn` | Musique du slice, non attribuée à un morceau cible des niveaux de la démo. | À établir. |

La [PR RUN-001](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/1) conserve les WAV originaux `coin`, `jump` et `tap` dans `assets/source/sounds/` et corrige leurs conteneurs RIFF aux chemins utilisés par Godot. Cette conservation garantit l'identité des données audio, **pas** la provenance juridique des sons. La présente branche part de `develop` avant l'intégration de cette PR ; les originaux y apparaîtront après fusion.

**Décision avant distribution :** obtenir pour chacun des cinq fichiers le fichier/pack d'origine exact, auteur, URL officielle ou archive d'achat, version, licence, attribution et chaîne de transformation. Si ces éléments manquent, remplacer le média par une source documentée et tester son intégration. Les étiquettes `Free` et `DL ✅` des listes de candidats ne suffisent pas à valider un droit d'usage.
