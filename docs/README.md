# Milady's Knight — Documentation Index

## Purpose

Documentation découpée par responsabilité afin de servir de base de lecture et de planification à un agent de développement.
Les spécifications décrivent les contrats produit ; l’état réellement implémenté et ses preuves sont dans [brief.md](../brief.md) et [runs-journal.md](../runs-journal.md). La branche campagne N1–N4 est en audit global après validation humaine des dernières passes le 9 octobre 2026.

## Documents

1. [[00_PROJECT_VISION_SCOPE]] — vision du jeu, core features, game loop, scope et influences.
2. [[01_PLAYER_SYSTEMS]] — mouvements, combat joueur, dégâts/vie/mort, transitions et pause.
3. [[02_ENEMIES_AI]] — combat IA, PNJ, bestiaire, profils, comportements et Boss Final.
4. [[03_LEVEL_DESIGN_DIFFICULTY]] — niveaux, pièges, passages secrets, chemins secondaires, verticalité, difficulté et persistance.
5. [[04_PROGRESSION_ECONOMY_ITEMS]] — gold coins, shards, coffres, drops, armes, améliorations et consommables.
6. [[05_UI_HUD_MENU]] — HUD, menus, fenêtres, feedback, navigation et règles UI.
7. [[06_ART_BIBLE]] — direction artistique, pixel art, échelles, palette, contraste et variantes visuelles.
8. [[07_AUDIO_DESIGN_PIPELINE]] — direction sonore, règles techniques, formats et pipeline audio.
9. [[08_AUDIO_REQUIREMENTS]] — inventaire des SFX, ambiances et musiques nécessaires à l'implémentation.
10. [[09_LORE_NARRATION]] — lore, personnages, narration et dialogues.
11. [[10_CONTROLS_KEYBINDS]] — source dédiée des contrôles et key binds.
12. `11_GAME_ASSETS_LIBRARY.md` — procédure de sélection/intégration et catalogue graphique local, non suivi par Git.
13. `12_SFX_LIBRARY.md` — catalogue audio local, non suivi par Git.
14. [[13_ASSET_REQUIREMENTS]] — inventaire des assets visuels et graphiques, VFX, animations nécessaires à l'implémentation.

## Ordre de lecture recommandé pour un agent

[[00_PROJECT_VISION_SCOPE]] → systèmes concernés par la tâche → [[10_CONTROLS_KEYBINDS]] si interaction joueur → [[06_ART_BIBLE]] pour toute tâche visuelle → [[13_ASSET_REQUIREMENTS]] ; consulter `11_GAME_ASSETS_LIBRARY.md` si le catalogue local est présent et si la tâche intègre des ressources tierces → [[07_AUDIO_DESIGN_PIPELINE]] et [[08_AUDIO_REQUIREMENTS]] pour l'audio ; consulter `12_SFX_LIBRARY.md` si le catalogue audio local est présent.

Les catalogues 11 et 12 restent sur la machine où ils existent déjà. Un nouveau clone ne les contient pas ; les spécifications suivies par Git sont dans les autres documents de ce dossier.

L'essai visuel de RUN-003 et ses captures comparatives sont dans [RUN-003_SCALE_COMPARISON.md](RUN-003_SCALE_COMPARISON.md).

## Campagne N1–N4 et revue RUN-020/021

- [RUN-020 — review du playtest et proposition munitions](RUN-020_PLAYTEST_REVIEW.md) et [contrat de reprise Claude](RUN-020_CLAUDE_HANDOFF_02.md) : décisions et reprise historiques.
- [RUN-021 — notes de revue](RUN-021_REVIEW_NOTES.md) et [guide de playtest](RUN-021_PLAYTEST.md) : retours et critères de validation.
- [Contrat des munitions et piques](RUN-021_AMMO_SPIKES_PROPOSAL.md), [contrat Secret Wall](RUN-021_SECRET_WALL_CONTRACT.md) et [contrat des indices](RUN-021_SECRET_WALL_HINTS_CONTRACT.md) : règles validées pour les compléments concernés.
- [Manifeste N2](RUN-021_N2_VISUAL_MANIFEST.md), [manifeste N3](RUN-021_N3_VISUAL_MANIFEST.md), [manifeste N4](RUN-021_N4_VISUAL_MANIFEST.md) et [manifeste des assets](RUN-021_ASSET_MANIFEST.md) : livraisons visuelles et provenance.

Ces documents conservent les contrats, comptes rendus et preuves historiques. Les statuts actuels et les résultats consolidés de l’audit ne sont pas déduits de ces anciens checkpoints ; consulter le journal et le workflow.
