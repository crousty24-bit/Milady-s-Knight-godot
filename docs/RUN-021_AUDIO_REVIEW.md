# RUN-021 — Revue audio : musique N4 et audit SFX

Date : 6 octobre 2026. Auteur : sous-agent audio (Sonnet 5.5) pour le lot Claude de RUN-021. Spécification : [RUN-021_CLAUDE_HANDOFF_02.md](RUN-021_CLAUDE_HANDOFF_02.md). Crédits : [assets/AUDIO_CREDITS.md](../assets/AUDIO_CREDITS.md).

Règle de lecture : trois statuts sont séparés partout. **Décision proposée** (non appliquée), **remplacement appliqué** (seulement la musique N4 ; aucun SFX), **écoute humaine en attente**. Aucune écoute humaine n'a eu lieu ; toutes les observations sonores ci-dessous sont des mesures objectives (ffmpeg), pas des jugements d'écoute.

## 1. Musique N4 Forbidden Graveyard

### 1.1 Source et licence

- Choix humain : *Dark Synthwave Retro 80s*, DELOSound, Pixabay 453292 ([page](https://pixabay.com/music/dance-dark-synthwave-retro-80s-453292/), 3:24, mise en ligne le 18 décembre 2025 d'après la page, mention « Content ID Registered »).
- Licence : [Pixabay Content License](https://pixabay.com/service/license-summary/) ; conditions pertinentes archivées dans `assets/source/run021/audio/provenance.json` (usage et modification gratuits, attribution facultative, distribution isolée inchangée interdite). Pas de certificat de téléchargement ; aucun n'est inventé.
- Fichier source copié sans modification dans `assets/source/run021/audio/delosound-dark-synthwave-retro-80s-453292.mp3` (dossier ignoré par Godot : `assets/source/.gdignore` existe). SHA-256 `0eb8ae69cc50a3ab5ac8108d92e2aaf3b3859f9efa7b2e654e1e7b5bb6414c3c`, 6 529 358 octets. ffprobe : MP3, 44,1 kHz, stéréo, 256 kb/s, 204,042 s, sans tags. Le fichier de la bibliothèque externe n'a pas été modifié (copie en lecture seule).
- Risque à noter pour la recette des licences : Content ID (revendication possible sur une vidéo monétisée du jeu).

### 1.2 Conversion

Script : `work/run021/audio/prepare_n4.sh`, qui suit la méthode de `tools/prepare_audio.py` (loudnorm −13 LUFS, TP −1,5, Ogg Vorbis q5, métadonnées retirées). Dérivé : `assets/run021/audio/music_n4_forbidden_graveyard.ogg` (3 710 267 octets, SHA-256 `961e1e73…57cb2`, 185,274 s, 44,1 kHz stéréo, ~160 kb/s).

Mesures (ebur128 / ffmpeg) :

| Fichier | LUFS intégré | True peak | LRA |
| --- | --- | --- | --- |
| Source MP3 | −13,2 | +0,1 dBFS | 11,3 LU |
| Dérivé OGG N4 | −12,6 | −0,8 dBFS | 3,5 LU |
| Dreamer (N2/N3 actuel) | −12,8 | −1,1 dBFS | — |
| Menu lo-fi | −15,6 | −8,3 dBFS (crête) | — |

Le dérivé est à +0,2 dB de Dreamer : même niveau perçu que les autres niveaux. Le true peak mesuré (−0,8 dBFS) dépasse la cible −1,5 dBFS du loudnorm (réencodage Vorbis après limiteur dynamique) ; le Master a un limiteur dur et le volume nœud est −24 dB, donc sans conséquence pratique, mais à signaler.

### 1.3 Boucle

Analyse de la structure (RMS par fenêtre, autocorrélation d'attaques) : tempo ≈ 106,9 BPM ; intro avec montée de 0 à 5,56 s ; groove 1 de 5,56 à ~77 s ; pont calme ~77–113 s ; groove 2 ~113–185 s ; sortie en fondu dès ~185 s. Les deux grooves font 128 temps (32 mesures) et le pont 64 temps, ce qui confirme la grille.

- **Point de boucle :** début S = 5,564 s (le « drop » du premier groove, attaque nette), fin E = 185,274 s ; E − S = 179,710 s = 320 temps = 80 mesures. E a été choisi par corrélation croisée de la forme d'onde après E avec celle après S (pic à 0,45 à 185,274 s) pour tomber sur la même position rythmique.
- **Import :** `assets/run021/audio/music_n4_forbidden_graveyard.ogg.import` : `loop=true`, `loop_offset=5.564` (les autres musiques ont `loop=true`, `loop_offset=0` ; la valeur non nulle évite de rejouer l'intro en fondu à chaque tour). Import exécuté.
- **Raccord :** les 6 dernières millisecondes du fichier sont un fondu croisé vers les 6 ms qui précèdent S. Mesure sur le PCM décodé : saut de 192 et −138 (sur 32 768) entre le dernier échantillon et celui de S, contre des pas ordinaires jusqu'à 7 000–26 000 : pas de clic mesurable. Le fichier fait bien 185,274 s (la première version du script, sans coupe après loudnorm, créait 26 ms de silence/retard ; corrigée).
- **Limite honnête :** le raccord rythmique (320 temps) est vérifié par mesure ; la continuité musicale (fin de phrase du groove 2 vers le début du groove 1, avec le fill de ~182 s inclus) est un jugement d'écoute **en attente**. Extrait : `work/run021/audio/excerpt_n4_loop.ogg` (20 s : 10 s avant E puis 10 s après S, donc le raccord à 10 s).

### 1.4 Raccord dans la scène

Patch texte minimal de `scenes/forbidden_graveyard.tscn`, **une seule ligne** (ligne 59, `ext_resource` id `29`, référencé par un seul nœud `Music`, vérifié) :

```
- [ext_resource type="AudioStream" path="res://assets/music/music_slice_dreamer.ogg" id="29"]
+ [ext_resource type="AudioStream" path="res://assets/run021/audio/music_n4_forbidden_graveyard.ogg" id="29"]
```

Les lignes `ext_resource` de cette scène n'ont pas d'uid, donc aucune ligne uid à ajouter. Scène non ouverte dans l'éditeur ni réenregistrée ; `git diff --stat` : 1 insertion, 1 suppression. Les 6 fichiers du baseline humain ont été re-hachés après les opérations : identiques à `work/run021/human-baseline-sha256.json`. Les autres niveaux ne sont pas touchés.

### 1.5 Vérifications Godot (harnais verrouillé)

```
export GODOT_BIN="/mnt/c/Users/allen/OneDrive/Documents/Godot Engine/Godot_v4.7.2-stable_win64_console.exe"
bash work/run021/check.sh import-audio --headless --editor --import --quit      # import initial
bash work/run021/check.sh import-audio2 --headless --editor --import --quit     # après loop=true / loop_offset
bash work/run021/check.sh audio-check --headless --script res://tools/art/run021/audio_check.gd
```

Dernière exécution de `audio-check` : `RESULT checks=19 failures=0` ; journal `work/test-results/run-Dl5qMLLx/audio-check.log` (pointeur `work/run021/audio-check-results.txt`). Une exécution antérieure (`run-ranRSgxf`) avait aussi 19/19 mais a terminé par « 4 resources still in use at exit » (course à la sortie), corrigée par une attente avant `quit`. Une toute première exécution (`run-LeBsU4OI`) avait 2 échecs : le test supposait la musique mise en pause avec l'arbre ; le comportement réel est ci-dessous.

Contrôles couverts : flux = nouveau OGG ; bus `Music` ; volume −24 dB inchangé ; `loop=true`, `loop_offset=5.564`, durée 185,274 s ; entrée dans le niveau : lecture et une seule voix sur le bus Music ; `Ambient` joue à part sur le bus `Ambient` ; position qui avance ; passage de boucle (lancement 0,4 s avant la fin, position revenue à ~6,2 s) ; sortie du niveau (`_exit_tree` → plus aucune voix) ; nouvelle entrée (une seule voix) ; seconde sortie (aucune voix).

**Constat pause/reprise :** la racine de chaque niveau N3/N4 a `process_mode = 3` (ALWAYS), donc `Music` et `Ambient` continuent de jouer quand `get_tree().paused` est vrai (menu pause, modales, écran de mort). Ce comportement est identique aux autres niveaux avec Dreamer ; aucune reprise ni voix en double n'a été observée. Si l'humain préfère une musique atténuée ou muette pendant la pause, c'est une modification de `level.gd`/des scènes, propriété Codex, hors de ce lot. Le harnais est headless (pilote audio factice) : il prouve l'état des nœuds et les positions de lecture, pas ce qu'on entend.

### 1.6 Niveau de mixage

Mesures : musique −12,6 LUFS au fichier ; `volume_db` −24 dB sur le nœud ; bus Music 0 dB ; ambiance N4 `amb_forbidden_graveyard.ogg` −29,6 LUFS (crête −14 dBFS) à −8 dB sur le nœud ; SFX en crête −8 à −12 dBFS.

| Mix (simulation ffmpeg, extrait de 20 s) | LUFS intégré |
| --- | --- |
| Musique −24 dB + ambiance −8 dB (valeurs actuelles) | −33,8 |
| Musique −18 dB + ambiance −8 dB (proposition) | −29,5 |

Musique seule à −24 dB : ≈ −36,6 LUFS, soit environ comme l'ambiance (−37,6 LUFS), à plus de 20 dB sous les crêtes de SFX. L'humain avait déjà jugé la musique « trop basse » en RUN-014. **Valeur proposée, non appliquée : −18 dB pour la musique des quatre niveaux** (un changement cohérent, pas seulement N4), à confirmer à l'écoute. Volume conservé à −24 dB pour N4 dans ce lot. Extraits de mix : `work/run021/audio/excerpt_n4_ingame_mix_music-24dB.ogg` et `…-18dB.ogg` (ce ne sont que des simulations ffmpeg, pas le rendu du moteur).

### 1.7 Écoute humaine en attente (musique)

- Fond sonore, ambiance et humeur adaptés à Forbidden Graveyard ? (synthwave rétro 80s dans un cimetière : décision humaine déjà prise.)
- Raccord de boucle à 179,7 s : fin du groove 2 vers drop du groove 1.
- Niveau −24 dB ou −18 dB avec ambiance et SFX.
- Intro de 5,6 s (montée) à l'entrée du niveau.

## 2. Audit SFX (aucun remplacement appliqué)

### 2.1 Méthode

- Références : `grep` des `preload/load/ext_resource` dans `scripts/` et `scenes/`, puis lecture des chemins d'appel `play()`. Mesures : `work/run021/audio/sfx_measurements.tsv` (script `work/run021/audio/measure_sfx.sh` : durée, crête, RMS, centroïde spectral moyen, platitude spectrale moyenne ; sur de très courts sons, le LUFS n'est pas significatif). Centroïde élevé + platitude élevée = souffle/sifflement ; platitude très faible = son quasi pur (sinusoïde), typiquement « synthé/sci-fi ».
- Aucune écoute n'a été faite : les « défauts suspectés » sont des hypothèses d'après la mesure et les noms de familles (le pack Pixel Combat est un pack de design sonore synthétique : `Mecha`, `Laser`, `Zap`…).
- **Fichiers sur disque mais jamais joués** (ne sont pas des événements) : `sounds/jump.wav`, `hurt.wav`, `tap.wav` (aucune référence, hors `tools/build_level.gd` pour `time_for_adventure.ogg`, un générateur) ; `assets/music/time_for_adventure.ogg` (idem). `sounds/coin.wav` **est** joué (`gold_gate.gd` via `scenes/gold_gate.tscn`, nœud `Sound`).
- Les `.tres` `AudioStreamRandomizer` appliquent pitch ±4–8 % et volume ±1 dB.

### 2.2 Propriété des scripts

Codex : `scripts/player.gd`, `scripts/run019_enemy.gd`, `scripts/run019_enemy_attack.gd`, `scripts/keyboard_menu.gd`, `scripts/level.gd`, scripts de gameplay et UI. Pour ces scripts seul le changement de référence est **proposé** ; il est livré comme chemin de fichier à substituer. Les scènes (`player.tscn`, `coin.tscn`, `slime.tscn`) référencent aussi des sons mais relèvent de la scène : à traiter après remise explicite. Rien n'a été modifié.

### 2.3 Tableau événement → asset → mesure → défaut → proposition

Légende des décisions : **K** garder, **R** remplacer, **S** supprimer, **A** à écouter d'abord. Colonne « Lieu » : S = scène, G = script gameplay Codex. Mesures : durée (s) / crête (dBFS) / centroïde (Hz) / platitude.

**Priorité haute (discordant, répétitif ou signalé)**

| Événement | Asset réellement référencé (chemin d'appel) | Mesure | Défaut suspecté | Décision proposée | Justification | Candidat (licence) |
| --- | --- | --- | --- | --- | --- | --- |
| Saut | `sounds/sfx_player_jump.wav` (`player.tscn` `JumpSound` → `player.gd:332`) ; Bamboo Whip 005 | 0,22 / −8,0 / 1 696 / 0,12 | signalé trop sci-fi par l'humain ; « fouet » à glissando tonal, pas un effort physique | **R** | Un saut très fréquent doit être discret et physique : poussée de botte sur pierre | `run021/audio/sfx_candidates/cand_player_jump_01–03.wav` ← Pixel Combat `FEETMisc_STEP-Boots on Concrete Dungeon` 001/003/005, 0,18 s, −10 dBFS ; CC BY 4.0 ; 3 prises (à brancher en `AudioStreamRandomizer`) |
| Double saut | `sounds/sfx_player_double_jump.wav` (`DoubleJumpSound` → `player.gd:351`) ; Whoosh Sweep 005 | 0,30 / −8,0 / 3 621 / 0,19 | signalé trop sci-fi ; balayage synthétique | **R** | Souffle d'air bref qui distingue le 2ᵉ saut du 1ᵉʳ sans ton de synthé | `cand_player_double_jump_01–02.wav` ← `WHSH_MOVEMENT-Windy Passby` 002/004, 0,28 s, −10 dBFS ; CC BY 4.0 |
| Saut mural | `sounds/sfx_player_wall_jump.wav` (`WallJumpSound` → `player.gd:344`) ; Simple Whoosh 001 | 0,19 / −8,0 / 11 075 / 0,72 | souffle aigu (sifflement presque pur bruit) | **R** | Cohérence avec le nouveau saut : pied qui repousse un mur | `cand_player_wall_jump.wav` ← `FEETMisc_STEP-Hard Step` 004, 0,15 s, −10 dBFS ; CC BY 4.0 |
| Ramassage d'or | `sounds/sfx_gold_coin_pickup.tres` (3 prises Magic Coin) (`coin.tscn` nœud `Sound` → `coin.gd:54`) | 0,70 / −8,0 / ~12 000 / 0,43–0,51 | l'événement le plus répété du jeu ; queue de 0,7 s qui se chevauche, très brillant | **R** (raccourcir et ternir) | Pièces en rafale : sifflement répétitif | `cand_gold_coin_pickup_01–03.wav` ← `DSGNTonl_USABLE-Whimsy Coin` 001/002/005, 0,4 s, −10 dBFS (centroïde ~8 000) ; CC BY 4.0 |
| Potion mineure (ramassage) | `sounds/sfx_minor_potion_pickup.wav` (`potion_art.gd:5`, `drink.stream`) ; Bubble Babbler 001 | 0,50 / −8,0 / 682 / 0,055 | quasi sinusoïde grave : gémissement synthé, pas un liquide | **R** | Retour d'action utile mais caractère « laser » | `cand_minor_potion_pickup.wav` ← `DSGNTonl_USABLE-Fleeting Consume` 005, 0,5 s ; centroïde 2 981, platitude 0,16 ; CC BY 4.0 (**A** : candidat approximatif) |
| Potion majeure (ramassage) | `sounds/run018/sfx_major_potion_pickup.wav` (`major_potion_art.gd:6`) ; Bubble Babbler 005 | 0,80 / −8,0 / 261 / 0,012 | sinusoïde pure grave (la plus tonale du jeu) | **R** après choix du candidat potion mineure | Même défaut, plus marqué | Même famille Fleeting/Generic Consume, prise plus longue à choisir à l'écoute |

**Priorité moyenne (probable défaut ou répétition, à écouter avant décision)**

| Événement | Asset référencé (chemin d'appel) | Mesure | Défaut suspecté | Décision proposée | Justification | Candidat |
| --- | --- | --- | --- | --- | --- | --- |
| Tir d'arc | `sounds/sfx_weapon_bow_shot.tres` (`player.gd:106`, G) ; High Whoosh 001–003 | 0,38 / −10 / ~8 400 / 0,74 | souffle blanc aigu, pas de corde ; répétitif | **A** puis R | Substitut déjà reconnu (RUN-016) | Aucune corde dans le pack ; `SWSH_MOVEMENT-Bamboo Whip` ou `DSGNTonl_SKILL RELEASE-Small Bark` à comparer ; pas de candidat préparé |
| Lancer de couteau | `run018/sfx_weapon_knives_throw.tres` (`player.gd:119`, G) | 0,28 / −10 / ~11 000 / 0,77 | sifflement aigu répété | **A** puis R | Même profil que le tir d'arc | `SWSH_MOVEMENT-Reso Swish` autres prises / Windy Swipy ; non préparé |
| Éclats (shards) | `sfx_shard_gain.tres` (`coin.gd:11`) ; Star Sparkle | 0,55–0,58 / −10 / 4 300–6 400 / ~0,35 | scintillement « jeu mobile », répétitif | **A** | Non signalé ; événement fréquent | Garder si l'écoute est acceptable |
| Plante empoisonnée | `run019/sfx_poison_plant_hit.wav` (`poison_plant.gd:19`) ; Bubbly Zaps 005 | 0,60 / −8 / 1 057 / 0,066 | bourdonnement quasi pur, aspect électrique | **R** | Danger : doit sonner organique, pas synthé | `DSGNMisc_CAST-Slime Ball` autre prise ou `SKILL RELEASE-Wet Splash` ; non préparé |
| Incantation du Sorcerer | `run019/sfx_sorcerer_spell_cast.wav` (`run019_enemy.gd:230`, G) ; Mind Eraser 005 | 0,60 / −8 / 724 / 0,019 | quasi pure sinusoïde grave (note du RUN-019 : « très grave ») | **A** | Télégraphie du danger, à conserver ; défaut de timbre | Candidat à chercher dans `MAGSpel_CAST` (Hollow Spell, Energy Noise) ; à écouter |
| Trappe, hp-bonus, fin de bouclier, upgrade d'arme, porte | `sfx_trapdoor_trigger` (Mecha Lock In), `sfx_player_hp_bonus` (Mecha Level Up), `sfx_magic_shield_end` (Mecha Barrier Fail), `sfx_weapon_upgrade` (Mecha Upgrade Equip), `sfx_door_open` (Mecha Large Takeoff) | 0,4–1,1 / −8 à −10 / 1 800–11 000 | familles « Mecha » = ton robotique, hors direction dark fantasy | **A** | Retours de confirmation/danger nécessaires ; seul le timbre est en cause | Alternatives de forme : `MAGAngl_BUFF` (Buff Pickup, Effect Success), `UIMisc_INTERFACE-Lock`, `DSGNImpt_EXPLOSION-Thud` (grondement de porte) ; choix à l'écoute |
| Impacts de mêlée | `sfx_melee_hit.tres` (Gut Punch 003/006/005) (`slime.tscn`, `possessed_skull.gd`, `run019_enemy.gd:214`) | 0,35–0,41 / −8 / ~2 900 / 0,19 | déjà remplacé en RUN-014 ; reste partagé par tous les ennemis | **K** (**A**) | Retour d'action indispensable | — |
| Coup reçu par le joueur | `sfx_player_hit.tres` (Strong Smack) (`player.tscn` `HurtSound`) | 0,23–0,24 / −8 / ~3 500 / 0,33 | aucun défaut mesuré | **K** | Danger/confirmation : à conserver | — |

**Garder (aucun défaut mesuré) ou à écouter seulement**

| Événement | Asset référencé | Décision | Note |
| --- | --- | --- | --- |
| Mort du joueur | `sfx_player_death.wav` (Thud 001, 1,24 s, centroïde 2 303, platitude 0,16) via `player.tscn`/`player.gd:603` | **K** | Feedback de danger essentiel |
| Swing léger | `sfx_melee_swing_light.tres` (Sword Slash 001–003) via `player.gd:278` | **K**/**A** | Centroïde ~6 000, platitude ~0,5 : whoosh d'épée plausible |
| Swing lourd | `run018/sfx_melee_swing_heavy.tres` (`player.gd:121`) | **A** | Partagé par plusieurs armes |
| Mort du slime | `sfx_slime_death.tres` (`slime.tscn`) | **K** | Familier |
| Menu UI : navigate, confirm, cancel, error | `sfx_ui_*.wav` (`keyboard_menu.gd:33–36`) | **K** | Crête −12 dBFS, courts ; error/confirm plus aigus (9–10 kHz) à écouter |
| Refus de coffre | `run018/sfx_chest_reward_refuse.wav` (`keyboard_menu.gd:46`) | **K** | Retour de refus requis |
| Coffre : ouverture, révélation, acceptation, upgrade, rare | `sfx_chest_*`, `run018/sfx_weapon_upgrade.wav`, `sfx_chest_open_rare.wav` | **A** | Substituts connus (verrou) ; récompense, à conserver |
| Porte : paiement, déverrouillage | `run019/sfx_door_coin_payment`, `sfx_door_unlock` | **K** | Confirmation d'action |
| Ennemis RUN-019 (mort/attaque) | `run019/sfx_*` référencés par `run019_enemy.gd` | **K**/**A** | Seul le caractère tonal est suspect pour `skull_death` (10 kHz, risque de sifflement en groupe) |
| Pièges (piques, turret, plaque, bouton) | `run019/sfx_spikes_*`, `sfx_turret_*`, `sfx_pressure_plate_activate`, `sfx_button_activate` | **K** | Télégraphie de danger/action |
| Secret, shield, dialogue, spirit | `sfx_secret_reveal`, `sfx_magic_shield_activate`, `sfx_dialogue_open`, `sfx_spirit_appear` | **K**/**A** | Cues narratifs uniques |
| Porte d'or (hérité) | `sounds/coin.wav` (`gold_gate.gd:14`, scène `gold_gate.tscn`) | **A** | Provenance non établie (déjà noté dans les crédits) ; 0,20 s, crête 0 dBFS. Le plus fort du jeu (+8 dB vs −8 dBFS des autres) |

À retenir : `sounds/coin.wav` culmine à 0 dBFS alors que tous les autres SFX sont normalisés à −8 à −12 dBFS ; il est joué par la porte d'or. Aucune suppression n'est proposée sans remplacement : chaque retour de danger, d'action ou de confirmation reste couvert.

### 2.4 Bibliothèques externes et licences

- **Helton Yan, *Pixel Combat*** : dossier `SFX/Helton Yan's Pixel Combat - Single Files/` (2 101 fichiers, 350 familles). CC BY 4.0, crédit obligatoire (voir `assets/AUDIO_CREDITS.md`). Candidats préparés uniquement ici. Pack synthétique : peu de sons physiques (pas de corde d'arc, de bois, de grincement), d'où les substituts.
- **Minifantasy Dungeon SFX** (`SFX/Minifantasy_Dungeon_SFX/`, 62 fichiers : `01_chest_open`, `05_door_open`, `12_human_jump`, `11_human_damage`, `26_sword_hit`, `16_human_walk_stone`…) : stylistiquement le plus adapté (foley réel de donjon, saut, coffres, portes), mais **aucun fichier de licence dans le dossier** ; les crédits du projet notent déjà que la redistribution est interdite et que le dépôt est public. **Non utilisable sans nouvelle autorisation** ; non copié, non traité. Peut servir de référence d'écoute.
- **Shooter Synthwave Music Pack** (AlkaKrab) : musique, licence interdit la redistribution ; non pertinent pour les SFX.

### 2.5 Candidats préparés (non branchés)

10 WAV mono 44,1 kHz PCM 16 bits dans `assets/run021/audio/sfx_candidates/`, produits par `work/run021/audio/prepare_sfx_candidates.py` (pipeline `tools/prepare_audio.py` : silence retiré, fondu d'entrée 2 ms, plafond de durée avec fondu de sortie, crête normalisée). Sources copiées dans `assets/source/run021/audio/sfx/` ; hashes source et candidat dans `assets/source/run021/audio/sfx/provenance_sfx.json`. Import Godot exécuté (fichiers `.import` créés), aucune référence ajoutée dans `scripts/` ou `scenes/`. Comparaison A/B (actuel puis candidat, 0,5 s de silence entre) : `work/run021/audio/ab_sfx_current_then_candidate.ogg` dans l'ordre saut, double saut, saut mural, pièce, potion mineure. Candidats mesurés (durée / crête / centroïde / platitude) : saut 0,18 / −10,0 / ~850 / 0,10 ; double saut 0,28 / −10,0 / ~8 000–8 800 / 0,60–0,64 ; saut mural 0,15 / −10,0 / 3 329 / 0,31 ; pièces 0,40 / −10,0 / ~7 700–8 400 / ~0,52–0,60 ; potion 0,50 / −8,0 / 2 981 / 0,16.

Limites : le saut candidat est volontairement très grave (centroïde ~850 Hz, pas de souffle) et risque de sonner étouffé ; le double saut reste un souffle brillant (platitude élevée) : à juger à l'écoute. Le candidat potion est une hypothèse approximative.

### 2.6 Références proposées (à appliquer par le propriétaire du fichier, non appliquées)

| Fichier propriétaire | Référence actuelle | Référence proposée |
| --- | --- | --- |
| `scenes/player.tscn` `JumpSound` | `sounds/sfx_player_jump.wav` | randomizer sur `cand_player_jump_01–03.wav` (après promotion vers `assets/sounds/`) |
| `scenes/player.tscn` `DoubleJumpSound` | `sounds/sfx_player_double_jump.wav` | randomizer sur `cand_player_double_jump_01–02.wav` |
| `scenes/player.tscn` `WallJumpSound` | `sounds/sfx_player_wall_jump.wav` | `cand_player_wall_jump.wav` |
| `scenes/coin.tscn` | `sounds/sfx_gold_coin_pickup.tres` | `.tres` sur `cand_gold_coin_pickup_01–03.wav` |
| `scripts/potion_art.gd:5` | `sounds/sfx_minor_potion_pickup.wav` | `cand_minor_potion_pickup.wav` (après écoute) |

Les candidats doivent d'abord être promus de `assets/run021/audio/sfx_candidates/` vers le dossier de jeu retenu avec leurs crédits, une fois l'humain d'accord.

### 2.7 Écoute humaine en attente (SFX)

Tout. En priorité : saut, double saut, saut mural (candidats vs actuels, fichier A/B) ; pièce (rafale de 5–10 pièces) ; potions ; tir d'arc et couteaux ; plante ; incantation Sorcerer ; porte d'or (`coin.wav` à 0 dBFS) ; famille Mecha (trappe, hp-bonus, upgrade) ; mix musique/ambiance/SFX en jeu.
