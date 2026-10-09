# RUN-021 — Indices visuels et introduction des Secret Walls, 9 octobre 2026

L'humain a validé après playtest la révélation précédente, puis demandé ce complément pour rendre les secrets découvrables. Le masque, le fondu0,6s, la sauvegarde et les récompenses sont conservés. Aucune nouvelle distribution de secrets ou refonte du terrain.

## Comportement demandé

- Au moins trois variantes : faible glow, fissures discrètes, légère différence de teinte. L'indice concerne l'entrée16×32, pas toute la salle masquée. Pas d'icône, de texte flottant ou de son préalable permanent.
- Chaque mur référence un style réutilisable (Resource) : variante, texture/indices, couleur et intensité modifiables selon niveau/biome. Le rendu de fond continue de suivre le TerrainSkin courant. N4 utilise initialement la variante fissures ; les trois variantes sont livrées et rendues en contexte.
- Introduction activée seulement sur le premier mur N4, par une propriété opt-in. À64px de son centre, avec ligne de vue physique vers l'entrée (pas à travers plafond/sol/autre obstacle), fenêtre contextuelle existante : titre `A Strange Wall`, texte **`There's something strange about this wall...`**, bouton Continue.
- Une fois le mur révélé ET le fondu terminé, fenêtre tuto existante : titre `Hidden Secrets`, texte **`The world is full of secrets. Many lie hidden behind walls. Keep your eyes open.`**, bouton Continue. Cette explication attend si un autre modal, une pause, la mort ou une fin de niveau empêche son ouverture.
- Les deux acquittements réutilisent `completed_dialogues`, ids `secret_wall_hint` et `secret_wall_tutorial`, durables par partie. New Game réinitialise ; les erreurs d'écriture utilisent le retry du tuto existant. Fermer avec Escape suit la règle existante : suppression pour la tentative, sans faux flag durable.
- Une sauvegarde où le mur est déjà acquis ne rejoue ni l'indice de proximité ni le fondu. Si le tuto explicatif n'a jamais été acquitté, il peut être présenté quand le joueur s'approche de l'entrée déjà ouverte ; pas de popup à distance au spawn. Un tir qui révèle le mur avant l'indice laisse seulement l'explication.
- Aucun tutoriel ne s'intercale pendant le fondu, et aucune fenêtre ne remplace un modal actif. Reprise après relâchement des commandes selon le comportement du niveau.

## Ownership et interfaces

- **Claude Opus5.5** : nouveaux `scripts/secret_wall_hint.gd`, `scripts/secret_wall_style.gd`, trois ressources `assets/run021/secrets/n4_{glow,cracks,tint}.tres`, textures sources/dérivés sous `assets/source/run021/secrets/` et `assets/run021/secrets/`, générateur sous `tools/art/run021/secrets/`. Aucun fichier existant, aucun Godot/commit/document partagé. Style Resource sans gameplay ; `hint.configure(style: Resource, rect: Rect2)` avec rectangle local au mur, par défaut `Rect2(-8,-32,16,32)`. Hint enfant du mur, z51 absolu, effritement à52. Parent gère tout le fondu.
- **Codex root** : `secret_wall.gd` (style et intro opt-in, signal `passage_revealed` après animation), `level.gd` (déclencheurs et fenêtres), propriétés ciblées N4, intégration et validation.
- **Sous-agent Codex** : tests dédiés `tests/secret_wall_intro.gd`, ajout au lanceur `tools/test.sh`. Les tests de transactions existants désactivent explicitement ce tuto lorsqu'ils isolent les récompenses ; le root possède cet ajustement.
- Le travail N4 parallèle existant (`campaign_decor.gd`, `campaign_terrain_skin.gd`, `secret_wall_mask.gd`, assets/tools N4) constitue la baseline protégée. Le nouveau hint se superpose au masque sans le modifier ; pas de scan des bibliothèques externes.

## Vérification

Godot Windows4.7.2, profil isolé et lock : indice proche/loin/obstacle/plafond, séquence après fondu seulement, pause/modal/death, mémoire et cold/New Game, échec/retry, commandes maintenues, variantes sans fuite du loot. Rendu des trois variantes sur N4 courante au zoom1,2× et des deux fenêtres. Validation humaine restante pour la subtilité, lisibilité et ressenti de cette nouvelle passe. RUN-021 reste ACTIVE ; aucun push/PR/merge ou lancement d'une autre run.

## Livraison et sélection du style

Claude Code Opus5.5 a livré `secret_wall_style.gd`, `secret_wall_hint.gd`, cinq textures transparentes16×32 et les trois ressources suivantes :

| Ressource | Indice | Réglages initiaux |
| --- | --- | --- |
| `assets/run021/secrets/n4_cracks.tres` | Fissure fine traversant les joints, éclats et liseré | N4 par défaut, intensité1 |
| `assets/run021/secrets/n4_glow.tres` | Lumière cyan grisée filtrant par quelques joints | Additif, intensité0,5, respiration15%/4,5s |
| `assets/run021/secrets/n4_tint.tres` | Pierres légèrement plus chaudes/pâles, bord tramé | Intensité0,24 |

Sélectionner le mur dans l'Inspector et affecter sa propriété `hint_style`. Pour un autre biome, dupliquer une ressource et ajuster couleurs/intensité ; ses textures sont des masques blancs réutilisables. `intro_enabled` reste réservé au premier N4. Les overlays sont des enfants du mur et suivent son fondu.

Art original procédural du projet, sources et provenance dans `assets/source/run021/secrets/`. Régénération : `python3 tools/art/run021/secrets/secret_hints.py`. Le helper `tools/art/pixel.py` est suivi ; le générateur N4 parallèle reste facultatif et ne sert qu'aux aperçus. `--no-n4` fournit un aperçu de secours sans cette dépendance. Les PNG du jeu sont identiques avec ou sans elle. Aucune modification des assets N4 parallèles, aucune licence tierce ajoutée.
