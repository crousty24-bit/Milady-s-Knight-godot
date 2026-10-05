# RUN-003 — Essai d'échelle

Essai reproductible dans Godot 4.7.2 : ouvrir `scenes/scale_comparison.tscn`, puis régler `grid_size` à 16 ou 32 dans l'inspecteur. Les captures de la scène à **640×360** sont [16×16](media/run-003-scale-16.png) et [32×32](media/run-003-scale-32.png). Les regénérer avec `tools/capture_scale_comparison.gd` via `tools/run.sh --script res://tools/capture_scale_comparison.gd` (avec `GODOT_BIN` configuré). La capture requiert un rendu graphique ; le mode `--headless` utilise un moteur de rendu factice.

## Méthode et portée

Les deux vues conservent une fenêtre de 640×360, le même sol et les mêmes positions d'objets. La variante 32 double la taille des motifs de terrain, des sprites existants, des silhouettes provisoires et de leurs contours de collision. Elle **n'ajoute aucun détail graphique** : elle mesure l'occupation de l'écran d'un agrandissement uniforme, pas la qualité d'assets dessinés sur une grille 32. Le projet reste réglé à 320×180 ; cette scène d'essai ne change pas la résolution du jeu (RUN-004).

Le terrain plat et les arbres sont une maquette inspirée des éléments du slice existant. Il n'existe pas encore de scène N1 conçue à la main. Le chevalier et le Slime utilisent les premières frames des sprites du projet ; l'humanoïde, les piques dessinées ici et le coffre sont des silhouettes de comparaison. Le prototype possède des piques générées par code, mais aucun sprite de piques, d'humanoïde ou de coffre utilisable comme asset final. Ces substitutions interdisent de valider la cohérence artistique d'un ensemble 32×32 de production.

## Mesures vérifiées

| Élément | Source actuelle / collision | Vue 16 | Vue 32 |
| --- | --- | --- | --- |
| Terrain | Cellule et polygone 16×16 dans le slice | 16×16 | 32×32 simulé |
| Joueur | Frame 32×32, pixels opaques 13×19 ; capsule de rayon 5, hauteur 18 | Opaque 13×19 ; collision 10×18 | Opaque 26×38 ; collision 20×36 simulée |
| Slime | Frame 24×24, pixels opaques 14×12 ; corps 14×12 | Opaque 14×12 ; collision 14×12 | Opaque 28×24 ; collision 28×24 simulée |
| Humanoïde | Aucune ressource ; silhouette 24×36 proposée pour l'essai | 24×36 | 48×72 simulé |
| Piques | `hazard.tscn` : zone 30×10 ; dessin de jeu procédural | 30×10 | 60×20 simulé |
| Coffre | Aucune ressource ; silhouette 24×20 proposée pour l'essai | 24×20 | 48×40 simulé |

Les dimensions opaques viennent de `Image.get_used_rect()` sur les frames de repos sélectionnées ; elles ne décrivent pas toutes les animations. Les contours jaunes sont des rectangles indicatifs : la collision joueur réelle est une capsule et aucun test physique de la variante 32 n'a été effectué.

## Lecture et décision

À 16, les sprites actuels paraissent très petits à 640×360 : la frame de 32 px du joueur ne contient que 19 px opaques en hauteur. À 32, les silhouettes et le danger occupent davantage l'écran, mais les pixels du chevalier et du Slime sont simplement doublés et deviennent plus grossiers. La taille des frames ne doit donc pas être confondue avec la hauteur opaque, et la grille du terrain peut rester à 16 même si les futurs personnages ont une silhouette plus grande ou plus détaillée.

**Décision humaine du 23 septembre 2026 :** grille de terrain **16×16 retenue**, conforme à l'art bible, avec réévaluation de la taille opaque des personnages et des collisions lors de l'intégration de leurs véritables assets. Aucun changement de grille ou de résolution du prototype n'est nécessaire ici. La comparaison avec N1 et les assets humanoïde/coffre finaux sera possible lorsqu'ils existeront ; elle servira à ajuster leurs proportions et collisions, sans remettre automatiquement en cause la grille retenue.
