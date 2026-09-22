# Milady's Knight — Level Design, Difficulty & Persistence

## level design :
- niveaux 2D vertical et horizontal : il y a 10 niveaux en tout
	- la linéarité des niveaux s'estompe au fur et à mesure de la progression et de la montée en difficulté
	- un niveau se constitue globalement de :
		- un point de départ joueur (spawn fixe), c'est toujours le même spawn
		- un point d'arrivé du joueur : la porte finale à déverrouiller avec des coins (toujours le même)
		- des éléments de terrain demandant un déplacement tout aussi horizontal que vertical suivant le niveau
		- le niveau est parsemé d'embuches : mobs, pièges, vide
		- de gold coins à collecter (le joueur ramasse une pièce en passant dessus à son contact)
		- de chest à ouvrir
		- de passages dérobés secrets à trouver
		- des portes secondaires à ouvrir via des plaques de pression ou à déverrouiller avec des coins
	- ordre des niveaux :
		- **niveau 1** - *The Eidolon Vale*  : Intro (prologue narrative + tuto minimal basique) ; très court et facile
			- ennemis : Green et Purple Slime
			- PNJ :  The Ancien Spirit
			- introduction au gameplay et fonctionnalités grâce à des fenêtres de texte pour expliquer (tuto)
			- le niveau doit contenir un common chest à ouvrir, exceptionnellement gratuit uniquement pour présenter son fonctionnement ; donne une récompense fixe prédéterminée : une arme de tir =  *Longbow* niveau 0 ; mais pas d'amélioration
			- le niveau doit contenir une potion de soin mineure à ramasser
		- **niveau 2** - *Blight Town* : village infesté et corrompu par la pourriture ; niveau basique, introduit la difficulté standard du jeu ; axé sur l'horizontalité et forte linéarité 
			- ennemis : Green, Purple et Red Slime + élite mob Bloated Slime
		- **niveau 3** - *Black Forrest* : forêt dense, de nuit ; niveau basique, difficulté standard ; axé sur l'horizontalité et forte linéarité 
			- ennemis : Green, Purple et Red Slime ; Skeleton Warrior et Skeleton Archer
		- **niveau 4** - *Forbidden Graveyard* : cimetière hantée ; niveau basique, difficulté standard un peu plus élevée ; axé sur l'horizontalité et forte linéarité 
			- ennemis : Red Slime, Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls + mob élite Chud Blob
		- **niveau 5** - *Haunted Caves* : les catacombs du cimetière ; niveau avancée, difficulté plus élevée (gap significatif) ; axé sur l'horizontalité et la verticalité, bien moins linéaire
			- ennemis : Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls
		- **niveau 6** - *Desolands* : contrée montagneuse désertique ;  niveau avancée, difficulté plus élevée ; axé sur l'horizontalité et la verticalité, bien moins linéaire
			- ennemis : Red Slime ; Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls
		- **niveau 7** - *Rotbringer Camps* : ruines et camps de guerre dévastés ;  niveau avancée, difficulté plus élevée (beaucoup de mobs) ; axé sur l'horizontalité ; linéaire
			- ennemis : Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls + élite mob Chud Blob et Chaos Champion
		- **niveau 8** - *Fallen Temple* : ancien temple détruit par la corruption ; niveau très avancée, difficulté plus élevée (gap significatif ; beaucoup de mobs et de pièges) ; axé sur l'horizontalité et la verticalité, bien moins linéaire
			- ennemis : Green, Purple et Red Slime ; Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls + Bloated Slime et Chud Blob ;
		- **niveau 9** - *Darkveil Dungeon* : le donjon dans lequel est retenu la princesse ; niveau très avancée, difficulté plus élevée (beaucoup de mobs et de pièges) ; axé sur l'horizontalité et la verticalité, bien moins linéaire
			- ennemis : Skeleton Warrior, Skeleton Archer, Blight Sorcerer et Possessed Skulls + Bloated Slime, Chaos Champion et Necromancer
		- **niveau 10** - *Darkveil Dungeon Throne* : niveau final (arena) avec le combat du Boss et la princesse à sauver !
			- ennemi : Boss Final
			- PNJ : Princess Karla
	- système de pièges :
		- les pièges font partis intégrante du gameplay et du level design
		- les pièges sont présents dans tous les niveaux du jeu
		- il existe plusieurs type de pièges, chacun ayant leur propre dégâts et leur comportement :
			- **piques sur surface** (fixes) : piques qui infligent des dégâts au joueur à la collision ; peuvent être placé sur n'importe quel surface à l'horizontal et à la vertical
				- DMG : 0,5
				- présent dans tous les niveaux
			- **piques sur surface** (mobiles) : idem que les piques mais avec une animation durant laquelle ils se rétractent à interval régulier ; leur vitesse de retractation dépendent de leur emplacement dans le niveau et de la difficulté du niveau
				- DMG : 0,5
				- présent à partir du niveau 2, puis dans tous les niveaux
			- **trappes ouvrables** : une trappe qui remplace un bloc de terrain normal ; au passage du joueur sur la trappe, celle-ci s'ouvre et le joueur peut tomber dedans ; une trappe peut s'ouvrir sur des piques, des plantes, des flammes ou du vide ; leur vitesse de retractation dépendent de leur emplacement dans le niveau et de la difficulté du niveau ; il est possible au joueur d'en sortir en sautant
				- DMG : dépend du piège
				- une fois une trappe ouverte, elle ne se referme plus, elle reste ouverte (sauf au reset du niveau bien sûr)
				- présent à partir du niveau 2, puis dans tous les niveaux
			- **tourelles à projectiles** (fixes) : mini tourelles pouvant être placé sur n'importe quel surface à l'horizontal et à la vertical ; tire des projectiles dans un sens à interval régulier ; leur vitesse de retractation dépendent de leur emplacement dans le niveau et de la difficulté du niveau
				- DMG : 1
				- les projectiles touchant le joueur infligent les dégâts de la même manière qu'un mob (exemple: Skeleton Archer)
				- présent à partir du niveau 3, puis dans tous les niveaux
			- **plantes** (fixes) : similaires aux piques mais infligeant plus de dégâts au joueur à la collision
				- DMG : 1
				- présent à partir du niveau 3, puis dans tous les niveaux
			- **flammes** (fixes) : similaires aux piques mais infligeant beaucoup plus de dégâts au joueur à la collision
				- DMG : 2
				- fonction un peu différent : le joueur doit bien entrer en collision mais tant que le joueur reste "dans les flammes", le piège continu d'infliger 2 DMG toutes les 1,5sec ; l'élément est donc traversables ; le joueur n'est pas repoussé
				- présent à partir du niveau 5, puis dans tous les niveaux
			- **chute dans le vide** : un trou faisant plonger le joueur hors de la map lorsqu'il franchir un certain seuil (zone) ; mort instantanée du joueur
				- DMG : mort immédiate (reset)
				- présent dans tous les niveaux
		- excepté pour les flammes et les tourelles à projectiles : les pièges infligent des dégâts à la collision
			- au moment de la collision, le joueur est ensuite légèrement "repoussé"
			- les pièges sont donc des éléments pleins, non traversables
	- système de passages dérobés :
		- certains murs/surfaces du jeu sont des passages dérobés unique = passage secret
		- les passages dérobés sont rares et sont fait pour être difficile à trouver
		- cela reprend le système connu dans les jeux Dark Souls
		- pour révéler un passage dérobé, le joueur doit effectuer une attaque sur la surface
			- une animation de fondu (+ effet sonore) fait disparaître le mur et révèle un passage, une salle secrète.
			- révéler un passage dérobé ne se fait qu'une seule fois ; il n'y a pas besoin de révéler un passage dérobé à chaque reset du niveau
		- les passages dérobés ont une fonctionnalité :
			- découvrir une salle secrète contenant un chest (rare ou Légendaire) ou un item rare (Major Healing Potion, Enchant Juice) = items cachés
			- ces salles secrète peuvent être petite et confinée ou être une grande salle contenant des pièges et/ou des mobs
		- il n'y a pas d'indicateur clair au joueur qu'une surface est un passage dérobé, cela doit rester difficile à trouver :
			- un passage dérobés peut avoir une teinte (couleur) de surface légèrement différente de celle des autres OU un signe discret (symbole, marque)
		- les passages dérobés sont présent à partir du niveau 4 jusqu'au niveau 9
			- il y a au total 10 passages dérobés dans le jeu
			- type et nombre d'item total à trouver dans les passages dérobés :
				- 1 Enchant Juice
				- 3 Golden Chest
				- 8 Major Healing Potion
				- 6 Rare Chest
			- répartition emplacement des passages dérobés :
				- 1 dans le niveau 4, contient : 1 Major Potion + 1 Rare Chest
				- 2 dans le niveau 5, contient : 1 Enchant Juice ; 2 Major Potion + 2 Rare Chest
				- 2 dans le niveau 6, contient : 1 Golden Chest ; 1 Rare Chest
				- 1 dans le niveau 7, contient : 1 Golden Chest + 1 Major Potion
				- 2 dans le niveau 8, contient : 2 Major Potion ; 1 Rare Chest
				- 2 dans le niveau 9, contient : 2 Major Potion + 1 Rare Chest ; 1 Golden Chest
	- système de portes/chemins secondaire :
		- au fur et à mesure de la progression et de la montée en difficulté, les niveaux deviennent de moins en moins linéaire
		- chemin secondaire = chemin de progression qui dévie plus ou moins de la route principale qui mène à la fin du niveau (porte finale)
		- les niveaux ont des chemins secondaires optionnels ou obligatoire pour accéder à la fin du niveau
			- un chemin optionnel permet d'accéder à une zone ou une salle contenant des chest, des consommables et/ou une concentration plus importante de mobs (utile si le joueur veut farmer plus de shards)
			- un chemin obligatoire doit forcément être débloqué pour progresser dans le niveau
		- les chemins secondaires peuvent être bloqués par une porte / portail / mur qu'il faut alors déverrouiller ; il y a 2 façons de déverrouiller ces accès :
			- dépenser un montant en coin (et non pas en shards !) requis
			- déverrouiller la porte via un mécanisme caché : plaque de pression (se placer dessus ou tirer dessus) à actionner OU interagir avec un bouton (E)
			- les accès aux chemins secondaires sont reset à la mort du joueur ; il faut alors les déverrouiller à chaque tentative
			- les chemins optionnels sont généralement débloqués via dépense de coin
			- les chemins obligatoires sont généralement débloqués via des mécanismes
		- les chemins secondaires sont présent à partir du niveau 4
	- système de verticalité :
		- au fur et à mesure de la progression et de la montée en difficulté, les niveaux deviennent de moins en moins linéaire
		- certains niveaux vont introduire une dimension verticalité qui va demander au joueur de monter/descendre dans le niveau
			- ces déplacements peuvent bien sûr être réalisé via des jump / double jump de plateformes en plateformes OU wall slide 
			- mais certains accès haut/bas peuvent aussi être fait en se déplaçant via des rails/échelles (éléments de terrain) : le joueur doit appuyer sur touches de déplacement haut/bas (exemple : flèche du haut / flèche du bas)
	
	- **EMPLACEMENT DU JOUEUR :**
		- le joueur a un spawn fixe au début du niveau, c'est toujours le même spawn
	- **EMPLACEMENTS DES MOBS :**
		- dans chaque niveau, l'emplacement initial des mobs est fixe et reste le même à chaque chargement/reset du niveau
		- suivant la difficulté du niveau, il y a de plus en plus de mobs au total dans le niveau
		- il y a une concentration (pack) de mobs plus importante dans certaines zone d'un niveau pour augmenter la difficulté (par exemple : dans une pièce étroite avec un rare chest)
	- **EMPLACEMENTS DES PIEGES :**
		- les pièges ont un emplacement fixe et ne change jamais à chaque chargement/reset du niveau
	- **EMPLACEMENTS DES COINS :**
		- les gold coins à collecter pour ouverture de la porte final ont un emplacement fixe et ne change jamais à chaque chargement/reset du niveau
	- **EMPLACEMENTS DES CHEST :**
		- les chest ont un emplacement fixe et ne change jamais à chaque chargement/reset du niveau
	- **EMPLACEMENTS DES CONSOMMABLES :**
		- les consommables (potions de soins, Rage Drink, Magic Shield) ont un emplacement fixe et ne change jamais à chaque chargement/reset du niveau
	- **EMPLACEMENTS DES BONUS HP :**
		- les bonus HP ont un emplacement fixe et ne change jamais à chaque chargement/reset du niveau

## système de difficulté :
- système de difficulté :
	- le jeu se veut progressif dans la montée en difficulté
	- la montée en difficulté est affectée par :
		- le nombre de mobs total présent dans le niveau
		- le concentration plus ou moins importante de mobs dans un ou plusieurs périmètres
		- le type de mobs et leur type d'attaque
		- le nombre de HP des mobs
		- la présence de un ou plusieurs mobs d'élite
		- le nombre de pièges à esquiver ; nombres de chute dans le vide possible
		- la complexité du level design : la taille du niveau ; plus ou moins linéaire ; déplacement horizontal et vertical pour parcourir le terrain ; nombre de passage dérobés ; nombre de portes secondaires à déverrouiller
		- le nombre de coin à collecter requis
	- le jeu sauvegarde (automatiquement) uniquement la progression lors du passage d'un niveau à l'autre : il n'y pas de checkpoints à l'intérieur d'un niveau
		- SI le joueur quitte/ferme le jeu en plein milieu d'un niveau, il sera reset au début du niveau lorsqu'il relancera le jeu (sa partie)
	- cependant de nombreux éléments persistent explicitement après une mort à l'intérieur du même niveau et sont donc sauvegardés dans la progression du joueur :
		- Un passage secret découvert ne doit plus être révélé après le reset
		- Un bonus HP déjà obtenu ne réapparaît plus
		- Un golden chest ouvert ne réapparaît plus après la mort
		- L'Enchant Juice est à usage unique permanent.

		***Tableau persistance intra-niveau*** :
	
| Élément                     | Mort                                                                    | Changement niveau                                                                                                   | Quitter/recharger partie (en cours de niveau) |                                                                                                                                                                                                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Gold coins                  | **RESET**                                                               | **RESET**                                                                                                           | **RESET**                                     |                                                                                                                                                                                                                                                                                         |
| Shards                      | **RESET** (sauf cas particulier si offrande acceptée voir [[#^e403b9]]) | **SAUVEGARDE** (les prochains shards obtenus au niveau suivant sont accumulés sur la nouvelle base total de shards) | **RESET**                                     | **Exemple sauvegarde de niveau en niveau :** joueur termine niveau 5 avec 50 shards => passe au niveau 6 => 50 shards sauvegardés => il accumule +33 shards au niveau 6 (donc total : 50 +33 = 83) => le joueur meurt niveau 6 => il perd les 33 shards au reset et retombe à 50 shards |
| Arme équipée                | **SAUVEGARDE**                                                          | **SAUVEGARDE**                                                                                                      | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| Amélioration d'arme         | **SAUVEGARDE**                                                          | **SAUVEGARDE**                                                                                                      | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| HP bonus ramassé (obtenu)   | **SAUVEGARDE**                                                          | **SAUVEGARDE**                                                                                                      | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| Golden chest ouvert         | **SAUVEGARDE**                                                          | **N/A**                                                                                                             | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| Passage secret découvert    | **SAUVEGARDE**                                                          | **N/A**                                                                                                             | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| Portes/ chemins secondaires | **RESET**                                                               | **RESET**                                                                                                           | **RESET**                                     |                                                                                                                                                                                                                                                                                         |
| Enchant Juice utilisé       | **SAUVEGARDE**                                                          | **SAUVEGARDE**                                                                                                      | **SAUVEGARDE**                                |                                                                                                                                                                                                                                                                                         |
| Common & Rare chest ouvert  | **RESET**                                                               | **RESET**                                                                                                           | **RESET**                                     |                                                                                                                                                                                                                                                                                         |
	
- équilibrage selon les HP du joueur :
	- le joueur peut augmenter sont nombre max de HP en collectant des bonus HP (voir plus bas) ce qui peut influencer l'expérience de difficulté pour le joueur et surtout pour le combat final du boss.
	- Il faut bien comprendre que :
		- les HP bonus sont des "bonus" rares et plus ou moins difficiles à trouver et procurent uniquement un avantage sans pour autant déséquilibrer le jeu
		- **REGLES D'EQUILIBRAGE** :
			- le jeu se veut difficile mais pas punitif
			- le jeu est pensé pour être battu avec les 7 HP max obtenu normalement, avec une progression de la difficulté au fil des niveaux
			- le boss final est pensé pour être battu avec les 7 HP max obtenu normalement mais sera un combat difficile
			- avoir le max de HP bonus cumulés (14 HP) ne rend pas la difficulté du jeu triviale
			- avoir le max de HP bonus cumulés (14 HP) ne rend pas la difficulté du Boss Final triviale mais offre un avantage
			- le joueur qui ne récolte aucun HP bonus ne doit pas être pénalisé, tout comme celui qui trouve la majorité des HP bonus ne doit être sur-avantagé : les bonus HP sont un **avantage**, pas une condition implicite de victoire.
- équilibrage selon les items/ améliorations du joueur :
	- le joueur peut obtenir de meilleures armes / améliorer le niveau de ses armes
	- il y a ici une notion de scaling assumée : le joueur doit augmenter le niveau de ses armes pour ne pas se retrouver en trop grande difficulté ; le joueur doit tuer des mobs et ouvrir le plus de chest possibles pour avoir une chance d'obtenir des améliorations
		- **REGLES D'EQUILIBRAGE :**
			- le jeu est pensé pour que le joueur augmente le niveau de ses items (armes) au fur et à mesure de la progression
			- le jeu est pensé pour que le joueur arrive dans les derniers niveaux (8, 9, 10) avec une ou deux armes de niveau 2 ou 3 (mêlée + tir) ; idem pour le Boss Final
			- malgré la dimension aléatoire (gamble) assumé des chest, c'est la base du loop d'ouvrir des chest pour améliorer son équipement (comme dans le gameplay de Megabonk)
			- si un joueur n'ouvre aucun chest et garde son arme de départ niveau 0 : la difficulté pourrait être disproportionné (pas prévue pour) mais cela n'engage que le joueur !
			- à l'inverse, posséder une arme Légendaire va volontairement rendre le joueur OP et donner un avantage considérable sur le combat du Boss Final : parti pris assumé compte tenu de la faible chance de drop une légendaire
- en cas de mort du joueur : reset au début du niveau (zone de spawn fixe)
	- le jeu se veut donc difficile (die and retry) avec une part de randomness et une approche rogue lite sans être non plus trop hardcore ni trop punitif
