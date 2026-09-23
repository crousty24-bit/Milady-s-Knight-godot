# Milady's Knight — Documentation Index

## Purpose

Documentation découpée par responsabilité afin de servir de base de lecture et de planification à un agent de développement.

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
