# RUN-019 — Contribution Claude préparée

**5 octobre 2026 — Préparation seulement ; contrat produit en attente, aucune remise de fichiers partagés ni message envoyé.**
Branche `feature/run-019-threats-exploration`. Codex orchestre le lot ; [contrat proposé](RUN-019_CONTRACT_REVIEW.md). Les API définitives seront documentées après le checkpoint technique avant toute intégration dans les scripts/scènes partagés.

## Livrable

Red/Bloated Slime, Skeleton Warrior/Archer, Blight Sorcerer, Possessed Skulls, Chud Blob : silhouettes distinctes, patrouille/poursuite, attaque et préparation, dégâts/mort selon famille. Archer : départ/trajectoire/impact ; Sorcerer : incantation, zone figée annoncée une seconde, explosion ; Skulls : apparition/disparition, déplacement/contact/mort. Respecter l'absence d'interruption des attaques par les dégâts et les formes physiques fournies par Codex.

Piques mobiles rentrées/préparation/sorties, trappe fermée/avertissement/ouverte, tourelle préparation/tir/projectile/impact, plante solide, Shield pickup/aura/fin, bonus HP pickup/feedback, plaque inactive/active, bouton, porte secondaire fermée/ouverture, mur secret discret/fondu. Les états sûrs et dangereux doivent être lisibles ; textes visibles anglais. Rendu 640×360 nearest, grille 16 px et chevalier existant conservés. Aucun placement ni habillage global de N2–4 dans cette contribution ; RUN-020/021 les prennent en charge.

Lire docs/06, docs/08 et docs/13 pour l'inventaire précis. Tous les SFX P0 des familles de ce lot sont requis : attaques/morts Warrior et Archer, incantation/avertissement/explosion/mort Sorcerer, apparition/mort Skull, contact/mort Bloated, attaque/mort Chud ; activation Shield ; trappe déclenchée, tir/impact tourelle, contact plante, contact piques ; paiement/déverrouillage/ouverture porte, plaque/bouton activé, secret révélé. Red peut partager la famille Slime existante selon docs/08. HP bonus et fin Shield P1 : fournir ou consigner leur traitement explicite, sans prétendre couvrir toute la campagne. Réutilisations/substituts sonores doivent être identifiés et soumis à l'écoute humaine.

## Propriété et sources

- Claude pourra créer ses générateurs `tools/art/run019/`, dérivés `assets/run019/`, sons `assets/sounds/run019/`, sources `assets/source/run019/`, et `docs/RUN-019_ASSET_MANIFEST.md`. Ces chemins constituent le périmètre proposé de la contribution, pas une preuve de leur existence ni d'un travail en cours.
- Codex possède gameplay, persistance, tests, scènes fonctionnelles, workflow/journal/learning et contrats. Aucun script/scène partagé n'est remis à Claude à ce stade. Après checkpoint technique, une liste exacte et des hooks vérifiés seront ajoutés ici ; Codex cessera alors d'éditer les fichiers remis jusqu'au retour.
- Ne pas régénérer globalement les atlas existants ni modifier N1. Consultations futures : `.claude/rules/visual-assets.md`, `.local/asset-paths.md` si présent puis bibliothèques pertinentes. Sources externes en lecture seule ; origine → adaptation → dérivé → intégration ; sources et licences conservées, crédits remis dans le manifeste.
- Le manifeste devra lister fichiers, provenance/licence, dimensions, frames/fps/boucles, ancrages, captures, commandes réellement exécutées et limites. Signaler les besoins de correction physique à Codex avant toute édition des règles.

## Retour et recette

L'intégration sera vérifiée par Codex sur les comportements réels, avec profil de sauvegarde isolé et `flock work/.godot.lock`, import Godot4.7.2, régressions, captures 640×360 et inspection. La validation humaine du rendu/écoute et essai des interactions reste requise avant DONE. Aucun lancement RUN-020/021, push/PR/merge par cette contribution. Les APIs ne sont pas encore stabilisées : ne pas inventer de noms de scènes/signaux à partir de ce document.
