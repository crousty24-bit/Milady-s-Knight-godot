# Milady's Knight — Audio Design & Pipeline

## 4. Sound Design & Music :

##### Key Features

- **SFX** : 
- **Music** : thème principale (menu) ; sons d'ambiance par niveau ; musique par thèmes narratifs par groupe de niveau musique boss final

### Règles techniques SFX, Music

#### Direction sonore

Le sound design doit renforcer à la fois la lisibilité du gameplay et l'atmosphère dark fantasy du jeu.

L'identité sonore générale doit être sombre, médiévale, inquiétante et parfois horrifique, avec une approche rétro cohérente avec la direction artistique pixel-art.

Les sons associés à des événements importants de gameplay doivent être facilement reconnaissables par le joueur.

#### SFX

Les principaux événements du jeu disposent de feedbacks sonores dédiés :

- mouvements du joueur : jump, double jump, landing, wall jump, wall slide ; pas de SFX pour footsteps
    
- combat joueur : weapon swing, weapon hit, projectile, landing attack, special attacks ;
    
- états joueur : dégâts reçus, soin, mort, Magic Shield, Rage Drink ;
    
- armes : identité sonore distincte pour chaque famille d'arme et effets spécifiques pour les armes légendaires ; A DEFINIR
    
- ennemis : attaques, dégâts reçus, mort, capacités particulières ;
    
- Boss Final : attaques et capacités spécifiques, passage en phase Enraged et mort ;
    
- collectibles : gold coins, shards, potions, HP bonus ;
    
- chests : interaction, paiement, ouverture, apparition de la récompense, validation/refus ;
    
- Golden Chest : sound design distinctif et plus spectaculaire ;
    
- environnement : portes, plaques de pression, mécanismes, passages secrets ;
    
- pièges : spikes, trapdoors, turrets, fire ;
    
- UI : navigation, sélection, confirmation, annulation, erreur, pause ;
    
- systèmes : changement d'équipement et cooldown terminé.
    

Les sons très répétitifs peuvent posséder plusieurs variantes afin d'éviter une répétition artificielle. Une légère variation aléatoire du pitch et/ou du volume peut également être utilisée.

#### Ambience

Chaque niveau possède une ambiance sonore environnementale correspondant à son biome.

Les ambiances sont indépendantes de la musique et peuvent continuer à être jouées lors de passages sans musique.

Exemples : vent, forêt nocturne, feu, grottes, chaînes, ruines, sons organiques liés à la corruption, réverbérations de donjon.

#### Music

La musique doit rester relativement discrète pendant l'exploration afin de laisser suffisamment d'espace aux SFX nécessaires au gameplay.

Plusieurs niveaux peuvent partager une même famille musicale lorsque leurs environnements ou leur progression narrative sont proches.

Prévoir principalement :

- **Main Menu Theme ;**

- **Eidolon Vale / Intro Theme ;**

- **Early Kingdom Theme (Blight Town / Dark Forest);**

- **Graveyard / Haunted Caves Theme ;**

- **Desolands / Rotbringer Camps Theme ;**

- **Fallen Temple / Darkveil Dungeon Theme ;**

- **Boss Final Theme**

Il n'y a pas de système complet de musique dynamique pour les combats standards/aggro.

Le Boss Final dispose en revanche de sa propre musique.

#### Technical Audio

Formats audio utilisés dans le projet :

- **SFX courts : WAV ;**

- **Music : Ogg Vorbis ;**

- **Ambient loops : Ogg Vorbis**

Les SFX positionnels liés au monde utilisent une spatialisation 2D lorsque celle-ci apporte une information pertinente au joueur.

Les musiques et sons UI restent non positionnels.

Les assets audio sont répartis dans plusieurs groupes logiques :

- **Master ;**

- **Music ;**

- **Ambient ;**

- **SFX ;**

- **UI**

Des contrôles séparés Master Volume, Music Volume et SFX Volume doivent pouvoir être ajoutés dans les réglages du jeu.

Les sons doivent être testés ensemble afin de conserver un mix équilibré et d'éviter le clipping.

#### Audio Assets Pipeline

Le projet utilisera des SFX et musiques provenant de bibliothèques d'assets externes.

Pour chaque asset tiers doivent être conservés :

- **source ;**

- **auteur ;**

- **licence ;**

- **obligation éventuelle d'attribution ;**

- **autorisation de modification et d'utilisation dans le jeu**

Les assets peuvent être édités afin d'harmoniser leur volume, leur durée et leur identité sonore avant leur intégration.

Les fichiers audio doivent suivre une convention de nommage cohérente par catégorie et par fonction.
