# 🗺️ AI Context Craft : Roadmap

## 1. Vision et Objectif
**Vision :** Un outil CLI personnel, robuste et pragmatique pour préparer des bases de code avant de les envoyer à un LLM.
**Objectif :** Obtenir un contexte IA ultra-pertinent en combinant un filtrage drastique et une extraction intelligente (Périmètre + Zoom), sans s'encombrer de fonctionnalités gadgets.

---

## 2. État Actuel (Version Stable - Phase 1)
* **Filtrage hiérarchique :** Respect de `.gitignore`, `.dockerignore`, etc.
* **Sécurité :** Exclusion forcée des secrets (`.env`, `*.pem`) et fallback d'encodage.
* **Plug & Play :** Zero-config, presse-papiers automatique (-cb), formats XML/Markdown.
* **Git-Diff :** Rapport Markdown des différences entre deux branches.

---

## 3. 🚀 Prochaine Étape : Phase 2 - L'Extraction Universelle (Tree-sitter)
Actuellement, l'optimisation (`--strip-comments` et `--headers-only`) ne gère que Python (via l'AST natif). Le but est de l'étendre aux langages du quotidien (JS, TS, Rust, Go, C++, etc.) de manière robuste.

1. **Intégration de `tree-sitter` :**
   * Remplacer l'AST Python par le parseur universel `tree-sitter`.
   * Permettre la suppression fiable des commentaires pour les langages majeurs.
2. **Le "Repo Map" Universel :**
   * Rendre l'option `--headers-only` compatible multi-langage pour générer une "carte" compacte du projet (uniquement les signatures de fonctions/classes).

---

## 4. 🧠 Phase 3 - Le Filtrage "Focus" (Le modèle Cursor)
Combiner le "Périmètre" (YAML Config) et le "Zoom" (Focus) pour envoyer à l'IA la carte globale du projet, mais avec le code complet uniquement sur les fichiers pertinents.

1. **Le Focus Git (`--focus-git`) :**
   * À l'intérieur du périmètre autorisé, inclure le code complet *uniquement* pour les fichiers modifiés localement (ou staged).
   * Rétrograder automatiquement le reste du projet en mode `--headers-only` (Repo Map).
2. **Le Focus Sémantique / Grep (`--focus "keyword"`) :**
   * Extraire le code complet des fichiers qui matchent un mot-clé précis, et garder le reste en Repo Map.

---

## 5. 💡 Le Labo (Boîte à Idées & Explorations)
*Une liste d'idées et de concepts à explorer pour l'avenir.*

* **L'Agent d'Investigation (Focus IA) :** Connecter l'outil à une API IA low-cost (ou locale via Ollama) pour qu'elle lise la "carte du projet" (Repo Map) et trouve d'elle-même les fichiers pertinents pour résoudre un ticket, automatisant ainsi le filtrage de manière "pseudo-intelligente".
* **Le Chasseur de Dépendances (Imports Crawler) :** Si un fichier est ciblé par le Focus, analyser ses `import` pour inclure automatiquement le code des fichiers dont il dépend pour fonctionner.
* **Support Multimodal (Vision) :** Détecter les images (PNG, SVG, JPG) et les encoder en Base64 dans le XML pour que les modèles multimodaux (Claude 3.5, GPT-4o) puissent "voir" les maquettes UI ou les diagrammes d'architecture.
* **Optimisation "Prompt Caching" :** Structurer le document XML pour placer le contexte statique en haut et le contexte dynamique (fichiers modifiés) en bas, afin de maximiser les hits de cache sur les API Anthropic/OpenAI.
* **Découverte Automatique des Tests :** Lors d'un Focus sur un fichier source, détecter et inclure automatiquement le fichier de tests unitaires associé (`test_*.py`, `*.spec.js`).
* **Secret Scanning (Redaction) :** Scanner activement le contenu des fichiers pour détecter et masquer (ex: `[REDACTED]`) les clés API AWS/Stripe oubliées dans le code avant la copie.
* **Templates de Prompts :** Permettre d'englober le contexte généré directement à l'intérieur d'une consigne pré-définie (ex: `--template code-review`).
* **Smart Minification :** Résumer intelligemment les lockfiles (`package-lock.json`) en une simple liste de dépendances pour économiser des milliers de tokens.
* **Ingestion Distante :** Remplacer le chemin local par une URL GitHub pour analyser un dépôt à la volée.

---

## 6. ✅ Historique (Archives)

### Phase 1 : Expérience Utilisateur (Terminée)
* Barre de progression console via `rich`.
* Gestion intelligente du presse-papiers (limite de taille, `-cb`, fallback SSH).
* Formats de sortie LLM (XML par défaut, Markdown).
* Logique "Plug & Play" (configuration auto-détectée, sortie `build/`).

### Phase 0 : Refactoring et Fondation (Terminée)
* Découpage du script monolithique en modules dédiés (`craft/`).
* Mise en place de tests automatisés (+30) pour éviter les régressions.
* Documentation d'architecture as-code (Modèle C4, séquences Mermaid).