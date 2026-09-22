# Milady's Knight — Art Bible

## 3. DA & Design :

##### Caractéristiques Principales

- **Jeu modern retro pixel art 2D**
- **Dark Fantasy**
- **Univers sombre, horrifique**
- **Couleurs ternes, nuances de noirs, de gris, ombrages forts**
- **Accents saturés sur le rouge**
##### Influences Principales

- **Dark Souls**
- **Warhammer Fantasy**
- **World of Warcraft**
- **Halls Of Torment**

### Règles techniques et échelle Pixel Art (Art Bible de base)

> **Statut : premières règles de référence — susceptibles d'évoluer après prototypage et playtests.**

L'objectif est de maintenir une échelle graphique cohérente entre les différents assets du jeu. Tous les sprites ne doivent pas avoir les mêmes dimensions : c'est leur densité de pixels, leurs proportions et leur échelle relative dans le monde qui doivent rester cohérentes.

**Base grid / Tile Grid : 16×16 px**

La grille principale du monde utilise une unité de référence de 16×16 pixels.

Cette grille sert principalement à construire le terrain, les plateformes et les éléments de level design.

Un asset peut occuper plusieurs tiles et n'a aucune obligation d'avoir des dimensions de 16×16 px.

**Internal Resolution : 640×360 px — 16:9**

Résolution logique de référence utilisée pour concevoir le jeu.

Le jeu devra privilégier un agrandissement par facteur entier afin de préserver l'apparence du pixel art.

Résolutions cibles naturelles :

640×360 → ×2 → 1280×720  
640×360 → ×3 → 1920×1080  
640×360 → ×4 → 2560×1440  
640×360 → ×6 → 3840×2160

**Pixel Scaling**

Pixel source : 1×.

Scaling entier privilégié.

Pas de redimensionnement arbitraire des sprites permettant de mélanger différentes densités de pixel art.

**Texture Filtering**

Nearest / Nearest Neighbor.

Pas de filtrage bilinéaire sur les sprites pixel-art principaux.

#### Échelle des personnages

**Player Character**

Référence visuelle : environ 24×32 px pour le corps du personnage.

Le personnage représente environ 2 tiles de hauteur.

Les dimensions réelles des frames d'animation peuvent être supérieures lorsque les armes, attaques ou effets dépassent de la silhouette du personnage.

**Standard Humanoid Enemy**

Échelle similaire au joueur.

Environ 24–32 px de largeur pour 32–40 px de hauteur selon le type d'ennemi.

La différence entre ennemis doit être perceptible principalement par la silhouette et les proportions plutôt que par une simple augmentation uniforme de taille.

**Small Enemy**

Environ 0,5 à 1× la hauteur du joueur.

Exemple : Slimes.

**Large Enemy / Elite**

Environ 1,5 à 2,5× la taille visuelle du joueur selon le design.

Les élites doivent être immédiatement identifiables comme plus imposants qu'un ennemi standard.

**Boss**

Environ 3 à 5× la masse visuelle du joueur.

Sa taille exacte dépendra de l'arène, de ses animations et de la nécessité de conserver une bonne lisibilité durant le combat.

#### Tilesets et environnement

Les tilesets utilisent une grille de référence de 16×16 px.

Les éléments d'environnement peuvent être composés de plusieurs tiles :

porte : 2×3 tiles ;  
statue : 3×5 tiles ;  
grande structure : dimensions libres sur la grille.

Les gros éléments décoratifs peuvent également être utilisés comme sprites ou scènes indépendantes sans respecter une taille de fichier 16×16.

La densité des détails doit cependant rester cohérente avec le pixel art du terrain.

#### Sprites et animations

La taille d'une frame d'animation n'est pas obligatoirement identique à la taille visuelle du personnage.

Une animation d'attaque peut utiliser un canvas plus large afin de contenir l'arme, le mouvement ou un effet.

Les frames appartenant à une même animation doivent conserver un point d'ancrage cohérent afin d'éviter que le personnage semble se déplacer artificiellement entre les frames.

#### Backgrounds

Les arrière-plans ne sont pas contraints par la grille 16×16.

Ils peuvent utiliser des images ou couches beaucoup plus grandes destinées notamment au scrolling ou au parallax.

Le background doit conserver une densité pixel cohérente avec les éléments jouables.

Les arrière-plans devront être moins contrastés et moins détaillés que le premier plan afin de ne pas concurrencer les éléments interactifs.

#### VFX

Les VFX ont des dimensions libres.

Exemples : impacts, flammes, magie, éclairs, poussière, dégâts, effets de collecte.

Ils doivent conserver la même densité de pixels et le même langage visuel que les autres assets.

Les VFX doivent améliorer la compréhension d'une action sans masquer les hitboxes, ennemis, pièges ou plateformes importantes.

#### Lisibilité

Le joueur, les ennemis, les pièges, objets interactifs, collectibles et projectiles doivent pouvoir être distingués rapidement de l'arrière-plan.

Les silhouettes ont priorité sur les petits détails.

Les éléments importants pour le gameplay peuvent utiliser davantage de contraste, luminosité ou saturation que les éléments purement décoratifs.

#### Statut de la grille

La grille 16×16 constitue actuellement la direction privilégiée.

Une alternative 32×32 reste possible si les premiers tests visuels montrent que la densité de détail offerte par le 16×16 est insuffisante.

Le choix définitif devra être validé en comparant directement dans Godot :

un extrait du niveau 1 ;  
le personnage joueur ;  
un Slime ;  
un Skeleton ;  
un élément de décor ;  
un piège ;  
un coffre ;

dans une version 16×16 et une version 32×32.

### Camera System

> **Statut : règles générales de référence — les valeurs précises de smoothing, drag margins, offsets et effets de caméra devront être validées durant le prototypage et les playtests.**

#### Principes généraux

Le jeu utilise une caméra 2D suivant le personnage joueur pendant l'exploration.

La caméra doit avant tout préserver :

- la lisibilité du level design ;
    
- l'anticipation des ennemis et pièges ;
    
- la lisibilité des déplacements du joueur ;
    
- la stabilité visuelle pendant les jumps et combats ;
    
- la cohérence du rendu pixel-art.
    

La caméra ne doit pas créer de mouvements inutiles ou distraire le joueur du gameplay.

#### Relation avec l'échelle Pixel Art

La grille de level design reste basée sur des tiles de **16×16 px**.

La caméra n'est pas directement contrainte par cette grille : son cadrage dépend principalement de la résolution interne du viewport et de son zoom.

Résolution interne de référence :

**640×360 px — 16:9**

Avec un zoom de référence `1×`, le viewport correspond approximativement à :

**40 tiles horizontalement × 22,5 tiles verticalement.**

Le Player Character ayant une hauteur visuelle d'environ **32 px**, il représente approximativement deux tiles de hauteur.

Le zoom de référence initial sera **1×**. Toute modification de ce zoom devra être testée directement dans un niveau représentatif avant d'être adoptée.

#### Scaling et rendu

Le rendu pixel-art doit privilégier un scaling entier.

Résolutions cibles naturelles :

640×360 → ×2 → 1280×720  
640×360 → ×3 → 1920×1080  
640×360 → ×4 → 2560×1440  
640×360 → ×6 → 3840×2160

Configuration générale visée :

**Internal Resolution : 640×360**  
**Aspect Ratio : 16:9**  
**Stretch Mode : Viewport**  
**Stretch Scale Mode : Integer**  
**Texture Filtering : Nearest**

Les comportements de pixel snapping devront être testés avec le mouvement du joueur et le smoothing de la caméra avant validation définitive.

#### Player Follow

La caméra suit le joueur pendant le gameplay.

Le suivi doit fonctionner horizontalement et verticalement afin de prendre en charge les niveaux contenant de la verticalité.

Le joueur ne doit pas obligatoirement rester parfaitement centré à chaque instant.

Une zone de tolérance autour du joueur pourra être utilisée afin d'éviter que la caméra réagisse à chaque petit déplacement.

**A DEFINIR PAR PROTOTYPAGE :**

- drag margins horizontales ;
    
- drag margins verticales ;
    
- position du joueur dans le cadrage ;
    
- vitesse de suivi ;
    
- smoothing ;
    
- comportement pendant jump / double jump / wall jump ;
    
- comportement lors des chutes importantes.
    

#### Horizontal Look-Ahead

Un léger décalage du cadrage dans la direction du déplacement pourra être utilisé afin de montrer davantage de terrain devant le joueur.

Ce comportement doit permettre au joueur d'anticiper :

- terrain ;
    
- plateformes ;
    
- pièges ;
    
- ennemis ;
    
- projectiles ;
    
- interactions.
    

Le déplacement du cadrage ne doit cependant pas produire de mouvements brusques lors des changements fréquents de direction.

**Valeur et comportement exacts : A DEFINIR PAR PROTOTYPAGE.**

#### Vertical Camera Behaviour

La caméra ne doit pas nécessairement suivre immédiatement chaque petit déplacement vertical du joueur.

Les jumps standards doivent rester visuellement stables.

La caméra doit cependant permettre de suivre correctement le joueur pendant :

- longues montées ;
    
- sections verticales ;
    
- wall jump ;
    
- wall slide ;
    
- grandes chutes ;
    
- déplacements via échelles ou éléments similaires.
    

**Comportement exact : A DEFINIR PAR PROTOTYPAGE.**

#### Camera Limits

Chaque niveau possède des limites de caméra correspondant à sa zone jouable.

La caméra ne doit normalement pas afficher de zone située hors des limites prévues du niveau.

Les limites peuvent être différentes selon le level design.

Certaines salles ou sections particulières peuvent utiliser leurs propres limites temporaires.

#### Camera Zones

Certaines zones peuvent modifier temporairement le comportement normal de la caméra lorsque cela améliore la lisibilité.

Exemples potentiels :

- salle fermée ;
    
- grande salle verticale ;
    
- passage étroit ;
    
- salle secrète ;
    
- événement particulier ;
    
- Boss Arena.
    

Ces zones doivent rester exceptionnelles et servir directement le gameplay.

#### Boss Final

Le combat contre le Boss Final se déroule dans une arène dédiée.

Lorsque le joueur entre dans l'arène, la caméra peut adopter un comportement spécifique afin de garantir que le Boss, le joueur et les attaques importantes restent lisibles.

Le comportement exact dépendra des dimensions définitives de l'arène et de la taille finale du Boss.

**A DEFINIR PAR PROTOTYPAGE.**

#### Camera Shake

Des effets courts de camera shake peuvent être utilisés pour renforcer certains événements importants.

Exemples :

- Landing Attack ;
    
- attaque lourde (capacité Dragon Slayer) ;
    
- impact important ;
    
- capacité du Boss ;
    
- événement environnemental majeur.
    

Le camera shake doit rester court et modéré.

Il ne doit jamais empêcher le joueur de lire correctement les plateformes, ennemis, pièges ou projectiles.

**Amplitude et durée : A DEFINIR PAR PROTOTYPAGE.**

#### UI / HUD

Le HUD permanent et les fenêtres UI ne suivent pas les déplacements de la caméra du monde.

Les éléments suivants restent positionnés relativement à l'écran :

- HP ;
    
- slots d'équipement ;
    
- gold coins ;
    
- shards ;
    
- effets temporaires ;
    
- Boss HP ;
    
- fenêtres contextuelles ;
    
- dialogues ;
    
- fenêtres de récompense.
    

#### Règle générale de validation

Toute modification importante du système de caméra doit être testée au minimum dans :

- une section horizontale ;
    
- une section verticale ;
    
- une séquence de jump / double jump ;
    
- une séquence de wall jump / wall slide ;
    
- un combat avec plusieurs ennemis ;
    
- une zone contenant des pièges ;
    
- une grande chute ;
    
- une Boss Arena.
    

La caméra doit être considérée comme un composant du gameplay et du level design, et non comme un simple élément visuel.

### Palette & hiérarchie de contraste

> **Statut : premières règles de référence — susceptibles d'évoluer après prototypage et playtests.**

La direction artistique utilise une palette Dark Fantasy principalement sombre et désaturée.

Le jeu ne repose pas sur une palette strictement identique pour tous les niveaux. Il utilise une **palette globale commune**, complétée par une ou plusieurs couleurs dominantes propres à chaque environnement.

L'objectif est de permettre à chaque niveau d'avoir une identité visuelle distincte tout en conservant un langage graphique cohérent.

#### Palette globale

Couleurs dominantes :

- noirs colorés ;
    
- gris froids ;
    
- gris chauds ;
    
- anthracite ;
    
- bruns désaturés ;
    
- bleus très sombres.
    

Les couleurs fortement saturées sont utilisées avec parcimonie et principalement pour communiquer des informations importantes au joueur.

Chaque biome peut ajouter 1 à 2 couleurs dominantes secondaires.

Exemples :

	Black Forest : bleu nuit / vert froid.  
	Forbidden Graveyard : violet désaturé / cyan spectral.  
	Haunted Caves : brun / vert maladif.  
	Desolands : ocre / rouge poussière.  
	Fallen Temple : violet corruption / rouge sombre.  
	Darkveil Dungeon : gris acier / rouge profond.

#### Hiérarchie de contraste

La lisibilité du gameplay est prioritaire sur le niveau de détail.

Ordre général de priorité visuelle :

**Background → Terrain → Éléments interactifs → Ennemis → Joueur → VFX**

#### Background

Contraste très faible.

Couleurs fortement désaturées.

Les éléments éloignés doivent rester visuellement en retrait.

Éviter les valeurs extrêmes, les couleurs très saturées et les détails trop contrastés.

Les différentes couches de background peuvent utiliser de légères variations de luminosité afin de renforcer la profondeur et le parallax.

#### Terrain

Contraste faible à moyen.

Le terrain doit être clairement identifiable comme surface praticable ou obstacle.

Les surfaces jouables peuvent recevoir une bordure légèrement plus claire afin d'améliorer la compréhension immédiate des plateformes.

Les textures ne doivent jamais rendre la silhouette d'une plateforme difficile à identifier.

#### Éléments interactifs

Contraste moyen à fort.

Les coffres, portes, leviers, plaques de pression, collectibles et consommables doivent être visuellement différenciés du décor.

La saturation, la luminosité, une animation légère ou un VFX discret peuvent être utilisés pour renforcer cette distinction.

Le niveau de contraste dépend de l'importance de l'objet.

#### Ennemis

Contraste fort.

Les silhouettes des ennemis doivent être immédiatement distinguables du terrain et de l'arrière-plan.

Chaque famille d'ennemis doit avoir une silhouette reconnaissable indépendamment de ses petits détails graphiques.

Les ennemis ne doivent pas utiliser exactement les mêmes valeurs dominantes que leur environnement immédiat.

#### Joueur

Priorité visuelle permanente maximale.

Le personnage joueur doit rester facilement identifiable dans toutes les situations de gameplay.

Sa silhouette, ses valeurs et certains accents de couleur doivent rester suffisamment distincts de l'environnement et des ennemis.

La lisibilité du joueur est prioritaire sur son intégration réaliste dans l'éclairage ou les couleurs du niveau.

#### VFX

Contraste très élevé mais temporaire.

Les effets liés aux attaques, impacts, magie, collecte, soins et dégâts peuvent utiliser des couleurs significativement plus lumineuses ou saturées que le reste de l'environnement.

Plus un VFX possède un contraste important, plus sa présence à l'écran doit être courte.

Les VFX ne doivent jamais masquer durablement les ennemis, plateformes, pièges ou projectiles importants.

#### Couleurs fonctionnelles

Certaines familles de couleurs peuvent être associées de manière relativement stable à des fonctions de gameplay :

- **Gold Coin / richesse : or / jaune.**

- **Legendary Item : or / orange.**

- **HP / dégâts / danger : rouge.**

- **Healing : vert.**

- **Magic Shield : cyan / bleu.**

- **Rage : rouge-orange.**

- **Shards : violet.**

- **Corruption / magie hostile : violet sombre / magenta / vert.**

- **Interaction neutre : blanc / jaune pâle.**

- **Électricité / Thunder : bleu clair / blanc.**

Ces associations doivent rester cohérentes dans les sprites, VFX, collectibles et UI.

#### Usage du rouge

Le rouge saturé constitue une couleur importante de la direction artistique mais doit rester relativement rare.

Il est principalement réservé aux éléments liés au danger, aux dégâts, à la violence, à la corruption avancée et aux événements importants.

Les éléments décoratifs peuvent utiliser des rouges plus sombres et désaturés afin de préserver l'impact visuel du rouge saturé.

#### Principe de lisibilité

Un environnement sombre ne signifie pas que tous les éléments doivent être proches du noir.

La sensation Dark Fantasy doit principalement provenir de la palette, de l'ambiance et des rapports de contraste.

Les éléments importants pour le gameplay doivent conserver suffisamment de luminosité et de séparation visuelle pour rester immédiatement identifiables.

### Variantes visuelles des mobs avancés

> **Statut : principe de direction artistique et d'organisation du bestiaire — à formaliser plus précisément avec Astra lors de la documentation du projet.**

Le profil gameplay d'un mob avancé est dissocié de son apparence visuelle.

Une même entité gameplay peut donc utiliser plusieurs assets graphiques différents selon le niveau, le biome ou le contexte narratif.

L'objectif est d'apporter davantage de variété visuelle, d'éviter la répétition du même bestiaire sur plusieurs niveaux et de renforcer l'immersion du joueur dans les différents environnements du jeu.

#### Principe

Les profils **actuellement définis** sous des noms comme :

- Skeleton Warrior ;
    
- Skeleton Archer ;
    
- Blight Sorcerer ;
    
- Possessed Skulls ;
    

doivent être considérés avant tout comme des **archétypes de gameplay**.

Lors de la formalisation définitive du projet, ces profils pourront recevoir un nom fonctionnel générique correspondant à leur rôle.

Exemple :

**Melee Warrior**

Profil gameplay :  
attaque de mêlée, patrouille, système d'aggro, déplacement vers le joueur, statistiques et scaling définis selon la difficulté.

Ce même profil peut recevoir plusieurs représentations visuelles :

Dark Forest → Orc Warrior  
Forbidden Graveyard / Haunted Caves → Skeleton Warrior  
Desolands / Fallen Temple → Demon Warrior

Le comportement fondamental du mob reste celui du même archétype gameplay malgré le changement d'apparence.

#### Nombre de variantes

Chaque archétype de mob avancé pourra disposer d'environ **2 à 3 variantes visuelles différentes** réparties dans les niveaux du jeu.

Cette règle concerne uniquement les mobs avancés.

Elle ne concerne pas :

- les Slimes ;
    
- les mobs Élites ;
    
- le Boss Final.
    

Ces derniers conservent une identité visuelle propre et unique.

#### Cohérence entre variantes

Les différentes représentations graphiques d'un même archétype doivent conserver une lecture gameplay cohérente.

Les variantes doivent notamment conserver :

- un gabarit global suffisamment proche ;
    
- une silhouette correspondant au même rôle de combat ;
    
- des animations fonctionnellement équivalentes ;
    
- des timings d'attaque comparables ;
    
- une télégraphie claire et cohérente des attaques ;
    
- des proportions compatibles avec les mêmes règles générales de collision et de déplacement.
    

Une variation graphique ne doit pas modifier implicitement le fonctionnement gameplay de l'entité.

Si une variante possède un comportement, une attaque, une portée ou une mécanique significativement différente, elle doit être considérée comme un nouvel archétype gameplay et non comme une simple variante visuelle.

#### Adaptation au biome

Chaque variante doit pouvoir adopter les codes visuels du niveau dans lequel elle apparaît :

- palette ;
    
- matériaux ;
    
- armures ;
    
- vêtements ;
    
- corruption ;
    
- effets magiques ;
    
- détails anatomiques ;
    
- accessoires.
    

Ces variations doivent permettre d'intégrer naturellement les ennemis dans leur environnement tout en conservant la lisibilité de leur rôle gameplay.

#### Exemple répartition variantes par niveaux

**Niveau 2 & 3**

- Orc Warrior
- Goblin Archer
- Fury Bats

**Niveau 4 & 5**

- Skeleton Warrior
- Skeleton Archer
- Blight Sorcerer
- Fury Bats (niveau 4)
- Possessed Skulls (niveau 5)

**Niveau 6**

- Demon Warrior
- Demon Archer
- Demon Cultist
- Possessed Skulls

**Niveau 7**

- Skeleton Warrior
- Skeleton Archer
- Blight Sorcerer
- Possessed Skulls

**Niveau 8**

- Demon Warrior
- Demon Archer
- Demon Cultist
- Possessed Skulls & Fury Bats

**Niveau 9**

- Skeleton Warrior
- Skeleton Archer
- Blight Sorcerer
- Possessed Skulls & Fury Bats

#### Exemple de mapping

**Melee Warrior**

- Orc Warrior
    
- Skeleton Warrior
    
- Demon Warrior
    

**Ranged Archer**

- Goblin Archer
    
- Skeleton Archer
    
- Demon Archer
    

**Caster**

- Corrupted Shaman
    
- Blight Sorcerer
    
- Demon Cultist
    

**Swarm**

- Possessed Skulls
    
- Fury Bats


#### Principe général

Le joueur doit pouvoir reconnaître rapidement le **rôle gameplay** d'un ennemi même lorsque son apparence change.

La variété visuelle sert donc l'immersion et l'identité des niveaux sans compromettre l'apprentissage des comportements ennemis.


---
