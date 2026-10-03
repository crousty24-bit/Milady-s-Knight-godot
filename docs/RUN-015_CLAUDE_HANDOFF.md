# RUN-015 — Contribution artistique Claude

La run est autorisée sur `feature/v0.2.0-reprise-equipment`. Codex réalise l'ingénierie. Le contrat intégral D03–D05 est validé ; voir `RUN-015_CONTRACT_REVIEW.md`. RUN-016 attend la revue et validation humaine de RUN-015.

## Travail attendu pour RUN-015

Donner aux menus une présentation cohérente avec le HUD et les assets acceptés 0.1.0, à 640×360 : menu principal New Game / Continue / Controls / Quit ; confirmation de remplacement ; migration v1 ; erreurs de sauvegarde ; pause Resume / Restart / Quit to menu ; fenêtre contextuelle. Focus clavier lisible, option Continue indisponible distincte, textes anglais lisibles sans découpage. Conserver tous les libellés et transitions fonctionnelles. Inclure les éléments de menu requis par docs/05 (logo centré et fond/artwork) ainsi que les feedbacks audio UI P0 de docs/08 : navigation, confirmation, annulation et erreur. Sélection/production sonore et validation d’écoute reviennent à Claude avec le même pipeline de provenance. Les contrôles actuels du menu servent de base technique ; leur présentation n'est pas une validation artistique.

Propriété à réserver exclusivement à Claude après handoff : présentation dans `scripts/keyboard_menu.gd` (`_ready`, `_redraw_rows`), éventuels nouveaux assets de menu/audio UI et leur provenance. Codex cesse les modifications de ce script pendant cette passe. Ne pas modifier sa navigation `_process`, son garde de frame d'ouverture, les signaux, ni les scripts game/level/progression, ni le terrain humain. Si une modification fonctionnelle devient nécessaire, transmettre le problème à Codex avant édition. Les noms et l'API `show_menu`, `close`, `opened`, `selection`, `unavailable` restent stables.

Lire les sources pertinentes d'AGENTS, docs/05, docs/06, docs/08 et docs/13. Pour des assets externes, suivre `.local/asset-paths.md` et le pipeline source → adaptation → dérivé intégré ; sources et licences conservées. Réutiliser les ressources déjà acceptées lorsque pertinent. Aucun asset Longbow/coffre/potion à intégrer dans RUN-015.

## Vérification après contribution

Sérialiser Godot avec `flock work/.godot.lock`. Exécuter les tests de menus avec rendu, puis inspecter les captures 640×360 et la navigation clavier ; retester la suite commune si comportement ou références modifiés. Les captures sont produites par `tests/menus.gd` dans `work/run015/`. Le runner `tools/test.sh` isole user:// ; le pilote menus utilise aussi son propre fichier et ne touche pas `progress.json`.

Validation artistique humaine requise avant clôture. Pas de push, PR, merge ou démarrage de RUN-016 pendant cette contribution. Consigner fichiers, sources et preuves au journal ; revenir à Codex pour intégration/revue.

## Assets prévus en RUN-016

Préparer alors un second périmètre distinct : Longbow et flèche, tir/impact, shard et feedback de gain, coffre tuto fermé/ouvert et récompense fixe, potion mineure et soin, deux slots verticaux et focus d'arme active. Les scènes/scripts de gameplay restent à Codex ; réserver les fichiers graphiques exacts avant travail parallèle.
