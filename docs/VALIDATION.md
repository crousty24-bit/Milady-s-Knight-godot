# Validation — passe mobilité et collisions, 9 septembre 2026

## Résultats vérifiés

Godot **4.5.1 stable officiel**. Les onze suites de `tools/test.sh` passent : **150 vérifications**, sans erreur de parsing, d’exécution ni fuite signalée dans leurs logs finaux.

| Suite | Contrôles | Ce qui est exercé |
| --- | ---: | --- |
| movement | 6 | Déplacement, saut, second saut, refus du troisième, atterrissage |
| physics | 6 | Saut court/long, attaque aérienne, buffer, coyote, transport, ronces |
| mobility | 25 | Glissade, sauts muraux, même mur/murs opposés, blocage du double saut, plafond, états d’attaque |
| combat | 18 | Green en 3 frappes, Purple en 4, cible unique par frappe, groupe, portée, mur, contact, feedback et mort |
| platform | 14 | Accostage à pied des deux côtés, transport, saut, atterrissage à quatre phases, marche sur le bac |
| boundaries | 6 | Poterne fermée, limites non grimpables, portée du double saut, récompense murale |
| keyboard | 9 | Événements de touches Q/D/Z/S/ESPACE/F/E/R/Échap, reprise et pause |
| integration | 23 | Huit slimes dont trois Purple, 18 pièces, paiement, dégâts, mort, reprise, victoire et fosse |
| bonus | 39 | Récompenses, surplus, HUD, mort/reprise, sauvegarde, erreurs, transition et démarrage mémorisé |
| routes | 2 | Branche haute puis branche basse, chacune depuis le départ jusqu’à la victoire |
| backtracking | 2 | Retour par la première branche et exploration de l’autre, dans les deux ordres |

Les routes normales finissent avec **13 pièces collectées, 12 payées et 7 bonus validés** : 1 pièce excédentaire et 6 récompenses d’ennemis. Les parcours avec retour finissent avec **18 collectées et 14 bonus validés** : 6 pièces excédentaires et les 8 ennemis. Le pilote conserve 2 ou 3 PV selon le parcours et la phase du bac.

Les pilotes de parcours n’écrivent ni position, ni vitesse, ni santé, ni gold ; ils ne retirent aucun ennemi ou plateforme. Ils utilisent les actions publiques du jeu, combattent, sautent, grimpent et attendent le bac. Les tests ciblés emploient des mises en situation isolées, explicitement indiquées dans leur source.

## Windows et cadences de rendu

Les mesures à 30/60/144 images/s ci-dessous datent de la passe mobilité. Les vérifications Windows de la fonctionnalité bonus figurent dans la section dédiée en fin de document.

- Deux branches traversées graphiquement sous Windows, NVIDIA RTX 4070 Ti, sans erreur.
- Captures Windows avec collisions visibles examinées : chevalier au sol, épée active, slimes, murs et bac.
- Régénération des scènes et du TileSet : sorties identiques aux fichiers livrés. Import final de l’éditeur et `git diff --check` réussis.
- Captures prises pendant les actions réelles du pilote : double saut, saut mural et déplacement sur le bac. Captures de présentation du village, des murs, du sommet, de la branche haute et de la poterne examinées.
- `render_timing.gd` exécuté graphiquement à **30, 60 et 144 images/s**, sans `--fixed-fps`, avec VSync désactivée et physique à 60 Hz. Les cadences relevées sont respectivement 30, 60 et 144. **9 contrôles par cadence, 27 au total, tous réussis**.
- Ce test supplémentaire vérifie double saut, attaque aérienne, glissade, saut mural, persistance de l’interdiction du double saut, transport et départ du bac.

Les dernières sorties sont dans `work/test-results/`, les captures dans `work/`. Ces artifacts sont ignorés par Git.

## Corrections et précautions issues des vérifications

- Décalage du chevalier corrigé par le sprite, sans modifier sa capsule ni les collisions de toutes les tuiles.
- Bac aligné aux berges ; essais à pied et à différentes phases pour contrôler sa collision unidirectionnelle.
- Zone d’épée orientée comme la lame, interrogée à sa position actuelle et bloquée par le terrain.
- Contact ennemi réduit, interruption courte et non dangereuse après une frappe.
- Collisions de poterne et limites extérieures adaptées aux nouvelles possibilités d’escalade.
- Caméra relevée localement pour montrer les sommets sans les masquer sous le HUD.
- Les pilotes ont été adaptés aux nouveaux mouvements : deux pressions doivent être séparées par un relâchement effectivement traité. Le test de cadence laisse aussi expirer la pression mémorisée avant sa mise en situation sur le bac ; autrement, l’atterrissage déclenchait correctement un saut bufferisé et invalidait le test de transport.
- Une attente de libération audio élimine les avertissements de sortie des nouvelles salles de test.

## Limites

Le contrôle manuel de la fenêtre Windows n’a pas pu démarrer : le service renvoie « failed to launch codex app-server … chemin d’accès … introuvable ». Aucun essai manuel au clavier n’est revendiqué. Les tests d’événements de touches passent dans Godot ; ils ne constituent pas une session humaine au clavier.

Ces vérifications établissent le fonctionnement et la traversabilité des scénarios couverts. Elles ne prouvent pas l’absence de tout exploit et ne mesurent ni le plaisir de découverte, ni la difficulté pour un nouveau joueur. La prochaine validation utile est une courte session humaine sur la montée murale, l’attente du bac et les rencontres Purple.

## Reproduire

```bash
./tools/test.sh
./tools/run.sh --script res://tests/routes.gd
./tools/run.sh --script res://tests/backtracking.gd
./tools/run.sh --debug-collisions --script res://tests/visual.gd
./tools/run.sh --disable-vsync --max-fps 30 --script res://tests/render_timing.gd
./tools/run.sh --disable-vsync --max-fps 60 --script res://tests/render_timing.gd
./tools/run.sh --disable-vsync --max-fps 144 --script res://tests/render_timing.gd
```

Les commandes de cadence doivent rester sans `--fixed-fps`, pour découpler le rendu de la physique. Les générateurs de scènes ne sont pas nécessaires aux tests.

## Vérification après ajustement du recul et des patrouilles

- Recul mural réglé à 110 px/s avec contrôle imposé 70 ms ; patrouille Green 30 px/s et Purple 34 px/s.
- `tools/test.sh` rejoué : **111 contrôles réussis**, dont les deux routes et les retours complets ; journal `work/test-results/tuning-suite.log`.
- Trois mesures ciblées dans la physique réelle : recul maximal de 13,75 px avec retour vers le même mur, Green à 30 px/s et Purple à 34 px/s ; journal `work/test-results/tuning-probe.log`.
- Les mesures à 30/60/144 images/s de la section précédente concernent la version avant cet ajustement des valeurs.
- Les deux branches ont également été traversées dans la fenêtre Godot Windows avec ces nouveaux réglages, sans erreur ; journal `work/test-results/tuning-windows.log`.

## Fonctionnalité bonus et progression entre niveaux

- Suite complète : **150 contrôles réussis**, journal `work/test-results/bonus-suite.log`.
- Les **39 contrôles bonus** passent aussi avec le moteur Windows natif ; les écritures et remplacements sont effectués dans un fichier temporaire isolé sur le système de fichiers de sauvegarde, puis ce fichier est retiré. Aucune modification de `progress.json` du joueur.
- Deux traversées graphiques Windows avec la nouvelle UI : réussite, 7 bonus par tentative ; journal `work/test-results/bonus-routes-windows.log`.
- Les retours complets donnent 14 bonus ; chaque dépôt est vérifié par différence avec la réserve de départ du pilote.
- Captures Windows `bonus-earned.png`, `bonus-threshold.png` et `bonus-banked.png` examinées : récompense avec la pièce existante, séparation du sceau et des bonus, gains à valider puis réserve.
- La transition E est exercée vers `tests/fixtures/next_level.tscn` : nouvelle tentative, sceau fermé, santé restaurée, réserve conservée. La scène de démarrage retrouve également la destination mémorisée.
- Les cas d’erreur couvrent un fichier illisible/invalide, une version future, une écriture impossible, une destination manquante et la relance E de la sauvegarde sans double récompense.

Reproduction ciblée : `./tools/run.sh --headless --fixed-fps 60 --script res://tests/bonus.gd`. Pour les captures : `./tools/run.sh --script res://tests/bonus_visual.gd`. Les lancements avec `--script` isolent la réserve en mémoire ; la persistance normale s’utilise avec F5 ou le lanceur Windows.
