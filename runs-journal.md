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
