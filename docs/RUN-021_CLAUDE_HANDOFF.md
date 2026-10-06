# RUN-021 — Contrat Claude : cohérence visuelle N1–4

**6 octobre 2026 — Lancement autorisé par l’humain, après validation de RUN-020 en l’état.** Branche `feature/run-020-021-campaign`. Main agent : Claude Code Opus 5.5 ; sous-agents Sonnet 5.5 sur tâches indépendantes selon CLAUDE.md. Codex prépare le passage, possède les corrections de gameplay et la recette d’intégration. Ce contrat autorise la première passe visuelle ; les résultats et leur validation restent à produire.

## Objectif et ordre des passes

Harmoniser N1–4 : palettes, fonds, décor, sprites et animations, VFX, objets, interfaces, silhouettes et télégraphies. Partir du dépôt réel, pas d’une reconstruction de RUN-020. Les niveaux actuels sont une étape : l’humain veut à terme des niveaux beaucoup plus grands, beaucoup plus de mobs, de chemins et d’items. Les dimensions et populations de RUN-020 ne constituent pas le scope final ; aucune nouvelle taille cible chiffrée n’est décidée ici.

1. Passe visuelle Claude selon ce contrat.
2. Complément Claude [animation Archer et audio](RUN-021_CLAUDE_HANDOFF_02.md), avec remise des fichiers partagés avant toute autre édition.
3. Passe technique Codex : portée/aggro Archer et Sorcerer, nouvelle baisse légère du tir joueur, vitesse d’aggro Bloated/Chud ; paramètres justifiés à partir des valeurs réellement exécutées et du playtest. Pas de tuning implicite pendant le dessin.
4. Recette complète après intégration, corrections finales, validation artistique/audio et playtest humains, puis Jev/inspection avant DONE et validation éventuelle 0.3.0.

Les [remarques humaines](RUN-021_REVIEW_NOTES.md) font partie du périmètre de RUN-021. Elles ne sont pas des corrections déjà réalisées.

## Baseline humaine à préserver

L’humain édite manuellement les TileMap pour façonner précisément son level design et demandera des reviews/audits. Les scènes présentes au début de chaque passe font autorité. Ne jamais effacer ou écraser ses changements hors run, y compris indirectement par régénération, remplacement de scène, réenregistrement global ou retour à un ancien commit. Une review/audit ne donne pas l’autorisation de modifier le terrain. Une correction de terrain humain attend une demande explicite et un patch local identifié.

Six fichiers déjà modifiés au lancement sont gelés pour cette contribution : `assets/kingdom_tileset.tres`, `assets/run018/knight/knight_body_frames.tres`, `knight_mid_frames.tres`, `knight_over_frames.tres`, `assets/sprites/ashen_knight_frames.tres` et `scenes/blight_town.tscn`. Leur état est enregistré dans `work/run021/human-baseline-sha256.json` et `human-baseline.patch`. Ne pas les restaurer, normaliser, inclure dans un commit de contribution ou modifier leurs ressources de substitution à leur insu. Les changements de terrain N2 ne sont pas présumés annulables sous prétexte d’une différence avec le générateur.

Toute nouvelle modification humaine pendant la run devient la nouvelle baseline ; coordonner le créneau d’édition et actualiser l’inventaire avant de travailler. Ne rejouer aucun générateur de scènes de production, notamment `tools/build_run020.py`. Les tests doivent s’adapter au terrain réellement conservé ; pas de retour au terrain des tests.

## Ownership et interfaces

Lire AGENTS.md, CLAUDE.md, la fiche RUN-021, `.claude/rules/visual-assets.md`, docs/06 et docs/13 ; docs/08 pour les événements audio. Consulter `.local/asset-paths.md` et les exigences ciblées avant toute recherche. Les bibliothèques externes sont en lecture seule. Préserver originaux, adaptations et crédits.

Claude peut produire dans de nouveaux répertoires dédiés `assets/run021/`, `assets/source/run021/` et `tools/art/` ; éditer `scripts/campaign_backdrop.gd`, `scripts/campaign_decor.gd`, `scripts/campaign_terrain_skin.gd` uniquement pour la présentation, ainsi que les ressources visuelles non gelées et les crédits concernés. Pour N1, `scripts/backdrop.gd`, `scripts/kingdom.gd` et `scripts/terrain_skin.gd` sont explicitement attribués à Claude pour le dessin uniquement ; aucune cellule, collision ni position d’acteur modifiée. Ne pas modifier `world_tileset.png` ou les PNG du chevalier utilisés par les ressources gelées : cela contournerait leur protection. Ne pas couvrir visuellement une ouverture praticable ni déplacer un danger pour faciliter le décor.

Pour une intégration dans une scène : déclarer d’abord dans le manifeste les nodes/propriétés exacts, travailler par patch limité aux références et nodes de présentation, et vérifier que les données TileMap, collisions, acteurs, coordonnées, budgets et IDs sont conservés. `scenes/blight_town.tscn` reste gelée : livrer séparément les ressources ou le patch de raccord proposé, sans l’appliquer. N1, N3 et N4 ne peuvent recevoir de remplacement global ni de modification de terrain. Ne pas réenregistrer une scène entière dans l’éditeur pour un simple changement de référence.

`scripts/run019_enemy.gd` contient à la fois logique et présentation : dans un créneau exclusivement Claude, seules ses tables et méthodes de présentation peuvent changer. Livrer cette contribution et arrêter les éditions avant la passe Codex sur ce même fichier. Pour Archer, le complément précise la reproduction requise. Les scripts partagés HUD/objets suivent le même principe : annoncer la portion de présentation, garder les règles intactes.

Codex réserve mouvement, combat, aggro, projectiles, catalogue d’armes, progression/persistance, économie, collisions et tests. Préserver noms de nodes, signaux, sorties12/18/25/32, IDs durables, timers et valeurs gameplay de la baseline. Les corps d’élites44×40/36×40 et le contact Bloated30px ne sont pas remis en cause par un changement d’asset seul. Pas de munitions ni de nouveau système.

## Livrables et vérification

- `docs/RUN-021_ASSET_MANIFEST.md` : état réel, problèmes traités/restants, ownership précis, sources/licences/empreintes, pipeline, fichiers, pivots et dimensions opaques, changements de références proposés ou appliqués ; aucune validation artistique inventée.
- Comparaisons avant/après et captures natives640×360 de N1–4 : terrain praticable, acteur/joueur au contact, télégraphies, objets, HUD et modales. Préciser scène de production ou fixture ; des poses forcées ne prouvent pas un parcours naturel.
- Import et vérifications pertinentes sous Godot4.7.2, `flock work/.godot.lock`, profil isolé sans sauvegarde humaine ; fournir commandes/logs réels. Vérifier les animations, pieds/pivots, bords, visibilité et performance du décor.
- Remise explicite à Codex après arrêt des éditions : inventaire de fichiers, références et nodes affectés, risques et preuves. Codex adaptera les tests/pilotes à l’état réellement livré, exécutera les parcours et régressions après les passes finales.

La validation de RUN-020 ne valide pas les nouveaux visuels de RUN-021. Ni une capture, ni une préanalyse ne clôt cette run ; aucun push/PR/merge autorisé par ce lancement.

## Préanalyse exécutée et décisions de préparation

Claude Opus5.5 a exécuté la préanalyse initiale en lecture seule (`work/run021/claude/preflight.json`, succès), sans asset, moteur ni modification de production. Les points pratiques soulevés sont résolus dans ce contrat : utiliser le répertoire existant `assets/source/` ignoré par Godot ; attribuer les trois scripts de dessin N1 ci-dessus ; maintenir le gel des textures dépendant des ressources humaines. La piste N4 a été vérifiée par Codex dans la bibliothèque locale, même si la session restreinte de préanalyse ne pouvait pas la lire.

La restriction aux outils de lecture concernait uniquement cette préanalyse. La future session de production peut utiliser shell, conversion, import/capture Godot4.7.2 sous verrou et profil isolé pour les livrables attribués, avec accès à la bibliothèque externe **en lecture seule**. Cela n’autorise ni réécriture de terrain, ni modification des fichiers gelés, ni changement de gameplay. Aucun connecteur externe n’est nécessaire pour ce travail local.
