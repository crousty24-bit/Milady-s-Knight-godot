# RUN-020 — Contrat Claude : reprise après playtest

**6 octobre 2026 — Contrat de contribution préparé, non exécuté.** Commande humaine : review puis correctifs RUN-020, aucun changement visuel/design par Codex, délégation de ces changements dans un contrat Claude. Branche commune `feature/run-020-021-campaign`. RUN-020 ACTIVE ; RUN-021 attend sa clôture. Le présent contrat remplace, pour cette reprise, la restriction historique de Claude à l’habillage de N2–4.

## Objectif et responsabilité

Claude Code Opus5.5 est propriétaire de la recomposition du level design N2–4 et de la refonte visuelle Bloated Slime/Chud Blob, avec sous-agents Sonnet5.5 sur responsabilités disjointes si utile. Codex possède les règles techniques, la revue et la recette d’intégration. Le contrat est prêt pour une session Claude ; aucun lancement ou résultat Claude n’est prétendu par sa rédaction.

Lire AGENTS.md, CLAUDE.md, la fiche RUN-020, [retours/review](RUN-020_PLAYTEST_REVIEW.md), docs03/06/13 et le manifeste RUN-019 pour les élites. Lire `.local/asset-paths.md` si présent avant des recherches d’assets, puis les exigences/catalogues ciblés. Préserver sources et crédits, ne pas modifier les bibliothèques externes.

## Problèmes à résoudre

N2 et N3 sont courts et presque rectilignes : 2800/3200 px, soit 4,375/5 écrans ; N4 3600 px, soit5,625 écrans, comporte deux salles secondaires mais reste insuffisant. Les coins/items/coffres/pièges suivent trop souvent la même ligne. Le joueur peut traverser avec peu de décisions. L’objectif n’est pas de rendre le jeu brutal : préserver la difficulté graduelle et la jouabilité jugées bonnes, tout en augmentant nettement la richesse du parcours.

Avant d’éditer les scènes, Claude doit produire dans son manifeste un plan coté de chaque niveau (largeur, hauteur exploitable, sections, branches, chemin obligatoire, raccourcis/retours, budget). Il choisit le gabarit et le langage spatial ; Codex ne fournit pas de layout à reproduire. Repère de travail à évaluer par Claude : une emprise explorée de l’ordre du double de l’actuelle, obtenue par largeur et/ou étages, sans ajouter de couloirs vides. Ce repère n’est pas une dimension humaine validée. Justifier le gabarit retenu avec les sauts réels et la densité de contenu ; documenter toute contrainte nécessitant une décision humaine.

Les passages obligatoires doivent demander autre chose que maintenir une direction : changements de hauteur, franchissements, décisions de route ou séquences d’interaction. Les branches doivent proposer des récompenses lisibles et des risques différents ; éviter des impasses sans intérêt et des détours obligatoires sans contenu. Ne pas ajouter de système gameplay pour forcer artificiellement la longueur. N4 reste la référence relative de complexité/exploration, à enrichir aussi.

## Propriété des fichiers

Après le checkpoint technique Codex, Claude peut éditer :

- `tools/build_run020.py` et les trois scènes `scenes/blight_town.tscn`, `scenes/black_forrest.tscn`, `scenes/forbidden_graveyard.tscn` : terrain, dimensions, placements et connexions locales existantes. Préserver le raccord N1. Maintenir générateur et scènes cohérents ; aucune régénération du N1.
- `scripts/campaign_backdrop.gd`, `scripts/campaign_decor.gd`, `scripts/campaign_terrain_skin.gd`, assets et générateurs visuels RUN-020 nécessaires à l’intégration du nouveau layout. Pas de nouvelles règles dans ces scripts de présentation.
- Nouveaux assets normalisés/sources/générateurs des deux élites (répertoire dédié `run020_feedback` recommandé), et remplacement de leurs ressources de présentation. Dans `scripts/run019_enemy.gd`, **uniquement les tables et méthodes de présentation en fin de fichier**, sur Bloated/Chud. Aucune modification de la logique d’aggro/attaque/dégâts ajoutée par Codex. Ne pas éditer ce fichier pendant que Codex le modifie ; la remise se fait après son checkpoint.
- `docs/RUN-020_ASSET_MANIFEST_02.md` (nouveau), crédits/provenance correspondant aux contributions. Captures/logs/préviews sous `work/run020/claude-feedback/`.

Codex réserve `scripts/player.gd`, `weapon_catalog.gd`, `arrow.gd`, `skull_swarm.gd`, `progression.gd`, `level.gd`, tous les tests, docs de règles/journal/learning/workflow. Claude peut lire les tests et fournir les nouveaux waypoints/coordonnées attendus ; Codex adaptera les parcours à la géométrie finale. Les collisions corporelles des élites ne sont pas dans cette autorisation de dessin : signaler une incohérence démontrée pour correction technique coordonnée, sans grossir silencieusement la hitbox.

## Contraintes de contenu et interfaces

- Prix des sorties18/25/32 conservés. Budgets existants24/32/40 coins conservés par défaut, répartis plus intelligemment ; N4 conserve au moins36 coins accessibles sans payer la porte optionnelle, coût4, sortie32. Si la taille retenue nécessite davantage de coins, proposer le budget avant de changer l’économie. Aucun passage payant conduisant à une tentative insoluble.
- Préserver contenu introduit par niveau et mécaniques déjà validées : coffre, potions, Shield N3/4, secret/rare chest/potion majeure/HP bonus, porte optionnelle4, bouton et passage obligatoire N4. Les coordonnées changent, les IDs durables `n4_secret_01` et `n4_hp_01` restent. Conserver noms et chemins des nœuds pour l’intégration, sauf nécessité explicitement remise à Codex.
- Répartir les pièces, coffres, consommables et pièges en fonction des routes et de leurs risques. Faire des récompenses une raison d’explorer, pas une rangée automatiquement aspirée. Préserver suffisamment de coins atteignables pour finir sans forcer tous les coffres, le secret ni un achat optionnel.
- Aggro terrestre480×96, conservation640×160, délai2s ; swarm480×240 et quatre slots par tentative. Les offsets et placements doivent rendre cette rencontre lisible. Ne pas rétablir les anciennes valeurs ni associer un respawn à la mort du Sorcier.
- Le tir est désormais Longbow0 portée192px/intervalle2s et Knives0 portée112px/intervalle1,3s. Équilibrer l’espace de combat en conséquence. Aucun projectile ennemi nouveau, aucun changement de cadence ou dommage dans cette passe.
- Shield bloque tous les dégâts pendant10s ; le vide reste mortel. Conserver la solidité des pièges et leurs avertissements.
- Pas de munitions, caisses destructibles, nouvelles capacités, nouveaux types d’ennemis, musiques ou systèmes de sauvegarde dans cette reprise. L’humain retient l’idée des munitions pour un contrat dédié ultérieur ; aucun paramètre ni code autorisé dans cette passe.
- Orthographe affichée : **Black Forest**. Le chemin technique `black_forrest.tscn` et les noms d’assets historiques restent des identifiants compatibles, pas du texte à afficher.

## Bloated Slime et Chud Blob

Refaire les silhouettes, détails et animations nécessaires pour que l’élite soit immédiatement identifiable et **visiblement plus grande que le personnage joueur** à l’échelle native. Les ~34×30/34–36×29 pixels actuels n’assurent pas une hauteur supérieure au chevalier ~24×32. Mesurer la silhouette opaque et les frames, pas la case d’atlas et ses marges transparentes.

Claude choisit les nouvelles dimensions et proportions cohérentes avec docs06, conserve pieds/pivots, distingue les deux archétypes et vérifie toutes les animations, contact et préparation d’attaque. Éviter un simple étirement flou ou l’agrandissement artificiel de marges transparentes. Fournir une planche comparative joueur/élites avant-après à facteur entier, puis captures natives en situation ; aucune apparence déclarée validée sans revue humaine. Les autres mobs sont acceptés à ce stade : pas de refonte globale.

## Livraison attendue et recette

1. Manifeste : plans cotés, nombre de sections/branches, inventaire réel des acteurs/récompenses, budgets par route, nouveaux waypoints/noms, fichiers modifiés et provenance, dimensions opaques/pivots des élites.
2. Scènes éditables et générateur cohérent ; import Godot4.7.2 sans erreur. Exécuter tout moteur sous `work/.godot.lock` et profil de test isolé ; ne pas utiliser la sauvegarde humaine.
3. Captures natives640×360 : routes distinctes, verticalité, chaque récompense/secret/mécanisme, aggro/skulls, danger et élites à côté du joueur. Préserver la lisibilité des items, du terrain praticable et des télégraphies.
4. Remettre explicitement les fichiers à Codex après arrêt des éditions. Codex vérifie parcours réel clavier N1–4 et variantes, accessibilité/budgets, achats/refus, mort/restart/reprise, collisions et élites, puis régressions pertinentes. Les captures/téléportations de fixture ne prouvent pas le parcours naturel.
5. Nouveau playtest humain : variété/densité/ennui N2–4, absence de raccourci rectiligne dominant, confort de saut et difficulté graduelle, opportunités de tir, taille/design des élites et lisibilité. Le temps de parcours doit être mesuré, pas inventé. Pas de DONE ni de RUN-021 avant clôture020 selon le workflow.

Aucun push, PR, merge ni changement des sources externes autorisé par ce contrat. La remise technique Codex ne vaut pas validation du résultat Claude. Consulter la dernière entrée RUN-020 de `runs-journal.md` pour le checkpoint et les preuves de recette ; aucune autre édition de la logique technique ne lui est déléguée.
