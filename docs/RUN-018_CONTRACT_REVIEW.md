# RUN-018 — Contrat proposé avant implémentation

> **Révision RUN-020 :** Les tables historiques de portée/cadence des armes de tir standard sont remplacées par la passe de rééquilibrage demandée lors du playtest RUN-020 du 6 octobre. Voir [les valeurs actuelles](RUN-020_PLAYTEST_REVIEW.md#tir--première-passe-technique-à-playtester). Les autres règles restent inchangées.

**5 octobre 2026 — Contrat validé intégralement par l’humain (« Je valide le contrat »), tables et exception de paiement comprises.**
Branche : `feature/run-018-standard-equipment`, issue de `develop` propre `6bb15b4`.
RUN-017 DONE et 0.2.0 validée ; `develop` est ancêtre de `main` et leurs arbres sont identiques lors du lancement.

## Vérification du jalon 0.3.0

Les six critères de `runs-workflow.md` sont conservés. Ils sont des conditions de livraison futures, pas des fonctionnalités déjà validées.

| Critère | Lot responsable | État au lancement |
| --- | --- | --- |
| Tables validées, common/rare, rewards/upgrades, Legendary exclu | 018 | À réaliser ; décisions D02/D04 ci-dessous |
| Armes standard hors Fire Gauntlet, persistance, soins terrain/drops | 018 | Sword0/Longbow0 et potion mineure existent ; extension à réaliser |
| N2 à 18 coins, Red/Bloated, piques rétractables/trappes, régression N1 | 019–020 | Contenu à réaliser |
| Warrior/Archer/Sorcerer/Swarm/Chud, tests et télégraphies/SFX P0 | 019 puis 021 | À réaliser |
| Tourelles/plantes/Shield/mécanismes/portes/secrets/HP bonus | 019–020 | À réaliser ; D01/D06/D07 à trancher dans le lot concerné |
| N3/N4 à 25/32, récompenses N4 et budget coins sans soft-lock | 020 puis 021 | À réaliser ; recette/playtest humains requis |

La cohérence artistique et la recette globale relèvent de 021. Les assets fonctionnels nécessaires aux armes/coffres de 018 demandent déjà une passe Claude, sans construire N2–4.

## D02 — Tables d’armes proposées

Conserver les bases de docs/04, le sens de ATK SPEED (intervalle en secondes), 1 RANGE = 24 px et 1 bloc de FALLOFF = 16 px.
Pour chaque niveau `n` de 0 à 5 : DMG = base + `0,5 × n` ; intervalle = base − `0,1 × n` ; RANGE mêlée = base + `0,1 × n` ; FALLOFF tir = base + `n` blocs. Toutes les cadences restent positives, minimum 0,5 s.

| Arme | DMG niveaux 0 / 1 / 2 / 3 / 4 / 5 | Intervalle en s niveaux 0 / 1 / 2 / 3 / 4 / 5 | RANGE ou FALLOFF niveaux 0 / 1 / 2 / 3 / 4 / 5 |
| --- | --- | --- | --- |
| Sword | 0,5 / 1 / 1,5 / 2 / 2,5 / 3 | 1 / 0,9 / 0,8 / 0,7 / 0,6 / 0,5 | 1 / 1,1 / 1,2 / 1,3 / 1,4 / 1,5 RANGE |
| Longsword | 1 / 1,5 / 2 / 2,5 / 3 / 3,5 | 1,5 / 1,4 / 1,3 / 1,2 / 1,1 / 1 | 1,2 / 1,3 / 1,4 / 1,5 / 1,6 / 1,7 RANGE |
| Brutal Axe | 1,5 / 2 / 2,5 / 3 / 3,5 / 4 | 1,2 / 1,1 / 1 / 0,9 / 0,8 / 0,7 | 0,8 / 0,9 / 1 / 1,1 / 1,2 / 1,3 RANGE |
| Dark Scythe | 2 / 2,5 / 3 / 3,5 / 4 / 4,5 | 2,5 / 2,4 / 2,3 / 2,2 / 2,1 / 2 | 1,5 / 1,6 / 1,7 / 1,8 / 1,9 / 2 RANGE |
| Warhammer | 1,5 / 2 / 2,5 / 3 / 3,5 / 4 | 1,5 / 1,4 / 1,3 / 1,2 / 1,1 / 1 | 0,8 / 0,9 / 1 / 1,1 / 1,2 / 1,3 RANGE |
| Halberds | 1 / 1,5 / 2 / 2,5 / 3 / 3,5 | 1,5 / 1,4 / 1,3 / 1,2 / 1,1 / 1 | 2 / 2,1 / 2,2 / 2,3 / 2,4 / 2,5 RANGE |
| Longbow | 1 / 1,5 / 2 / 2,5 / 3 / 3,5 | 1,5 / 1,4 / 1,3 / 1,2 / 1,1 / 1 | 20 / 21 / 22 / 23 / 24 / 25 blocs |
| Throwing Knives | 0,5 / 1 / 1,5 / 2 / 2,5 / 3 | 1 / 0,9 / 0,8 / 0,7 / 0,6 / 0,5 | 10 / 11 / 12 / 13 / 14 / 15 blocs |

Upgrades ordinaires +1 plafonnés à 3 ; aucun upgrade proposé si l’arme active est déjà niveau 3, 4 ou 5. Les niveaux 4/5 sont définis et testés mais restent réservés à Enchant Juice (RUN-023). Fire Gauntlet, Legendary et leurs capacités restent exclus.
Aucun combo à dégâts supplémentaires ni comportement spécial implicite pour les armes standard. Conserver coup unique par cible, occlusion, attaque aérienne et restriction de mêlée en wall slide. Le dessin devra respecter la portée physique exacte, y compris fractionnaire.
Le tir des Knives sera horizontal et balayé comme Longbow, à 320 px/s, avec disparition au premier impact/à portée. Les cooldowns par slot sont conservés, y compris lors d’un remplacement d’arme, pour empêcher une frappe gratuite en alternant/acquérant.

## D04 — Coûts proposés

| Niveau du monde | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Premier common | 5 | 7 | 10 | 15 | 22 | 34 | 50 | 75 |
| Premier rare | 15 | 21 | 30 | 45 | 66 | 102 | 150 | 225 |

Pour `k` ouvertures précédentes du même type dans la tentative : `prix = ceil(base × 1,5^k)`. Compteurs common/rare indépendants, incrémentés uniquement à l’ouverture payée ; reset mort/restart/reprise/changement de niveau. Exemple N2 : common 5, 8, 12, 17 ; rare 15, 23, 34, 51. Pas de plafond produit ajouté ; une valeur hors domaine entier sûr est refusée sans mutation.
Les prix N5–9 sont une table préparatoire ; le budget réel des niveaux sera vérifié avec leur contenu. Les coûts n’emploient jamais les coins.

## D04 — Pools proposés

Tirages indépendants du type d’arme, du niveau et de l’upgrade, RNG injectable pour tests reproductibles.

- Niveaux common au contrat RUN-018 : 0/1/2/3 = 40/30/20/10 %. **Remplacé en RUN-021 le 6 octobre 2026 sur demande humaine : drops directs0/1/2 = 40/30/30 %, aucun drop direct3.** La proposition séparée d’upgrade reste à5 % et peut monter une arme2→3.
- Niveaux rare : 2/3 = 70/30 %. Pas de case Legendary ou Fire Gauntlet tant que non implémentés.
- Chance de proposer aussi l’upgrade de l’arme active : common 5 %, rare 15 %, uniquement si niveau inférieur à 3. L’arme active est capturée à l’ouverture ; le jeu est suspendu jusqu’au choix.

| Arme | Poids common | Poids rare |
| --- | --- | --- |
| Sword | 9 | 5 |
| Longsword | 8 | 9 |
| Halberds | 7 | 6 |
| Warhammer | 6 | 8 |
| Brutal Axe | 5 | 4 |
| Longbow | 4 | 7 |
| Throwing Knives | 3 | 3 |
| Dark Scythe | 1 | 1 |

Poids relatifs normalisés sur les huit armes disponibles ; respect de l’ordre de rareté docs/04 après retrait des armes exclues. L’item est garanti ; l’upgrade ne l’est pas. Accepter un item plus faible reste possible ; un seul choix attribué.

## Ouverture payante, refus et reprise — exception explicite au contrat RUN-015

Les specs exigent un débit à l’ouverture, avant le choix, et aucun remboursement si refus/Escape. Proposition :

1. E vérifie proximité, exclusivité modale, vie et fonds ; prépare une offre figée.
2. Débiter gains courants puis banque ; si une écriture de banque échoue, ne rien consommer et permettre retry sans nouveau tirage.
3. Après paiement réussi seulement, consommer le coffre de tentative, incrémenter son compteur et afficher l’offre. Aucun nouveau débit sur E maintenu ou retry.
4. Accepter l’item/upgrade l’écrit durablement avant attribution, à coût zéro car déjà payé. En cas d’échec disque, conserver l’offre et permettre retry ou refus sans deuxième paiement.
5. Refus/Escape donne rien, garde le débit et ferme. Fermeture après ouverture garde le débit de banque mais abandonne offre/gains de tentative ; l’ancien équipement reste acquis. Fermeture après acceptation conserve le nouvel équipement.

**Cette séparation paiement puis acquisition est à valider comme exception à la transaction unique acquisition + paiement du contrat RUN-015**, nécessaire pour appliquer le refus payant décrit dans docs/04. Le coffre tuto gratuit garde ses règles actuelles.
Les common/rare réapparaissent à chaque tentative ; leurs offres ne sont pas durables. Le reset permet donc un nouveau tirage contre un nouveau paiement. Les gains non dépensés restent perdus à la mort/fermeture ; les armes confirmées restent durables. Aucun mécanisme anti-farm permanent ajouté. Les mobs fixes récompensent une fois par vie, reviennent au reset ; règles d’invocations/swarm à préciser en RUN-019 (D06), pas inventées ici. Offrandes/rétention restent en RUN-023.

## Soins proposés

Potion majeure de terrain : 1 HP, plafonné à MAX HP ; pleine vie = reste disponible ; reset restaure la potion. Potion mineure reste à 0,5 HP.
Drops sur kill : soin instantané au joueur vivant, aucun objet/inventaire ; un tirage par ennemi effectivement vaincu, même à pleine vie (pas de soin stocké).

| Monde | Minor sur mob ordinaire/avancé éligible | Major sur élite |
| --- | --- | --- |
| N1 | 0 % | 0 % |
| N2–4 | 10 % | 3 % |
| N5–7 | 6 % | 2 % |
| N8–9 | 4 % | 1 % |

Possessed Skulls exclus ; Boss et N10 hors de cette table. Un kill attribue soit le soin mineur soit le majeur selon le profil, jamais les deux. En 018, vérifier les profils futurs avec fixtures ; leur intégration aux ennemis de production appartient à 019. Aucun nouveau mob ni soin de résurrection implicite.

## Vérification requise après validation du contrat

- Chaque arme/niveau : dégâts fractionnaires, intervalle réel F maintenu, portée aux limites, gauche/droite, occlusion, impact unique, air/wall slide, interruption, pause et remplacement sans reset de cooldown.
- Tirages déterministes : limites cumulées de poids, item garanti, upgrade conditionnel/cap, absence de Fire Gauntlet/Legendary ; ne pas valider les probabilités par un petit échantillon aléatoire.
- Coffres réels avec clavier : argent insuffisant, débit mixte, compteurs indépendants, choix horizontal/E/Escape, coût après refus, E maintenu, deux coffres proches, double validation, erreur disque au débit puis acquisition/retry.
- Persistance en vrais processus : ouverture puis fermeture, acceptation puis fermeture, mort/restart après achat ; banque débitée conservée, équipement confirmé conservé, gains perdus, coffre/compteurs reset. Anciennes saves Sword0/Longbow0 intactes.
- Soins par contact et kill : pleine vie, blessure partielle, max, mort, unique émission de kill, reprise ; Skull exclu et RNG aux bornes.
- Import Godot 4.7.2, isolation user:// et régressions complètes via tools/test.sh ; pilotes avec rendu 640×360, inspection captures des huit armes, UI common/rare et soin ; validation humaine art/écoute et essai combat/coffres.
- Journal et learning décrivant uniquement le travail implémenté ; revue Jev puis inspection des preuves avant DONE. Aucun lancement 019 pendant attente.
