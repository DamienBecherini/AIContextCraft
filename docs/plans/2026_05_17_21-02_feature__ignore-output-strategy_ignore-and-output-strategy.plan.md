---
name: ignore-and-output-strategy
overview: Align CLI ignore-file behavior with help/docs, add selective skip by ignore type, and introduce a bot-friendly output strategy without breaking current human UX.
todos:
  - id: create-dedicated-branch
    content: Create and use dedicated branch feature/ignore-output-strategy before any code changes.
    status: pending
  - id: align-ignore-contract
    content: Align --no-ignore contract for 4 supported ignore files and expose selective control in IgnoreManager + CLI.
    status: pending
  - id: add-cli-flags
    content: Implement --skip-ignore-files and --ignore-files with strict validation and documented priority/conflict rules.
    status: pending
  - id: add-output-modes
    content: Introduce output-format/output-destination/quiet with stdout-stderr separation for bots.
    status: pending
  - id: update-help-readme
    content: Update argparse help and README with exact behavior and examples.
    status: pending
  - id: expand-tests
    content: Extend unit/CLI tests for global ignore, selective skip, output formats, and no file creation.
    status: pending
  - id: run-project-tests
    content: Run pytest via .aicc_venv and report collected/pass-fail/warnings.
    status: pending
  - id: publish-plan-copy
    content: Publish validated plan copy in docs/plans/ with kebab-case timestamped name.
    status: pending
isProject: false
---

# Finalize ignore files and CLI output strategy

## Objective
Make ignore option behavior explicit and consistent (`--no-ignore` global + selective skip), then harden bot/CI integration with stable machine output (opt-in JSON) while keeping current human UX as default.

## Scope
- **Ignore files**: keep `--no-ignore` as global disable for all supported ignore files.
- **Selective skip**: add a practical way to disable only certain ignore file types.
- **Console output**: keep human output by default, add structured machine mode.
- **Documentation and help**: align user-facing text with actual behavior.
- **Tests**: cover CLI parsing/validation, ignore behavior, and output formats.

## Proposed changes

### 0) Create dedicated branch
- Create and use branch: `feature/ignore-output-strategy`.
- Run all implementation on this branch to isolate scope.

### 1) Clarify and consolidate ignore logic
- Contractually confirm `--no-ignore` disables the full ignore-files layer (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) while keeping security rules.
- Extend `IgnoreManager` configuration to accept a list of selectively disabled ignore file types.
- Target files:
  - [`/opt/AIContextCraft/craft/ignore_manager.py`](/opt/AIContextCraft/craft/ignore_manager.py)
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)

### 2) Introduce selective skip CLI UX (both syntaxes)
- Add `--skip-ignore-files=gitignore,dockerignore,cursorignore,npmignore` (recommended syntax).
- Add `--ignore-files=...` (complementary syntax) with clear validation/conflict rules.
- Interaction rules:
  - `--no-ignore` has global priority.
  - if `--no-ignore` + selective flags: explicit warning or error (single documented and tested decision).
  - strict value validation (typo => clear usage error).
- Target file:
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)

### 3) Recommended output strategy (human default, bot opt-in)
- Add `--output-format human|json` (default: `human`).
- In `json`: stable structured result on `stdout`; logs/diagnostics on `stderr`.
- Add `--quiet` (practical inverse of `verbose`) to reduce non-essential output.
- Introduce `--output-destination file|stdout|both|none` to control output file creation.
- Keep simple robust exit codes (`0` success, `2` usage/arguments, `1` runtime error).
- Target files:
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)
  - (if present) result render/export module used by `main.py`.

### 4) Update CLI help and documentation
- Align help strings with real multi-ignore-file behavior.
- Document ignore option matrix (`--no-ignore`, `--skip-ignore-files`, `--ignore-files`).
- Document output modes (`human/json`, destination, `--quiet`) and CI/bot examples.
- Main target:
  - [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md)

### 5) Test coverage
- Extend unit and/or CLI tests for:
  - global `--no-ignore` on all ignore file types.
  - selective skip by type.
  - new flag conflicts/validation.
  - stable `json` output with clean `stdout`.
  - no file creation when `--output-destination=stdout|none`.
- Target files:
  - [`/opt/AIContextCraft/tests/test_ignore_manager.py`](/opt/AIContextCraft/tests/test_ignore_manager.py)
  - [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py)

## Validation
- Run tests via project local environment (`.aicc_venv`) per project procedure (`pytest`).
- Manually verify reference commands:
  - default human case,
  - bot JSON case (clean `stdout`),
  - global ignore and selective skip cases.

## Risks and safeguards
- **UX risk**: too many similar ignore options.
  - Safeguard: one recommended syntax (`--skip-ignore-files`) + clear error messages.
- **Compatibility risk**: existing scripts depend on console output.
  - Safeguard: `human` remains default; `json` strictly opt-in.
- **`stdout` ambiguity risk**: mixed logs/result.
  - Safeguard: strong contract `stdout=data`, `stderr=diagnostic` in `json` mode.

## Plan publication (requested)
- Copy this validated plan into `docs/plans/`.
- Rename copy to `YYYY_MM_DD_HH-MM_<branch-slug>_<plan-title>.plan.md` with ASCII kebab-case title.

---
## Implementation report

### Changes made
- Dedicated branch created and used: `feature/ignore-output-strategy` (in `AIContextCraft`).
- `--no-ignore` contract aligned: global disable of hierarchical ignore files (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) with security rules kept.
- Selective ignore skip added:
  - `--skip-ignore-files=...` (disable only listed types)
  - `--ignore-files=...` (keep only listed types, inverse alias)
  - strict type validation and mutual exclusion of both flags.
- Bot-friendly output mode added:
  - `--output-format human|json`
  - `--output-destination file|stdout|both|none`
  - `--quiet` (minimal console logs).
- In `json` mode, structured report on `stdout` with clean output control.
- Help/documentation updated for real behavior and new flags.
- Tests added/extended for global ignore, selective skip, and JSON bot output.

### Modified files
- `main.py`
- `craft/ignore_manager.py`
- `craft/utils.py`
- `tests/test_aicc.py`
- `tests/test_ignore_manager.py`
- `README.md`

### Validation and tests
- Command run: `cd /opt/AIContextCraft && .aicc_venv/bin/python -m pytest tests`
- Tests collected: **33**
- Result: **33 passed**
- Warnings: **96** (`pathspec` `gitwildmatch` deprecations, no failures)

### Notes
- Fix after context incident: branch initially created in wrong repo, cleaned in `wp-manager`, then recreated correctly in `AIContextCraft`.
