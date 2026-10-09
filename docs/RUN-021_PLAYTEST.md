# RUN-021 — Vérification humaine après passe technique

**Validation globale reçue le 9 octobre 2026 :** l’humain valide toutes les dernières passes Codex et Claude et déclare RUN-020–021 terminées. Les demandes d’essai ci-dessous décrivent les étapes antérieures ; elles restent un guide de régression, sans constituer une liste détaillée des actions réellement effectuées par l’humain. Recette finale et clôture : voir `runs-journal.md`. L’humain autorise aussi le report non bloquant des anciens pilotes `run020_routes` (bas/haut), qui ne suivent plus les placements actuels ; leurs échecs restent visibles et seront signalés dans la PR.

Le visuel Claude et l’ajout de la musique N4 sont validés humainement le6octobre. Cette fiche concerne les nouveaux correctifs Codex et la sélection SFX restante ; les tests moteur ne valent pas playtest humain. Utiliser les scènes actuelles conservées et la chaîne menu→N1→N4, sans rejouer de générateur ni effacer une sauvegarde humaine pour tester.

| Point | Changement à juger |
| --- | --- |
| Archer hors aggro | Les six archers N3/N4 sont désormais des sentinelles en idle : pas de marche sur place ni retournement incessant. L’inspection des71images de la vidéo montre une alternance d’orientation sur place compatible avec le défaut reproduit ; vérifier sa disparition dans votre jeu. Ils poursuivent à22px/s pendant l’aggro, même hors portée240px ou avec tir occlus ; ils ne tirent qu’au sol, à portée et avec ligne de vue libre. Vérifier aussi leur stabilité après perte d’aggro ou recul. |
| Archer et Sorcerer | Détection visible jusqu’à±360px au même étage, déclenchement à240px ; pas de tir initié à travers un mur. Juger le danger à distance et la lisibilité des préparations. La zone Sorcerer reste figée au point annoncé. |
| Bloated et Chud | Poursuite60/48px/s, patrouilles18/12 inchangées ; juger la pression, le contact et la possibilité d’esquiver. Ils doivent tenter de sauter les obstacles franchissables sans traverser les murs/plafonds. |
| Tir joueur | Longbow0 :2,2s/176px ; Knives0 :1,4s/104px. Juger le rythme et la distance de combat, avec équipement de base puis amélioration. Les dégâts sont identiques. |
| Poursuite des mobs | Tester Warrior, Archer, Sorcerer, Bloated (inclus malgré son nom de Slime) et Chud contre un bloc bas, une plateforme/rupture praticable, un piège solide et un plafond bas. Confirmer le franchissement physique quand le saut local le permet, l’arrêt devant un mur/plafond infranchissable, et la poursuite dans la portée d’aggro existante. Vérifier que l’aggro et sa perte gardent leur comportement. Les coffres/objets sont des zones d’interaction : confirmer qu’ils ne bloquent pas le mouvement. |
| Slimes exclus | Vérifier que Green, Purple et Red conservent leur comportement actuel et ne commencent pas à poursuivre/sauter les obstacles. |
| Possessed Skulls | Vérifier qu’ils contournent un solide en vol, sans le traverser, et que la zone d’activation/désactivation reste inchangée. |
| Common chest | Ouvrir un common chest : un item direct doit être niveau0,1 ou2 ; une amélioration séparée peut porter un item de2 à3. Vérifier que le rare chest n’a pas changé. |
| Parcours | N1–4 et variantes hautes/basses, économies de sorties12/18/25/32, achat optionnel4/secret/HP N4 ; vérifier difficulté, sauts, dangers et reprise après mort. Les scènes manuelles n’ont pas été redessinées pour le pilote. |
| SFX | Dix candidats préparés par Claude restent non branchés tant qu’ils ne sont pas retenus. Écoute A/B sous `work/run021/audio/ab_sfx_current_then_candidate.ogg` ; décision et intégration audio restent distinctes. |

Le scope final prévoit des niveaux beaucoup plus grands et plus riches que ces scènes ; ce playtest n’est pas une validation de leur ampleur définitive. La clôture de RUN-021 et la validation0.3.0 demandent inspection des critères du workflow et validation des correctifs restants. Aucune autorisation de push/PR/merge n’est impliquée.


## Correctifs de poursuite et common chest en attente de playtest

Après la validation humaine de la passe précédente, de nouveaux correctifs gameplay ont été demandés puis intégrés : poursuite avec saut local pour les mobs concernés, contournement en vol des solides par les Skulls, et limitation du tirage direct du common chest aux niveaux0–2. Les scénarios ci-dessus sont à tester sur le jeu intégré. La validation humaine précédente ne couvre pas ces correctifs ; aucun résultat de playtest humain nouveau n’est consigné ici.

Vérification Codex terminée : recette complète composée2375PASS/50RESULT, routes basses19/19 et hautes21/21, sauts rendus16/16. Les tests couvrent obstacles16/32px, gap16px, descente32px, refus de vide120px et plafonds/murs infranchissables ; ils ne couvrent pas toutes les géométries possibles ni le perchoir optionnel Coin23 N2 avec Bloated poursuivant. Les changements humains N2 sont préservés.

## Dernière reprise — élites, ferry et rebond mural

Le retour humain de la dernière passe demande encore trois corrections. Après leur vérification technique, contrôler en jeu :

- Bloated et Chud : attirer chaque élite par-dessus un bloc, revenir de l’autre côté et répéter. Elle doit redescendre sur un appui sûr puis remonter, tant que la cible reste poursuivie. Montée et descente locales sont limitées à72px ; cela ne calcule pas un trajet global entre étages.
- Ferry N2 : vérifier le ferry déjà ajouté près deX1209/Y−15, son mouvement, puis le transport et le saut du joueur. Le fond doit rester derrière lui indépendamment de l’ordre de ses nœuds. La ligne rouge de l’éditeur est l’axeY=0.
- Wall slide/jump : Space seul depuis la glissade, Space avec la direction opposée, puis direction opposée légèrement avant Space ; tester les deux côtés, après un double saut consommé et en rebondissant entre murs. Le double saut après wall jump reste interdit jusqu’au sol.

Ces changements demandent un nouvel essai du ressenti ; le retour reçu ne valide pas par anticipation le résultat corrigé.

Vérification finale Codex : recette composée2476PASS/51RESULT,39suites dont variante haute,11sessions à froid et isolation ;102/102contrôles rendus. Les parcours N1→N4 réussissent19/19 et21/21 par entrées physiques. Dans le N2 actuel, le pilote par défaut emprunte la première branche basse puis la passerelle haute et le tunnel ; le second prend la première branche haute puis le même passage. L’ancienne sortie directe basse du deuxième embranchement est fermée par la nouvelle géométrie, et ces succès ne valident pas un parcours complet de cette branche. Les variantes basses/hautes N3/N4 sont couvertes. Le terrain humain et les37scènes de la baseline sont préservés.

## Retour humain et reprise du 7 octobre 2026

L’humain confirme « Retours validés après playtest », puis signale un blocage restant de Bloated N2 lors de l’arrivée dans la zone basse à gauche, avec les deux Red Slimes. La validation de la passe précédente est acquise à cette précision ; aucun détail supplémentaire d’essai n’est inventé.

La correction traite la navigation sous la plateforme suspendue et la sortie fermée par les piques. À réessayer sur le résultat corrigé : arriver par la gauche après avoir laissé l’élite patrouiller, puis changer de côté et de hauteur. Bloated doit utiliser le passage inférieur lorsqu’il est praticable, ou reculer vers un bord libre et passer par-dessus. Vérifier aussi Chud, les montées/descentes répétées, la perte de cible et l’absence de traversée du terrain. Une limite physique ou un trajet hors de la recherche locale ne doit pas provoquer une téléportation ou une collision désactivée.

Les tests natifs de cette reprise utilisent le terrain N2 intact et une chute physique du joueur. Bloated est le mob réel du niveau ; le même terrain avec substitution explicite par Chud est une fixture d’intégration de ce profil, pas un nouveau placement en production ni un parcours N1→N4.

Vérification finale sur le code corrigé : **188/188 contrôles de navigation**, inclus dans **651PASS/21RESULT** (9suites avec les deux parcours,11sessions à froid et isolation), plus **46/46 contrôles rendus**. Les essais natifs vérifient acquisition après chute, toit, retour au sol gauche, absence de heurt du plafond et de pénétration du terrain, poursuite conservée ; les captures des deux profils sur le toit sont inspectées. Les38scènes correspondent à la baseline de cette reprise. Ces preuves ciblées incluent les systèmes IA touchés ; elles ne sont pas présentées comme une nouvelle commande globale de toutes les suites réussie. RUN-021 reste VERIFY pour ce comportement corrigé ; la validation précédente est conservée.


## Nouvelle passe du 7 octobre — Piques et munitions

La passe précédente est testée et validée par l’humain. Cette nouvelle passe a son propre playtest ; [règles validées](RUN-021_AMMO_SPIKES_PROPOSAL.md). Aucun nouvel équilibrage ou visuel présumé accepté.

- Marcher dans les deux sens sur les piques RETRACTED/WARNING, sans saut ; vérifier danger et lisibilité à leur sortie. Rejouer les piques murales et les placements suspendus humains N2.
- Observer le compteur Longbow courant/15, et courant/20 si Knives acquises. Tirer jusqu’à zéro : aucun projectile ; mêlée encore utilisable. Changer/améliorer l’arme sans recharge.
- Casser une caisse et un tonneau à la mêlée ; traverser les props intacts ; vérifier flèches/couteaux visibles, drops et feedback de quantité réellement récupérée. À réserve presque pleine, vérifier que le reliquat reste au sol. Les quantités0/1/3/5 sont aléatoires : un prop vide n’est pas un bug.
- Dans N2, relever le stock juste avant la sortie ; entrer dans N3 avec ce même stock. Y ramasser des munitions puis mourir/restart : retrouver le stock relevé à l’entrée de N3. Retour menu/Continue et relance du jeu doivent aussi restaurer ce snapshot, sans garder le loot de l’essai.
- Juger le confort à réserve basse ou nulle, la visibilité du compteur, la présence des ravitaillements sur les routes, leur quantité et la lisibilité de la casse. Signaler niveau/repère/famille/stock initial si un passage obligatoire paraît nécessiter du tir.

Positions exactes des26props dans le [manifeste d’intégration](RUN-021_AMMO_INTEGRATION_MANIFEST.md). Les captures natives de poses et fixtures de transactions ne constituent pas ce playtest ni une preuve d’équilibrage.


## Complément du 7 octobre — Bloated et poursuite verticale

La passe piques/munitions est validée humainement. Ce complément demande son propre essai :

- DansN2, esquiver Bloated par double saut en arrivant de chaque côté ; comparer la marge pendant la montée, la descente et après l'atterrissage. La vitesse est48px/s ; le mob conserve taille et dégâts. Les essais automatiques ne garantissent pas tous les timings ni les rencontres avec plusieurs mobs.
- Rester sous la plateforme d'un Archer, bouger légèrement horizontalement puis changer de côté. Vérifier l'absence de tremblement et la reprise de poursuite. Faire de même avec Warrior, Sorcerer et élites sur un autre étage, puis au-dessus lorsqu'un chemin existe.
- Faire poursuivre une élite vers un petit toit accessible : le détour et le saut doivent rester actifs malgré l'alignement vertical. Vérifier aussi un joueur qui croise le mob pendant son saut.

Le contrat Claude complémentaire existant est [RUN-021_CLAUDE_HANDOFF_03.md](RUN-021_CLAUDE_HANDOFF_03.md), livré pour les props/HUD de munitions. Les correctifs ci-dessus sont techniques et ne demandent pas de nouveau livrable artistique.


### Secret Wall N4 — complément du 8 octobre

- Depuis un état où `n4_secret_01` n'est pas découvert, approcher le mur : cache, HP et CommonChest2 invisibles, maçonnerie continue sans halo ni couture révélatrice.
- Frapper : effritement et un seul SFX, révélation en0,6s, passage solide jusqu'à la fin puis franchissable. Vérifier la discrétion et le confort sonore en mouvement ; les attaques supplémentaires ne rejouent rien.
- Mettre en pause au milieu : le fondu s'arrête puis reprend. Vérifier que le coffre et le HP deviennent accessibles après l'ouverture.
- Après mort/reprise : cache immédiatement visible sans révélation rejouée. Une sauvegarde ayant déjà découvert le secret commence naturellement dans cet état.

Recette technique :793contrôles ciblés réussis et captures natives. Trois échecs du test Swarm4 existent aussi sur la baseline et ne sont pas corrigés par ce complément. Ces résultats ne constituent pas une validation humaine de RUN-021.


### Indices et tutoriels Secret Wall — complément du 9 octobre

La révélation précédente a été validée explicitement après playtest. Les points suivants concernent la nouvelle passe.

- Avec une partie sans le secret découvert ni les deux acquittements, approcher l'entrée N4 : fissure subtile visible sur le mur, salle/loot encore masqués ; premier message anglais proche, sans déclenchement depuis l'étage au-dessus.
- Continue puis frapper : aucun tuto pendant le fondu ; `Hidden Secrets` apparaît après sa fin et la cache ouverte est visible derrière. Vérifier le confort de la pause et de la reprise, sans attaque involontaire.
- Après Continue, quitter/reprendre : aucun de ces messages ne revient. New Game les réinitialise. Une ancienne partie avec secret déjà acquis mais explication jamais acquittée reçoit celle-ci près de l'entrée.
- Pour comparer les variantes, sélectionner `Exploration/SecretWall`, changer `hint_style` vers `assets/run021/secrets/n4_glow.tres`, `n4_cracks.tres` ou `n4_tint.tres`, puis lancer depuis une partie où le secret est fermé. Conserver les fissures N4 par défaut après comparaison. Juger la subtilité au zoom1,2×, sans indice trop évident ni indice invisible.

Les captures techniques utilisent la vraie scène, des poses injectées et des combats désactivés ; elles ne constituent pas un parcours humain.
