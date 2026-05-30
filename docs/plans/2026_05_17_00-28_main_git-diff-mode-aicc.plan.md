---
name: git-diff-mode-aicc
overview: Add a CLI `--git-diff` mode that generates a Markdown report of the Git diff between two revisions, bypassing standard concatenation, with error handling and automated tests.
todos:
  - id: cli-git-diff-arg
    content: Add CLI `--git-diff` argument with two Git references.
    status: completed
  - id: git-diff-helper
    content: Implement robust `git diff` utility function.
    status: completed
  - id: main-short-circuit
    content: Add `if args.git_diff` flow in `main()` to bypass tree/concat and emit Markdown output.
    status: completed
  - id: tests-git-diff-mode
    content: Add unit tests for success and failure of the new Git diff mode.
    status: in_progress
  - id: docs-cli-update
    content: Document `--git-diff` in README with usage example.
    status: pending
  - id: plan-publication-step
    content: Include plan copy/rename step to docs/plans/ with timestamped format.
    status: pending
isProject: false
---

# Add Git Diff mode to AIContextCraft

## Objective
Implement an alternate `--git-diff <REF_A> <REF_B>` mode that produces a Markdown file containing the raw Git diff between two revisions, then exits without running standard tree scan/concatenation logic.

## Technical scope
- **CLI input**: dedicated argument in [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- **Diff retrieval**: centralize `git` calls in a robust utility in [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- **Execution routing**: early path in `main()` before tree generation and file reading.
- **Tests**: cover the new mode in [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py).
- **User documentation**: document the option and examples in [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md).

## Implementation plan
1. **Extend the CLI interface**
   - Add `parser.add_argument('--git-diff', nargs=2, metavar=('REF_A', 'REF_B'), ...)`.
   - Clearly define this mode as exclusive from the classic concatenation flow.

2. **Create a dedicated Git utility**
   - Add `get_git_diff(repo_path: Path, ref_a: str, ref_b: str) -> str`.
   - Expected behavior:
     - verify `repo_path` is a Git repo (`git rev-parse --is-inside-work-tree`),
     - run `git diff ref_a ref_b`,
     - return `stdout`.
   - Explicit error handling:
     - Git missing (`FileNotFoundError`),
     - non-Git directory,
     - invalid revisions / failed `git diff`.

3. **Wire the mode in `main()`**
   - Add an early `if args.git_diff:` block after base path/config initialization.
   - In that block:
     - read the two revisions,
     - call `get_git_diff(...)`,
     - build dedicated Markdown output (title + ```diff block),
     - compute stats with `get_file_stats(...)`,
     - force `.md` extension if configured output is `.txt`,
     - write the file (or simulate with `--dry-run`),
     - print final messages and exit cleanly.
   - Ensure no tree/concat logic runs in this mode.

4. **Define final output format**
   - Header similar to existing format (date, statistics).
   - Specific body:
     - `# Git Diff: <REF_A> -> <REF_B>`
     - `diff` code block with raw `git diff` output.
   - No changes case: inject a readable message (e.g. `No differences detected between these revisions.`) in the content block.

5. **Add unit tests**
   - At least one success test in [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py):
     - create a temporary mini Git repo,
     - make two commits,
     - run `aicc.py --git-diff <sha1> <sha2> ...`,
     - verify return code, file existence, `diff` block presence, and expected `+/-` lines.
   - One error test (invalid reference):
     - verify `returncode != 0`,
     - verify understandable error message in `stderr`.

6. **Update documentation**
   - Add `--git-diff` to the CLI options table in [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md).
   - Add a real command example.
   - Clarify that this mode produces a global diff, not file concatenation.

## Planned validation
- Run project unit tests.
- Manually verify a successful run on a local Git repo and an error run (invalid ref).
- Verify Markdown output and that standard logic is short-circuited.

## Plan publication (requested)
- After plan validation, add an execution step that:
  - copies the validated plan file into `docs/plans/`,
  - renames the copy to `YYYY_MM_DD_HH-MM_<branch-slug>_<plan-title>.plan.md` with ASCII kebab-case title.

---
## Implementation report

### Changes made
- Added CLI argument `--git-diff REF_A REF_B` in `aicc.py`.
- Added `get_git_diff(repo_path, ref_a, ref_b)` with Git repo check and error handling (`FileNotFoundError`, invalid refs, non-Git directory).
- Added early path in `main()` for Git Diff mode without standard tree/concat execution.
- Dedicated Markdown output generation:
  - title `# Git Diff: <REF_A> -> <REF_B>`
  - `diff` code block
  - explicit message when no differences.
- Automatic `.txt` to `.md` output conversion in this mode.
- Updated documentation in `README.md` (CLI option + example).

### Modified files
- `/opt/AIContextCraft/aicc.py`
- `/opt/AIContextCraft/tests/test_aicc.py`
- `/opt/AIContextCraft/README.md`

### Validation and tests
- Tests run: `pytest /opt/AIContextCraft/tests/test_aicc.py`
  - collected: 6
  - result: 6 passed
  - warnings: 1 `PytestCacheWarning` (pytest cache permissions under `/opt`)
- Manual mode verification:
  - success case: expected `.md` report with diff (`+print('v2')`, etc.)
  - error case: invalid reference returns `exit=1` with explicit Git message.
