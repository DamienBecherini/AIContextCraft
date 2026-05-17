# AI Context Craft Craft Craft

<div align="center">
  <h1>AI Context Craft</h1>
  <p><strong>The essential CLI tool for intelligently packaging your codebase for Large Language Models.</strong></p>
  
  <p>
    <a href="https://creativecommons.org/publicdomain/zero/1.0/"><img src="https://img.shields.io/badge/license-CC0_1.0-blue.svg" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python Version"></a>
    <a href="#"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status"></a>
  </p>
</div>

---

**AI Context Craft** solves a common problem for developers using LLMs like GPT-4, Claude, or Llama: how do you feed an entire codebase to an AI that has a limited context window? This tool lets you intelligently select, filter, and concatenate your project files into a single, clean, context-optimized text file, ready to be pasted into any AI chat.

Stop manually copying and pasting files and start crafting the perfect context in seconds.

## ✨ Key Features

*   **Powerful YAML Configuration**: Define exactly what to include and exclude using a simple `config.yaml` file.
*   **Intelligent Two-Step Filtering**: A robust `include-then-exclude` logic gives you granular control over your context. First, specify what you want with `include_patterns`, then clean it up with various exclusion filters.
*   **Advanced Python Code Processing**:
    *   `--strip-comments`: Reliably remove all comments and docstrings using Abstract Syntax Tree (AST) parsing, not just simple regex.
    *   `--headers-only`: Create a high-level summary of your code by extracting only class and function signatures and their docstrings.
*   **Customizable Project Tree Generation**: Automatically generate a filtered file tree with sizes, per-extension totals, and visual markers (`●` concatenated, `○` tree-only via `project_only_filters`) to give the LLM a clear overview of the project structure.
*   **Two-Stage Filtering (Shield + Scalpel)**:
    *   **Stage 1 (Shield, on by default):** Hierarchical `.gitignore` files are applied during directory traversal for fast pruning, plus hardcoded security patterns (`.env`, `.env.*`, `*.pem`, `*.key`, `.git/`) that always apply.
    *   **Stage 2 (Scalpel):** YAML `include_patterns` and exclusion filters refine what remains.
    *   Use `--no-ignore` to disable `.gitignore` matching while keeping security exclusions.
*   **Built-in Utilities**:
    *   Automatic token and size calculation with `tiktoken`.
    *   Verbose logging for easy debugging.
*   **LLM-Optimized Output Formats**:
    *   `--format text|xml|markdown` lets you target different AI workflows.
    *   `xml` is recommended for Anthropic (Claude) and OpenAI usage because it provides strongly structured context sections such as `<repository>`, `<directory_structure>`, and `<files>`.
*   **Smart Clipboard Integration**:
    *   `-cb` / `--clipboard` copies the final output directly after generation.
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
git clone https://github.com/your-username/ai-context-craft.git
cd ai-context-craft
 
# (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install pyyaml tiktoken
```

### 2. Usage

Run the script from your terminal. By default, it looks for a `config.yaml` in the same directory and scans the current project.

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
| `--no-ignore`        | Disable hierarchical `.gitignore` filtering (security patterns still apply). |
| `--git-diff REF_A REF_B` | Generate a Markdown report with the global Git diff between two revisions. |
| `--format {text,xml,markdown}` | Choose output format (`text` default, `xml`, or `markdown`). |
| `-cb`, `--clipboard` | Copy the generated final content directly to the clipboard (OSC 52 supported). |
| `--no-timestamp`     | Do not append a timestamp to the output filename.                         |
| `--dry-run`          | Run the script without writing any files to see what would be included.   |
| `-v`, `--verbose`    | Print detailed processing information to the console.                     |

#### CLI Help Snapshot (`python main.py --help`)

```text
usage: main.py [-h] [-c CONFIG] [-p PROJECT] [-o OUTPUT] [--no-timestamp]
               [--strip-comments] [--headers-only] [--tree-only] [--dry-run]
               [--encoding ENCODING] [--no-ignore] [--git-diff REF_A REF_B]
               [--format {text,xml,markdown}] [-cb] [-v]

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
  --no-ignore           Disable hierarchical .gitignore filtering (security rules still apply).
  --git-diff REF_A REF_B
                        Special mode: generate global Git diff Markdown report between two revisions.
  --format {text,xml,markdown}
                        Output format: text (default), xml or markdown.
  -cb, --clipboard      Copy final generated content to clipboard.
  -v, --verbose         Print detailed processing information.
```

### Example Workflow

Generate a context for a Python project with comments stripped (`.gitignore` and security filters apply by default):

```bash
python main.py --project ./my-python-app --strip-comments -v
```

On large repositories (Node, Python, etc.), ignored folders such as `node_modules/` or `.venv/` are pruned during traversal before YAML filters run, which speeds up scanning significantly.

This will create a file in the `build/` directory containing the project tree and the cleaned content of all relevant files.

Generate a dedicated Markdown diff report (without running the standard concatenation flow):

```bash
python main.py --project ./my-python-app --git-diff HEAD~1 HEAD --output ./build/git_diff_report.txt --no-timestamp
```

Generate XML output optimized for LLM ingestion and copy it to clipboard in one command:

```bash
python main.py --project ./my-python-app --format xml --clipboard
```

## ⚙️ Configuration (`config.yaml`)

The real power of **AI Context Craft** lies in its configuration. A `config.yaml` is automatically created on first run.

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

This project has a bright future! Our goal is to make it the most powerful and developer-friendly context-crafting tool available.

*   ✅ **Phase 0: Foundation** - Refactor complete with modular and testable architecture.
*   ✅ **Phase 1: Pro Experience** - Rich progress UI, clipboard support (`--clipboard`), and LLM output formats (`--format text|xml|markdown`) are in place.
*   🚀 **Phase 2: The Universal Tool** - Next priority: `tree-sitter` migration, multi-language comment handling, and token-based splitting (`--max-tokens`).
*   🔄 **Phase 3: The Leap to Intelligence** - Git diff mode is available (`--git-diff REF_A REF_B`) and can be extended further.

## 🤝 Contributing

Contributions are welcome! Whether it's a feature request, bug report, or a pull request, please feel free to engage. Check out the [ROADMAP.md](ROADMAP.md) for inspiration.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📜 License

This project is released into the public domain under the [CC0 1.0 Universal](LICENSE) license. Feel free to use, modify, and distribute it as you see fit.