---
name: llm-output-formats
overview: Introduire des formats de sortie `text`, `xml` et `markdown` via un module dédié, tout en préservant strictement le comportement historique par défaut et en couvrant les cas spéciaux CLI/tests.
todos:
  - id: cli-config-format
    content: "Ajouter `--format` et `output_format: text` avec résolution CLI > config."
    status: completed
  - id: formatter-module
    content: Créer `craft/formatter.py` avec renderers text/xml/markdown et API de rendu unique.
    status: completed
  - id: main-pipeline-refactor
    content: Refactoriser `main.py` pour collecter des données fichiers et déléguer le rendu au formatter.
    status: completed
  - id: special-modes-policy
    content: Stabiliser `--tree-only` multi-format et conserver `--git-diff` sur son flux Markdown dédié.
    status: completed
  - id: tests-formats
    content: Ajouter les tests xml/markdown/tree-only et un test d’échappement XML.
    status: in_progress
  - id: python-test-procedure
    content: Valider via `.aicc_venv` et reporter collected/pass-fail/warnings.
    status: pending
  - id: publish-plan-copy
    content: Publier une copie horodatée du plan dans `docs/plans/<branch-name>/` avec titre kebab-case.
    status: pending
isProject: false
---

# Phase 1 - Formats de sortie LLM (Text/XML/Markdown)

## Objectif
Ajouter un moteur de rendu multi-format pour la sortie de concaténation dans AIContextCraft, avec `text` comme défaut strictement rétrocompatible, puis `xml` et `markdown` comme formats optimisés LLM.

## Constat actuel (base de travail)
- La génération finale est centralisée dans [`main.py`](/opt/AIContextCraft/main.py) avec une concaténation texte en dur (arbre + extensions + sections `--- FICHIER:`).
- Le mode `--git-diff` suit un flux dédié et produit déjà un rapport Markdown autonome.
- Les tests CLI sont regroupés dans [`tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py).
- Aucune abstraction de formatage n’existe encore dans `craft/`.

## Stratégie d’implémentation

### 1) Étendre la configuration/CLI sans casser l’existant
- Dans [`main.py`](/opt/AIContextCraft/main.py), ajouter l’argument `--format` avec `choices=['text', 'xml', 'markdown']`.
- Ajouter `output_format: 'text'` dans `DEFAULT_CONFIG` et lire la valeur config/CLI avec priorité CLI.
- Garder la sortie identique à aujourd’hui quand `format == 'text'` (y compris séparateurs, titres, structure globale).

### 2) Créer un module de rendu dédié
- Créer [`craft/formatter.py`](/opt/AIContextCraft/craft/formatter.py) avec une API unique, par exemple:
  - `build_output(format_type, intro_header, project_tree, extension_summary, files_data, tree_only=False)`
- Standardiser `files_data` comme liste de tuples `(relative_path, content)` (ou structure équivalente).
- Implémenter trois renderers:
  - `text`: reproduction stricte du rendu actuel.
  - `xml`: structure `<repository>`, `<directory_structure>`, `<files>`, `<file path="...">`.
  - `markdown`: sections `# Project Context`, `## Directory Structure`, `## Files`, blocs de code avec language hint par extension (fallback `text`).
- Échapper correctement le contenu XML (`&`, `<`, `>`) pour garantir un document valide.

### 3) Refactoriser le pipeline de génération dans `main.py`
- Remplacer `all_files_content` (chaînes déjà formatées) par une collecte de données brutes par fichier.
- Après lecture/transformations (`--strip-comments`, `--headers-only`), déléguer le rendu final à `craft.formatter`.
- Conserver l’en-tête global existant (phrase descriptive, date, statistiques), puis injecter le corps formaté.

### 4) Définir clairement les modes spéciaux
- `--tree-only`:
  - `text`: garder le rendu actuel arbre + extensions.
  - `xml`: produire `<repository><directory_structure>...</directory_structure></repository>` sans `<files>`.
  - `markdown`: produire seulement la section contexte/arborescence, sans section fichiers.
- `--git-diff`:
  - Conserver le flux actuel inchangé (rapport Markdown dédié) pour éviter une régression fonctionnelle.
  - Ignorer `--format` dans ce mode avec un log explicite, afin d’avoir un comportement déterministe.

### 5) Compléter la couverture de tests
- Étendre [`tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py) avec:
  - un test `--format xml` (présence de `<repository>`, `<directory_structure>`, `<files>`, `<file path="...">`).
  - un test `--format markdown` (présence de `# Project Context`, `## Directory Structure`, `## Files`).
  - un test `--tree-only --format xml|markdown` (absence de section fichiers).
  - un test de rétrocompatibilité `text` (comparaison robuste existante conservée).
- Ajouter si utile un cas d’échappement XML sur contenu incluant `<tag>&value`.

### 6) Validation et exécution des tests Python (procédure projet)
- Utiliser l’environnement local `.aicc_venv`:
  - créer le venv si absent, installer les dépendances via `requirements.txt`.
  - exécuter `pytest` avec le Python du venv (suite ciblée puis complète si nécessaire).
- Reporter dans le compte-rendu:
  - nombre de tests collectés,
  - statut pass/fail,
  - warnings éventuels.

### 7) Publication du plan (demandée)
- Déterminer le nom de branche courant.
- Créer `docs/plans/<branch-name>/` si nécessaire.
- Copier le plan validé dans ce dossier et le renommer au format:
  - `YYYY_MM_DD_HH:MM_<plan-title>.plan.md`
- Normaliser `<plan-title>` en kebab-case ASCII.

## Critères d’acceptation
- `--format` accepte `text|xml|markdown`.
- Sans `--format`, la sortie est strictement identique au comportement historique.
- `--tree-only` et `--git-diff` ont un comportement explicite, stable et testé.
- Les nouveaux tests de format passent, sans casser les tests existants.
- Le plan est publié dans `docs/plans/<branch-name>/` avec le nom horodaté attendu.

---
## Compte rendu d'implementation

### Changements réalisés
- Ajout de `--format {text,xml,markdown}` dans `main.py`.
- Ajout de `output_format: "text"` dans `config.yaml` et dans `DEFAULT_CONFIG` pour conserver la rétrocompatibilité.
- Création de `craft/formatter.py` avec une API unique `build_output(...)` et trois renderers:
  - `text`: rendu historique inchangé
  - `xml`: structure `<repository>`, `<directory_structure>`, `<files>`, `<file path=\"...\">`
  - `markdown`: sections `# Project Context`, `## Directory Structure`, `## Files`, avec détection de langage pour les blocs de code
- Refactorisation du pipeline de sortie de `main.py`:
  - collecte des fichiers en données brutes `(relative_path, content)`
  - délégation du rendu final au formatter
  - gestion homogène de `--tree-only` pour tous les formats
- Mode `--git-diff` conservé en flux Markdown dédié, avec log explicite si `--format` est fourni.

### Fichiers modifiés
- `main.py`
- `config.yaml`
- `craft/formatter.py` (nouveau)
- `tests/test_aicc.py`
- `docs/plans/feature/llm-formats/2026_05_17_17:29_llm-output-formats.plan.md` (ajout du compte rendu)

### Validation / tests
- Environnement utilisé: `.aicc_venv` (Python local du projet).
- Commande exécutée: `.aicc_venv/bin/python -m pytest tests`
- Résultat:
  - tests collectés: 21
  - statut: 21 passed
  - warnings: 54
- Détail warnings:
  - warnings de dépréciation `pathspec` sur `gitwildmatch` (pas de régression introduite par cette phase).