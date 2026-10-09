# RUN-021 — Contrat Claude : props et munitions

**7 octobre 2026 — Autorisé par validation humaine du [contrat produit](RUN-021_AMMO_SPIKES_PROPOSAL.md), amendé pour transmettre les stocks courants au niveau suivant.** Branche actuelle `feature/run-020-021-campaign`. Nouvelle passe dans RUN-021, sans clôture ni promotion0.3.0 anticipée.

## Livrables visuels

- Une caisse et un tonneau destructibles, cohérents avec N1–4 ; états intact/détruit, animation brève de casse et résidu discret facultatif. Emprise visuelle cible32×32px maximum, pivot bas-centre ; aucune collision bloquant la marche. Signaler une taille différente avant le raccord technique.
- Pickup flèches et pickup couteaux distincts, icônes et marquage lisible sur chaque prop pour sa famille. Cellule cible16×16px, pivot centre ; quantité indépendante du nombre d’objets dessinés, affichée par la logique Codex.
- Proposition de présentation du compteur actuel/plafond et feedback plein/vide/ramassage. Préserver les informations HP/pièces/arme dans le viewport640×360. Codex raccorde les données et le feedback logique.
- Pas de nouveau système audio demandé : proposer, si utile, un asset existant de casse/collecte avec provenance ; Codex raccorde. Aucun remplacement des SFX existants dans ce lot.

Claude consulte `.local/asset-paths.md` si présente et les exigences artistiques pertinentes. Bibliothèques externes en lecture seule, sources/licences conservées, pipeline source → adaptation → asset normalisé → intégration. Ownership exclusif de `assets/run021/ammo/**`, `assets/source/run021/ammo/**`, `tools/art/run021/ammo/**`, de son manifeste `docs/RUN-021_AMMO_ASSET_MANIFEST.md` et des ajouts de crédits correspondants. Ne pas supposer qu’une licence/source existe sans la vérifier.

## Interface et séquence de remise

Codex crée les scènes et scripts techniques caisse/tonneau/pickup, leurs collisions de réception des coups et signaux de destruction/collecte. Avant adaptation finale des sprites, il remet à Claude les noms de nodes, chemins et signaux réels. Claude peut intégrer uniquement la présentation de ces nouveaux objets dans un créneau exclusif ; ni consommation, probabilités, dégâts, reset ni persistance ne relèvent de ce raccord artistique.

Après remise par Codex, Claude ajoute les instances dans `scenes/eidolon_vale.tscn`, `scenes/blight_town.tscn`, `scenes/black_forrest.tscn`, `scenes/forbidden_graveyard.tscn` : budgets/familles du contrat produit, placements accessibles à la mêlée, répartis sur les routes. Relever coordonnées, famille et type dans le manifeste. Préserver intégralement TileMap, objets existants et leurs propriétés ; ne pas rejouer de générateur. La baseline doit être relevée juste avant édition, car les scènes sont éditées par l’humain. Aucun ajout au vertical slice hors fixture Codex.

HUD partagé : Claude livre une proposition et les icônes ; `scripts/hud.gd` reste Codex. Une édition de `scenes/hud.tscn` ne commence qu’après remise exclusive explicite par Codex. Pas d’édition de player/progression/catalogue/tests/workflow par Claude. À la livraison, arrêter les éditions partagées avant recette Codex.

## Piques : intervention conditionnelle seulement

Codex possède `scripts/retractable_spikes.gd` et `scenes/retractable_spikes.tscn`. Le socle solide est la cause probable du blocage ; la correction de collision ne nécessite pas une nouvelle direction artistique.

Si le rendu après correction montre une marche visuelle trompeuse en RETRACTED/WARNING, Claude reçoit exclusivement le dérivé `assets/run019/world/trap_spikes_retract.png` et son outil d’adaptation existant après identification de la source. Conserver cellules32×16, ordre/nombre de frames, durées et pivot contractuels ; enfouir visuellement le socle au plan de pose sans effacer l’avertissement ni la lisibilité du danger. Ne modifier ni source externe ni timings/collisions. Livrer comparaison avant/après, poses et rendu au sol/au mur. Sinon, aucun asset de piques modifié.

## Preuves et limites

Manifeste : sources/crédits/hashes, dimensions/pivots/animations, fichiers effectivement touchés, placements et famille, captures natives des deux props, casse, pickups et HUD ; distinguer vérification d’assets, rendu et playtest. Codex possède recette comportementale/régression finale. La validation artistique et l’équilibrage restent humains. Aucune commande Git de push/PR/merge ni modification hors ownership.
