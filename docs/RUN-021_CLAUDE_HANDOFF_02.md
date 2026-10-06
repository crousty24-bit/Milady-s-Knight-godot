# RUN-021 — Complément Claude : Archer, SFX et musique N4

**6 octobre 2026 — Demande humaine consignée et contribution autorisée dans RUN-021.** Complément au [contrat visuel principal](RUN-021_CLAUDE_HANDOFF.md), à exécuter après sa première remise sur les fichiers communs. Claude Opus5.5 pilote ; Codex réserve gameplay/tests. Tous les garde-fous de baseline humaine et de terrain s’appliquent.

## Skeleton Archer : signalement et preuve attendue

L’humain rapporte des animations de déplacement parfois buguées et fournit `20261006-1322-01.9178368.mp4`, sous `C:/Users/allen/AppData/Local/Packages/Microsoft.ScreenSketch_8wekyb3d8bbwe/TempState/Recordings/`. Copie accessible via `/mnt/c/Users/allen/…` ; copie stable `work/run021/video/source.mp4`, empreinte/provenance, inspection et planches sous `work/run021/video/`.

Faits de l’inspection : clip106×98,30fps, environ2,4s ; plusieurs cycles de marche, sans transition d’attaque/impact isolée de manière certaine. Source actuelle `assets/run019/enemies/skeleton_archer.png`, cellules40×32 ; walk4–9 à10fps via `scripts/run019_enemy.gd`. La cause du défaut intermittent : **Je ne sais pas.** Le signalement reste ouvert ; ne pas conclure que le clip démontre ou exclut un bug moteur.

Reproduire patrouille, retournement, aggro/tir, impact et reprise de marche dans Godot ; conserver une capture native et les états animation/frame/direction/vitesse. Comparer cellules, pivots et transitions. Corriger dessin/cadrage/animation de présentation si la cause est démontrée ; tout défaut d’IA ou de mouvement passe à Codex avec reproduction. Possession exclusive des seules tables/méthodes de présentation de `scripts/run019_enemy.gd` pendant cette passe ; pas d’édition simultanée avec le tuning Codex. Fournir preuve avant/après et limites de reproduction.

## Musique Forbidden Graveyard : choix humain

Choix explicite : **`delosound-dark-synthwave-retro-80s-453292`**. Source locale présente au lancement : `Music/delosound-dark-synthwave-retro-80s-453292.mp3` dans la bibliothèque indiquée par `.local/asset-paths.md`. Ne pas modifier ce fichier externe.

Page officielle : [Dark Synthwave Retro 80s — DELOSound](https://pixabay.com/music/dance-dark-synthwave-retro-80s-453292/), piste3:24 signalée Content ID Registered. Archiver les éléments de provenance et les conditions pertinentes de la [licence Pixabay](https://pixabay.com/service/license-summary/), sans inventer un certificat de téléchargement absent. Copier la source, enregistrer son hash, produire un dérivé OGG identifié, documenter conversion/normalisation/boucle et crédits dans `assets/AUDIO_CREDITS.md`.

Raccorder seulement le node `Music` de `scenes/forbidden_graveyard.tscn` par patch de référence précis. Baseline : stream Dreamer, busMusic, volume−24dB ; relever le mix réellement entendu avec ambiance et SFX avant un ajustement. Préserver les autres niveaux, buses et scènes, toutes les données de terrain, sauvegardes et coordonnées. Tester le passage de boucle, pause/reprise, transition entrée/sortie et absence de doubles voix ; livrer un extrait d’écoute et les valeurs finales. La sélection est validée par l’humain ; le raccord et le mix doivent encore être vérifiés.

## SFX : audit puis remplacement ou suppression justifiés

L’humain indique que beaucoup de sons seront à remplacer ou supprimer. Établir un tableau événement → asset réellement référencé → défaut → conserver/remplacer/supprimer → justification et source. Écouter en situation : mouvement/saut, armes/impacts, ennemis et télégraphies, pièges, récompenses, UI et transitions. Ne pas traiter un son hérité simplement présent sur disque comme un événement joué.

Prioriser les sons discordants/répétitifs et préserver les feedbacks utiles au danger, à l’action ou à la confirmation. Pour retirer un feedback requis, expliciter son remplacement visuel/audio ; ne pas supprimer aveuglément tous les événements. Faire la sélection et l’intégration minimale dans un créneau de propriété explicite ; pour les scripts réservés à Codex, livrer les références de remplacement proposées puis obtenir la remise du fichier avant d’appliquer uniquement ces références audio ; aucun timer, dégât, portée ou cadence modifié pour adapter un son. Conserver les sources/licences, vérifier les références avant toute suppression de dérivé. Bibliothèque SFX externe en lecture seule.

Livrer `docs/RUN-021_AUDIO_REVIEW.md`, le complément du manifeste principal, crédits, extraits d’écoute et logs des événements testés. Différencier décision proposée, remplacement effectif et écoute humaine. Codex réserve les tests et la recette finale ; les fichiers partagés sont remis avant cette phase.
