---
name: phase-1-documentation
overview: Update ROADMAP.md and README.md to reflect completion of Phase 0 (Refactoring) and Phase 1 (UX, LLM formats, Clipboard, Git Diff).
todos:
  - id: update-roadmap
    content: Update ROADMAP.md to mark Phases 0 and 1 (and Git diff integration) complete and redefine next steps.
    status: pending
  - id: update-readme-features
    content: Add new features (XML/Markdown formats, SSH clipboard, Git Diff) to README.md.
    status: pending
  - id: update-readme-cli
    content: Update README.md CLI help section with new options (--format, -cb, --git-diff).
    status: pending
  - id: save-report
    content: Ask whether implementation report should be saved.
    status: pending
isProject: true
---

# PRD: Documentation and roadmap update

## 🎯 Objective
The project evolved quickly; code is ahead of documentation. Synchronize `ROADMAP.md` and `README.md` with the current state (end of Phase 1).

## 📝 1. Update `ROADMAP.md`

### State to reflect:
- **Phase 0 (Foundation / Refactoring): ✅ COMPLETE.** (`craft/` architecture in place).
- **Phase 1 (Pro experience): ✅ COMPLETE.**
  - A1. Progress bar (implemented via `rich`).
  - A2. Clipboard copy (implemented with OSC 52 for SSH).
  - *Additional completed item:* LLM-optimized formatting (XML, Markdown).
- **Phase 3 (Git integration): 🔄 IN PROGRESS / PARTIALLY COMPLETE.**
  - C1. Git `diff` integration (successfully implemented).

### Next steps to highlight (new “Next Phase”):
The roadmap should now point to **Phase 2: Universal Tool**, whose main goal is replacing the Python `ast` analyzer with **`tree-sitter`** for `--strip-comments` and analysis across all languages (JS, TS, Rust, C++, etc.), plus token splitting (`--max-tokens`).

## 📖 2. Update `README.md`

Ensure the following are clearly explained to users:

### Key new features:
1. **LLM-optimized formats (`--format {text,xml,markdown}`)**: Explain that `xml` is recommended for Anthropic (Claude) and OpenAI because it structures context with `<repository>`, `<directory_structure>`, and `<files>` tags.
2. **Smart clipboard copy (`-cb` or `--clipboard`)**: Explain direct result copy. Mention **OSC 52** support: works even when run on a remote Linux server over SSH.
3. **Git Diff mode (`--git-diff <ref_a> <ref_b>`)**: Explain Markdown report of differences between branches or commits, ideal for AI-assisted PR descriptions.
4. **Modern console UI**: Mention progress bars and colored logs for large projects.

### CLI help update:
Update the code block showing `python main.py --help` output to include the new flags.

---
## Implementation report

### Changes made
- `ROADMAP.md` updated to reflect actual state:
  - Phase 0 marked complete
  - Phase 1 marked complete (`rich` progress, `-cb/--clipboard` with OSC 52, `--format`)
  - Phase 3 marked in progress/partial with `--git-diff REF_A REF_B`
  - Phase 2 repositioned as next priority (`tree-sitter`, multi-language, `--max-tokens`)
- `README.md` extended with new features:
  - LLM formats (`--format text|xml|markdown`) and XML recommendation
  - smart clipboard (`-cb/--clipboard`) with SSH via OSC 52
  - Git diff mode (`--git-diff REF_A REF_B`) for PR/AI use
  - modern console UX mention (progress bars, colored logs)
- README CLI help section updated to include:
  - `--format {text,xml,markdown}`
  - `-cb, --clipboard`
  - `--git-diff REF_A REF_B`

### Modified files
- `ROADMAP.md`
- `README.md`
- `docs/plans/2026_05_17_18-25_feature__ux-clipboard-rich_phase-1-documentation.plan.md`

### Validation
- Coherence check between documentation and CLI options detected in `main.py`
- Linter check on modified files: no errors
