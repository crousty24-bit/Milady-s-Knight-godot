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

### Fusion et clôture du 25 septembre 2026

L'humain confirme que la PR est fusionnée, que le correctif est validé et que le ressenti a été vérifié. Les durées de 0,18 s de hit-stun et de 0,16 s de recul, notamment au contact d'un Slime et des ronces, restent provisoires ; elles devront être équilibrées ultérieurement. `git pull --ff-only origin develop` a mis le `develop` local à jour de `95ec7f9` à `2f3871e`. `gh pr view 9` confirme que la [PR #9](https://github.com/crousty24-bit/Milady-s-Knight-godot/pull/9) est `MERGED` depuis le 25 septembre 2026 à 15:42:24 UTC, avec le commit de fusion `2f3871e54494421c070746b2e5192341206a4a09`. Les 243 contrôles de jeu, l'isolation et les captures HUD sont consignés ci-dessus ; aucun test de gameplay n'a été relancé pour cette clôture documentaire. RUN-006 passe à **DONE**. RUN-007 reste en **BACKLOG** et n'a pas été lancée.


## RUN-007 — Lancement (28 septembre 2026)

Autorisation humaine « Oui » après inspection en lecture seule. Branche existante `feature/run-007-combat-sword-slimes`, ancêtre commun avec `develop` : `eeeb62c`. RUN-006 DONE. Modification humaine préexistante : `skills-lock.json` (+450 lignes), conservée et exclue des commits de la run. Skills ajoutés présents dans `.agents/skills/`. Skill `godot-gdscript-headless-testing` utilisé pour les fixtures physiques ; aucun polish spéculatif.

`git ls-files .claude` révélait `.claude/rules/visual-assets.md`, ajouté au commit `7adc3c2`. `.gitignore` contient déjà `.claude` : ignorer un chemin ne retire pas les fichiers déjà suivis. Après validation, `git rm -r --cached -- .claude` a retiré cette entrée de l’index et conservé le fichier local. Aucun changement de l’historique.

Périmètre : Sword 0,5 DMG, départs espacés de 1 s indépendamment du geste de 0,28 s et des interruptions ; Green 1 HP/0,5 DMG, Purple 2 HP/1 DMG ; recul sans immunité contact ni aux coups. RANGE en attente de décision humaine. Contrôles et résultat final à compléter après exécution.


### Implémentation et recette (28 septembre 2026)

L’humain a choisi **1 RANGE = 1 bloc = 16 px depuis la main**. La forme de lame passe de 22×4 à 16×4 px et son centre se situe à 8 px de la main ; dessin et traînée atteignent 16 px. Sword inflige 0,5 DMG. Le geste reste à 0,28 s avec ses proportions de fenêtre active, tandis qu’un compteur indépendant impose 1 s entre départs. Relâche/repression, projectile ou contact n’effacent pas ce compteur ; pause le suspend. L’air reste autorisé et le wall slide interdit le départ ou annule la fenêtre du coup en cours.

Les Slimes Green/Purple ont 1/2 HP et infligent 0,5/1 DMG au contact. Le timer de recul de 0,12 s préserve la vitesse d’impulsion puis rend la main à la patrouille ; `move_and_slide()` et la requête de contact restent exécutés pendant ce timer. Les dégâts ne sont pas refusés pendant le recul. Vitesses, sprites, limites de patrouille, signaux de récompense et terrain conservés.

**Bugtest et corrections de fixtures :** les anciennes assertions d’intégration attendaient encore 1 DMG et trois coups pour Green : premier essai complet arrêté avec 2 échecs, après les suites de combat passées. Elles ont été adaptées au contrat Sword et au délai. Le deuxième essai avec la portée validée passe combat, clavier, intégration et bonus, puis échoue aux deux parcours : le pilote restait immobile au contact pendant le nouveau cooldown et meurt à x≈1018 (haut) et x≈1144 (bas). Le pilote maintient désormais un espacement de 22–24 px et utilise les touches de déplacement pour reculer pendant la récupération, puis se réorienter au prochain geste. Aucun waypoint, état joueur/ennemi ni règle de jeu modifié pour rendre ces tests verts. Les essais ciblés routes/retours passent : 3 HP aux sorties, bonus 7/14. Les profils RUN-006 sont adaptés à 1 HP ennemi et au cooldown prioritaire après une interruption, tout en conservant les tests de sources et de saut.

**Vérification finale :** `GODOT_BIN='/mnt/c/Users/allen/OneDrive/Documents/Godot Engine/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` termine avec code 0. Godot **4.7.2.stable.official.ed1daf0bf** : import sans erreur, isolation `user://`, **12 suites / 261 contrôles de jeu, 0 échec**. Logs finaux : `work/test-results/run-7HimSa00/`, résumé `work/test-results/run-007-final-suite.log`. Les 47 contrôles combat couvrent coups uniques par cible, maintien plusieurs secondes avec impacts exactement espacés de 60 ticks, relâche/repression, direction, portée et occlusion, dégâts réels en l’air, wall slide, interruption avant impact, mort, pause, contacts Green/Purple pendant recul, impacts simultanés, mort/récompense uniques et patrouille aux bords/murs. Les 63 contrôles de profils vérifient aussi la santé fractionnaire et les réactions du joueur.

`tests/combat_visual.gd` exécuté en rendu GL Compatibility (RTX 4070 Ti), `--fixed-fps 60`, code 0 : **2 contrôles visuels réussis**, log `work/test-results/run-007-combat-visual.log`. Captures `work/run-007-sword-right.png` et `work/run-007-sword-left.png` inspectées : lame et traînée orientées du côté du Slime, flash de cible visible, HUD conservé. Ce contrôle de rendu ne remplace pas le jugement humain sur le ressenti. Les fixtures graphiques utilisent un profil temporaire isolé ; les drivers désactivent la sauvegarde réelle.

Revue statique ciblée indépendante sans défaut bloquant trouvé ; elle ne compte pas comme vérification runtime. Revue directe du diff, des logs et des captures faite par l’agent principal. `git diff --check` passe. `.claude/rules/visual-assets.md` existe toujours localement, est ignoré et `git ls-files .claude` ne retourne plus d’entrée. Les skills locaux et `skills-lock.json` humain sont préservés.

RUN-007 passe à **VERIFY** : essai humain attendu sur cadence, portée et contacts pendant recul. Dossier `work/test-results/RUN-007/review.json` préparé avec validation humaine `pending` ; aucune revue Jev de clôture n’est revendiquée avant cet essai. Aucun push, PR ni fusion ; RUN-008 non lancée.


### Révision de portée après essai humain (28 septembre 2026)

L’humain juge la portée de 16 px trop courte et demande le passage à 24 px. La conversion de mêlée devient **1 RANGE = 24 px = 1,5 bloc de terrain**, toujours mesurée depuis la main jusqu’à la pointe. La grille du terrain reste à 16 px. Le dessin utilise maintenant `SWORD_RANGE = 24.0`, et la forme de collision mesure 24×4 px, centrée à 12 px de la main. La portée augmente de 50 % ; dégâts, cadence, fenêtre active, patrouilles et pilote des parcours restent inchangés. La fixture de portée déplace ses cibles de limite à x=193/196 pour distinguer volume accessible et volume au-delà de la pointe.

État humain de départ préservé : commit `4c7438b` sur `skills-lock.json`, ajouté après le checkpoint `8e43085`. Aucun changement de ce fichier dans cette révision.

Retest : même commande `GODOT_BIN='…/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh`, Godot **4.7.2.stable.official.ed1daf0bf**, code 0 ; import, isolation `user://`, **12 suites / 261 contrôles de jeu, zéro échec**. Logs : `work/test-results/run-fiV2rgTT/`, résumé `work/test-results/run-007-range24-suite.log`. Les deux parcours et leurs retours restent réussis, sans retoucher le pilote. `tests/combat_visual.gd` en GL Compatibility termine avec code 0 et **2 contrôles visuels réussis** ; log `work/test-results/run-007-range24-visual.log`. Captures gauche/droite actualisées dans `work/run-007-sword-right.png` et `work/run-007-sword-left.png`, inspectées : lame étendue et traînée présentes du bon côté. Copies des captures précédentes conservées dans `work/run-007-sword16-right.png` et `work/run-007-sword16-left.png`.

Specs, brief, workflow, learning et dossier local de revue actualisés pour 24 px. `git diff --check` passe. RUN-007 reste **VERIFY**, en attente d’un nouvel essai humain de portée avant clôture. Aucun push, PR ni fusion.


### Audit et ajustement de protection après validation humaine (28 septembre 2026)

À HEAD `b12c4f5`, l’humain ressent une invulnérabilité trop courte et demande un audit puis une proposition soumise à validation. Aucun changement de gameplay pendant cet audit : historique comparé à `eeeb62c`, invulnérabilité 0,85 s, recul 0,16 s et hit-stun 0,18 s restés identiques à RUN-006. Godot 4.7.2, 27 contrôles locaux réussis : dégâts continus sur cinq profils et contacts de deux vrais Slimes maintenus par la fixture espacés de 51 ticks à 60 Hz, pause correcte, recul non annulé par la direction opposée. Le driver d’audit initial avait des avertissements de libération à l’arrêt ; sa fermeture a été corrigée, le log final n’en comporte plus. Le recul des ronces dirigé selon le regard a été reproduit vers le danger depuis chaque côté. Captures du feedback initial inspectées : teinte rouge et transparence peu visibles dans certaines phases. Scripts, logs, captures et rapport local dans `work/audit-damage/`, ignoré par Git. Cette simulation de contact prolongé ne prétend pas reproduire la session humaine exacte.

L’humain répond **« Oui »** aux quatre ajustements proposés. Implémentation ciblée : protection joueur **1,20 s**, flash blanc **0,10 s** par `assets/shaders/hurt_flash.gdshader`, puis clignotement alpha **0,25/1** sur le reste du délai. Les compteurs suivent la physique et s’arrêtent en pause ; les petites erreurs de calcul à l’expiration sont ramenées à zéro. Le flash préserve la transparence du sprite et son matériau est propre à chaque instance. La mort supprime le flash et restaure l’opacité. Recul **0,16 s** et hit-stun **0,18 s** conservés. Ronces : impulsion horizontale loin de leur centre ; si centres alignés, repli opposé au regard. Dégâts de 1 HP, impulsion verticale, sources et profils conservés. Aucun nouveau piège de RUN-008 ni changement de terrain.

`tests/damage_protection.gd` ajoute **35 contrôles** : protection entière jusqu’au tick 71, expiration au tick 72, flash jusqu’au tick 5 puis expiration au tick 6, tentatives par cinq sources pendant chaque tick, pause, matériaux indépendants, mort pendant le flash, deux Slimes simultanés sous contact maintenu et cadence de 72 ticks, six configurations de ronces (deux regards × gauche/centre/droite) et mouvement physique loin du piège. `tools/test.sh` inclut cette treizième suite. L’ancienne attente de 55 ticks dans l’intégration devient 75 pour tester un nouveau dégât après la protection de 1,20 s ; aucun gameplay artificiellement contourné.

**Vérification finale :** `GODOT_BIN='/mnt/c/Users/allen/OneDrive/Documents/Godot Engine/Godot_v4.7.2-stable_win64_console.exe' ./tools/test.sh` termine avec code 0, Godot **4.7.2.stable.official.ed1daf0bf**. Import sans erreur, isolation `user://`, **13 suites / 296 contrôles de jeu, zéro échec**. Logs : `work/test-results/run-iYLHAGNL/`, résumé `work/test-results/run-007-protection-final-suite.log`. Les suites RUN-006 de saut/recul/hit-stun sont conservées et passent. Deux parcours et leurs retours passent sans nouvelle adaptation du pilote.

`tests/damage_feedback_visual.gd`, rendu GL Compatibility sur RTX 4070 Ti, code 0 : **5 contrôles visuels réussis**. Log `work/test-results/run-007-protection-visual.log` ; captures `work/run-007-protection-{flash,blink-dim,blink-visible,protected-end,normal}.png`. Captures du flash, des deux phases de clignotement et de la fin inspectées : silhouette blanche opaque, alternance avec le sprite normal/translucide, retour à l’apparence normale sans toucher le HUD. Absence d’erreur de shader, script ou fuite dans les logs finaux. `git diff --check` passe.

Specs, brief, workflow, learning et dossier local de revue actualisés. RUN-007 revient à **VERIFY** : proposition technique validée et implémentée, nouvel essai humain du ressenti attendu avant clôture. Revue Jev de clôture non exécutée pendant cette attente. Aucun push, PR ni fusion ; RUN-008 reste BACKLOG.


### Validation humaine de RUN-007 (28 septembre 2026)

L’humain confirme : **« Je valide la run et les changements. »** La validation de la run et de son résultat final est obtenue après les retours sur la portée et la protection. Dossier local `work/test-results/RUN-007/review.json` actualisé avec validation humaine `passed` et preuves finales de `run-iYLHAGNL/`. Les logs existants confirment 13 suites / 296 contrôles de jeu et 5 contrôles visuels réussis ; les parcours et retours se terminent à 3 HP. Aucun changement de gameplay depuis le commit `e97a526` et aucun test de gameplay relancé pour cette clôture documentaire. Revue Jev et décision de clôture à consigner ci-dessous.


### Revue Jev et clôture locale de RUN-007 (28 septembre 2026)

Commande exécutée après chargement silencieux de la configuration locale : `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-007/review.json --json`, sortie conservée dans `work/test-results/RUN-007/jev-final.json`, code 0. Modèle `jev-1.13.0`. Les quatre décisions sont examinées individuellement : couverture des critères (Noul oui 0,81), vérifications obligatoires complètes (Noul oui 0,67), blocage présent (Noul oui 0,25), Choice **READY_FOR_DONE** (confiance 0,43 ; probabilités READY_FOR_DONE 0,61 / VERIFY 0,24 / BLOCKED 0,15). Ces probabilités non calibrées ne constituent ni un test ni une autorisation automatique.

Inspection directe déclenchée par cette revue : critères Sword/Slimes/protection comparés au code livré à `e97a526`, logs de chacune des 13 suites revus (296 contrôles, zéro échec), import et isolation confirmés, deux parcours et retours à 3 HP, logs du rendu et captures inspectées lors de l’implémentation, preuves de bugtest et correctifs revues, journal/learning actualisés. Validation humaine explicite obtenue dans le message précédent. Aucun contrôle obligatoire en échec, non exécuté ou en attente ; aucun blocage constaté. Les probabilités modérées du reviewer ne conduisent pas à redemander une validation déjà obtenue. Conclusion : **RUN-007 DONE localement**.

État Git avant clôture documentaire propre sur `feature/run-007-combat-sword-slimes`. Gameplay livré aux commits `8e43085`, `b12c4f5`, `e97a526` ; commit humain `4c7438b` préservé. La clôture change seulement brief/workflow/journal/learning ; `git diff --check` et `git diff --cached --check` réussis ; contenu staged limité aux quatre documents de clôture et revu avant commit local. Aucun push, PR ni fusion autorisé ou effectué dans cette clôture. RUN-008 reste BACKLOG et n’est pas lancée.


## RUN-008 — Piques fixes solides et vide par niveau (28 septembre 2026)

**Statut : DONE localement après validation humaine et revue de clôture.** Lancement explicitement demandé. Base propre `develop` à `260c8a8`, RUN-007 fusionnée via PR #11 ; branche dédiée `feature/run-008-solid-spikes`. Aucun changement humain local préexistant. Inspection ciblée des systèmes dégâts, niveau, hazards, collisions et parcours. Une inspection/revue indépendante en lecture seule a été déléguée à Luna Low.

### Implémentation et périmètre

Nouvelle scène `scenes/spikes.tscn` et script `scripts/spikes.gd` : corps statique terrain 1 sans grippable, rectangle solide 32×12 px, capteur joueur 34×14 px ; dessin provisoire de quatre dents. Rotation commune des formes/dessin/impulsion. Contact 0,5 HP via SOLID_TRAP : recul sans hit-stun ni interruption, protection existante 1,20 s. Piques au sol `(1120,224)` et vers la gauche `(2240,80)` sur la limite droite. Deux ronces existantes à 1 HP conservées ; aucune tuile ni source d’asset modifiée. Indication de saut près des nouvelles piques au sol. Le pilote du chemin bas ajoute un saut par-dessus les piques dans chaque sens avec entrées de jeu publiques.

Le niveau exporte `void_y=304` en coordonnées locales ; sa boucle physique applique VOID sous cette limite, hors pause et tant que le niveau n’est pas terminé. Retrait du `y>340` dans le joueur et de la zone Pit redondante. La valeur 304 conserve l’ancien bord supérieur de cette zone, sans prétendre reproduire exactement le tick d’entrée d’un capteur sur la capsule. La mort reste unique et traverse l’invulnérabilité. Reprise manuelle inchangée (RUN-009 non lancée).

### Preuves exécutées

Moteur Windows **4.7.2.stable.official.ed1daf0bf** via `GODOT_BIN` ciblant l’exécutable console installé dans `C:/Users/allen/OneDrive/Documents/Godot Engine/`.

- `./tools/test.sh` : code 0, import réussi (cache existant, aucune revendication d’import depuis zéro), contrôle d’isolation `user://` réussi, **14 suites / 335 contrôles de jeu**, zéro échec/erreur/fuite dans les logs. Profil temporaire isolé supprimé par le lanceur. Logs : `work/test-results/run-g3diTC5Q/`, sortie consolidée `work/run-008-tests.log`.
- `tests/spikes_void.gd` : **39 contrôles**. Approches par `move_and_collide` contre la forme réelle, dans quatre orientations ; dégâts exacts, contact répété protégé puis nouveau dégât lorsque la protection est retirée, impulsion hors de la surface, attaque préservée sans stun, sondes murales ignorant les piques. Les compteurs du joueur sont figés dans ces fixtures pour isoler le contact ; leur durée réelle reste exercée par les 35 contrôles `damage_protection`. Chute avec limite abaissée à 500 px : le joueur survit sous 340 ; pause, retour de limite à 300, mort fatale malgré protection et émission unique. Chute par gravité sur les piques intégrées : dégâts et recul observés.
- Régressions : mobilité, physique, murs grippables, ferry, limites, combat, clavier/pause, collecte/offrande, mort/reprise/transition et bonus réussis. Parcours haut/bas terminés respectivement à **3 / 2 HP** ; retours terminés à **2 / 1,5 HP**, sans tricher sur santé/position/compteurs. Ils prouvent la traversabilité, pas un parcours sans dégâts ni un équilibrage humain.
- `./tools/run.sh --fixed-fps 60 --script res://tests/spikes_visual.gd` : code 0, **2 contrôles graphiques** ; rendu Windows OpenGL Compatibility / RTX 4070 Ti. Captures `work/run-008-spikes-floor.png` et `work/run-008-spikes-wall.png`, toutes deux inspectées. Piques claires visibles au sol, silhouette vers la gauche à la limite droite. Log `work/run-008-visual.log`.
- Import final après ajout du script de capture : code 0, aucune erreur dans `work/run-008-final-import.log` ; UID de scripts générés par Godot. `git diff --check` réussi. Journal, learning, brief et contrat technique du piège/vide actualisés. Dossier de revue préparé dans `work/test-results/RUN-008/review.json`, validation humaine explicitement en attente.

### Bugtest et limites

Les scénarios ciblés ont tenté les contacts répétés, chaque orientation, les sondes murales sur les piques, une limite de vide différente, la pause et une chute prolongée après mort. Aucun échec constaté ; aucun correctif de bug nécessaire pendant cette passe. Le dessin a une collision rectangulaire couvrant son emprise, sans collision dent par dent. Aucun asset final ni équilibrage humain revendiqué.

Revue indépendante Luna Low : aucun défaut concret constaté dans le diff ni les nouvelles formes, le contact et le contrôle pause/vide ; les angles cardinaux et placements actuels sont le périmètre vérifié. Inspection racine du code et des logs concordante.

À la fin de l’implémentation, la revue humaine de lisibilité/placement et de ressenti du recul, puis la revue Jev, restaient attendues. Elles sont réalisées à la clôture consignée ci-dessous. Aucun push, PR ou merge effectué ; pas de lancement de RUN-009.


### Validation et clôture locale de RUN-008 (28 septembre 2026)

L’humain confirme : **« Ok run 008 vérifiée et validée »**. Validation enregistrée `passed` dans `work/test-results/RUN-008/review.json`. État Git propre sur `feature/run-008-solid-spikes` à `03f42ba`, sans changement gameplay depuis les vérifications.

Après chargement silencieux de la configuration locale, commande `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-008/review.json --json`, sortie `work/test-results/RUN-008/jev-final.json`, code 0, modèle `jev-1.13.0`. Résultats examinés individuellement : couverture des critères (Noul oui **0,80**), vérifications complètes (Noul oui **0,72**), blocage présent (Noul oui **0,28**), Choice **READY_FOR_DONE** (confiance **0,32** ; probabilités READY_FOR_DONE **0,54** / VERIFY **0,30** / BLOCKED **0,16**). Probabilités consultatives, non calibrées ; Jev n’exécute pas les contrôles et n’autorise pas DONE.

Inspection directe des preuves : chacun des logs de `run-g3diTC5Q/` confirme ses résultats, total **335 contrôles de jeu** sur 14 suites, plus isolation ; aucun FAIL, SCRIPT ERROR, ERROR ou fuite relevé. Import et log graphique relus ; **2 contrôles graphiques** réussis et captures déjà inspectées pendant l’implémentation. Code piques/vide, critères, bugtest et limites rapprochés des preuves : contacts physiques dans quatre orientations, profil de dégâts, absence d’accrochage, chute configurable, pause et mort unique couverts ; les parcours restent traversables. La validation humaine reçue porte sur le résultat final. Aucun test obligatoire restant, aucun blocage constaté. Conclusion : **RUN-008 DONE localement**.

Clôture documentaire seulement : brief/workflow/journal/learning mis à jour, sans nouvelle modification de gameplay ni relance des tests de jeu. Contrôle du diff et du contenu staged avant commit local. Aucun push, PR ou merge autorisé ou effectué ; RUN-009 reste BACKLOG.

## RUN-009 — Mort et reprise automatiques (30 septembre 2026)

**État initial.** Dépôt propre sur `develop`, dépendances RUN-006 et RUN-008 terminées. Branche `feature/run-009-auto-respawn` créée depuis `develop`. La mort attendait E ; le niveau gérait déjà un signal de mort unique, les bonus de tentative et la réserve validée séparément.

**Changement.** `level.gd` suspend le gameplay à la mort, affiche « Thou hast perished. », compte 3 s puis anime un fondu noir de 0,4 s avant un seul rechargement. Le nœud du niveau reste actif pendant la pause ; le rechargement retire la pause. Le HUD masque l'ancien indice et le rappel Échap pendant cet écran. Aucun changement à la sauvegarde ni à la victoire. Les anciens tests E ont été adaptés et une suite ciblée `death_transition.gd` ajoutée. Dans la fixture piques/vide, le nettoyage retire désormais la pause laissée par une scène morte avant de créer la fixture suivante.

**Preuves.** Godot Windows `4.7.2.stable.official.ed1daf0bf`. `GODOT_BIN=… ./tools/test.sh` : code 0, import et isolation `user://` réussis, 15 suites / **353 contrôles de jeu** réussis, aucun FAIL, SCRIPT ERROR, ERROR ni fuite dans les logs. Preuves finales : `work/test-results/run-OVkdZlmx/`, sortie `work/run-009-final-test.log`. La suite ciblée (15 contrôles) vérifie le titre, l'attente de 3 s sans E, le fondu, la vie pleine, deux morts successives, mort pendant Sword et pause, rechargement unique, bonus de tentative perdus une fois, réserve conservée et quatre secondes d'attente sans danger au spawn. Régressions intégration, bonus, clavier, combat, piques/vide et parcours aller/retour toutes réussies.

**Bugtest.** La première suite complète a échoué sur le dernier contrôle de `spikes_void` parce que sa fixture libérait une scène morte en laissant `SceneTree.paused=true` ; le test suivant ne pouvait plus tomber sur les piques. Le nettoyage retire la pause, puis la suite complète a réussi deux fois. Le résultat final inclut le changement HUD de lisibilité. `git diff --check` réussi.

**Contrôle graphique.** Exécution réelle non headless avec rendu Windows : captures `work/run-009-death.png` et `work/run-009-fade.png` inspectées. Titre anglais centré et lisible sur décor assombri ; ancien indice et rappel Échap absents ; la seconde capture montre le fondu qui couvre l'écran. Commande et erreurs : `work/run-009-death-visual.log`, code 0, aucune erreur relevée. Les captures concernent le viewport 640×360 et le niveau actuel. Aucun playtest humain requis explicitement par RUN-009 ; ressenti de durée non revendiqué. Aucun push, PR ou merge effectué.

**Documentation et clôture.** `brief.md`, `runs-workflow.md` et `learning.md` actualisés. Revue Jev après correction du statut `human_validation` dans le JSON (`not_required`) : commande `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-009/review.json --json`, code 0, modèle `jev-1.13.0`, sortie `work/test-results/RUN-009/jev-final.json`. Noul couverture oui **0,83**, vérification complète oui **0,75**, blocage présent oui **0,48** ; Choice **READY_FOR_DONE**, confiance **0,24**, probabilités READY_FOR_DONE **0,49** / VERIFY **0,38** / BLOCKED **0,13**. Ces probabilités restent consultatives. Inspection directe du code, des logs finaux et des deux captures : tous les critères et contrôles obligatoires sont couverts, aucun défaut ni blocage restant constaté. RUN-009 **DONE localement** ; aucun push, PR ni merge.

### Validation et fusion de RUN-009 (30 septembre 2026)

L'humain confirme : **« Run validée et PR merged. Mettre à jour statut. Ne lance pas de run »**. Inspection du dépôt propre sur `develop` : `a2ac33c` est le merge commit de la PR #14, avec `760ad06` pour parent de la branche RUN-009 ; `develop` suit `origin/develop`. RUN-009 est **DONE et fusionnée**. Seules les mentions de statut dans la documentation ont été actualisées ; aucun code de jeu ni test modifié, aucune autre run lancée.

## RUN-010 — Bus audio et feedbacks élémentaires (30 septembre 2026)

**État initial.** Dépôt propre sur `develop` (`a2ac33c`), dépendances DONE. Branche `feature/run-010-audio-buses`. Aucun bus personnalisé ; quatre WAV hérités et une OGG sur des `AudioStreamPlayer` sans bus. `hurt.wav` servait aux dégâts joueur et Slime ; le saut, le wall jump et le double saut partageaient `jump.wav` à des pitchs différents ; aucun son de mort ni de mort Slime. À la mort, `SceneTree.paused` aurait suspendu tout son joué par le joueur.

**Sources et licences.** L'humain demande d'utiliser les bibliothèques locales SFX et Music (`.local/asset-paths.md`), lues sans modification. *Pixel Combat* de Helton Yan : CC BY 4.0 d'après sa page itch.io (résultat de recherche ; la page elle-même est protégée par Cloudflare), crédit obligatoire. *Minifantasy Dungeon SFX* : la licence de Krishna Palacio interdit la redistribution des assets ; `gh repo view` confirme un dépôt **public**, donc pack non intégré. Musique : fichiers au format Pixabay, [Pixabay Content License](https://pixabay.com/service/license-summary/) consultée ; la page exacte du morceau reste à relier. Détail fichier par fichier dans `assets/AUDIO_CREDITS.md`.

**Sélection et adaptation.** Mesures ffprobe/ffmpeg : sources Helton en 96 kHz / 24 bits stéréo, calées sur 2,5 s de silence. `tools/prepare_audio.py` produit 19 WAV mono 44,1 kHz 16 bits, rognés et crête −3 dBFS, et une OGG q5 à −15,6 LUFS intégrés (true peak −8,3 dBFS). Le morceau source mesurait −5,6 LUFS avec des crêtes au-dessus de 0 dBFS. Cinq `AudioStreamRandomizer` (3 variantes, pitch ±4–8 %, ±1 dB) pour swing, impact, dégâts, pièce et mort Slime. Choix de la musique : seul morceau « dark fantasy retro » de la bibliothèque ; il reste provisoire et figure aussi comme candidat au thème du menu dans le catalogue local.

**Intégration.** `default_bus_layout.tres` : Master avec `AudioEffectHardLimiter` −1 dB, Music, Ambient, SFX et UI envoyés vers Master, tous à 0 dB. Les volumes des nœuds reprennent les crêtes effectives de l'ancien mix ; la musique garde un niveau proche de l'ancien (≈ −37 dB RMS). Joueur : nœuds dédiés au saut, double saut, wall jump, dégâts, swing et mort, non positionnels puisque la caméra le suit. `DeathSound` est en `PROCESS_MODE_ALWAYS` ; le coup mortel ne joue plus le son de dégâts, que la pause couperait. Slime : impact et éclaboussure en `AudioStreamPlayer2D` (portée 480 px). Au coup fatal, ces deux sons sont déplacés vers la scène courante, repassés en mode pausable, puis libérés à leur fin : la durée de vie du Slime et le contenu de `Enemies` restent inchangés. Pièces en 2D ; porte et son `coin.wav` hérité routés vers SFX. `tools/build_*` référencent encore les anciens médias ; ils n'ont pas été relancés.

**Preuves.** Godot Windows `4.7.2.stable.official.ed1daf0bf`, `GODOT_BIN=… ./tools/test.sh` : code 0, import et isolation `user://`, **16 suites / 377 contrôles** réussis, aucun FAIL, SCRIPT ERROR, ERROR ni fuite. Logs `work/test-results/run-ehRPuuFh/`, sortie `work/run-010-final-test.log`. Nouvelle suite `tests/audio.gd` (24) : ordre et envois des bus, limiteur, routage, types positionnels, rotations, 60 frames de course sans son, saut/double/wall jump/swing distincts, dégâts non mortels contre mortels, boucle musicale, Slime (impact, éclaboussure à la position de mort, conteneur intact, son qui survit puis se libère), pièce, et son de mort toujours actif 30 frames après la pause. `python3 tests/wav_import.py` et `git diff --check` réussis.

**Mix.** `tools/run.sh --write-movie work/run-010-mix.avi --fixed-fps 60 --script res://tests/audio_mix_capture.gd`, code 0, limiteur Master coupé. Sur une même frame et par-dessus la musique : saut, swing, deux Slimes tués au contact, pièce et dégât joueur, puis double saut, swing répété et mort. Mesures astats du PCM 48 kHz : musique seule crête −28,7 / RMS −36,7 dBFS ; empilement crête **−5,5 dBFS** ; mort −6,8 dBFS. Aucun écrêtage, sans compter sur le limiteur. Forme d'onde `work/run-010-mix-wave.png` inspectée ; audio écoutable dans `work/run-010-mix.wav`.

**Bugtest.** Ancienne assertion du double saut (pitch de `JumpSound`) réécrite pour le nœud dédié. Premier essai : un Slime restait vivant jusqu'à la fin de son éclaboussure et `combat` échouait ; son détachement vers `Enemies` faisait ensuite échouer le pilote de parcours, qui suppose que ce conteneur ne contient que des ennemis. Correction : détachement vers la scène courante. L'impact du coup fatal, coupé net à 0,35 s, est détaché de la même façon. Les fuites en fin de `audio.gd` venaient de lectures encore actives au `quit()` : le test arrête les sons et attend 0,3 s réelle. En headless, l'audio avance en temps réel indépendamment de `--fixed-fps`, d'où l'attente réelle du test de libération.

**Limites.** Aucune écoute effectuée par l'agent : les mesures prouvent les niveaux et l'absence d'écrêtage, pas l'adéquation artistique. Validation humaine attendue sur les sons, l'équilibre et la musique. Bus UI et Ambient vides : aucun son UI n'existe encore dans le jeu. Atterrissage, wall slide, piques dédiées et menus restent à couvrir par leurs runs. RUN-010 passe en **VERIFY** ; aucun push, PR ni merge.

### Validation et clôture de RUN-010 (30 septembre 2026)

L'humain a écouté en jeu : **« C'est ok pour une première itération »**. Limites consignées pour une run audio ultérieure : la musique est un peu trop basse et un autre morceau devra être choisi ; les SFX sont trop forts ; l'impact d'épée n'est pas agréable et doit être changé ; les sons de saut et de double saut doivent être changés. Consigne explicite : **ne rien modifier**. Aucun code, asset, volume ou réglage n'a été retouché ; seules la documentation et le statut ont été mis à jour.

Revue Jev : `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-010/review.json --json`, code 0, modèle `jev-1.13.0`, sortie `work/test-results/RUN-010/jev-final.json`. Noul couverture oui **0,81**, vérification complète oui **0,75**, blocage présent oui **0,44** ; Choice **READY_FOR_DONE**, confiance **0,24**, probabilités READY_FOR_DONE **0,50** / VERIFY **0,42** / BLOCKED **0,08**. Ces probabilités sont consultatives. Inspection directe : les critères, les 377 contrôles, la capture de mix, le bugtest, le journal et le learning sont présents. La validation humaine est obtenue et les limites relèvent d'un travail futur, sans blocage de cette run. **RUN-010 DONE localement** ; pas de push, PR ni merge, aucune run suivante lancée.

## RUN-011 — Recette du socle de production (30 septembre 2026)

**Lancement.** Dépôt propre sur `develop` au commit `24213f2`, identique à `origin/develop`. Branche `feature/run-011-production-foundation` créée depuis `develop`. Les dépendances RUN-004, RUN-005, RUN-007, RUN-008, RUN-009 et RUN-010 sont `DONE` ; RUN-010 est déjà fusionnée dans `develop` par la PR #15. RUN-011 passe à **ACTIVE**. Périmètre : import, suites adaptées, deux branches avec retours, pause/mort, rendu et comportement à 30/60/144 fps, correction ciblée des défauts constatés. L'essai humain du saut mural sera requis avant `DONE`. Aucun test de RUN-011 n'est encore revendiqué à ce stade.

**Recette automatique.** Sous Windows Godot `4.7.2.stable.official.ed1daf0bf`, `GODOT_BIN=… ./tools/test.sh` finit avec code 0 : import propre, profil `user://` isolé, 16 suites et **377 contrôles de jeu** réussis, plus le contrôle d'isolation. Logs `work/test-results/run-5sBVPPnz/`, sortie `work/run-011-baseline-test.log`. Aucun `FAIL`, `SCRIPT ERROR`, `ERROR:` ou `leaked` relevé. `routes` traverse séparément les branches haute et basse jusqu'à la sortie ; `backtracking` fait sortie, retour, changement de branche et nouvelle sortie. Le pilote applique des entrées physiques sans déplacer artificiellement joueur, ennemis ou bac. `keyboard` vérifie pause/reprise par Échap, interaction E bloquée pendant la pause, mort et victoire ; `death_transition` vérifie morts répétées, attaque, pause, attente trois secondes, fondu, rechargement unique, réserve et spawn sûr. Ces tests ne constituent pas un essai humain.

**Cadences et rendu.** `./tools/run.sh --disable-vsync --max-fps {30,60,144} --script res://tests/render_timing.gd` sous le rendu OpenGL Compatibility de la RTX 4070 Ti : **30,0 / 60,0 / 144,0 fps observés**, physique à 60 Hz, 9 contrôles réussis à chaque cadence. Saut/double saut, attaque aérienne, wall slide/jump, blocage du double saut après wall jump et transport/saut depuis le bac passent. Logs `work/test-results/RUN-011/render-timing-{30,60,144}.log`. La même matrice avec `tests/visual.gd` produit 9 PNG 640×360 par cadence, sans erreur ; captures dans `work/test-results/RUN-011/visual-{30,60,144}/`. Inspection directe du mur à 30 fps, de la mort à 60 fps et du sommet à 144 fps : cadrage, HUD, indication du mur et titre de mort lisibles. Ce contrôle par captures fixe des états représentatifs ; il ne mesure pas le ressenti des commandes.

**Bugtest et validation humaine.** Aucun défaut du socle reproduit pendant la recette : aucun correctif gameplay ni retest après correctif nécessaire. Les cas limites mur/bac, pause, mort répétée, retour et changement de branche ont été exercés par les tests cités. L'humain a essayé le saut mural sur la branche et répondu **« Jouable, je valide »** le 30 septembre 2026. Le ressenti est ainsi validé pour ce jalon ; la fixture de cadence reste distincte de ce playtest.

**Suite de la roadmap.** Le dépôt reste un slice, sans menu, Spirit, coffre, Longbow, potion ni boucle de persistance N1 ; aucun de ces éléments n'est revendiqué pour 0.1.0. Le jalon 0.2.0 est découpé en dix runs BACKLOG, RUN-012 à RUN-021, qui couvrent contrats D03–D05, états/modales, sauvegarde, menu, HUD, tir Longbow, Spirit, coffre/potion, adaptation du niveau et recette. Les critères déjà validés exigent New Game/Continue/Controls/Quit et un Longbow qui tire ; les décisions ouvertes concernent leurs états précis, pas leur présence.

**Revue et clôture locale.** Dossier `work/test-results/RUN-011/review.json` relu avec les logs, captures et diff. Commande `.local/typesafe-venv/bin/python tools/jev/run_completion_reviewer/review.py work/test-results/RUN-011/review.json --json`, code 0, modèle `jev-1.13.0`, résultat `work/test-results/RUN-011/jev-review.json`. Noul couverture oui **0,89**, vérification complète oui **0,83**, blocage présent oui **0,41** ; Choice **READY_FOR_DONE**, confiance **0,41** (probabilités READY_FOR_DONE **0,61** / VERIFY **0,25** / BLOCKED **0,14**). Ces probabilités ne remplacent pas les preuves. Inspection directe : critères, 377 contrôles, 27 contrôles de cadence, 27 captures, essai humain, bugtest, journal et learning sont présents ; aucun défaut ni blocage constaté. **RUN-011 DONE localement**, 0.1.0 validée localement ; aucun push, PR ni merge de cette branche, aucune run 0.2.0 lancée.

## Réorganisation de la production — 2 octobre 2026

**Demande et baseline.** L’humain demande de regrouper la roadmap en 20–30 runs maximum, de raccourcir les versions, de désigner l’orchestrateur de chaque lot et de conserver le routage/délégation/Jev, sauf le passage du main Codex et de `code_worker` à GPT-6.1 Sol Medium. Au début de cette intervention, le dépôt est propre sur `feature/run-011-production-foundation`. Aucun changement de branche, aucune implémentation de run future.

**Plan remplacé.** Le workflow précédent annonçait 60–74 runs jusqu’à 0.9.0 beta ; README et brief contenaient encore une ancienne enveloppe de 59–75. Le nouveau plan compte **28 identifiants : 11 DONE + 3 réserves Claude conditionnelles + 14 lots futurs**. RUN-012–014 réservent les éventuelles passes visuelles sur la branche actuelle ; RUN-015–017 visent 0.2.0, 018–021 visent 0.3.0, 022–026 visent 0.4.0, 027–028 visent 0.5.0 beta. Les anciennes RUN-012–021 n’avaient pas été lancées ; une table de correspondance conserve leur traçabilité. Les références anciennes dans les entrées datées de ce journal décrivent le plan d’alors, pas le planning applicable.

**Validation du socle et verrou.** Conformément à la demande humaine du 2 octobre, les onze premières runs sont considérées validées et la version actuelle est **0.1.0**, également renseignée dans `project.godot` (`config/version`). Les preuves de RUN-011 ci-dessus restent celles réellement exécutées le 30 septembre ; aucun nouveau test Godot n’est revendiqué. La réorganisation reste à faire relire/valider ; le choix des passes Claude reste ouvert. Les travaux retenus doivent être terminés et validés avant validation finale et fusion autorisée de cette branche. La fusion effective dans `develop` précède tout démarrage de RUN-015 / 0.2.0.

**Documentation et modèles.** Roadmap, brief, README, vision produit et matrice de jalons d’assets alignés ; AGENTS/CLAUDE explicitent l’objectif d’accélération et d’autonomie sans surdécoupage. Le profil `.codex/agents/code_worker.toml`, le catalogue et le défaut Codex de `task_router`, son exemple et sa fixture utilisent `gpt-6.1-sol`. Les autres modèles, algorithmes de routage, autorisations, délégation et reviewer de clôture sont conservés. Il s’agit de la configuration prévue pour les prochaines invocations, pas d’une affirmation de changement du modèle du chat courant.

**Vérifications.** Sous-tâche déléguée bornée sur les règles et références de modèles : quatre tests unitaires du routeur réussis. Contrôle local de cohérence documentaire : 28 en-têtes de runs uniques et ordonnés ; 001–011 DONE ; 012–028 BACKLOG avec orchestrateur et dépendances antérieures ; les **28 critères de jalon non cochés du plan antérieur sont conservés**, avec seule adaptation de la version finale ; parsing TOML/JSON, version 0.1.0 et nouveaux liens Markdown relatifs valides. Recherche des anciennes versions : elles ne restent dans la documentation active que dans la table historique de correspondance. `git diff --check` passe. La revue croisée ne relève pas de critère produit supprimé ; ses alertes de comptage et de jalon ont été confrontées au texte : les réserves sont explicitement 0.1.0 et le report audio à RUN-027 réutilise un lot déjà compté. RUN-021 harmonise volontairement N1 livré par RUN-017 avec N2–4 livrés par RUN-020.

**Limites et arrêt.** Pas de gameplay modifié ; seule la métadonnée de version change dans le projet Godot. Pas de suite moteur rejouée pour cette passe documentaire/configuration de routage. Pas de nouvelle run à clôturer, donc pas de nouvelle revue Jev de complétion ; la revue RUN-011 reste enregistrée ci-dessus. Aucun push, PR ou merge effectué ; aucune run future lancée. La validation humaine du nouveau plan et la sélection éventuelle des lots visuels restent attendues.

## RUN-012 — Personnage et feedbacks visuels du socle (2 octobre 2026)

**Lancement et décision.** Sur `feature/run-011-production-foundation` (verrou de branche), l'humain retient les lots 012–014, dans l'ordre, avec une validation visuelle et d'écoute groupée en fin de lot C. Inspection de la bibliothèque locale (`.local/asset-paths.md`) : le seul personnage complet, le Soldier de Zerie (cases 100×100), mesure ≈ 17×21 px opaques, en vue RPG sans cape ni plaques, sous la cible Art Bible ≈ 24×32. Sous-tâche déléguée (Sonnet, `asset_integrator`, lecture seule) : inventaire et licences des packs d'effets/icônes ; seuls les icônes CC0 de Shade (vérifiées sur OpenGameArt) et les fichiers PixelLab de l'humain sont redistribuables dans un dépôt public. Les pages itch.io étaient inaccessibles (Cloudflare) : ces verdicts restent à confirmer par l'humain. Prototype idle 1× collé dans une capture 640×360 (`work/run-012/proto-knight-scale.png`) ; **l'humain choisit de générer l'Ashen Knight** dans ce style.

**Réalisé.** `tools/art/pixel.py` (grilles texte, calques, encodeur PNG sans dépendance) et `tools/art/knight.py` produisent `assets/sprites/ashen_knight.png` (frames 32×32 : idle 4, run 6, rise 2, fall 2, wall 2, attack 3, hurt 1, dead 4) et son `SpriteFrames` `.tres`, l'épée en 32 angles, une traînée en croissant et trois bandes VFX (impact, anneau de double saut, poussière murale). Corps ≈ 20×28 px ; dégagement minimal mesuré dans le niveau : 32 px (2 tuiles). `player.tscn` référence les nouvelles frames (sprite à −15 px, flip symétrique autour de x=0). `player.gd`, côté visuel seulement : choix d'animation par état (dégâts, attaque par phase de la lame, glissade, montée/chute, course/idle), épée et traînée dessinées depuis la main (+4, −10) avec l'angle exact du coup et miroir selon `attack_facing`, étincelle à chaque cible touchée, puff et poussière en sprites. Le sprite joue pendant la pause de mort (comme `DeathSound`) : auparavant l'animation `dead` restait figée sur sa première frame. Capsule 10×18, forme et requête de lame, portée 24 px, dégâts, cadence, fenêtre et timings inchangés. Ancien `knight.png` conservé (comparaison d'échelle RUN-003).

**Preuves.** Godot Windows `4.7.2.stable.official.ed1daf0bf`, `GODOT_BIN=… ./tools/test.sh` : code 0, import propre, isolation `user://`, 16 suites / **377 contrôles de jeu** réussis, avant et après le correctif de mort (`work/run-012-test-1.log`, `work/run-012-test-2.log`). Nouvelle suite non headless `tests/knight_visual.gd` : **17 contrôles** réussis (animation choisie pour idle, course, montée, chute, double saut, glissade réelle contre le mur de la branche haute, trois phases d'attaque des deux côtés contre un vrai Slime, étincelle unique par coup, dégâts, effondrement jusqu'à la frame couchée pendant la pause de mort) ; 21 captures dans `work/run-012/` inspectées (planche `contact.png`, `hurt.png`, `death_zoom.png`). Suites visuelles existantes relancées : combat 2, retour de dégâts 5, piques 2, santé et bonus sans erreur.

**Bugtest.** Premier essai de glissade mal placé (pas de mur à x=608) : repositionné contre le pilier x=624. Une exécution de `spikes_visual` a fini en `signal 11` dans `uxtheme.dll` **après** « 0 failures », à la fermeture de la fenêtre Windows ; trois relances avec les changements et une sur la base sans changements finissent avec le code 0. Crash ponctuel à la fermeture, non lié au contenu ; consigné comme limite.

**Limites.** Le flash blanc existant (0,10 s) recouvre presque toute la pose `hurt` : elle se lit comme une silhouette blanche. Le choix artistique, le ressenti des animations et la lisibilité en jeu attendent la validation humaine groupée. RUN-012 passe en **VERIFY** ; RUN-013 démarre selon la consigne d'enchaînement.

## RUN-013 — Décor et lisibilité du slice (2 octobre 2026)

**Lancement.** Selon la consigne d'enchaînement, RUN-013 démarre après la mise en VERIFY de RUN-012. Faute de packs redistribuables adaptés, même principe : génération par `tools/art/` sur une palette commune `tools/art/palette.py` (noirs colorés, gris chauds/froids, bleus très sombres ; or, rouge, violet et vert réservés aux fonctions de gameplay de l'Art Bible). Délégation : deux subagents Sonnet (`visual_architect`), sans scène ni Git, l'un pour Slimes/pièce/icônes HUD (`tools/art/creatures.py`), l'autre pour piques/ronces/bac/porte (`tools/art/hazards.py`), avec contrats de taille et d'ancrage fixés à l'avance ; intégration et vérification par le main agent.

**Réalisé.** `TerrainSkin` habille la `TileMapLayer` existante avec des tuiles 16×16 choisies selon les voisins (masque d'exposition), trois variantes, deux thèmes (village, approche corrompue au-delà de x=1392), assombrissement progressif en profondeur et touffes de surface ; tuiles, collisions et `TileSet` inchangés. Nouveau nœud `Backdrop` (`scripts/backdrop.gd`) avant `Kingdom` : ciel nocturne et lune de sang fixes à l'écran, citadelle lointaine, brume et forêt morte en parallaxe (facteurs 0,08 / 0,2 / 0,3). `kingdom.gd` dessine désormais des accessoires générés aux mêmes positions narratives (maisons, arbres, charrette, panneau « 12 OR > », piliers, étendard, tiges de corruption, rempart final, tours lointaines, lance au ruban). Slimes 6 frames, pièce 8 frames, piques, ronces, bac et porte remplacent les dessins par code ; le panneau de porte rentre dans le linteau à l'ouverture. HUD : cœurs en icônes pixel art, icône de pièce devant le sceau, couleurs de bandeau, titre de mort en rouge ; textes et logique inchangés. Icône de sceau générée mais jugée peu lisible, non utilisée. Anciens PNG conservés (comparaison d'échelle RUN-003, atlas de collision).

**Preuves.** Godot Windows 4.7.2 : import sans erreur ; `./tools/test.sh` code 0, 16 suites / **377 contrôles de jeu** réussis (`work/run-013-test-1.log`). Assertion réécrite explicitement : le retour de bonus réutilise désormais `item_gold_coin.png` au lieu de `coin.png` (même intention). `tests/slice_visual.gd` capture dix cadrages réels à 640×360 (village, charrette, bifurcation, mur, sommet, branche haute, branche basse, piques, corruption, porte) : captures inspectées (`work/run-013/contact.png`) — chevalier, Slimes, pièces, piques et ronces se détachent du terrain et du fond, surfaces praticables lisibles, HUD et textes non coupés. Les quatre générateurs régénèrent tous les PNG à l'identique (MD5).

**Bugtest.** Premières captures : chevalier terne à cause de l'invulnérabilité forcée par le script (clignotement alpha), corrigé en figeant les ennemis à la place ; grandes masses de maçonnerie trop chargées, corrigées par un assombrissement jusqu'à cinq tuiles de profondeur ; lune trop dominante, réduite ; panneau de porte qui flottait au-dessus de l'arche une fois levé, désormais masqué par le linteau.

**Limites.** Les arbres vivants se répètent beaucoup ; les pièces restent petites à 1× ; le HUD garde ses textes français provisoires jusqu'à RUN-016. Pas de son ni de gameplay modifiés. Ressenti visuel, contraste en mouvement et cohérence artistique attendent la validation humaine groupée. RUN-013 passe en **VERIFY**.
