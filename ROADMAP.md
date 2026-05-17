# **AI Context Craft : Document d'Évolution et Roadmap**

## 1. Vision et Mission

**Vision :** Un outil à la fois simple et puissant pour les développeurs qui préparent des bases de code pour une analyse par des Grands Modèles de Langage (LLM).

**Mission :** Offrir un contrôle granulaire, une performance élevée et des fonctionnalités intelligentes pour créer le contexte le plus pertinent et concis possible, optimisant ainsi l'efficacité des interactions avec l'IA.

## 2. État Actuel (v1.0 - Baseline)

*   **Gestion de la Configuration :** Configuration complète via un fichier `config.yaml`.
*   **Filtrage à Deux Étapes :** Logique puissante d'inclusion prioritaire (`include_patterns`) suivie par une exclusion (`common_filters`, etc.).
*   **Traitement de Code Python Avancé :**
    *   Suppression des commentaires et docstrings basée sur l'AST, garantissant une grande fiabilité (`--strip-comments`).
    *   Extraction des en-têtes et docstrings pour un contexte de haut niveau (`--headers-only`).
*   **Génération d'Arborescence :** Visualisation claire de la structure du projet, respectant les filtres.
*   **Utilitaires :** Logging, gestion des timestamps, calcul de statistiques (taille, tokens), et support du `.gitignore`.

## 3. Architecture Cible (v2.0 - Le Refactoring)

L'objectif principal est de passer d'un script monolithique à une architecture modulaire pour garantir la maintenabilité, la testabilité et l'évolutivité du projet.

#### Structure de Projet Proposée :

```
ai-context-craft/
├── main.py                  # Point d'entrée, orchestrateur principal
├── config.yaml              # Fichier de configuration
|
└── craft/                   # Package contenant la logique métier
    ├── __init__.py
    ├── config_manager.py    # Chargement, validation et fusion de la configuration.
    ├── file_processor.py    # Fonctions de traitement de contenu (strip_comments, get_headers).
    ├── filter_manager.py    # Logique d'assemblage des patterns d'inclusion/exclusion.
    ├── tree_generator.py    # Logique de génération de l'arborescence.
    └── utils.py             # Fonctions utilitaires transverses (logging, stats, etc.).
```

#### Bénéfices :

*   **Principe de Responsabilité Unique :** Chaque module a un rôle clair.
*   **Facilité de Test :** Permet d'écrire des tests unitaires pour chaque composant isolé.
*   **Lisibilité :** `main.py` devient un flux de travail de haut niveau, facile à comprendre.

---

## 4. Backlog des Fonctionnalités

### Catégorie A : Expérience Utilisateur & Améliorations de Base

1.  **A1. Barre de Progression : ✅ TERMINÉ**
    *   **Quoi :** Afficher une barre de progression (`rich`) lors de la concaténation des fichiers.
    *   **Pourquoi :** Fournir un retour visuel sur les projets volumineux et améliorer l'expérience utilisateur.

2.  **A2. Copie vers le Presse-papiers : ✅ TERMINÉ**
    *   **Quoi :** Ajouter une option `--clipboard` (`-cb`) pour copier la sortie directement dans le presse-papiers.
    *   **Pourquoi :** Fluidifier radicalement le workflow de l'utilisateur (Générer -> Coller), y compris via SSH (OSC 52).

3.  **A3. Gestion Robuste des Encodages :**
    *   **Quoi :** Remplacer `errors='ignore'` par une détection d'encodage (ex: `chardet`) ou, à défaut, logger un avertissement clair en cas d'échec de décodage.
    *   **Pourquoi :** Augmenter la fiabilité sur des projets hétérogènes.

4.  **A4. Formats de sortie LLM-Optimized : ✅ TERMINÉ**
    *   **Quoi :** Ajouter `--format {text,xml,markdown}` avec un rendu XML structuré pour les workflows IA.
    *   **Pourquoi :** Produire un contexte mieux structuré et directement exploitable par les LLMs.

### Catégorie B : Extension des Capacités

1.  **B1. Support Multi-langage pour le `strip-comments` :**
    *   **Quoi :** Étendre la fonction `strip_comments_from_code` pour gérer les commentaires `//`, `/* ... */` (JS, TS, Java, C++, CSS) et `<!-- ... -->` (HTML/XML).
    *   **Pourquoi :** Rendre l'outil universel et indispensable pour tout type de projet.

2.  **B2. Profils de Configuration :**
    *   **Quoi :** Permettre de définir des profils nommés dans `config.yaml` (ex: `frontend`, `backend`) que l'on peut activer via une option CLI (`--profile frontend`). Chaque profil aurait ses propres `include_patterns`.
    *   **Pourquoi :** Simplifier l'utilisation sur des monorepos ou des projets full-stack.

3.  **B3. Fractionnement Automatique de la Sortie :**
    *   **Quoi :** Ajouter une option `--max-tokens <N>` qui divise la sortie en plusieurs fichiers numérotés si le contexte dépasse N tokens.
    *   **Pourquoi :** Gérer les projets trop grands pour la fenêtre de contexte d'un LLM.

### Catégorie C : Contexte "Intelligent" & Intégration Git

1.  **C1. Intégration Git `diff` : 🔄 PARTIELLEMENT TERMINÉ**
    *   **Quoi :** Option `--git-diff <ref_a> <ref_b>` pour générer un rapport Markdown du diff Git global entre deux révisions.
    *   **Pourquoi :** **Fonctionnalité majeure.** Idéale pour les revues de code, la génération de descriptions de Pull Request ou le débuggage de nouvelles fonctionnalités.

2.  **C2. Priorisation Intelligente des Tokens :**
    *   **Quoi :** En conjonction avec `--max-tokens`, développer une logique qui, pour rester sous la limite, passe automatiquement certains fichiers en mode `--headers-only` en se basant sur des heuristiques (ex: fichiers les moins récemment modifiés, fichiers dans `tests/`).
    *   **Pourquoi :** Produire le meilleur contexte possible sous une contrainte de taille.

---

## 5. Roadmap Évolutive

### **Phase 0 : Fondation - Le Grand Refactoring (Prérequis) — ✅ TERMINÉE**

*   **Objectif :** Établir une base de code saine pour l'avenir.
*   **Tâches :**
    1.  Créer la nouvelle structure de dossiers (`craft/`).
    2.  Migrer la logique existante dans les modules dédiés (`config_manager.py`, `file_processor.py`, etc.).
    3.  Adapter `main.py` pour qu'il agisse en tant qu'orchestrateur.
    4.  S'assurer que toutes les fonctionnalités existantes fonctionnent parfaitement après le refactoring.

### **Phase 1 : L'Expérience "Pro" (Améliorations UX) — ✅ TERMINÉE**

*   **Objectif :** Rendre l'outil plus agréable et plus rapide à utiliser au quotidien.
*   **Tâches réalisées :**
    1.  Implémenter la barre de progression (**A1**, via `rich`).
    2.  Implémenter la copie vers le presse-papiers (**A2**, avec support OSC 52 en SSH).
    3.  Ajouter les formats LLM-Optimized (**A4**, `--format text|xml|markdown`).

### **Phase 2 : L'Outil Universel (Extension des capacités) — 🚀 PROCHAINE PRIORITÉ**

*   **Objectif :** Faire de l'outil un compagnon indispensable pour tous types de projets.
*   **Tâches :**
    1.  Remplacer l'analyseur Python AST par **`tree-sitter`** pour débloquer une base multi-langage robuste.
    2.  Ajouter le support multi-langage pour la suppression des commentaires (**B1**: JS/TS/Rust/C++/etc.).
    3.  Introduire le fractionnement automatique de la sortie par tokens (**B3**, `--max-tokens`).
    4.  Mettre en place le système de profils de configuration (**B2**) pour les projets complexes.

### **Phase 3 : Le Saut vers l'Intelligence (Intégration Git) — 🔄 EN COURS (PARTIEL)**

*   **Objectif :** Transformer l'outil d'un simple "concaténateur" à un véritable "assistant de contexte".
*   **Tâches :**
    1.  Consolider et enrichir l'intégration `git diff` (**C1**) déjà disponible.
    2.  (Optionnel) Commencer à explorer la priorisation intelligente des tokens (**C2**).