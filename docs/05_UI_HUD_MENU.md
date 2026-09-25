# Milady's Knight — UI, HUD & Menu

## 2. UI/HUD & menu :

##### Key Features

- 1 Menu Principal (New Game / Continue / Controls / Quit)
- 1 Ecran de lancement du jeu avec artwork
- 1 Ecran de chargement au lancement de la partie / retour au menu
- UI/HUD minimalist rétro qui affiche en haut de l'écran : cadre avatar du joueur / HP / 2 slots d'équipement / gold coins / shards
- Fenêtres d'interactions ou d'informations (tutoriels, "vous êtes mort" etc.)
- Affichage de textes lors des dialogues narratif (PNJ) avec avatar dans un bandeau au bas de l'écran
- Icon pour chaque item (armes, potions, etc.)
- Le jeu est entièrement en anglais

##### Wireframes concept UI

- **UI/HUD**
	- l'interface de base sur l'écran de jeu d'un partie en cours
	- elle affiche dans la zone supérieure gauche : 
		- l'avatar du joueur : purement stylistique, n'apporte aucune information sur le gameplay => **A DEFINIR** si pertinent (après premiers playtests réels) où si consomme trop d'espace et gène visuellement
		- les HP du joueur répartis sur 2 lignes, icon coeurs : les coeurs s'affichent visuellement par coeurs entiers ou par demi-coeurs
			- pour les HP fractionnaires, la valeur numérique reste exacte ; l'icône arrondit vers le demi-cœur supérieur afin qu'un joueur encore vivant conserve un demi-cœur visible (décision RUN-006)
		- un compteur de gold coins avec une icon : x gold coin /12
		- un compteur de shards : doit afficher les current shards collectés (+35) et les saved shards (/50)
		- les 2 slots d'armes affichés verticalement : slot 1 (mêlée) et slot 2 (tir)
			- affiche icon arme + couleur rareté d'item + nom (type d'arme) + niveau de l'arme
	- elle affiche dans zone inférieure :
		- un bandeau de dialogue sur toute la largeur de l'écran (de gauche à droite) : s'affiche uniquement lors des dialogues avec les PNG ; indique l'option de passer rapidement les dialogues avec (SPACE) - Skip

![[HUD UI 1 1.png]]

- **UI/HUD + fenêtre de contextualisation**

![[HUD UI FENETRE CONTEXT.png]]

- **UI/ HUD + message mort du joueur**

![[HUD UI MESSAGE MORT JOUEUR.png]]

- **UI/ HUD dynamique : états actifs**
	- affichage dynamique lors du ramassage des consommables et de la collecte des gold coin, shards, HP bonus : s'affichent brièvement avec une animation autour du personnage joueur
	- affichage dynamique avec animation lors du changements d'état des HP joueur : perte d'HP, gain HP
	- affichage dynamique avec animation lors de mise à jour des gold coin et des shards
	- slot équipement actif : focus visuel clair et distinct
	- affichage des effets consommables dans coin supérieur droit : icon + durée restante d'effet du Magic Shield et/ou du Rage Drink
	- le cooldown pour capacité arme légendaire (Dragon Slayer) + cooldown utilisation Fire Gauntlet : une jauge translucide se rempli progressivement dans le slot de l'arme pour signifier le cooldown = lorsque jauge a rempli le slot => cooldown passé et utilisation possible
		- il faut prévoir une petite animation lorsque la jauge de cooldown est passée pour marquer visuellement au joueur que la capacité/utilisation est disponible

![[HUD UI 1 DYNAMIQUE ACTIF.png]]

![[HUD UI FOCUS SLOT ACTIF.png]]

- **UI/ HUD dynamique : BOSS FINAL**
	- affiche la barre de vie rouge du Boss

![[HUD UI BOSS FINAL.png]]

- **UI/ HUD + fenêtre récompense ouverture de chest

![[HUD UI FENETRE OPEN CHEST.png]]

- **UI/ HUD + fenêtre récompenses chest
	- le joueur sélectionne un slot de récompense avec touches fléchées (gauche, droite)
	- focus visuel distinct sur le slot actif = slot sélectionné (exemple : bordure, glow)

![[FENETRE RECOMPENSE CHEST.png]]

- **UI/ HUD + fenêtre récompenses golden chest

![[FENETRE RECOMPENSE GOLDEN CHEST.png]]

- **MENU PRINCIPAL
	- le menu vertical avec les boutons : New Game / Continue / Controls / Quit
	- Continue est désactivé en l’absence de sauvegarde
	- bouton menu sélectionné : focus visuel
	- affiche le logo du jeu centré en haut
	- le background affiche un artwork du jeu

![[MENU PRINCIPAL.png]]

### Règles générales de comportement UI / HUD

> **Statut : règles de comportement de référence — à préciser, normaliser et documenter avec Astra lors de la phase d'implémentation.**

L'interface doit rester simple, lisible et cohérente avec un jeu jouable uniquement au clavier.

Les règles ci-dessous définissent le comportement général attendu de l'UI sans figer encore les valeurs exactes, dimensions, timings ou détails d'implémentation.

#### Priorité d'affichage et superposition

Les différents éléments de l'interface doivent respecter une hiérarchie claire afin d'éviter les conflits visuels.

Les fenêtres modales importantes doivent être prioritaires sur le HUD permanent.

Exemple de priorité générale :

**bandeau de dialogue / récompense / contextualisation → messages système → HUD permanent → éléments dynamiques temporaires**

Deux fenêtres modales importantes ne doivent pas être affichées simultanément.

Lorsqu'une fenêtre modale nécessitant une décision du joueur est ouverte, les interactions de gameplay doivent être bloquées ou mises en pause selon le contexte.

#### États visuels des éléments UI

Les éléments interactifs doivent pouvoir disposer de plusieurs états visuels clairement différenciés :

- normal ;
    
- sélectionné / focus ;
    
- indisponible / disabled ;
    
- actif ;
    
- cooldown ;
    
- interaction impossible.
    

Le focus clavier doit toujours être facilement identifiable.

Un élément indisponible doit rester compréhensible mais visuellement distinct d'un élément actuellement utilisable.

#### Navigation clavier

La navigation dans les menus et fenêtres doit suivre une logique commune dans tout le jeu.

Convention générale :

- **flèches directionnelles** : déplacer la sélection ;
    
- **E** : interagir / confirmer ;
    
- **ESC** : annuler / fermer / revenir en arrière ; mettre en pause (en cours de partie)
    
- **Space** : skip dialogue.
    

Une même action ne doit pas changer arbitrairement de touche entre différentes fenêtres.

Les règles exactes devront être normalisées avec Astra afin que les key binds documentés constituent une source de vérité unique.

#### Feedback des interactions impossibles

Lorsqu'une interaction existe mais ne peut pas être réalisée, le joueur doit recevoir un feedback immédiat.

Exemples :

- coffre nécessitant plus de shards que le joueur n'en possède ;
    
- porte finale nécessitant davantage de gold coins ;
    
- porte secondaire inaccessible ;
    
- capacité ou arme actuellement en cooldown ;
    
- option de menu indisponible.
    

Le feedback peut utiliser :

- changement de couleur ;
    
- état visuel disabled ;
    
- courte animation ;
    
- texte contextuel ;
    
- effet sonore.
    

Une interaction impossible ne doit pas ouvrir inutilement une nouvelle fenêtre.

#### Lisibilité à la résolution de référence

L'ensemble de l'interface doit être conçu pour rester lisible directement à la résolution interne de référence du jeu.

Les textes, icônes, compteurs et états importants ne doivent pas dépendre de l'upscale vers une résolution supérieure pour devenir compréhensibles.

Le rendu final doit conserver une bonne lisibilité après integer scaling.

#### Safe margins

Les éléments permanents du HUD et les textes importants doivent conserver une marge cohérente avec les limites de l'écran.

Les informations critiques ne doivent pas être collées directement aux bords du viewport.

Une valeur standard de marge devra être définie ultérieurement pour uniformiser l'ensemble de l'interface.

#### Typographie

Le jeu doit utiliser une direction typographique cohérente avec son esthétique pixel-art et Dark Fantasy.

Une police principale commune doit être privilégiée pour la majorité de l'interface.

Des variantes de taille peuvent être utilisées selon le contexte :

- HUD ;
    
- menu ;
    
- titre ;
    
- dialogue ;
    
- message système ;
    
- contextualisation.
    

**La lisibilité reste prioritaire sur l'esthétique.**

Les textes affichés pendant le gameplay doivent rester courts et immédiatement compréhensibles.

#### Actions destructrices ou irréversibles

Certaines actions importantes peuvent demander une confirmation supplémentaire afin d'éviter les erreurs accidentelles.

Exemples possibles :

- commencer une New Game lorsqu'une sauvegarde existe déjà ;
    
- recommencer le niveau ;
    
- quitter la partie ;
    
- accepter certaines décisions permanentes.
    

Le niveau exact de confirmation devra rester limité afin de ne pas créer de friction inutile.

#### Écran Controls

Le menu principal contient une section **Controls**.

Cette section doit présenter clairement les touches utilisées dans le jeu et leur fonction.

Le joueur doit pouvoir revenir au menu précédent avec **ESC**.

À ce stade, aucun système de remapping des touches n'est prévu.

#### Écrans de chargement et transitions

Les écrans de chargement doivent rester simples et cohérents avec la direction artistique générale.

Ils peuvent afficher :

- artwork ;
    
- logo du jeu ;
    
- éventuellement une courte indication contextuelle.
    

Le contenu exact devra être défini en fonction de la durée réelle des chargements et des transitions.

#### Cohérence avec la palette fonctionnelle

L'UI doit utiliser les mêmes associations de couleurs fonctionnelles que le reste du jeu.

Exemples :

- rouge : HP / dégâts / danger ;
    
- or / jaune : gold coins / Legendary ;
    
- violet : shards ;
    
- vert : soin ;
    
- cyan / bleu : Magic Shield ;
    
- rouge-orange : Rage ;
    
- blanc / jaune pâle : interaction neutre.
    

Ces codes visuels doivent rester cohérents entre HUD, fenêtres, collectibles, VFX et messages contextuels.

#### Éléments permanents et contextuels

Les informations essentielles doivent rester visibles en permanence pendant le gameplay normal :

- HP ;
    
- armes équipées ;
    
- gold coins ;
    
- shards.
    

Les informations secondaires doivent apparaître uniquement lorsqu'elles sont nécessaires :

- effets temporaires ;
    
- cooldowns ;
    
- prompt d'interaction ;
    
- contextualisation ;
    
- dialogue ;
    
- récompense ;
    
- message système.
    

L'objectif est de limiter l'encombrement permanent de l'écran.

#### Principe général

L'UI doit donner une information claire uniquement lorsque celle-ci est utile.

Chaque feedback visuel doit répondre à au moins une question du joueur :

- que puis-je faire ?
    
- que suis-je en train de sélectionner ?
    
- pourquoi cette action ne fonctionne-t-elle pas ?
    
- quel état est actuellement actif ?
    
- quelle ressource ai-je gagnée ou dépensée ?
    
- combien de temps reste-t-il avant qu'une capacité ou un effet soit disponible ?
    

Les règles précises de priorité, dimensions, marges, timings, transitions, couleurs et animations UI devront être définies plus rigoureusement avec Astra lors de la documentation technique du projet.

---
