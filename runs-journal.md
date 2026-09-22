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
