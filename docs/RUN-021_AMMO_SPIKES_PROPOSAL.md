# RUN-021 — Nouvelle passe : piques rétractables et munitions

**7 octobre 2026 — Contrat validé par l’humain, avec correction du transfert entre niveaux.** La validation humaine reçue ce jour couvre la passe précédente, notamment la reprise de Bloated/Chud. L’humain valide ensuite la proposition, sauf le reset au niveau suivant : le stock courant doit y être transmis. RUN-021 reste ouverte ; implémentation locale de cette nouvelle passe autorisée.

## Constats avant implémentation

- `scenes/retractable_spikes.tscn` possède un socle `Solid` de32×2px, centré àY−1 : il dépasse donc de2px au-dessus de l’origine. `scripts/retractable_spikes.gd` désactive seulement `Points` hors phase EXTENDED ; `Solid` reste toujours actif. C’est la cause probable du blocage rapporté, à reproduire physiquement avant correction. Les placements comprennent aussi des piques murales : ne pas traiter uniquement le sol horizontal.
- Les munitions ne sont pas implémentées. `docs/04_PROGRESSION_ECONOMY_ITEMS.md` et la review RUN-020 renvoient à une proposition non approuvée, différente de la demande actuelle (réserve commune12/24 et autres drops). Les chiffres humains de cette nouvelle demande remplacent cette ancienne proposition après validation.
- Le tir dans `scripts/player.gd` crée actuellement un projectile sans réserve. `scripts/progression.gd` conserve l’équipement ; les resets de niveau passent par le rechargement de scène. Des réserves de tentative peuvent donc être ajoutées sans stock durable ni migration de sauvegarde.

## Piques : comportement proposé

En RETRACTED et WARNING, passage à pied dans les deux sens, sans saut imposé par le socle, sans dommage. En EXTENDED, pointes solides et dangereuses comme actuellement ; timings, dégâts0,5 et protection Shield hors VOID conservés. La montée physique d’une pointe sous le joueur doit rester cohérente et être testée.

Codex reproduit le blocage puis corrige localement la collision du socle pour l’encastrer au plan de pose. Le support utile ne doit pas disparaître pour les placements suspendus. Aucun changement global du mouvement joueur, du TileSet ou du terrain pour contourner ce défaut. Vérifier les quatre orientations et les placements réels ; ne pas déplacer les piques humaines par défaut.

**Claude n’est pas nécessaire pour la cause technique identifiée.** Son contrôle visuel est conditionnel : si le sprite rétracté paraît encore former une marche après correction, il adapte seulement son cadrage/dessin pour correspondre à la surface praticable, selon le contrat séparé. Pas de retouche graphique présumée nécessaire avant rendu.

## Munitions : règles validées

| Famille | Stock nouvelle partie / ancienne v2 | Plafond |
| --- | ---: | ---: |
| Longbow | 10 | 15 |
| Throwing Knives | 12 | 20 |

Deux réserves distinctes, identiques pour tous les niveaux d’amélioration d’une même famille. Une unité consommée par projectile effectivement créé, même si le tir manque ou heurte le terrain. Une pression refusée ou un cooldown actif ne consomme rien. À zéro : pas de projectile, pas de nouveau cooldown, feedback discret et mêlée disponible. Le lance-flamme et les autres armes hors ces deux familles sont exclus.

Les deux réserves sont initialisées une seule fois au début de la tentative depuis le snapshot d’entrée du niveau, même avant acquisition de la famille ; le HUD montre celle de l’arme de tir équipée. Acquérir, remplacer, améliorer ou changer de slot ne recharge pas et ne convertit pas les réserves. Ainsi une acquisition durable d’équipement ne crée pas une source de recharges répétées dans une tentative.

### Reset validé : chaque essai restaure le stock reçu à l’entrée du niveau

Nouvelle partie : Longbow10, Knives12. Lors d’une sortie réussie vers un autre niveau, les deux stocks **courants** sont transmis et sauvegardés atomiquement avec la destination : ils deviennent les stocks d’entrée du niveau suivant. Mort, restart, retour au menu puis reprise à froid restaurent ces stocks d’entrée. Les dépenses et loots de l’essai courant ne modifient jamais ce snapshot avant une sortie réussie. Un replay du même niveau ne remplace pas son snapshot par son loot de fin d’essai.

Exemple validé : N2 commence à10 → tire3 →7 → loot3 →10 → mort →10 au nouvel essai. Si N2 se termine à2, N3 commence à2 ; dans N3, loot5 →7 → mort →**2**. Les loots sont ainsi transportables après réussite d’un niveau, sans accumulation par morts/restarts. Les familles encore non équipées suivent aussi leurs réserves séparées.

Sauvegarde : ajouter un snapshot de munitions d’entrée optionnel à la v2 ; les anciennes v2 dépourvues de ce champ commencent à10/12, sans altérer banque/équipement/drapeaux. Champ présent invalide : save refusée, pas de remplacement silencieux. Échec d’écriture de sortie : destination et stocks d’entrée antérieurs restent protégés ; retry sans double règlement. L’équipement suit sa persistance actuelle. Aucune comptabilité séparée des munitions initiales/lootées dans l’essai.

Cette règle interdit le cumul entre essais ratés ; elle permet le cumul plafonné au fil des niveaux réussis. Entrer avec0 reste possible : props accessibles à la mêlée et chemins obligatoires sans tir requis. Le confort de ce cas doit être vérifié en playtest.

### Caisses, tonneaux et drops

- Deux props distincts, non bloquants pour le déplacement ; une frappe dommageable suffit à détruire chacun, indépendamment du niveau d’arme. Destruction possible à la mêlée sans dépenser de munition ; les projectiles standard peuvent aussi les toucher et sont consommés normalement.
- Chaque instance a une famille de munitions explicite et visible (flèches ou couteaux), fixée dans l’éditeur. Le changement d’arme ne modifie pas son loot. Aucun drop de munitions ajouté aux ennemis/coffres existants.
- Même table initiale pour les deux props : **0/1/3/5 unités à20/40/30/10 %**. Moyenne1,8unité par prop ;80 % de chance d’obtenir quelque chose. Valeurs exportées/centralisées pour réglage ultérieur, pas d’équilibrage final revendiqué.
- Tirage une seule fois à la destruction ; pas de double loot par hits simultanés, pas de respawn pendant la tentative. Drop au sol collectable au contact, vers sa famille même si elle n’est pas équipée. Au plafond, il reste au sol ; ramassage partiel laisse le reliquat. Afficher la quantité réellement récupérée.
- Budget de prototype proposé : N1 deux props flèches ; N2 six props (quatre flèches/deux couteaux) ; N3 huit (quatre/quatre) ; N4 dix (cinq/cinq). Répartir caisses et tonneaux et alimenter plusieurs routes ; aucune cellule terrain ni objet existant remplacé. Ces nombres sont des valeurs de départ validées, pas une mesure du besoin réel des niveaux.
- Sorties et parcours obligatoires restent réalisables sans munition ; contrôler également les boutons/secrets et le tutoriel de tir. Une mauvaise série aléatoire reste possible : juger le confort en playtest avant d’introduire éventuellement une garantie de ravitaillement.

## Responsabilités et vérification après validation

Codex : collision des piques, compteurs/consommation/reset, destructibilité/drop/collecte, raccord HUD, scènes techniques des nouveaux props, tests et intégration. Claude : silhouettes, animation de destruction, pickups/icônes, lisibilité HUD et placements additifs selon le [contrat Claude](RUN-021_CLAUDE_HANDOFF_03.md). Les fichiers partagés ont une remise exclusive ; aucun travail simultané sur une même scène/script.

Recette attendue : reproduction puis marche réelle sur piques rétractées/avertissement, danger et transitions, quatre orientations et niveaux réels ;10/15 et12/20, consommation unique, zéro/cooldown, familles et upgrades, drops0/1/3/5 et frontières des pondérations, destruction unique, saturation/reliquat, pause, morts/restarts/reprises à froid, transition de niveau et absence d’écriture du loot intra-tentative en sauvegarde, transfert atomique des stocks courants à la sortie réussie. Puis parcours et régressions des systèmes touchés, rendu des nouveaux objets/HUD, contrôle des diffs de terrain et playtest humain. Fixtures déterministes ne prouvent pas l’équilibrage ni le confort des routes.

La validation humaine couvre le passage des piques, le reset au stock d’entrée avec transfert du courant au niveau suivant, les réserves séparées, les props/drops et leurs budgets de prototype, ainsi que le partage Codex/Claude. Elle autorise l’implémentation locale de cette passe ; pas de push, PR, merge, clôture ou prochaine run implicite.
