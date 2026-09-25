# Milady's Knight — Runs Journal

## Rôle

Historique factuel des runs exécutées.

Ce fichier sert à conserver :

- ce qui a réellement été modifié ;
- ce qui a été testé ;
- les bugs détectés ;
- les corrections appliquées ;
- les limitations restantes ;
- les modifications humaines importantes observées entre deux runs.

Il ne remplace ni `runs-workflow.md`, ni `learning.md`, ni `docs/`.

`runs-journal.md` conserve les preuves d'exécution.
`learning.md` explique à l'humain comment l'implémentation fonctionne et ce qu'il peut en apprendre.

Les entrées sont ajoutées chronologiquement et ne doivent pas être réécrites pour modifier l'historique.
Une attente en `VERIFY` peut être consignée, puis complétée par un suivi daté lors de la décision ou de la clôture.

---

## Modèle d'entrée

```markdown
## RUN-XXX — Titre

**Version-cible :** 0.x.x
**Date :** YYYY-MM-DD
**Statut constaté :** VERIFY / DONE / BLOCKED / CANCELLED
**Git (facultatif) :** branche ; commit local vérifié ; lien de PR si autorisée et créée.

### État initial observé
- ...
- ...

### Modifications humaines détectées depuis la run précédente
- aucune
- ou description courte des changements pertinents.

### Modifications réalisées
- ...
- ...

### Fichiers / scènes concernés
- ...

### Vérification
- test exécuté :
- résultat :
- bugtest :
- régressions vérifiées :
- revue Jev avant DONE (si effectuée) : commande, résultat, preuves relues et limites ; sinon motif de la revue directe.
- validation humaine (si requise) : objet, attente ou résultat reçu.

### Bugs rencontrés
- aucun
- ou description + correction.

### Documentation mise à jour
- aucune
- ou fichiers concernés.

### Learning
- `learning.md` mis à jour : oui / non
- sujets expliqués :
- fichiers, scènes ou réglages indiqués à l'humain :

### Limitations / suivi
- aucune
- ou RUN-XXX à prévoir.
```

Utiliser les critères de clôture de [runs-workflow.md](runs-workflow.md#cycle-de-vie). Les champs Git sont facultatifs : ne renseigner que les références existantes utiles pour retrouver un résultat, sans recopier le changelog Git ni anticiper le hash du commit contenant l’entrée.

---

## Journal

<!-- Ajouter les nouvelles entrées sous cette ligne. -->

## RUN-001 — Stabiliser moteur, import et commandes de vérification

**Version-cible :** 0.1.0
**Date :** 2026-09-22
**Statut constaté :** VERIFY — contrôles automatisés terminés ; F5/fermeture et revue humaine en attente.
**Git :** `feature/run-001-engine-import`, créée depuis `develop` à `04f1f05`. Aucun push, PR ou merge effectué.

### État initial et changements humains

Working tree propre au démarrage. Les commits humains `83c4722` et `04f1f05` fixent la documentation, les bibliothèques locales d’assets et le workflow `feature/* → develop → main` ; ces règles sont préservées. Le projet et le TileSet remaniés par l’humain restent la référence. Les lanceurs utilisaient encore 4.5.1, alors que le projet déclarait 4.7 et que le moteur Windows disponible était 4.7.2.

### Cause démontrée et correction

L’import Windows 4.7.2 retourne 0 avec trois erreurs `p_position > length`, aussi bien sur chemin UNC que sur NTFS local. Dans des projets minimaux séparés, `coin.wav`, `jump.wav` et `tap.wav` produisent chacun une erreur ; `hurt.wav` n’en produit aucune. Les trois premiers ont un bloc `data` impair sans octet final de remplissage.

L’ajout de cet octet et l’ajustement de la taille RIFF suppriment les erreurs. Les paramètres audio et tous les échantillons PCM restent identiques ; aucun réencodage. Cette correction respecte la [structure RIFF documentée par Microsoft](https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff-).

Les originaux sont conservés byte pour byte dans `assets/source/sounds/`, sous `.gdignore`. Les variantes corrigées gardent les chemins utilisés par les scènes dans `assets/sounds/`. Cela ne résout pas la provenance/licence encore à établir en RUN-002.

| Original conservé | Taille source → compatible | SHA-256 source |
| --- | --- | --- |
| coin.wav | 8785 → 8786 | `caa932c06548047f678e09226d910b7ed1382f927196b44a0f6da55583e2e56d` |
| jump.wav | 4059 → 4060 | `fd545eaa7e89360d08fe95d995747ae53a8159e26ec1b14cdb16b8239d08f0ab` |
| tap.wav | 1565 → 1566 | `3ca3241c3b3a5dc81b228a557c7cfc5af8a59544b2388b331d258a4fbe439659` |

### Commandes et isolation

- `tools/godot-version.txt` fixe **4.7.2**. `tools/run.sh` et `Lancer-Windows.cmd` refusent une version différente ; le lanceur Bash convertit les chemins lors d’un appel Windows depuis WSL.
- `tools/test.sh` crée un profil unique dès l’import : variables XDG pour Linux ; `APPDATA` et `LOCALAPPDATA` sur NTFS pour Windows, transmises par WSLENV. `tests/user_data_path.gd` vérifie le chemin réellement utilisé par Godot. Le profil est supprimé après succès, conservé après échec ; logs toujours conservés.
- Préflight des dépendances, délais bornés et contrôle des logs. Un marqueur `RESULT …; 0 failures` est requis ; `movement.gd` et `physics.gd` reçoivent leurs compteurs/marqueurs manquants, sans modifier leurs assertions.

### Vérification exécutée

Les suites ont été lancées depuis deux copies propres du working tree, sans `.godot/` initial, avec le même moteur Windows `4.7.2.stable.official.ed1daf0bf` :

```bash
GODOT_BIN='/mnt/c/Users/allen/OneDrive/Documents/Godot Engine/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh
python3 tests/wav_import.py
bash -n tools/run.sh tools/test.sh
```

| Vérification | Résultat |
| --- | --- |
| Import puis suites sur copie WSL/UNC | 0 erreur ; 150 PASS jeu + 1 PASS isolation, 12 marqueurs de fin, code 0. |
| Import puis suites sur copie Windows locale | Même résultat ; `user://` résolu dans le profil NTFS temporaire attendu. |
| Anciennes sauvegardes réelles avant/après | Windows : empreinte identique ; Linux : toujours absente. |
| WAV | 4 conteneurs alignés ; paramètres et PCM des 3 variantes identiques aux originaux. |
| Lanceur Windows réel | 4.7.2 accepté, 4.5.1 et exécutable absent refusés ; chemin par défaut testé. |
| Runner avec faux moteur isolé | Succès normal accepté ; mauvaise version, erreur d’import avec code 0, erreur de suite, FAIL, RESULT absent, code 7, timeout et dépendance `rg` absente refusés. Le timeout simulé est ramené à 1 s dans le banc d’essai, sans changer les délais du runner. |
| Fermeture graphique par `tests/close_window.gd` | Code 0, sans erreur ni fuite dans le log ; rendu OpenGL/NVIDIA initialisé. |
| Syntaxe shell et diff | Vérifiés, sans erreur. |

### Limites et validation restante

- Le démarrage graphique de la scène principale avec arrêt forcé `--quit-after 120` a produit des avertissements de fuite et deux ressources encore utilisées à la sortie. Ce mode ne passe pas par la notification de fermeture temporisée du niveau ; il n’est **pas** compté comme fermeture validée. La notification normale a ensuite été testée sans erreur. F5 et fermeture effective restent à confirmer dans l’éditeur.
- Computer Use a échoué avant initialisation avec `failed to launch codex app-server … os error 3`, y compris après réinitialisation et à la reprise. Une copie Windows locale a été ouverte dans l’éditeur 4.7.2 avec profil isolé ; le contrôle F5/fermeture a été demandé à l’humain. Aucun résultat humain n’est présumé.
- Le binaire Linux 4.7.2 n’est pas installé ici : aucune validation de ce moteur natif revendiquée. Le runner Linux a ses garde-fous exercés avec un faux moteur ; le moteur de production réellement testé est Windows 4.7.2.
- Push, PR vers `develop` et merge attendent l’autorisation humaine. RUN-002 n’est pas lancée.

Preuves locales regroupées dans `work/test-results/RUN-001/` (ignoré par Git) : reproductions, imports corrigés, logs complets `unc/` et `windows-local/`, essais du runner et sauvegardes. Les chemins temporaires et logs locaux ne remplacent pas ce résumé durable.

### Documentation et learning

README et état vérifié du brief actualisés ; roadmap passée en VERIFY. Entrée RUN-001 ajoutée dans `learning.md` : version du moteur, source/dérivé audio, cache d’import, isolation de `user://` et différence entre code de sortie et test terminé. Aucun script de gameplay, scène, réglage de `project.godot` ou TileSet modifié.

### Suivi du 22 septembre 2026 — validation humaine de F5

Après le commit local `f358643`, l’humain confirme : « oui fonctionne avec F5 ». Le lancement depuis l’éditeur est donc validé. Ce retour ne précise pas la fermeture manuelle du jeu et de l’éditeur ; seul le test automatique de notification de fermeture est déjà établi.

RUN-001 reste en **VERIFY**, en attente de cette confirmation et de la revue finale. README, brief et workflow reflètent ce retour ; aucune nouvelle implémentation ni entrée d’apprentissage nécessaire. Vérification de cette mise à jour limitée au diff documentaire ; les tests moteur ne sont pas relancés. Aucun push, PR, merge ou lancement de RUN-002 effectué.

### Suivi du 23 septembre 2026 — fermeture et revue finale

L’humain confirme : « Je confirme bien la fermeture manuelle du jeu et de l’éditeur. F5 fonctionne et fermeture aussi. » Les deux contrôles manuels requis par RUN-001 sont donc satisfaits. La revue finale constate un arbre propre avant cette mise à jour, un diff `develop...HEAD` sans erreur de whitespace et le périmètre attendu : lanceurs, tests, trois WAV normalisés et originaux préservés, documentation ; `AGENTS.md` porte un commit humain supplémentaire `e05aacc`, conservé tel quel. Les preuves des deux imports et des 11 suites figurent plus haut ; aucun nouveau test moteur n’est nécessaire pour cette mise à jour documentaire.

**Décision d’intégration :** PR de `feature/run-001-engine-import` vers `develop`, conformément au Git Flow ; push, création de PR et merge nécessitent encore l’autorisation humaine. RUN-001 reste en VERIFY jusqu’à l’intégration. RUN-002 est autorisée par la demande du 23 septembre et commence par un inventaire documentaire indépendant sur une branche dédiée.

## RUN-002 — Inventorier les sources et définir les livrables visuels/sonores

**Version-cible :** 0.1.0
**Date :** 2026-09-23
**Statut constaté :** ACTIVE — inventaire et matrice réalisés, traçabilité des sources en cours.
**Git :** `feature/run-002-asset-inventory` créée depuis `develop` à `04f1f05`, premier checkpoint `4c13259`, puis intégration locale de `feature/run-001-engine-import`. PR RUN-001 [#1](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/1) ouverte vers `develop`, non mergée à cette date.

### État vérifié et travail effectué

Le dépôt comporte 12 médias de jeu : six PNG, quatre WAV, un OGG et une police TTF. Onze ont une référence `res://` trouvée dans les scènes/scripts ou la ressource TileSet inspectés ; `assets/sprites/platforms.png` est présent sans référence trouvée. Les scènes définissent des animations par sprites pour le joueur (idle/run/jump/dead), les Slimes Green/Purple et la pièce ; cela ne prouve pas que les animations cible de la démo soient déjà réalisées. Les trois WAV originaux conservés par RUN-001 s'ajoutent comme sources archivées, pas comme médias de jeu distincts.

Les docs/11 et 12 listent chaque média présent, son usage vérifié et l'état de preuve de provenance/licence. Docs/13 relie les ensembles, animations et VFX nécessaires aux jalons 0.1.0–0.9.0. Aucune licence n'est attribuée sur la base d'un nom de pack ou du marqueur `Free`. Recherche ciblée dans la bibliothèque locale indiquée par `.local/asset-paths.md` : aucun nom de fichier exact correspondant aux médias de jeu parmi les résultats ; deux fichiers `license.txt` trouvés dans des packs d'inspiration, sans lien démontré avec les médias intégrés. Les empreintes SHA-256 des 12 médias ont été calculées pour faciliter une comparaison de source ; les dimensions PNG et formats audio ont été vérifiés. La recherche ne démontre pas l'absence de copies renommées.

**Validation restante :** rattacher les justificatifs que l'humain dit posséder aux fichiers exacts, ou identifier les remplacements nécessaires ; contrôler chaque licence, ses obligations d'attribution et le pipeline source → dérivé ; relire les tableaux. Aucun achat, déplacement massif, édition de bibliothèque externe, changement gameplay ou test moteur effectué pendant cette phase documentaire.

### Suivi du 23 septembre 2026 — intégration de RUN-001

La [PR #1](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/1) est passée à `MERGED` sur GitHub le 23 septembre 2026 à 13:52:30 UTC, commit de merge `9f4ecab832154f55a15fe60062d80d0af80512c6` dans `develop` (vérifié par `gh pr view` et `git ls-remote`). L'humain a validé F5 et la fermeture, les vérifications techniques et la revue finale sont satisfaisantes : RUN-001 passe à **DONE**. RUN-002 continue sur sa branche dédiée ; aucune nouvelle run lancée.

### Suivi du 23 septembre 2026 — besoins audio et vérification documentaire

Les familles audio de docs/08 sont attribuées aux jalons 0.1.0–0.9.0 dans docs/12, en complément de la matrice visuelle de docs/13. Les 12 fichiers de jeu recensés existent, les liens relatifs de docs/11–13 pointent vers des fichiers présents, et `git diff --check` ne signale pas d'erreur. Cette vérification porte sur la documentation ; aucune suite Godot n'a été relancée, aucun asset externe intégré. La traçabilité licence/source attend toujours l'emplacement des justificatifs annoncés par l'humain.

### Suivi du 23 septembre 2026 — conditions déclarées et sources candidates

L'humain confirme que les licences de ses assets sont accessibles par leurs liens sources et transmet des conditions autorisant l'usage et la modification dans les jeux personnels/commerciaux, interdisant la redistribution/revente/remise en ligne des assets modifiés ou non, avec crédit facultatif. Ces conditions ont été vérifiées sur les pages officielles des deux packs Zerie candidats (docs/11) ; elles ne prouvent pas leur emploi dans le prototype ni les conditions propres aux autres sources. La page de l'auteur Pixel Operator liste `PixelOperator8.ttf` sous CC0 1.0 pour sa version 2018.10.04-1, mais la version exacte du fichier du dépôt n'est pas encore établie. Une comparaison par taille et SHA-256 des 12 médias du jeu avec la bibliothèque externe déclarée n'a trouvé aucune copie identique ; cela n'exclut pas les dérivés. Les liens sources correspondant aux fichiers du prototype ont été demandés à l'humain. Le dépôt étant public, le partage direct de fichiers issus d'un pack « sans redistribution » devra être examiné une fois la correspondance établie. RUN-002 reste **ACTIVE** ; aucun gameplay ni asset modifié.

### Suivi du 23 septembre 2026 — décision humaine et vérification finale locale

L'humain précise que les licences des packs qu'il utilise ont les mêmes principes malgré des formulations différentes, mais qu'il n'a pas de dossier de justificatifs ni de correspondance par fichier. Il demande d'ignorer ce rattachement pour l'instant. Cette décision remplace la recherche de provenance fichier par fichier dans les critères immédiats de RUN-002 ; elle ne transforme pas les déclarations de licence en preuves pour les médias actuels. La correspondance et les conditions de partage des assets retenus sont reportées à leur intégration et à la recette des crédits/licences avant distribution, déjà prévue dans le jalon 0.8.0–0.9.0.

L'inventaire des 12 médias, leurs références, les lacunes signalées et les besoins audio/visuels/animations/VFX par jalon sont consignés dans docs/11–13. Le cycle source conservée → dérivé de jeu est décrit sans déplacement d'asset. Relecture des tableaux, liens internes, références de fichiers et `git diff --check` effectuée sur la branche ; aucun test moteur requis pour ces seules modifications documentaires. **RUN-002 passe en VERIFY local** pour revue et intégration de la branche selon le workflow Git. RUN-003 n'est pas lancée.

### Suivi du 23 septembre 2026 — fusion de RUN-002 et catalogues locaux

L'humain confirme la revue de RUN-002 et autorise le push et la PR. La [PR #2](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/2) est vérifiée fusionnée dans `develop` au commit `1d176db30becce582e99ed01880625ab3b1d8c81` ; RUN-002 passe à **DONE**. L'humain demande ensuite d'ignorer par Git les catalogues 11 et 12. Les fichiers sont retirés de l'index sans suppression locale sur une branche documentaire distincte ; les références de l'index des docs signalent leur caractère facultatif pour les nouveaux clones. RUN-003 reste BACKLOG et n'est pas lancée.

## RUN-003 — Comparer l'échelle sur un échantillon représentatif

**Date :** 2026-09-23 · **Statut : ACTIVE** · **Branche :** `feature/run-003-scale-comparison`, créée depuis `origin/develop` à `fb13745` après avance rapide de la branche locale `develop`.

Inspection : le slice existant repose sur des cellules 16×16 et un rendu 320×180 ; aucune scène N1 conçue à la main, aucun sprite humanoïde et aucun coffre intégrés. Le joueur a une frame 32×32 mais seulement 13×19 pixels opaques sur la frame de repos mesurée ; le Slime a une frame 24×24 et 14×12 pixels opaques. Les collisions inspectées sont documentées dans `docs/RUN-003_SCALE_COMPARISON.md`.

Une scène d'essai isolée avec sélection 16/32, silhouettes provisoires et contours de collision a été produite. Godot Windows **4.7.2** a importé le projet sans erreur (code 0), puis lancé `tools/capture_scale_comparison.gd` en mode graphique et écrit deux images 640×360 (`docs/media/`, résultats `save_png=0`). Les deux images ont été ouvertes et comparées visuellement. Le premier essai en mode `--headless` n'a pas rendu de texture (moteur factice) ; le mode graphique a corrigé ce problème. La grille réelle, le viewport du jeu, les niveaux et les collisions de gameplay sont inchangés.

L'essai 32 agrandit les sprites actuels sans ajouter de détail source ; l'humanoïde et le coffre restent des maquettes. Une décision humaine explicite sur la grille et un échantillon d'assets représentatif sont attendus avant de valider la direction et de passer en VERIFY. L'hypothèse 16×16 de l'art bible reste en vigueur. Aucun test de gameplay 32 n'est revendiqué.

### Décision humaine du 23 septembre 2026 et passage en VERIFY

L'humain retient explicitement la grille **16×16**, conforme à l'art bible, et demande de réévaluer la taille opaque des personnages et leurs collisions lors de l'intégration de leurs véritables assets. La maquette 32 ne comporte pas de nouveaux détails source et les éléments N1/humanoïde/coffre finaux restent absents ; ces limites sont conservées dans le compte rendu. La décision est reportée dans docs/06, docs/13, le workflow et le learning. `docs/media/.gdignore` évite l'import inutile des captures par Godot ; un nouvel import sous Godot Windows 4.7.2 s'est terminé avec code 0 et sans erreur, sans régénérer leurs fichiers `.import`. `git diff --check` est passé. À l'autorisation humaine, la branche a été poussée et la [PR #4](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/4) est ouverte vers `develop`. RUN-003 reste en VERIFY jusqu'à la revue humaine et à l'intégration ; aucun merge n'est présumé.

### Clôture du 23 septembre 2026

L'humain confirme que RUN-003 est vérifiée et la PR fusionnée. `git fetch origin` montre la [PR #4](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/4) fusionnée dans `origin/develop` au commit `1b99bb4`. RUN-003 passe à **DONE** ; sa décision de grille 16×16 et la réévaluation ultérieure des silhouettes/collisions sont conservées.

## RUN-004 — Résolution et cadrage du prototype

**Date :** 2026-09-23 · **Statut : VERIFY local** · **Branche :** `feature/run-004-resolution-camera`, créée depuis `origin/develop` à `1b99bb4` avec un arbre propre. Aucun push ni PR effectué.

### Changement réalisé

- `project.godot` passe le viewport de 320×180 à **640×360** ; la fenêtre initiale 1280×720, le stretch `viewport`/`integer`, le filtrage nearest et le pixel snapping restent actifs. Aucun niveau, coordonnée ni collision n'est redimensionné.
- Le HUD conserve ses informations, mais ses bandeaux, le hint et l'overlay suivent désormais les bords du viewport. Police de 12 px pour les informations courantes, 16 px pour le titre d'overlay ; la pause s'ancre à droite. Les captures de départ, pause, mort et victoire sont conservées dans `docs/media/run-004-*.png`.
- La caméra réutilisable du joueur ne porte plus les limites et offsets propres au slice. `scripts/level.gd` définit les limites `(0, -224, 2240, 304)`, l'offset `(32, -38)` et le smoothing `7` pour le niveau existant. La transition locale à `-54` lors de l'escalade est supprimée : à 640×360 elle déplaçait le cadre de 16 px sans apporter de visibilité utile au sommet. La caméra calcule désormais son suivi au tick physique, comme le joueur.

### Vérification exécutée

Le runner `GODOT_BIN=...Godot_v4.7.2-stable_win64_console.exe ./tools/test.sh` a importé le projet sans erreur, puis réussi **150 contrôles de jeu et 1 contrôle d'isolation `user://`**, 11 suites, code 0, sur la version finale. Logs : `work/test-results/run-bl4nYu5Z/` (local, ignoré par Git). Un premier passage avant la correction du suivi avait également réussi ; la version finale est celle de ce second passage. Les parcours hauts/bas et retours exercés par les suites couvrent sol, double saut, mur, bac, combat, chute, limites et sortie ; les tests clavier couvrent pause et reprise.

Un contrôle graphique indépendant sous **Godot Windows 4.7.2**, OpenGL, a inspecté les captures 640×360 du HUD, de la pause, de la mort et de la victoire : textes et bandeaux non découpés, y compris une réserve bonus maximale. Le rendu a été contrôlé aux fenêtres **640×360 (×1), 1280×720 (×2), 1920×1080 (×3) et 1500×1000 (×2)** ; pour cette dernière, la transform mesurée centre le viewport avec 110 px de bande de chaque côté et 140 px en haut/bas. Les dimensions du viewport et les rectangles du HUD restent 640×360. Captures persistantes dans `docs/media/`, logs graphiques locaux dans `/tmp/milady-472-physics.log` et `/tmp/milady-472-size.log`.

Le subagent a comparé le suivi au sol sur des ticks réels : l'ancien callback de rendu alternait des déplacements de caméra d'environ 1,2/2,4 px pour une marche régulière de 1,75 px/tick ; le callback physique de la version finale progresse régulièrement vers 1,75 px/tick, sans cette oscillation. Le cadrage de départ, du sommet, du bac, de la voie basse et de la fin reste dans les limites du décor. La transition `-54` supprimée ne modifie plus l'image lors du franchissement de sa zone. `git diff --check` et la revue du périmètre ne signalent aucune anomalie.

**Limites :** les captures pause/victoire proviennent d'une fixture qui appelle `set_overlay`, alors que la mort appelle `player.die()` ; les interactions de pause et de sortie sont couvertes séparément par les suites. Les captures de viewport n'incluent pas les bandes physiques des fenêtres hors ratio ; celles-ci sont établies par la transform runtime. Les scripts graphiques temporaires ont produit des avertissements de ressources à la fermeture de leur fixture, sans erreur de chargement ni de rendu. Une revue humaine du résultat local et l'autorisation Git sont encore attendues pour l'intégration ; RUN-005 n'est pas lancée.

### Suivi du 24 septembre 2026 — revue rétrospective et clôture

L'humain confirme que les vérifications manuelles de RUN-004 ont été validées. La [PR #5](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/5) est vérifiée fusionnée dans `origin/develop` au commit `846137d42e98dc7bc8f32df65d4f8e1faeb446a1` le 23 septembre 2026 à 16:09:41 UTC. Les contrôles techniques et graphiques, leurs limites et l'entrée de `learning.md` figurent ci-dessus ; aucun test Godot n'a été relancé pour cette clôture documentaire. RUN-004 passe à **DONE**. RUN-005 reste BACKLOG.

Le Run Completion Reviewer Jev est testé après fusion, à titre rétrospectif, avec `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py` et deux dossiers JSON locaux de preuves conservés dans `work/test-results/jev-review-2026-09-24/` (ignoré par Git). RUN-003 avait déjà sa clôture et son learning dans `origin/develop` ; son dossier a déclenché un appel réel à `jev-1.13.0` avec des probabilités de 0,13 à 0,80 selon l'item. RUN-004 a d'abord été refusée localement (`not_ready`, `api_called: false`) parce que sa clôture manquait dans ce journal. Après cette mise à jour, le même dossier a déclenché un appel réel à `jev-1.13.0` avec des probabilités de 0,13 à 0,61. Les deux réponses demandent `inspect_evidence_reviews`. Ces sorties montrent le fonctionnement des contrôles, pas une nouvelle vérification du gameplay ; les probabilités demandent une relecture humaine et ne constituent pas un seuil de décision. Les déclarations de tests anciens sont confrontées aux comptes rendus existants, sans prétendre avoir relancé Godot.

## Tooling Jev V1 — vérification du 24 septembre 2026

Sur `feature/jev-run-completion-reviewer-v1`, le nouveau reviewer a été exécuté avec `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py <dossier> --json` et `jev-1.13.0`. Résultats détaillés locaux, ignorés par Git : `work/test-results/jev-review-2026-09-24/*-v1-result.json`. Les quatre décisions sont données ici dans l'ordre couverture / vérifications / blocage / statut, les trois premiers nombres étant des probabilités de **oui**. RUN-003 rétrospective : 0,86 / 0,55 / 0,17 / `READY_FOR_DONE` (confiance 0,64). RUN-004 rétrospective : 0,82 / 0,68 / 0,25 / `READY_FOR_DONE` (confiance 0,56). Ces résultats n'ont pas changé leurs statuts historiques ; aucun test Godot n'a été relancé.

Essais synthétiques : un dossier avec échec obligatoire explicitement non résolu a reçu `BLOCKED` (confiance 1,00 ; probabilité de blocage 0,92) ; un dossier aux preuves ambiguës a reçu `VERIFY` (confiance 0,63 ; probabilité de blocage 0,58). Un autre dossier décrivant des contrôles non confirmés a reçu `BLOCKED` (confiance 0,65). Ces variations montrent qu'il faut lire les quatre décisions et les preuves, pas uniquement le `Choice`. Le précontrôle a refusé l'exemple en attente sans appel API ; les dossiers RUN-003/004 restent compatibles. Les contrôles Python ont couvert statut proposé invalide, blocage déclaré, statut JSON mal typé, panne API simulée (`review_unavailable`) et rendu terminal ; ils ont réussi. `git diff --check` a réussi. Jev n'a ni exécuté les tests décrits ni décidé d'un passage à `DONE` ; la sortie exige toujours l'inspection humaine des preuves.

## RUN-005 — Actions clavier de production

**Date :** 2026-09-25 · **Statut : VERIFY local** · **Branche :** `feature/run-005-production-keyboard`, créée depuis `develop` avec arbre propre. RUN-001 à RUN-004 étaient DONE ; aucune modification humaine non commise à préserver.

### Changement et limites

- L'Input Map emploie les quatre flèches à la place de Q/D/Z/S. Space, E, F et Escape gardent leur rôle ; G, R et A ont chacun une action logique distincte, sans capacité nouvelle. L'action `restart` liée à R est retirée. F répète une frappe après la récupération de 0,32 s tant que la touche reste enfoncée ; chaque frappe conserve sa fenêtre de hit et la protection contre les hits multiples par cible.
- Le niveau réserve E à la confirmation des overlays de mort et de victoire finale. La pause reste reprise par Escape ; le portail requiert une nouvelle pression de E après la pause. Il n'y a plus de redémarrage volontaire en cours de tentative avant le futur menu de pause. Les textes du niveau et le README ont été alignés. Aucun support souris/manette, dialogue, équipement ou nouvelle attaque n'a été ajouté.
- `tests/keyboard.gd` envoie de vrais `InputEventKey` et couvre les anciennes touches inactives, la répétition F, G/R/A, le portail pendant et après pause, R pendant le jeu/mort/victoire, E après mort/victoire. Les tests de bonus et d'intégration passent par la nouvelle confirmation E. La reprise sur mort et l'écriture du bonus sont vérifiées par ces suites.

### Vérification exécutée

`GODOT_EXE='…/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` : import propre, contrôle d'isolation `user://` et **11 suites / 164 contrôles de jeu réussis**, code 0. Logs finaux : `work/test-results/run-raKjXA4N/` ; résumé local : `work/test-results/run-005-final-suite.log`. Les parcours hauts/bas et retours ont réussi ; les interactions pause, portail, mort, victoire et sauvegarde ont été exercées en Godot. `tests/visual.gd` a aussi produit les captures graphiques dans `work/` (code 0, log `work/test-results/run-005-visual.log`) : le hint d'accueil et l'overlay de mort avec E ont été inspectés, sans découpage visible. `git diff --check` a réussi.

Premier essai sans `GODOT_EXE` : binaire introuvable, aucun test lancé. Un essai intermédiaire a atteint 39 contrôles bonus puis a expiré : après la confirmation E, la fixture conservait une référence à l'ancien niveau libéré par la transition. Le test a été corrigé pour reprendre `current_scene` ; la suite complète finale est passée. Aucun échec résiduel. Le texte de victoire modifié n'a pas été recapturé ; son interaction est couverte par les tests et le changement R → E n'allonge pas sa ligne. Aucun push, PR ni fusion ; RUN-006 n'est pas lancée.

### Revue Jev et état de sortie

Dossier local `work/test-results/RUN-005/review.json` relu contre les logs, le diff et les captures ; commande `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-005/review.json --json`, sortie `work/test-results/RUN-005/review-result.json`. Jev 1.13.0 : couverture **0,85**, vérifications **0,77**, blocage **0,43** (probabilités de oui), choix **VERIFY** (confiance **0,28** ; READY_FOR_DONE 0,29, BLOCKED 0,19, VERIFY 0,52). La revue directe retrouve les 164 contrôles et l'isolation réussis, les interactions clavier réelles et aucun blocage technique résiduel. Le choix prudent de Jev ne vaut ni échec de test ni validation humaine ; RUN-005 demeure en VERIFY local pour revue de branche. Le push et la PR nécessitent l'autorisation humaine prévue par AGENTS.md ; ils n'ont pas été effectués.

### Suivi du 25 septembre 2026 — réactivité validée pour implémentation

L'humain confirme avoir vérifié et validé le premier changement, puis signale un délai perceptible avec F maintenu et l'alternance des flèches. Analyse dans `scripts/player.gd` : l'accélération 1100 px/s² imposait environ 0,19 s pour inverser la vitesse de −105 à +105 px/s ; `facing` restait figé pendant tout le cycle de frappe de 0,32 s. La première frappe partait immédiatement, mais la zone de contact commençait après environ 0,07 s. L'humain valide explicitement la proposition d'accélération 2100 px/s², de rotation hors de la fenêtre de contact et d'un cycle F de 0,28 s, en précisant que la cadence sera réévaluée avec l'ATK SPEED des armes.

Le cycle de l'épée passe à 0,28 s, avec préparation/contact/récupération proportionnels à l'ancien cycle. `attack_facing` fixe la direction du coup pendant le contact ; le personnage peut se tourner pendant la préparation et la récupération. L'accélération horizontale passe à 2100 px/s² ; les restrictions de recul et de contrôle mural restent en place. Le helper de combat relâche désormais F avant la répétition automatique afin de tester une frappe à la fois. Deux tests exercent un changement de côté au cours de F maintenu, l'absence de hit sur les deux côtés pendant la même frappe et la direction correcte de la suivante.

`GODOT_EXE='…/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` : import, isolation `user://`, **11 suites et 170 contrôles de jeu réussis**, code 0. Logs finaux : `work/test-results/run-AEWqf6hc/` ; résumé `work/test-results/run-005-control-response.log`. Le premier essai du nouveau test clavier attendait à tort la pleine vitesse droite après quatre ticks alors que le joueur arrivait à pleine vitesse gauche ; six ticks sont nécessaires pour inverser totalement à 2100 px/s². Cette attente a été corrigée et la suite finale passe. Le test clavier vérifie aussi le passage par zéro en trois ticks et la nouvelle frappe F dans les 18 premiers ticks. Ces mesures de test ne remplacent pas l'appréciation humaine de la sensation de jeu. RUN-005 reste en VERIFY local ; aucun push ni PR.

Revue Jev mise à jour sur le dossier `work/test-results/RUN-005/review.json` après les nouveaux tests ; résultat `work/test-results/RUN-005/review-response-result.json`. Jev 1.13.0 : couverture 0,85, vérifications 0,79, blocage 0,54 (probabilités de oui) ; choix VERIFY, confiance 0,31 (READY_FOR_DONE 0,29, VERIFY 0,54, BLOCKED 0,17). Inspection des preuves originales : aucun test final en échec, aucune contradiction observée dans le diff ; le choix VERIFY est conservé pour la revue de sensation de jeu et l'intégration de la branche. Ces probabilités ne prouvent ni n'infirment la jouabilité ; Jev n'a pas exécuté Godot.

### Validation humaine et autorisation Git du 25 septembre 2026

L'humain confirme : « Ressenti vérifié OK validé pour l'instant. Run validé, ok pour push et PR. » Le réglage de réactivité de RUN-005 satisfait donc la validation de sensation de jeu demandée après l'ajustement. Le push de `feature/run-005-production-keyboard` et la création d'une PR vers `develop` sont autorisés ; aucune autorisation de fusion n'est inférée. La branche reste en VERIFY pendant la revue et l'intégration Git. La cadence F de 0,28 s est provisoire, à réévaluer avec l'ATK SPEED des armes.

### Livraison Git du 25 septembre 2026

`git fetch origin develop` confirme que la branche RUN-005 est issue de `origin/develop` sans commit divergent (`0` derrière, `2` devant avant le commit de validation) ; `git diff origin/develop...HEAD --check` passe. Le commit `8e7420c` consigne la validation humaine. La branche `feature/run-005-production-keyboard` est poussée sur `origin` et la [PR #8](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/8) est ouverte vers `develop`. `gh pr view` la rapporte `OPEN`, base `develop`, `MERGEABLE`, sans décision de revue ni contrôle CI déclaré au moment de l'inspection. Aucune fusion effectuée ; RUN-005 reste en VERIFY. Cette mise à jour documentaire ne modifie pas le jeu et ne nécessite pas de relancer Godot.

### Fusion et clôture du 25 septembre 2026

L'humain confirme la fusion et que son `develop` local est à jour avec `origin`. Vérification Git : `develop` propre au commit `95ec7f9`, identique à `origin/develop` ; la PR #8 est `MERGED` le 25 septembre 2026 à 14:19:48 UTC, commit de fusion `95ec7f940abb67a4093bcfb63af7c5634666ea4f`. La validation du ressenti et les contrôles requis étaient déjà consignés ci-dessus. RUN-005 passe à **DONE** ; RUN-006 peut démarrer depuis cette base.

## RUN-006 — Santé fractionnaire et réactions aux dégâts

### Démarrage et décision produit du 25 septembre 2026

Branche `feature/run-006-fractional-health` créée depuis `develop` propre à `95ec7f9`. Les scènes et scripts réels du joueur, du Slime, des ronces, de la fosse et du HUD ont été inspectés avant édition. La spécification ne définissait pas la réaction à une flamme qui blesse le joueur ; l'humain a choisi explicitement « Piège : invulnérabilité + recul ». La flamme infligeant 0,2 DMG aux ennemis est un cas distinct. Les nouveaux profils projectile, flamme et swarm sont exercés dans une fixture sans ajouter d'ennemis ou d'armes à cette run.

### Réalisation et essais locaux

`HealthUnits` convertit les HP en dixièmes entiers pour éviter les pertes par conversion en entier de HP ; les API et signaux du joueur et du Slime exposent des valeurs fractionnaires. Le joueur conserve une borne de 0 à MAX HP, un soin borné et une mort unique. Le HUD affiche la valeur exacte ; les cœurs sont arrondis vers le demi-cœur supérieur. Le contrat de dégâts distingue contact/mêlée (invulnérabilité, hit-stun, recul, interruption), projectile (invulnérabilité, interruption), piège et flamme (invulnérabilité, recul), swarm (invulnérabilité) et vide (mort malgré l'invulnérabilité). Le contact réel du Slime et les ronces existantes utilisent leur profil ; la fosse utilise le vide. F reste bloqué pendant le hit-stun et Space pendant le recul, y compris au mur et à l'atterrissage. Les durées initiales sont 0,85 s d'invulnérabilité, 0,18 s de hit-stun et 0,16 s de recul ; leur ressenti reste à confirmer.

Godot Windows 4.7.2 avec `GODOT_EXE='…/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` : import, isolation `user://`, **12 suites et 242 contrôles de jeu réussis**, code 0. Logs : `work/test-results/run-VqASB9xs/`, résumé `work/test-results/run-006-suite.log`. `tests/damage_profiles.gd` ajoute 70 contrôles sur 0,5 HP, 0,2 DMG, zéro exact, soin, mort et récompense uniques, cinq profils, vide, F/Space, mur, atterrissage et contacts répétés. `tests/combat.gd` et `tests/physics.gd` vérifient aussi les réactions lors des contacts réels du Slime et des ronces. `tests/health_visual.gd` a produit trois captures graphiques locales dans `work/` ; les états plein, demi-cœur et 0,2 HP arrondi ont été inspectés sans chevauchement visible.

Un premier essai de la fixture échouait sur le compteur de mort du Slime : la variable locale capturée par une lambda n'était pas mise à jour comme attendu. Le compteur est devenu un membre de fixture et les 70 contrôles finaux passent. Le soin MAX HP futur et les attaques/ennemis encore absents ne sont pas implémentés. Les ronces actuelles sont traversables ; les pièges solides appartiennent à RUN-008. RUN-006 est en **VERIFY local** pour apprécier la sensation des durées et des réactions ; aucun push ni PR n'est autorisé pour cette run à ce stade.

### Revue Jev du 25 septembre 2026

Le dossier local `work/test-results/RUN-006/review.json` a été relu contre les logs et le diff, puis soumis via `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-006/review.json --json` ; sortie `work/test-results/RUN-006/review-result.json`. Jev 1.13.0 estime la couverture à **0,80**, les vérifications à **0,69** et la présence d'un blocage à **0,72** (probabilités de oui) ; il choisit **VERIFY** (confiance 0,38 ; READY_FOR_DONE 0,30, VERIFY 0,59, BLOCKED 0,11). La revue directe des preuves ne trouve pas d'échec final ; le signal de blocage n'identifie pas à lui seul un défaut reproductible. Le choix VERIFY est cohérent avec l'essai de sensation encore attendu pour les durées provisoires. Jev n'a pas exécuté Godot.

### Validation humaine et audit du 25 septembre 2026

L'humain confirme avoir vérifié RUN-006 et la valide. L'audit du diff contre `develop` et des trois captures HUD ne révèle pas d'autre défaut confirmé. Un cas limite est trouvé dans `scripts/player.gd` : relâcher Space pendant un recul vertical réduisait sa vitesse ascendante avec la règle de saut variable. L'humain valide explicitement le correctif ciblé et sa vérification avant édition. La règle de saut variable est désormais suspendue pendant le recul ; `tests/damage_profiles.gd` vérifie la conservation de l'impulsion. L'humain valide aussi la mise à jour des présentes preuves et du dossier local de revue.

Après le correctif, Godot Windows 4.7.2 avec `GODOT_EXE='…/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` termine avec code 0 : import sans erreur, isolation `user://`, **12 suites et 243 contrôles réussis** (dont 71 dans `damage_profiles`). Logs : `work/test-results/run-fY70meWI/`. `git diff develop...HEAD --check` passe. Les captures HUD réalisées avant ce correctif sans impact sur l'UI ont été revues pendant l'audit : 3, 2,5 et 0,2 HP sont lisibles avec les cœurs correspondants. RUN-006 reste en **VERIFY** jusqu'à la livraison Git et la fusion de la PR selon le workflow du dépôt.

Le dossier local `work/test-results/RUN-006/review.json` est actualisé avec la validation humaine et les 243 contrôles. La nouvelle invocation de Jev renvoie `review_unavailable` avant appel API, car `TYPESAFE_API_KEY` n'est pas défini dans ce shell. Les quatre décisions Jev précédentes restent celles de la passe avant validation ; elles ne sont pas présentées comme une revue des nouvelles preuves. La revue directe des logs, du diff et des captures est satisfaisante ; aucune vérification obligatoire ne reste en échec ou en attente.

### Livraison Git du 25 septembre 2026

`git fetch origin develop` confirme que la branche RUN-006 est à jour sur la base `origin/develop` (`0` derrière) ; `git diff origin/develop...HEAD --check` passe. Après le commit `397307a` du correctif validé, la branche `feature/run-006-fractional-health` est poussée sur `origin` et la [PR #9](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/9) est ouverte vers `develop`. `gh pr view` la rapporte `OPEN` et `MERGEABLE`, sans décision de revue ni contrôle CI déclaré lors de l'inspection. Aucune fusion effectuée ; RUN-006 reste en **VERIFY**. L'humain a validé l'ajout de cette note de livraison. Ce changement documentaire ne modifie pas le jeu et ne nécessite pas de relancer Godot.
