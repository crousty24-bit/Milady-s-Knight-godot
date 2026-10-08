# RUN-021 — Secret Wall : contrat approuvé le 8 octobre 2026

L'humain a validé la proposition puis demandé l'implémentation. Périmètre : le secret existant de N4, avec un masque réutilisable ; aucune redistribution des récompenses ni régénération de niveau.

- Fermé : la cache entière ressemble à la maçonnerie voisine ; récompenses et effets masqués, interactions bloquées. Pas de fissure ou de signal sonore préalable systématique.
- Une attaque valide du joueur (mêlée ou projectile) sauvegarde `secret:<id>` avant de commencer la révélation. Un échec laisse masque et collision en place, sans effet ni SFX ; retry possible.
- Révélation : effritement à l'entrée, disparition du masque sur **0,6 s**, un seul SFX au début. L'entrée reste solide jusqu'à la fin ; la pause suspend la transition.
- À la fin : passage franchissable et interactions des récompenses disponibles. Les coups supplémentaires ne rejouent rien.
- Secret acquis au chargement/reprise/mort : passage ouvert et cache visible immédiatement, sans animation ni SFX. New Game rétablit le secret fermé.

Baseline inspectée : `Exploration/SecretWall` à (568,64), id `n4_secret_01`. La cavité est entre plafond y16–32 et sol y64–80, fermée à droite par le terrain à x720. Elle contient actuellement `Items/HpBonus` à (655,48) et `Items/CommonChest2` à (704,64). La potion majeure est hors de cette cavité. Préserver ces changements humains, contrairement à l'ancienne description de RUN-020.

## Ownership

- Codex : `scripts/secret_wall.gd`, garde d'accès dans `scripts/hp_bonus.gd` et `scripts/reward_chest.gd`, propriétés ciblées de `scenes/forbidden_graveyard.tscn`, tests, documentation et vérification finale.
- Claude : **seulement** le nouveau `scripts/secret_wall_mask.gd`, raccord visuel de maçonnerie et évaluation du SFX existant. Aucun changement des scripts possédés par Codex ni du terrain. Aucun nouveau son externe requis.
- Sous-agent Codex : tests dédiés et adaptation de l'attente d'ouverture dans la fixture RUN-019 ; aucun script de production ni scène.
- Travail N2 parallèle : `scripts/campaign_terrain_skin.gd`, `assets/run021/n2/`, `tools/art/run021/n2/` réservés à l'autre travail, jamais édités ni stagés ici.

## Interface du masque

`secret_wall_mask.gd` étend Node2D. `configure(terrain: TileMapLayer, rect: Rect2)` reçoit le terrain réel et le rectangle **local au SecretWall**. Le parent fournit le fondu par son `modulate:a`. Le masque est sans collision et dessiné au-dessus du monde, sous le HUD. N4 : `Rect2(-8,-48,176,64)` inclut plafond/sol pour masquer les lèvres et les touffes qui trahiraient une cavité. Le rendu doit considérer les fausses cellules pleines avec les cellules réelles voisines pour raccorder atlas/exposition et ombrage. Aucun effet d'autonomie ou de sauvegarde dans ce script.

Le mur expose `passage_open` (false jusqu'à la fin de la transition, true au chargement acquis), `cover_rect` et `mask_art`. `opened` continue de signifier secret acquis et interdit les coups dupliqués. Les deux récompenses exposent `required_secret: NodePath`, vide par défaut ; lorsqu'une référence est fournie, l'accès exige `passage_open`, y compris les appels directs.

## Recette

Tests avec Godot Windows4.7.2, lock et profil isolé : attaques réelles, solide pendant fondu puis franchissement, quatre contours, échec/retry, pause, récompenses bloquées, secret acquis à froid et New Game. Captures natives640×360 au zoom humain1,2× : fermé, mi-fondu, ouvert, rechargé. Garder la distinction entre poses injectées, physique exercée et playtest humain. RUN-021 reste ACTIVE ; aucune clôture, push, PR ou merge autorisé par cette demande.
