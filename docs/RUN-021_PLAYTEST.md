# RUN-021 — Vérification humaine après passe technique

Le visuel Claude et l’ajout de la musique N4 sont validés humainement le6octobre. Cette fiche concerne les nouveaux correctifs Codex et la sélection SFX restante ; les tests moteur ne valent pas playtest humain. Utiliser les scènes actuelles conservées et la chaîne menu→N1→N4, sans rejouer de générateur ni effacer une sauvegarde humaine pour tester.

| Point | Changement à juger |
| --- | --- |
| Archer hors aggro | Les six archers N3/N4 sont désormais des sentinelles en idle : pas de marche sur place ni retournement incessant. L’inspection des71images de la vidéo montre une alternance d’orientation sur place compatible avec le défaut reproduit ; vérifier sa disparition dans votre jeu. Ils se tournent vers le joueur et tirent pendant l’aggro, puis restent stables après perte d’aggro ou recul. |
| Archer et Sorcerer | Détection visible jusqu’à±360px au même étage, déclenchement à240px ; pas de tir initié à travers un mur. Juger le danger à distance et la lisibilité des préparations. La zone Sorcerer reste figée au point annoncé. |
| Bloated et Chud | Poursuite60/48px/s, patrouilles18/12 inchangées ; juger la pression, le contact et la possibilité d’esquiver. Arrêt aux bords/murs toujours requis. |
| Tir joueur | Longbow0 :2,2s/176px ; Knives0 :1,4s/104px. Juger le rythme et la distance de combat, avec équipement de base puis amélioration. Les dégâts sont identiques. |
| Parcours | N1–4 et variantes hautes/basses, économies de sorties12/18/25/32, achat optionnel4/secret/HP N4 ; vérifier difficulté, sauts, dangers et reprise après mort. Les scènes manuelles n’ont pas été redessinées pour le pilote. |
| SFX | Dix candidats préparés par Claude restent non branchés tant qu’ils ne sont pas retenus. Écoute A/B sous `work/run021/audio/ab_sfx_current_then_candidate.ogg` ; décision et intégration audio restent distinctes. |

Le scope final prévoit des niveaux beaucoup plus grands et plus riches que ces scènes ; ce playtest n’est pas une validation de leur ampleur définitive. La clôture de RUN-021 et la validation0.3.0 demandent inspection des critères du workflow et validation des correctifs restants. Aucune autorisation de push/PR/merge n’est impliquée.
