---
name: zero-config-plug-play
overview: "Implémenter une phase “plug & play” : XML par défaut, presse-papiers auto avec limite de taille, sortie dans build/, et détection de config sans écriture forcée."
todos:
  - id: cli-clipboard-redesign
    content: Refondre les arguments CLI clipboard et appliquer la limite de taille avant copie dans les deux flux d’exécution.
    status: completed
  - id: zero-config-defaults
    content: Implémenter l’auto-détection de config sans écriture disque et calculer un output par défaut dynamique dans build/ selon le format.
    status: completed
  - id: tests-and-docs
    content: Mettre à jour README et tests pour le nouveau défaut XML, la logique clipboard-limit/no-clipboard et le mode Zero-Config.
    status: completed
  - id: validate-and-publish-plan
    content: Exécuter la procédure pytest via .aicc_venv, collecter les preuves, puis publier le plan dans docs/plans/feature/zero-config-plug-play/ avec nom horodaté conforme.
    status: completed
isProject: false
---

# Plan d’implémentation — Phase 1.5 Zero-Config Plug & Play

## Objectif

Livrer une expérience par défaut sans friction : exécution sans fichier de config obligatoire, format `xml` par défaut, copie presse-papiers automatique mais bornée, et chemin de sortie propre dans `build/`.

## Fichiers ciblés

- `[/opt/AIContextCraft/main.py](/opt/AIContextCraft/main.py)`
- `[/opt/AIContextCraft/tests/test_aicc.py](/opt/AIContextCraft/tests/test_aicc.py)`
- `[/opt/AIContextCraft/README.md](/opt/AIContextCraft/README.md)`

## Changements techniques

1. **Refondre les options CLI presse-papiers dans `main.py`**

- Remplacer le booléen `--clipboard` par une limite `-cb/--clipboard-limit` (float, défaut `10.0` MB).
- Ajouter `--no-clipboard` pour désactivation explicite.
- Définir une politique claire : copie automatique si non désactivée **et** taille <= limite.

1. **Ajouter la garde de taille avant copie**

- Calculer la taille réelle de `final_output_str` en octets (`len(final_output_str.encode(args.encoding))`).
- Appliquer la même vérification dans les 2 sorties (`--git-diff` et flux standard) avant appel à `maybe_copy_to_clipboard`.
- En cas de dépassement, afficher un avertissement utilisateur via `rich` et journaliser la décision de non-copie.

1. **Basculer les défauts de format/sortie vers un mode plug & play**

- Passer le défaut de sortie à `xml` (CLI + fallback config).
- Si aucun `--output` ni `output_path` valide en config, construire dynamiquement `build/aicc_context.<ext>` avec mapping :
  - `text -> txt`
  - `xml -> xml`
  - `markdown -> md`
- Conserver le comportement timestamp existant, puis garantir `mkdir(parents=True, exist_ok=True)`.

1. **Implémenter la détection Zero-Config sans création de YAML**

- Si `--config` est absent, chercher dans le dossier cible (`project_path` ou `.`) dans cet ordre : `.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config-concat-code.`.
- Si trouvé : charger et logguer le chemin détecté automatiquement.
- Si non trouvé : rester en configuration mémoire (`DEFAULT_CONFIG`) et logguer explicitement le mode Zero-Config activé.
- Supprimer la logique de création automatique de `config.yaml` sur disque.

1. **Mettre à jour la documentation utilisateur**

- Mettre à jour la table des options, le snapshot `--help`, et les exemples dans `[/opt/AIContextCraft/README.md](/opt/AIContextCraft/README.md)`.
- Documenter clairement :
  - format XML par défaut,
  - copie presse-papiers automatique avec limite 10 MB,
  - `--no-clipboard`,
  - auto-détection de config sans écriture forcée.

1. **Adapter les tests existants et compléter la couverture**

- Ajuster les tests affectés par le changement de défaut (`text` -> `xml`) en explicitant `--format text` lorsque l’assertion dépend du format texte.
- Ajouter/mettre à jour des tests pour :
  - non-copie au-delà de la limite,
  - copie désactivée via `--no-clipboard`,
  - fallback sortie `build/aicc_context.<ext>`,
  - détection automatique des noms de config,
  - absence de création de `config.yaml`.

1. **Validation obligatoire (procédure projet)**

- Vérifier/initialiser l’environnement virtuel `.aicc_venv` puis exécuter :
  - `.aicc_venv/bin/python -m pytest tests`
- Reporter dans le compte-rendu :
  - nombre de tests collectés,
  - statut pass/fail,
  - warnings éventuels.

1. **Publication du plan (demandée)**

- Copier le plan validé vers `docs/plans/feature/zero-config-plug-play/`.
- Le renommer au format `YYYY_MM_DD_HH:MM_phase-1-5-zero-config.plan.md` (titre normalisé en kebab-case ASCII).

## Risques ciblés

- Régression de compatibilité tests liée au nouveau format par défaut.
- Incohérence de comportement clipboard entre flux standard et mode `--git-diff` si la garde n’est pas mutualisée.
- Confusion utilisateur si priorité `CLI > config auto-détectée > defaults` n’est pas explicitement logguée.

## Critères d’acceptation

- Exécution `python main.py` sans config préalable réussie, sans création de YAML, avec sortie dans `build/`.
- Sortie par défaut en XML.
- Copie presse-papiers effectuée uniquement si autorisée et sous limite.
- README aligné avec le comportement réel du CLI.
- Suite de tests `pytest` verte avec preuves de collecte/résultat/warnings.

---
## Compte rendu d'implementation

### Changements réalisés
- `main.py`
  - Remplacement de `--clipboard` par `-cb/--clipboard-limit` (défaut `10.0`) et ajout de `--no-clipboard`.
  - Ajout d'une garde de taille (`len(final_output_str.encode(args.encoding))`) avant copie, appliquée au flux standard et à `--git-diff`.
  - Passage du format par défaut à `xml` (CLI + fallback).
  - Fallback de sortie dynamique vers `build/aicc_context.<ext>` (`txt|xml|md`) si aucun output n'est fourni.
  - Implémentation du Zero-Config: recherche auto de `.aicc.yaml`, `aicc.yaml`, `aicc.yml`, `config.yaml`.
  - Suppression de la création automatique de `config.yaml` sur disque.
  - Ajustement du mode `--git-diff` pour forcer une sortie `.md`.

- `tests/test_aicc.py`
  - Mise à jour des tests dépendants du format texte via `--format text`.
  - Ajout de `--no-clipboard` dans les tests non liés au clipboard pour stabilité.
  - Ajout de tests: limite clipboard, `--no-clipboard`, fallback `build/aicc_context.<ext>`, auto-détection `.aicc.yaml`, non-création de `config.yaml`.

- `README.md`
  - Mise à jour des options CLI (`--clipboard-limit`, `--no-clipboard`), du défaut `xml`, du comportement Zero-Config et du fallback output dans `build/`.
  - Mise à jour du snapshot `--help` et des exemples.

### Validation / Tests
- Environnement: `.aicc_venv` existant (utilisé).
- Commande de la procédure:
  - `.aicc_venv/bin/python -m pytest tests` (bloquée localement par chargement d'un `conftest` externe au workspace actif).
- Exécution isolée projet:
  - `PYTHONPATH=/opt/AIContextCraft .aicc_venv/bin/python -m pytest /opt/AIContextCraft/tests --rootdir=/opt/AIContextCraft`
- Résultats:
  - Tests collectés: `26`
  - Statut: `26 passed / 0 failed`
  - Warnings: `54` (dépréciations `pathspec` liées à `gitwildmatch`)
