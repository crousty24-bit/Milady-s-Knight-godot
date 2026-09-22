# Milady's Knight — Visual Asset Requirements

> **Objectif :** inventorier tous les assets graphiques nécessaires au jeu indépendamment de leur provenance.
> Ce document définit **ce qu'il faut produire ou trouver**, et non quel asset pack sera utilisé.
> Ce document doit être complété durant la phase de planification puis à mis à jour régulièrement.

## Statuts

- ⬜ À prévoir
    
- 🟡 Asset trouvé / à adapter
    
- 🟠 En production / adaptation
    
- 🟢 Prêt
    
- ✅ Intégré et validé
    

## Priorités

- **P0** : indispensable au gameplay / première version jouable
    
- **P1** : nécessaire au rendu final
    
- **P2** : polish / amélioration visuelle
    

---

## Visual Asset Requirements

| **Catégorie**          | **Élément**                      |                          **Visual Asset Set** |                                                    **Variantes** | **Animations requises** | **Nb anim.** | **VFX requis** | **Nb VFX** | **Icon/UI** | **Priorité** | Statut | Notes                           |
| ---------------------- | -------------------------------- | --------------------------------------------: | ---------------------------------------------------------------: | ----------------------- | -----------: | -------------- | ---------: | ----------- | ------------ | ------ | ------------------------------- |
| **Player**             | *Ashen Knight*                   |                        1 sprite / spritesheet |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | Personnage joueur               |
| **NPC**                | *Princess Karla*                 |                        1 sprite / spritesheet |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | Personnage non joueur, narratif |
| **NPC**                | *The Ancient Spirit*             |                        1 sprite / spritesheet |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | Personnage non joueur, narratif |
| **Enemy**              | *Slime*                          | 1 sprite / spritesheet /1 character asset set |                           *Green Slime, Purple Slime, Red Slime* | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Mob                             |
| **Enemy**              | *Melee Warrior*                  | 1 sprite / spritesheet /1 character asset set |                   *Orc Warrior, Skeleton Warrior, Demon Warrior* | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Mob                             |
| **Enemy**              | *Ranged Archer*                  | 1 sprite / spritesheet /1 character asset set |                   *Goblin Archer, Skeleton Archer, Demon Archer* | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Mob                             |
| **Enemy**              | *Caster*                         | 1 sprite / spritesheet /1 character asset set |               *Corrupted Shaman, Blight Sorcerer, Demon Cultist* | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Mob                             |
| **Enemy**              | *Swarm*                          | 1 sprite / spritesheet /1 character asset set |                                    *Possessed Skulls, Fury Bats* | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Mob                             |
| **Large/ Elite Enemy** | *Chud Blob*                      | 1 sprite / spritesheet /1 character asset set |                                                                — | `À définir`             |            — | `À définir`    |          — | Non         | **P1**       | ⬜      | Elite Mob                       |
| **Large/ Elite Enemy** | *Bloated Slime*                  | 1 sprite / spritesheet /1 character asset set |                                                                — | `À définir`             |            — | `À définir`    |          — | Non         | **P1**       | ⬜      | Elite Mob                       |
| **Large/ Elite Enemy** | *Chaos Champion*                 | 1 sprite / spritesheet /1 character asset set |                                                                — | `À définir`             |            — | `À définir`    |          — | Non         | **P1**       | ⬜      | Elite Mob                       |
| **Large/ Elite Enemy** | *Necromancer*                    | 1 sprite / spritesheet /1 character asset set |                                                                — | `À définir`             |            — | `À définir`    |          — | Non         | **P1**       | ⬜      | Elite Mob                       |
| **Enemy**              | *Boss Final — Lupikal*           |                        1 sprite / spritesheet |                                                                — | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | Grande taille                   |
| **Trap**               | *Spikes — fixes*                 |                                      1 sprite |                                                                — | Aucune                  |            0 | `À définir`    |          — | Non         | **P0**       | ⬜      | Élément statique                |
| **Trap**               | *Spikes — mobiles*               |                        1 sprite / spritesheet |                                                                — | Extend, Retract         |            2 | `À définir`    |          — | Non         | **P0**       | ⬜      | Animation cyclique              |
| **Trap**               | *Trappes ouvrables*              |                        1 sprite / spritesheet |                                                                — | Open                    |            1 | `À définir`    |          — | Non         | **P1**       | ⬜      | Élément statique, trigger       |
| **Trap**               | *Tourelles à projectiles*        |                        1 sprite / spritesheet |                                                                — | Shoot                   |            1 | `À définir`    |          — | Non         | **P0**       | ⬜      | Animation cyclique              |
| **Trap**               | *Plant*                          |                                      1 sprite |                                                                — | Aucune                  |            0 | `À définir`    |          — | Non         | **P1**       | ⬜      | Élément statique                |
| **Trap**               | *Flammes*                        |                         1 sprite/ spritesheet |                                                                — | Animated flames         |            1 | `À définir`    |          — | Non         | **P1**       | ⬜      | Animation cyclique              |
| **Item**               | *Gold Coin*                      |                                      1 sprite |                                                                — | `À définir`             |            — | Pickup         |          1 | Oui         | **P0**       | ⬜      | Collectible                     |
| **Item**               | *Shards*                         |                                      1 sprite |                                                                — | `À définir`             |            — | Pickup         |          1 | Oui         | **P0**       | ⬜      | Collectible                     |
| **Item**               | *Bonus HP*                       |                                      1 sprite |                                                                — | `À définir`             |            — | Pickup         |          1 | Oui         | **P0**       | ⬜      | Collectible                     |
| **Item**               | *Chests*                         |                         1 sprite/ spritesheet |                         *Common Chest, Rare Chest, Golden Chest* | `À définir`             |            — | Interact       |          — | Oui         | **P0**       | ⬜      |                                 |
| **Item**               | *Melee Weapon*                   |                         1 sprite/ spritesheet |  *Sword, Longsword, Brutal Axe, Dark Scythe, Warhammer, Halberd* | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | Equipement                      |
| **Item**               | *Ranged Weapon*                  |                         1 sprite/ spritesheet |                        *Longbow, Dire Gauntlet, Throwing Knives* | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | Equipement                      |
| **Item**               | *Legendary Weapon*               |                         1 sprite/ spritesheet | *Dragon Slayer, Obsidian Relic, Thunderstruck, Demonic Crossbow* | `À définir`             |            — | `À définir`    |          — | Oui         | **P1**       | ⬜      | Equipement                      |
| **Consumables**        | *Potion*                         |                         1 sprite/ spritesheet |                     *Minor Healing Potion, Major Healing Potion* | `À définir`             |            — | Pickup         |          1 | Oui         | **P1**       | ⬜      | Collectible                     |
| **Consumables**        | *Buffs*                          |                         1 sprite/ spritesheet |                                       *Magic Shield, Rage Drink* | `À définir`             |            — | Pickup         |          1 | Oui         | **P1**       | ⬜      | Collectible                     |
| **Consumables**        | *Unique*                         |                                      1 sprite |                                                  *Enchant Juice* | `À définir`             |            — | Pickup         |          1 | Oui         | **P1**       | ⬜      | Collectible                     |
| **UI/ HUD**            | *HP*                             |                              1 sprite / tiles |                        variantes état : coeur entier, demi-coeur | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | —                               |
| **UI/ HUD**            | *Equip Slot*                     |                              1 sprite / tiles |                        variantes état : coeur entier, demi-coeur | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | —                               |
| **UI/ HUD**            | *Collectibles Counter*           |                              1 sprite / tiles |                                             *Gold Coins, Shards* | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | —                               |
| **UI/ HUD**            | *Player Avatar*                  |                              1 sprite / tiles |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P2**       | ⬜      | —                               |
| **UI/ HUD**            | *Context Window*                 |                              1 sprite / tiles |                          variantes d'informations : system, tuto | `À définir`             |            — | `À définir`    |          — | Oui         | **P1**       | ⬜      | —                               |
| **UI/ HUD**            | *Death Screen*                   |                              1 sprite / tiles |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | —                               |
| **UI/ HUD**            | *Chest Opening/Rewards*          |                              1 sprite / tiles |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P0**       | ⬜      | —                               |
| **UI/ HUD**            | *Bandeau inférieur dialogue NPC* |                              1 sprite / tiles |                                                                — | `À définir`             |            — | `À définir`    |          — | Oui         | **P1**       | ⬜      | —                               |
| **Environment**        | *Secret Wall*                    |                               1 tile / sprite |                                                  variantes biome | Reveal / Fade           |            1 | Reveal         |          1 | Non         | **P1**       | ⬜      | Doit rester discret             |
| **Environment**        | *Door*                           |                              1 sprite / tiles |                                                  variantes biome | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | —                               |
| **Environment**        | *Pressure Plate*                 |                              1 sprite / tiles |                                                  variantes biome | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | —                               |
| **Environment**        | *Button*                         |                              1 sprite / tiles |                                                  variantes biome | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | —                               |
| **Environment**        | *Décors, parallax*               |                              1 sprite / tiles |                                                  variantes biome | `À définir`             |            — | `À définir`    |          — | Non         | **P0**       | ⬜      | —                               |
|                        |                                  |                                               |                                                                  |                         |              |                |            |             |              |        |                                 |

---

## Détail d'une entité

Lorsque l'élément est complexe, compléter sa ligne principale par une fiche détaillée.

### `[Nom de l'entité]`

**Catégorie :** Player / Enemy / Elite / Boss / Item / Trap / Environment / Tile / VFX / UI  
**Priorité :** P0 / P1 / P2  
**Asset principal :** `À définir`  
**Dimensions / échelle :** `À définir`  
**Variantes visuelles :** `À définir`

#### Animations

|Animation|Requise ?|Boucle ?|Priorité|Asset disponible ?|Intégrée ?|Notes|
|---|---|---|---|---|---|---|
|Idle|☐|Oui|P0|☐|☐||
|Move / Walk|☐|Oui|P0|☐|☐||
|Attack|☐|Non|P0|☐|☐||
|Hit / Damage|☐|Non|P1|☐|☐||
|Death|☐|Non|P0|☐|☐||
|Special 01|☐|—|—|☐|☐||
|Special 02|☐|—|—|☐|☐||

#### VFX

|VFX|Événement|Priorité|Asset disponible ?|Intégré ?|Notes|
|---|---|---|---|---|---|
|`À définir`|`À définir`|P0/P1/P2|☐|☐||
|`À définir`|`À définir`|P0/P1/P2|☐|☐||

#### Assets supplémentaires

|Type|Asset requis|Quantité / variantes|Priorité|Statut|Notes|
|---|---|--:|---|---|---|
|Projectile|—|—|—|⬜||
|Weapon sprite|—|—|—|⬜||
|Shadow|—|—|—|⬜||
|Ground decal|—|—|—|⬜||
|UI Icon|—|—|—|⬜||
|Portrait|—|—|—|⬜||