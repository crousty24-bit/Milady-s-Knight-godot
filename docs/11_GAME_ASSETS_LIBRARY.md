
Procédure pour trouver, évaluer et intégrer des assets au projet.

### Checklist choix d'achat/téléchargement : 

1. **Pixel-art natif**, idéalement.
2. **Side-scroller/platformer** en priorité
3. Densité graphique proche de ta référence 16×16.
4. Personnage standard autour de ton échelle visuelle ~24×32, même si sa cellule est plus grande.
5. Spritesheets régulières et documentées.
6. Animations nécessaires présentes.
7. Sources Aseprite/PSD utiles lorsque disponibles.
8. Palette et contours compatibles avec ton Art Bible.
9. Licence autorisant usage commercial et modification.
10. Conditions IA vérifiées séparément.
11. Ne pas choisir un asset simplement parce qu'il est « redimensionnable ».
12. Tester **un seul sprite + un morceau de tileset dans le niveau 1 Godot avant d'adopter tout un pack**.

### Stratégie « pack → Astra → adaptation » :

- analyser les dimensions et spritesheets ;
- découper correctement les animations ;
- organiser et renommer les fichiers ;
- configurer l'import Godot ;
- adapter les animations au personnage ;
- harmoniser éventuellement certaines couleurs ;
- créer les ressources/scènes nécessaires ;
- vérifier l'échelle avec le niveau ;
- adapter les collisions indépendamment du sprite ;
- documenter la provenance et la licence.


### Workflow Assets agent possible :

ART_BIBLE.md
      ↓
assets/reference/
      ↓
Astra analyse les références
      ↓
création / adaptation de l'asset
      ↓
PNG source
      ↓
vérification dimensions / palette / pixel grid
      ↓
spritesheet propre
      ↓
import dans Godot
      ↓
animation + collision
      ↓
test dans le niveau 1
      ↓
correction

Et surtout, conserver deux catégories :

```
assets/source/
```

pour les fichiers originaux / références,

et :

```
assets/game/
```

pour les assets effectivement normalisés et utilisés par Godot.


---
### Assets

**Liste candidats Game Assets à intégrer :**

| Nom                                          | Type                                 | Catégorie                                                    | Liens                                                              | Prix            | Rating | DL  |
| -------------------------------------------- | ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------ | --------------- | ------ | --- |
| Tiny RPG Character Asset Pack 01 V2.0        | **Asset Pack**                       | **Characters, sprites, mobs, animation**                     | https://zerie.itch.io/tiny-rpg-character-asset-pack                | 2,50€ full pack | 🔴     | ❌   |
| Tiny RPG Character Asset Pack 02             | **Asset Pack**                       | **Characters, sprites, mobs, animation**                     | https://zerie.itch.io/tiny-rpg-character-asset-pack-02             | 2,50€ full pack | 🔴     | ❌   |
| Blood Demons                                 | **Asset Pack**                       | **Mobs, animations**                                         | https://immortal-burrito.itch.io/blood-demons                      | 2€              | 🟠     | ❌   |
| 2D Soulslike                                 | **Asset Pack, Plateformer, Tileset** | **Tile, sprites, characters, décors, doors, item, UI**       | https://samvieten.itch.io/2d-soulslike-metroidvania                | 5€ (promo)      | 🔴     | ❌   |
| 2D Metroidvania Tileset 16x16                | **Asset Pack**                       | **Tile, décors, item, mobs, biomes, palette couleurs**       | https://samvieten.itch.io/2d-metroidvania-tileset-16x16            | 5€ (promo)      | 🟠     | ❌   |
| Mine Tileset                                 | **Platformer, Tileset**              | **Tile, plateformes, décors, animation**                     | https://atomicrealm.itch.io/mine-tileset                           | 5€              | 🟠     | ❌   |
| Dark Series - Castle of Bones                | **Platformer Tileset**               | **Platformer, level design, décors, background**             | https://penusbmic.itch.io/the-dark-series-the-city-of-bones-tilset | 5€              | 🟠     | ❌   |
| Umbral Vault                                 | **Platformer Tileset**               | **Platformer, level design, décors, background**             | https://aethrall.itch.io/umbral-vault                              | 2€              | 🟡     | ❌   |
| Weapon Asset 16x16                           | **Asset Pack**                       | **Weapons, Sprites**                                         | https://dantepixels.itch.io/weapons-asset-16x16                    | Free            | 🟡     | ✅   |
| Pixel Fire Asset Pack                        | **Asset Pack**                       | **Animation, piège (flammes), décors**                       | https://devkidd.itch.io/pixel-fire-asset-pack                      | Free            | 🟠     | ✅   |
| Swordtember                                  | **Asset Pack**                       | **Weapons (swords)**                                         | https://thewisehedgehog.itch.io/hs2020                             | Free            | 🔴     | ✅   |
| 16x16 Assorted RPG Icons                     | **Asset Pack**                       | **Weapons, chest, potions, item, icons**                     | https://merchant-shade.itch.io/16x16-mixed-rpg-icons               | Free            | 🔴     | ✅   |
| RPG Effects 64x64                            | **Asset Pack**                       | **VFX, animations**                                          | https://bdragon1727.itch.io/1050-rpg-effects-64x64                 | Free            | 🟠     | ✅   |
| Raven Fantasy Icons                          | **Asset Pack**                       | **Icons**                                                    | https://clockworkraven.itch.io/raven-fantasy-icons                 | Free            | 🟠     | ✅   |
| Tool Assets 16x16                            | **Asset Pack**                       | **Tools, Sprites**                                           | https://dantepixels.itch.io/tools-asset-16x16                      | Free            | 🟢     | ✅   |
| Hallo Asset Pack                             | **Asset Pack**                       | **Tile, décors, item, mobs, animations, donjon, intérieurs** | https://crumpaloo.itch.io/whimsy-hallow                            | Free            | 🔴     | ✅   |
| Pixel RPG Health Bars - Classic Hearts 16x16 | **Asset Pack**                       | **Icon, heart, HP**                                          | https://yujii-arts.itch.io/pixel-rpg-health-bars-classic-hearts    | Free            | 🟡     | ✅   |


**Liste Game Assets d'inspiration visuelle/ conceptuelle :**

| Nom                                           | Type                   | Catégorie                                       | Liens                                                                                              | Rating | DL  |
| --------------------------------------------- | ---------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------ | --- |
| Free Plague Town 2D Platformer Vector Tileset | **Platformer Tileset** | **Platformer, level design**                    | https://craftpix.net/freebies/free-plague-town-2d-platformer-vector-tileset/ (+ 4 liens variantes) | 🔴     | ✅   |
| Free Top-Down Pixel Art Tileset               | **Tileset**            | **Utile pour décors/background + plante traps** | https://free-game-assets.itch.io/free-cursed-land-top-down-pixel-art-tileset                       | 🟠     | ✅   |
| Free Top-Down Pixel Dungeon Level Game Assets | **Tileset**            | **Level design, item, décors, pièges, coffres** | https://free-game-assets.itch.io/free-2d-top-down-pixel-dungeon-asset-pack                         | 🔴     | ✅   |
| Fantasy Skeleton Army                         | **Asset Pack**         | **Mobs, skeleton, top-down**                    | https://blpixelartist.itch.io/fantasyskeletonarmy                                                  | 🟠     | ✅   |
| 2D Platformer Tiles - Dungeon's End           | **Platformer Tileset** | **Platformer, level design**                    | https://gtajima.itch.io/2d-platformer-tiles-castle                                                 | 🟠     | ✅   |
