# RUN-017 — Contribution Claude : Spirit, dialogue et lisibilité N1

**Historique de la première passe, livrée dans `1fbb730` et validée humainement le 3 octobre 2026.** Les instructions ci-dessous décrivent son contrat initial. La nouvelle demande (Space phrase par phrase, +2 s, résurrection et apparition/disparition du Spirit) est définie dans [le contrat de seconde passe](RUN-017_CLAUDE_HANDOFF_02.md), qui remplace les comportements concernés.

RUN-017 ACTIVE, autorisée le 3 octobre 2026. Codex réalise l'ingénierie et la recette ; la contribution artistique ci-dessous reste à réaliser avant VERIFY complet. Aucun chat Claude créé ou sollicité par ce document.

## Propriété

Claude possède les nouveaux assets Spirit (repos/dialogue), portrait, VFX associés, leurs générateurs/sources/crédits, et un nouveau `scripts/spirit_art.gd` branché sur le node `AncientSpirit` de N1. Codex possède `scripts/level.gd`, `scripts/progression.gd`, `scripts/n1_dialogue.gd`, les règles/modales et les tests.

Après remise du checkpoint Codex, Claude peut adapter la présentation de `scripts/dialogue_panel.gd` (layout, textures, portrait et sons), sans changer son API ni ses gardes d'entrée/fin/retry. Pas d'édition concurrente : ces fichiers sont remis explicitement après le checkpoint. Aucun déplacement ou modification de collision, économie, cadence, ennemis, terrain ou scène partagée sans handoff.

## Contrats techniques et résultat attendu

- N1 : `scenes/eidolon_vale.tscn`, hérite du terrain/parcours du slice conservé. Intro activée uniquement dans N1 ; fixture de transition reste un outil de test, aucun N2 final.
- Spirit : node `AncientSpirit` Node2D au spawn, `(76,144)`, sans collision/combat. Placeholder fonctionnel temporaire ; fournir silhouette et idle/dialogue lisibles à 640×360. État `level.modal == "dialogue"` disponible pour animation. Aucun nouveau gameplay.
- Portrait et bandeau inférieur cohérents avec le HUD existant. Neuf phrases anglaises de docs/09, animation du texte puis avancement automatique ; Space passe toute la conversation, Escape n'ouvre pas pause. Le contrôle joueur reste bloqué jusqu'à sauvegarde réussie et relâchement des touches.
- Dialogues terminés/skippés non rejoués après mort/Continue ; New Game réinitialise. Échec disque visible, E réessaie ; aucun flag validé avant écriture réussie.
- Coffre N1 `(220,144)`, potion `(1968,134)` : placements à vérifier par recette Codex, éloignés des pièces et de leurs éclats. Contrôle de lisibilité avec les feedbacks existants.
- Art/audio P0 du jalon selon docs/13 : Spirit repos/dialogue, décor Eidolon Vale, indication d'interaction et sortie. Réutiliser les assets conformes déjà livrés ; compléter seulement les manques du périmètre. Sons de dialogue sont P1/P2 dans docs/08 ; pas de voix imposée. Examiner le son de sortie/interaction existant avant d'ajouter une source.
- Correction de recette Codex : fermeture arrête les lecteurs audio ; `scripts/chest_opened_fx.gd::_play` ignore les cues si `current_scene.closing` est vrai. Préserver ce garde : le reveal retardé relançait une voix pendant la fermeture.
- Sources et licences : consulter `.local/asset-paths.md` et exigences/library pertinentes si sourcing nécessaire. Sources externes intactes ; dérivés dans le projet, provenance/crédits conservés.

## Recette et retour

Importer avec Godot 4.7.2, vérifier introduction animée/skip et reprise, erreurs de sauvegarde, tutoriels/coffre/potion, rendu 640×360 et indication de sortie. Préserver les assertions gameplay. Rapporter fichiers changés, résultats exécutés, captures et limites d'écoute/rendu. Validation artistique humaine et playtest N1 obligatoires avant DONE ; pas de push/PR/merge autorisé dans ce handoff.
