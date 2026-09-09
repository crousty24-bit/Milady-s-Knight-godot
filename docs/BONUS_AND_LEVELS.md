# Bonus coins, sauvegarde et progression entre niveaux

## Règles livrées

- Les Green et Purple rapportent chacun **1 bonus** à leur mort, une seule fois. La propriété exportée `bonus_reward` permet à un futur ennemi de rapporter davantage, ou zéro.
- La récompense est automatique : une petite pièce et « +N BONUS » apparaissent sur l’ennemi. Le sprite, l’animation et le son proviennent de la scène de pièce existante ; ce feedback n’est pas un nouvel objet à collecter.
- Les pièces du décor alimentent le sceau jusqu’à **12**. Tout excédent est un bonus ; après ouverture, chaque pièce ramassée est également un bonus.
- Les bonus sont séparés des pièces du sceau et ne peuvent pas servir à l’ouvrir.
- Les bonus de la tentative sont **validés uniquement à la fin du niveau**, après le paiement et le franchissement de la sortie. Mort, reprise avec R ou fermeture anticipée les perdent. La réserve des niveaux déjà terminés reste acquise.
- Rejouer et terminer à nouveau un niveau accorde de nouveaux bonus. Les ennemis ne réapparaissent pas pendant une tentative.

Exemple : 14 pièces ramassées et trois ennemis tués donnent **12 pour le sceau + 5 bonus**. Avec une réserve précédente de 20, le HUD affiche « BONUS 25 » et « +5 à valider ». La victoire sauvegarde 25 ; une mort conserve seulement les 20 précédents.

## Affichage

Le bandeau conserve les PV et Échap, avec deux compteurs distincts : `SCEAU 00/12` puis `SCEAU OUVERT`, et `BONUS total`. La ligne sous BONUS distingue les gains à valider de la réserve. À la victoire, le bilan indique les bonus validés et la nouvelle réserve. Les grandes valeurs sont abrégées ; le survol du compteur donne les valeurs exactes.

## Responsabilités et interfaces

| Élément | Responsabilité |
| --- | --- |
| `scripts/coin.gd` | Collecte physique unique d’une pièce ; réutilisation visuelle pour les récompenses déjà créditées |
| `scripts/slime.gd` | PV, combat et émission unique de `defeated(bonus: int, at: Vector2)` |
| `scripts/level.gd` | Compteur du sceau, bonus de la tentative, paiement, validation de sortie, HUD et transitions |
| `scripts/progression.gd` / autoload `Progression` | Réserve validée, sauvegarde versionnée et changement de scène |
| `scenes/game.tscn` | Démarrage sur le niveau mémorisé |

`register_enemy(enemy)` raccorde le signal de récompense sans doubler la connexion. Le niveau enregistre automatiquement les enfants de `Enemies` au démarrage. Pour un ennemi généré plus tard, appeler cette méthode au moment de son ajout. L’ennemi doit verrouiller son état mort **avant** d’émettre `defeated`.

`Progression.settle_level(earned_bonus, destination)` écrit d’abord le nouvel état, puis met à jour la réserve en mémoire. Le niveau garde un verrou `reward_settled` : deux événements de sortie, une nouvelle pression E ou une notification répétée ne valident pas deux fois la même tentative. `Progression.change_level(path)` effectue la transition vers une scène valide.

## Sauvegarde

Le jeu normal utilise **`user://progress.json`**, dans le dossier utilisateur que Godot attribue à ce projet. Il ne dépend donc pas du répertoire d’installation du jeu. Format v1 :

```json
{
  "version": 1,
  "bonus_bank": 25,
  "resume_scene": "res://scenes/vertical_slice.tscn"
}
```

Seuls la réserve validée et le niveau de reprise sont persistants. PV, pièces du sceau, bonus de la tentative, ennemis et état de porte sont recréés à chaque entrée dans le niveau.

L’écriture passe par un fichier temporaire puis son remplacement. Une écriture échouée ne crédite pas la mémoire : l’écran de victoire conserve les gains et propose E pour réessayer. Une reprise avec R est bloquée pendant cette attente afin de ne pas effacer ces gains. Une sauvegarde illisible, un montant invalide ou une version inconnue ne sont pas écrasés. Si le fichier est réparé, E peut retenter la validation. Si la scène sauvegardée n’existe plus, le jeu reprend au niveau du prototype en conservant la réserve.

## Ajouter un prochain niveau

1. Créer sa scène avec la structure utilisée par `level.gd` : `Player` et sa caméra, `Coins`, `Enemies`, `GoldGate`, `ExitArea`, `HUD`, `Music`, ainsi que le terrain et le décor propres au niveau.
2. Dans la scène précédente, renseigner **`next_level_scene`** avec son chemin `.tscn` via l’inspecteur.
3. Vérifier que la sortie ne valide qu’après l’ouverture du sceau. Le bilan proposera automatiquement **E — Niveau suivant** ; la sauvegarde mémorisera cette destination.
4. Le nouveau niveau repart avec ses PV, ses ennemis, son sceau et zéro bonus de tentative. La réserve reste disponible dans `Progression`.
5. Lancer F5 pour vérifier aussi la reprise après fermeture. F6 permet de travailler directement sur une scène particulière.

Le prototype reste constitué d’un seul niveau de jeu. `tests/fixtures/next_level.tscn` est uniquement une scène de contrôle pour tester une véritable transition et une reprise ; ce n’est pas un deuxième niveau conçu pour le joueur.

## Évolution prévue, sans systèmes prématurés

- Autres ennemis : reprendre le signal `defeated` et configurer leur récompense ; aucun nouveau type de pièce nécessaire.
- Plusieurs niveaux : renseigner les destinations successives. Pour un catalogue plus grand ou des embranchements, remplacer les chemins sauvegardés par des identifiants stables et une table de niveaux, avec migration explicite du format v1.
- Nouveaux champs de sauvegarde : augmenter la version et écrire une migration testée ; ne pas remettre la réserve à zéro silencieusement.
- Menu de sélection, profils de sauvegarde, dépenses de bonus et récompenses uniques par niveau restent des décisions futures. La réserve actuelle n’implique aucun de ces systèmes.

## Vérification

`tests/bonus.gd` couvre les récompenses uniques et variables, le surplus avant/après paiement, les compteurs, la mort/reprise, le changement réel de scène, le démarrage mémorisé, l’écriture et la relecture sur disque, le remplacement d’un fichier existant, les erreurs et la reprise de sauvegarde. Les pilotes complets vérifient aussi la réserve obtenue par combat et exploration.

Les pilotes lancés avec `--script` utilisent automatiquement une réserve en mémoire et ne lisent pas `progress.json`. Les tests de disque utilisent un nom temporaire unique dans `user://`, puis le retirent ; la sauvegarde du joueur n’est pas modifiée. Le lanceur Windows et F5 utilisent la vraie persistance.
