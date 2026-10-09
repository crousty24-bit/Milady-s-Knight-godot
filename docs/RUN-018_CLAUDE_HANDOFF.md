# RUN-018 — Contrat de contribution Claude

**5 octobre 2026 — Contrat produit validé ; contribution Claude préparée, pas transmise à un chat.**
Branche commune : `feature/run-018-standard-equipment`. Codex orchestre RUN-018 ; Claude pilote sa contribution artistique. Les décisions D02/D04 de [RUN-018_CONTRACT_REVIEW.md](RUN-018_CONTRACT_REVIEW.md) sont validées par l’humain. La base technique ci-dessous est implémentée ; résultats de recette et autorisation du handoff partagé consignés au checkpoint de fin.

## Livrable visuel et sonore

Huit armes standard : Sword, Longsword, Brutal Axe, Dark Scythe, Warhammer, Halberds, Longbow, Throwing Knives. Compléter les silhouettes équipées et attaques du chevalier, projectile Knife départ/impact, icônes des huit armes, niveaux 0–3 (gris/vert/bleu/rouge), common/rare chest fermé/ouvert, proposition item et upgrade +1 dans deux cases horizontales, focus clavier, potion majeure et feedback de soin. Garder Sword0/Longbow0 et la direction artistique validée.

Lire docs/06, docs/08, docs/13 et `.claude/rules/visual-assets.md`, puis `.local/asset-paths.md` et les catalogues locaux pertinents s’ils sont présents. Les bibliothèques externes sont en lecture seule. Garder sources, adaptations et dérivés séparés avec licences et crédits. Le choix des sources n’est pas prescrit par ce contrat.

Sons P0 de common/rare chest, récompense/upgrade et interactions clavier ; réutilisation des cues existants possible si cohérente, choix et limites documentés. Sons spécifiques de nouvelles armes/potion majeure P1 selon docs/08 : les inventorier et livrer ou signaler ce qui reste pour RUN-027. Pas de refonte du mix/menu/Spirit ni de Legendary/Fire Gauntlet, N2–4, buff ou ennemi dans cette passe. RUN-021 demeure la passe globale N1–4.

## Propriété pendant la production des assets

- Claude peut créer ses générateurs dans `tools/art/run018/`, textures dans `assets/run018/`, sons normalisés dans `assets/sounds/run018/` et sources dans `assets/source/run018/`. Respecter la convention de source du dépôt si une licence exige autre chose, et déclarer les chemins exacts au retour. Fournir un manifeste de noms, tailles, frames, fps, boucles, ancrages et provenance dans `docs/RUN-018_ASSET_MANIFEST.md`.
- Codex possède tous les scripts gameplay/persistance, tests et scènes fonctionnelles : `scripts/player.gd`, `scripts/arrow.gd`, `scripts/progression.gd`, `scripts/level.gd`, `scripts/tutorial_chest.gd`, `scripts/minor_potion.gd` et nouveaux scripts/scènes de RUN-018. Claude ne les édite pas pendant cette phase.
- Les générateurs existants `tools/art/knight.py`, `tools/art/items.py`, `tools/art/ui.py`, les atlas actuellement utilisés, `scripts/hud.gd`, `scenes/hud.tscn`, `scenes/player.tscn` restent réservés tant qu’aucun handoff d’intégration n’est consigné. Ne pas régénérer globalement ces assets.
- `runs-workflow.md`, `runs-journal.md`, `learning.md` restent à Codex pendant le parallèle ; Claude remet ses preuves dans son manifeste. Les crédits existants seront intégrés au retour afin d’éviter des éditions simultanées.

Une seconde phase d’intégration visuelle exige un handoff explicite de fichiers : Codex publie les API/nœuds/signaux réellement implémentés, attribue les fichiers partagés, puis cesse de les éditer pendant la passe Claude. Une scène/script partagé n’a jamais deux propriétaires actifs. Claude peut effectuer l’intégration technique minimale du rendu sans modifier profils, collisions ou valeurs produit.

## Contraintes de rendu à respecter

640×360, nearest, grille terrain 16 px ; conserver gabarit/ancrage du chevalier 64×64 validé. Montrer l’arme active sans déplacer le corps physique. Une attaque reste un hit par cible et la longueur de la lame suit RANGE×24 px ; ne pas prétendre livrer chaque portée via une image Sword inchangée. Prévoir ancrages et transformations compatibles avec les huit tables et niveaux, sous réserve du contrat validé.

Deux slots HUD verticaux (mêlée/tir) ; choix de coffre horizontaux (item/upgrade), navigation gauche/droite, E confirme, Escape refuse. Textes anglais, nom et niveau exacts ; pas d’information transmise uniquement par couleur. Aux niveaux 4/5 futurs, garder un chiffre explicite ; leur style supplémentaire ne doit pas être inventé dans cette passe sans décision.

Le soin instantané de kill est un feedback, pas un pickup supplémentaire. La potion majeure de terrain est un pickup distinct. Les collisions et API de collecte appartiennent à Codex. Ne pas modifier le terrain humain ni les placements de N1.

## Retour et validation

Remettre les fichiers exacts, sources/licences, contrats de frames/ancrages, captures Godot 4.7.2 et résultats effectivement exécutés, limites d’animation et d’écoute. Utiliser `flock work/.godot.lock` pour les moteurs et des profils de test isolés ; aucune lecture/écriture de la sauvegarde joueur.

Après intégration : cadence/range/collision vérifiées par Codex, puis pilotes de rendu de chaque arme gauche/droite/air, Knife départ/impact, common/rare choix/refus/upgrade et soin ; inspection à 640×360 et validation humaine artistique/sonore. Une preview d’asset seul ne valide pas son intégration en jeu. Pas de DONE, push, PR, fusion ou autre run par cette contribution. Retour explicite à Codex pour recette et revue Jev.


## Interfaces implémentées pour la passe d’intégration

- `WeaponCatalog.stats(id)` fournit `damage`, `interval`, `reach` en pixels, `slot`, `name`, `level` ; `label(id)` est le texte exact. IDs : Sword0–5, Longsword0–5, BrutalAxe0–5, DarkScythe0–5, Warhammer0–5, Halberds0–5, Longbow0–5, ThrowingKnives0–5. Aucun Legendary/Fire Gauntlet.
- `SlicePlayer.equipment` = dictionnaire `melee`/`ranged`, `active_slot` 0/1, `active_item()` donne l’ID actif ; `configure_loadout(slots)` applique une acquisition sans effacer les cooldowns. `has_longbow` est conservé comme alias de compatibilité pour « slot de tir non vide » ; ce booléen ne distingue pas Knives/Longbow. Employer l’ID pour les visuels.
- `equipment_changed(slot)` et `projectile_fired(projectile)` sont les hooks existants. `scripts/arrow.gd` gère les deux projectiles avec `damage`, `reach`, `direction`, `distance_travelled` et `impacted(at, enemy)`. La variante visuelle peut suivre l’ID du tireur à `projectile_fired`, mais doit capturer cet ID au départ : un projectile déjà lancé ne change pas de look avec l’équipement courant.
- `scenes/reward_chest.tscn` / `scripts/reward_chest.gd` : Area2D44×48 offset `(0,-16)`, groupe `reward_chests`, `kind` common/rare, `offer` item/upgrade, `paid`, `consumed`, `save_failed`. Le niveau cache le coffre après paiement ; pour un effet d’ouverture/dissolution indépendant, prendre un snapshot à ce moment. Aucun deuxième débit par la présentation.
- `scripts/level.gd` possède `world_level` (1 par défaut), `chest_economy`, `active_reward`, `reward_choices`, `open_reward_chest(chest)`, `_show_paid_reward(error, selected_index)`, `_choose_paid_reward(index)`. `modal == "reward"` suspend gameplay ; l’upgrade est absent quand non tiré, pas remplacé par une fausse option. Escape refuse sans remboursement. Retry disque conserve l’offre et le choix.
- `scripts/keyboard_menu.gd` possède `show_menu(title, detail, options, disabled=[], horizontal=false)` ; les récompenses payantes utilisent des choix horizontaux et gauche/droite. Les autres menus restent verticaux. `opened_frame` empêche qu’E à l’ouverture confirme déjà une récompense. Conserver ces comportements lors de l’ajout d’icônes.
- `hud.set_loadout(active, slots)` écrit les deux labels exacts ; les plaques/icônes héritées ne couvrent actuellement que Sword/Longbow et attendent remplacement. Les armes longues demandent vérification du texte à 640×360.
- `scripts/minor_potion.gd` expose `healing_amount` (0,5 par défaut), `used`, `collected(amount)` ; `scenes/major_potion.tscn` hérite de la scène mineure avec amount1, même rayon8. Son `Art` utilise `major_potion_preview.gd`, marqueur à remplacer. Le gameplay ne dépend pas de ce script de preview.
- Les morts d’ennemis ordinaires sont raccordées au niveau ; metadata `healing_profile` ordinary/elite/skull, un seul tirage par mort. `level.kill_healed(amount)` est émis seulement après soin effectif, pour un VFX/cue instantané. Les profils élite/skull sont testés par fixture, pas de nouveaux mobs créés.

À la remise technique, Claude peut posséder exclusivement la présentation de `scripts/player.gd`, `scripts/arrow.gd`, `scripts/hud.gd`, `scripts/equipment_slots.gd`, `scripts/keyboard_menu.gd`, `scenes/player.tscn`, `scenes/hud.tscn`, et Art des scènes reward_chest/major_potion, plus ses assets/générateurs. **Avant d’éditer, vérifier que Codex a explicitement terminé le checkpoint et cessé d’éditer ces fichiers.** Les sections physiques/transactions de ces fichiers restent contractuellement inchangées ; si un correctif technique est découvert, retour à Codex et nouvelle attribution avant correction. `level.gd`, catalogue/économie/persistance, tests et scripts de collecte restent à Codex. Un raccord visuel au signal kill_healed dans `level.gd` doit faire l’objet d’un patch remis à Codex plutôt que d’une édition parallèle.

Pilotes techniques disponibles : `tests/standard_weapons.gd` (48 profils, physique/cadences), `tests/chest_economy.gd` (tables/pools/prix), `tests/reward_transactions.gd` (contacts/modal/save/soins), `tests/equipment_cold_session.gd` (trois processus successifs), fixture explicite `tests/fixtures/economy_level.tscn`. Ce n’est pas N2 de production. Avec rendu, reward_transactions produit `work/run018/paid-choice.png` et `major-heal.png` sur une sauvegarde de test dédiée. Ne pas lancer la fixture en partie normale pour vérifier les transactions de la sauvegarde réelle. Ajouter un pilote de rendu dédié pour les nouveaux assets au retour.


## Remise de propriété pour la contribution artistique

**Checkpoint technique Codex du 5 octobre 2026 terminé ; intégration visuelle désormais attribuée exclusivement à Claude sur les fichiers de présentation listés ci-dessus.** Codex cesse leurs éditions jusqu’au retour Claude. La recette complète technique et le pilote de rendu UI sont au journal ; aucun asset nouveau n’a été validé comme final. Les sections de gameplay restent à préserver ; demander une nouvelle attribution avant toute correction fonctionnelle. `shot_age` suit maintenant l’âge réel du tir et annule son release visuel lors d’un remplacement, sans effacer bow_cooldown.

La run attend cette contribution puis l’art/écoute et essai humain des nouvelles armes/coffres, suivis de la recette après intégration et revue Jev. Elle n’est pas DONE et ce contrat ne prétend pas qu’un chat Claude a déjà démarré.
