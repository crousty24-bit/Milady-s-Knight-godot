# RUN-017 — Seconde passe Claude : résurrection et apparition du Spirit

**Contrat historique livré dans `36a6251`, correctifs dans `b825d11`, validés humainement le 3 octobre 2026.** À la demande humaine, le Spirit est désormais à `(140,144)` sur la tombe, sans offset Art ; le chevalier est posé au sol et la caméra stabilisée avant résurrection. Ces décisions remplacent les positions initiales ci-dessous. Codex reprend le dernier correctif de pose idle pendant apparition/dialogue, la revue finale et la PR autorisée vers `develop` ; la présente délégation n'est plus en attente.

Demande humaine du 3 octobre 2026, sur **`feature/run-017-eidolon-vale`**. La première contribution Claude (`1fbb730`) est validée humainement. La nouvelle passe technique Codex est livrée sur cette même branche ; les règles ci-dessous remplacent les comportements concernés du premier handoff. Ce document est le contrat à transmettre à Claude Code ; aucun chat Claude n'a été créé ni contacté depuis Codex.

## Résultat demandé

1. Le chevalier commence allongé, comme mort, puis ressuscite et rejoint sa garde idle. Cette séquence est réservée à la première entrée de **New Game** ; aucune lecture après mort, restart ou Continue.
2. Le Spirit reste caché jusqu'à ce que le joueur atteigne **32 px devant son spawn**, deux blocs de 16 px vers la droite. Son apparition visuelle et sonore précède l'ouverture du dialogue. Après la dernière phrase, il reste présent puis disparaît lorsque le joueur s'éloigne.
3. Préserver les sprites repos/dialogue, portrait, halo et présentation acceptés. **Space passe une seule phrase, sans son.** Chaque phrase bénéficie de **2 s supplémentaires**. Ne pas remettre le skip global ni ajouter de son skip/next.

## Propriété remise à Claude

Claude possède les nouveaux sprites/VFX/cue, sources et générateurs associés, imports et crédits ; `tools/art/knight.py` pour ajouter la résurrection, `assets/sprites/ashen_knight_frames.tres` pour enregistrer cette animation ; `tools/art/spirit.py` et **`scripts/spirit_art.gd`** pour la présentation du Spirit. Il peut assigner le cue sur l'enfant `AncientSpirit/Art` dans **`scenes/eidolon_vale.tscn`**, sans modifier le terrain, les positions ni les contrats du niveau. Ces fichiers sont remis après le checkpoint Codex ; pas d'édition concurrente.

Codex conserve **`scripts/level.gd`**, **`scripts/progression.gd`**, les règles de **`scripts/player.gd`**, **`scripts/dialogue_panel.gd`**, les textes et tests. Les hooks existants suffisent : signaler un besoin de changement avant de toucher une règle. Ne pas rejouer les anciens générateurs de scènes (`build_player.py`, `build_scenes.py`, `build_level.gd`) : ils ne représentent pas les scènes humaines actuelles. Éviter toute modification des sprites existants lors de la génération des nouveaux strips ; vérifier le diff.

## Chevalier : interface disponible

- `player.resurrection_active` et `player.resurrection_progress` (0 → 1). Le niveau pilote la progression pendant que la simulation est suspendue ; aucune AnimationTree nécessaire.
- Ajouter **`resurrect`** au SpriteFrames du corps, **sans boucle**, frames 64×64 avec le même placement et point d'appui que le rig existant. Première frame allongée ; dernière frame debout, compatible avec idle. Le script échantillonne les frames dans l'ordre et masque la couche d'attaque supérieure. Le fallback actuel échantillonne `dead` à l'envers ; il prouve le raccord technique, pas la qualité de l'animation finale.
- Durée globale **2 s**, dont **0,5 s** de pose initiale ; paramètres exportés `n1_resurrection_duration` et `n1_dead_hold_duration`. Le reste est normalisé 0 → 1 ; aucun timer autonome dans l'art.
- Le niveau termine par `finish_resurrection()` puis rend les contrôles après relâchement Space/E/F/Escape. Pas de vraie mort, dégâts, perte de vie, son de mort ni signal `died` pendant cette présentation. Ne pas modifier collision, position, santé ou cadence.
- `n1_new_game` / `n1_resurrection_started` sont gérés transactionnellement par Codex. Un échec disque bloque la pose et propose E/retry. Ne pas écrire les flags depuis la présentation. Aucun son de résurrection supplémentaire n'est demandé.

## Spirit : interface disponible

Le nœud narratif reste **`AncientSpirit` à `(76,144)`**, sans collision ; l'enfant Art garde son décalage validé **+8 px**. Le trigger est relatif au spawn du chevalier, pas à la position du Spirit.

| `level.spirit_phase` | Présentation / contrôle |
| --- | --- |
| `hidden` | Corps et halo invisibles, aucun cue ; chevalier libre après sa résurrection. |
| `appearing` | `spirit_phase_progress` 0 → 1 sur **0,8 s** ; gameplay suspendu. Cue joué une fois à l'entrée. |
| `present` | Repos, puis pose `talk` lorsque `level.modal == "dialogue"`. Après dialogue, repos jusqu'au départ. |
| `disappearing` | Progression 0 → 1 sur **0,8 s**, joueur libre ; pause menu/contexte gèle la séquence. |
| `gone` | Corps et halo invisibles, cue arrêté ; aucun retour/retrigger pour la tentative. |

`spirit_phase_changed(phase: String)` annonce chaque changement ; **ne pas recréer le trigger** dans le script artistique. `spirit_appearance_duration`, `spirit_disappearance_duration` et `spirit_departure_distance` sont exportés par le niveau. Seuil de départ choisi techniquement : **96 px / 6 blocs**, distance au nœud Spirit ; réglable après retour humain. Le départ ne commence qu'après sauvegarde du dialogue. Revenir vers le Spirit ne l'annule pas. Introduction déjà enregistrée au chargement : Spirit absent. Mort avant dialogue terminé : nouvelle tentative cachée, trigger à 32 px à nouveau, mais sans résurrection.

Dans `spirit_art.gd::_frames()`, ajouter les animations **`appear`** et **`disappear`**, non bouclées, compatibles avec les frames **32×48** existantes. Le hook les échantillonne déjà avec la progression du niveau ; le fondu technique actuel reste un fallback. Claude peut adapter ce fondu pour servir l'animation authored, sans changer les états/timings. Halo/particules doivent également finir invisibles. Animation et orientation doivent fonctionner lorsque le tree est en pause pour l'apparition/dialogue ; les autres pauses les gèlent.

À 32 px devant le spawn, le chevalier traverse visuellement le Spirit. Les captures techniques montrent leur chevauchement ; préserver la priorité du joueur et la translucidité validée, mais rendre l'apparition lisible par le halo/particules ou les frames dédiées. Vérifier à **640×360** avec le décor réel, pas seulement l'atlas isolé.

### Audio

**`@export appearance_sound: AudioStream`** est prêt dans Art ; le lecteur enfant **`appearance_audio`** est sur **SFX** et fonctionne pendant la pause cinématique. Assigner un nouveau cue approprié à l'apparition, déclenché une seule fois par la phase `appearing`. Le cue final est encore absent ; le test d'interface assigne temporairement le son d'ouverture du dialogue, sans ajouter d'asset de production.

Conserver `sfx_dialogue_open` sur UI à l'ouverture du bandeau. Aucun son sur Space, ni à chaque phrase. Aucun son supplémentaire de disparition imposé. Lire `.local/asset-paths.md` et les exigences/bibliothèques pertinentes si sourcing ; ne pas modifier les bibliothèques externes. Garder sources, normalisation et attribution dans `assets/AUDIO_CREDITS.md` / `assets/VISUAL_CREDITS.md`. Préserver l'arrêt audio à la fermeture et la garde du reveal retardé du coffre.

## Recette et retour à Codex

- Godot **4.7.2**, import puis `flock work/.godot.lock ./tools/test.sh` avec `GODOT_BIN` adapté. Les profils temporaires isolés protègent la sauvegarde joueur.
- Pilotes rendus : `tests/n1_cinematics.gd` et `tests/n1_visual.gd` avec GL Compatibility / fixed-fps60. Vérifier pose morte, relèvement, idle, apparition après marche réelle de deux blocs, dialogue phrase par phrase silencieux, disparition en s'éloignant et gel en pause.
- Vérifier les animations dédiées dans les vraies scènes, et l'écoute du cue final ; les tests des hooks ne remplacent pas ce contrôle artistique/audio. Captures techniques Codex : `work/run017-revision/{knight-dead,knight-resurrection,knight-idle-spirit-hidden,spirit-appearing,spirit-dialogue,spirit-disappearing,spirit-gone}.png`.
- Retour attendu : fichiers modifiés, ressources liées, commandes réellement exécutées, résultats, captures et limites d'écoute/rendu. Codex reprend l'intégration/recette finale ; humain valide la nouvelle passe et le playtest N1, puis Jev avant DONE. **Pas de push, PR, merge ni lancement d'une autre run.**
