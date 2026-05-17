---
name: ignore-and-output-strategy
overview: Aligner le comportement CLI des ignore files avec l’aide/doc, ajouter un skip sélectif par type d’ignore file, et introduire une stratégie de sortie bot-friendly sans casser l’usage humain actuel.
todos:
  - id: create-dedicated-branch
    content: Créer et utiliser la branche dédiée `feature/ignore-output-strategy` avant toute modification de code.
    status: pending
  - id: align-ignore-contract
    content: Aligner le contrat --no-ignore avec les 4 ignore files supportés et exposer le contrôle sélectif dans IgnoreManager + CLI.
    status: pending
  - id: add-cli-flags
    content: Implémenter --skip-ignore-files et --ignore-files avec validation stricte et règles de priorité/conflit documentées.
    status: pending
  - id: add-output-modes
    content: Introduire output-format/output-destination/quiet avec séparation stdout-stderr adaptée aux bots.
    status: pending
  - id: update-help-readme
    content: Mettre à jour help argparse et README avec exemples et comportements exacts.
    status: pending
  - id: expand-tests
    content: Étendre les tests unitaires/CLI pour ignore global, skip sélectif, formats de sortie, et non-création de fichiers.
    status: pending
  - id: run-project-tests
    content: Exécuter pytest via .aicc_venv et reporter collecte/pass-fail/warnings.
    status: pending
  - id: publish-plan-copy
    content: Publier une copie du plan validé dans `docs/plans/feature-ignore-output-strategy/` avec nom horodaté kebab-case.
    status: pending
isProject: false
---

# Finalisation ignore files et stratégie de sortie CLI

## Objectif
Rendre le comportement des options d’ignore explicite et cohérent (`--no-ignore` global + skip sélectif), puis fiabiliser l’intégration bot/CI avec une sortie machine stable (JSON opt-in), tout en conservant l’UX humaine actuelle par défaut.

## Périmètre
- **Ignore files**: conserver `--no-ignore` comme désactivation globale de tous les ignore files supportés.
- **Skip sélectif**: ajouter un mécanisme pratique pour désactiver seulement certains types d’ignore files.
- **Sortie console**: conserver la sortie humaine par défaut, ajouter un mode structuré machine.
- **Documentation et aide**: aligner le texte utilisateur avec le comportement réel.
- **Tests**: couvrir parsing/validation CLI, comportement ignore, et formats de sortie.

## Changements proposés

### 0) Créer la branche dédiée
- Créer puis utiliser la branche: `feature/ignore-output-strategy`.
- Exécuter toute l’implémentation sur cette branche pour isoler le scope.

### 1) Clarifier et consolider la logique ignore
- Confirmer contractuellement que `--no-ignore` désactive la couche ignore files complète (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) tout en gardant les règles de sécurité.
- Étendre la configuration de `IgnoreManager` pour accepter une liste de types d’ignore files désactivés sélectivement.
- Fichiers cibles:
  - [`/opt/AIContextCraft/craft/ignore_manager.py`](/opt/AIContextCraft/craft/ignore_manager.py)
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)

### 2) Introduire une UX CLI de skip sélectif (les 2 syntaxes)
- Ajouter `--skip-ignore-files=gitignore,dockerignore,cursorignore,npmignore` (syntaxe recommandée).
- Ajouter `--ignore-files=...` (syntaxe complémentaire), avec règles de validation/conflit claires.
- Règles d’interaction:
  - `--no-ignore` a priorité globale.
  - si `--no-ignore` + flags sélectifs: warning explicite ou erreur (décision unique documentée et testée).
  - validation stricte des valeurs (typo => erreur d’usage claire).
- Fichier cible:
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)

### 3) Stratégie de sortie recommandée (humain par défaut, bot opt-in)
- Ajouter `--output-format human|json` (défaut: `human`).
- En `json`: résultat structuré stable sur `stdout`; logs/messages diagnostics sur `stderr`.
- Ajouter `--quiet` (inverse pratique de `verbose`) pour réduire les sorties non essentielles.
- Introduire `--output-destination file|stdout|both|none` pour contrôler la création de fichier de sortie.
- Conserver des codes de sortie simples et robustes (`0` succès, `2` usage/arguments, `1` erreur runtime).
- Fichiers cibles:
  - [`/opt/AIContextCraft/main.py`](/opt/AIContextCraft/main.py)
  - (si présent) module de rendu/export résultat utilisé par `main.py`.

### 4) Mettre à jour aide CLI et documentation
- Aligner les help strings sur le comportement réel multi-ignore files.
- Documenter la nouvelle matrice d’options ignore (`--no-ignore`, `--skip-ignore-files`, `--ignore-files`).
- Documenter les modes de sortie (`human/json`, destination, `--quiet`) et exemples CI/bot.
- Fichier cible principal:
  - [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md)

### 5) Couverture de tests
- Étendre tests unitaires et/ou CLI pour:
  - `--no-ignore` global sur tous les types d’ignore files.
  - skip sélectif par type.
  - conflits/validation des nouveaux flags.
  - format de sortie `json` stable et sans bruit parasite sur `stdout`.
  - non-création de fichier quand `--output-destination=stdout|none`.
- Fichiers cibles:
  - [`/opt/AIContextCraft/tests/test_ignore_manager.py`](/opt/AIContextCraft/tests/test_ignore_manager.py)
  - [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py)

## Validation
- Exécuter les tests via l’environnement local du projet (`.aicc_venv`) selon la procédure projet (`pytest`).
- Vérifier manuellement quelques commandes de référence:
  - cas humain par défaut,
  - cas bot JSON (`stdout` propre),
  - cas ignore global et skip sélectif.

## Risques et garde-fous
- **Risque UX**: trop d’options proches sur les ignore files.
  - Garde-fou: une syntaxe recommandée (`--skip-ignore-files`) + messages d’erreur pédagogiques.
- **Risque compatibilité**: scripts existants dépendants des sorties console.
  - Garde-fou: `human` reste défaut; `json` strictement opt-in.
- **Risque ambiguïté `stdout`**: mélange logs/résultat.
  - Garde-fou: contrat fort `stdout=data`, `stderr=diagnostic` en mode `json`.

## Publication du plan (demandée)
- Créer `docs/plans/feature-ignore-output-strategy/` si nécessaire.
- Copier ce plan validé dans ce dossier.
- Renommer la copie au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` avec `<plan-title>` en kebab-case ASCII.

---
## Compte rendu d'implementation

### Changements réalisés
- Branche dédiée créée et utilisée: `feature/ignore-output-strategy` (dans `AIContextCraft`).
- Alignement du contrat `--no-ignore`: désactivation globale des ignore files hiérarchiques (`.gitignore`, `.dockerignore`, `.cursorignore`, `.npmignore`) avec maintien des règles de sécurité.
- Ajout du skip sélectif des ignore files:
  - `--skip-ignore-files=...` (désactive seulement les types listés)
  - `--ignore-files=...` (garde seulement les types listés, alias inverse)
  - validation stricte des types et incompatibilité des deux flags ensemble.
- Ajout d'un mode sortie bot-friendly:
  - `--output-format human|json`
  - `--output-destination file|stdout|both|none`
  - `--quiet` (logs console minimaux).
- En mode `json`, émission d'un rapport structuré sur `stdout` et contrôle propre des sorties.
- Mise à jour de l’aide/documentation pour refléter les comportements réels et nouveaux flags.
- Ajout/extension des tests pour couvrir ignore global, skip sélectif et sortie JSON bot-friendly.

### Fichiers modifiés
- `main.py`
- `craft/ignore_manager.py`
- `craft/utils.py`
- `tests/test_aicc.py`
- `tests/test_ignore_manager.py`
- `README.md`

### Validation et tests
- Commande exécutée: `cd /opt/AIContextCraft && .aicc_venv/bin/python -m pytest tests`
- Tests collectés: **33**
- Résultat: **33 passed**
- Warnings: **96** (dépréciations `pathspec` sur `gitwildmatch`, sans échec)

### Remarques
- Correction effectuée après incident de contexte: branche créée initialement au mauvais dépôt, nettoyée dans `wp-manager`, puis recréée correctement dans `AIContextCraft`.