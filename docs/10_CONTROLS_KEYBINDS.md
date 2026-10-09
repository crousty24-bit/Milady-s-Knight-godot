# Milady's Knight — Controls & Key Binds

## Profils intégrés — 7 octobre 2026

Le jeu propose clavier + souris AZERTY, clavier + souris QWERTY, clavier classique et personnalisé. Pas de support manette. Le profil initial suit la disposition du système si elle est détectable ; QWERTY est le repli. Le menu **Controls** est accessible depuis le titre et la pause.

| Action | AZERTY | QWERTY | Clavier classique |
| --- | --- | --- | --- |
| Gauche / droite | Q / D | A / D | Flèches gauche / droite |
| Haut / bas, navigation | Z / S | W / S | Flèches haut / bas |
| Saut / double saut / saut mural / phrase suivante | Espace | Espace | Espace |
| Attaque / tir continu | Clic gauche maintenu | Clic gauche maintenu | F maintenu |
| Interaction / confirmation | E | E | E |
| Alterner les deux slots | A | Q | A |
| Attaque spéciale, prévue | Clic droit maintenu | Clic droit maintenu | R maintenu |
| Attaque d’impact, prévue | Maj gauche | Maj gauche | G |
| Pause / fermer / retour | Échap | Échap | Échap |

Les deux profils souris utilisent les mêmes positions physiques ; les lettres affichées correspondent au profil choisi. Les flèches restent des commandes secondaires des directions. Haut/bas n’ajoute aucun déplacement vertical libre. Les clics déclenchent le combat existant : mêlée et projectiles suivent l’orientation du personnage, sans visée au curseur. Les actions spéciale/impact sont réservées dans InputMap mais n’ont pas encore de consommateur de gameplay ; le menu les indique « planned ».

## Menus et personnalisation

- Survol et clic gauche sélectionnent/valident les choix disponibles ; les cartes de récompense utilisent la même navigation. Les clics hors des choix ne valident rien.
- Les commandes de direction, interaction et retour suivent le profil ; flèches, Entrée et Échap restent des commandes de secours dans les menus. La souris reste visible.
- **Change bindings** présente deux pages. Choisir une action puis presser une touche physique ou un bouton de souris. Échap annule la capture ; la pause dispose aussi d’un choix **Use Escape**.
- Les conflits entre actions sont refusés et affichés. Une réattribution remplace les entrées de l’action sélectionnée et active le profil personnalisé. Les boutons latéraux sont facultatifs. La molette peut être attribuée aux actions ponctuelles, pas aux attaques maintenues. Les combinaisons de touches avec modificateur ne sont pas proposées.
- **Restore profile defaults** restaure le profil courant ; depuis personnalisé, revient au profil de base. Un profil personnalisé est conservé lors d’un choix temporaire d’AZERTY/QWERTY/classique, jusqu’à une restauration explicite.
- Les aides de déplacement, combat, interactions, dialogue et coffre affichent les attributions courantes. Après fermeture d’une modale, les commandes d’action et les boutons de souris doivent être relâchés avant le retour du contrôle joueur. L’entrée d’ouverture ne peut pas valider dans la même frame.

## Stockage

`Controls` est un autoload séparé de `Progression`. Les réglages sont sauvegardés dans `user://controls.json` (version 1), indépendamment de la partie : démarrer une nouvelle partie ou mourir ne les réinitialise pas. Chargement validé intégralement, écriture temporaire puis remplacement ; un échec d’écriture conserve le profil et InputMap précédents. Un fichier illisible n’est pas écrasé au démarrage ; une modification explicite des réglages peut le remplacer. Le menu affiche les erreurs de stockage.

Les pilotes `--script` ne chargent ni n’écrivent les préférences réelles par défaut. Les tests de persistance activent explicitement le stockage sur des chemins isolés.
