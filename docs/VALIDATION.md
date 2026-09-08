# Validation du vertical slice — 8 septembre 2026

## Résultats

Godot 4.5.1 stable officiel. **35 vérifications réussies** dans cinq suites exécutées via `tools/test.sh` :

- Mouvement : 5 (sol initial, déplacement physique, saut, absence de double saut, atterrissage).
- Physique : 6 (saut court ≈19 px et long ≈45 px, attaque aérienne, buffer, coyote time, plateforme porteuse, contact avec les ronces).
- Intégration : 20 (18 pièces, répartition 8/5/5, collecte physique unique, refus à 11, paiement unique à 12, victoire conditionnelle, deux coups sur un slime, invulnérabilité, mort, reprise complète, pause et fosse).
- Parcours : 2 traversées intégrales, haut et bas ; **13 pièces collectées, 12 dépensées, 1 restant**, deux PV restants.
- Retours : 2 parcours longs, dans les deux sens de choix des branches ; approche de la porte, retour par la branche initiale, exploration de l'autre, sortie avec **18 collectées et 6 restantes après paiement**.

Les pilotes de parcours emploient les actions d'entrée publiques et la physique réelle. Ils ne téléportent pas le joueur, ne suppriment pas les ennemis et ne modifient pas santé/gold. Les suites ciblées utilisent des mises en situation contrôlées pour isoler un contact ou un seuil.

## Lancements et rendu

- Import propre Linux : réussi.
- Import propre Windows, copie sans `.godot` dans `work/clean-windows-check` : réussi, code de sortie 0. Le nouveau projet ne dépend pas du cache de l'ancien.
- Lancements graphiques Linux durant le développement : réussis (WSLg/Mesa).
- Deux traversées graphiques sous **Windows / NVIDIA RTX 4070 Ti** : réussies.
- Captures du village, embranchement, passage haut, corruption, poterne, frappe et mort examinées visuellement.
- Lanceur `Lancer-Windows.cmd` testé : code de sortie 0.
- Fermeture demandée à la fenêtre : testée séparément avec `tests/close_window.gd`, sans erreur.
- La dernière série de captures Windows se termine sans erreur ni fuite audio.

## Corrections issues des tests

1. Protection du saut court lorsqu'un relâchement et une nouvelle pression surviennent dans la même image.
2. Ajout d'un palier haut près de la jonction pour permettre le retour en arrière.
3. Habillage du sol par une pierre sobre et bord praticable clair : les premiers motifs de l'atlas étaient trop chargés.
4. Ronces lumineuses différenciées des plantes décoratives et indice contextuel de danger.
5. Nettoyage audio lors de la fermeture et attente de libération des lectures dans les tests. Une fermeture forcée très rapide avec `--quit-after` peut produire un avertissement de ressources audio ; la fermeture normale utilise un court délai d'arrêt.
6. Correction du typage du tableau de couleurs du terrain, détectée au lancement graphique.

## Limites honnêtes

- Pas de session jouée manuellement au clavier : le service de contrôle Windows a échoué deux fois avant de cibler une fenêtre. Les actions ont été injectées **dans Godot**, et les captures proviennent du moteur graphique réel.
- Ces tests attestent le fonctionnement et la traversabilité, pas le plaisir de jeu ni l'équilibrage auprès de personnes découvrant le niveau.
- Niveau compact : une route connue est terminée en moins d'une minute par le pilote. La cible initiale de 5–8 minutes de découverte reste à évaluer.
- Pas d'export Windows autonome : lancement avec Godot 4.5.1 installé, via le lanceur fourni ou l'éditeur.
- La corruption est un décor local statique ; pas de simulation de propagation, conformément au scope.
- Provenance/licences des assets d'origine à compléter.

## Reproduction

```bash
./tools/test.sh
./tools/run.sh --script res://tests/routes.gd
./tools/run.sh --script res://tests/visual.gd
```

Les logs détaillés et captures restent dans `work/` et ne sont pas versionnés. Ne pas lancer plusieurs pilotes en même temps dans la même fenêtre/projet si l'on souhaite comparer les captures : ils partagent leurs noms de fichiers.
