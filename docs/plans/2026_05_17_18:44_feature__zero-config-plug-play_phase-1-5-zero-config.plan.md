---
name: zero-config-plug-play
overview: "Implement a plug-and-play phase: XML by default, auto clipboard with size limit, output under build/, and config detection without forced file creation."
todos:
  - id: cli-clipboard-redesign
    content: Redesign CLI clipboard arguments and apply size limit before copy in both execution flows.
    status: completed
  - id: zero-config-defaults
    content: Implement config auto-detection without disk write and dynamic default output under build/ by format.
    status: completed
  - id: tests-and-docs
    content: Update README and tests for new XML default, clipboard-limit/no-clipboard, and Zero-Config mode.
    status: completed
  - id: validate-and-publish-plan
    content: Run pytest via .aicc_venv, collect evidence, then publish plan in docs/plans/ with conforming timestamped name.
    status: completed
isProject: false
---

# Implementation plan — Phase 1.5 Zero-Config Plug & Play

## Objective

Deliver a frictionless default experience: run without mandatory config file, `xml` format by default, automatic but bounded clipboard copy, and clean output path under `build/`.

## Target files

- [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)
- [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py)
- [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md)

## Technical changes

1. **Redesign clipboard CLI options in `main.py`**

- Replace boolean `--clipboard` with limit `-cb/--clipboard-limit` (float, default `10.0` MB).
- Add `--no-clipboard` for explicit disable.
- Clear policy: auto-copy if not disabled **and** size <= limit.

2. **Add size guard before copy**

- Compute actual size of `final_output_str` in bytes (`len(final_output_str.encode(args.encoding))`).
- Apply the same check in both outputs (`--git-diff` and standard flow) before `maybe_copy_to_clipboard`.
- On exceed, show user warning via `rich` and log non-copy decision.

3. **Switch format/output defaults to plug-and-play**

- Default output to `xml` (CLI + config fallback).
- If no `--output` and no valid `output_path` in config, build dynamically `build/aicc_context.<ext>` with mapping:
  - `text -> txt`
  - `xml -> xml`
  - `markdown -> md`
- Keep existing timestamp behavior, then ensure `mkdir(parents=True, exist_ok=True)`.

4. **Implement Zero-Config without YAML creation**

- If `--config` is absent, search target folder (`project_path` or `.`) in order: `.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config-concat-code.yaml`.
- If found: load and log auto-detected path.
- If not found: stay in in-memory config (`DEFAULT_CONFIG`) and log Zero-Config mode explicitly.
- Remove automatic `config.yaml` creation on disk.

5. **Update user documentation**

- Update options table, `--help` snapshot, and examples in [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md).
- Document clearly:
  - XML default format,
  - automatic clipboard with 10 MB limit,
  - `--no-clipboard`,
  - config auto-detection without forced write.

6. **Adapt existing tests and extend coverage**

- Adjust tests affected by default change (`text` -> `xml`) by passing `--format text` when assertions depend on text format.
- Add/update tests for:
  - no copy above limit,
  - copy disabled via `--no-clipboard`,
  - `build/aicc_context.<ext>` output fallback,
  - automatic config name detection,
  - no `config.yaml` creation.

7. **Mandatory validation (project procedure)**

- Verify/initialize `.aicc_venv` then run:
  - `.aicc_venv/bin/python -m pytest tests`
- Report in summary:
  - number of tests collected,
  - pass/fail status,
  - warnings if any.

8. **Plan publication (requested)**

- Copy validated plan to `docs/plans/`.
- Rename to `YYYY_MM_DD_HH:MM_feature__zero-config-plug-play_phase-1-5-zero-config.plan.md` (ASCII kebab-case title).

## Targeted risks

- Test compatibility regression due to new default format.
- Clipboard behavior inconsistency between standard flow and `--git-diff` if guard is not shared.
- User confusion if `CLI > auto-detected config > defaults` priority is not clearly logged.

## Acceptance criteria

- `python main.py` runs without prior config, no YAML creation, output under `build/`.
- Default output is XML.
- Clipboard copy only when allowed and under limit.
- README aligned with actual CLI behavior.
- `pytest` suite green with collection/result/warning evidence.

---
## Implementation report

### Changes made
- `main.py`
  - Replaced `--clipboard` with `-cb/--clipboard-limit` (default `10.0`) and added `--no-clipboard`.
  - Added size guard (`len(final_output_str.encode(args.encoding))`) before copy, in standard and `--git-diff` flows.
  - Default format set to `xml` (CLI + fallback).
  - Dynamic output fallback to `build/aicc_context.<ext>` (`txt|xml|md`) when no output provided.
  - Zero-Config: auto-search `.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config.yaml`.
  - Removed automatic `config.yaml` creation on disk.
  - `--git-diff` mode adjusted to force `.md` output.

- `tests/test_aicc.py`
  - Updated text-format-dependent tests with `--format text`.
  - Added `--no-clipboard` in non-clipboard tests for stability.
  - Added tests: clipboard limit, `--no-clipboard`, `build/aicc_context.<ext>` fallback, `.aicc.yaml` auto-detection, no `config.yaml` creation.

- `README.md`
  - Updated CLI options (`--clipboard-limit`, `--no-clipboard`), `xml` default, Zero-Config behavior, `build/` output fallback.
  - Updated `--help` snapshot and examples.

### Validation / tests
- Environment: existing `.aicc_venv` (used).
- Project procedure command:
  - `.aicc_venv/bin/python -m pytest tests` (blocked locally by external `conftest` in active workspace).
- Isolated project run:
  - `PYTHONPATH=/opt/AIContextCraft .aicc_venv/bin/python -m pytest /opt/AIContextCraft/tests --rootdir=/opt/AIContextCraft`
- Results:
  - Tests collected: `26`
  - Status: `26 passed / 0 failed`
  - Warnings: `54` (`pathspec` `gitwildmatch` deprecations)
