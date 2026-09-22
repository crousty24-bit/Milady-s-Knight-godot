# Milady's Knight — Project Vision & Scope

Jeu retro pixel-art 2D action-platformer inspiré par des mécaniques Rogue-lite. On incarne un chevalier ordonné de sauver la princesse d'un Royaume déchiré par la corruption.

Le jeu est un prototype similaire à une démo. Le rendu final doit être une démo jouable et testable dans une première version 0.x.0.

## 1. Gameplay :

##### Core Features

*Concept global* : le joueur incarne un chevalier qui doit traverser plusieurs niveaux afin de délivrer la princesse du royaume. Chaque niveau augmente en difficulté. Le joueur doit accumuler un nombre de gold coin minimal lui permettant de déverrouiller une porte par offrande afin d'accéder au niveau suivant. Le joueur doit parcourir les niveaux en combattant des monstres, éviter des pièges et améliorer son équipements grâce à des chest qu'il doit déverrouiller avec des shards. Le dernier niveau consiste à battre le Boss Final ce qui permet de délivrer la princesse et terminer le jeu.

- **Platformer 2D**
- **Action**
- **Rogue-lite inspired**
- **Progression par niveaux**
- **Ouverture de chest & améliorations**
- **Tuer des mobs**
- **Eviter des pièges, tomber dans le vide**
- **Ouverture de portes, passages dérobés secrets**
- **Système de combat (mêlée et distance) et aggro**
- **Mécaniques uniques propres à certains mobs ou item**
- **Loot de consommables**
- **Collecter des gold coins**
- **Vaincre le Boss final**

Ces features sont expliquées en détails plus bas.

*Game Loop :*

**exploration → coins de progression → combat → shards → coffres → amélioration → exploration plus risquée → porte de sortie →  sortie du niveau → niveau suivant.**

Le jeu combine 3 formes de progression :

- progression spatiale : atteindre la sortie et passer au niveau suivant ;
- progression mécanique : armes, niveaux d’armes, HP bonus ;
- progression de maîtrise : connaître les niveaux, les pièges, les ennemis et les passages secrets.

Il y a une dimension die & retry marquée, inspirée par le Rogue-lite. La mort ne repose alors pas  sur une nouvelle génération du niveau mais sur l’apprentissage de celui-ci.

*Scope & durée de vie :*

L'objectif est d'avoir une durée de jeu d'environ 1 à 2 heure maximum. Il n'y aura pas ou peu de rejouabilité.
La durée de vie annoncée ici est encore une estimation approximative car celle-ci va dépendre de prises de décisions sur les concepts clé du jeu qui ne sont pas encore clairement établis à ce stade :
- taille réelle des niveaux
- équilibrage difficulté et scaling de la progression
- établir, selon la difficulté, le temps que peut prendre en moyenne la completion d'un niveau (combien de retry le joueur va-t-il faire en moyenne)

La vision global est celle d'un mini-jeu. Il n'y a pas vocation de créer un jeu avec 10 ou 20 heures de jouabilité.

Le scope établi ici est de produire un prototype jouable et testable = jeu en version alpha.
La première version visée est 0.1.0. L'intégration complète de toute les features définies dans ce document devra s'opérer sur de nombres itérations, tests et playtests qui mèneront à plusieurs versions, exemple :
- 0.1.0 => 0.1.1 => 0.1.2 => 0.2.0 => etc.

Cela devra être défini clairement au moment de la production.

##### Influences Principales

- **Dark Souls, Souls-like**
- **Halls Of Torment**
- **Megabonk**
