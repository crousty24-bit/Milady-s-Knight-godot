# Milady's Knight — Learning

## Objectif

Ce document sert de support d'apprentissage humain pendant le développement de **Milady's Knight**.

Le projet est un premier projet Godot : l'objectif n'est donc pas seulement qu'Astra implémente les fonctionnalités, mais aussi de comprendre progressivement **comment le jeu est construit**.

`learning.md` doit être mis à jour après chaque run.

Il ne remplace pas :

- `runs-journal.md`, qui consigne ce qui a été fait et testé ;
- `docs/`, qui décrit les règles et spécifications du projet.

Ici, on explique **comment l'implémentation fonctionne**, avec des mots simples et des exemples directement tirés du projet.

---

## Principes

Pour chaque run, Astra doit expliquer uniquement les éléments réellement rencontrés ou modifiés.

L'explication doit rester :

- simple ;
- concise ;
- concrète ;
- liée au projet ;
- adaptée à un débutant en game-dev et Godot.

Éviter :

- les longs cours théoriques sans lien avec la run ;
- la copie complète des scripts ;
- le jargon non expliqué ;
- les détails internes inutiles.

Lorsqu'un terme Godot apparaît pour la première fois, l'expliquer brièvement.

Exemples :

- **Node** : élément de base d'une scène Godot ;
- **Scene** : ensemble de nodes réutilisable ;
- **Signal** : mécanisme permettant à un élément d'annoncer qu'un événement vient de se produire ;
- **CollisionShape2D** : forme utilisée par le moteur pour calculer une collision.

---

## Ce qui doit être documenté

Selon le contenu de la run, expliquer les changements dans les catégories pertinentes.

### Code et scripts

- script créé ou modifié ;
- responsabilité du script ;
- logique importante ajoutée ;
- fonctions ou variables essentielles ;
- relation avec les autres scripts.

### Scènes et interface Godot

- scène créée ou modifiée ;
- nodes ajoutés ou réorganisés ;
- propriétés importantes configurées dans l'Inspector ;
- signaux connectés ;
- groupes utilisés ;
- collisions, layers ou masks concernés.

### Level design

- TileMap / TileSet ;
- plateformes ;
- blocs ;
- zones ;
- placement d'entités ;
- collisions du terrain ;
- organisation du niveau.

### Assets

- import d'un sprite, tileset, animation, son ou autre asset ;
- réglages d'import importants ;
- découpage d'une spritesheet ;
- création d'animations ;
- intégration dans une scène.

### Project Settings

Documenter tout réglage important modifié, par exemple :

- Input Map ;
- résolution ;
- rendering ;
- physics ;
- autoloads ;
- layers de collision.

### Concepts game-dev

Expliquer brièvement le concept général rencontré dans la run :

- hitbox / hurtbox ;
- machine à états ;
- aggro ;
- cooldown ;
- delta time ;
- spawn ;
- instance de scène ;
- persistance ;
- etc.

---

## Format d'une entrée

```markdown
## RUN-XXX — Nom de la run

### Ce qui a été réalisé
Résumé très court des changements visibles.

### Comment Astra l'a implémenté

#### Scripts
- fichier concerné ;
- rôle ;
- logique ajoutée ;
- interaction avec le reste du projet.

#### Godot
- scène ou nodes concernés ;
- réglages effectués dans l'Inspector ;
- signaux, collisions, assets ou settings concernés.

Ne conserver que les sous-sections utiles à la run.

### Comment cela fonctionne
Explication simple du fonctionnement obtenu, étape par étape.

### Exemple concret dans Milady's Knight
Décrire un cas réel permettant de relier la théorie au jeu.

### Concepts à retenir
- **Concept** : explication en une ou deux phrases.
- **Concept** : explication en une ou deux phrases.

### À regarder dans le projet
Indiquer les fichiers, scènes ou réglages que l'humain peut ouvrir dans Godot pour observer l'implémentation.
```

---

## Exemple

### RUN-006 — Intégration du Melee Warrior

### Ce qui a été réalisé

Ajout d'un ennemi de mêlée capable de patrouiller, détecter le joueur et se déplacer vers lui lorsqu'il entre dans sa zone d'aggro.

### Comment Astra l'a implémenté

#### Scripts

Le script du Melee Warrior gère plusieurs comportements :

- déplacement de patrouille ;
- détection du joueur ;
- poursuite ;
- déclenchement de l'attaque à portée.

La logique sépare donc le comportement normal de l'ennemi de son comportement lorsqu'il a détecté le joueur.

#### Godot

La scène de l'ennemi contient les éléments nécessaires à son fonctionnement, par exemple :

- son sprite ou animation ;
- sa collision physique ;
- une zone de détection ;
- une zone ou portée d'attaque.

Les formes de collision peuvent être différentes du sprite visible : elles représentent les zones utiles au gameplay, pas simplement le contour exact de l'image.

### Comment cela fonctionne

1. L'ennemi patrouille entre ses limites prévues.
2. Une zone de détection suit l'ennemi.
3. Lorsque le joueur entre dans cette zone, l'ennemi passe en comportement d'aggro.
4. Il se dirige vers le joueur.
5. Lorsqu'il atteint sa portée d'attaque, il peut lancer son attaque.
6. Si le joueur sort de la zone prévue, l'ennemi revient à son comportement normal.

### Exemple concret dans Milady's Knight

Un Skeleton Warrior peut utiliser ce comportement.

Son apparence graphique peut changer selon le biome, mais son rôle reste celui d'un **Melee Warrior** : ennemi terrestre qui patrouille puis poursuit le joueur pour l'attaquer au corps à corps.

### Concepts à retenir

- **Aggro** : état dans lequel un ennemi a détecté le joueur et commence à réagir à sa présence.
- **Zone de détection** : zone invisible utilisée pour savoir si le joueur est suffisamment proche.
- **Scene réutilisable** : une scène d'ennemi peut être instanciée plusieurs fois dans différents niveaux.
- **Collision gameplay** : la forme utilisée pour les collisions est choisie pour obtenir un comportement cohérent, pas uniquement pour suivre chaque pixel du sprite.

### À regarder dans le projet

Après cette run, ouvrir :

- la scène du Melee Warrior ;
- son script principal ;
- ses `CollisionShape2D` / `Area2D` ;
- les propriétés de détection et de déplacement dans l'Inspector ;
- un niveau où l'ennemi est instancié.

---

# Journal d'apprentissage

<!--
Ajouter une entrée après chaque run.

Même si une run est principalement corrective, documenter ce qu'elle permet d'apprendre : cause du bug, fonctionnement concerné et méthode de correction.

Si une run n'apporte réellement aucun nouvel apprentissage technique, l'indiquer brièvement plutôt que d'inventer du contenu.
-->
