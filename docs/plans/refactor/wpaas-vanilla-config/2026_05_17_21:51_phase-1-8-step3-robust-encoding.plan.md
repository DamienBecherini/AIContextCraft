---
name: phase-1.8-step3-robust-encoding
overview: Sécuriser la lecture des fichiers concaténés en détectant automatiquement les encodages non UTF-8 et en évitant toute corruption silencieuse des caractères, puis valider avec des tests ciblés.
todos:
  - id: add-dependency
    content: Ajouter `charset-normalizer` dans `/opt/AIContextCraft/requirements.txt`.
    status: completed
  - id: add-read-helper
    content: Implémenter `read_file_with_fallback` dans `/opt/AIContextCraft/craft/utils.py` avec détection d'encodage et fallback `errors=replace`.
    status: completed
  - id: wire-context-builder
    content: Remplacer la lecture `errors='ignore'` de `ContextBuilder._process_files()` par l'utilitaire robuste.
    status: completed
  - id: add-encoding-tests
    content: Créer des tests unitaires dédiés à l'encodage dans `/opt/AIContextCraft/tests/test_context_builder.py`.
    status: completed
  - id: run-pytests
    content: Exécuter pytest via `.aicc_venv` (ciblé puis suite complète) et collecter les résultats.
    status: completed
  - id: publish-plan-copy
    content: Copier le plan validé dans `docs/plans/<branch-name>/` avec nom horodaté conforme.
    status: completed
isProject: false
---

# Plan d'implémentation — Robustesse d'encodage

## Objectif
Remplacer la lecture permissive actuelle des fichiers (`errors='ignore'`) par une lecture robuste avec détection d'encodage, afin de conserver les caractères accentués et d'éviter les pertes silencieuses de données.

## Portée
- Mettre à jour la logique de lecture dans [`/opt/AIContextCraft/craft/context_builder.py`](/opt/AIContextCraft/craft/context_builder.py).
- Ajouter une fonction utilitaire de lecture robuste dans [`/opt/AIContextCraft/craft/utils.py`](/opt/AIContextCraft/craft/utils.py).
- Ajouter la dépendance dans [`/opt/AIContextCraft/requirements.txt`](/opt/AIContextCraft/requirements.txt).
- Ajouter des tests unitaires dédiés (nouveau fichier recommandé: [`/opt/AIContextCraft/tests/test_context_builder.py`](/opt/AIContextCraft/tests/test_context_builder.py)).

## Implémentation
1. Ajouter `charset-normalizer` à la fin de [`/opt/AIContextCraft/requirements.txt`](/opt/AIContextCraft/requirements.txt).
2. Créer `read_file_with_fallback(file_path: Path, default_encoding: str = 'utf-8') -> str` dans [`/opt/AIContextCraft/craft/utils.py`](/opt/AIContextCraft/craft/utils.py) avec ce comportement:
   - tentative 1: lecture stricte avec `default_encoding`;
   - en cas de `UnicodeDecodeError`: utiliser `charset_normalizer.from_path(file_path).best()`;
   - si un match existe: retourner le texte décodé (et logger l'encodage détecté en niveau debug/info);
   - sinon: fallback final avec `errors='replace'` + warning explicite (politique validée).
3. Modifier [`/opt/AIContextCraft/craft/context_builder.py`](/opt/AIContextCraft/craft/context_builder.py) pour remplacer `open(..., errors='ignore')` dans `_process_files()` par l'appel à `read_file_with_fallback(file_path, self.encoding)`.
4. Ajouter des tests unitaires d'encodage:
   - cas `iso-8859-1` ou `windows-1252` contenant des accents;
   - assertion que les caractères accentués sont préservés après lecture;
   - cas de non-détection: vérifier fallback `errors='replace'` et absence de plantage.

## Validation
1. Préparer l'environnement local:
   - vérifier l'existence de `.aicc_venv` à la racine de [`/opt/AIContextCraft`](/opt/AIContextCraft);
   - le créer si absent (`python -m venv .aicc_venv`) puis installer les dépendances (`.aicc_venv/bin/pip install -r requirements.txt`).
2. Exécuter les tests:
   - ciblé: `.aicc_venv/bin/python -m pytest tests/test_context_builder.py`;
   - non-régression: `.aicc_venv/bin/python -m pytest tests`.
3. Reporter les preuves de test: nombre de tests collectés, statut pass/fail, warnings éventuels.

## Publication du plan
- Copier le plan validé vers `docs/plans/<branch-name>/` (dans le projet AIContextCraft).
- Renommer la copie au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` avec `<plan-title>` en kebab-case ASCII.

---
## Compte rendu d'implementation

### Changements appliques
- Ajout de la dependance `charset-normalizer` dans `requirements.txt`.
- Ajout de `read_file_with_fallback(file_path, default_encoding)` dans `craft/utils.py`:
  - lecture stricte avec l'encodage par defaut;
  - en cas d'echec Unicode, detection via `charset_normalizer.from_path(...).best()`;
  - fallback final en `errors='replace'` avec warning explicite si aucun encodage fiable n'est detecte.
- Remplacement de la lecture `open(..., errors='ignore')` dans `ContextBuilder._process_files()` par `read_file_with_fallback(...)` dans `craft/context_builder.py`.
- Ajout d'un nouveau fichier de tests `tests/test_context_builder.py` avec:
  - test de lecture `iso-8859-1` (accents preserves),
  - test de fallback `errors='replace'` quand la detection ne renvoie pas de match,
  - test d'integration de `_process_files()` pour verifier la preservation des accents.

### Validation / Tests
- Environnement: `.aicc_venv` existant utilise.
- Commande ciblee:
  - `PYTHONPATH=/opt/AIContextCraft .aicc_venv/bin/python -m pytest --rootdir=/opt/AIContextCraft --confcutdir=/opt/AIContextCraft -o cache_dir=/opt/AIContextCraft/.pytest_cache /opt/AIContextCraft/tests/test_context_builder.py`
  - Resultat: `collected 3 items`, `3 passed`.
- Commande suite complete:
  - `PYTHONPATH=/opt/AIContextCraft .aicc_venv/bin/python -m pytest --rootdir=/opt/AIContextCraft --confcutdir=/opt/AIContextCraft -o cache_dir=/opt/AIContextCraft/.pytest_cache /opt/AIContextCraft/tests`
  - Resultat: `collected 36 items`, `36 passed`.
- Warnings:
  - warnings de depreciation `pathspec` (utilisation de `gitwildmatch`) deja presents dans la base de tests;
  - aucun warning lie au nouveau mecanisme d'encodage.