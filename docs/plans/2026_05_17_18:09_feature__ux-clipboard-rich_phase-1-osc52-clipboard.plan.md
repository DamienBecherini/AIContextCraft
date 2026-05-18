---
name: phase-1-osc52-clipboard
overview: Add OSC 52 fallback for clipboard copy to support SSH/headless runs without breaking the existing console flow.
todos:
  - id: update-clipboard-function
    content: Update maybe_copy_to_clipboard in main.py for pyperclip to OSC 52 fallback.
    status: completed
  - id: add-safe-logging-path
    content: Keep Rich user messages and warning log only when OSC 52 fails.
    status: completed
  - id: validate-behavior
    content: Manually validate 3 scenarios (local clipboard OK, OSC 52 fallback, OSC 52 failure).
    status: completed
  - id: publish-plan-copy
    content: Copy validated plan to docs/plans/ as YYYY_MM_DD_HH:MM_feature__ux-clipboard-rich_phase-1-osc52-clipboard.plan.md.
    status: in_progress
  - id: save-report
    content: Ask whether implementation report should be saved to plan, then act on answer.
    status: pending
isProject: false
---

# Implementation plan — OSC 52 support (SSH/headless)

## Objective
Make `--clipboard` reliable in remote/headless environments by keeping local `pyperclip` copy first, then falling back to OSC 52 when the system backend is unavailable.

## Files involved
- [main.py](/opt/AIContextCraft/main.py)
- [docs/plans/2026_05_17_18:09_feature__ux-clipboard-rich_phase-1-osc52-clipboard.plan.md](/opt/AIContextCraft/docs/plans/2026_05_17_18:09_feature__ux-clipboard-rich_phase-1-osc52-clipboard.plan.md)

## Changes to implement
1. In [main.py](/opt/AIContextCraft/main.py), add `base64` import (keep existing `sys`).
2. Modify `maybe_copy_to_clipboard(clipboard_enabled, content, console)` with this flow:
   - **Step A (local)**: try `pyperclip.copy(content)` then show current local success message.
   - **Step B (OSC 52 fallback)**: only on `pyperclip.PyperclipException` or `pyperclip.PyperclipWindowsException`:
     - encode `content` as UTF-8 base64,
     - write `\x1b]52;c;{encoded}\x07` to `stdout`,
     - call `flush()`,
     - show `[green]Content sent to clipboard via SSH (OSC 52).[/green]`.
   - **Step C (fallback error)**: wrap step B in `try/except Exception` for a clean warning log without stopping the program.
3. Preserve console ergonomics:
   - do not alter existing Rich messages outside clipboard scope,
   - keep non-blocking execution if both local clipboard and OSC 52 fail.

## Verification
1. **Local GUI case**: verify “Content copied to clipboard.” appears and content is pasteable.
2. **SSH/headless without clipboard backend**: simulate/observe `PyperclipException`, verify OSC 52 emission and success message.
3. **OSC 52 error case**: force stdout write error and confirm warning is logged without crash.

## Plan publication (requested)
After plan validation, add an execution step that:
1. copies the validated plan into `docs/plans/`,
2. renames to `YYYY_MM_DD_HH:MM_feature__ux-clipboard-rich_phase-1-osc52-clipboard.plan.md`.

---
## Implementation report

- Main change: OSC 52 fallback in `maybe_copy_to_clipboard` after `pyperclip` failure.
- Behavior:
  - local attempt kept via `pyperclip.copy(content)`,
  - OSC 52 fallback on `PyperclipException`/`PyperclipWindowsException`,
  - Rich success message for OSC 52,
  - non-blocking warning only if OSC 52 step fails.
- Modified files:
  - `main.py`
  - `docs/plans/2026_05_17_18:09_feature__ux-clipboard-rich_phase-1-osc52-clipboard.plan.md` (report appended)
- Validation:
  - lint: no issues on `main.py`,
  - tests: `21 passed`, `54 warnings`,
  - collected: `21` tests.
