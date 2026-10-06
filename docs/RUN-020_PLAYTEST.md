# RUN-020 — Recette humaine N1–4

Branche : `feature/run-020-021-campaign`. RUN-020 a reçu le playtest du 6 octobre et revient ACTIVE pour corrections ; les points acceptés et refusés sont dans [la review](RUN-020_PLAYTEST_REVIEW.md) ; RUN-021 est autorisée ensuite sur cette même branche.

## Parcours complet

Dans Godot4.7.2, ouvrir le projet puis **F5**. **New Game** remplace la progression active après confirmation (le précédent fichier est sauvegardé en backup) ; **Continue** la conserve. Partir de N1, accepter le Longbow gratuit puis avancer jusqu’à N4. Flèches : mouvement ; Space : saut/double saut ; A : changer d’arme ; F maintenu : attaquer ; E : interagir/confirmer ; Escape : pause. Menus : flèches et E.

| Niveau | Coins placés | Coût de sortie | Points à juger |
| --- | ---: | ---: | --- |
| N1 Eidolon Vale | 18 | 12 | terrain existant, raccord vers N2 |
| N2 Blight Town | 24 | 18 | Red/Bloated, piques rétractables, trappe, première montée de difficulté |
| N3 Black Forest | 32 | 25 | Warrior/Archer, plante/tourelle, rythme combat/plateforme |
| N4 Forbidden Graveyard | 40 | 32 | Sorcerer/Chud, swarm4, secret, porte optionnelle et mécanisme obligatoire |

Les scènes sont aussi accessibles directement : ouvrir `scenes/blight_town.tscn`, `scenes/black_forrest.tscn` ou `scenes/forbidden_graveyard.tscn`, puis **F6**. Elles utilisent l’équipement et les flags de la sauvegarde actuelle ; F6 ne donne pas gratuitement le Longbow ni des shards. Ce raccourci permet de rencontrer réellement les nouveaux ennemis sans refaire N1.

## Exploration N4

- Première petite salle en hauteur, vers x560 : frapper/tirer sur le mur secret ; potion majeure et rare chest derrière. Le secret reste révélé après mort/reprise.
- Deuxième salle en hauteur, vers x1300 : porte à4 coins, bonus HP derrière (+1 HP actuel et maximum durable). Il reste36 coins possibles, suffisants pour la sortie à32.
- Vers x2640 : actionner le bouton avec E pour ouvrir le passage obligatoire. Cette porte ne peut pas être achetée.
- Mort/Restart : coins, portes, mécanismes, buffs et gains non déposés repartent à zéro ; équipement, banque, secret et HP acquis restent. La sortie N4 termine ce segment, sans niveau5.

## Retour attendu

Indiquer les passages trop difficiles/faciles, les temps morts, la lisibilité des attaques/pièges/objets et le confort des sauts. Écouter les trois ambiances avec musique/SFX (volume, timbre, boucle). La musique Dreamer est actuellement partagée par N2–4 ; le choix musical N4 reste un point de la passe visuelle suivante.

La recette automatique et les captures natives sont consignées dans `runs-journal.md`. Elles ne remplacent pas ce playtest. Une validation explicite de RUN-020 permettra sa revue de clôture puis le lancement de RUN-021.

## Retest après correctifs techniques

Vérifier l’aggro plus large et sa perte après2s, la swarm nettoyée qui reste vide malgré sortie/réentrée, le tir plus court/lent et le Shield contre piques/plantes/tourelles (vide mortel). Les coordonnées de ce guide restent celles des scènes initiales ; les niveaux et élites doivent encore être repris par Claude selon [le contrat](RUN-020_CLAUDE_HANDOFF_02.md), puis ce guide sera adapté aux scènes finales. Aucun résultat artistique nouveau n’est encore livré.
