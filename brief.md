# Milady's Knight — Brief projet

## Résumé

**Milady's Knight** est un action-platformer 2D rétro pixel-art Dark Fantasy avec des mécaniques inspirées du rogue-lite.

Le joueur incarne **The Ashen Knight**, ramené à la vie pour traverser un royaume corrompu, atteindre Darkveil Dungeon, vaincre Lupikal The Doombringer et libérer Princess Karla.

Le projet vise une **démo jouable courte et complète**, pas un jeu commercial de grande ampleur.

## Scope

- environ 1 à 2 heures de jeu visées ;
- 10 niveaux conçus manuellement ;
- difficulté progressive ;
- combat mêlée et distance ;
- plateforme, exploration, pièges et passages secrets ;
- collecte de Gold Coins ;
- Shards obtenus par le combat ;
- coffres et amélioration d'équipement ;
- progression die-and-retry ;
- Boss final.

La version finale du projet restera une version de démonstration alpha/beta et ne correspond pas nécessairement à `1.0.0`.

## Ce qu'est le projet

- un action-platformer 2D ;
- un jeu à niveaux fixes ;
- une expérience courte orientée maîtrise du niveau ;
- une démo alpha/beta développée par itérations ;
- un projet où gameplay, lisibilité et stabilité priment sur le polish.

## Ce que le projet n'est pas

- un roguelike procédural ;
- un open world ;
- un RPG long ;
- un Metroidvania basé sur un grand système d'ability-gating ;
- un jeu multijoueur ;
- un live-service ;
- un projet visant obligatoirement une version `1.0.0`.

## Direction technique et visuelle

Références actuelles :

- moteur : Godot ;
- pixel-art Dark Fantasy ;
- grille de référence : 16×16 px ;
- résolution interne : 640×360 ;
- ratio : 16:9 ;
- filtrage pixel-art : Nearest / Nearest Neighbor ;
- scaling entier privilégié.

Les détails complets restent dans `docs/`.

## Workflow documentaire

- `README.md` : présentation générale du dépôt ;
- `AGENTS.md` : règles durables pour les agents ;
- `brief.md` : contexte synthétique et état vérifié ;
- `runs-workflow.md` : roadmap agentique par versions et runs ;
- `runs-journal.md` : historique des runs et preuves de validation ;
- `learning.md` : journal pédagogique expliquant à l'humain comment les runs ont été implémentées dans Godot et le code ;
- `docs/` : documentation détaillée du projet.

## État du projet — 9 octobre 2026

Les preuves techniques et leurs limites sont consignées dans [runs-journal.md](runs-journal.md) ; la roadmap et les critères de clôture sont dans [runs-workflow.md](runs-workflow.md).

### Version publiée et branche en revue

**La version publiée reste 0.2.0, avec le jalon N1 validé.** La branche `feature/run-020-021-campaign` porte les travaux de campagne N1–N4 et la cible de production 0.3.0. La cible ne constitue pas une promotion de version. Le 9 octobre, l’humain a validé toutes les dernières passes Codex et Claude. L’audit global de la branche est en cours et la PR vers `develop` est demandée ; la clôture formelle des runs et les résultats consolidés de la revue seront consignés à son issue.

Le dépôt compte 29 identifiants de run. Les décisions de statut, de version et de clôture doivent suivre `runs-workflow.md` ; les jalons historiques ci-dessous décrivent des étapes antérieures et ne remplacent pas l’état courant.

### Systèmes présents sur la branche campagne

- **Campagne N1–N4 :** Eidolon Vale, Blight Town, Black Forest et Forbidden Graveyard sont reliés par leurs sorties. Les niveaux sont conçus à la main et comprennent des routes verticales, ennemis, pièges, coffres, mécanismes et récompenses.
- **Combat et équipement :** armes de mêlée et à distance, huit armes standard, deux slots, munitions de Longbow et Throwing Knives, caisses et tonneaux de ravitaillement. Le stock courant est transmis au niveau suivant ; mort et reprise restaurent le stock d’entrée du niveau.
- **Commandes :** profils AZERTY, QWERTY, clavier classique et personnalisé. Les attributions peuvent être remappées au clavier et à la souris depuis le menu Controls ; les préférences sont sauvegardées séparément de la partie. Les tirs restent orientés selon le personnage, sans visée au curseur. Les actions spéciale et impact sont réservées mais sans consommateur gameplay.
- **Secrets et interface :** Secret Walls masquent une cache puis la révèlent après découverte, avec indices et introduction. Le HUD affiche les deux slots, les munitions, les coins, les shards et les cœurs sans nombre de HP. Les règles précises restent dans les documents de [contrôles](docs/10_CONTROLS_KEYBINDS.md), [interface](docs/05_UI_HUD_MENU.md), [progression](docs/04_PROGRESSION_ECONOMY_ITEMS.md) et les contrats RUN-021 référencés dans [l’index](docs/README.md).
- **Progression et présentation :** sauvegarde v2, banque de shards, équipements et flags permanents ; menu principal, pause, récompenses de coffre, dialogue Spirit et tutoriels contextuels. Les assets et leur provenance sont suivis dans `assets/VISUAL_CREDITS.md` et `assets/AUDIO_CREDITS.md`.

Le viewport est **640×360**, terrain sur grille 16×16. **Zoom joueur de référence : 1,2× sur les deux axes**, choisi manuellement et retenu après playtests humains le 8 octobre ; ne pas le compenser automatiquement. Voir [Art Bible](docs/06_ART_BIBLE.md#relation-avec-léchelle-pixel-art). Les niveaux N1–N4 actuels ne représentent pas encore les dix niveaux visés par la démo. Les capacités, armes légendaires, N5–N10, le boss final et la conclusion restent à produire selon la roadmap.

### Historique des jalons publiés

- **0.1.0**, clôturée localement le 2 octobre 2026 : socle et première passe de production. Détails et limites dans le journal.
- **0.2.0**, publiée après validation du jalon N1 : RUN-015–017 et RUN-029 livrées. La recette documentée au 3 octobre est historique et ne représente pas l’état de la branche campagne.
- **Cible 0.3.0 :** campagne N1–N4 et systèmes associés. Elle n’est pas déclarée publiée par cette mise à jour documentaire.

Les médias hérités dont les sources ou licences restent à établir doivent être clarifiés avant distribution. Voir le journal pour le périmètre de provenance déjà établi et les limites des validations.

## Principe directeur

Le projet doit rester volontairement limité.

Une feature ou une modification importante doit servir directement la démo prévue et son expérience de jeu.

## Workflow de développement

Le projet avance par lots cohérents, dans une roadmap de 29 identifiants. Les statuts, versions, dépendances et critères de clôture font autorité dans [runs-workflow.md](runs-workflow.md). Les checkpoints datés et preuves de chaque passe, y compris les limites des pilotes, sont conservés dans [runs-journal.md](runs-journal.md) ; ils décrivent l’historique et ne remplacent pas le statut courant ci-dessus.
