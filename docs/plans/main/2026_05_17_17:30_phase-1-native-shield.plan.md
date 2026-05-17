---
name: phase-1-native-shield
overview: Introduire un filtrage natif à deux étages (ignore files + sécurité, puis YAML pathspec) via un module IgnoreManager, actif par défaut, avec CLI --no-ignore et tests de non-régression.
todos:
  - id: create-ignore-manager
    content: Créer craft/ignore_manager.py (sécurité, cache .gitignore hiérarchique, is_ignored)
    status: completed
  - id: update-main-cli-walk
    content: "main.py : --no-ignore, supprimer --use-gitignore et fusion racine, intégrer Bouclier dans os.walk"
    status: completed
  - id: integrate-tree-generator
    content: "tree_generator.py : appliquer IgnoreManager dans _collect_tree_paths + signature generate_tree"
    status: completed
  - id: add-nested-tests
    content: Fixture nested_ignore_project + tests/test_aicc.py + test_ignore_manager.py
    status: completed
  - id: update-readme
    content: "README : filtrage par défaut, --no-ignore, retirer --use-gitignore"
    status: completed
  - id: save-plan-file
    content: Enregistrer le plan dans docs/plans/main/2026_05_17_17:30_phase-1-native-shield.plan.md
    status: completed
  - id: run-pytest
    content: Exécuter pytest (16 tests) et documenter le résultat
    status: completed
isProject: true
---

# Phase 1 — Filtrage natif à deux étages (Bouclier + Scalpel)

## Objectif

Aligner l'outil sur l'écosystème développeur (`.gitignore` hiérarchiques) avec un filtrage en deux étages :

1. **Bouclier (étage 1)** : `.gitignore` hiérarchiques + règles de sécurité hardcodées, actif par défaut, élagage pendant `os.walk`.
2. **Scalpel (étage 2)** : filtres YAML (`include_patterns`, `common_filters`, etc.) inchangés dans leur rôle.

## Architecture

| Étage | Module | Source |
|-------|--------|--------|
| Bouclier | `craft/ignore_manager.py` | `.env`, `.env.*`, `*.pem`, `*.key`, `.git/` + `.gitignore` par dossier |
| Scalpel | `main.py` | `config.yaml` via pathspec |

## Implémentation réalisée

- `IgnoreManager` avec cache par répertoire et sémantique hiérarchique.
- CLI : `--no-ignore` remplace `--use-gitignore`.
- Intégration dans `main.py` et `craft/tree_generator.py` (`_collect_tree_paths`).
- Fixture `tests/test_projects/nested_ignore_project/` et tests associés.

## Validation

- `pytest tests` : 16 tests collectés, 16 passés.
- Warnings : dépréciation `gitwildmatch` dans pathspec (sans impact fonctionnel).

## Hors scope

`.npmignore`, `config_manager.py`, refactor complet de `filter_manager`.

---

## Compte rendu d'implementation

### Changements livrés

| Fichier | Action |
|---------|--------|
| `craft/ignore_manager.py` | Créé — classe `IgnoreManager` (sécurité + `.gitignore` hiérarchiques, cache par répertoire) |
| `main.py` | `--no-ignore` remplace `--use-gitignore` ; suppression de la fusion racine `.gitignore` dans les filtres YAML ; Bouclier appliqué avant le Scalpel dans `os.walk` |
| `craft/tree_generator.py` | Paramètre `ignore_manager` sur `generate_tree` / `_collect_tree_paths` (même élagage que le parcours contenu) |
| `tests/test_projects/nested_ignore_project/` | Fixture (`.gitignore` racine + `frontend/`, `.env.local`, `logs/`, `node_modules/`) |
| `tests/test_ignore_manager.py` | 3 tests unitaires (sécurité, hiérarchie, `--no-ignore`) |
| `tests/test_aicc.py` | Test E2E `test_nested_gitignore_and_security_patterns` |
| `tests/setup_tests.sh` | Fonction `create_nested_ignore_project` |
| `README.md` | Documentation Bouclier/Scalpel, `--no-ignore`, retrait de `--use-gitignore` |

### Comportement

- **Par défaut** : lecture des `.gitignore` à chaque niveau de l'arborescence + patterns de sécurité toujours actifs (`.env`, `.env.*`, `*.pem`, `*.key`, `.git/`).
- **`--no-ignore`** : désactive uniquement les `.gitignore` ; les règles de sécurité restent appliquées (ex. `.env.local` toujours exclu).

### Validation

```
.aicc_venv/bin/python -m pytest tests
16 passed, 54 warnings in ~2.3s
```

- Warnings : dépréciation `gitwildmatch` dans pathspec (préexistant, sans impact fonctionnel).
- Non-régression : `basic_project` et les 12 tests initiaux passent ; 4 nouveaux tests (3 unitaires + 1 E2E).

### Points d'attention

- Le texte `node_modules/` peut encore apparaître dans la sortie s'il est contenu dans un fichier `.gitignore` concaténé (ex. `frontend/.gitignore`) — ce n'est pas un scan du dossier `node_modules/`.
- `.npmignore` reporté hors scope Phase 1.
