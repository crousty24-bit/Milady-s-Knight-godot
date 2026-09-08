# Astra — La Poterne des cendres

## Décisions fixées
Godot 4.5.1, Windows et clavier. Saut simple à hauteur variable, tolérance au bord et buffer. Épée au sol/en l'air, sans combo. 3 PV, invulnérabilité temporaire. Mort : niveau entièrement réinitialisé, pas de checkpoint. 18 pièces fixes, porte à 12 ; 8 communes et deux branches de 5. Offrande à la poterne : justification provisoire. Aucun inventaire, farming, manette, sauvegarde ou progression RPG.

## Ordre d'implémentation
1. Socle et contrôleur autonome : import propre, scène de joueur, saut, caméra, salle de test ; lancer Godot.
2. Combat : épée, slime physique, PV, invulnérabilité et mort ; tests des impacts et du redémarrage.
3. Boucle complète : pièces, HUD, porte à 12 et victoire ; tester 11/12, double collecte, double dépense.
4. Parcours : 8 pièces communes, 5 hautes, 5 basses ; plateforme mobile, fosse, deux ronces ; traverser les deux routes dans le moteur.
5. Habillage : village abandonné, fortification, corruption progressive, trois indices narratifs, sons.
6. Validation : import neuf, scénarios de physique et de progression, captures du rendu, lancement Windows ; corriger puis rejouer les scénarios concernés.

## Architecture
Scènes éditables : vertical_slice, player, slime, coin, moving_platform, hazard, gold_gate, hud. Le niveau possède le gold et l'état de tentative. Joueur et slime possèdent leur santé. Signaux locaux pour collecte, santé, mort, demande d'offrande. TileSet externe, TileMapLayer de terrain. Pas de gestionnaire global.

## Critères d'acceptation
- Aucune erreur de parsing ou d'exécution au lancement/import.
- Aucun double saut ; saut court/long distinct ; combat utilisable en l'air.
- Un ennemi ne reçoit qu'un dégât par frappe ; invulnérabilité bloque les impacts répétés.
- Les deux branches sont traversables et réversibles ; pas de pièce nécessaire piégée.
- 18 pièces collectables une fois ; ouverture refusée à 11, paiement unique à 12, victoire seulement derrière la porte.
- Mort et reprise remettent gold, ennemis, porte et pièces à zéro.
- HUD lisible à 320×180, pas de danger caché sous le HUD.

## Origine
Assets sélectionnés dans l'ancien projet test-1, conservé intact. Licences non fournies ; provenance à compléter avant distribution publique. Nouvelle implémentation ciblée : les scripts de mort et de saut mural de l'ancien projet ne sont pas repris.

## État livré

- [x] 1. Socle / joueur et premier lancement.
- [x] 2. Combat / dégâts / mort.
- [x] 3. Pièces / HUD / paiement / victoire.
- [x] 4. Deux routes / dangers / plateforme / retours en arrière.
- [x] 5. Habillage village et corruption, indices narratifs, sons.
- [x] 6. Vérifications moteur et rendu, lancement Windows, 35 contrôles.

Les scènes sont livrées prêtes à modifier dans Godot. Le plaisir de jeu et la durée de découverte doivent maintenant être évalués par des joueurs ; ce n'est pas un critère que le pilote automatique peut valider.
