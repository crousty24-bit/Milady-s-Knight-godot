# Bilan de la passe d’amélioration

Ce bilan décrit la mobilité et les rencontres. La fonctionnalité bonus ajoutée ensuite est documentée dans [BONUS_AND_LEVELS.md](BONUS_AND_LEVELS.md) ; les résultats actuels sont dans [VALIDATION.md](VALIDATION.md).

## Problèmes détectés et corrections
Le chevalier flottait de 4 px à cause de la marge transparente de ses frames : le sprite a été descendu, en conservant les pieds de la capsule à l’origine du personnage. Le bac se trouvait 3 px au-dessus des berges : son dessus est désormais au même niveau. La collision fixe de l’épée a été remplacée par un rectangle fin qui suit la lame ; les coups sont bloqués par le terrain.

Les slimes avaient tous 2 PV et le Purple était une simple teinte du Green. Ils utilisent maintenant les deux spritesheets et une variante exportée dans leur script commun. Leur volume de contact passe de 15 × 12 à 12 × 10, à l’intérieur du corps de 14 × 12. Les ronces conservent leur volume de 30 × 10, déjà contenu dans le dessin des pointes : il n’a pas été agrandi.

## Capacités et règles
Le saut initial reste à hauteur variable. Un second appui déclenche un double saut un peu moins puissant, signalé par une petite onde et un son plus aigu. Aucun troisième saut n’est possible.

Le contact avec un mur praticable ralentit automatiquement la chute. ESPACE repousse le personnage vers le haut et l’extérieur ; une brève séparation précède une nouvelle accroche. Les remontées successives d’un même mur et les sauts entre murs sont possibles. Après **tout saut mural**, le double saut reste interdit jusqu’à un vrai atterrissage, même après un changement de mur, une chute ou un contact avec un plafond.

L’épée fonctionne au sol, pendant les deux sauts et pendant la chute. La glissade interdit son déclenchement et annule une frappe déjà commencée, sans annuler son temps de récupération.

## Rencontres et difficulté
Exactement **quatre ajouts**, pour **huit slimes : cinq Green et trois Purple**. Green meurt en trois frappes, Purple en quatre. Les nouvelles rencontres se trouvent sur les deux berges hautes, à la réunion des branches et avant la poterne. Les Purple occupent la branche basse, la seconde berge haute et la zone corrompue.

Le recul reçu par les slimes est moins exagéré (±60/−55), avec une interruption de 120 ms pendant laquelle leur contact est inoffensif. Le joueur conserve trois PV et 850 ms d’invulnérabilité après impact. Une frappe touche chaque ennemi au maximum une fois, même lorsqu’elle traverse plusieurs ennemis.

## Niveau et gold
La branche haute reçoit une marche de 64 px, une zone murale de 112 px et un passage de 176 px nécessitant le bac. La caméra montre mieux les sommets. Le décor de fond suit les nouvelles berges ; la poterne est dessinée à la hauteur de sa collision et ses surfaces lisses ne permettent pas l’escalade.

La pièce de l’escalade est placée sur le sommet d’arrivée, plutôt qu’au milieu du vide. Les autres pièces hautes guident vers la marche, le double saut, le bac et le retour au chemin commun. Le niveau conserve 18 pièces, une offrande de 12 et le choix entre deux branches. Les deux chemins restent réversibles et les 18 pièces sont récupérables dans une tentative.

## Vérifications et suite
**111 contrôles automatisés réussis**, complétés par **27 contrôles graphiques de cadence** à 30/60/144 images/s. Les deux branches passent aussi dans la fenêtre Windows. Les scénarios complets jouent avec les actions normales et la physique réelle, sans téléportation ni modification de santé/gold. Voir [le détail des validations](VALIDATION.md).

Le pilotage manuel Windows reste indisponible ; il n’y a donc pas encore de validation humaine de la sensation de contrôle. La prochaine passe devrait commencer par une session de découverte pour mesurer le confort de la remontée sur un même mur, la lisibilité de la règle « saut mural → pas de double saut » et la difficulté des rencontres Purple. Aucun système supplémentaire n’est nécessaire avant ce retour.

## Ajustement demandé : recul mural et vitesse des slimes

L’impulsion horizontale du saut mural passe de 155 à **110 px/s**, et le contrôle imposé de 100 à **70 ms**. La hauteur et la séparation minimale avant réaccroche sont conservées. Une remontée avec la direction maintenue vers le mur produit désormais un recul maximal mesuré de **13,75 px** ; les sauts entre murs restent fonctionnels.

La patrouille passe de 27 px/s pour tous les slimes à **30 px/s pour Green** (+11 %) et **34 px/s pour Purple** (+26 %). Ces valeurs alimentent `velocity.x` ; les PV et les dégâts ne changent pas.

Les 111 contrôles ont été rejoués après cet ajustement, ainsi que trois mesures ciblées du recul et des vitesses effectives. Le pilote de parcours a été corrigé pour revenir vers sa cible lorsqu’il dépasse le sommet avec le saut plus compact.
