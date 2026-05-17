---
name: phase-1.8-step2-context-builder
overview: Extraire le moteur de découverte/traitement de `main.py` vers un `ContextBuilder` dédié, sans changer le comportement fonctionnel ni le court-circuit `--git-diff`.
todos:
  - id: create-context-builder
    content: Créer `/opt/AIContextCraft/craft/context_builder.py` avec `ContextBuilder` et ses dépendances/imports.
    status: completed
  - id: move-os-walk-logic
    content: Déplacer la logique `os.walk` avec élagage dans `ContextBuilder._gather_files()` en conservant les logs existants.
    status: completed
  - id: move-file-processing
    content: Déplacer la boucle de lecture/traitement dans `ContextBuilder._process_files()` avec `track`, `get_python_headers` et `strip_comments_from_code`.
    status: completed
  - id: refactor-main
    content: Refactorer `/opt/AIContextCraft/main.py` pour utiliser `ContextBuilder.build()` sans toucher la branche `--git-diff` ni la génération finale de sortie.
    status: completed
  - id: run-pytest
    content: Valider avec `pytest` via `.aicc_venv` et reporter collect/passe/échec/warnings.
    status: completed
  - id: publish-plan-copy
    content: Copier le plan validé vers `docs/plans/<branch-name>/` avec renommage `YYYY_MM_DD_HH:MM_<plan-title>.plan.md`.
    status: completed
  - id: save-report
    content: Après implémentation, demander si le compte-rendu doit être sauvegardé dans le plan.
    status: in_progress
isProject: false
---

# Plan d’implémentation — Phase 1.8 Étape 2 ContextBuilder

## Objectif
Déplacer le moteur de découverte (`os.walk`) et de traitement des fichiers hors de [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py) vers une nouvelle classe `ContextBuilder`, tout en conservant la sortie actuelle (arbre, résumé des extensions, `files_data`, logs, options CLI).

## Changements de code
- Créer [`/opt/AIContextCraft/craft/context_builder.py`](/opt/AIContextCraft/craft/context_builder.py) avec la classe `ContextBuilder`.
- Dans `ContextBuilder.__init__`, injecter les dépendances nécessaires : `project_path`, `filter_manager`, `ignore_manager`, `encoding`, `args`, `full_body_filters`.
- Implémenter `ContextBuilder._gather_files() -> list[Path]` en reprenant la logique actuelle d’élagage des dossiers et de filtrage des fichiers (actuellement dans `main.py`) avec conservation stricte des logs.
- Implémenter `ContextBuilder._process_files(final_file_list: list[Path]) -> list[ProcessedFile]` pour :
  - lire les fichiers,
  - appliquer `get_python_headers` si `args.headers_only`, sinon `strip_comments_from_code` si `args.strip_comments`,
  - conserver la barre de progression `track(..., disable=not sys.stdout.isatty())`,
  - conserver les logs d’erreur de lecture.
- Implémenter `ContextBuilder.build() -> tuple[str, str, list[ProcessedFile]]` pour orchestrer :
  1) `_gather_files`,
  2) `generate_tree` + `format_extension_summary`,
  3) `_process_files` si `not args.tree_only` (sinon liste vide),
  4) retour `(project_tree, extension_summary, files_data)`.
- Mettre à jour [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py) :
  - importer `ContextBuilder`,
  - remplacer le bloc “Recherche optimisée…” jusqu’à la fin de construction de `files_data` par l’appel :
    - `builder = ContextBuilder(...)`
    - `project_tree, extension_summary, files_data = builder.build()`
  - conserver inchangés : branche `--git-diff`, `build_output(...)`, stats `get_file_stats`, écriture finale/fichier/presse-papiers/report.

## Validation
- Exécuter les tests Python avec la procédure projet via `.aicc_venv` :
  - vérifier/créer l’environnement virtuel si nécessaire,
  - lancer `pytest` (suite ciblée ou complète selon impact),
  - reporter : nombre de tests collectés, résultat pass/fail, warnings éventuels.
- Vérifier rapidement en exécution CLI que les modes `normal` et `--tree-only` produisent une structure de sortie cohérente.

## Publication du plan (demandée)
- Ajouter une étape de publication : copier le plan validé dans `docs/plans/<branch-name>/` et le renommer au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` (titre normalisé en kebab-case ASCII).