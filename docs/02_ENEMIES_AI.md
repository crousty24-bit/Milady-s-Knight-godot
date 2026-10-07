# Milady's Knight — Enemies, AI & NPC

## système de combat (IA) :
- système de combat (IA) :
	- ennemi de base (exemple Slime) : inflige des dégâts lors de collision avec joueur
	- ennemi avancé : attaques de mêlée ou à distance suivant le type de mob
	- ennemi élite : mob rare avec mécanique de combat unique dédiée
	- boss final unique
	- pièges : piques au sol, plantes toxiques, trappes, etc.
	- **REACTION AUX DEGATS**
		- lorsqu'un mob subit un dégât, l'effet suivant s'applique :
		- knockback : au moment où il subit un dégât, le mob est légèrement repoussé en arrière (dans le sens opposé de l'attaque)
			- sauf exception : Possessed Skulls
		- les mobs ne sont pas sujets à l'invincibilité temporaire, hit-stun, interruption d'attaque
			- RUN-007 : Green/Purple conservent leur impulsion de recul pendant 0,12 s, puis reprennent leur patrouille. Le contact reste dangereux pendant ce recul et un autre impact est accepté immédiatement ; la teinte jaune est un feedback visuel, sans immunité.

## bestiaire des PNJ :
- il y a 2 PNJ dans le jeu : 
	- il n'y a pas d'interaction spécifique avec les PNJ hormis servir à la narration et/ou au guide du joueur
	- **Princess Karla :** il s'agit de la princesse à retrouver et à délivrer dans le niveau final
		- présente dans le niveau 10
		- dialogue narratif de fin avec le joueur lorsque celui-ci a battu le Boss et la délivre
	- **The Ancien Spirit :** esprit d'un sage du Royaume ayant ramené le chevalier à la vie à qui il donne la quête de secourir la Princess Karla et sauver le Royaume de la corruption.
		- présent dans le niveau 1, au tout début du niveau
		- dialogue narratif avec le joueur pour présenter l'histoire et le but du jeu

## bestiaire mobs (IA) :
- bestiaire mobs (IA) :
	- ennemis de base :  Green Slime ; Purple Slime ; Red Slime
	- ennemis avancé : Skeleton Warrior ; Skeleton Archer ; Blight Sorcerer ; Possessed Skulls
	- ennemis d'élite : Bloated Slime ; Chud Blob ; Chaos Champion ; Necromancer
	- boss : le boss final du jeu

## profil des mobs (IA) :
- profil des mobs (IA) : attaques, dégâts et HP
	- le profil des mobs varient suivant le niveau dans lequel on se situe. Exemple, un Red Slime présent dans le niveau 1 et 2 n'a pas le même profil que celui présent dans le niveau 7 ou 8 = montée en difficulté. Voir ci-dessous.
	- les mobs peuvent infliger des dégâts plein (1, 2, 3 DMG) et des demi-dégâts (0,5 ; 1,5 ; 2,5 DMG) au joueur selon leur profil
	- excepté le boss final, les dégâts min/max des mobs vont de 0,5 à 3 DMG.
	- **CONCEPTS DE BASE :**
		- **comportement de base : patrouille**
			- par défauts, tous les mobs opèrent un déplacement de patrouille
			- ce déplacement est fixe, allant d'une position à l'autre sur le terrain
			- ce déplacement consiste en allers-retours (A <--> B) en boucle
			- ce pattern de comportement est rompu lorsqu'un mob prend l'aggro du joueur
		- **mouvement des mobs : déplacement**
			- un mob peut avoir une vitesse de déplacement de base : lente, modérée ou rapide
			- la vitesse de déplacement du mob dépend de son type et du niveau dans lequel il se situe
			- il faut distinguer 2 vitesse de déplacement du mob :
				- vitesse de base : c'est sa vitesse de déplacement lors des patrouilles
				- vitesse d'aggro : c'est sa vitesse de déplacement lors de l'aggro du joueur
				- la vitesse d'aggro est toujours un peu plus élevée que la vitesse de base
				- exemple : un Skeleton Warrior en patrouille à une vitesse de base lente ; il aggro le joueur et se dirige vers lui avec une vitesse d'aggro modérée
				- les *Green, Purple et Red Slimes* n'ont qu'une vitesse de base
		- **système aggro :** un mob aggro le joueur lorsque celui-ci entre un périmètre fixe (zone) défini par rapport à sa position initiale
			- ce périmètre peut être plus ou moins large selon le type de mob
			- ce périmètre est horizontal et vertical
			- le point de départ du périmètre est le mob et est attaché à lui : il se déplace selon le déplacement du mob (exemple : le mob patrouille d'un point A vers B en aller-retour, son périmètre se déplace avec lui)
			- le mob perd l'aggro après le délai de perte hors de son périmètre de conservation (réglages N2–4 ci-dessous) et retourne à son déplacement de patrouille initial
			- un mob qui a l'aggro est toujours attiré vers le joueur, son déplacement est directement en direction du joueur et déclenche une attaque lorsqu'il est à portée de celui-ci
			- les *Green, Purple et Red Slimes* n'ont pas de système d'aggro
	
	- **SLIMES (niveau 1 à 4) :**
		- *Green Slime* : 1 HP | 0,5 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée  ; pas de système d'aggro
		- *Purple Slime* : 2 HP | 1 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; pas de système d'aggro
		- *Red Slime* : 2 HP | 1,5 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; pas de système d'aggro
	- **SLIMES (niveau 5 à 9) :**
		- *Green Slime* : 2 HP | 1 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée à rapide ; pas de système d'aggro
		- *Purple Slime* : 3 HP | 2 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée à rapide ; pas de système d'aggro
		- *Red Slime* : 3 HP | 3 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée à rapide ; pas de système d'aggro
	- **SKELETONS (niveau 3 et 4) :**
		- *Skeleton Warrior* : 2 HP | 0,5 DMG | attaque de mêlée (sword, axe)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Skeleton Archer* : 2 HP | 0,5 DMG | attaque à distance (arc)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob attaque le joueur à distance (sans se déplacer) mais perd l'aggro si joueur quitte le périmètre
		- *Blight Sorcerer* : 2 HP | 0,5 DMG et 2 DMG | attaque de mêlée (bâton) + attaque au sol à distance = surface au sol qui explose à esquiver (environ 1sec de temps avant dégâts infligés)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Possessed Skulls* : 1 HP | 0,5 DMG | swarm (plusieurs entités) attaque au contact avec joueur (collision)
			- pattern comportement : spawn lorsque le joueur entre dans un périmètre défini ; vitesse modérée ; la swarm (plusieurs skulls) aggro directement le joueur : se déplace plus ou moins directement vers le joueur infligeant dégât au contact mais perd l'aggro si joueur quitte le périmètre
			- si joueur quitte le périmètre de spawn défini, les skulls disparaissent (despawn) et spawn si le joueur entre à nouveau dans ce même périmètre
	- **SKELETONS (niveau 5 et 9) :**
		- *Skeleton Warrior* : 3 HP | 1 DMG | attaque de mêlée (sword, axe)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Skeleton Archer* : 2 HP | 1 DMG | attaque à distance (arc)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente à modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob attaque le joueur à distance (sans se déplacer) mais perd l'aggro si joueur quitte le périmètre
		- *Blight Sorcerer* : 2 HP | 1 DMG et 2,5 DMG | attaque de mêlée (bâton) + attaque au sol à distance = surface au sol qui explose à esquiver (environ 1sec de temps avant dégâts infligés)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Possessed Skulls* : 1 HP | 0,5 DMG | swarm (plusieurs entités) attaque au contact avec joueur (collision)
			- pattern comportement : spawn lorsque le joueur entre dans un périmètre défini ; vitesse rapide ; la swarm (plusieurs skulls) aggro directement le joueur : se déplace plus ou moins directement vers le joueur infligeant dégât au contact mais perd l'aggro si joueur quitte le périmètre
			- si joueur quitte le périmètre de spawn défini, les skulls disparaissent (despawn) et spawn si le joueur entre à nouveau dans ce même périmètre
	- **MOBS ELITES (niveau 2 et 4) :**
		- *Bloated Slime* : 5 HP | 1,5 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Chud Blob* : 10 HP | 2 DMG | attaque de mêlée (sword, axe)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
	- **MOBS ELITES (niveau 5 à 9) :**
		- *Bloated Slime* : 8 HP | 2 DMG | attaque au contact avec joueur (collision)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Chud Blob* : 14 HP | 3 DMG | attaque de mêlée (sword, axe)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse lente ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
		- *Chaos Champion* : 20 HP | 3 DMG | attaque de mêlée (sword, axe)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse rapide ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
			- capacité spéciale : charge. Uniquement lors du premier aggro, le mob charge le joueur = double sa vitesse de déplacement et se dirige directement vers le joueur ;  SI entre en contact avec le joueur à l'issu de la charge, trigger une attaque de mêlée instantanée, dangereuse, clairement télégraphiée, mais systématiquement évitable par maîtrise ; cette capacité reset à chaque fois que le joueur perd l'aggro, donc si reprise de l'aggro = charge
		- *Necromancer* : 16 HP | 2 DMG et 3 DMG | attaque de mêlée (bâton) + attaque au sol à distance = x3 surfaces au sol simultanément qui explosent à esquiver (moins d'une 1sec de temps avant dégâts infligés)
			- pattern comportement : déplacement fixe type patrouille, allers-retours (A <--> B) ; vitesse modérée ; changement de comportement quand en ligne de vue du joueur (périmètre) = aggro : le mob se déplace vers le joueur pour l'attaquer mais perd l'aggro si joueur quitte le périmètre
			- capacité spéciale : tant que le Necromancer est en vie, il invoque des *Possessed Skulls* dans son périmètre d'aggro tant le joueur est présent à l'intérieur de celui-ci ;  SI le joueur qui le périmètre et perd l'aggro du mob, les *Possessed Skulls* disparaissent. Il y a un timer auquel le Necromancer peut les invoquer : au bout des premières 3 secondes d'aggro avec le joueur puis toutes les 5 secondes ; reset le timer quand le joueur perd l'aggro
		- **BOSS FINAL (niveau 10) :**
			- *BOSS* : 50 HP | 3 DMG et 5 DMG | attaque de mêlée + attaque au sol à distance = x4 surfaces au sol simultanément qui explosent à esquiver (moins d'une 1sec de temps avant dégâts infligés) + attaque à distance (comme un Skeleton Archer) mais tires boules de feu, à vitesse lente, en direction du joueur
				- pattern comportement : pas de système d'aggro/reset = le combat commence directement et le boss reste focus sur le joueur jusqu'au bout ; vitesse modéré
				- capacité spéciale : charge. Pas le même comportement que pour le Chaos Champion mais même effet. Première charge au début du combat puis système aléatoire calculé toutes les 20 secondes : 30% de chances que le Boss fasse une charge sur le joueur peu importe sa position.
				- capacité spéciale : invocation de *Possessed Skulls* (idem que Necromancer sauf pour le timer = au bout des 10 premières secondes de combat puis toutes les 15 secondes)
				- capacité spéciale : lorsque les HP du Boss atteignent <= 20HP, il devient enragé = double vitesse de déplacement et augmente la vitesse de toute ses d'attaques ; l'invocation de *Possessed Skulls* n'est pas impactée


## RUN-019 — Comportements N2–4 implémentés

Les profils N2–4 ci-dessus sont livrés comme scènes réutilisables et fixtures. Révision RUN-020 du 6 octobre (comportement alors livré, remplacé pour la locomotion par RUN-021 ci-dessous) : aggro terrestre acquise avec visibilité dans un rectangle 480×96 px attaché au mob (±240 px horizontalement). Conservation dans 640×160 px ; perte après 2 s continues hors enveloppe ou sans visibilité, timer suspendu en pause et remis à zéro à la revue du joueur. Mort du joueur : perte immédiate. Aucune nouvelle attaque déclenchée à travers le terrain. La poursuite s’arrêtait alors aux bords/obstacles ; Archer était stationnaire en aggro. La perte d'aggro annule une préparation non libérée ; projectiles/zones libérés terminent leur cycle, sauf mort de la source qui les supprime.

Sorcerer : point au sol capturé au lancement, avertissement1s puis impact unique2DMG avec profil projectile ennemi. Skulls : zone N4 de 480×240 px, quatre emplacements par tentative. Sortie : disparition des survivants ; réentrée : seuls les emplacements non vaincus réapparaissent. Un crâne tué ne revient plus avant mort/restart du niveau ; zone nettoyée = vide pour la tentative. Un shard par emplacement vaincu, maximum quatre ; aucun soin. Cette swarm est indépendante du Blight Sorcerer, qui ne l’invoque pas et dont la mort ne la supprime pas. Les profils N5–9 et invocations Necromancer/Boss ne sont pas implémentés dans ce lot.

Les paramètres techniques exacts et interfaces sont dans [le handoff](RUN-019_CLAUDE_HANDOFF.md), les décisions validées dans [le contrat](RUN-019_CONTRACT_REVIEW.md). Dessins provisoires et Red teinté ne constituent pas un habillage final ; contribution Claude P0 et playtest encore requis.

### RUN-020 — Volumes des élites après reprise visuelle

Les silhouettes redessinées utilisent un corps physique centré sur leur masse, pieds à l’origine : Bloated 44×40, Chud 36×40. Le volume sert aux collisions avec le terrain et à la réception des coups ; les excroissances et l’arme restent hors de ce rectangle. Les sondes de bord se placent 4 px devant la demi-largeur réelle du corps. Bloated inflige son contact sous 30 px horizontalement et 18 px verticalement entre les pieds, avec ligne libre et aggro ; Chud garde sa mêlée de 28 px et sa préparation de 0,3 s. Le sprite du chevalier se dessine au premier plan des acteurs pour rester visible au contact.


## Réglage RUN-021 après remise visuelle (6 octobre 2026)

La logique considère désormais un intervalle de patrouille nul ou inversé comme une sentinelle : hors aggro, vitesse horizontale nulle et orientation conservée, y compris après un recul. La gravité, les collisions et le recul restent actifs. Les six archers N3/N4 gardent leurs bornes nulles et leur placement ; aucune cellule de terrain ni donnée de niveau n’est remplacée. Une patrouille positive garde ses retournements et ses sondes de bord. Le défaut ancien de retournements continus est reproduit puis corrigé dans le moteur ; la correspondance exacte avec la vidéo humaine reste non confirmée.

Pour Archer et Blight Sorcerer seulement, acquisition avec visibilité dans720×144px (±360 horizontal, ±72 vertical), conservation880×208px avec la marge existante, délai de perte2s inchangé. La distance de déclenchement du tir/de la zone passe de140 à240px. L’archer poursuit désormais à22px/s pendant l’aggro, y compris hors de sa portée de tir ou lorsque la ligne de tir est bloquée ; il ne tire qu’au sol, à portée et avec ligne de vue libre. Sa flèche conserve vitesse150px/s et durée maximale5s ; « portée240 » désigne ici la distance de déclenchement, pas une suppression à240px du projectile. Sorcerer conserve point au sol figé, avertissement1s et2DMG. La ligne de vue garde son rôle pour acquérir l’aggro et déclencher les attaques.

Bloated poursuit à60px/s (36 avant) et Chud à48px/s (28 avant), avec patrouilles18/12px/s conservées. Corps44×40/36×40, contact Bloated30px, mêlée Chud28px, dégâts et préparation restent identiques. Le joueur marche à sa vitesse existante. Ces réglages sont validés par le playtest de la passe précédente ; le nouveau franchissement ci-dessous reste à essayer.


### Poursuite RUN-021 — obstacles franchissables

Sur demande humaine après playtest, les Green, Purple et Red Slimes gardent leur locomotion actuelle et ne poursuivent pas le joueur. Tous les autres mobs concernés — Skeleton Warrior, Skeleton Archer, Blight Sorcerer, Bloated Slime et Chud Blob — tentent de rejoindre le joueur pendant l’aggro en franchissant physiquement les obstacles praticables. Bloated est explicitement inclus malgré son nom de Slime. Les Possessed Skulls contournent les solides en vol. Les coffres et objets ramassables sont des zones d’interaction et ne constituent pas des obstacles physiques.

La locomotion terrestre sonde localement les appuis, l’espace du corps et le dégagement du saut ; elle peut monter jusqu’à72px, avec un saut plafonné à environ82px de hauteur, franchir un vide seulement si la portée horizontale du saut le permet et descendre jusqu’à72px, soit la même hauteur que les blocs franchissables en montée. La sonde descendante inclut la marge de contact du corps pour ne pas manquer le sol au bord de cette limite. Les ennemis ne traversent ni murs ni plafonds. Ils conservent les collisions physiques et s’arrêtent si aucun trajet sûr local n’est praticable. Les Skulls contournent également sans traverser les solides. Ces limites décrivent le saut borné, pas un pathfinding global.

L’acquisition, le rectangle de conservation et le délai nominal de perte de 2 s restent identiques. Un saut vers un appui vérifié, une avancée réelle sur un appui vers le joueur ou un recul réel le long d’un détour vérifié réarment la tolérance d’occlusion si la cible reste dans le rectangle de conservation. Une cible hors de ce rectangle est toujours perdue après 2 s ; un mob physiquement bloqué ne réarme pas ce délai par une simple intention de mouvement. Les portées de tir ne changent pas. L’Archer garde sa poursuite à22px/s et ne lance son tir que s’il est au sol, à portée et en ligne de vue libre.

**Plateformes suspendues — reprise du 7 octobre 2026.** Le sol praticable sous une plateforme est sondé depuis la hauteur des pieds : le dessus du toit ne masque plus ce passage. Quand un obstacle ferme le passage inférieur ou que le joueur se trouve sur le toit, le mob peut reculer vers un bord dégagé, sauter dessus puis reprendre sa poursuite. Le détour est local, recherché sur144px au maximum, avec appui de même hauteur, dégagement du corps et corridor de saut vérifiés ; il ne franchit pas un vide ou un mur à reculons. La montée/descente reste limitée à72px. Le détour s’annule si la cible change de côté, meurt ou sort de la conservation d’aggro, ou si le passage prévu se bloque. Ce comportement ne constitue pas un pathfinding global ni une garantie de franchir toute géométrie.
