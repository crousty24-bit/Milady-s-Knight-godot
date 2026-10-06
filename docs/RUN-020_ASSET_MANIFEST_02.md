# RUN-020 — Manifeste Claude de la reprise (level design N2–4 et élites)

**6 octobre 2026.** Exécution du [contrat de reprise](RUN-020_CLAUDE_HANDOFF_02.md) par Claude Code Opus5.5 (main), avec un sous-agent Sonnet5.5 (profil `visual_architect`) pour les élites, sur des fichiers disjoints. Branche `feature/run-020-021-campaign`, après le checkpoint technique Codex (recette composée 2225 PASS). RUN-020 reste **ACTIVE** : ni la recette Codex sur les nouvelles scènes, ni le playtest humain n’ont eu lieu. Aucun commit, push, PR ou merge ; aucune source externe modifiée.

## 1. Gabarit retenu

Références physiques mesurées dans `scripts/player.gd` : apex du saut ≈42 px, double saut ≈75 px au total, 105 px/s, double saut disponible seulement après un saut au sol. Règles d’auteur appliquées : montée ≤32 px en saut simple, ≤64 px en double saut, trou plat ≤48 px en simple, ≤96 px en double. Tunnels d’au moins 48 px de haut pour un corps de 18 px. Les murs restent grippables (couche 4) mais **aucun passage n’exige de saut mural**.

| Niveau | Avant : largeur / hauteurs de sol | Après : largeur (écrans 640) | Hauteurs praticables | Surface praticable atteinte |
| --- | --- | --- | --- | --- |
| N2 Blight Town | 2800 / y112–176 | 3840 (6,0) | y36–240, écart 204 px | ≈4585 px contre ≈2624 |
| N3 Black Forest | 3200 / y112–176 | 4320 (6,75) | y−48–240, écart 288 px | ≈4783 px contre ≈2992 |
| N4 Forbidden Graveyard | 3600 / y112–176 + 2 salles | 4800 (7,5) | y−16–240, écart 256 px | ≈6767 px contre ≈3392 |

L’emprise explorée double par la largeur (+37 à +35 %) **et** surtout par les étages : la longueur de surfaces atteintes augmente de 1,6× à 2×, sur trois à quatre fois la hauteur utilisée auparavant. Pas de couloir vide ajouté : chaque section porte une montée, un franchissement ou une décision. La caméra, les limites et `void_y` 304 sont inchangés (camera Rect2(0,−224,W,528)). Le repère « double » n’est pas une dimension validée par l’humain ; le temps de parcours n’a pas été mesuré.

Langage spatial commun : chaque niveau a **deux fourches** (F1, F2). Une route haute (remparts, canopée, chapelle) et une route basse (chemin de halage, sous-bois, crypte, catacombe) se rejoignent. Tomber d’une route haute ramène sur la route basse, jamais dans le vide, sauf au-dessus des failles explicitement mortelles. Les routes basses exposent davantage aux pièges et aux mêlées ; les routes hautes aux tireurs et aux sauts. Une pièce sur trois environ est placée sur une caisse, un arc de saut ou un rebord, au lieu d’une rangée au sol.

## 2. Plans cotés

Coordonnées en pixels monde ; `y` désigne la surface sous les pieds (le spawn reste `(48,144)`, la porte finale `(W−144,144)`).

### N2 Blight Town — W 3840, sortie 18, 24 pièces

| Section | x | Contenu et passage obligatoire |
| --- | --- | --- |
| S1 Faubourgs | 0–1008 | caisse y112, piques fixes x432, cour surélevée y112 (x480–704), piques rétractables x864 ; Green, Purple |
| F1 Brèche du canal | 1008–1600 | tour y112 = point de fourche visible. **Haut** : remparts brisés y80/48/48/64/96 (trous de 32–48), Purple. **Bas** : chemin de halage y240, voûte (plafond y176–192) avec **coffre commun** x1232 et deux Red, trou de 48 au-dessus de l’eau, piques rétractables x1440, marches y208/176 |
| S2 Marché | 1600–2400 | **première trappe** x1728 sur fosse à piques (y208, sortie au double saut), puits, caisses, puis le **toit de la halle y64 est le seul passage** (mur de 80 px au sol) ; Green sur le toit, Red à la descente |
| F2 Colline de l’église | 2400–3168 | terrasse y112 commune. **Haut** : chaussée y48 coupée par un trou de 48, piques fixes x2896, **potion mineure** x2976, Purple. **Bas** : ruelle avec tronçon enfoncé y176 à deux piques rétractables déphasées, deuxième trappe x2944 sur fosse à piques, Red |
| S3 Place de la peste | 3168–3696 | arène plate de 464 px, corniche de tir y80 (x3312–3392), **Bloated** x3456 patrouille ±72, porte 18 |

Pièces : tronc commun 17, F1 haut 2 / bas 2, F2 haut 1 / bas 2. Passage unique le plus pauvre : **20** (marge 2) ; le plus riche : 21 ; les 24 avec retour en arrière (les deux fourches sont parcourables dans les deux sens). Acteurs : 10 (2 Green, 3 Purple, 4 Red, 1 Bloated), contre 7. Pièges : 4 piques fixes, 4 rétractables, 2 trappes.

### N3 Black Forest — W 4320, sortie 25, 32 pièces

| Section | x | Contenu et passage obligatoire |
| --- | --- | --- |
| S1 Lisière | 0–1200 | tronc couché y128, creux y176 avec plante, piques fixes x688, **premier trou mortel de 48** (x832–880), piques rétractables x1120 ; Green, Purple, Red |
| F1 Canopée / sous-bois | 1200–2048 | tronc y112 = fourche. **Haut** : branches y80→48→16→16→48→80, Purple et **Archer** sur branche (x1704, y16). **Bas** : creux de ronces y176 avec **coffre commun** entre deux plantes, tronc géant y96 (Red dessus), Warrior |
| S2 Ravin | 2048–2800 | **Magic Shield** x2176 avant le ravin ; faille mortelle franchie sur trois souches y128/96/112 (trous de 48), falaise est y128 battue par une **tourelle** (x2678, tir vers l’ouest), montée sur l’éperon y96 |
| F2 Couronnes / ravine | 2800–3760 | **Haut** : couronnes jusqu’à **y−48** avec **potion mineure** au sommet, Archer, Green. **Bas** : ravine de racines y240, trappe sur fosse à plante x3088, deux piques rétractables déphasées, Red, Warrior, sortie par marches y192/160 |
| S3 Clairière | 3760–4176 | butte y112 avec Archer, plante x4000, Warrior devant la porte 25 |

Pièces : tronc commun 22, F1 3/3, F2 2/2. Passage unique : **27** (marge 2), 32 avec retours. Acteurs : 13 (2 Green, 2 Purple, 3 Red, 3 Warrior, 3 Archer), contre 10. Pièges : 5 plantes, 3 rétractables, 1 pique fixe, 1 trappe, 1 tourelle.

### N4 Forbidden Graveyard — W 4800, sortie 32, 40 pièces, porte optionnelle 4

| Section | x | Contenu et passage obligatoire |
| --- | --- | --- |
| S1 Entrée du cimetière | 0–1040 | tombes, marche y112, **mausolée à arche** (toit y64, passage dessous) ; depuis le toit, mur `n4_secret_01` x568 y64 ; salle secrète (x560–752, intérieur 32 px) avec **potion majeure** x640 et **rare chest** x704, au-dessus du chemin ; piques x816 ; Red, Warrior, Archer sur haute tombe |
| F1 Chapelle / crypte | 1040–2000 | **Haut** : marches y96/64, sol de chapelle y48 avec Sorcerer, **porte à 4 coins** x1544 menant à la salle **HP bonus `n4_hp_01`** x1640 ; on continue par le toit de cette salle (y−16, double saut de 64) puis y16/48. **Bas** : cour de crypte y240, trappe sur fosse à piques x1696, **coffre commun** x1824, Red, Warrior, sortie y192 |
| S2 Champ des crânes | 2000–2720 | **Magic Shield** x2048 ; tombes et crypte surélevée y96 avec un second Sorcerer ; **SkullSwarm** (2368,48), zone 480×240, quatre emplacements par tentative |
| F2 Surface / catacombe | 2720–3680 | **Haut** (surface y144) : puits d’entrée et de sortie à sauter, tombe, deux plantes, **potion mineure** x3200, mausolée y80 (double saut de 64) avec tourelle vers l’ouest et Archer dessus. **Bas** : catacombe y240 haute de 64 px, trappe sur fosse à piques, piques rétractables, deux Warriors ; sortie par corniche y192 |
| S3 Clocher et arène | 3680–4656 | montée obligatoire y96→48→0 jusqu’au **bouton** (4048,0), sous un Archer ; redescente vers la **porte mécanique** (4168,144), cloison x4160–4176 fermée jusqu’en haut ; piques rétractables x4224 ; arène avec corniche y80, **Chud** x4480 ±64 ; porte 32 |

Pièces : tronc commun 32, chaque route de fourche 2. **Tout passage simple donne 36 pièces** : sortie 32 + porte 4, sans secret ni coffre ; 40 avec retours. Aucune pièce derrière la porte payante ni dans la salle secrète. Acteurs : 14 (3 Red, 5 Warrior, 3 Archer, 2 Sorcerer, 1 Chud) + swarm4, contre 11. Pièges : 3 piques fixes, 2 trappes, 2 plantes, 2 rétractables, 1 tourelle.

## 3. Contrôle hors moteur des accès

`work/run020/claude-feedback/level_check.py` (aide d’auteur, non commitée car sous `work/`) simule les sauts image par image avec les constantes du joueur, contre les cellules et les corps solides (piques, plantes, tourelles, trappes fermées, portes, mur secret, grille), sans saut mural. Résultat (`level_check.log`, cartes `maps/map_n2–4.png`) :

- N2 24/24, N3 32/32, N4 40/40 pièces atteignables ; coffres, potions, Shield, bouton et swarm atteignables ; grille finale atteinte ;
- N4, portes fermées : sortie **inaccessible** sans le bouton, salle secrète et salle HP inaccessibles ; avec seulement la porte mécanique ouverte, sortie et 40 pièces accessibles ;
- génération répétée dans un dossier temporaire : scènes identiques octet pour octet au dépôt.

C’est une indication géométrique : le parcours clavier réel dans Godot reste à prouver par Codex.

## 4. Points de passage pour Codex

Liste complète des nœuds et positions : `work/run020/claude-feedback/nodes.txt`. Repères de parcours principaux (pieds du joueur) :

- **N2** : (240,112) caisse → (592,112) cour → (1032,112) tour/fourche → haut (1216,48)(1344,48)(1472,64)(1584,96) ou bas (1080,192)(1232,240) coffre (1336 saut) (1528,208) → (1664,144) → saut de trappe (1728) → caisses (1928,112) → toit de halle (2060,64)…(2290,64) → (2350,144) → terrasse (2472,112) → haut (2600,48)(2820,48) potion (2976,48) ou bas (2700,176)(2944 saut)(3056,144) → arène (3330,144), corniche (3352,80) → grille (3696).
- **N3** : (256,128) → creux (480,176) → saut de faille (856) → tronc (1224,112) → haut (1312,80)(1424,48)(1552,16)(1704,16)(1840,48)(1960,80) ou bas (1536,176) coffre (1712,96) → Shield (2176,144) → souches (2288,128)(2368,96)(2448,112) → (2600,128) → éperon (2744,96) → haut (2880,48)(2992,16)(3112,−16) potion (3248,−48)(3376,−16)(3504,16)(3616,48) ou bas (2824,176)(3000,240)(3088 saut)(3688,192)(3736,160) → butte (3880,112) → grille (4176).
- **N4** : marche (376,112) → toit (472,64), mur secret à frapper vers x568 → (1064,176) ou marches (1120,96)(1248,64) → chapelle (1440,48), porte payante (1544) puis HP (1640,48), toit (1600,−16) → (1776,16)(1896,48) ; ou crypte (1376,240)(1824,240) coffre (1976,192) → Shield (2048,144) → crypte (2368,96) → surface (2976,112)(3200,144)(3416,80) ou catacombe (2896,240)(3440,240)(3520,192) → (3600,144) → clocher (3808,96)(3920,48)(4048,0) **E** → (4100,144) → porte (4168) → arène (4360,80) → grille (4656).

Comptes changés pour les tests : ennemis 10/13/14, pièges 10/11/10, nœuds `Trapdoor2` (N2, N4) et `Turret1` conservés selon les noms historiques. Noms/chemins conservés : `CommonChest`, `MinorPotion`, `MagicShield`, `RareChest`, `MajorPotion`, `HpBonus`, `SecretWall`, `CoinDoor`, `MechanismDoor`, `MechanismButton`, `SkullSwarm`, `GoldGate`, `ExitArea`. Exécution de `tests/run020_campaign.gd` sur les nouvelles scènes, fichier non modifié : 159 PASS / 19 FAIL, tous attendus car les valeurs sont codées en dur (populations, coordonnées des fixtures (544,48), (1280,48), (2640,144), (1424,48), (640,48), (2016,144), occlusion et échecs en cascade). `run020_routes.gd` non exécuté : son pilote suit l’ancienne géométrie.

## 5. Élites Bloated Slime et Chud Blob

Le sous-agent a redessiné les deux élites à densité native avec `tools/art/run020_feedback/elites.py` : pas d’agrandissement, d’étirement ni de marges artificielles. Les sorties sont `assets/run020_feedback/enemies/{bloated_slime,chud_blob,vfx_bloated_burst}.png`. Les imports sont identiques à RUN-019 (nearest, sans mipmaps). Les feuilles RUN-019 restent en place.

| Sprite | Cellule / frames | Silhouette opaque mesurée | Pivot |
| --- | --- | --- | --- |
| Chevalier idle (référence, épée et cape incluses) | 64×64 | 36×34 (corps Art Bible ≈24×32) | pieds |
| Ancien Bloated | 40×32, 20 | 30×27 (crawl 29–34 × 23–30) | (20,32) |
| **Nouveau Bloated** | **72×56, 20** | crawl 49–57 × 45–51 ; swell 57–63 × 49–55 ; hit 51–59 × 45–50 ; death jusqu’à la flaque | (36,56) |
| Ancien Chud | 48×36, 26 | 33×29 | (24,36) |
| **Nouveau Chud** | **96×64, 26** | idle 58–59 × 48–49 (corps ≈38 de large) ; windup jusqu’à 60 de haut ; slam 63–67 × 46–52 | (48,64) |
| Éclatement Bloated | 112×48, 6 | gerbe au sol, centre x56 | bas-centre |

Les deux silhouettes font environ 1,5× la hauteur du chevalier. Noms, nombres de frames et cadences sont inchangés : Bloated crawl/swell (0,29 s)/hit/death ; Chud idle/walk/windup (0,3 s, égal à `windup_duration`)/slam/hit/death. Les pieds reposent sur la dernière rangée de chaque frame, journal `work/run020/claude-feedback/elites/bbox_check.log`.

**Bloated** : masse putride gonflée, pustules dont deux crevées, gros œil terne, gueule de crocs, crâne à demi digéré. **Chud** : brute voûtée, mêmes chair gris-vert et yeux rouges, côtes, coutures, éperons violets et couperet rouillé tenu dans un poing énorme. Le couperet porte environ 27–30 px devant le centre, ce qui correspond à la portée logique de 28 px.

Modification de code : seulement la présentation en fin de `scripts/run019_enemy.gd`, soit les lignes `SHEETS` de Bloated et de Chud, `BURST_FX` et la taille de l’effet d’éclatement. Aucune logique d’aggro, d’attaque ou de dégâts n’est touchée. Suite `run019_enemies` : 82/82.

**Collisions, non modifiées et à arbitrer par Codex** : le corps reste à 20×22 et ne couvre que le bas des sprites. Le contact du Bloated se déclenche sous 18 px d’origine à origine, alors que sa demi-largeur visuelle est de 25–28 px. Le joueur pénètre donc d’environ 7 px dans l’image avant d’être touché, et à cette distance l’élite masque le chevalier, qu’elle recouvre dans l’ordre de dessin. Aucun défaut physique n’est démontré, mais l’écart visuel est réel.

## 6. Autres fichiers et provenance

- `tools/build_run020.py` : réécrit en plans explicites (`Plan`, sections commentées, plus de placement automatique des pièces). Il ne touche pas au N1. Les rangées d’atlas sont calculées d’après l’exposition réelle des cellules.
- `scenes/blight_town.tscn`, `black_forrest.tscn`, `forbidden_graveyard.tscn` : régénérées par cet outil.
- `scripts/campaign_decor.gd` : les corniches minces (moins de trois rangées pleines) ne reçoivent plus que des accessoires de 20 px de haut au plus. Les maisons, arbres et mausolées ne flottent plus sur les remparts et les branches. C’est du dessin pur, sans règle de jeu.
- `tools/art/run020_feedback/capture_levels.gd` et `capture_elites.gd` : scripts de capture, plus les utilitaires `pngio.py`, `board.py` et `crops.py`.
- `assets/VISUAL_CREDITS.md` : entrée ajoutée. Tout est original et procédural, sans pixel tiers ni IA d’image.

## 7. Vérifications réellement exécutées

Toutes les exécutions ont utilisé Godot4.7.2 Windows via `work/run020/check.sh` : verrou `work/.godot.lock` et profil NTFS isolé, sans toucher à la sauvegarde humaine.

- **Import** : `--headless --import`, code0, aucune erreur.
- **Captures natives** : 640×360, 29 vues de route (10 N2, 9 N3, 10 N4), 58/58 contrôles dans `work/run020/claude-feedback/native/`, dernier passage `work/test-results/run-eoiJm9ER/`. Elles couvrent les fourches, la verticalité, chaque récompense et mécanisme, la swarm, les dangers et les deux élites à côté du joueur. Le joueur est placé par code et les acteurs tournent 40 images : ces captures ne prouvent pas le parcours naturel.
- **Captures élites** : 20/20 contrôles dans `work/run020/claude-feedback/elites/native/` (poses forcées) et planche avant/après ×4 dans `elites/compare_board_x4.png`.
- **Suites non modifiées** : `run019_enemies` 82/82, `run019_integration` 42/42, `run019_exploration` 27/27, `run019_traps` 55/55, `integration` 24/24, sans échec ni fuite. `run020_campaign` 159/178, voir §4.
- **Relecture des vues** : lisibilité des pièces, du terrain praticable, des télégraphies et des élites jugée correcte par Claude ; décor flottant corrigé puis recapturé. Ce n’est pas une validation humaine.

Non exécutés : la recette complète `tools/test.sh`, le pilote de parcours, `run020_visual.gd` et le jeu au clavier.

## 8. Remise et décisions humaines

**Remise à Codex** : les éditions sont arrêtées. Fichiers remis : les trois scènes, `tools/build_run020.py`, `scripts/campaign_decor.gd`, la présentation de `scripts/run019_enemy.gd`, `assets/run020_feedback/`, `tools/art/run020_feedback/`, `assets/VISUAL_CREDITS.md` et ce manifeste. Il reste à Codex :

- adapter `run020_campaign`, `run020_routes`, `run020_visual` et le guide de playtest à la nouvelle géométrie ;
- vérifier le parcours clavier N1–4 et ses variantes ;
- vérifier budgets, achats et refus, ainsi que mort, restart et reprise ;
- vérifier les collisions des élites et lancer la recette complète.

**À juger par l’humain** :

- variété, densité et ennui ;
- absence de raccourci dominant ;
- confort des doubles sauts de 64 px (halle N2, toit HP N4, mausolée N4) et du trou mortel de 48 px en N3 ;
- difficulté graduelle avec 10/13/14 acteurs ;
- espaces de tir face aux Archers ;
- lisibilité de la salle secrète, dont l’intérieur est visible de l’extérieur comme dans la première passe ;
- taille et design des élites, et masquage du joueur au contact ;
- temps de parcours, à mesurer.

Aucune apparence n’est déclarée validée.
