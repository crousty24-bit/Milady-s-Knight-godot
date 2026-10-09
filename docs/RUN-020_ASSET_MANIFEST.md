# RUN-020 — Manifeste de la contribution Claude (présentation minimale N2–4 et ambiances)

**5 octobre 2026 — contribution remise au root Codex pour raccord, recette et validation humaine.** Délégation : `work/run020/claude/IMPLEMENTATION.md`. Fichiers nouveaux uniquement ; aucune scène, aucun script commun, aucun fichier N1, aucun test ni document de workflow modifié ; aucune commande git. RUN-020 n'est pas DONE ; RUN-021 n'est pas commencée.

Orchestration : Opus 5.5 (principal : direction artistique, générateurs visuels, scripts de présentation, aperçus et revue) ; un sous-agent Sonnet 5.5 (`asset_integrator`, Medium demandé) pour la synthèse des ambiances, sur fichiers disjoints. L'outil n'expose pas de preuve du niveau de raisonnement appliqué.

## Provenance et licences

- **Visuels : originaux, générés par code**, sans pixel tiers ni génération d'image par IA, sur la palette commune `tools/art/palette.py` et les accents de biome de `tools/art/run020/palette_run020.py`. Les modules `tools/art/{pixel,palette,world_terrain,world_bg,world_props}.py` sont importés en lecture seule, non modifiés. Les générateurs sont la source des PNG ; les WAV sources sont conservés dans `assets/source/run020/`.
- **Ambiances : originales, synthétisées par code** (Python stdlib, graines fixes), sans audio tiers ni service externe. La bibliothèque locale (`.local/asset-paths.md`) n'était pas accessible depuis cette session (accès refusé hors du dépôt) : aucune piste externe n'a été sélectionnée.
- **Crédits intégrés par le root** :
  - `assets/VISUAL_CREDITS.md` : « RUN-020 : `assets/run020/**` généré par `tools/art/run020/biomes_run020.py` (original, projet ; réutilise des accessoires N1 de `assets/sprites/`). »
  - `assets/AUDIO_CREDITS.md` : « RUN-020 : `assets/sounds/run020/amb_*.ogg`, dérivés des WAV sources, synthétisés par `tools/art/run020/ambience_run020.py` (original, projet, aucune source tierce). »

**Régénération** (Python3 pour les sources, ffmpeg pour les OGG ; déterministe ; MD5 identiques vérifiés sur deux passages pour les 24 PNG et les 3 WAV) :

```
python3 tools/art/run020/biomes_run020.py [--preview DIR]
python3 tools/art/run020/ambience_run020.py --ogg
```

## Choix artistiques (jugement humain requis)

| Niveau | `world_level` | Accents | Terrain | Fond (ciel / lointain / proche) |
| --- | --- | --- | --- | --- |
| N2 Blight Town | 2 | brun putride / olive sourd (**proposition**, non prescrite par docs/06) | maçonnerie N1 avec mousse de pourriture olive et teinte boue (`terrain_campaign.png` thème 0) | lune voilée jaune-gris, brume olive ; village et clocher penchés, fumées ; maisons condamnées, gibet, arbres morts |
| N3 Black Forest | 3 | bleu nuit / vert froid (docs/06) | terre tassée, pierres et racines, rebord de mousse froide clair (thème 1) | lune pâle froide ; crêtes de pins ; grands pins et troncs nus |
| N4 Forbidden Graveyard | 4 | violet désaturé / cyan spectral grisé (docs/06) | **`terrain_stone.png` thème 0 inchangé** pour que le mur secret RUN-019 corresponde ; touffes et vrilles violet-gris propres à N4 | lune cyan grisé ; colline aux croix, chapelle ; mausolée, saule mort, grille en fer |

- Saturations réservées : aucun cyan saturé (Shield), aucun violet saturé (shards), aucun or (coins), aucun rouge vif (danger/Red Slime) dans le décor. Lumières chaudes rares (lanternes N2), lueur froide basse opacité (bougies N4).
- Limite connue : en N4, la maçonnerie conserve sa mousse verte N1 (contrainte du mur secret). Une variante teintée exigerait de régénérer `env_secret_wall.png`, hors périmètre.
- Les ennemis RUN-019 sont réutilisés sans variante visuelle (exemples Orc/Goblin/Fury Bats de docs/06 non introduits).

## Fichiers livrés

### Scripts (`@tool`, rendu pur, aucune collision créée)

| Script | Nœud attendu | Exports | Comportement |
| --- | --- | --- | --- |
| `scripts/campaign_backdrop.gd` | remplace le script de `Backdrop` | `world_level` (2–4), `reference_top` (−74) | ciel fixe à l'écran, nuages N1 et brume N1 teintés, bandes lointaine (×0,08) et proche (×0,3), remplissage sous la bande proche, poussières lentes très sombres. Même cadrage que `backdrop.gd` (sol 144, caméra haut −74). |
| `scripts/campaign_terrain_skin.gd` | remplace le script de `TerrainSkin`, frère de `Terrain` | `world_level` | même masque d'exposition, ombrage en profondeur et règles de touffes/vrilles que `terrain_skin.gd` ; atlas et ligne de thème selon le niveau (tableau ci-dessus). |
| `scripts/campaign_decor.gd` | nouveau `Node2D` `Decor`, frère de Player/Coins/Enemies, **après `Backdrop`, avant `Terrain`/`TerrainSkin`** | `world_level`, `level_width` (mettre 2800/3200/3600), `spacing` (72), `avoid_margins` | place les accessoires de façon déterministe sur les surfaces réelles de `Terrain` : largeur entière posée sur un même rang d'au moins 4 cellules, hauteur libre au-dessus, marges autour de `Enemies` 12, `Hazards` 20, `Items` 24, `ExitArea` 24, `Exploration` et `GoldGate` 64 px (rien près des murs secrets/portes). Les coins ne sont pas évités : ils se dessinent par-dessus ce décor sombre. Suit automatiquement les changements de layout ; aucun panneau ni comptage. N2 : teinte vers la pourriture vers la sortie selon `level_width`. |

Raccord final pour chaque scène : `Backdrop.script = campaign_backdrop.gd`, `TerrainSkin.script = campaign_terrain_skin.gd`, nouveau `Decor` (`campaign_decor.gd`), et `world_level` identique à celui du niveau sur les trois nœuds.

### Textures (`assets/run020/`, PNG RGBA, imports par défaut du projet : sans perte, nearest global)

| Fichier | Taille | Contenu |
| --- | --- | --- |
| `terrain_campaign.png` | 256×576 | 2 thèmes × 18 lignes × 16 masques, tuiles 16×16 (N2, N3) |
| `tufts_campaign.png` / `vines_campaign.png` | 128×36 / 128×72 | 8 variantes × 3 lignes (N2, N3, N4), cellules 16×12 / 16×24 |
| `bg_<biome>_sky.png` ×3 | 640×360 | ciel fixe |
| `bg_<biome>_far.png` ×3 | 640×170 | bande lointaine, raccord horizontal sans couture |
| `bg_<biome>_mid.png` ×3 | 512×132 | bande proche, raccord horizontal sans couture |
| `blight_town_{barrels,rot_mound,well}.png` | 30×22, 32×14, 30×34 | accessoires N2 |
| `black_forrest_{pine,stump,rock,fungus}.png` | 48×100, 24×14, 28×16, 16×10 | accessoires N3 |
| `forbidden_graveyard_{mausoleum,willow,cross,fence,candle}.png` | 60×62, 64×84, 18×34, 48×24, 8×14 | accessoires N4 |

Accessoires N1 réutilisés (légèrement teintés par biome) : N2 maisons, puits, charrette, gibet, clôture, lanterne, gravats, os, arbre mort ; N3 arbres N1, arbre mort, buisson ; N4 tombes a/b/c, os, arbre mort.

### Ambiances (sources `assets/source/run020/`, dérivés `assets/sounds/run020/`)

| Fichier | Format | Crête / RMS | Contenu |
| --- | --- | --- | --- |
| `amb_blight_town.wav` | mono 22,05 kHz 16 bits, 28 s, boucle `smpl` 0–617399 | −13,0 / −29,6 dBFS | vent bas en rafales, hurlement creux, craquements de bois, bulles sourdes |
| `amb_black_forrest.wav` | idem | −13,0 / −30,7 dBFS | bruissement de feuilles, vent faible, grillons ~1,65–1,9 kHz très bas, deux hululements, brindilles |
| `amb_forbidden_graveyard.wav` | idem | −13,9 / −28,0 dBFS | vent froid, sifflement résonant lent, nappe grave 55–110 Hz, deux cloches lointaines filtrées, souffles |

Raccord final : WAV PCM conservés comme sources ; conversion ffmpeg Vorbis (`-q:a 4`), mono22 050Hz, durée28s, OGG importés avec `loop=true`. `AudioStreamPlayer` `Ambient`, bus Ambient, −8dB, démarré/arrêté par le niveau. Le générateur écrit les WAV sources et encode les OGG avec `--ogg` (ffmpeg requis). Les mesures du tableau concernent les sources PCM.

**Musique** : aucune nouvelle piste (bibliothèque inaccessible, aucun achat/téléchargement). Choix concret : conserver `music/music_slice_dreamer.ogg` (Pixabay, licence documentée) sur N2–4, bus Music, `volume_db = -24.0` sur N2–4 ; l'identité de chaque niveau passe par son ambiance. Défendable pour N2–3 (« Early Kingdom » partagé, docs/07) ; pour N4, `music_graveyard_caves` (P1) reste ouvert à une sélection humaine dans la bibliothèque.

Le root a résolu la livraison initiale en WAV en produisant les OGG attendus. Identifiant `amb_black_forrest` (graphie canon docs/03) au lieu de `amb_black_forest`. Sons P0 : ceux de RUN-018/019 suffisent, aucun nouveau P0 requis par cette contribution.

## Vérifications réellement exécutées

- Générateurs : 24 PNG et 3 WAV, MD5 identiques sur deux passages ; tailles et type RGBA relus dans les en-têtes PNG.
- WAV : en-têtes relus (PCM mono 22 050 Hz 16 bits, `smpl` une boucle avant 0–617399) ; crête/RMS/raccord mesurés par `work/run020/claude/audio/measure.py` (notes `work/run020/claude/audio/NOTES.md`).
- Aperçus hors Godot (`work/run020/claude/compose_preview.py`, `level_preview.py`) : décodent le `tile_map_data` réel des trois scènes du worker et les positions des nœuds de gameplay, reproduisent les règles de `campaign_terrain_skin.gd`/`campaign_decor.gd` et rendent des vues 640×360 (×2) dans `work/run020/claude/preview/` avec chevalier, coins, Slimes, squelettes, plante, tourelle, piques, Shield et portes réels. Inspection : coins, ennemis, piques, plantes, tourelles et portes restent lisibles ; décor N2 18, N3 29, N4 35 accessoires placés sur les layouts du moment.
- **Recette root après intégration :** import Godot4.7.2 ; pilote natif `tests/run020_visual.gd` **33/33**, 12 captures640×360, ambiances actives sur Ambient et passage réel de fin de boucle. Revue Claude Opus5.5 en lecture seule des 12 captures et des références finales : aucun défaut bloquant concret. Preuves `work/run020/visual-final.log`, `work/run020/claude/native-review.json`. L’écoute et la validation artistique humaines restent attendues.

## Limites et suites

- Le placement du décor dépend du layout : vérifié sur les captures natives finales ; toute modification ultérieure des scènes exige une nouvelle inspection. Les premiers aperçus Python restent une approximation.
- Les fosses montrent la couleur de remplissage du fond ; à juger en jeu.
- Décor N2 clairsemé dans les zones de pièces/ennemis ; `spacing` permet de densifier.
- Jugement humain : palette N2, lune N4 cyan grisé, densité du décor, mousse verte de la maçonnerie N4, niveau et caractère des ambiances, réutilisation de *Dreamer*.
- Pilote natif écrit par le root : `tests/run020_visual.gd`, vues spawn/piège/combat et trois vues d’exploration N4 ; il déplace explicitement le joueur pour capturer et ne prouve pas un parcours naturel. Celui-ci est exercé séparément par `tests/run020_routes.gd`.
