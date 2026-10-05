# RUN-015 — Contrats à valider avant implémentation

Contrat **validé intégralement par l’humain le 3 octobre 2026** (« Je valide le contrat run-015 »). Les résultats d’implémentation et de vérification sont consignés au journal.
Sources : docs/03 (table de persistance), docs/04 (économie et coffres), docs/05 (modales et clavier), docs/01 et docs/10 (pause et dialogues).

## D03 — Tentative et état durable

**Validé par l’humain le 3 octobre 2026**, y compris la règle de dépense gains courants puis banque et la sauvegarde immédiate du débit de banque décrites sous D04. Migration v1 également validée avec le contrat intégral.

- Reprendre au spawn du niveau courant ; ne conserver ni position, ni coins, ni état des ennemis, ni soins de tentative.
- Sauvegarder la destination et les shards restants au passage de niveau.
- Sauvegarder immédiatement les acquisitions d'équipement, améliorations et éléments uniques permanents ; aucune acquisition confirmée ne doit disparaître à la fermeture.
- Sur mort, restart ou fermeture, abandonner les shards courants ; conserver la banque après les débits déjà effectués.
- Une opération durable n'est confirmée que si son écriture réussit ; afficher l'échec et permettre une nouvelle tentative, sans écraser une sauvegarde illisible.

## D04 — Économie et ancienne sauvegarde

- Les coins restent des coins, y compris au-delà des 12 requis. Aucun surplus converti en shards. Les kills N1 ordinaires donnent chacun 1 shard.
- Dépenser d'abord les gains de tentative, puis la banque ; sauvegarder immédiatement tout débit de banque. Exemple : banque 50, gains 8, achat 12 → banque 46 et gains 0 ; une mort laisse 46.
- Proposer explicitement la conversion du bonus v1 entier en banque de shards, avec accord humain dans le menu et copie originale conservée. L'origine exacte des bonus anciens n'est pas reconstructible avec le schéma v1.
- Sans accord de migration, conserver le fichier original et ne pas le remplacer silencieusement.
- Les taux d'offrande 20/50 %, leur base et la seconde offrande sans première restent à trancher avant RUN-023 ; ne pas implémenter ces offrandes en RUN-015.

## D05 — Interface et contrats pour RUN-016/017

**Validé par l’humain le 3 octobre 2026.**

- Deux slots d'équipement verticaux (mêlée/tir). Les choix de récompense dans une fenêtre de coffre restent horizontaux.
- Une seule modale importante à la fois ; une demande concurrente ne remplace pas une décision en cours. Mort et transition interdisent les nouvelles interactions.
- Escape ferme la fenêtre active ; la même pression ne déclenche pas pause. Depuis le jeu libre, Escape ouvre pause.
- Le dialogue immobilise le joueur. **Amendement humain RUN-017, 3 octobre 2026 :** Space passe une phrase par pression, sans son, au lieu de terminer toute la conversation ; délai de chaque phrase augmenté de 2 s. Escape n'ouvre pas pause pendant le dialogue. Mémoriser durablement seulement après la dernière phrase (fin naturelle ou Space).
- Coffre tuto gratuit : refus ou fermeture consomme le coffre pour la tentative ; après reset il redevient disponible tant que Longbow n'a pas été acquis. L'acquisition durable empêche un doublon et ne donne aucune amélioration.
- Confirmer New Game lorsqu'il remplace une partie ; restart et sortie ordinaires ne nécessitent pas de confirmation supplémentaire.

## Contribution Claude et propriété proposée

Claude prend la direction artistique, la création/adaptation des assets et leur provenance : présentation des menus RUN-015 ; Longbow/flèche, shards, coffre fermé/ouvert, potion, icônes de slots et feedbacks RUN-016, selon docs/08 et docs/13. Codex prend les contrats, la persistance, les interactions clavier et le gameplay.

Avant édition parallèle, attribuer précisément les fichiers : les scripts d'état et de gameplay restent à Codex ; Claude peut produire des assets dans des fichiers convenus. Une scène ou un script UI partagé demande un handoff explicite, jamais deux éditions concurrentes. Aucun travail n'a été transmis à un chat Claude par cette préparation.

## Validation technique prévue

- Matrice mort/sortie/fermeture/rechargement/dépense, dont achat puis mort et acquisition puis fermeture.
- Migration v1 acceptée/refusée, original préservé, corruption, version inconnue et échec disque ; aucune perte silencieuse.
- Continue sans sauvegarde, reprise à froid, New Game confirmé/annulé et restart.
- Navigation clavier et rendu 640×360 : focus, Controls, pause, exclusivité, touches maintenues et absence de double déclenchement/input traversant.
- Régressions mobilité, combat, collecte, porte, mort/reset/transition et sauvegarde selon les changements réels.
- Revue humaine de RUN-015 puis revue Jev et clôture suivant le workflow ; RUN-016 seulement après validation, sur la même branche.
