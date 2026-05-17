# AI Context Craft

<div align="center">
  <h1>AI Context Craft</h1>
  <p><strong>The essential CLI tool for intelligently packaging your codebase for Large Language Models.</strong></p>
  
  <p>
    <a href="https://github.com/DamienBecherini/AIContextCraft"><img src="https://img.shields.io/badge/GitHub-AIContextCraft-181717?logo=github" alt="GitHub"></a>
    <a href="https://creativecommons.org/publicdomain/zero/1.0/"><img src="https://img.shields.io/badge/license-CC0_1.0-blue.svg" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status"></a>
  </p>
</div>

---

**AI Context Craft** solves a common problem for developers using LLMs like GPT-4, Claude, or Llama: how do you feed an entire codebase to an AI that has a limited context window? This tool lets you intelligently select, filter, and concatenate your project files into a single, clean, context-optimized text file, ready to be pasted into any AI chat.

Stop manually copying and pasting files and start crafting the perfect context in seconds.

## ✨ Key Features

*   **Powerful (Optional) YAML Configuration**: Define exactly what to include and exclude with auto-detected config files (`.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config-concat-code.yaml`).
*   **Intelligent Two-Step Filtering**: A robust `include-then-exclude` logic gives you granular control over your context. First, specify what you want with `include_patterns`, then clean it up with various exclusion filters.
*   **Advanced Python Code Processing**:
    *   `--strip-comments`: Reliably remove all comments and docstrings using Abstract Syntax Tree (AST) parsing, not just simple regex.
    *   `--headers-only`: Create a high-level summary of your code by extracting only class and function signatures and their docstrings.
*   **Customizable Project Tree Generation**: Automatically generate a filtered file tree with sizes, per-extension totals, and visual markers (`●` concatenated, `○` tree-only via `project_only_filters`) to give the LLM a clear overview of the project structure.
*   **Tree-Only Mode**: Use `--tree-only` to emit only the filtered project tree (sizes and per-extension totals) without file contents—useful for lightweight structural overviews.
*   **Robust File Encoding**: Reads files as UTF-8 by default (`--encoding`); on decode failure, detects encoding via `charset-normalizer` and falls back to a controlled `replace` strategy with an explicit warning instead of silent data loss.
*   **Two-Stage Filtering (Shield + Scalpel)**:
    *   **Stage 1 (Shield, on by default):** Hierarchical ignore files (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) are applied during directory traversal for fast pruning, plus hardcoded security patterns (`.env`, `.env.*`, `*.pem`, `*.key`, `.git/`) that always apply.
    *   **Stage 2 (Scalpel):** YAML `include_patterns` and exclusion filters refine what remains.
    *   Use `--no-ignore` to disable all hierarchical ignore files while keeping security exclusions.
    *   Use `--skip-ignore-files` or `--ignore-files` for selective control by ignore type.
*   **Built-in Utilities**:
    *   Automatic token and size calculation with `tiktoken`.
    *   Verbose logging for easy debugging.
*   **LLM-Optimized Output Formats**:
    *   `--format text|xml|markdown` lets you target different AI workflows (`xml` default).
    *   `xml` is recommended for Anthropic (Claude) and OpenAI usage because it provides strongly structured context sections such as `<repository>`, `<directory_structure>`, and `<files>`.
*   **Smart Clipboard Integration**:
    *   Clipboard copy is automatic by default up to 10 MB (`-cb/--clipboard-limit MB`).
    *   Use `--no-clipboard` to disable automatic clipboard copy completely.
    *   Includes OSC 52 support, so clipboard copy also works from remote Linux sessions over SSH when the terminal supports it.
*   **Dedicated Git Diff Mode**:
    *   `--git-diff REF_A REF_B` generates a Markdown diff report between two revisions.
    *   Ideal for AI-assisted Pull Request descriptions, review summaries, and change analysis.
*   **Modern Console UX**:
    *   Rich progress bars and colored logs improve readability and feedback on large repositories.

## 🚀 Quick Start

### 1. Installation

Currently, you can run the script directly by cloning the repository.

```bash
# Clone the repository
git clone https://github.com/DamienBecherini/AIContextCraft.git
cd AIContextCraft
 
# (Recommended) Create and activate a virtual environment
python -m venv .aicc_venv
source .aicc_venv/bin/activate  # On Windows, use `.aicc_venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### 2. Usage

Run the script from your terminal. By default, it scans the current project, auto-detects config files if present (`.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config-concat-code.yaml`), and writes output to `build/aicc_context.<ext>` (`xml` by default).

```bash
# Generate context for the current directory
python main.py

# Specify project and output paths
python main.py -p /path/to/your/project -o /path/to/output/context.txt
```

`python aicc.py` remains supported as a compatibility alias (same behavior as `main.py`).

#### Command-Line Options

| Flag                 | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `-c`, `--config`     | Path to your YAML configuration file.                                     |
| `-p`, `--project`    | Path to the target project directory (default: current dir).              |
| `-o`, `--output`     | Path for the generated output file.                                       |
| `--strip-comments`   | Remove comments and docstrings from code files.                           |
| `--headers-only`     | Extract only function/class signatures and docstrings from Python files.  |
| `--tree-only`        | Generate only the project tree (sizes, extensions), without file contents. |
| `--encoding ENCODING` | Target encoding for reading files (default: `utf-8`; auto-detection on failure). |
| `--no-ignore`        | Disable all hierarchical ignore files (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) while security patterns still apply. |
| `--skip-ignore-files TYPES` | Disable only selected ignore types (`gitignore,dockerignore,cursorignore,npmignore`). |
| `--ignore-files TYPES` | Enable only selected ignore types (inverse alias of `--skip-ignore-files`). |
| `--git-diff REF_A REF_B` | Generate a Markdown report with the global Git diff between two revisions. |
| `--format {text,xml,markdown}` | Choose output format (`xml` default, or `text`/`markdown`). |
| `--output-format {human,json}` | Execution reporting mode (`human` default, `json` for bot-friendly automation). |
| `--output-destination {file,stdout,both,none}` | Where generated content is written (`file` default). |
| `-cb MB`, `--clipboard-limit MB` | Maximum size in MB for automatic clipboard copy (default: `10.0`). |
| `--no-clipboard` | Disable automatic clipboard copy completely. |
| `--no-timestamp`     | Do not append a timestamp to the output filename.                         |
| `--dry-run`          | Run the script without writing any files to see what would be included.   |
| `-v`, `--verbose`    | Print detailed processing information to the console.                     |
| `-q`, `--quiet`      | Minimize console logs (errors only).                                      |

#### CLI Help Snapshot (`python main.py --help`)

```text
usage: main.py [-h] [-c CONFIG] [-p PROJECT] [-o OUTPUT] [--no-timestamp]
               [--strip-comments] [--headers-only] [--tree-only] [--dry-run]
               [--encoding ENCODING] [--no-ignore]
               [--skip-ignore-files SKIP_IGNORE_FILES]
               [--ignore-files IGNORE_FILES] [--git-diff REF_A REF_B]
               [--format {text,xml,markdown}] [--output-format {human,json}]
               [--output-destination {file,stdout,both,none}] [-cb MB]
               [--no-clipboard] [-v] [-q]

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to YAML config file.
  -p PROJECT, --project PROJECT
                        Path to target project directory.
  -o OUTPUT, --output OUTPUT
                        Path to output file.
  --no-timestamp        Do not append timestamp to output filename.
  --strip-comments      Remove comments from files.
  --headers-only        Keep only function/method signatures.
  --tree-only           Generate only project tree (sizes/extensions), without file contents.
  --dry-run             Simulate run without writing output file.
  --encoding ENCODING   File encoding (default: utf-8).
  --no-ignore           Disable all hierarchical ignore files (.gitignore, .dockerignore, .cursorignore, .npmignore), security rules still apply.
  --skip-ignore-files SKIP_IGNORE_FILES
                        Disable only listed ignore types.
  --ignore-files IGNORE_FILES
                        Keep only listed ignore types (inverse alias).
  --git-diff REF_A REF_B
                        Special mode: generate global Git diff Markdown report between two revisions.
  --format {text,xml,markdown}
                        Output format: xml (default), text or markdown.
  --output-format {human,json}
                        Execution report format.
  --output-destination {file,stdout,both,none}
                        Where generated content is written.
  -cb MB, --clipboard-limit MB
                        Maximum size in MB for automatic clipboard copy (default: 10.0).
  --no-clipboard        Disable automatic clipboard copy.
  -v, --verbose         Print detailed processing information.
  -q, --quiet           Minimize console logs (errors only).
```

### Example Workflow

Generate a context for a Python project with comments stripped (hierarchical ignore files and security filters apply by default):

```bash
python main.py --project ./my-python-app --strip-comments -v
```

On large repositories (Node, Python, etc.), ignored folders such as `node_modules/` or `.venv/` are pruned during traversal before YAML filters run, which speeds up scanning significantly.

This creates a file in `build/` (default `build/aicc_context.xml`) containing the project tree and the cleaned content of all relevant files.

Bot-friendly JSON execution report to `stdout` without creating output files:

```bash
python main.py --project ./my-python-app --output-format json --output-destination stdout --no-clipboard
```

Generate a dedicated Markdown diff report (without running the standard concatenation flow):

```bash
python main.py --project ./my-python-app --git-diff HEAD~1 HEAD --output ./build/git_diff_report.txt --no-timestamp
```

Generate XML output optimized for LLM ingestion and increase clipboard limit for large projects:

```bash
python main.py --project ./my-python-app --format xml --clipboard-limit 25
```

## 🧭 Architecture Documentation

AIContextCraft architecture is documented in diagrams-as-code form (C4 + sequence diagrams):

- Architecture guide: [`docs/architecture/README.md`](docs/architecture/README.md)
- C4 source model: [`docs/architecture/structurizr/workspace.dsl`](docs/architecture/structurizr/workspace.dsl)

Regenerate all architecture artifacts (Structurizr export, Mermaid validation, SVG assets):

```bash
./scripts/architecture/generate-all.sh
```

## ⚙️ Configuration (YAML)

The real power of **AI Context Craft** lies in its configuration. Configuration files are optional and auto-detected in this order inside the target project: `.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config-concat-code.yaml`. If none is found, Zero-Config mode is used without creating files on disk.

When no `--output` flag is provided, `output_path` in your YAML config overrides the default fallback path (`build/aicc_context.<ext>` based on `--format`).

```yaml
# Default output file path.
output_path: "./build/project_context.txt"

# --- FILE SELECTION ---

# STEP 1: INCLUSION (Priority)
# Only files matching these glob patterns will be considered.
include_patterns:
  - '**/*' # Default: all files in all subdirectories

# STEP 2: EXCLUSION
# From the files included above, remove any that match these patterns.

# Filters applied to BOTH the file tree and content.
common_filters:
  - "__pycache__/"
  - "*.pyc"
  - ".git/"
  - ".venv/"
  - "node_modules/"
  - "build/"

# Excludes from file content ONLY (will still appear in the tree).
project_only_filters:
  - ""

# Excludes from the tree ONLY (content will still be included).
tree_only_filters:
  - "*.md"
  - "LICENSE"

# --- ADVANCED OPTIONS ---

# For --headers-only, functions/classes matching these names
# will have their full body included.
full_body_filters:
  - "main"
  - "run_app"
```

### Paths with special characters (Unicode, emoji, Windows separators)

When writing `include_patterns` and exclusion filters:

- Prefer `/` as separator, even on Windows.
- Unicode characters (accents, emoji) are supported directly.
- If you must write backslashes, avoid YAML double-quoted traps:
  - use single quotes: `'🚀 Projets\🏰 Proxmox Homelab\**'`
  - or escape backslashes in double quotes: `"🚀 Projets\\\\🏰 Proxmox Homelab\\\\**"`

Recommended example:

```yaml
include_patterns:
  - "🚀 Projets/🏰 Proxmox Homelab/**"
```

## 🗺️ Roadmap

High-level direction (details and ideas in [ROADMAP.md](ROADMAP.md)):

*   ✅ **Phase 0–1 (done):** Modular `craft/` architecture, hierarchical ignores, security exclusions, Zero-Config, Rich UI, clipboard limits, LLM formats (`--format text|xml|markdown`), and Git diff mode (`--git-diff`).
*   🚀 **Phase 2 (next):** Universal extraction via `tree-sitter`—multi-language comment stripping and `--headers-only` repo maps beyond Python.
*   🧠 **Phase 3 (planned):** Focus filtering (`--focus-git`, `--focus`) to combine full code on relevant files with repo-map summaries elsewhere.

## 🛠️ Development

From the repository root, using the project virtual environment:

```bash
# Full suite (~36 tests)
.aicc_venv/bin/python -m pytest tests

# Targeted run
.aicc_venv/bin/python -m pytest tests/test_context_builder.py
```

## 🤝 Contributing

Contributions are welcome! Whether it's a feature request, bug report, or a pull request, please feel free to engage. Check out the [ROADMAP.md](ROADMAP.md) for inspiration.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📜 License

This project is released into the public domain under the [CC0 1.0 Universal](LICENSE) license. Feel free to use, modify, and distribute it as you see fit.