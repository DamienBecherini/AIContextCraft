---
name: phase-1-native-shield
overview: Introduce two-stage native filtering (ignore files + security, then YAML pathspec) via IgnoreManager, enabled by default, with CLI --no-ignore and regression tests.
todos:
  - id: create-ignore-manager
    content: Create craft/ignore_manager.py (security, hierarchical .gitignore cache, is_ignored)
    status: completed
  - id: update-main-cli-walk
    content: "main.py: --no-ignore, remove --use-gitignore and root merge, integrate Shield in os.walk"
    status: completed
  - id: integrate-tree-generator
    content: "tree_generator.py: apply IgnoreManager in _collect_tree_paths + generate_tree signature"
    status: completed
  - id: add-nested-tests
    content: nested_ignore_project fixture + tests/test_aicc.py + test_ignore_manager.py
    status: completed
  - id: update-readme
    content: "README: default filtering, --no-ignore, remove --use-gitignore"
    status: completed
  - id: save-plan-file
    content: Save plan to docs/plans/2026_05_17_17-30_feature__2stairs-filters_phase-1-native-shield.plan.md
    status: completed
  - id: run-pytest
    content: Run pytest (16 tests) and document result
    status: completed
isProject: true
---

# Phase 1 — Two-stage native filtering (Shield + Scalpel)

## Objective

Align the tool with the developer ecosystem (hierarchical `.gitignore`) using two filtering stages:

1. **Shield (stage 1)**: hierarchical `.gitignore` + hardcoded security rules, on by default, pruning during `os.walk`.
2. **Scalpel (stage 2)**: YAML filters (`include_patterns`, `common_filters`, etc.) unchanged in role.

## Architecture

| Stage | Module | Source |
|-------|--------|--------|
| Shield | `craft/ignore_manager.py` | `.env`, `.env.*`, `*.pem`, `*.key`, `.git/` + per-folder `.gitignore` |
| Scalpel | `main.py` | `config.yaml` via pathspec |

## Implementation delivered

- `IgnoreManager` with per-directory cache and hierarchical semantics.
- CLI: `--no-ignore` replaces `--use-gitignore`.
- Integration in `main.py` and `craft/tree_generator.py` (`_collect_tree_paths`).
- Fixture `tests/test_projects/nested_ignore_project/` and associated tests.

## Validation

- `pytest tests`: 16 tests collected, 16 passed.
- Warnings: `gitwildmatch` deprecation in pathspec (no functional impact).

## Out of scope

`.npmignore`, `config_manager.py`, full `filter_manager` refactor.

---

## Implementation report

### Delivered changes

| File | Action |
|---------|--------|
| `craft/ignore_manager.py` | Created — `IgnoreManager` class (security + hierarchical `.gitignore`, per-directory cache) |
| `main.py` | `--no-ignore` replaces `--use-gitignore`; removed root `.gitignore` merge in YAML filters; Shield applied before Scalpel in `os.walk` |
| `craft/tree_generator.py` | `ignore_manager` parameter on `generate_tree` / `_collect_tree_paths` (same pruning as content walk) |
| `tests/test_projects/nested_ignore_project/` | Fixture (root + `frontend/` `.gitignore`, `.env.local`, `logs/`, `node_modules/`) |
| `tests/test_ignore_manager.py` | 3 unit tests (security, hierarchy, `--no-ignore`) |
| `tests/test_aicc.py` | E2E test `test_nested_gitignore_and_security_patterns` |
| `tests/setup_tests.sh` | `create_nested_ignore_project` function |
| `README.md` | Shield/Scalpel documentation, `--no-ignore`, removed `--use-gitignore` |

### Behavior

- **By default**: read `.gitignore` at each tree level + security patterns always active (`.env`, `.env.*`, `*.pem`, `*.key`, `.git/`).
- **`--no-ignore`**: disables only `.gitignore` files; security rules still apply (e.g. `.env.local` still excluded).

### Validation

```
.aicc_venv/bin/python -m pytest tests
16 passed, 54 warnings in ~2.3s
```

- Warnings: `gitwildmatch` deprecation in pathspec (pre-existing, no functional impact).
- Non-regression: `basic_project` and the initial 12 tests pass; 4 new tests (3 unit + 1 E2E).

### Notes

- `node_modules/` may still appear in output if it is contained in a concatenated `.gitignore` file (e.g. `frontend/.gitignore`) — this is not a scan of the `node_modules/` folder itself.
- `.npmignore` deferred out of Phase 1 scope.
