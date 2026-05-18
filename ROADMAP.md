# 🗺️ AI Context Craft Roadmap

## 1. Vision and goal
**Vision:** A personal, robust, pragmatic CLI tool to prepare codebases before sending them to an LLM.
**Goal:** Deliver highly relevant AI context by combining aggressive filtering and smart extraction (scope + focus), without gadget features.

---

## 2. Current state (stable — Phase 1)
* **Hierarchical filtering:** Respects `.gitignore`, `.dockerignore`, etc.
* **Security:** Forced exclusion of secrets (`.env`, `*.pem`) and encoding fallback.
* **Plug & play:** Zero-config, automatic clipboard (`-cb`), XML/Markdown formats.
* **Git diff:** Markdown report of differences between two branches.

---

## 3. 🚀 Next step: Phase 2 — Universal extraction (Tree-sitter)
Today, optimization (`--strip-comments` and `--headers-only`) only handles Python (native AST). The goal is to extend it to everyday languages (JS, TS, Rust, Go, C++, etc.) robustly.

1. **`tree-sitter` integration:**
   * Replace the Python AST with the universal `tree-sitter` parser.
   * Enable reliable comment stripping for major languages.
2. **Universal “Repo Map”:**
   * Make `--headers-only` multi-language to produce a compact project map (function/class signatures only).

---

## 4. 🧠 Phase 3 — “Focus” filtering (Cursor-style model)
Combine “Scope” (YAML config) and “Zoom” (Focus) to send the global project map to the AI, with full code only on relevant files.

1. **Git focus (`--focus-git`):**
   * Within the allowed scope, include full code only for locally modified (or staged) files.
   * Automatically downgrade the rest of the project to `--headers-only` (Repo Map).
2. **Semantic / grep focus (`--focus "keyword"`):**
   * Extract full code from files matching a keyword; keep the rest as Repo Map.

---

## 5. 💡 Lab (ideas and explorations)
*Ideas and concepts to explore for the future.*

* **Investigation agent (AI focus):** Connect to a low-cost (or local Ollama) API so it reads the project map and finds relevant files for a ticket, pseudo-intelligent filtering.
* **Dependency hunter (import crawler):** When a file is focused, follow imports to include dependent code automatically.
* **Multimodal support (vision):** Detect images (PNG, SVG, JPG) and encode as Base64 in XML for multimodal models (Claude 3.5, GPT-4o).
* **Prompt caching optimization:** Structure XML with static context on top and dynamic context (changed files) at the bottom for Anthropic/OpenAI cache hits.
* **Automatic test discovery:** On focus of a source file, include the associated unit test file (`test_*.py`, `*.spec.js`).
* **Secret scanning (redaction):** Scan file content and mask forgotten AWS/Stripe API keys (e.g. `[REDACTED]`) before copy.
* **Prompt templates:** Wrap generated context in a predefined instruction (e.g. `--template code-review`).
* **Smart minification:** Summarize lockfiles (`package-lock.json`) as a dependency list to save tokens.
* **Remote ingestion:** Replace a local path with a GitHub URL to analyze a repo on the fly.

---

## 6. ✅ History (archive)

### Phase 1: User experience ✅ (complete)
* Console progress bar via `rich`.
* Smart clipboard handling (size limit, `-cb`, SSH fallback).
* LLM output formats (XML default, Markdown).
* “Plug & play” logic (auto-detected config, `build/` output).

### Phase 0: Refactoring and foundation ✅ (complete)
* Split monolithic script into dedicated modules (`craft/`).
* Automated tests (30+) to prevent regressions.
* Architecture-as-code documentation (C4 model, Mermaid sequences).
