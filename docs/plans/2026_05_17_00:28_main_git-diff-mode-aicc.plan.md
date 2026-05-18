---
name: git-diff-mode-aicc
overview: Ajouter un mode CLI `--git-diff` qui génère un rapport Markdown du diff Git entre deux révisions, sans passer par la concaténation standard, avec gestion d’erreurs et tests automatisés.
todos:
  - id: cli-git-diff-arg
    content: Ajouter l’argument CLI `--git-diff` avec deux références Git.
    status: completed
  - id: git-diff-helper
    content: Implémenter la fonction utilitaire d’exécution `git diff` avec gestion d’erreurs robuste.
    status: completed
  - id: main-short-circuit
    content: Ajouter le flux `if args.git_diff` dans `main()` pour court-circuiter tree/concat et générer la sortie Markdown.
    status: completed
  - id: tests-git-diff-mode
    content: Créer les tests unitaires de succès et d’échec pour le nouveau mode Git diff.
    status: in_progress
  - id: docs-cli-update
    content: Documenter `--git-diff` dans le README avec exemple d’usage.
    status: pending
  - id: plan-publication-step
    content: Inclure l’étape de copie/renommage du plan vers `docs/plans/<branch-name>/` au format horodaté demandé.
    status: pending
isProject: false
---

# Ajouter un mode Git Diff dans AIContextCraft

## Objectif
Implémenter un mode alternatif `--git-diff <REF_A> <REF_B>` qui produit un fichier Markdown contenant le diff Git brut entre deux révisions, puis termine l’exécution sans lancer la logique standard de scan d’arborescence/concaténation.

## Portée technique
- **Entrée CLI** : ajouter un argument dédié dans [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- **Récupération du diff** : centraliser l’appel à `git` dans une fonction utilitaire robuste dans [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- **Aiguillage d’exécution** : introduire un chemin court dans `main()` avant la phase de génération d’arbre et lecture des fichiers.
- **Tests** : couvrir le nouveau mode dans [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py).
- **Documentation utilisateur** : documenter l’option et ses exemples dans [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md).

## Plan d’implémentation
1. **Étendre l’interface CLI**
   - Ajouter `parser.add_argument('--git-diff', nargs=2, metavar=('REF_A', 'REF_B'), ...)`.
   - Définir clairement que ce mode est exclusif au flux de concaténation classique.

2. **Créer une fonction utilitaire Git dédiée**
   - Ajouter une fonction `get_git_diff(repo_path: Path, ref_a: str, ref_b: str) -> str`.
   - Comportement attendu :
     - vérifier que `repo_path` est un dépôt Git (`git rev-parse --is-inside-work-tree`),
     - exécuter `git diff ref_a ref_b`,
     - retourner `stdout`.
   - Gestion d’erreurs explicite :
     - Git absent (`FileNotFoundError`),
     - dossier non-Git,
     - révisions invalides / commande `git diff` en échec.

3. **Brancher le mode dans `main()`**
   - Introduire un bloc précoce `if args.git_diff:` après l’initialisation des chemins/config de base.
   - Dans ce bloc :
     - lire les deux révisions,
     - appeler `get_git_diff(...)`,
     - construire un rendu Markdown dédié (titre + bloc ```diff),
     - calculer les stats avec `get_file_stats(...)`,
     - forcer une extension `.md` si la sortie configurée est `.txt`,
     - écrire le fichier (ou simuler en `--dry-run`),
     - afficher les messages finaux et sortir proprement.
   - Garantir qu’aucune logique de tree/concat n’est exécutée dans ce mode.

4. **Définir le format de sortie final**
   - En-tête similaire au format existant (date, statistiques).
   - Corps spécifique :
     - `# Diff Git: <REF_A> -> <REF_B>`
     - bloc code `diff` contenant le résultat brut de `git diff`.
   - Cas sans changement : injecter un message lisible (ex. `Aucune différence détectée entre ces révisions.`) dans le bloc de contenu.

5. **Ajouter les tests unitaires**
   - Ajouter au moins un test de succès dans [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py) :
     - créer un mini repo Git temporaire,
     - faire deux commits,
     - exécuter `aicc.py --git-diff <sha1> <sha2> ...`,
     - vérifier code retour, existence fichier, présence du bloc `diff`, et lignes `+/-` attendues.
   - Ajouter un test d’erreur (référence invalide) :
     - vérifier `returncode != 0`,
     - vérifier présence d’un message d’erreur compréhensible dans `stderr`.

6. **Mettre à jour la documentation**
   - Ajouter `--git-diff` dans la table des options CLI de [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md).
   - Ajouter un exemple de commande réel.
   - Clarifier que ce mode produit un diff global et non une concaténation de fichiers.

## Validation prévue
- Lancer les tests unitaires projet.
- Vérifier manuellement un run nominal sur un repo Git local et un run en erreur (ref invalide).
- Vérifier que la sortie est bien en Markdown et que la logique standard est bien court-circuitée.

## Publication du plan (demandée)
- Après validation du plan, ajouter une étape d’exécution qui :
  - crée `docs/plans/<branch-name>/` si nécessaire,
  - copie le fichier de plan validé,
  - renomme la copie au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` avec `<plan-title>` en kebab-case ASCII.

---
## Compte rendu d'implementation

### Changements realises
- Ajout de l'argument CLI `--git-diff REF_A REF_B` dans `aicc.py`.
- Ajout de la fonction `get_git_diff(repo_path, ref_a, ref_b)` avec verification du depot Git et gestion des erreurs (`FileNotFoundError`, refs invalides, dossier non-Git).
- Ajout d'un chemin court dans `main()` pour le mode Git Diff, sans execution de la logique standard de tree/concat.
- Generation d'une sortie Markdown dediee :
  - titre `# Diff Git: <REF_A> -> <REF_B>`
  - bloc code `diff`
  - message explicite si aucune difference.
- Conversion automatique de la sortie `.txt` vers `.md` dans ce mode.
- Mise a jour de la documentation dans `README.md` (option CLI + exemple).

### Fichiers modifies
- `/opt/AIContextCraft/aicc.py`
- `/opt/AIContextCraft/tests/test_aicc.py`
- `/opt/AIContextCraft/README.md`

### Validation et tests
- Tests executes : `pytest /opt/AIContextCraft/tests/test_aicc.py`
  - collectes : 6
  - resultat : 6 passed
  - warnings : 1 `PytestCacheWarning` (permissions cache pytest sous `/opt`)
- Verification manuelle du mode :
  - cas nominal : rapport `.md` genere avec diff attendu (`+print('v2')`, etc.)
  - cas erreur : reference invalide renvoie `exit=1` avec message Git explicite.