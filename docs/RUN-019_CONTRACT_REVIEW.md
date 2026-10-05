# RUN-019 — Contrat proposé avant implémentation

**5 octobre 2026 — Contrat validé intégralement par l’humain (« Je valide le contrat décidé pour la run ») ; checkpoint technique vérifié, contribution art/SFX en attente.**
Lancement demandé par l'humain. Baseline propre `develop` `288b518` (PR #21 intégrant RUN-018 DONE), branche `feature/run-019-threats-exploration` créée depuis develop.

## Périmètre et état vérifié

RUN-019 livre les familles fonctionnelles et leurs fixtures : Red/Bloated Slime, Warrior, Archer, Sorcerer, Possessed Skulls et Chud ; piques rétractables, trappes, tourelles, plantes ; Shield, secrets permanents, mécanismes, portes secondaires et HP bonus. RUN-020 construit et peuple N2–4 ; RUN-021 harmonise leur présentation. N1 et ses placements humains sont préservés.

Dans le code actuel, `slime.gd` n'a que Green/Purple, `spikes.gd` des piques fixes. `player.gd` traite les dégâts par source et stocke la santé en dixièmes. `progression.gd` v2 possède déjà des flags permanents sauvegardés par transaction, mais aucun calcul de HP bonus. `level.gd` enregistre les ennemis et récompense une seule émission de mort par instance ; ce contrôle ne borne pas les récompenses d'instances recréées. Le profil metadata `healing_profile` ordinary/elite/skull est déjà traité, Skulls exclus des soins selon RUN-018. Les attaques actuelles ciblent les ennemis et le terrain ; elles ne révèlent pas encore les secrets et n'activent pas les plaques.

Sources : [ennemis](02_ENEMIES_AI.md), [joueur](01_PLAYER_SYSTEMS.md), [niveaux](03_LEVEL_DESIGN_DIFFICULTY.md), [économie](04_PROGRESSION_ECONOMY_ITEMS.md), [contrat RUN-018 validé](RUN-018_CONTRACT_REVIEW.md). Aucun asset externe inspecté ou modifié pour cette préparation.

## Règles déjà spécifiées à conserver

| Profil N2–4 | HP | Dégâts | Comportement | Shards par kill |
| --- | --- | --- | --- | --- |
| Red Slime | 2 | 1,5 contact | Patrouille sans aggro | 1 |
| Bloated Slime | 5 | 1,5 contact | Patrouille puis poursuite | 5 |
| Skeleton Warrior | 2 | 0,5 mêlée | Patrouille puis poursuite | 1 |
| Skeleton Archer | 2 | 0,5 projectile | Patrouille puis tir stationnaire | 1 |
| Blight Sorcerer | 2 | 0,5 mêlée / 2 sol | Poursuite ; explosion annoncée environ 1 s | 1 |
| Possessed Skull | 1 | 0,5 contact | Swarm de zone, disparition à la sortie | Décision ci-dessous |
| Chud Blob | 10 | 2 mêlée | Patrouille lente puis poursuite | 5 |

Les ennemis ne gagnent ni invincibilité, ni hit-stun, ni interruption d'attaque lorsqu'ils sont blessés. Le recul demeure, excepté Skulls. Les profils de soins ordinary/elite/skull suivent RUN-018 ; un seul tirage par mort éligible. Les morts et projectiles ne récompensent pas deux fois une cible.

Piques rétractables : 0,5 DMG ; plantes solides : 1 DMG ; tourelles : 1 DMG par projectile. Trappe ouverte jusqu'au reset, sans dégâts intrinsèques. Shield : 10 s contre les attaques ennemies, aucun effet contre pièges/vide. Secret révélé par attaque, fondu et son, permanent. Bonus HP : +1 MAX HP permanent par objet unique ; ne réapparaît pas après mort/reprise. Portes secondaires/mécanismes/coins restent des états de tentative.

## D01 — Bonus HP proposé

- Collecter +1 MAX HP augmente aussi CURRENT HP de 1, sans soigner davantage : 1/3 devient 2/4, 3/3 devient 4/4. Le soin complet reste celui du reset/changement de niveau.
- Écriture durable du flag unique avant disparition du pickup et augmentation de santé. Échec disque : aucune attribution, pickup encore disponible et retry possible. IDs stables par niveau/objet ; aucun compteur déduit des instances vivantes.
- Au spawn, MAX HP = base existante + nombre de bonus acquis. Mort/restart/reprise conserve les bonus et soigne au nouveau maximum. New Game confirmé supprime ces acquisitions comme les autres flags.
- Aucun palier N5/N8 ni offrande implémenté ici ; leur contrat reste RUN-023.

## D06 — Aggro, mouvement et attaques proposés

- Acquisition de l'aggro : joueur vivant dans un rectangle attaché au mob **et** ligne de vue libre contre terrain. Conservation : même rectangle et même contrôle de visibilité ; perte dès sortie/occlusion. Les Slimes Green/Purple/Red restent sans aggro ; Bloated est l'exception élite explicitement spécifiée.
- Ennemis terrestres : pas de saut, pas de chute volontaire, pas de pathfinding. Arrêt devant bord/obstacle pendant poursuite ; retour vers le segment de patrouille initial dès perte d'aggro. Le terrain doit permettre ce retour ; aucun téléport/reset de santé au retour. Archer reste immobile pendant son aggro.
- Chaque attaque possède une préparation visible et une phase de dégâts, sans impact à travers terrain. À la perte d'aggro, annuler la préparation non libérée. Une flèche déjà tirée ou une zone déjà annoncée termine son cycle ; mort de la source supprime ses attaques encore actives. Pause suspend tous les compteurs. Aucun dégât au joueur déjà mort.
- Explosion Sorcerer : zone figée au sol sous le joueur au lancement, avertissement 1 s, un seul impact de 2 DMG ; pas de suivi du joueur pendant l'avertissement. Utiliser le profil projectile ennemi (protection/interruption, sans recul/hit-stun), car c'est une attaque à distance de mob.
- Vitesses, rectangle d'aggro, portée, cadence et phases seront des paramètres techniques explicites par famille, vérifiés avec physique réelle et télégraphie. Les valeurs non chiffrées des specs ne seront pas présentées comme des règles existantes ; réglages consignés au journal et soumis au playtest requis.
- Les profils N5–9, Necromancer et Boss ne sont pas implémentés ici. L'ambiguïté « niveau 5 et 9 » et leurs timers/plafonds restent à résoudre avant RUN-024/026.

## D06/D04 — Swarm et récompenses proposés

- Une zone N4 produit quatre Skulls simultanés au maximum. Aucun remplacement des morts pendant la même présence du joueur. Quitter la zone supprime les survivants ; rentrer fait réapparaître quatre Skulls. Mort/reset/rechargement détruit toutes les instances ; pas de Skull hors zone.
- Chaque zone a quatre emplacements logiques stables. Un emplacement rapporte 1 shard à son premier kill de la tentative, puis 0 pour ses réapparitions après sortie/rentrée. Budget maximal : 4 shards par zone et tentative. Aucune récompense au despawn, aucun soin de Skull. C'est une **précision/exception au “un mob tué rapporte 1 shard”** à valider pour borner le farm de zone.
- Les mobs fixes reviennent au reset avec leurs récompenses normales, conformément à RUN-018. Aucune protection anti-farm permanente ajoutée. Les futurs Skulls invoqués par Necromancer/Boss ne sont pas couverts par cette décision.

## D07 — Shield et déclencheurs proposés

- Un nouveau Shield ramassé rafraîchit le temps restant à 10 s, sans addition. Le pickup est consommé même sous Shield. Le timer suit le temps de gameplay, suspendu par pause/modales ; échange d'arme sans effet ; mort/reset/reprise/changement de niveau supprime le buff.
- Le bouclier annule entièrement dégâts et réactions des attaques ennemies (contact/mêlée, projectile et sort au sol, swarm). Les projectiles ennemis sont consommés au contact même si les dégâts sont annulés. Distinguer explicitement les projectiles de tourelles : même réaction de dégâts que les tirs ennemis, mais **ils traversent la protection Shield** car ce sont des pièges.
- Secret : un coup de mêlée ou un projectile du joueur suffit, sans quantité de dégâts requise. Projectile arrêté par le mur ; mêlée ne frappe pas au travers ; pas de révélation depuis la face opposée d'un obstacle. Ni attaque ennemie, ni corps du joueur, ni piège ne révèle. L'attaque d'atterrissage reste RUN-022.
- Sauvegarder le flag avant suppression de collision/fondu. Échec disque : mur fermé, feedback d'échec et retry possible. Au reload, secret acquis directement ouvert, sans rejouer le reveal. Contenu de la salle suit ses règles propres : coffre rare/potion de tentative, bonus HP permanent.
- Plaque : activée une fois par tentative en se plaçant dessus ou avec un tir du joueur. Bouton : E à proximité, joueur vivant, hors modale, une seule activation. Une activation maintient la porte ouverte jusqu'au reset ; aucun temporisateur de fermeture ajouté. Mêlée et tirs ennemis n'activent pas la plaque.
- Porte payante : coût en coins explicite par instance, E à proximité ; contrôle des fonds puis débit/ouverture une seule fois. Jamais de shards, jamais de sauvegarde durable. Prix et placements finaux appartiennent à RUN-020. Son budget total optionnel doit laisser le coût de sortie accessible sans reset obligatoire, y compris après dépenses successives.

## Pièges et intégration proposés

Les cycles des piques et tourelles sont configurables par instance, avec phase initiale fixe et préparation visible. Les piques rentrés ne blessent pas ; leur base peut rester solide mais les pointes/capteur ne doivent pas bloquer le passage à tort. Trappe : déclenchement par dessus au passage du joueur, bref avertissement puis ouverture, sans fermeture avant reset. Les fixtures vérifient une sortie possible par saut selon le terrain ; les placements réels seront vérifiés en RUN-020. Réutiliser les profils de réaction existants : piège solide avec recul/protection, projectile de tourelle avec protection/interruption sans recul/hit-stun.

Art/SFX : contribution Claude cadrée dans [RUN-019_CLAUDE_HANDOFF.md](RUN-019_CLAUDE_HANDOFF.md), préparée sans message à un autre chat. Codex fournit les scènes/événements/paramètres fonctionnels ; les assets et leur intégration visuelle ont un propriétaire explicite au handoff. Les télégraphies et sons P0 de ce lot doivent être intégrés et vérifiés avant sa clôture ; RUN-021 ne sert pas à omettre ces exigences.

## Recette requise après validation

1. Profils et comportements par famille : patrouille, acquisition/perte/occlusion, bords/retour, portée/phase, tirs et explosions réels, dégâts fractionnaires, recul sans interruption, mort unique et soins/récompenses.
2. Swarm : limite quatre, sortie/rentrée, budget quatre malgré recréation, despawn sans reward, pause/mort/reset ; pas de soin et pas de recul Skull.
3. Pièges : phases sûres/dangereuses, rotation, collisions réelles, trappe ouverte jusqu'au reset et saut de sortie, trajectoire/occlusion des tourelles, plantes solides ; pause et interactions Shield/source.
4. Shield : collecte/réactivation, dix secondes de gameplay, échange d'arme, toutes sources ennemies contre chaque source de piège, fin d'effet, mort/reprise.
5. Secrets et bonus : mêlée/tir depuis les faces accessibles, occlusion, doublons, erreur disque/retry ; sauvegarde/reprise dans des processus distincts, ancienne save v2 conservée, New Game. Bonus à pleine vie/blessé et MAX HP après reset.
6. Plaques/boutons/portes : clavier réel, paiement insuffisant/suffisant, maintien E, ouvertures multiples sans double débit, plusieurs portes proches, reset complet. Budget financier de fixture vérifié ; budget N2–4 réel à RUN-020.
7. Import Godot 4.7.2, isolation user://, régressions complètes `tools/test.sh`, fixtures avec rendu 640×360 et inspection des captures ; validation humaine art/écoute et essai des nouvelles interactions. Évidence, corrections/retests et limites dans journal, learning sur résultat réel ; Jev puis inspection avant DONE.

**Validation acquise le 5 octobre 2026 pour D01/D06/D07 et le budget Skull ; implémentation autorisée.** Les paramètres techniques et l'organisation du code ne demandent pas une approbation supplémentaire à chaque étape. Aucun push/PR/merge autorisé par le lancement.
