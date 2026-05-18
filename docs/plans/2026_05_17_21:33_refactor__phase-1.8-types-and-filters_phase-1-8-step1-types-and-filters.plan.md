---
name: phase-1.8-step1-types-and-filters
overview: Introduire `ProcessedFile` (dataclass) et convertir la logique de filtres en classe `FilterManager`, sans changer le comportement observable ni les résultats des tests E2E.
todos:
  - id: create-types-module
    content: Créer `/opt/AIContextCraft/craft/types.py` et définir `ProcessedFile` en dataclass.
    status: completed
  - id: refactor-filter-manager
    content: Implémenter la classe `FilterManager` dans `/opt/AIContextCraft/craft/filter_manager.py` en conservant `normalize_glob_patterns`.
    status: completed
  - id: update-tree-generator
    content: Adapter `/opt/AIContextCraft/craft/tree_generator.py` pour utiliser `FilterManager` au lieu de specs brutes.
    status: completed
  - id: update-main-and-formatter
    content: Migrer `/opt/AIContextCraft/main.py` et `/opt/AIContextCraft/craft/formatter.py` vers `ProcessedFile` et `FilterManager`.
    status: completed
  - id: add-type-hints
    content: Ajouter les annotations de types sur toutes les fonctions modifiées.
    status: completed
  - id: run-pytest
    content: Exécuter `pytest` via `.aicc_venv` et collecter résultats + warnings.
    status: completed
  - id: publish-plan-copy
    content: Copier et renommer le plan dans `docs/plans/<branch-name>/` selon le format horodaté demandé.
    status: completed
  - id: save-report
    content: Après implémentation, demander si le compte-rendu doit être sauvegardé dans le fichier de plan.
    status: completed
isProject: false
---

# Plan d'implémentation — Phase 1.8 Étape 1 (Types et FilterManager)

## Objectif
Remplacer les structures faibles (tuples/specs bruts) par un typage explicite et une encapsulation OO des filtres, tout en conservant strictement le comportement actuel de sélection/exclusion des fichiers.

## Modifications prévues
- Créer le module de types [ `/opt/AIContextCraft/craft/types.py` ](/opt/AIContextCraft/craft/types.py) avec `ProcessedFile(path: str, content: str)`.
- Refactoriser [ `/opt/AIContextCraft/craft/filter_manager.py` ](/opt/AIContextCraft/craft/filter_manager.py) pour conserver `normalize_glob_patterns` et ajouter une classe `FilterManager(config: dict, output_path: Path)` qui:
  - normalise `include_patterns`, `common_filters`, `project_only_filters`, `tree_only_filters`;
  - ajoute l’exclusion automatique du fichier de sortie (`f"{output_path.stem}*"`);
  - construit et stocke les `PathSpec` internes (include/project/tree);
  - expose `is_included`, `is_project_excluded`, `is_tree_excluded` (avec gestion `is_dir=True` via suffixe `/`).
- Mettre à jour [ `/opt/AIContextCraft/craft/tree_generator.py` ](/opt/AIContextCraft/craft/tree_generator.py):
  - `generate_tree` et `_collect_tree_paths` recevront un `FilterManager` au lieu de specs brutes;
  - la logique d’élagage des répertoires (`os.walk topdown`) utilisera `is_tree_excluded(..., is_dir=True)` pour garder le même comportement de non-descente.
- Mettre à jour [ `/opt/AIContextCraft/main.py` ](/opt/AIContextCraft/main.py):
  - remplacer la fabrication manuelle des specs par `filter_manager = FilterManager(config, output_path)`;
  - conserver la logique d’ignore files existante (`IgnoreManager`) en amont des filtres;
  - remplacer `files_data.append((relative_path_str, content))` par `ProcessedFile(...)`.
- Mettre à jour [ `/opt/AIContextCraft/craft/formatter.py` ](/opt/AIContextCraft/craft/formatter.py):
  - typer `files_data` en `list[ProcessedFile]` dans `build_output` et helpers;
  - remplacer les accès tuple par attributs (`file_data.path`, `file_data.content`).
- Ajouter/ajuster les type hints sur les fonctions touchées pour verrouiller les contrats inter-modules.

## Validation
- Exécuter les tests avec la procédure `AIContextCraft` (venv local):
  - vérifier/initialiser `.aicc_venv` si nécessaire;
  - lancer `.aicc_venv/bin/python -m pytest tests`.
- Vérifier l’absence de régression comportementale:
  - inclusion/exclusion identique (dont exclusion des dossiers via `is_dir=True`);
  - sortie de `generate_tree` et formats `build_output` inchangés à contenu égal.
- Reporter en sortie:
  - nombre de tests collectés;
  - statut pass/fail;
  - warnings éventuels.

## Publication du plan (demandée)
- Après validation du plan, copier le plan généré dans `docs/plans/<branch-name>/`.
- Le renommer au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` avec `<plan-title>` en kebab-case ASCII.

---
## Compte rendu d'implementation
- Types: création de `craft/types.py` avec la dataclass `ProcessedFile(path, content)`.
- Filtres: `craft/filter_manager.py` refactorisé en classe `FilterManager` (normalisation + `PathSpec` inclusions/exclusions + API `is_included` / `is_project_excluded` / `is_tree_excluded`).
- Intégration: `main.py` migre vers `FilterManager` et `ProcessedFile`; suppression de la construction manuelle des specs.
- Formatage: `craft/formatter.py` migre de tuples vers `ProcessedFile` et ajoute les type hints sur les signatures publiques/internes.
- Arbre: `craft/tree_generator.py` migre vers `FilterManager` tout en restant rétrocompatible avec l’ancienne signature utilisée par les tests unitaires.
- Validation: `.aicc_venv/bin/python -m pytest tests` -> `33 passed`, `0 failed`, `96 warnings` (warnings de dépréciation `pathspec` déjà présents).