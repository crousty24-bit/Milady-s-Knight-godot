# RUN-016 — Art, animations et feedbacks pour Claude

RUN-015 est DONE, passe menu/audio validée humainement ; la musique choisie du menu est intégrée. RUN-016 est autorisée sur la même branche `feature/v0.2.0-reprise-equipment`. La partie technique est implémentée ; les nouveaux objets ont seulement des repères de test, la flèche n'a pas encore de rendu. L'amélioration du détail du logo est consignée pour RUN-027 et n'appartient pas à ce lot.

## Résultat attendu

Selon docs/06, docs/08 et docs/13 : Longbow 0 équipé lisible sur le chevalier, départ de tir ; flèche orientée gauche/droite et impact terrain/ennemi ; icône shard et feedback de gain ; coffre tuto fermé/ouvert, choix de récompense fixe Longbow 0 ; potion mineure, collecte/soin ; deux slots verticaux Sword/Longbow/Empty avec focus actif, icônes et texte exact sans superposition à 640×360. Intégrer les sons/VFX P0 correspondant à ces interactions. Conserver les médias et la provenance existants ; pipeline source/adaptation/dérivé et crédits requis. Ne pas créer de Spirit, de N2 ou réécrire le terrain.

## Propriété de fichiers

- Claude : nouveaux générateurs d'art, textures/animations et sons, provenance ; présentation dans `scenes/tutorial_chest.tscn`, `scenes/minor_potion.tscn`, `scenes/hud.tscn`, visuels du chevalier (`tools/art/knight.py`, ressources/animations nécessaires et partie visuelle de player.gd si besoin). Conserver tous les nœuds/API employés par les tests.
- Les scripts `level.gd`, `progression.gd`, `tutorial_chest.gd`, `minor_potion.gd` et les tests restent à Codex. Aucun changement de collision, placement ou règle pendant la passe.
- `arrow.gd` est technique ; une insertion de Sprite2D/animation et écoute du signal `impacted(at, enemy)` est permise comme intégration visuelle minimale, sans modifier collision, vitesse, cadence ou portée. Si une autre modification fonctionnelle est requise, handoff à Codex avant édition.
- Codex cesse toute édition des fichiers de présentation partagés pendant la passe. Pas de deux agents simultanés sur player.gd ou hud.tscn.

## Contrats stables

Longbow : 1 DMG, 1,5 s, 20 blocs = 320 px depuis la bouche `(4*facing, -10)` ; vitesse technique 320 px/s, raycast balayé terrain1/enemies4, disparition au premier impact ou à portée. Flèche en espace monde, enfant du joueur pour destruction à la mort/reset ; pausable. Sword conserve 0,5 DMG, 1 s, 24 px et ses animations de chaîne. L'interdiction d'attaque en wall slide de docs/01 concerne la mêlée ; le tir reste disponible.

`player.has_longbow`, `active_slot` (0 Sword/1 Bow), `configure_equipment(bool)`, `equipment_changed(slot)`, `projectile_fired(arrow)` ; cooldowns séparés. A ne sélectionne pas un slot vide. Le nom durable est `Longbow0`, Sword reste `Sword0`. Le spawn reprend avec Sword sélectionnée et les deux armes acquises conservées.

Coffre : libre/gratuit, récompense fixe, pas d'upgrade ; ouvert/consommé pour la tentative dès que la modale s'ouvre, Refuse/Escape ne donnent rien, reset le restaure tant que Longbow0 n'est pas acquis. Acquisition sauvegardée avant attribution ; échec disque remet le coffre disponible avec invite retry. Il est supprimé visuellement après acquisition et à la reprise suivante. `tutorial_chest.consumed`, `save_failed`, `player_near()` restent stables. Placeholder `CHEST` à remplacer par l'art ; Area2D44×48 offset `(0,-16)` inchangée.

Potion : contact réel, soigne au maximum 0,5 HP ; vie pleine = reste disponible, peut soigner ensuite sans devoir sortir de sa zone ; consommation unique, réapparaît au reset. `minor_potion.used` et signal `collected(amount)` ; CircleShape2D8 inchangée, placeholder `POTION` à remplacer.

HUD : chemins `Equipment/Melee` et `Equipment/Ranged` restent des Labels actualisés par `hud.set_equipment`. `Health`, `Gold`, `Bonus`, `BonusPending` et l'API de prompt demeurent. Ajouter icônes/plaques autour des textes ; ne pas remplacer les valeurs par une interprétation approximative.

Positions temporaires : coffre `(120,144)`, potion `(176,134)` dans le niveau ; adaptation finale N1 appartient à RUN-017. Ne pas déplacer silencieusement les objets ou le terrain pendant cette contribution.

## Vérification et retour

Godot4.7.2 via outils existants, sérialiser avec `flock work/.godot.lock`. `tests/longbow.gd` pour tir/occlusion/impact/portée/pause/changement/cooldowns et glissade ; `tests/rewards.gd` pour interactions/soin/save/reset. Le second pilote non headless produit `work/run016/{reward,equipped,potion}.png`. Ajouter les captures/tests de rendu pertinents pour flèche, arme et sons réellement intégrés. `tools/test.sh` exécute les 20 suites et isole user://. Les captures des repères de test ne sont pas des assets acceptés.

Consigner sources, fichiers, preuves et limites au journal. Validation humaine de l'art et de l'écoute puis revue Jev restent requises avant DONE ; pas de push/PR/merge ni RUN-017. Retour à Codex pour intégration et revue finale.
