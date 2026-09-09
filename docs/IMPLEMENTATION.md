# Astra — Architecture et règles du vertical slice

## Règles actuelles
Godot 4.5.1, Windows, clavier Q/D, ESPACE, F, E, R et Échap. Z/S restent associés à haut/bas sans marche verticale. Trois PV, mort et reprise complète du niveau, réserve de bonus sauvegardée, sans checkpoint dans un niveau. Dix-huit pièces fixes, huit communes et cinq par branche ; offrande unique de douze pièces puis sortie. Pas d’inventaire ni de progression RPG. Chaque tentative terminée peut rapporter de nouveaux bonus.

## Mobilité
- Vitesse 105 px/s, accélération/décélération 1100 px/s², gravité 760 px/s², chute plafonnée à 420 px/s.
- Saut initial −255 px/s, double saut −225 px/s. Relâcher réduit la vitesse ascendante ; une pression continue ne répète pas le saut.
- Tolérance au bord 100 ms, mémorisation d’une pression 120 ms. Marcher hors d’une plateforme au-delà de cette tolérance ne donne pas un saut aérien gratuit.
- Glissade descendante automatique plafonnée à 35 px/s sur les murs praticables. Appuyer vers l’extérieur détache du mur.
- Saut mural : ±110 px/s vers l’extérieur, −255 px/s verticalement ; contrôle horizontal imposé 70 ms et réaccroche du même côté empêchée 200 ms. Répéter sur le même mur reste possible.
- Tout saut mural interdit le double saut jusqu’au prochain appui réel au sol. Ni plafond, ni changement de mur, ni glissade ne restituent cette capacité.

## Combat et collisions
Le personnage conserve sa capsule 10 × 18, pieds à y=0 ; le sprite est à y=−12 pour aligner ses pixels opaques. L’épée dure 320 ms et frappe entre 70 et 210 ms. Sa forme 22 × 4 suit sa rotation ; une requête physique à la position actuelle cherche les corps ennemis, et un rayon de terrain bloque les coups à travers les murs. Chaque cible reçoit un dégât maximum par frappe.

Attaquer reste possible au sol, pendant chacun des sauts et pendant la chute. Une entrée en glissade annule la fenêtre de dégâts mais conserve la récupération. Le joueur reçoit un dégât par contact, avec 850 ms d’invulnérabilité. Les slimes partagent une scène et un script ; la variante exportée Green/Purple choisit les animations et 3/4 PV. Patrouille : Green 30 px/s, Purple 34 px/s. Corps 14 × 12, contact 12 × 10, recul reçu ±60/−55 et interruption de 120 ms sans dégâts de contact.

## Architecture
Le niveau possède l’or, le paiement, la tentative, les messages contextuels et le cadrage propre au passage mural. Joueur et slimes possèdent leur santé. Signaux locaux pour collecte, santé, mort, récompense et offrande. L’autoload `Progression` possède la réserve validée, son fichier de sauvegarde et la destination de reprise ; les bonus non validés restent dans le niveau. Le contrôleur distingue sol, air, glissade et mort ; l’attaque possède son propre temps et son indicateur d’annulation.

Couches physiques : terrain=1, joueur=2, ennemis=4, surfaces praticables=8. Le TileSet utilise 1|8 ; poterne, limites extérieures et bac utilisent seulement 1. Le bac reste un AnimatableBody2D à collision unidirectionnelle, 34 × 6, dessus y=48, course 144 px et période 4 s.

## Niveau
La structure du village, de la branche basse et de l’approche corrompue est conservée. La branche haute reçoit une marche de 64 px, deux murs de 112 px séparés de 48 px, une récompense sur le premier sommet et un passage mobile de 176 px. La caméra relève légèrement son cadrage dans cette zone ; les limites extérieures restent hors des trajectoires normales.

| Slime | Position | Variante | Patrouille |
| --- | --- | --- | --- |
| 1 | 355,144 | Green | ±20 |
| 2 | 755,224 | Green | ±20 |
| 3 | 1150,224 | Purple | ±20 |
| 4 | 1740,144 | Purple | ±20 |
| 5, ajouté | 752,48 | Green | ±16 |
| 6, ajouté | 1024,48 | Purple | ±16 |
| 7, ajouté | 1488,144 | Green | ±12 |
| 8, ajouté | 1872,144 | Green | ±20 |

Pièces hautes : (536,100), (608,36), (632,−76), (1008,36), (1136,68). La pièce murale repose au-dessus du sommet d’arrivée pour récompenser l’escalade et rester visible. Le bac et les deux branches sont traversables dans les deux sens.

## Ordre appliqué
1. Alignement du joueur, du bac et des volumes d’attaque/contact ; vérifications moteur et capture Windows.
2. Double saut et tests de charges/pressions.
3. Murs, transitions et tests des interdictions.
4. Variantes de slimes, impacts exacts et contacts crédibles.
5. Quatre ajouts, adaptation locale de la branche haute, gold et limites.
6. Traversées, retours, contrôles des touches, cadences de rendu et captures.

Les scènes restent éditables. Les générateurs d’auteur ont été synchronisés avec ces changements ; ils réécrivent leurs sorties et ne sont pas nécessaires au lancement du jeu.

## Bonus et futurs niveaux

La mort d’un ennemi émet une seule fois `defeated(bonus, position)` ; `bonus_reward` vaut 1 par défaut. `register_enemy()` raccorde ce contrat, y compris pour de futurs ennemis créés à l’exécution. Le niveau crédite le bonus puis affiche une animation de la pièce existante, déjà comptabilisée et non ramassable.

Les premières pièces remplissent `gold` jusqu’à 12 ; l’excédent va dans `bonus`. Après paiement, toute nouvelle pièce rejoint `bonus`. Finir valide et sauvegarde ce bonus ; mourir ou recommencer l’efface. Les niveaux suivants commencent avec leur propre compteur de sceau et une réserve de bonus conservée.

Le champ `next_level_scene` définit la prochaine scène. La victoire prépare la sauvegarde et E effectue le changement de scène ; le champ vide conserve la fin de prototype avec R pour rejouer. La scène de démarrage charge la destination sauvegardée. Voir [BONUS_AND_LEVELS.md](BONUS_AND_LEVELS.md) pour le contrat, le format versionné et les points d’évolution.
