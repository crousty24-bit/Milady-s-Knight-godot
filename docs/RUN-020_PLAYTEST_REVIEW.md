# RUN-020 — Review du playtest du 6 octobre 2026

Branche `feature/run-020-021-campaign`. Retour humain reçu ; la run revient de VERIFY à ACTIVE. La validation de certains systèmes ne vaut pas validation de RUN-020. Aucun lancement de RUN-021.

## Ce que le retour valide et qu’il faut préserver

Progression globale et difficulté graduelle, déplacements, différences de cadence en mêlée, combat de base, fonctionnement des pièges/boutons, lisibilité, paiement/transition entre niveaux, introduction au secret et au bonus HP. Coûts de sortie 12/18/25/32 conservés. Base visuelle Warrior/Archer, Slimes, Skulls et Sorcerer acceptée pour ce stade ; détail ultérieur. N4 est la meilleure référence relative, mais n’atteint pas le niveau de contenu attendu.

## Constats et traitement

| Retour | Preuve dans la baseline | Traitement |
| --- | --- | --- |
| N2/N3 trop faciles et vides | Largeurs 2800/3200 px, soit 4,375/5 écrans de 640 px ; grandes plaques à y144 et petites ruptures, aucune vraie branche | Recomposition du level design réservée à Claude ; allonger un couloir ne suffira pas |
| Récompenses/pièges trop linéaires | Générateur : 7 ennemis N2, 10 N3 ; pièces réparties régulièrement parmi des candidats du parcours, coffre/potion proches de cette ligne | Contrat Claude : parcours, densité et placements à concevoir ensemble, pas simple multiplication des ennemis |
| Aggro insuffisante/perte rapide | Rectangle 240×96, soit seulement ±120 px ; sortie ou occlusion = perte immédiate | Acquisition 480×96, conservation 640×160 ; 2 s continues sans visibilité/hors enveloppe avant perte ; pause gèle le délai, mort du joueur immédiate |
| Skulls peu présents et respawn infini | Zone N4 240×160 ; chaque réentrée recrée quatre crânes, seul leur gain est borné | Zone 480×240 ; quatre emplacements par tentative, vaincu = ne revient plus. Les survivants disparaissent à la sortie et reviennent à la réentrée. Mort/restart réarme les quatre |
| Soupçon de lien Sorcier/swarm dans le retour | Sorcier crée mêlée/explosion au sol ; aucun lien avec `SkullSwarm` | Comportement indépendant existant conservé et explicité ; ce choix n’est pas une nouvelle validation humaine : swarm de zone autonome. Pas d’invocation ni de résurrection par ce Sorcier. Les invocations Necromancer/Boss restent aux runs futures |
| Bloated/Chud trop petits et design insuffisant | Corps visuels consignés ~34×30 et 34–36×29 ; joueur ~24×32. Largeur d’atlas ne prouve pas une silhouette plus haute. Collisions élites20×22 | Refonte des silhouettes/animations et contrôle d’échelle confiés à Claude ; aucun asset/scale/collider élite modifié par Codex |
| Tir trop puissant | Longbow0 320 px/1,5 s ; Knives0 160 px/1 s ; +16 px par niveau | Réduction portée/cadence standard, table ci-dessous ; dégâts, mêlée et Legendary préservés |
| Shield incomplet | `take_damage` ne filtrait que les trois sources ennemies | Bloque désormais toutes les sources de dégâts et leurs réactions ; vide toujours mortel, décision humaine explicite du 6 octobre |
| Black Forrest | Faute dans noms/docs/commentaires | Nom humain corrigé en Black Forest ; identifiants de fichiers `black_forrest` conservés pour ne pas casser les sauvegardes/imports existants |

Les Slimes ordinaires restent en patrouille sans aggro conformément à leur profil ; aucun comportement nouveau inventé. Les réglages d’aggro ne changent ni HP ni dégâts des mobs. Les attaques doivent garder une ligne de vue à leur déclenchement et respecter le terrain.

## Tir — première passe technique à playtester

Un bloc = 16 px. Les valeurs ci-dessous remplacent les anciennes tables de tir RUN-018, à la demande de rééquilibrage du playtest.

| Arme | Portée niveau0 avant → après | Intervalle niveau0 avant → après | Nouveau niveau3 | Nouveau niveau5 préparé |
| --- | --- | --- | --- | --- |
| Longbow | 20 → 12 blocs (192 px) | 1,5 → 2 s | 13,5 blocs / 1,7 s | 14,5 blocs / 1,5 s |
| Throwing Knives | 10 → 7 blocs (112 px) | 1 → 1,3 s | 8,5 blocs / 1 s | 9,5 blocs / 0,8 s |

Progression : +0,5 bloc et −0,1 s par niveau. Dégâts et vitesse de projectile320 px/s conservés. La portée maximale du Longbow devient inférieure à la demi-largeur d’acquisition des ennemis240 px ; cela ne garantit pas qu’un Archer stationnaire tire à cette distance (sa portée reste140 px). Le placement des zones de combat reste donc essentiel. Les niveaux4/5 ne deviennent pas obtenables par cette correction. Aucun équilibrage final prétendu sur la base de tests automatiques.

## Munitions — proposition non implémentée

**Décision humaine du 6 octobre : retenir l’idée pour un contrat dédié ultérieur.** Cette décision ne valide pas les chiffres ci-dessous et n’autorise pas leur implémentation dans la présente correction.

**Avis : intéressante pour limiter le tir permanent et valoriser l’exploration, mais à prototyper après la reprise des niveaux et cette baisse du tir.** Elle ne corrige pas un parcours vide et peut pousser à économiser au point de ne plus utiliser l’arc. Avec des drops seulement aléatoires, une mauvaise série peut aussi priver longtemps du tir.

Prototype proposé, à autoriser explicitement avant code :

- Une réserve commune aux deux armes de tir standard, affichée au HUD ; un projectile effectivement tiré consomme une unité. À zéro, pas de projectile ni de consommation de cooldown ; la mêlée reste disponible. Legendary exclu.
- Hypothèse de départ à tester : 12 unités au début d’une tentative, plafond24. Réserve de tentative, aucune conversion en banque ; mort/restart/reprise/niveau suivant reviennent au stock initial, afin de ne pas introduire immédiatement une migration de sauvegarde. Changer/remplacer/améliorer l’arme ne recharge pas.
- Loot complémentaire sur mobs fixes : exemple initial30 % de chance de3 unités ; Skulls/invocations exclus pour éviter le farm. Ce taux est une proposition, pas une règle actée.
- Pour garantir un minimum de ravitaillement, caisses fixes destructibles donnant6 unités, utilisables à la mêlée et une seule fois par tentative. Elles nécessitent un contrat de création/intégration Claude, des emplacements authored et des tests de destruction/collecte/reset. Ne pas multiplier les ressources au reset au-delà du stock initial.
- Vérifier réserve pleine, ramassage partiel, pause/mort, échange/remplacement, sauvegarde/reprise, feedback à zéro et absence de blocage de progression. La sortie ne doit jamais nécessiter une munition ; secrets/boutons doivent garder une alternative compatible.

Alternative moins coûteuse : drops uniquement, sans caisses, mais l’aléatoire rend l’approvisionnement moins maîtrisable. Suite retenue : **contrat dédié ultérieur**, avec arbitrage des chiffres, de la réserve, de sa persistance et des caisses avant implémentation, éclairé par le playtest des niveaux repris. Aucun fichier gameplay/UI/save pour des munitions n’est créé dans ce correctif.

## Livraison et limites

Les preuves techniques sont au journal. Le [contrat Claude](RUN-020_CLAUDE_HANDOFF_02.md) est le livrable de délégation pour les points de design/visuels ; il ne constitue pas leur réalisation. La RUN-020 ne pourra être clôturée qu’après cette contribution, la recette des scènes finales et un nouveau playtest humain. Aucun push/PR/merge dans cette intervention.
