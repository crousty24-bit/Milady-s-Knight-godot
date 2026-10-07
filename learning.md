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

## RUN-001 — Fiabiliser le moteur, l’import et les tests

### Ce qui a été réalisé

Les commandes du projet utilisent maintenant **Godot 4.7.2 stable**. L’import des trois sons problématiques ne produit plus d’erreur, et les tests disposent de leur propre dossier de sauvegarde. Cette run ne change aucune règle de gameplay.

### Comment cela fonctionne

**Une version commune.** `tools/godot-version.txt` contient la version attendue. Les lanceurs lisent ce fichier et interrogent le moteur avant de démarrer. Le vieux binaire 4.5.1 peut rester sur le disque, mais il est refusé pour éviter de tester avec une version différente de celle utilisée en production. La déclaration `4.7` dans `project.godot` est conservée.

**Un son et son conteneur.** Un WAV contient des échantillons audio et des informations qui permettent de les lire. Les sons coin, jump et tap avaient un bloc de taille impaire sans son octet de remplissage final. Godot 4.7.2 signalait alors un accès au-delà du fichier. Ajouter cet octet et ajuster la taille du conteneur résout l’erreur sans changer le son. Les originaux restent dans `assets/source/sounds/` ; `.gdignore` empêche Godot de les importer une seconde fois. Les scènes gardent leurs références aux variantes compatibles dans `assets/sounds/`.

**Source et cache d’import.** Le dossier `.godot/` contient notamment les fichiers transformés par Godot à partir des sources. Un import depuis zéro sur une copie sans ce cache permet de vérifier que le projet reste reproductible. Il ne faut pas confondre un cache déjà rempli et une source correctement importable.

**Une sauvegarde réservée aux tests.** `user://` désigne le dossier de données utilisateur choisi par Godot, pas un sous-dossier automatique du projet. Le runner lui fournit un profil temporaire, puis `tests/user_data_path.gd` vérifie le chemin réellement obtenu. Sous Windows, ce profil reste sur NTFS pour tester les écritures de sauvegarde sur le même type de disque. La vraie partie n’est ni chargée ni écrasée par ces essais.

**Un test terminé doit le prouver.** Pendant la reproduction, Godot affichait des erreurs tout en retournant le code 0. Le runner vérifie donc le code, les messages d’erreur et une ligne finale `RESULT …; 0 failures`. Une suite interrompue ou silencieuse ne peut plus passer pour un succès. Les 150 contrôles existants sont conservés ; un contrôle supplémentaire vérifie l’isolation.

### Exemple concret dans Milady’s Knight

`tests/bonus.gd` écrit puis recharge une sauvegarde de test. Avec le nouveau runner, ce fichier se trouve dans le profil temporaire, tandis que le `progress.json` de la vraie partie reste inchangé. Si un test échoue, le runner conserve ce profil pour l’inspecter ; s’il réussit, il le supprime et garde les logs.

### À regarder dans le projet

- `tools/run.sh`, `Lancer-Windows.cmd` et `tools/godot-version.txt` : choix et vérification du moteur.
- `tools/test.sh` et `tests/user_data_path.gd` : profil isolé et preuves de fin de test.
- `assets/source/sounds/`, `assets/sounds/` et `tests/wav_import.py` : originaux conservés et contrôle indépendant du PCM.
- `work/test-results/` : résultats locaux ; les preuves résumées et les contrôles humains encore attendus sont dans `runs-journal.md`.

## RUN-002 — Inventorier les médias et préparer les besoins d'assets

### Ce qui a été réalisé

Les 12 fichiers image, audio et police du prototype sont inventoriés dans `docs/11_GAME_ASSETS_LIBRARY.md` et `docs/12_SFX_LIBRARY.md`. Les besoins visuels, animations, VFX et sons de la démo sont répartis par version dans ces documents et `docs/13_ASSET_REQUIREMENTS.md`. Aucun asset ni réglage d'import Godot n'a été modifié.

### Comment cela fonctionne

Une **ressource référencée** est un fichier que la scène ou un script charge effectivement : `knight.png` est utilisé dans `scenes/player.tscn`. Un fichier simplement présent n'est pas nécessairement utilisé : aucune référence au chemin de `platforms.png` n'a été trouvée dans les scènes, scripts et réglages inspectés. Cette distinction évite de compter un fichier inutilisé comme une fonctionnalité du jeu.

Une **source** est le fichier obtenu auprès de son auteur ; un **dérivé** est la version préparée pour le jeu, par exemple une image découpée ou un son réencodé. Conserver la source permet de comprendre et de refaire cette adaptation. Comparer les empreintes SHA-256 peut confirmer qu'une copie est identique, mais une adaptation change son empreinte : l'absence de correspondance ne prouve pas que le fichier provient d'un autre pack.

La licence appartient à la source identifiée, pas à un nom de fichier ressemblant. Les conditions des deux packs Zerie candidats ont été vérifiées sur leurs pages officielles, sans correspondance établie avec les médias actuels. À la demande de l'humain, ce rattachement est différé jusqu'à la sélection et à la recette des assets distribués.

### Exemple concret dans Milady's Knight

`world_tileset.png` apparaît dans la scène du vertical slice et dans `assets/kingdom_tileset.tres`. Cette dernière ressource n'est pas référencée par la scène de jeu inspectée : modifier seulement son TileSet externe ne prouverait donc pas que le terrain joué a changé.

### À regarder dans le projet

- `docs/11_GAME_ASSETS_LIBRARY.md` et `docs/12_SFX_LIBRARY.md` : fichiers présents, usages vérifiés et état des sources.
- `docs/13_ASSET_REQUIREMENTS.md` : familles d'assets à produire ou choisir selon les versions.
- `scenes/player.tscn` et `scenes/vertical_slice.tscn` : exemples de références effectivement chargées par Godot.

## RUN-003 — Choisir la grille visuelle

### Ce qui a été réalisé

Une scène d'essai Godot compare une grille 16×16 et une grille 32×32 dans deux captures de 640×360. Le choix validé est **16×16 pour le terrain**. Le jeu garde encore son viewport 320×180 ; son changement relève de RUN-004.

### Comment cela fonctionne

Une **cellule de terrain** sert à placer les blocs du niveau. La **frame** d'un sprite est le rectangle réservé à une image d'animation ; elle peut contenir de la transparence. Le chevalier actuel occupe une frame de 32×32, mais seulement 13×19 pixels sont opaques sur la frame de repos mesurée. La frame ne donne donc pas directement la taille perçue du personnage.

Une **collision** est une forme définie séparément du dessin. Le joueur utilise une capsule de 10 px de large et 18 px de haut, le Slime un rectangle de 14×12. Agrandir un sprite ne règle pas automatiquement ses collisions ni sa lisibilité. L'essai 32 double les images existantes et leurs contours indicatifs ; il ne représente pas un nouvel art détaillé.

### Exemple concret dans Milady's Knight

Le terrain du slice utilise des cellules 16×16. Le chevalier a une frame 32×32 et peut donc occuper plusieurs cellules sans changer cette grille. Quand son véritable sprite sera intégré, on examinera sa silhouette opaque à l'écran, puis sa capsule de collision sur les animations utiles avant de fixer ses dimensions.

### À regarder dans le projet

- `scenes/scale_comparison.tscn` et `scripts/scale_comparison.gd` : les deux variantes de la maquette.
- `docs/RUN-003_SCALE_COMPARISON.md` : captures, mesures et limites de la décision.

## RUN-004 — Agrandir le viewport sans agrandir le niveau

### Ce qui a été réalisé

Le jeu dessine désormais dans un viewport **640×360**. Les cellules du terrain, les positions du niveau, les personnages et les collisions gardent leurs dimensions. Le HUD utilise toute la largeur et sa barre d'indication reste au bas de l'écran. La caméra suit le joueur dans le slice avec ses limites propres au niveau.

### Comment cela fonctionne

Le **viewport** est la surface interne que Godot dessine. La fenêtre peut ensuite afficher cette surface à une taille entière : 640×360 à ×1, 1280×720 à ×2 et 1920×1080 à ×3. Avec une fenêtre hors ratio, Godot centre une image entière et laisse des bandes autour. Le réglage `nearest` conserve les pixels nets. Changer le viewport montre davantage de monde autour du joueur ; cela ne multiplie pas les coordonnées des plateformes ou des pièges.

Les **ancrages** des éléments `Control` du HUD décrivent leur position par rapport aux bords du viewport. La barre du bas reste ainsi en bas quand la résolution change, et l'overlay couvre l'espace central. Les textes gardent une marge et une taille lisibles dans les captures de pause, mort et victoire.

La **Camera2D** appartient au joueur, mais le niveau définit ses limites et son décalage : ces valeurs décrivent la géométrie du slice, pas une propriété universelle du personnage. Le joueur avance pendant les ticks physiques. Calculer le suivi de la caméra sur ces mêmes ticks évite l'alternance mesurée quand la caméra était mise à jour pendant le rendu. Le smoothing reste actif pour adoucir le suivi ; les limites empêchent de montrer une zone hors du niveau.

### Exemple concret dans Milady’s Knight

Au sommet du mur, l'ancienne correction locale de caméra remontait le cadre de 16 px. Avec 640×360, le sommet est déjà visible ; cette correction n'aide plus et a été retirée. Le parcours du mur et du bac reste le même, ce que les tests physiques ont vérifié.

### À regarder dans le projet

- `project.godot` : résolution interne et agrandissement entier.
- `scenes/hud.tscn` : ancrages des bandeaux, textes et overlay.
- `scenes/player.tscn` et `scripts/level.gd` : caméra générique et cadrage du slice.
- `docs/media/run-004-*.png` : captures du HUD et des overlays à 640×360.

## RUN-005 — Les touches deviennent des actions de jeu

### Ce qui a été réalisé

Le personnage se déplace avec les flèches gauche et droite ; haut et bas sont réservées aux interactions futures. Space saute, E interagit ou confirme l'écran de mort/victoire, F attaque en continu tant qu'il est maintenu et Escape met en pause ou reprend. G, R et A ont leur propre action, sans attaque d'atterrissage, pouvoir spécial ni équipement encore implémentés. R ne redémarre plus le niveau.

### Comment cela fonctionne

L'**Input Map** associe une touche physique à un nom d'action tel que `move_left` ou `special_attack`. Le code du personnage lit le nom de l'action, ce qui évite de disperser les codes des touches dans ses règles de mouvement. `is_action_pressed("attack")` reste vrai pendant le maintien de F : une nouvelle frappe commence quand le temps de récupération de la précédente est terminé. `is_action_just_pressed("interact")` ne vaut vrai qu'au début d'une nouvelle pression de E, ce qui évite qu'une touche maintenue confirme plusieurs fois.

Après retour de jeu, le changement de vitesse gauche/droite est plus rapide : une inversion complète prend six ticks physiques à 60 Hz dans la fixture. Le cycle de frappe du prototype dure désormais 0,28 s ; les phases de préparation, de contact et de récupération gardent leurs proportions. Le personnage peut changer de côté pendant la préparation ou la récupération, tandis que `attack_facing` mémorise le côté frappé : une seule frappe ne touche pas des ennemis situés de part et d'autre du joueur. Cette cadence provisoire sera ajustée avec l'ATK SPEED propre aux armes.

### Exemple concret dans Milady's Knight

Près de la poterne, E peut offrir les douze pièces pendant le jeu. Si la pause est ouverte, l'appui sur E n'ouvre rien. Reprendre avec Escape alors que E est toujours enfoncé ne réutilise pas cet appui ; il faut relâcher puis presser E à nouveau. Après une mort ou une victoire finale, E confirme le redémarrage affiché à l'écran. Le menu de pause avec choix « Recommencer » n'est pas encore présent.

### À regarder dans le projet

- `project.godot` : association des touches aux actions.
- `scripts/player.gd` et `scripts/level.gd` : lecture des actions pendant le jeu et sur les overlays.
- `tests/keyboard.gd` : événements clavier réels et cas de pause/confirmation.

## RUN-006 — Compter les points de vie fractionnaires

### Ce qui a été réalisé

Le joueur et les Slimes peuvent perdre des fractions de point de vie. Une perte de 0,5 HP pour le joueur et des coups de 0,2 DMG sur un ennemi s'accumulent exactement. Le HUD montre le nombre exact de HP et des cœurs entiers ou à moitié remplis. Les réactions du joueur dépendent maintenant de la source du dégât.

### Comment cela fonctionne

Le jeu stocke chaque point de vie sous forme de **dix unités entières**. Ainsi, 3 HP valent 30 unités, 0,5 HP vaut 5 unités et 0,2 DMG en retire 2. Le calcul évite qu'une conversion en HP entiers efface une fraction. Les scripts exposent pourtant les valeurs familières en HP aux autres systèmes et aux signaux `health_changed`. Un soin ne dépasse jamais le maximum, et une mort ne peut être émise qu'une fois.

Le HUD affiche la valeur numérique sans arrondir. Pour le dessin, il arrondit au demi-cœur supérieur : avec 0,2 HP, « VIE 0.2 » accompagne un demi-cœur visible. Cette convention évite de montrer zéro cœur tant que le joueur vit encore ; la valeur écrite reste la référence précise.

Chaque source de dégât indique son profil au joueur. Le contact d'un Slime interrompt l'attaque, bloque brièvement F, repousse le personnage et bloque le saut pendant le recul. Un projectile interrompt l'attaque sans recul ; un piège ou une flamme repousse sans interrompre l'attaque ; un swarm accorde seulement l'invulnérabilité. Le vide tue même pendant l'invulnérabilité. La flamme suit le profil du piège selon la décision prise pour cette run. Le correctif et le ressenti ont été validés par l'humain ; les durées de 0,18 s de hit-stun et 0,16 s de recul, notamment au contact d'un Slime et des ronces, restent provisoires et seront équilibrées ultérieurement.

### Exemple concret dans Milady's Knight

Si le joueur touche les ronces, il perd 1 HP, recule et ne peut pas sauter pendant les 0,16 premières secondes du recul. Si un Slime le touche, il subit aussi 0,18 seconde de hit-stun : maintenir F ne relance une frappe qu'après ce délai. Après la fenêtre d'invulnérabilité de 0,85 seconde, un nouveau contact peut infliger un autre dégât.

### À regarder dans le projet

- `scripts/health_units.gd` : conversion exacte entre HP et unités.
- `scripts/player.gd` et `scripts/slime.gd` : santé, signaux et profils de dégâts.
- `scripts/health_hearts.gd` et `scripts/hud.gd` : valeur écrite et cœurs dessinés.
- `tests/damage_profiles.gd` : scénarios de fractions et de réactions.


## RUN-007 — Séparer la frappe et sa cadence

### Ce qui a été réalisé

Sword niveau 0 inflige **0,5 HP** par coup. Deux frappes tuent un Green Slime (1 HP), quatre tuent un Purple (2 HP). La touche F maintenue répète le geste toutes les secondes. La lame mesure **24 px depuis la main**, soit un bloc et demi de terrain : son dessin et sa collision utilisent cette même longueur. Green inflige 0,5 HP au contact, Purple 1 HP.

### Comment cela fonctionne

Le **geste** dure 0,28 s : préparation, courte fenêtre de contact, puis récupération. Un autre compteur, le **cooldown**, mesure la seconde nécessaire entre deux départs. L’animation peut donc être terminée alors que le prochain coup est encore indisponible. Relâcher puis presser F ne réinitialise pas ce compteur ; une interruption annule le geste mais conserve le délai. Après un contact, il faut que le hit-stun du joueur et le cooldown soient tous deux terminés pour pouvoir frapper. La pause suspend les deux compteurs.

Pendant la fenêtre active, Godot interroge une forme rectangulaire de 24×4 px, centrée à 12 px de la main et tournée avec la lame. Une liste mémorise les ennemis déjà touchés par ce coup : rester dans la forme plusieurs ticks ne multiplie pas les dégâts. Un rayon contre le terrain empêche de frapper à travers un mur. Le coup reste possible en l’air ; entrer en wall slide annule sa fenêtre active.

Le **recul** d’un Slime préserve brièvement sa vitesse d’impulsion au lieu de l’écraser par sa vitesse de patrouille. Le Slime continue de bouger et son contact reste actif. Son flash jaune ne signifie pas qu’il est inoffensif ou invincible : deux impacts indépendants sont acceptés immédiatement. La mort protège son signal de récompense contre une seconde émission.

### Exemple concret dans Milady’s Knight

Après un premier coup contre un Green, le joueur doit garder ses distances pendant le délai avant de donner le second. Le pilote des parcours utilise maintenant les touches de déplacement pour maintenir cet espacement ; les suites de parcours ne modifient ni la santé, ni la position, ni les compteurs pour contourner les combats.

### À regarder dans le projet

- `scripts/player.gd` : durée du geste, cooldown, portée et déduplication des impacts.
- `scripts/slime.gd` : profils Green/Purple et recul sans immunité.
- `tests/combat.gd` : cadence, portée, interruptions, collisions et patrouille exercées dans Godot.
- `tests/route_driver.gd` : maintien de la distance avec des entrées réelles.

Les contrôles automatiques et les captures vérifient le fonctionnement ; l’humain valide la run et les changements finaux le 28 septembre 2026, après révision de la portée et de la protection.


### RUN-007 — Rendre la protection après impact visible

L’audit a mesuré les anciennes 0,85 s d’invulnérabilité : elles existaient bien, même au contact de deux Slimes. Le combat était devenu plus exigeant parce qu’un Slime blessé reste dangereux et que Sword attend 1 s entre ses coups. Après validation humaine, la protection passe à **1,20 s**. Les **0,16 s de recul** et **0,18 s de hit-stun** restent distinctes : être protégé ne bloque pas le joueur pendant toute cette seconde.

Un petit **shader** remplace la couleur des pixels du personnage par du blanc pendant **0,10 s**, en conservant leur transparence originale. Ensuite, le sprite alterne entre une opacité de 0,25 et de 1 pendant le reste de la protection. Chaque joueur possède son propre matériau : toucher une instance ne fait pas clignoter une autre. Les compteurs évoluent sur les ticks physiques, donc la pause les suspend. La mort retire le flash et rend le sprite opaque.

Le recul des ronces utilisait auparavant le regard du personnage : regarder à l’opposé du piège pouvait provoquer une poussée vers lui. Il compare maintenant les positions horizontales du joueur et des ronces pour choisir le côté qui éloigne du danger. Si les centres sont exactement alignés, il choisit le côté opposé au regard. Le dégât de 1 HP et l’impulsion verticale sont conservés.

L’humain a validé la run et ces changements après ses retours en jeu. Les durées restent des paramètres d’équilibrage qui pourront évoluer lors de playtests ultérieurs.

Ces comportements ont été vérifiés dans Godot par 35 nouveaux contrôles, intégrés à une suite complète de 296 contrôles de jeu. Cinq captures vérifient le flash, les deux phases du clignotement et le retour normal. Les parcours restent traversables sans modifier le niveau.


## RUN-008 — Bloquer avec un corps, blesser avec une zone

Les piques fixes utilisent deux éléments complémentaires. Le `StaticBody2D` empêche le joueur de traverser leur volume. L’`Area2D`, un peu plus grande, détecte le joueur même lorsque la collision solide l’arrête juste devant. Un seul corps solide ne suffirait pas à appliquer automatiquement les dégâts ; une zone seule serait traversable, comme les ronces conservées.

Le corps appartient à la couche terrain, mais pas à celle des murs grimpables : il bloque sans accorder de saut mural. Le capteur ne cherche que la couche joueur. La rotation du nœud tourne ensemble dessin, formes et impulsion ; la même scène fonctionne au sol, au plafond et sur les deux côtés d’un mur. Un contact retire exactement cinq unités de santé, soit 0,5 HP. Le profil de piège conserve Sword et n’ajoute pas de hit-stun, mais repousse le personnage et déclenche sa protection de 1,20 s.

Le vide dépend maintenant du niveau. Dans l’inspecteur du niveau, `void_y` définit la hauteur au-delà de laquelle les pieds du joueur provoquent sa mort. Le slice utilise 304 px : la hauteur de son ancienne fosse létale. Un autre niveau peut choisir une hauteur plus basse sans devoir modifier le script du personnage. La pause suspend ce contrôle et `die()` garantit une seule émission du signal de mort. La reprise automatique est expliquée dans RUN-009 ci-dessous.

Godot a exécuté 39 nouveaux contrôles de collisions/contact dans les quatre orientations, maintien de l’attaque, protection, sondes murales et chute réelle avec limite modifiée. La suite complète compte 335 contrôles réussis ; deux captures des placements au sol et au mur ont été inspectées. Les tests d’orientation utilisent des déplacements `move_and_collide` contrôlés et figent les compteurs du joueur pour isoler le contact ; ils ne représentent pas une partie humaine. Une chute réelle sur les piques du niveau et les parcours aller/retour complètent ces fixtures. L’humain confirme RUN-008 vérifiée et validée le 28 septembre 2026. La revue de clôture confirme les critères et preuves ; RUN-008 est DONE localement.

## RUN-009 — Reprendre sans confirmation après la mort

Quand le joueur meurt, le niveau suspend le gameplay et affiche « Thou hast perished. » sur l'écran assombri. Son propre compteur continue pendant la pause, car le nœud du niveau est configuré pour fonctionner même lorsque l'arbre Godot est en pause. Après trois secondes, un rectangle noir transparent devient opaque en 0,4 seconde ; la scène se recharge alors et la pause est retirée. Aucun appui n'est nécessaire.

Le joueur émet le signal de mort une seule fois et le niveau garde aussi un verrou pendant le rechargement. Les bonus obtenus durant la tentative sont effacés ; la réserve déjà validée dans `Progression` n'est pas modifiée. Recharger la scène restaure le spawn, la vie, les pièces, la porte et les ennemis. Le test attend ensuite quatre secondes au spawn : aucun danger n'y tue le joueur dans le niveau actuel.

Godot 4.7.2 a passé l'import, l'isolation des sauvegardes et 15 suites totalisant 353 contrôles de jeu. Les cas ciblés couvrent le délai, le fondu, plusieurs morts, la pause, l'attaque, la perte des gains et le rechargement unique. Deux captures du message et du fondu ont été inspectées. Ces preuves portent sur le niveau actuel ; elles ne garantissent pas les futurs points de spawn.

L'humain a validé RUN-009 et sa PR #14 a été fusionnée dans `develop` le 30 septembre 2026.

## RUN-010 — Faire passer les sons par des bus

Godot mélange chaque son dans un **bus audio** avant de l'envoyer à la sortie. Le fichier `default_bus_layout.tres`, chargé automatiquement, déclare cinq bus : Master, puis Music, Ambient, SFX et UI qui se déversent tous dans Master. Chaque `AudioStreamPlayer` indique son bus dans sa propriété `bus`. Un futur réglage « volume de la musique » n'aura qu'à modifier le bus Music avec `AudioServer.set_bus_volume_db`, sans toucher aux scènes. Master porte un limiteur de sécurité à −1 dB. Le mix a toutefois été mesuré sans lui : il ne sert pas à cacher un volume trop élevé.

Les sons du joueur utilisent un `AudioStreamPlayer` classique : la caméra suit le personnage, une position ne donnerait aucune information utile. Les Slimes et les pièces utilisent `AudioStreamPlayer2D` : Godot baisse leur volume avec la distance à la caméra et les place à gauche ou à droite. Un son très fréquent passe par un `AudioStreamRandomizer`, qui choisit l'une des trois variantes et modifie légèrement pitch et volume pour éviter la répétition mécanique.

Un nœud en pause arrête aussi ses sons. Or la mort met l'arbre en pause : le son de mort utilise donc `PROCESS_MODE_ALWAYS`. De même, un son enfant d'un Slime disparaîtrait avec lui ; au coup fatal, l'impact et l'éclaboussure sont déplacés vers la scène avec `reparent()`, puis se libèrent à leur fin.

Les fichiers de la bibliothèque ne sont jamais modifiés. `tools/prepare_audio.py` en crée des copies courtes en WAV mono 16 bits pour les effets, et en Ogg Vorbis bouclé pour la musique, dont le volume perçu est ramené à −16 LUFS. Les SFX viennent d'un pack CC BY 4.0 : le crédit de Helton Yan devra apparaître dans le jeu. `assets/AUDIO_CREDITS.md` conserve la source de chaque fichier.

Godot 4.7.2 a passé 16 suites et 377 contrôles, dont 24 dédiés à l'audio. Une capture Movie Maker empile sept sons sur la musique : le pic reste à −5,5 dBFS, sous la saturation. À l'écoute, l'humain a validé cette première itération. Il demande toutefois une musique plus forte et différente, des SFX moins forts, ainsi que d'autres sons pour l'impact d'épée, le saut et le double saut. Une mesure sans saturation ne garantit donc pas un mix agréable.

## RUN-011 — Recetter le socle avant le premier niveau

La recette distingue trois types de preuve. Une suite ciblée isole une règle : par exemple `render_timing.gd` déclenche un saut mural à un endroit préparé et vérifie vitesse et état du joueur. Le pilote de parcours part du niveau et commande réellement le joueur pour franchir les deux branches, revenir et sortir ; il détecte des problèmes d'enchaînement que la fixture isolée ne voit pas. Enfin, un essai humain juge si l'escalade paraît jouable, ce qu'un compteur de vitesse ne peut pas décider.

Le moteur dessine des **images** à la cadence de l'écran, tandis que la physique avance ici à **60 ticks par seconde**. RUN-011 a plafonné le rendu à 30, 60 et 144 images par seconde sans changer ce pas physique. Les neuf contrôles de saut, attaque, glissade, bac et verrou de double saut ont réussi aux trois cadences mesurées. Des captures 640×360 montrent le mur, le sommet, les autres zones et l'écran de mort ; elles vérifient le cadrage et la lisibilité, pas la sensation de jeu.

L'import et les 16 suites ont passé 377 contrôles de jeu. Les tests de parcours, de pause et de mort ont aussi exercé les régressions les plus pertinentes pour ce socle. Aucun défaut n'a été reproduit, donc aucun code gameplay n'a été changé pour cette run. L'humain a joué le saut mural et l'a validé. Cette validation concerne le slice actuel : The Eidolon Vale, son menu, le Longbow et sa sauvegarde restent à réaliser dans les runs de 0.2.0.

## Réorganisation du 2 octobre 2026 — Runs, lots et versions

Une **run** devient un lot de travail cohérent : par exemple la reprise réunit son contrat, la sauvegarde et les menus qui l’utilisent. Elle peut contenir plusieurs sessions, tâches déléguées et commits. Regrouper ces étapes évite de rouvrir un chantier pour chaque petite tâche ; chaque comportement conserve ses propres vérifications avant la recette intégrée.

Une **version** décrit un résultat utilisable, pas le nombre de runs effectuées. Les onze premières runs forment le socle validé **0.1.0**. La roadmap réserve trois éventuelles passes visuelles supplémentaires sur la branche actuelle, puis regroupe le reste en quatorze lots jusqu’à **0.5.0 beta**. Le nombre total d’identifiants est donc 28, sans réduire les dix niveaux ni leurs systèmes. Cette modification du planning n’implémente aucun de ces futurs systèmes.

La version actuelle est aussi inscrite dans `project.godot` sous `config/version`. Cette métadonnée ne crée ni tag Git, ni export, ni écran de version. De même, une run DONE peut être validée localement alors que sa branche n’est pas fusionnée : ici, la validation de la réorganisation et des compléments retenus, puis la fusion autorisée, doivent précéder le travail vers 0.2.0.

Chaque lot indique son orchestrateur à l’avance. Le défaut Codex et son profil de travail de code utilisent désormais `gpt-6.1-sol` ; les autres profils et les décisions de délégation restent en place. Jev conseille toujours le routage et la clôture : il ne démarre pas les runs, ne remplace pas les tests et ne fusionne pas les branches.

## RUN-012 — Dessiner un personnage avec du code

Un sprite en pixel art est une grille de couleurs. `tools/art/knight.py` écrit cette grille sous forme de texte : chaque caractère est un pixel (`o` le contour, `1` à `5` l'acier du plus sombre au plus clair, `R` la cape…). Le chevalier est découpé en **calques** — cape, jambe arrière, jambe avant, torse, heaume, bras — superposés dans un ordre fixe. Une course de six images réutilise ainsi le même torse avec des poses de jambes différentes. La jambe arrière est la même grille que la jambe avant, assombrie automatiquement d'un ton : la profondeur coûte une ligne de code.

Toutes les images partagent un **point d'ancrage** : les pieds au bas de la ligne 30 et le corps centré sur la colonne 16. Sans cela, le personnage semblerait glisser d'une image à l'autre. Comme le torse est symétrique autour de cette colonne, retourner le sprite vers la gauche ne le décale pas. Le script écrit aussi le `SpriteFrames` de Godot : chaque image y est une `AtlasTexture` qui découpe une région de la planche.

L'épée n'est pas dans le sprite : sa position vient du gameplay, qui fait tourner la lame autour de la main pendant 0,28 s. Faire pivoter une petite image de pixel art la rend floue ou crénelée. Le script pré-dessine donc l'épée sous 32 angles et le jeu choisit la plus proche de l'angle réel. Le dessin suit ainsi exactement la zone de dégâts. La collision du joueur (10×18) n'a pas changé : un sprite plus grand ne doit pas modifier la façon dont le personnage passe sous un plafond de deux tuiles.

Enfin, un nœud en pause n'anime plus. La mort met tout le jeu en pause : l'animation de chute restait figée sur sa première image. Le sprite passe donc en `PROCESS_MODE_ALWAYS` à la mort, comme le son de mort de RUN-010.

## RUN-013 — Habiller un niveau sans le reconstruire

Le niveau garde une seule source de vérité pour sa forme : la `TileMapLayer` `Terrain`, qui porte les collisions. Le nœud `TerrainSkin` se contente de **redessiner** par-dessus chaque case occupée. Pour choisir l'image, il regarde les quatre voisines et forme un **masque d'exposition** : 1 si le dessus est libre, 2 pour la droite, 4 pour le dessous, 8 pour la gauche. Les seize combinaisons ont chacune leur tuile : une case avec le dessus libre reçoit une margelle claire et de la mousse, une case au bord droit une arête sombre. C'est le principe de l'**autotiling**, appliqué ici en dessin plutôt que dans le `TileSet`. Plus une case est profonde sous la surface, plus elle est assombrie : l'œil lit d'abord le sol praticable.

La **parallaxe** donne de la profondeur avec des images plates. `backdrop.gd` lit le centre de la caméra et décale chaque couche d'une fraction de son mouvement. La citadelle lointaine bouge à 8 % de la vitesse de la caméra, la forêt à 30 %, le niveau à 100 %. Le ciel ne bouge pas du tout. Les couches se répètent horizontalement pour couvrir toute la largeur.

Les accessoires (maisons, charrette, panneau…) restent dessinés aux coordonnées choisies par l'auteur du niveau ; seules leurs images changent. Une palette partagée (`tools/art/palette.py`) garde la cohérence entre plusieurs scripts et plusieurs agents. Les couleurs vives y sont réservées à une fonction : rouge pour le danger et la vie, or pour l'argent, violet pour la corruption.

## RUN-014 — Finir les retours visuels et rééquilibrer le son

Un **feedback** confirme une action au joueur. Ramasser une pièce faisait disparaître le sprite d'un coup : elle joue maintenant une courte animation `collect` avant de se cacher. Pour la mort d'un Slime, l'effet ne peut pas être enfant du Slime, puisque celui-ci est supprimé presque aussitôt. L'éclaboussure est donc créée dans la scène courante, à la position de la mort, puis elle se libère d'elle-même. C'est la même solution que pour ses sons en RUN-010.

Côté son, chaque effet est normalisé à une **crête** cible : sa valeur maximale. Passer de −3 à −8 dBFS baisse tous les effets de 5 dB d'un coup, sans changer leur équilibre entre eux. La musique est réglée en **LUFS**, une mesure du volume perçu sur la durée : −13 LUFS au lieu de −16 la rend audible sous les effets. Une musique bouclée doit se terminer au même niveau qu'elle commence. Le nouveau morceau finissait par un fondu ; il est coupé avant, à la fin d'une mesure, pour que la reprise tombe en rythme. Les mesures prouvent l'absence de saturation, pas le plaisir d'écoute : seule une écoute humaine valide ce choix.

## RUN-029 — Animer un personnage avec un squelette

Dessiner chaque image à la main oblige à tout redessiner pour une nouvelle pose. `tools/art/knight.py` décrit plutôt une **pose** : position de la hanche, inclinaison du torse, position des pieds et des mains, angle de l'épée, forme de la cape. Le script en déduit le reste. Pour une jambe, il connaît la hanche, le pied et la longueur de la cuisse et du tibia ; la **cinématique inverse à deux os** calcule où doit se trouver le genou (deux solutions possibles, on garde celle qui plie vers l'avant). Les membres sont ensuite peints comme des tubes éclairés par une même lumière, puis réduits à quelques tons de la palette : chaque image reste du vrai pixel art, cohérent d'une pose à l'autre.

Le **contour sélectif** évite l'effet « coloriage » : chaque pièce reçoit un contour sombre là où elle touche le vide, mais une ligne plus douce là où elle passe devant une autre pièce. La silhouette reste nette sans écraser les détails intérieurs.

L'attaque montre comment séparer présentation et règle. La règle de `docs/01` reste : un hit par seconde tant que F est maintenu, avec une seule fenêtre de dégâts. Le jeu compte simplement les coups successifs et choisit le mouvement 1, 2 ou 3 ; si plus de 1,25 s passent, il revient au premier. Entre deux hits, au lieu de revenir au repos, le sprite affiche une pose d'enchaînement qui prépare le mouvement suivant. Pendant la fenêtre de contact, la lame est dessinée à l'angle même de la zone de dégâts : ce que le joueur voit correspond à ce qui touche.

Pour attaquer en courant sans « patiner », le personnage est rendu en **deux calques** : un `AnimatedSprite2D` pour les jambes, la jupe du tabard et la cape, et un enfant `Upper` pour le torse, les bras et l'épée. `use_parent_material` partage le shader de flash blanc et la modulation du parent, donc le clignotement d'invulnérabilité s'applique aux deux. En passant de `run` à `base_run`, le script recopie l'image et la progression de l'animation (`set_frame_and_progress`) : la foulée continue sans à-coup.

Côté interface, une information n'apparaît que lorsqu'elle sert (`docs/05`). Le bandeau d'indications a disparu ; l'invite de la porte est dessinée par le HUD mais placée sur la porte : sa position dans le monde est convertie en position d'écran avec la transformation du canevas de la vue. Enfin, tous les PNG du dépôt sont reproduits à l'identique par leurs générateurs : on le vérifie en comparant leurs empreintes MD5 avant et après régénération.

### Clôture 0.1.0 — Vérifier le résultat assemblé

La dernière validation porte sur l’assemblage des passes, pas seulement sur chacune séparément. Les 377 contrôles de jeu passent encore après les changements d’animations, de décor et de HUD ; 49 contrôles avec rendu vérifient ensuite les états du chevalier, l’invite de porte et les effets qui doivent se libérer après lecture. Les tests et l’inspection des captures complètent la validation artistique donnée par l’humain.

La version 0.1.0 comprend les runs 001–014 et 029. Le numéro 029 évite de renuméroter les lots déjà planifiés : il ne signifie pas que 015–028 ont été réalisés. Le plan compte maintenant 29 identifiants, dont 15 réalisés et 14 à venir. L’ouverture de la PR clôt la préparation de la livraison ; sa fusion dans `develop` reste nécessaire avant de commencer RUN-015 vers la 0.2.0.

## RUN-015 — Partie technique : tentative, fichier durable et menus clavier

Une tentative contient ce que le joueur peut perdre : coins, shards gagnés dans le niveau, position et état des ennemis. `level.gd` garde ces valeurs en mémoire. Les coins excédentaires restent des coins ; tuer un ennemi crédite séparément les shards. Une mort, Restart ou fermeture abandonne la tentative ; seule la sortie ajoute ses shards restants à la banque.

`Progression` garde ce qui doit survivre : banque, niveau de reprise, équipement et flags permanents/dialogues. Le JSON v2 est écrit dans un fichier temporaire puis renommé ; la mémoire n'est modifiée qu'après succès. Une dépense utilise les gains courants puis la banque. L'acquisition d'un équipement et son paiement passent par la même écriture : il est impossible de confirmer l'objet en oubliant son débit. Les tests lisent ces valeurs depuis une nouvelle instance après écriture. Cela prépare les données de RUN-016 ; aucun Longbow ni objet de récompense n'est encore implémenté.

Une v1 contient un bonus dont on ne connaît plus la part issue des coins. Le menu demande donc explicitement sa conversion en shards et conserve les octets originaux dans une copie. Une sauvegarde corrompue ou future ne devient pas une partie vide silencieusement : Continue est désactivé, les opérations ordinaires protègent le fichier. New Game demande confirmation et conserve la partie remplacée, y compris lorsqu'une copie plus ancienne existe déjà.

`game.gd` affiche désormais le menu au démarrage. `keyboard_menu.gd` affiche et sélectionne les choix avec haut/bas, E et Escape. Le niveau utilise le même panneau pour pause et contexte. Une variable `modal` désigne la fenêtre propriétaire des entrées ; une seconde demande est refusée. La frame d'ouverture est ignorée par le panneau pour qu'Escape ne puisse pas ouvrir puis fermer pause immédiatement. Après Resume, le contrôle attend le relâchement de E/F/Space/Escape ; la confirmation ne devient donc pas une action de gameplay. La mort annule cette attente afin que son reset automatique reste possible même si E est tenu.

Les tests ont reproduit le défaut d'ouverture/fermeture dans une frame, puis vérifié sa correction, et exercent des fichiers isolés plutôt que la sauvegarde du joueur. La présentation des panneaux est fonctionnelle et provisoire ; habillage, assets et sons UI doivent encore passer par Claude puis par la validation humaine. Cette entrée explique l'ingénierie réalisée, sans déclarer RUN-015 clôturée.


### Complément RUN-015 — présentation validée et musique du menu

Claude a habillé le panneau, ajouté le logo/fond et les sons de navigation, confirmation, annulation et erreur. L'humain valide cette passe le 3 octobre 2026, avec une retouche future du détail du logo. La musique choisie existe déjà en Ogg dans le projet : `game.gd` la joue sur le bus Music et l'import active la boucle. Controls et les confirmations gardent le même lecteur ; entrer dans le niveau détruit ce lecteur et laisse place à sa musique propre. Le retour au menu recrée le thème. Les tests vérifient ces transitions ainsi que le passage de fin de piste, sans prétendre qu'une analyse automatique remplace l'écoute humaine.


## RUN-016 — Partie technique : Longbow, coffre et potion

Le joueur garde Sword 0 dans le slot de mêlée. Le coffre gratuit propose une seule récompense fixe, Longbow 0 ; A alterne ensuite les deux slots. Chaque arme conserve son propre temps d’attente : changer de slot ne permet pas de raccourcir son cooldown. Le Longbow inflige 1 HP, part toutes les 1,5 secondes si F reste tenu et disparaît après 20 tuiles de 16 pixels (320 pixels). La vitesse de déplacement retenue est 320 pixels/seconde ; cette valeur technique n’était pas fixée dans la spec.

Une flèche interroge tout le segment parcouru pendant chaque tick physique. Elle ne peut donc pas traverser un mur mince en passant d’un côté à l’autre entre deux frames. Le premier terrain ou ennemi touché termine son trajet ; un ennemi reçoit les dégâts une seule fois. La flèche reste en coordonnées du monde même si le joueur bouge. Elle appartient au joueur pour disparaître à sa mort ou au reset ; la pause fige le projectile et les cooldowns.

Le coffre devient consommé pour la tentative dès que sa fenêtre exclusive s’ouvre. Refuse ou Escape ne donnent rien ; le reset le restaure tant que l’arc n’est pas acquis. Pour Accept, la sauvegarde reçoit `Longbow0` avant que le joueur obtienne l’arme. Si le disque refuse l’écriture, le coffre revient pour réessayer ; le test recharge aussi le fichier après acquisition pour vérifier que l’arc survive et que le coffre ne donne pas de doublon. Le slot actif repart sur Sword au spawn, mais les deux armes acquises restent disponibles.

La potion utilise une zone de contact. Elle demande au joueur de soigner 0,5 HP et ne disparaît que si le soin réel est positif. À vie pleine, elle reste donc présente et peut soigner si le joueur se blesse tout en restant dessus. À 2,8 HP, elle remonte à 3 HP sans dépasser le maximum. Une nouvelle tentative recrée la potion.

Les tests ont exercé la physique, les entrées, les dégâts, la pause, les changements d’arme, les refus et la persistance. Le HUD indique les deux slots verticalement avec le texte de l’arme active. Ces labels et les repères CHEST/POTION servent à l’intégration technique ; flèche, chevalier à l’arc, icônes, coffres/potion et sons/VFX attendent la contribution Claude. Les trois captures rendues ne valent pas validation artistique, et RUN-016 n’est pas clôturée.


### Complément RUN-016 — présentation livrée et contrôle du shard

Claude a ajouté les animations avec arc, la flèche et ses effets, le coffre animé, la potion et le soin, les icônes des deux slots et le feedback violet des shards, avec les sons associés. Ces ajouts utilisent les signaux du gameplay ; ils ne changent ni dégâts ni cadence ni collisions. L’humain valide la passe le 3 octobre 2026.

Le gain de shard est déjà crédité par la mort de l’ennemi. Son animation n’est donc pas un nouvel objet à collecter. Le sprite historique de pièce reste dans la scène mais est masqué : vérifier sa texture ne démontre plus ce que le joueur voit. Le test cherche désormais le shard animé visible, vérifie que la pièce est cachée, puis simule un contact et vérifie que ni coins ni shards ne sont ajoutés.

Les positions du coffre et de la potion seront finalisées en RUN-017. RUN-027 reprendra les sons approximatifs et le mix d’acquisition, le détail du logo et la mort en mode arc, qui utilise encore l’épée. Ces limites acceptées ne changent pas les règles d’équipement validées.


## 3 octobre 2026 — RUN-017 : introduction et tutoriels N1, checkpoint technique

Une scène héritée permet de construire N1 à partir du terrain existant sans le régénérer. `eidolon_vale.tscn` reprend le slice et active l'introduction, avec des positions propres pour le coffre et la potion. Le slice demeure utilisable par les tests de physique. New Game charge N1 ; une sauvegarde qui pointait vers l'ancien slice arrive aussi dans N1 en conservant ses armes, sa banque et ses flags.

Le panneau de dialogue reprend le bandeau déjà présent dans le HUD. Il dévoile le texte progressivement, laisse un délai pour lire, puis passe automatiquement à la phrase suivante. Space termine toute la conversation. Le panneau fonctionne pendant la pause, alors que joueur et ennemis restent figés. À la fin, le niveau écrit le flag du dialogue avant de rendre le contrôle ; si le disque échoue, le panneau reste ouvert et E retente l'écriture. Il faut relâcher les touches de confirmation/attaque/saut/pause avant de reprendre le jeu.

Les tutoriels réutilisent la fenêtre contextuelle existante et son propriétaire de modale exclusif. Ils expliquent déplacement et monnaies, armes/santé, les deux chemins et la potion/sortie. Continue enregistre leur validation ; Escape les écarte pour cette tentative. Une mort ne rejoue donc pas une explication validée, mais peut reproposer celle qui a été fermée sans validation. New Game réinitialise ces flags.

Les parcours automatisés de N1 utilisent les vraies entrées et la physique jusqu'au paiement de 12 coins et à la sortie. Leurs tests de bord, distincts, placent parfois le joueur près d'un objet pour isoler un refus ou un soin. La destination suivante est injectée uniquement dans les tests : cette fixture n'est pas N2. Les captures ont vérifié le bandeau, l'erreur de sauvegarde, le tutoriel, le coffre et la potion ; elles montrent encore un repère SPIRIT provisoire. Le rendu artistique du Spirit et le playtest humain restent à réaliser : ce checkpoint ne clôture pas RUN-017.

La recette de fermeture immédiatement après acquisition a révélé un autre détail : arrêter la musique ne suffit pas si des sons d'équipement/récompense sont actifs. Le niveau arrête désormais les lecteurs audio avant de quitter, et le coffre vérifie l'état de fermeture avant de jouer un son retardé. Sans ce garde, son timer relançait le son de révélation après l'arrêt initial ; le journal détaillé Godot identifiait la ressource audio encore retenue.

## 3 octobre 2026 — RUN-017 : seconde passe, séquences d'ouverture

La première passe visuelle de Claude est validée. La demande suivante change la navigation : Space passe maintenant une seule phrase, même pendant l'apparition de ses lettres. Maintenir Space ne passe pas plusieurs phrases. L'avancement est silencieux et chaque phrase reste affichée deux secondes de plus que précédemment. Le flag du dialogue n'est toujours écrit qu'après sa dernière phrase ; passer la première ne suffit donc pas à enregistrer toute la conversation.

Une animation de présentation peut montrer le chevalier mort sans provoquer sa vraie mort. Le niveau fige le jeu, garde sa santé et pilote un nombre de zéro à un : le script du chevalier choisit la frame correspondant à cette progression. Pour l'instant il relit la mort à l'envers ; lorsque Claude ajoute un strip `resurrect`, le même code utilise ses frames dans l'ordre. À la fin, le chevalier passe à idle puis récupère les contrôles après relâchement des touches. Le spawn humain est quatre pixels au-dessus du sol : la physique le pose normalement après la séquence, sans déplacer son point de départ horizontal.

New Game écrit une intention de résurrection, et l'entrée N1 enregistre son commencement avant de l'animer. Cette distinction évite de rejouer la séquence après mort, restart ou fermeture, y compris si le dialogue n'a pas encore été terminé. Les sauvegardes anciennes n'ont pas cette intention et ne reçoivent pas rétroactivement une animation de nouvelle partie. Si le disque refuse le flag de commencement, le jeu conserve la pose initiale et propose E pour réessayer.

Le Spirit suit des étapes simples : caché, apparition, présent, disparition, absent. Marcher deux blocs devant le spawn déclenche l'apparition, puis le dialogue. Après ce dernier, s'éloigner de six blocs du Spirit lance sa disparition ; ce seuil reste réglable. Le joueur continue de jouer pendant le départ, et le menu pause gèle sa progression. Le niveau décide quand changer d'étape ; le script artistique dessine l'état et reçoit un hook audio sur SFX. Cela permet à Claude de compléter les sprites et le cue sans réécrire les règles de progression. Les tests exécutés vérifient la séquence, les sauvegardes, les vraies entrées et le gel en pause ; les fondus et la mort inversée restent des fallbacks, pas les nouvelles animations finales.

## 3 octobre 2026 — RUN-017 : fin de l'intégration et pose pendant le dialogue

Claude a ajouté les animations dédiées de résurrection, apparition et disparition, une manifestation lumineuse et le son d'apparition. Le Spirit est placé sur la tombe à `(140,144)`, devant le chevalier ; le corps du chevalier est posé sur le sol et la caméra stabilisée avant la résurrection. Ces contributions et correctifs sont validés humainement.

Le dernier défaut venait du moment où le niveau suspendait le jeu : le chevalier courait encore, donc son sprite conservait une frame de course. Il passe maintenant à idle avant la pause, avec vitesse nulle, attaque annulée et couche d'attaque masquée. Le sprite seul utilise le mode ALWAYS pour laisser l'idle respirer ; le corps physique et les ennemis restent figés. Après enregistrement du dialogue, le sprite reprend son mode hérité et les menus peuvent à nouveau le figer normalement. Ce sont deux responsabilités distinctes : autoriser le rendu à s'animer ne rend pas les contrôles au joueur.

La vraie mort possède déjà son propre mode ALWAYS pour jouer l'effondrement sous l'overlay. La revue a repéré qu'une restauration systématique du mode du dialogue dans le handler de mort le casserait. Ce chemin conserve donc le mode choisi par `die()` ; le nouveau joueur après restart reçoit les réglages de sa scène. Le test vérifie autant l'idle animé pendant le dialogue que la mort animée sous pause, pour éviter de corriger l'une en bloquant l'autre.


## RUN-018 — Équipement standard, coffres payants et soins (5 octobre 2026)

Le contrat numérique a été validé avant le code. Les nouveaux objets sont exercés dans `tests/fixtures/economy_level.tscn` : cette scène de test n’est pas le niveau N2. Les placements de N2–4 et la passe artistique ne sont pas encore livrés.

### Une définition commune pour les armes

`WeaponCatalog` donne les dégâts, l’intervalle entre attaques et la portée des huit armes, niveaux 0 à 5. Le nom sauvegardé reste une chaîne, par exemple `BrutalAxe2` : le format v2 existant suffit, sans ajouter une migration. Les coffres offrent uniquement des niveaux 0–3 et l’upgrade ordinaire s’arrête à 3. Les valeurs 4/5 sont préparées et testées pour Enchant Juice futur, pas accessibles par ces coffres.

Le joueur lit cette définition quand il attaque. Une lame de RANGE1 mesure 24 pixels depuis la main ; le tir compte les blocs de 16 pixels. La forme physique de la lame est dupliquée pour chaque joueur avant d’être redimensionnée : changer l’arme d’une instance ne modifie pas celle des autres. Les projectiles capturent leurs dégâts et leur portée au départ ; une acquisition ultérieure ne change pas les tirs déjà lancés.

Les deux slots ont leurs propres cooldowns. Acquérir une arme ou passer d’un slot à l’autre ne remet pas ces timers à zéro. Cela évite de contourner la cadence en changeant constamment d’arme. La physique et les dégâts sont généralisés ; les sprites hérités Sword/Longbow ne représentent pas encore correctement les nouvelles armes et attendent Claude.

### Pourquoi un coffre payant a deux étapes

Le contrat demande de payer dès l’ouverture, même si l’on refuse ensuite. `level.gd` vérifie la proximité et les fonds, prépare une offre, puis dépense les shards courants avant la banque. Un débit de banque est sauvegardé avant d’ouvrir la fenêtre. Le coffre et son compteur ne sont consommés qu’après un paiement réussi.

La fenêtre suspend le gameplay et laisse choisir l’item ou, lorsqu’il a été tiré, l’upgrade avec gauche/droite. E sauvegarde le choix avant d’équiper l’arme. Escape ferme sans rien donner ni rembourser. Cette séparation est l’exception explicite au contrat de transaction unique RUN-015, validée par l’humain pour RUN-018.

Si le disque échoue au paiement, le coffre garde son offre et ne consomme rien. S’il échoue lors de l’acquisition, la fenêtre garde son offre et son choix pour le retry, sans deuxième paiement. La fermeture avant acceptation laisse l’ancien équipement ; après acceptation, l’arme sauvegardée survit à la fermeture et à la mort. Les coffres et prix croissants repartent de zéro à chaque tentative.

`ChestEconomy` garde deux compteurs indépendants, common et rare. Le prix est le plafond de `base × 1,5^nombre_d’ouvertures`. Aux grands compteurs, une formule flottante pouvait donner un prix inférieur de deux shards : un calcul entier local conserve le résultat exact jusqu’à la limite de sauvegarde. Un prix hors de cette limite est refusé sans mutation.

### Soins de terrain et de kill

La potion mineure expose maintenant une quantité de soin. La potion majeure hérite de sa scène et règle cette quantité à 1 HP, tout en conservant la même collision. À pleine vie, le pickup reste sur place ; un soin partiel est plafonné au maximum et la consommation reste unique. Son dessin actuel est un repère de test.

Un ennemi raccordé par `register_enemy` peut soigner directement le joueur à sa mort. Le profil `ordinary` donne éventuellement 0,5 HP, `elite` éventuellement 1 HP, et `skull` ne donne aucun soin. Un ennemi est récompensé une seule fois ; les soins ne sont ni stockés ni déposés sur le terrain. Les nouveaux archétypes et invocations devront utiliser ce raccord en RUN-019. Le niveau émet `kill_healed` après un soin effectif pour permettre à Claude d’ajouter le feedback.

### Comment le résultat technique est vérifié

`standard_weapons` presse réellement F pour mesurer les cadences et utilise de vraies formes/rayons physiques pour les portées, dégâts, occlusions et collisions. Les sondes aux pointes sont des fixtures contrôlées, pas des parcours humains. `chest_economy` vérifie les tables et les frontières des tirages déterministes ; un petit échantillon aléatoire ne suffit pas à prouver une probabilité.

`reward_transactions` passe par les contacts et touches clavier pour les coffres, erreurs disque, refus, upgrades, soins et mort. `equipment_cold_session` relance des moteurs distincts et utilise Continue pour vérifier ce qui est réellement resté sur disque. `tools/test.sh` isole les données utilisateur et ajoute ces contrôles aux régressions N1 existantes. Les chiffres de recette finale restent au journal. La validation artistique, l’écoute et l’essai humain du nouveau combat ne sont pas remplacés par ces tests.


### RUN-018 — Ce que la passe Claude a intégré

Le chevalier utilise maintenant trois couches de frames : corps, parties devant la traînée et parties devant l’arme. Une arme dessinée séparément se place entre ces couches, avec la même main et le même angle que le rig. Sa longueur suit la portée physique du catalogue ; les grandes armes peuvent dépasser la cellule64×64 sans étirer les pixels. Les anciens atlas/générateurs restent conservés, notamment pour l’écran titre. Le résultat Sword0 est proche mais pas identique pixel à pixel : ce changement visuel a reçu la validation humaine de la run le 5 octobre 2026.

Les couteaux ont leurs postures et lancers. Le projectile reçoit son look au départ, donc un couteau en vol garde cette apparence même si le joueur reprend l’arc. Les couches suivent les frames et le miroir du corps ou du haut du corps, y compris pendant les présentations où le gameplay est suspendu. Leurs cues et VFX ne modifient pas la collision ni les dégâts.

Les slots montrent maintenant l’icône de chaque arme, son niveau et une plaque adaptée au texte. Le coffre présente ses récompenses sur des cartes horizontales ; common et rare ont des silhouettes et sons distincts. Un effet d’ouverture vit séparément du coffre caché pendant le choix. Il observe le changement d’équipement pour jouer le feedback : il ne réalise aucune transaction. La potion majeure et les soins au kill ont aussi leur rendu dédié ; le marqueur provisoire de potion a été retiré après contrôle des références.

Codex a relancé la recette de retour :1743 contrôles, puis68 contrôles avec rendu, sans erreur/fuite. Les crédits gardent les générateurs visuels originaux et les sources Helton Yan CC BY4 des sons. Les mesures de format/crête et les captures ne remplacent pas l’écoute et un essai humain : ces validations humaines ont été reçues le 5 octobre 2026 ; revue Jev et inspection des preuves terminées, RUN-018 est DONE localement.


La validation humaine de RUN-018 est reçue le 5 octobre 2026 après les explications de vérification du rendu, des sons et du combat/coffres. Les nouveaux objets restent intégrés aux fixtures : cette validation n’ajoute pas de placement dans les futurs niveaux N2–4 ni de banc d’essai interactif complet.


## RUN-019 — Checkpoint technique : menaces et exploration N2–4

Le contrat du 5 octobre 2026 est validé. Les familles fonctionnent dans des scènes de test ; N2–4 ne sont pas encore construits. La contribution Claude apporte désormais les animations et sons ; sa passe est validée en l’état. Cela ne documente pas à soi seul un playtest interactif complet.

Les ennemis avancés partagent un script de comportement avec des paramètres par scène. Warrior poursuit et prépare son coup ; Archer s'arrête pour tirer ; Sorcerer prépare une zone au sol figée qui explose après une seconde. Bloated blesse au contact, Chud par sa mêlée. Chaque profil garde sa santé, ses dégâts et sa récompense. Red étend le Slime existant sans donner d'aggro aux Slimes ordinaires. Un ennemi terrestre voit le joueur dans un rectangle et sans terrain entre eux ; il s'arrête aux bords/obstacles puis revient vers sa patrouille quand il perd l'aggro. Recevoir un coup le repousse sans interrompre son attaque.

Une swarm crée quatre Skulls. La zone conserve quatre emplacements logiques, pas seulement les instances présentes : sortir/rentrer crée de nouvelles instances, mais chaque emplacement n'accorde qu'un shard par tentative. Détruire les quatre donne donc au maximum quatre shards. Un despawn ne récompense pas ; ces ennemis ne donnent pas de soin et ne subissent pas de recul. Au reset, la zone retrouve ses quatre récompenses.

Les pièges utilisent des compteurs de temps de gameplay : les piques passent de rentrés à avertissement puis sortis ; la tourelle annonce son tir et balaie le trajet du projectile pour détecter un impact même entre deux frames. La trappe vérifie que les pieds passent sur sa largeur supérieure avant de s'ouvrir. Elle reste ouverte jusqu'au reset. La plante demeure solide. La pause suspend ces compteurs et déplacements.

Magic Shield donne dix secondes de protection contre les ennemis. Un second pickup remet le compteur à dix, sans ajouter de temps. Les sources de dégâts distinguent maintenant le tir d'un ennemi du tir d'une tourelle : leurs réactions sont similaires, mais la tourelle est un piège et traverse le Shield. Le vide reste fatal. Le buff ne passe pas à une autre tentative ; son pickup revient.

Les bonus HP et les secrets utilisent les flags booléens déjà prévus par la sauvegarde v2. Une acquisition écrit son ID avant de faire disparaître l'objet ou le mur. L'ancien fichier v2 garde ainsi sa banque et ses armes, sans migration supplémentaire. Si l'écriture échoue, le mur reste fermé ou le bonus reste disponible ; le HUD affiche l'échec et un nouvel essai est possible. Un bonus donne +1 MAX HP et +1 CURRENT HP : 1/3 devient 2/4. Le reset soigne à ce nouveau maximum ; l'objet acquis ne réapparaît plus. Accepter une arme ne soigne pas le joueur.

Une plaque peut être pressée ou touchée par un projectile du joueur ; un bouton s'utilise avec E. Les accès liés à un mécanisme ne sont pas payables : `coin_locked=false` empêche E de les contourner. Une porte payante utilise les coins, jamais les shards, et n'est débitée qu'une fois. Le niveau gère les priorités des interactions pour qu'E n'active pas deux objets à la fois. Portes et mécanismes se réinitialisent à chaque tentative ; les secrets révélés et bonus acquis restent durables. Les attaques de mêlée et les projectiles du joueur peuvent révéler un secret, avec occlusion par les autres murs.

Les vérifications exécutent la physique, les entrées d'attaque/interactions, les erreurs disque, la pause, les sources de dégâts et des reprises dans des processus distincts. Le pilote graphique contrôle les états et le viewport640×360. Les chiffres et chemins précis sont dans `runs-journal.md` ; ces tests ne remplacent pas la validation artistique, l'écoute ou le playtest humain. Les vrais budgets de coins et parcours N2–4 seront vérifiés lors de RUN-020.


## RUN-019 — Retour de la présentation Claude

Les sprites suivent les événements du gameplay : préparation, relâche, contact, mort, activation ou acquisition réussie. Un effet de mort vit dans la scène après la suppression de l’ennemi ; il ne garde ni collision ni récompense. Le Shield affiche une aura et clignote pendant ses deux dernières secondes. Les animations et sons restent séparés des calculs de dégâts, des timers et des écritures de sauvegarde. Les crédits recensent les générateurs des 37 PNG et les prises Pixel Combat des 37 WAV.

Un dessin peut dépasser son corps physique : les contours des élites mesurent jusqu’à 34–36 pixels de large, alors que leur collision fait 20×22. L’Art Bible décrit leur taille visible, pas leur zone de contact. Agrandir cette zone modifierait les contacts et déplacements ; l’audit conserve donc la collision du contrat validé.

Le test des piques a révélé une différence entre charger un état et passer à cet état pendant le jeu. Une instance déjà sortie doit montrer ses piques sans jouer une nouvelle extension. Un marqueur explicite distingue le premier affichage des transitions suivantes ; le test contrôle aussi qu’une extension ultérieure joue toujours son animation et son son. Enfin, la simulation des tests à FPS fixe avance plus vite que le mixeur audio : après destruction des fixtures, 300 ms de drainage réel évitent de quitter avec des lectures audio encore retenues. Ce délai concerne le runner, pas le rythme du jeu.

La run est validée humainement le 5 octobre 2026 avec une limite explicite : les nouveaux mobs n’ont pas été essayés directement en debug, faute de scène de test accessible. Les fixtures automatisées et le pilote de rendu les exercent ; cela ne devient pas un essai humain. L’ouverture de PR vers develop est autorisée séparément, sans fusion ni lancement de RUN-020.

La revue Jev et l’inspection des preuves sont terminées ; [PR #22](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/22) est ouverte vers develop. RUN-019 est DONE avec la limite humaine consignée ; les placements N2–4 restent à construire dans RUN-020.


## RUN-020 — Une campagne de quatre niveaux

N2, N3 et N4 sont maintenant des scènes fixes éditables. Leur générateur est un outil d’auteur : le jeu charge les fichiers `.tscn`, sans fabriquer de niveau aléatoire. N1 conserve son terrain humain ; seule sa sortie mène désormais à N2. Chaque scène indique son numéro, son cadrage, sa population et son coût de sortie. Le HUD affiche ce coût au lieu de supposer12 pour tous les niveaux. Le coffre gratuit et la potion tutorielle de N1 ne sont pas recréés ailleurs.

Les coins appartiennent à la tentative et financent les sorties18/25/32. Les40 coins de N4 permettent de payer la porte optionnelle4 puis la sortie32. Les coffres utilisent la banque de shards ; leur dépense ne réduit pas ce budget de coins. Le secret et le bonus HP de N4 utilisent les flags durables déjà construits en RUN-019. Une mort réinitialise les portes et mécanismes, mais conserve leurs acquisitions durables.

Un parcours automatique traverse réellement N1–4 au clavier, obtient le Longbow en N1, ramasse les coins par contact et paie les sorties. Il ne téléporte pas le joueur et ne supprime pas les ennemis. D’autres tests déplacent explicitement des fixtures pour isoler achats, refus, secret, HP et reprise ; ils servent à vérifier les transactions, pas la difficulté naturelle. Trois processus distincts contrôlent la persistance après fermeture du jeu. Le jugement humain sur rythme et difficulté reste nécessaire.

Deux erreurs de construction ont été détectées : les données TileMap doivent commencer par leur en-tête de version ; sans lui, le terrain était illisible et le joueur tombait. Un paramètre nommé `kind` dans le générateur capturait aussi le type du coffre : le rare chest restait common. Les contrôles physiques et économiques ont révélé ces défauts puis vérifié les corrections. Le parcours a également révélé un accès typé à un projectile déjà libéré lors du tir suivant ; supprimer les références invalides avant le nouveau tir corrige ce cas sans changer les dégâts.

Claude Opus5.5 et son sous-agent Sonnet5.5 ont produit les fonds, terrains, accessoires et ambiances sur des fichiers distincts. Les scripts de présentation dessinent autour du terrain existant sans créer de collision. Les générateurs Python restent les sources des images ; les WAV sources sont conservés séparément des OGG bouclés utilisés en jeu. Une capture rendue vérifie la lisibilité et le raccord ; elle ne permet pas de prétendre à une écoute humaine ni de valider un choix artistique. Les preuves chiffrées finales sont au journal, et le parcours humain est décrit dans `docs/RUN-020_PLAYTEST.md`.

## RUN-020 — Ce que le playtest a changé (6 octobre 2026)

Les tests de parcours initiaux montraient que les niveaux étaient franchissables ; ils ne pouvaient pas montrer qu’ils étaient intéressants. Le retour humain distingue précisément les deux : déplacements et progression fonctionnent, mais le contenu et les choix de route sont insuffisants. La refonte des parcours et des silhouettes élites est donc réservée au contrat Claude ; elle n’est pas présentée comme réalisée ici.

L’aggro utilise maintenant deux rectangles : un pour repérer le joueur, un un peu plus grand pour conserver sa cible. Quand le joueur disparaît derrière un obstacle ou sort du second rectangle, un compteur attend deux secondes avant d’abandonner. Cela évite les changements immédiats au bord de la zone. La visibilité reste nécessaire pour commencer une attaque, et la mort du joueur coupe immédiatement la poursuite. Les tests exercent réellement le temps, les rayons contre le terrain et la pause.

La swarm avait déjà quatre emplacements logiques pour limiter les récompenses. Auparavant, un emplacement déjà payé pouvait recréer un crâne sans récompense à chaque réentrée. La correction utilise aussi cet état pour empêcher la recréation du crâne tué. Il reste au maximum quatre adversaires à vaincre par tentative ; seuls les survivants reviennent après une sortie. Une nouvelle tentative réinitialise les quatre emplacements. Le Sorcier ne commande pas cette zone : il utilise ses propres attaques.

Le Shield est contrôlé au point commun où le joueur reçoit les dégâts. En remplaçant la liste de sources protégées par une protection générale, pièges et tirs de tourelle utilisent exactement la même règle. Le retour intervient avant le recul et l’interruption, donc un coup bloqué ne provoque aucune de ces réactions. Le vide reste traité avant le bouclier : tomber hors de la carte tue, conformément au choix humain. Les tests de collision confirment aussi que les obstacles restent solides et que leur danger revient à la fin du buff.

Réduire la cadence signifie ici augmenter le nombre de secondes entre deux tirs. Longbow0 passe à2s et192px, couteaux0 à1,3s et112px. Le catalogue continue à fournir les statistiques de chaque niveau ; les projectiles reçoivent leur portée réelle et sont supprimés au premier impact ou à la limite. Les tests d’armes vérifient les instants de tir et les cibles de part et d’autre de cette limite, pas seulement les nombres du catalogue. Le tutoriel doit annoncer les mêmes valeurs. L’équilibrage du ressenti reste une question de playtest, même lorsque ces vérifications passent.

Les munitions restent une idée retenue pour un contrat ultérieur. Ni inventaire, ni drop, ni caisse, ni règle de sauvegarde pour cette idée n’a été implémenté dans cette passe.

## RUN-020 — Reprise des parcours et collisions des élites

Claude a remplacé les couloirs initiaux par deux fourches dans chaque niveau, avec une route haute et une route basse qui se rejoignent. Les scènes sont toujours fixes ; le générateur d’auteur écrit leurs fichiers, sans génération pendant la partie. Les tests d’interactions prennent désormais leurs repères depuis les objets de la scène : déplacer le bouton ou le bonus HP ne laisse plus une ancienne coordonnée cachée dans le test. Les captures couvrent les deux étages ; seules les entrées de mouvement du pilote peuvent prouver un parcours physique.

Une silhouette visible, une collision de terrain et une portée d’attaque remplissent trois rôles différents. Les nouveaux dessins d’élites rendaient le petit corps20×22 insuffisant : les coups pouvaient traverser leur partie haute et le chevalier pénétrait dans Bloated avant de recevoir le contact. Le rectangle de masse devient44×40 pour Bloated et36×40 pour Chud ; les pieds restent au même point. Les sondes de bord avancent avec la demi-largeur pour garder ce corps sur le terrain. Les pointes, l’arme et les contours animés ne sont pas tous inclus dans la collision.

Bloated reçoit un seuil horizontal de contact30px et garde une bande verticale18px entre les pieds, la visibilité et l’aggro. Chud conserve sa portée et sa préparation de mêlée. Enfin, le sprite du joueur passe au premier plan des acteurs : le dessin peut encore se chevaucher, mais le chevalier reste visible. Les contrôles ciblés vérifient les deux côtés du seuil, la hauteur, les bords et le volume interrogé par les armes. Le jugement sur la lisibilité et la difficulté appartient encore au playtest humain.

Le pilote a révélé un raccord impossible sous l’arche N4 : la marche accolée au plafond laissait16px de hauteur pour un corps18px. Retirer une colonne de deux tuiles au bout de la marche laisse le chevalier descendre vers le passage bas. C’est une correction locale du terrain et de son générateur.


## Clôture RUN-020 et préparation RUN-021

L’humain accepte RUN-020 en l’état. Cela clôt le résultat testé de cette run, sans affirmer que la taille des niveaux et l’équilibrage sont définitifs. Ses remarques deviennent des travaux identifiés de RUN-021 : cohérence visuelle Claude, animation Archer et audio, puis ajustements de portée/cadence et de poursuite par Codex. Aucune valeur de gameplay n’a changé pendant ce lancement.

Un niveau édité manuellement devient la référence à préserver. Un générateur ancien ne connaît pas les décisions prises dans l’éditeur : le rejouer peut détruire ce travail, même si les tests attendent son ancien résultat. On conserve donc les scènes et les changements humains, puis on adapte les tests. Une review ou un audit observe et décrit ; elle n’autorise pas à effacer ou refaire le terrain.

Le clip de l’Archer sert de point de départ à la reproduction, pas de preuve de cause. Il faut observer l’animation et son état dans Godot pour distinguer un dessin mal cadré d’un changement d’état de mouvement. Les contrats de RUN-021 demandent cette preuve et définissent à quel moment Claude remet le fichier partagé à Codex. La production et sa validation restent à effectuer.


## RUN-021 — Sentinelles et portée des tireurs

Les bornes d’une patrouille décrivent un intervalle autour du point de départ. Lorsque ses deux bornes sont égales, marcher fait immédiatement sortir de cet intervalle, puis repartir dans l’autre sens : l’Archer se retournait sans arrêt sur place. Le correctif traite cette configuration comme une sentinelle. Il conserve l’orientation hors aggro, mais peut encore regarder le joueur, tirer, tomber ou reculer après un coup. Les niveaux et leurs perchoirs sont conservés ; on corrige le comportement qui interprète leurs données.

La détection, la distance de déclenchement et le trajet d’une attaque sont différents. Les tireurs repèrent désormais plus loin et commencent leurs attaques à240px. Au premier relais, l’Archer restait immobile en aggro ; sa flèche conserve sa vitesse et sa durée, tandis que Sorcerer annonce toujours un point au sol figé. On teste les positions juste avant et après chaque limite ainsi que les murs, plutôt que de vérifier seulement une valeur exportée.

Les élites poursuivent plus vite et le tir joueur devient légèrement plus lent et plus court. Les tests mesurent la distance réellement parcourue et les intervalles entre tirs, puis la recette doit exercer les routes avec ces changements combinés. La difficulté et le ressenti restent à valider humainement. Le raccord de musique N4 existant est réutilisé ; les candidats SFX préparés ne sont pas présentés comme des sons déjà retenus ou branchés.


## RUN-021 — Poursuite et franchissement des obstacles

La patrouille et la poursuite utilisent maintenant des décisions différentes. Hors aggro, les mobs terrestres gardent leurs limites et leur protection aux bords. En poursuite, Warrior, Archer, Sorcerer, Bloated et Chud cherchent un appui derrière ou sur l’obstacle et sautent si leur corps entier peut passer. Green, Purple et Red conservent leur comportement. La portée de détection, la visibilité et le délai de perte d’aggro ne changent pas : un mur peut encore faire perdre la cible après deux secondes.

Une sonde au niveau des pieds ne suffit pas pour une élite large. Le contrôle utilise son rectangle de collision complet, puis vérifie l’espace de montée et le passage au-dessus de l’obstacle. La recherche locale accepte une marche de72px et un appui inférieur jusqu’à64px ; elle refuse un mur trop haut, un plafond trop bas et un vide sans appui accessible. Le saut conserve les collisions physiques. Ce franchissement local ne calcule pas un itinéraire global entre plusieurs étages. Les Skulls font un détour perpendiculaire à leur direction de poursuite autour d’un corps solide, avec un changement de côté si le premier passage se ferme.

L’Archer avance à22px/s quand la cible est hors portée ou momentanément masquée, puis se stabilise au sol pour tirer dans sa portée de240px avec une ligne de vue libre. Les attaques terrestres ne démarrent plus en plein saut, ce qui permet de terminer la trajectoire. Les coffres et les objets ramassables sont déjà des zones d’interaction, sans corps solide : il n’est pas nécessaire de désactiver les collisions des mobs pour les traverser.

Le coffre common tire désormais son objet directement parmi les niveaux0,1,2 avec des probabilités40,30,30 %. Les anciens10 % de niveau3 rejoignent le niveau2. Une amélioration est une proposition distincte : elle garde sa chance de5 % et peut encore faire passer une arme de2 à3. Le rare, les prix et la sauvegarde des choix restent inchangés.

## RUN-021 — Redescente des élites, profondeur du fond et saut mural

Un corps physique reste légèrement au-dessus du sol à cause de sa marge de collision. Une sonde descendante de64px pouvait donc manquer un sol situé64,075px sous les pieds d’une élite perchée : elle voyait un vide et s’arrêtait. La sonde inclut maintenant cette marge, et la limite de descente rejoint la limite de montée à72px. Un saut vers un appui vérifié réarme aussi la tolérance d’occlusion si la cible reste dans le rectangle de maintien. Cela permet de terminer le franchissement sans oublier le joueur au milieu ; sortir de portée conserve la perte après2s. Les tests physiques répètent montée, descente et retour pour les deux élites, au lieu de vérifier seulement leur arrivée au-dessus du bloc.

Le ferry N2 existait et bougeait, mais le fond se dessinait ensuite par-dessus lui. À profondeur égale, l’ordre des nœuds compte. Les deux scripts de fond imposent désormais une profondeur absolue−100 dans l’éditeur et en jeu : un objet ordinaire placé avant eux reste devant le fond. La ligne rouge horizontale de l’éditeur est simplement l’axeY=0. Une comparaison rendue entre objet visible et caché peut prouver son apparition réelle à l’écran ; tester uniquement sa position ou sa propriété `visible` ne suffisait pas.

Pour le wall jump, presser une direction et Space n’arrive pas toujours sur la même image physique. Le joueur garde donc le dernier contact mural pendant0,10s après le départ. Cette courte tolérance permet encore le rebond si la direction opposée arrive légèrement avant Space. Le rebond consomme cette mémoire, et un nouveau contact devient utilisable après séparation physique. Le buffer existant fonctionne également juste avant l’arrivée au mur. Le double saut reste verrouillé après un wall jump jusqu’au sol : la correction de fluidité ne réarme pas une charge aérienne. Les tests couvrent les deux côtés, plusieurs décalages entre entrées, le retour au mur et l’expiration de la tolérance ; le ressenti reste à essayer humainement.

## RUN-021 — Pourquoi la plateforme suspendue bloquait encore l’élite

Les tests précédents prouvaient les allers-retours sur des blocs pleins. Une plateforme suspendue pose un autre problème : une sonde verticale partant au-dessus du toit peut voir son dessus, alors que le mob se trouve déjà dessous. Tenter de sauter à cet endroit est impossible, car son corps touche le plafond. Une sonde depuis les pieds distingue maintenant le sol inférieur du toit et permet de marcher dessous quand ce passage conduit au joueur.

Dans le N2, le passage fait48px de haut pour un corps d’élite de40px. Les piques à sa sortie réduisent cette hauteur à36px : le mob ne peut pas physiquement sauter par-dessous. Il cherche donc un bord dégagé en reculant sur des appuis sûrs, puis saute sur le toit et redescend. La recherche reste locale et bornée à144px ; elle ne traverse ni vide ni mur. Le recul est un déplacement réel, pas une affectation de position.

Une cible peut rester cachée par le toit pendant la traversée. Un déplacement réellement effectué sur un appui vers elle, ou le long du détour vérifié, renouvelle alors la courte tolérance d’occlusion. Rester immobile contre un obstacle ne suffit pas ; sortir de portée conserve la perte après2s. Les nouveaux scénarios distinguent passage libre, sortie fermée, cible sur le toit, plusieurs phases de patrouille, changement de côté, mort, pause et terrain infranchissable. Cette couverture évite de confondre un seul saut réussi avec une poursuite complète.


## RUN-021 — Un stock courant et un stock d’entrée

Le joueur possède deux petits compteurs : flèches et couteaux. Un projectile créé enlève une unité du compteur correspondant. Ramasser un item en ajoute jusqu’au plafond ; ce qui ne rentre pas reste au sol. Les caisses et tonneaux peuvent être cassés à l’épée : il reste donc un moyen de se ravitailler quand le compteur vaut zéro. Leurs collisions reçoivent les attaques sans bloquer la marche.

Le jeu garde séparément une photo des stocks à l’entrée du niveau. Pendant l’essai, seuls les compteurs du joueur changent. À la mort ou au restart, il recharge cette photo. Lors d’une sortie réussie, il prend une nouvelle photo des stocks restants et l’enregistre avec le niveau suivant. Ainsi N2 terminé avec2flèches donne2flèches à l’entrée de N3 ; en ramasser5 puis mourir dans N3 ramène à2. Les achats et autres sauvegardes intermédiaires utilisent toujours la photo d’entrée : ils ne permettent pas de conserver le loot d’une tentative ratée.

Les piques rétractables avaient un petit socle2px au-dessus du sol. Même sans pointes actives, ce rebord gênait la marche. Le socle est désormais encastré : sa surface arrive au plan de pose, et il reste présent pour les pièges suspendus. Le comportement des pointes et leur danger restent ceux du cycle existant.
