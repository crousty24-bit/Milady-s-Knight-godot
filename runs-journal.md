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
