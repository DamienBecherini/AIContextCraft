---
name: llm-output-formats
overview: Introduce `text`, `xml`, and `markdown` output formats via a dedicated module while strictly preserving default historical behavior and covering special CLI/test cases.
todos:
  - id: cli-config-format
    content: "Add `--format` and `output_format: text` with CLI > config resolution."
    status: completed
  - id: formatter-module
    content: Create `craft/formatter.py` with text/xml/markdown renderers and a single render API.
    status: completed
  - id: main-pipeline-refactor
    content: Refactor `main.py` to collect file data and delegate rendering to the formatter.
    status: completed
  - id: special-modes-policy
    content: Stabilize multi-format `--tree-only` and keep `--git-diff` on its dedicated Markdown flow.
    status: completed
  - id: tests-formats
    content: Add xml/markdown/tree-only tests and an XML escaping test.
    status: in_progress
  - id: python-test-procedure
    content: Validate via `.aicc_venv` and report collected/pass-fail/warnings.
    status: pending
  - id: publish-plan-copy
    content: Publish a timestamped plan copy in docs/plans/ with kebab-case title.
    status: pending
isProject: false
---

# Phase 1 - LLM output formats (Text/XML/Markdown)

## Objective
Add a multi-format rendering engine for concatenation output in AIContextCraft, with `text` as the strictly backward-compatible default, then `xml` and `markdown` as LLM-optimized formats.

## Current state (baseline)
- Final generation is centralized in [`main.py`](/opt/AIContextCraft/main.py) with hard-coded text concatenation (tree + extensions + `--- FILE:` sections).
- `--git-diff` mode follows a dedicated flow and already produces a standalone Markdown report.
- CLI tests are grouped in [`tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py).
- No formatting abstraction exists yet in `craft/`.

## Implementation strategy

### 1) Extend configuration/CLI without breaking existing behavior
- In [`main.py`](/opt/AIContextCraft/main.py), add `--format` with `choices=['text', 'xml', 'markdown']`.
- Add `output_format: 'text'` to `DEFAULT_CONFIG` and read config/CLI with CLI priority.
- Keep output identical to today when `format == 'text'` (separators, titles, overall structure).

### 2) Create a dedicated rendering module
- Create [`craft/formatter.py`](/opt/AIContextCraft/craft/formatter.py) with a single API, e.g.:
  - `build_output(format_type, intro_header, project_tree, extension_summary, files_data, tree_only=False)`
- Standardize `files_data` as a list of `(relative_path, content)` tuples (or equivalent structure).
- Implement three renderers:
  - `text`: strict reproduction of current output.
  - `xml`: `<repository>`, `<directory_structure>`, `<files>`, `<file path="...">` structure.
  - `markdown`: `# Project Context`, `## Directory Structure`, `## Files`, code blocks with language hint by extension (fallback `text`).
- Escape XML content correctly (`&`, `<`, `>`) for valid documents.

### 3) Refactor the generation pipeline in `main.py`
- Replace `all_files_content` (pre-formatted strings) with raw per-file data collection.
- After read/transformations (`--strip-comments`, `--headers-only`), delegate final rendering to `craft.formatter`.
- Keep the existing global header (descriptive sentence, date, statistics), then inject the formatted body.

### 4) Define special modes clearly
- `--tree-only`:
  - `text`: keep current tree + extensions output.
  - `xml`: produce `<repository><directory_structure>...</directory_structure></repository>` without `<files>`.
  - `markdown`: produce only context/tree section, no files section.
- `--git-diff`:
  - Keep current flow unchanged (dedicated Markdown report) to avoid functional regression.
  - Ignore `--format` in this mode with an explicit log for deterministic behavior.

### 5) Complete test coverage
- Extend [`tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py) with:
  - `--format xml` test (presence of `<repository>`, `<directory_structure>`, `<files>`, `<file path="...">`).
  - `--format markdown` test (presence of `# Project Context`, `## Directory Structure`, `## Files`).
  - `--tree-only --format xml|markdown` test (no files section).
  - `text` backward-compatibility test (existing robust comparison preserved).
- Add XML escaping test on content including `<tag>&value` if useful.

### 6) Validation and Python test execution (project procedure)
- Use local `.aicc_venv`:
  - create venv if missing, install dependencies via `requirements.txt`.
  - run `pytest` with venv Python (targeted then full suite if needed).
- Report in the implementation summary:
  - number of tests collected,
  - pass/fail status,
  - warnings if any.

### 7) Plan publication (requested)
- Determine current branch name.
- Copy validated plan into `docs/plans/`.
- Rename to `YYYY_MM_DD_HH:MM_<branch-slug>_<plan-title>.plan.md`.
- Normalize `<plan-title>` to ASCII kebab-case.

## Acceptance criteria
- `--format` accepts `text|xml|markdown`.
- Without `--format`, output is strictly identical to historical behavior.
- `--tree-only` and `--git-diff` have explicit, stable, tested behavior.
- New format tests pass without breaking existing tests.
- Plan is published in `docs/plans/` with the expected timestamped name.

---
## Implementation report

### Changes made
- Added `--format {text,xml,markdown}` in `main.py`.
- Added `output_format: "text"` in `config.yaml` and `DEFAULT_CONFIG` for backward compatibility.
- Created `craft/formatter.py` with single API `build_output(...)` and three renderers:
  - `text`: unchanged historical output
  - `xml`: `<repository>`, `<directory_structure>`, `<files>`, `<file path=\"...\">`
  - `markdown`: `# Project Context`, `## Directory Structure`, `## Files`, with language detection for code blocks
- Refactored `main.py` output pipeline:
  - collect files as raw `(relative_path, content)` data
  - delegate final rendering to formatter
  - handle `--tree-only` consistently for all formats
- `--git-diff` mode kept on dedicated Markdown flow, with explicit log if `--format` is provided.

### Modified files
- `main.py`
- `config.yaml`
- `craft/formatter.py` (new)
- `tests/test_aicc.py`
- `docs/plans/2026_05_17_17:29_feature__llm-formats_llm-output-formats.plan.md` (report appended)

### Validation / tests
- Environment used: `.aicc_venv` (project local Python).
- Command: `.aicc_venv/bin/python -m pytest tests`
- Result:
  - tests collected: 21
  - status: 21 passed
  - warnings: 54
- Warning detail:
  - `pathspec` deprecation warnings on `gitwildmatch` (not introduced by this phase).
