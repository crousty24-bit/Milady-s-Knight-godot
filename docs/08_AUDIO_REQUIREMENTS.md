# Milady's Knight — Audio Requirements

## Audio Asset List

**Priorité :**

- **P0** : indispensable pour la première version jouable.
    
- **P1** : important pour le feedback, la lisibilité ou l'identité sonore.
    
- **P2** : polish ; peut être ajouté dans une itération ultérieure.
    

Pour les sons très répétitifs, prévoir plusieurs variantes d'un même asset lorsque pertinent (`01`, `02`, `03`...).


### Player — Movement

| Nom                          | Événement déclencheur | Catégorie         | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ---------------------------- | --------------------- | ----------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_player_jump`            | Jump simple           | Player / Movement | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_player_double_jump`     | Double jump           | Player / Movement | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_player_land`            | Atterrissage          | Player / Movement | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_player_wall_jump`       | Wall jump             | Player / Movement | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_player_wall_slide_loop` | Wall slide            | Player / Movement | P1       | ☐              | —      | WAV    | ☐         |

---

### Player — Damage / Health / Death

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_player_hit_01-03`|Joueur reçoit des dégâts|Player / State|P0|☐|—|WAV|☐|
|`sfx_player_knockback`|Knockback après certains dégâts|Player / State|P1|☐|—|WAV|☐|
|`sfx_player_heal`|Récupération de HP|Player / State|P0|☐|—|WAV|☐|
|`sfx_player_hp_bonus`|Ramassage d'un bonus permanent +1 HP|Player / State|P1|☐|—|WAV|☐|
|`sfx_player_death`|HP atteint 0|Player / Death|P0|☐|—|WAV|☐|
|`sfx_player_death_message`|Apparition de "Thou hast perished."|Player / Death|P1|☐|—|WAV|☐|

---

### Player — Generic Combat

| Nom                            | Événement déclencheur                     | Catégorie | Priorité | Asset trouvé ? | Source | Format | Intégré ? | Item concerné                                          |
| ------------------------------ | ----------------------------------------- | --------- | -------- | -------------- | ------ | ------ | --------- | ------------------------------------------------------ |
| `sfx_melee_swing_light_01-03`  | Attaque arme légère                       | Combat    | P0       | ☐              | —      | WAV    | ☐         | *Sword*<br>*Brutal Axe*<br>                            |
| `sfx_melee_swing_heavy_01-03`  | Attaque arme lourde                       | Combat    | P0       | ☐              | —      | WAV    | ☐         | *Dark Scythe*<br>*Warhammer*<br>*Halberds* *Longsword* |
| `sfx_melee_hit_01-06`          | Attaque touche un ennemi                  | Combat    | P0       | ☐              | —      | WAV    | ☐         |                                                        |
| `sfx_melee_hit_environment`    | Attaque touche décor / surface            | Combat    | P1       | ☐              | —      | WAV    | ☐         |                                                        |
| `sfx_ranged_projectile_launch` | Tir générique                             | Combat    | P0       | ☐              | —      | WAV    | ☐         |                                                        |
| `sfx_ranged_projectile_hit`    | Projectile touche ennemi / décor          | Combat    | P0       | ☐              | —      | WAV    | ☐         |                                                        |
| `sfx_landing_attack_fall`      | Déclenchement de l'attaque d'atterrissage | Combat    | P0       | ☐              | —      | WAV    | ☐         |                                                        |
| `sfx_landing_attack_impact`    | Impact au sol de l'attaque d'atterrissage | Combat    | P0       | ☐              | —      | WAV    | ☐         |                                                        |

---

### Weapons — Standard

> Les familles sonores exactes restent à valider pendant le prototypage. Plusieurs armes peuvent partager certains sons si leur comportement physique reste proche.

| Nom                              | Événement déclencheur    | Catégorie        | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| -------------------------------- | ------------------------ | ---------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_weapon_sword_swing_01-03`   | Sword / Longsword attack | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_axe_swing_01-03`     | Brutal Axe attack        | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_hammer_swing_01-03`  | Warhammer attack         | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_scythe_swing_01-03`  | Dark Scythe attack       | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_halberd_swing_01-03` | Halberd attack           | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_bow_shot_01-03`      | Longbow projectile fired | Weapons          | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_knives_throw_01-03`  | Knives projectile fired  | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_fire_gauntlet_start` | Début du souffle         | Weapons          | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_fire_gauntlet_loop`  | Souffle actif            | Weapons          | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_fire_gauntlet_end`   | Fin du souffle           | Weapons          | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_weapon_fire_gauntlet_ready` | Fin du cooldown          | Weapons / System | P1       | ☐              | —      | WAV    | ☐         |

---

### Legendary Weapons

| Nom                           | Événement déclencheur             | Catégorie        | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ----------------------------- | --------------------------------- | ---------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_dragon_slayer_swing`     | Attaque normale Dragon Slayer     | Legendary Weapon | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_dragon_slayer_charge`    | Maintien de l'attaque spéciale    | Legendary Weapon | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_dragon_slayer_release`   | Relâchement de l'attaque chargée  | Legendary Weapon | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_dragon_slayer_ready`     | Cooldown attaque spéciale terminé | Legendary Weapon | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_obsidian_relic_swing`    | Attaque Obsidian Relic            | Legendary Weapon | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_obsidian_relic_heal`     | Heal après 10 kills               | Legendary Weapon | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_thunderstruck_swing`     | Attaque Thunderstruck             | Legendary Weapon | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_thunderstruck_lightning` | Foudre générée par landing attack | Legendary Weapon | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_thunderstruck_ready`     | Cooldown terminé                  | Legendary Weapon | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_demonic_crossbow_shot`   | Tir Demonic Crossbow              | Legendary Weapon | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_demonic_crossbow_pierce` | Projectile traverse un mob        | Legendary Weapon | P2       | ☐              | —      | WAV    | ☐         |

---

### Collectibles & Consumables

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_gold_coin_pickup_01-03`|Gold coin ramassé|Collectible|P0|☐|—|WAV|☐|
|`sfx_shard_gain_01-03`|Mob tué → shards obtenus|Collectible|P0|☐|—|WAV|☐|
|`sfx_minor_potion_pickup`|Minor Healing Potion utilisée|Consumable|P0|☐|—|WAV|☐|
|`sfx_major_potion_pickup`|Major Healing Potion utilisée|Consumable|P1|☐|—|WAV|☐|
|`sfx_magic_shield_activate`|Magic Shield ramassé|Consumable|P0|☐|—|WAV|☐|
|`sfx_magic_shield_end`|Fin de l'effet Magic Shield|Consumable|P1|☐|—|WAV|☐|
|`sfx_rage_drink_activate`|Rage Drink ramassé|Consumable|P0|☐|—|WAV|☐|
|`sfx_rage_drink_end`|Fin de l'effet Rage Drink|Consumable|P1|☐|—|WAV|☐|
|`sfx_enchant_juice_pickup`|Enchant Juice découvert / ramassé|Consumable|P1|☐|—|WAV|☐|
|`sfx_enchant_juice_upgrade`|Upgrade +2 confirmé|Consumable|P0|☐|—|WAV|☐|

---

### Equipment / Upgrade

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_weapon_equip`|Nouvelle arme équipée|Equipment|P0|☐|—|WAV|☐|
|`sfx_weapon_switch`|Changement slot mêlée / tir|Equipment|P0|☐|—|WAV|☐|
|`sfx_weapon_upgrade`|Niveau d'arme augmenté|Equipment|P0|☐|—|WAV|☐|
|`sfx_legendary_equip`|Arme légendaire obtenue / équipée|Equipment|P1|☐|—|WAV|☐|
|`sfx_cooldown_ready`|Capacité générique disponible|System|P1|☐|—|WAV|☐|

---

### Slimes

| Nom                     | Événement déclencheur                | Catégorie     | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ----------------------- | ------------------------------------ | ------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_slime_attack`      | Collision offensive avec joueur      | Enemy / Slime | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_slime_hit_01-03`   | Slime reçoit un coup                 | Enemy / Slime | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_slime_death_01-03` | Slime tué                            | Enemy / Slime | P0       | ☐              | —      | WAV    | ☐         |

Une même famille de sons peut être pitchée/modifiée pour différencier Green, Purple et Red Slime OU uniformiser même sons pour tous les Slimes. **A DEFINIR**

---

### Skeleton Warrior

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_skeleton_warrior_attack_01-02`|Attaque mêlée|Enemy / Skeleton|P0|☐|—|WAV|☐|
|`sfx_skeleton_warrior_hit_01-03`|Dégâts reçus|Enemy / Skeleton|P1|☐|—|WAV|☐|
|`sfx_skeleton_warrior_death_01-03`|Mort|Enemy / Skeleton|P0|☐|—|WAV|☐|

---

### Skeleton Archer

| Nom                               | Événement déclencheur    | Catégorie          | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| --------------------------------- | ------------------------ | ------------------ | -------- | -------------- | ------ | ------ | --------- |
| `sfx_skeleton_archer_shot_01-02`  | Flèche tirée             | Enemy / Skeleton   | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_skeleton_arrow_impact`       | Projectile touche joueur | Enemy / Projectile | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_skeleton_archer_hit_01-03`   | Dégâts reçus             | Enemy / Skeleton   | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_skeleton_archer_death_01-03` | Mort                     | Enemy / Skeleton   | P0       | ☐              | —      | WAV    | ☐         |

---

### Blight Sorcerer

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_sorcerer_melee_attack`|Attaque bâton|Enemy / Sorcerer|P0|☐|—|WAV|☐|
|`sfx_sorcerer_spell_cast`|Déclenchement attaque magique au sol|Enemy / Sorcerer|P0|☐|—|WAV|☐|
|`sfx_sorcerer_ground_warning`|Apparition zone télégraphiée|Enemy / Sorcerer|P0|☐|—|WAV|☐|
|`sfx_sorcerer_ground_explosion`|Explosion zone au sol|Enemy / Sorcerer|P0|☐|—|WAV|☐|
|`sfx_sorcerer_hit_01-02`|Dégâts reçus|Enemy / Sorcerer|P1|☐|—|WAV|☐|
|`sfx_sorcerer_death`|Mort|Enemy / Sorcerer|P0|☐|—|WAV|☐|

---

### Possessed Skulls

| Nom                     | Événement déclencheur         | Catégorie     | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ----------------------- | ----------------------------- | ------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_skull_spawn`       | Apparition de la swarm        | Enemy / Skull | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_skull_fly_loop`    | Déplacement de la swarm       | Enemy / Skull | P2       | ☐              | —      | WAV    | ☐         |
| `sfx_skull_attack`      | Collision avec joueur         | Enemy / Skull | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_skull_death_01-03` | Skull détruit                 | Enemy / Skull | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_skull_despawn`     | Joueur quitte la zone d'aggro | Enemy / Skull | P1       | ☐              | —      | WAV    | ☐         |

---

### Bloated Slime

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_bloated_slime_attack`|Attaque / collision|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_bloated_slime_hit_01-03`|Dégâts reçus|Elite Enemy|P1|☐|—|WAV|☐|
|`sfx_bloated_slime_death`|Mort|Elite Enemy|P0|☐|—|WAV|☐|

---

### Chud Blob

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_chud_attack_01-02`|Attaque mêlée|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_chud_hit_01-03`|Dégâts reçus|Elite Enemy|P1|☐|—|WAV|☐|
|`sfx_chud_death`|Mort|Elite Enemy|P0|☐|—|WAV|☐|

---

### Chaos Champion

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_chaos_champion_attack_01-02`|Attaque mêlée|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_chaos_champion_charge_warning`|Charge préparée|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_chaos_champion_charge`|Charge active|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_chaos_champion_charge_hit`|Charge touche le joueur|Elite Enemy|P1|☐|—|WAV|☐|
|`sfx_chaos_champion_hit_01-03`|Dégâts reçus|Elite Enemy|P1|☐|—|WAV|☐|
|`sfx_chaos_champion_death`|Mort|Elite Enemy|P0|☐|—|WAV|☐|

---

### Necromancer

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_necromancer_melee_attack`|Attaque bâton|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_necromancer_spell_cast`|Attaque magique au sol|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_necromancer_ground_warning`|Zones magiques apparaissent|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_necromancer_ground_explosion`|Explosion zone|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_necromancer_summon`|Invocation des Possessed Skulls|Elite Enemy|P0|☐|—|WAV|☐|
|`sfx_necromancer_hit_01-02`|Dégâts reçus|Elite Enemy|P1|☐|—|WAV|☐|
|`sfx_necromancer_death`|Mort|Elite Enemy|P0|☐|—|WAV|☐|

---

### Boss Final

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_boss_intro`|Début du combat|Boss|P1|☐|—|WAV|☐|
|`sfx_boss_melee_attack_01-03`|Attaque mêlée|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_ground_cast`|Cast attaque au sol|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_ground_warning`|Zones dangereuses apparaissent|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_ground_explosion`|Explosion attaque au sol|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_fireball_cast`|Tir boule de feu|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_fireball_loop`|Boule de feu en mouvement|Boss|P2|☐|—|WAV|☐|
|`sfx_boss_fireball_impact`|Boule de feu touche cible / décor|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_charge_warning`|Charge annoncée|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_charge`|Charge active|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_summon`|Invocation Possessed Skulls|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_hit_01-03`|Boss reçoit un coup|Boss|P1|☐|—|WAV|☐|
|`sfx_boss_enrage`|HP ≤ 20 → mode Enraged|Boss|P0|☐|—|WAV|☐|
|`sfx_boss_death`|Boss vaincu|Boss|P0|☐|—|WAV|☐|

---

### Traps

| Nom                            | Événement déclencheur           | Catégorie          | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ------------------------------ | ------------------------------- | ------------------ | -------- | -------------- | ------ | ------ | --------- |
| `sfx_spikes_hit`               | Joueur touche piques fixes      | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_spikes_extend`            | Piques mobiles sortent          | Trap               | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_spikes_retract`           | Piques mobiles se rétractent    | Trap               | P2       | ☐              | —      | WAV    | ☐         |
| `sfx_trapdoor_trigger`         | Joueur déclenche une trappe     | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_trapdoor_open`            | Trappe s'ouvre                  | Trap               | P2       | ☐              | —      | WAV    | ☐         |
| `sfx_turret_fire`              | Tourelle tire                   | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_turret_projectile_impact` | Projectile touche joueur        | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_poison_plant_hit`         | Joueur touche plante dangereuse | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_fire_loop`                | Flammes actives                 | Trap / Environment | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_fire_damage`              | Joueur prend dégâts des flammes | Trap               | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_player_fall_void`         | Joueur chute hors de la map     | Trap / Death       | P2       | ☐              | —      | WAV    | ☐         |

---

### Doors / Mechanisms / Secrets

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_door_locked`|Interaction avec porte non déverrouillable|Environment|P1|☐|—|WAV|☐|
|`sfx_door_coin_payment`|Coins dépensés pour une porte|Environment|P0|☐|—|WAV|☐|
|`sfx_door_unlock`|Porte déverrouillée|Environment|P0|☐|—|WAV|☐|
|`sfx_door_open`|Porte s'ouvre|Environment|P0|☐|—|WAV|☐|
|`sfx_pressure_plate_activate`|Plaque de pression activée|Mechanism|P0|☐|—|WAV|☐|
|`sfx_button_activate`|Bouton / mécanisme utilisé|Mechanism|P0|☐|—|WAV|☐|
|`sfx_mechanism_move`|Mécanisme / porte actionnée|Mechanism|P1|☐|—|WAV|☐|
|`sfx_secret_wall_hit`|Coup porté sur un passage secret|Secret|P1|☐|—|WAV|☐|
|`sfx_secret_reveal`|Mur secret disparaît|Secret|P0|☐|—|WAV|☐|
|`sfx_secret_discovered`|Salle secrète révélée|Secret|P1|☐|—|WAV|☐|

---

### Chests

| Nom                       | Événement déclencheur              | Catégorie  | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ------------------------- | ---------------------------------- | ---------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_chest_interact`      | Joueur interagit avec coffre       | Chest      | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_open_common`   | Common Chest ouvert                | Chest      | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_open_rare`     | Rare Chest ouvert                  | Chest      | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_reward_roll`   | Animation de génération récompense | Chest / UI | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_reward_reveal` | Récompense révélée                 | Chest / UI | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_reward_select` | Changement de slot récompense      | Chest / UI | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_reward_accept` | Récompense acceptée                | Chest / UI | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_chest_reward_refuse` | Récompense refusée                 | Chest / UI | P1       | ☐              | —      | WAV    | ☐         |

---

### Golden Chest

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_golden_chest_open`|Golden Chest ouvert|Golden Chest|P0|☐|—|WAV|☐|
|`sfx_golden_chest_roll`|Animation du drop|Golden Chest|P1|☐|—|WAV|☐|
|`sfx_golden_chest_legendary_reveal`|Arme légendaire obtenue|Golden Chest|P0|☐|—|WAV|☐|
|`sfx_golden_chest_empty`|Aucun item obtenu|Golden Chest|P0|☐|—|WAV|☐|

---

### Shards / Offerings

| Nom                         | Événement déclencheur          | Catégorie         | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| --------------------------- | ------------------------------ | ----------------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_offering_open`         | Fenêtre d'offrande niveau 5/7  | System / Offering | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_offering_accept`       | Sacrifice accepté              | System / Offering | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_offering_hp_sacrifice` | HP Max définitivement sacrifié | System / Offering | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_offering_refuse`       | Offre refusée                  | System / Offering | P1       | ☐              | —      | WAV    | ☐         |

---

### Generic UI

| Nom                   | Événement déclencheur          | Catégorie | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| --------------------- | ------------------------------ | --------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_ui_navigate`     | Changement élément sélectionné | UI        | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_confirm`      | Action confirmée               | UI        | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_cancel`       | ESC / annulation               | UI        | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_error`        | Action impossible              | UI        | P0       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_window_open`  | Ouverture fenêtre contextuelle | UI        | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_window_close` | Fermeture fenêtre contextuelle | UI        | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_pause`        | Pause ouverte                  | UI        | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_ui_unpause`      | Retour au jeu                  | UI        | P1       | ☐              | —      | WAV    | ☐         |

---

### Main Menu / System

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`sfx_menu_navigate`|Navigation New Game / Continue / Controls / Quit|UI / Menu|P0|☐|—|WAV|☐|
|`sfx_menu_confirm`|Option sélectionnée|UI / Menu|P0|☐|—|WAV|☐|
|`sfx_menu_disabled`|Continue indisponible / option désactivée|UI / Menu|P1|☐|—|WAV|☐|
|`sfx_game_start`|New Game / Continue lancé|System|P1|☐|—|WAV|☐|
|`sfx_level_transition`|Passage au niveau suivant|System|P1|☐|—|WAV|☐|
|`sfx_level_spawn`|Apparition du joueur après chargement|System|P2|☐|—|WAV|☐|

---

### Dialogue / Narration

| Nom                      | Événement déclencheur           | Catégorie | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ------------------------ | ------------------------------- | --------- | -------- | -------------- | ------ | ------ | --------- |
| `sfx_dialogue_open`      | Bandeau dialogue apparaît       | Dialogue  | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_dialogue_text_tick` | Animation texte progressive     | Dialogue  | P2       | ☐              | —      | WAV    | ☐         |
| `sfx_dialogue_next`      | Passage à la prochaine réplique | Dialogue  | P2       | ☐              | —      | WAV    | ☐         |
| `sfx_dialogue_skip`      | Dialogue passé avec Space       | Dialogue  | P1       | ☐              | —      | WAV    | ☐         |
| `sfx_dialogue_close`     | Fin du dialogue                 | Dialogue  | P2       | ☐              | —      | WAV    | ☐         |

---

### 🎵 Ambient Asset List

Les ambiances sont principalement des boucles longues indépendantes des musiques.

|Nom|Événement déclencheur|Catégorie|Priorité|Asset trouvé ?|Source|Format|Intégré ?|
|---|---|---|---|---|---|---|---|
|`amb_eidolon_vale`|Niveau 1 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_blight_town`|Niveau 2 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_black_forest`|Niveau 3 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_forbidden_graveyard`|Niveau 4 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_haunted_caves`|Niveau 5 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_desolands`|Niveau 6 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_rotbringer_camps`|Niveau 7 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_fallen_temple`|Niveau 8 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_darkveil_dungeon`|Niveau 9 chargé|Ambient|P1|☐|—|OGG|☐|
|`amb_darkveil_throne`|Niveau 10 chargé|Ambient|P1|☐|—|OGG|☐|

---

### 🎹 Music Asset List

| Nom                     | Événement déclencheur                | Catégorie | Priorité | Asset trouvé ? | Source | Format | Intégré ? |
| ----------------------- | ------------------------------------ | --------- | -------- | -------------- | ------ | ------ | --------- |
| `music_main_theme`      | Menu principal                       | Music     | P0       | ☐              | —      | OGG    | ☐         |
| `music_eidolon_vale`    | Niveau 1                             | Music     | P1       | ☐              | —      | OGG    | ☐         |
| `music_early_kingdom`   | Niveaux 2–3                          | Music     | P1       | ☐              | —      | OGG    | ☐         |
| `music_graveyard_caves` | Niveaux 4–5                          | Music     | P1       | ☐              | —      | OGG    | ☐         |
| `music_desolands_camps` | Niveaux 6–7                          | Music     | P1       | ☐              | —      | OGG    | ☐         |
| `music_temple_dungeon`  | Niveaux 8–9                          | Music     | P1       | ☐              | —      | OGG    | ☐         |
| `music_boss_final`      | Début du combat Boss Final           | Music     | P0       | ☐              | —      | OGG    | ☐         |
| `music_ending`          | Boss vaincu / Princess Karla libérée | Music     | P2       | ☐              | —      | OGG    | ☐         |

---

### Règles d'intégration

- Aucun SFX de footsteps n'est prévu.
    
- Un asset **P0** doit normalement être disponible avant de considérer la feature correspondante comme terminée.
    
- Un même asset peut temporairement être partagé entre plusieurs ennemis ou armes pendant le prototypage.
    
- Les variantes multiples sont prioritaires pour les sons entendus très fréquemment : attaques, impacts, dégâts, morts, coins et shards.
    
- Les SFX de télégraphie d'attaque doivent être clairement audibles et distincts des sons purement décoratifs.
    
- Les sons liés aux ennemis, pièges et éléments du monde peuvent utiliser une spatialisation 2D.
    
- Les sons UI, musique et feedbacks système globaux restent non positionnels.
    
- Toute source tierce doit être documentée avec son auteur, sa licence et ses éventuelles conditions d'attribution.
    
- La colonne `Source` doit idéalement contenir le nom du pack ou de la bibliothèque ainsi que son URL dans la documentation réelle du projet.

---
