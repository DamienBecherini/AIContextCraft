---
name: fix special-char paths
overview: Fix handling of paths with special characters and Windows separators in AIContextCraft, from YAML loading through pattern matching, with regression tests and configuration documentation.
todos:
  - id: improve-yaml-error
    content: Improve yaml.YAMLError message with concrete guidance on backslashes/quotes
    status: completed
  - id: normalize-patterns
    content: Implement pattern normalization (\ to /) before PathSpec
    status: completed
  - id: add-special-char-tests
    content: Add tests and fixtures for Unicode + Windows paths + guided YAML error
    status: completed
  - id: update-readme-config
    content: Document YAML/pattern best practices for special characters
    status: completed
  - id: publish-plan-aicontextcraft
    content: Publish validated plan copy in AIContextCraft docs/plans/ with timestamped name
    status: in_progress
isProject: false
---

# Special-character path fix (AIContextCraft)

## Objective
Enable reliable use of folder/file names containing Unicode characters (emoji, accents, etc.) and Windows separators (`\`) in `include_patterns`, without parsing errors or filtering mismatches.

## Current state
- Configuration loading relies on `yaml.safe_load` in [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- A value like `"🚀 Projects\🏰 Proxmox Homelab"` in a double-quoted YAML scalar fails before any application logic (`unknown escape character`).
- The matching engine compares paths normalized to `/` during scanning, but user patterns are not normalized symmetrically.

## Implementation plan
1. **Harden YAML loading with guided messages**
   - In [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py), enrich the `except yaml.YAMLError` block to detect escape errors related to backslashes and show clear guidance:
     - prefer `/` in patterns,
     - or use YAML single quotes,
     - or double backslashes (`\\\\`) if needed.
   - Keep explicit error output (no ambiguous silent fallback).

2. **Normalize user path patterns**
   - Add centralized pattern normalization in [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py) before creating `PathSpec`:
     - convert Windows `\` separators to `/`,
     - preserve Unicode characters as-is,
     - apply normalization to `include_patterns`, `common_filters`, `project_only_filters`, `tree_only_filters`.
   - Verify existing matching logic (`relative_path.replace('\\', '/')`) stays consistent with this normalization.

3. **Add targeted regression tests**
   - Extend [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py) with dedicated cases:
     - valid config with emoji + `/` pattern => expected inclusion,
     - Windows-style paths (`\\`) => identical behavior after normalization,
     - invalid YAML (double-quoted + invalid escape) => expected guided error message.
   - Add minimal project fixtures under [`/opt/AIContextCraft/tests/test_projects`](/opt/AIContextCraft/tests/test_projects) with Unicode folders/files.

4. **Document recommended syntax**
   - Update the config section of [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md) with safe examples for special paths:
     - recommended `/` usage,
     - Unicode examples,
     - YAML reminder (`'...'` or `\\\\` in double-quoted strings).

5. **Validate and publish the plan in AIContextCraft**
   - Run relevant tests.
   - Copy the validated plan into `docs/plans/` with format `YYYY_MM_DD_HH:MM_<branch-slug>_<plan-title>.plan.md` (title in ASCII kebab-case).

## Expected outcome
- No more blocking for Unicode names when YAML config is well formed.
- Patterns entered with Windows separators work predictably via normalization.
- Users have clear documentation to avoid YAML backslash-related errors.

---

## Implementation report

Implementation completed; all plan todos are done.

- Fix applied in AIContextCraft for special/Unicode paths and Windows separators in patterns.
- Improved YAML error message to clearly guide invalid `\` cases in double quotes.
- Centralized pattern normalization (`\` -> `/`) before PathSpec creation.
- Regression tests added (Unicode, backslashes, guided YAML error).
- Documentation updated with recommended examples.
- Plan copy published at `docs/plans/2026_05_16_23:28_main_fix-special-char-paths.plan.md`.

### Modified files

- `aicc.py`
- `tests/test_aicc.py`
- `README.md`
- `tests/test_projects/special_chars_project/config_slash.yaml`
- `tests/test_projects/special_chars_project/config_backslash.yaml`
- `tests/test_projects/special_chars_project/🚀 Projects/🏰 Proxmox Homelab/context.txt`
- `tests/test_projects/special_chars_project/other/ignored.txt`
- `docs/plans/2026_05_16_23:28_main_fix-special-char-paths.plan.md`

### Validation

- Lints checked on edited files: no errors.
- Tests executed:
  - `cd /opt/AIContextCraft && .venv/bin/python -m pytest -q --confcutdir=/opt/AIContextCraft tests/test_aicc.py`
- Result: `4 passed`
