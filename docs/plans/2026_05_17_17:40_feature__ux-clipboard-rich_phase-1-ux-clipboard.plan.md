---
name: phase-1-ux-clipboard
overview: Implement Phase 1 final UX with Rich (console + progress) and robust clipboard copy in headless environments, without polluting log files.
todos:
  - id: branch-and-plan-file
    content: Create feature/ux-clipboard-rich and save plan to docs/plans/2026_05_17_17:40_feature__ux-clipboard-rich_phase-1-ux-clipboard.plan.md.
    status: in_progress
  - id: deps-update
    content: Add rich and pyperclip to requirements.txt.
    status: pending
  - id: logging-rich-console-plain-file
    content: Adapt setup_logging for Rich on console and plain text in log file.
    status: pending
  - id: clipboard-cli
    content: Add --clipboard/-cb and implement pyperclip.copy with headless error handling.
    status: pending
  - id: progress-ui
    content: Use rich.progress.track in file processing loop and remove disruptive info logs.
    status: pending
  - id: tests-hardening
    content: Adjust/validate console output tests to avoid Rich ANSI effects.
    status: pending
  - id: run-pytests-venv
    content: Run tests via .aicc_venv/bin/python -m pytest tests and report collected/pass-fail/warnings.
    status: pending
  - id: implementation-report-flow
    content: Present report, ask whether to save to plan, then propose conventional commit message.
    status: pending
  - id: publish-plan-copy
    content: Copy validated plan to docs/plans/ with timestamped name YYYY_MM_DD_HH:MM_<plan-title>.plan.md.
    status: pending
isProject: false
---

# Phase 1 UX Clipboard + Rich implementation plan

## Objective
Add a smoother CLI experience with:
- a robust `--clipboard` option (no crash in SSH/headless),
- a Rich-enhanced console,
- a progress bar during processing,
- strictly plain-text `.log` files (no ANSI).

## Target files
- [requirements.txt](/opt/AIContextCraft/requirements.txt)
- [craft/utils.py](/opt/AIContextCraft/craft/utils.py)
- [main.py](/opt/AIContextCraft/main.py)
- [tests/test_aicc.py](/opt/AIContextCraft/tests/test_aicc.py)
- [docs/plans/2026_05_17_17:40_feature__ux-clipboard-rich_phase-1-ux-clipboard.plan.md](/opt/AIContextCraft/docs/plans/2026_05_17_17:40_feature__ux-clipboard-rich_phase-1-ux-clipboard.plan.md)

## Execution steps
1. Create branch `feature/ux-clipboard-rich`.
2. Save this plan to `docs/plans/2026_05_17_17:40_feature__ux-clipboard-rich_phase-1-ux-clipboard.plan.md`.
3. Add `rich` and `pyperclip` to `requirements.txt`.
4. Modernize `setup_logging` in `craft/utils.py`:
   - console with `rich.logging.RichHandler` (time/path hidden),
   - `.log` file via `logging.FileHandler` + classic text formatter,
   - prevent ANSI sequences in log files.
5. Update `main.py`:
   - add `-cb/--clipboard` to argument parser,
   - replace final `print()` with `Console().print(...)`,
   - integrate `pyperclip.copy(final_output_str)` at end of run when `args.clipboard`,
   - wrap copy in `try/except pyperclip.PyperclipException` with non-blocking warning.
6. Replace file processing loop with `rich.progress.track(...)` and remove per-file info log (`Processing ...`) that disrupts display, while keeping error logs.
7. Stabilize console output tests:
   - check `tests/test_aicc.py`,
   - if needed, disable Rich color in test context (e.g. `NO_COLOR`, `TERM=dumb` or appropriate Rich config) to avoid unexpected ANSI.
8. Run Python tests with project procedure:
   - prepare/validate `.aicc_venv` (create + install dependencies if missing),
   - run `pytest` via venv interpreter,
   - report collected count, pass/fail, warnings.
9. Produce implementation report (changes, modified files, validation), then explicitly ask whether it should be saved to the plan.
10. After answer on report save, propose a Conventional Commits message including plan file reference.
11. Publish a copy of the validated plan in `docs/plans/` renamed to `YYYY_MM_DD_HH:MM_<branch-slug>_<plan-title>.plan.md` (ASCII kebab-case title).

## Validation criteria
- `--clipboard` works when OS clipboard is available.
- In headless/SSH without clipboard backend, script does not crash and shows a clear warning.
- Console display is enriched (Rich) without hurting readability.
- `.log` files stay clean, without ANSI color codes.
- Progress displays during `final_file_list` processing.
- Tests pass with `.aicc_venv` procedure and results are reported.

---
## Implementation report

- Branch created: `feature/ux-clipboard-rich`.
- Plan saved: `docs/plans/2026_05_17_17:40_feature__ux-clipboard-rich_phase-1-ux-clipboard.plan.md`.
- Dependencies added in `requirements.txt`: `rich`, `pyperclip`.
- Logging modernized in `craft/utils.py`:
  - console via `RichHandler` (`show_time=False`, `show_path=False`),
  - `.log` file kept as plain `FileHandler`.
- CLI UX improved in `main.py`:
  - `-cb/--clipboard` option,
  - final copy via `pyperclip.copy(final_output_str)`,
  - headless/SSH handling via `try/except pyperclip.PyperclipException` with non-blocking warning,
  - end messages migrated to `Console().print(...)`.
- File processing: classic loop replaced with `rich.progress.track(...)`.
- Display cleanup: removed per-file info log during progress; kept error logs.
- Console output tests hardened in `tests/test_aicc.py` with `NO_COLOR=1` and `TERM=dumb` in subprocess.

### Validation

- Command run: `./.aicc_venv/bin/python -m pytest tests`
- Log generated: `logs/unit_tests_run_20260517_175908.log`
- Tests collected: `21`
- Result: `21 passed`
- Warnings: `54` (`pathspec` `gitwildmatch` deprecations)
