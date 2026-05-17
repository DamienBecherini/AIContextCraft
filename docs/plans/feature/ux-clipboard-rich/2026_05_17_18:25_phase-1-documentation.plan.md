---
name: phase-1-documentation
overview: Mettre à jour ROADMAP.md et README.md pour refléter l'achèvement de la Phase 0 (Refactoring) et de la Phase 1 (UX, Formats LLM, Clipboard, Git Diff).
todos:
  - id: update-roadmap
    content: Modifier `ROADMAP.md` pour marquer les Phases 0 et 1 (ainsi que l'intégration Git diff) comme terminées, et redéfinir les prochaines étapes.
    status: pending
  - id: update-readme-features
    content: Ajouter les nouvelles fonctionnalités (Formats XML/Markdown, Clipboard via SSH, Git Diff) dans le `README.md`.
    status: pending
  - id: update-readme-cli
    content: Mettre à jour la section d'aide CLI du `README.md` avec les nouvelles options (`--format`, `-cb`, `--git-diff`).
    status: pending
  - id: save-report
    content: Demander si le compte-rendu d'implémentation doit être sauvegardé.
    status: pending
isProject: true
---

# PRD : Mise à jour de la Documentation et de la Roadmap

## 🎯 Objectif
Le projet a évolué massivement et rapidement. Le code est maintenant en avance sur la documentation. Il faut synchroniser `ROADMAP.md` et `README.md` avec l'état actuel du code (fin de Phase 1).

## 📝 1. Mise à jour de `ROADMAP.md`

### État actuel à refléter :
- **Phase 0 (Fondation / Refactoring) : ✅ TERMINÉE.** (L'architecture `craft/` est en place).
- **Phase 1 (Expérience "Pro") : ✅ TERMINÉE.** 
  - A1. Barre de progression (Implémenté via `rich`).
  - A2. Copie vers le presse-papiers (Implémenté avec support OSC 52 pour SSH).
  - *Nouvelle sous-tâche complétée :* Formatage LLM-Optimized (XML, Markdown).
- **Phase 3 (Intégration Git) : 🔄 EN COURS / PARTIELLEMENT TERMINÉE.**
  - C1. Intégration Git `diff` (Implémenté avec succès).

### Prochaines étapes à mettre en valeur (La nouvelle "Prochaine Phase") :
La roadmap doit maintenant pointer vers la **Phase 2 : L'Outil Universel**, dont l'objectif principal sera de remplacer l'analyseur `ast` Python par **`tree-sitter`** pour permettre le `--strip-comments` et l'analyse de tous les langages (JS, TS, Rust, C++, etc.), ainsi que le fractionnement par tokens (`--max-tokens`).

## 📖 2. Mise à jour de `README.md`

Assure-toi que les éléments suivants sont clairement expliqués aux utilisateurs :

### Nouvelles fonctionnalités phares :
1. **Formats LLM-Optimisés (`--format {text,xml,markdown}`)** : Expliquer que `xml` est le format recommandé pour Anthropic (Claude) et OpenAI car il structure parfaitement le contexte avec des balises `<repository>`, `<directory_structure>` et `<files>`.
2. **Copie intelligente dans le presse-papiers (`-cb` ou `--clipboard`)** : Expliquer que cette option copie directement le résultat. Mentionner la magie du support **OSC 52** : cela fonctionne même si l'outil est lancé depuis un serveur Linux distant via une connexion SSH !
3. **Mode Git Diff (`--git-diff <ref_a> <ref_b>`)** : Expliquer que ce mode génère un rapport Markdown parfait des différences entre deux branches ou commits, idéal pour rédiger des descriptions de Pull Request avec l'IA.
4. **Interface Console Moderne** : Mentionner l'ajout de barres de progression et de logs colorés pour les grands projets.

### Mise à jour de l'aide CLI :
Mettre à jour le bloc de code montrant le résultat de `python main.py --help` pour inclure les nouveaux flags.

---
## Compte rendu d'implementation

### Changements realises
- `ROADMAP.md` mis a jour pour refleter l'etat reel:
  - Phase 0 marquee terminee
  - Phase 1 marquee terminee (progression `rich`, clipboard `-cb/--clipboard` avec OSC 52, formats `--format`)
  - Phase 3 marquee en cours/partielle avec `--git-diff REF_A REF_B`
  - Phase 2 repositionnee comme prochaine priorite (`tree-sitter`, multi-langage, `--max-tokens`)
- `README.md` complete avec les nouvelles fonctionnalites:
  - formats LLM (`--format text|xml|markdown`) et recommandation XML
  - copie presse-papiers intelligente (`-cb/--clipboard`) avec support SSH via OSC 52
  - mode Git diff (`--git-diff REF_A REF_B`) pour usages PR/IA
  - mention de l'UX console moderne (progress bars, logs colores)
- section d'aide CLI du `README.md` mise a jour pour inclure:
  - `--format {text,xml,markdown}`
  - `-cb, --clipboard`
  - `--git-diff REF_A REF_B`

### Fichiers modifies
- `ROADMAP.md`
- `README.md`
- `docs/plans/feature/ux-clipboard-rich/2026_05_17_18:25_phase-1-documentation.plan.md`

### Validation
- Verification de coherence entre documentation et options CLI detectees dans `main.py`
- Verification linter sur les fichiers modifies: aucune erreur
