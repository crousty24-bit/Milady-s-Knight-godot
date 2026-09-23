
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

La liste de candidats ci-dessus n'est pas une preuve de source ni de licence pour les fichiers effectivement intégrés. Les fichiers ci-dessous complètent les sept médias visuels inventoriés dans [11_GAME_ASSETS_LIBRARY.md](11_GAME_ASSETS_LIBRARY.md), soit **12 médias de jeu** au total (6 PNG, 4 WAV, 1 OGG, 1 TTF), sans compter les trois copies source conservées. La liste fonctionnelle cible des événements sonores reste dans [08_AUDIO_REQUIREMENTS.md](08_AUDIO_REQUIREMENTS.md).

| Fichier présent | Référence vérifiée | Usage actuel | Provenance et licence du fichier présent |
| --- | --- | --- | --- |
| `assets/sounds/coin.wav` | `scenes/coin.tscn`, `scenes/gold_gate.tscn` | Collecte et porte du slice. | À établir par une source et une licence rattachées au fichier exact. |
| `assets/sounds/jump.wav` | `scenes/player.tscn` | Saut du joueur. | À établir. |
| `assets/sounds/hurt.wav` | `scenes/player.tscn`, `scenes/slime.tscn` | Dégâts joueur/Slime. | À établir. |
| `assets/sounds/tap.wav` | `scenes/player.tscn` | Son d'attaque actuel. | À établir. |
| `assets/music/time_for_adventure.ogg` | `scenes/vertical_slice.tscn` | Musique du slice, non attribuée à un morceau cible des niveaux de la démo. | À établir. |

La [PR RUN-001](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/1) conserve les WAV originaux `coin`, `jump` et `tap` dans `assets/source/sounds/` et corrige leurs conteneurs RIFF aux chemins utilisés par Godot. Cette conservation garantit l'identité des données audio, **pas** la provenance juridique des sons. La branche RUN-002, créée depuis `develop`, a intégré localement RUN-001 après le premier checkpoint documentaire ; la PR RUN-001 a ensuite été fusionnée dans `develop` le 23 septembre 2026.

**Décision avant distribution :** obtenir pour chacun des cinq fichiers le fichier/pack d'origine exact, auteur, URL officielle ou archive d'achat, version, licence, attribution et chaîne de transformation. Si ces éléments manquent, remplacer le média par une source documentée et tester son intégration. Les étiquettes `Free` et `DL ✅` des listes de candidats ne suffisent pas à valider un droit d'usage.

### Livrables audio par jalon

Ces familles suivent les systèmes et niveaux planifiés dans `runs-workflow.md`. Les identifiants précis, priorités P0/P1/P2, formats et variantes restent définis dans [08_AUDIO_REQUIREMENTS.md](08_AUDIO_REQUIREMENTS.md). Le premier jalon indiqué correspond à l'apparition de la fonctionnalité, pas à une licence validée ni à un son déjà intégré. Les quatre WAV hérités et la musique du slice ne couvrent pas automatiquement ces familles cibles.

| Premier jalon | Événements à couvrir et vérifier dans le jeu | Ambiance et musique |
| --- | --- | --- |
| 0.1.0 | Saut, attaque Sword, dégâts/mort, Slime, pièce, piques et feedbacks élémentaires ; bus Master/Music/SFX | Le morceau du slice reste provisoire pendant les essais. |
| 0.2.0 | Tir Longbow et impact, shard, potion mineure, common chest, dialogue Spirit, menus clavier, sortie/reprise | `amb_eidolon_vale`, `music_eidolon_vale`, thème menu. |
| 0.3.0 | Red/Bloated Slime, piques mobiles, trappes, rare chest, choix/amélioration d'arme, soins | `amb_blight_town`, famille `music_early_kingdom`. |
| 0.4.0 | Warrior, Archer, Sorcerer, Swarm, Chud, tourelle, plante, Magic Shield, mécanismes et secret ; télégraphies distinctes | Ambiances N3–4, familles early kingdom et graveyard/caves. |
| 0.5.0 | Grimpe/atterrissage offensif, flammes, Rage, Fire Gauntlet, quatre légendaires, golden chest, Enchant Juice, offrande | Ambiances N5–6, familles graveyard/caves et desolands/camps. |
| 0.6.0 | Charge du Champion, incantations/invocations du Necromancer, seconde offrande | Ambiances N7–9, familles desolands/camps et temple/dungeon. |
| 0.7.0 | Intro, télégraphies, mêlée, zones, boules de feu, charge, invocations, enrage et mort de Lupikal ; libération de Karla | `amb_darkveil_throne`, `music_boss_final`, musique de fin. |
| 0.8.0 | Variantes et mix final de tous les feedbacks requis, volumes et spatialisation ; aucune famille P0 manquante | Contrôle des dix ambiances et des familles musicales de la démo. |
| 0.9.0 | Régression audio dans les builds et crédits/licences distribuables | Aucun nouveau morceau requis par le jalon ; corriger les défauts observés. |

Les achats et le choix final des packs restent une décision humaine. Avant toute intégration définitive, conserver la source, documenter sa licence et ses attributions, puis tester le dérivé normalisé avec les autres sons pour éviter masquage et clipping.
