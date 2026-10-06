# RUN-021 — Vérification humaine après passe technique

Le visuel Claude et l’ajout de la musique N4 sont validés humainement le6octobre. Cette fiche concerne les nouveaux correctifs Codex et la sélection SFX restante ; les tests moteur ne valent pas playtest humain. Utiliser les scènes actuelles conservées et la chaîne menu→N1→N4, sans rejouer de générateur ni effacer une sauvegarde humaine pour tester.

| Point | Changement à juger |
| --- | --- |
| Archer hors aggro | Les six archers N3/N4 sont désormais des sentinelles en idle : pas de marche sur place ni retournement incessant. L’inspection des71images de la vidéo montre une alternance d’orientation sur place compatible avec le défaut reproduit ; vérifier sa disparition dans votre jeu. Ils poursuivent à22px/s pendant l’aggro, même hors portée240px ou avec tir occlus ; ils ne tirent qu’au sol, à portée et avec ligne de vue libre. Vérifier aussi leur stabilité après perte d’aggro ou recul. |
| Archer et Sorcerer | Détection visible jusqu’à±360px au même étage, déclenchement à240px ; pas de tir initié à travers un mur. Juger le danger à distance et la lisibilité des préparations. La zone Sorcerer reste figée au point annoncé. |
| Bloated et Chud | Poursuite60/48px/s, patrouilles18/12 inchangées ; juger la pression, le contact et la possibilité d’esquiver. Ils doivent tenter de sauter les obstacles franchissables sans traverser les murs/plafonds. |
| Tir joueur | Longbow0 :2,2s/176px ; Knives0 :1,4s/104px. Juger le rythme et la distance de combat, avec équipement de base puis amélioration. Les dégâts sont identiques. |
| Poursuite des mobs | Tester Warrior, Archer, Sorcerer, Bloated (inclus malgré son nom de Slime) et Chud contre un bloc bas, une plateforme/rupture praticable, un piège solide et un plafond bas. Confirmer le franchissement physique quand le saut local le permet, l’arrêt devant un mur/plafond infranchissable, et la poursuite dans la portée d’aggro existante. Vérifier que l’aggro et sa perte gardent leur comportement. Les coffres/objets sont des zones d’interaction : confirmer qu’ils ne bloquent pas le mouvement. |
| Slimes exclus | Vérifier que Green, Purple et Red conservent leur comportement actuel et ne commencent pas à poursuivre/sauter les obstacles. |
| Possessed Skulls | Vérifier qu’ils contournent un solide en vol, sans le traverser, et que la zone d’activation/désactivation reste inchangée. |
| Common chest | Ouvrir un common chest : un item direct doit être niveau0,1 ou2 ; une amélioration séparée peut porter un item de2 à3. Vérifier que le rare chest n’a pas changé. |
| Parcours | N1–4 et variantes hautes/basses, économies de sorties12/18/25/32, achat optionnel4/secret/HP N4 ; vérifier difficulté, sauts, dangers et reprise après mort. Les scènes manuelles n’ont pas été redessinées pour le pilote. |
| SFX | Dix candidats préparés par Claude restent non branchés tant qu’ils ne sont pas retenus. Écoute A/B sous `work/run021/audio/ab_sfx_current_then_candidate.ogg` ; décision et intégration audio restent distinctes. |

Le scope final prévoit des niveaux beaucoup plus grands et plus riches que ces scènes ; ce playtest n’est pas une validation de leur ampleur définitive. La clôture de RUN-021 et la validation0.3.0 demandent inspection des critères du workflow et validation des correctifs restants. Aucune autorisation de push/PR/merge n’est impliquée.


## Correctifs de poursuite et common chest en attente de playtest

Après la validation humaine de la passe précédente, de nouveaux correctifs gameplay ont été demandés puis intégrés : poursuite avec saut local pour les mobs concernés, contournement en vol des solides par les Skulls, et limitation du tirage direct du common chest aux niveaux0–2. Les scénarios ci-dessus sont à tester sur le jeu intégré. La validation humaine précédente ne couvre pas ces correctifs ; aucun résultat de playtest humain nouveau n’est consigné ici.

Vérification Codex terminée : recette complète composée2375PASS/50RESULT, routes basses19/19 et hautes21/21, sauts rendus16/16. Les tests couvrent obstacles16/32px, gap16px, descente32px, refus de vide120px et plafonds/murs infranchissables ; ils ne couvrent pas toutes les géométries possibles ni le perchoir optionnel Coin23 N2 avec Bloated poursuivant. Les changements humains N2 sont préservés.
