# Milady's Knight — Player Systems

## système mouvement et plateforme (joueur)
- système mouvement et plateforme (joueur) : interface 2D qui permet un déplacement vertical/horizontal
	- jump entre d'un élément à l'autre ou libre dans l'environnement du niveau
	- jump simple suivant l'impulsion (pression sur la touche) fait varier légèrement la hauteur/ vélocité du saut = variable jump
	- double jump
	- wall jump
	- wall slide
	- déplacement par défaut de gauche à droite
	- déplacement vertical haut/bas par le biais d'éléments du décors (exemple: échelle, corde)
	- **A DEFINIR :**
		- Pour les déplacements : l’accélération horizontale, la décélération, le contrôle aérien, la vitesse de chute maximale, un éventuel coyote time, un jump buffer ou les restrictions après wall jump. Ce ne sont pas forcément des features supplémentaires : ce sont surtout des paramètres de contrôle à décider durant le prototypage.
	
## système de combat (joueur) :
- système de combat (joueur) :
	- attaque mêlée simple : directionnelle continue quand la touche Attaque est maintenue (F) ; touche (hit) le mob quand à portée (RANGE) et inflige dégât au contact
	- attaque à distance (tir) : directionnelle continue quand la touche Attaque est maintenue (F) ; touche le mob et inflige dégât au contact ; les projectiles tirés ont une trajectoire en ligne droite depuis l'emplacement initial du joueur (au moment où il a tiré) ; un projectile à une portée maximale à laquelle celui-ci disparaît s'il n'est entré en contact avec aucun mobs/éléments de terrain
	- attaque sautée (mêlée) : le joueur peut effectuer des attaques de mêlée simple pendant un jump ou un double jump ; il ne peut pas attaquer durant un wall slide
	- attaque d'atterissage (mêlée) : lorsque le joueur est dans les airs UNIQUEMENT APRES un double jump OU une chute de X hauteur (à définir), il peut faire une attaque d'impact à l'atterissage sur le terrain quand la touche (G) est appuyé ; ce type d'attaque permet d'infliger des dégâts de zone autour du joueur lors de l'impact (égal au dégâts de l'arme de mêlée équipée) ; l'attaque a donc une animation dédiée qui fait plonger le joueur directement vers le bas (en ligne droite) depuis son point initial dans les airs (au moment où il appuie sur la touche)
	- les attaques et les dégâts infligés varient selon l'item équipé : type d'item, niveau d'item

## système de transition, pause du jeu
- système de transition :
	- lorsque le joueur meurt : affichage d'un texte en grand sur l'écran de jeu "Thou hast perished." + assombrage de l'écran + effet sonore dramatique = dure 3 sec puis reset automatique du niveau => fondu au noir => chargement => apparition/spawn au début du niveau actuel => jouer ; le joueur n'a pas besoin d'appuyer sur une touche, la partie se relance automatiquement
		- à noter qu'il n'y a jamais de danger immédiat (mobs ni pièges) sur le point de spawn du joueur ; donc même si AFK au reset du niveau après une mort, le joueur ne peut pas mourir
	- lorsque le joueur passe d'un niveau à l'autre : quand le joueur a débloqué la porte finale, il la traverse = animation => fondu au noir => sauvegarde progression => chargement du niveau suivant => apparition/spawn au niveau suivant => jouer
- système de mise en pause :
	- le joueur peut appuyer sur ESC (échap) à tout moment pour mettre le jeu en pause
		- ouvre fenêtre type menu avec 3 choix : REPRENDRE / RECOMMENCER (reset) / QUITTER (quitter le jeu)
	- sauf dans les cas suivants ou ESC ne fonctionne pas car le jeu se met automatiquement en pause :
		- lors de l'animation/ fenêtre de récompense de chest
		- lors d'une fenêtre de contextualisation qui apparaît
		- dans ces cas, le jeu reprend dès le joueur ferme fenêtre /annule récompense/ valide récompense
	- également, lorsque le joueur est en dialogue avec un PNJ (au niveau 1 et au niveau 10), le jeu n'est techniquement "en pause" mais il n'y a pas de dangers pour le joueur et celui-ci ne peut pas se déplacer, ni sauter, ni attaquer (immobilisé) :
		- les dialogues avec PNJ apparaissent sous forme textuel dans un bandeau horizontal au bas de l'écran de jeu
		- les dialogues défilent tout seul, l'un après l'autre, avec une animation (texte qui s'affiche mots par mots)
		- les dialogues peuvent être skip par le joueur en appuyant sur (Space)
		- une fois dialogue terminé ou skip, le jeu reprend (le bandeau disparaît) ; le dialogue ne peut pas être rejoué
 

## système de vie/dégâts/mort du joueur :
- système de vie/dégâts/mort du joueur :
	- **VIE = HP**
		- le joueur commence le jeu (niveau 1) avec 3HP (points de vie) symbolisé par des coeurs (UI) = ce nombre de HP constitue les HP MAX du joueur
		- lors du passage au niveau suivant, le joueur récupère tout ses HP perdus précédemment (soigné) = il démarre le niveau full HP = HP MAX
		- lors du reset à la mort du joueur ou reset (relancer la partie/niveau actuel), le joueur récupère tout ses HP perdus précédemment (soigné) = il démarre le niveau full HP = HP MAX
		- upgrade auto à partir du niveau 5, le joueur démarre maintenant avec 5HP
		- upgrade auto à partir du niveau 8, le joueur démarre maintenant avec 7HP
		- lorsque le joueur passe un niveau avec palier de HP MAX, il est également automatiquement soigné
			- exemple : joueur termine niveau 4 avec 1HP restant => passe au niveau 5 => démarre le niveau 5 avec full HP donc 5HP MAX
			- autre exemple : joueur termine niveau 2 avec 0.5HP restant => passe au niveau 3 => démarre le niveau 3 avec full HP donc 3HP MAX
		- le joueur peut récupérer des HP bonus au cours de sa progression : ces points de vie sont généralement cachés dans le niveau et doivent être récoltés (ramassé) comme des coins. Une fois récupéré, il donne +1 MAX HP permanant au joueur (cumulatif). Ces HP bonus peuvent être obtenu dans des niveaux définis :
			- niveau 4 : 1 HP bonus à trouver
			- niveau 5 : 1 HP bonus à trouver
			- niveau 7 : 2 HP bonus à trouver
			- niveau 9 : 3 HP bonus à trouver
		- il ne sera pas indiqué au joueur où ni combien de HP bonus il peut trouver mais un indice subtile devra être laissé dans le niveau 4 (à définir)
		- attention un HP bonus déjà obtenu lors d'une tentative ne réapparaîtra pas lors d'une nouvelle tentative du joueur dans ce même niveau !
	- **DEGATS = DAMAGE**
		- les dégâts reçus sont directement imputés aux HP du joueur
		- il n'y pas de système d'armure, ni de blocage, ni de résistance quelconque aux dégâts
		- selon les dégâts du mob, le joueur peut perdre 0,5 HP, 1HP, 2HP, 3HP ou plus par coups (attaques).
		- la perte d'HP suite à des dégâts reçu constitue les CURRENT HP du joueur
			- exemple : joueur possède 3 HP MAX, il subit 1 DMG d'une attaque de mob => joueur possède 2 CURRENT HP
	- **REACTION AUX DEGATS**
		- lorsque le joueur subit un dégât, plusieurs effets s'appliquent :
			- invincibilité temporaire : fenêtre de 1,20 s après un hit durant laquelle le joueur ne peut pas subir de dégâts (ajustement RUN-007 validé après audit ; le vide reste fatal) = éviter de subir plusieurs collisions consécutives selon l'implémentation et/ou si le joueur se retrouve "coincé" dans un ou plusieurs ennemis
			- hit-stun : fenêtre de 0,18 s parallèle à l'invincibilité temporaire durant laquelle le joueur ne peut pas effectuer d'attaques
			- knockback : au moment où il subit un dégât, le personnage est légèrement repoussé en arrière (dans le sens opposé de l'attaque) ; fenêtre de 0,16 s durant laquelle le joueur ne peut pas effectuer de jump
			- interruption d'attaque : si le joueur appui sur attaquer au même moment où il subit un dégât, l'action d'attaque est interrompue (annulé)
			- feedback RUN-007 : flash blanc opaque de 0,10 s puis clignotement contrasté (alpha 0,25/1 par phases de 0,10 s) jusqu’à la fin de l’invulnérabilité. La pause suspend ces effets avec les compteurs ; la mort supprime le flash et restaure l’opacité.
			- les durées de recul/hit-stun sont conservées après audit ; l’équilibrage final reste à confirmer par essai humain. Les ronces poussent horizontalement loin de leur centre, avec repli opposé au regard si les centres sont alignés.
		- cas où tous les effets ci-dessus s'appliquent : 
			- le joueur subit un dégâts suite à une collision avec un mob : Slimes
			- le joueur subit un dégâts suite à une attaque de mêlée d'un mob : Skeleton Warrior, Sorcerer, mobs d'élite, Boss
		- cas où les effets ci-dessus s'appliquent différemment :
			- le joueur subit un dégâts suite à une collision avec un piège : invincibilité temporaire et knockback = oui ; hit-stun et interruption d'attaque = non
			- une flamme qui blesse le joueur suit le profil du piège : invincibilité temporaire et knockback = oui ; hit-stun et interruption d'attaque = non (décision RUN-006)
			- le joueur subit un dégâts suite à une attaque de tir d'un mob (Skeleton Archer) :  invincibilité temporaire et interruption d'attaque = oui ; knockback et hit-stun = non
			-  le joueur subit un dégâts suite à une collision avec un piège à projectiles (tir des mini-tourelles) : invincibilité temporaire et interruption d'attaque = oui ; knockback et hit-stun = non
			- le joueur subit un dégâts suite à une collision avec un mob swarm (Possessed Skulls) : invincibilité temporaire uniquement
	- **ATTAQUES = HIT/ COUPS**
		- une attaque est l'action de donner des coups/hit
		- une attaque de mêlée donne des hit répétés en continus lorsque la touche d'attaque est maintenue (hold) ; idem pour le tir ; hold (F)→ attaques (hits) répétées selon ATK SPEED de l'arme équipée
		- les attaques infligent des dégâts basés sur les DMG de l'arme équipée et de son ATK SPEED (= DPS)
		- le système doit garantir qu’une attaque ne provoque qu’un nombre de hits prévu et ne puisse pas infliger des dégâts à chaque frame physique : l’ATK SPEED correspond à un intervalle en secondes => cette règle doit rester la référence du système de dégâts
		- présentation de la mêlée (décision RUN-029) : les hits successifs d’une attaque maintenue enchaînent visuellement trois mouvements d’épée (taille, revers fendant, frappe à deux mains), puis reprennent au premier ; l’animation continue entre deux hits tant que F est maintenue. Chaque mouvement reste un seul hit : dégâts, ATK SPEED, fenêtre et zone de contact sont identiques
	- **MORT = RESET**
		- quand les HP du joueur sont réduit à zéro : mort du joueur et reset de la progression au début du niveau.


## RUN-019 — Bonus HP et Magic Shield, contrat validé le 5 octobre 2026

Bonus unique : +1 MAX HP et +1 CURRENT HP (1/3→2/4), sauvegarde du flag avant attribution. Reset/reprise soigne au nouveau maximum. Aucun soin par acquisition d'équipement. Sept bonus possibles dans la campagne spécifiée ; les paliers N5/N8 restent RUN-023.

Shield : dix secondes de gameplay, rafraîchissement à dix sans cumul, suspendu par pause/modales ; échange d'arme sans effet. Révision RUN-020 du 6 octobre : protection contre tous les dégâts (contact/mêlée, projectile/sort au sol, swarm, pièges solides, flammes et tirs de tourelles), sans réaction sur un impact bloqué. Le vide reste mortel, confirmé explicitement par l’humain. Mort/vide/reset/reprise/changement de niveau suppriment le buff. Les scènes de pickup, timers et interactions sont testés en fixture ; art/SFX et validation humaine attendus.
