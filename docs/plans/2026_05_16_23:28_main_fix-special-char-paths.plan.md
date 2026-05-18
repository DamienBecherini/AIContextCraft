---
name: fix special-char paths
overview: Corriger la gestion des chemins avec caractères spéciaux et séparateurs Windows dans AIContextCraft, de la lecture YAML jusqu’au matching des patterns, avec tests de non-régression et documentation de configuration.
todos:
  - id: improve-yaml-error
    content: Améliorer le message d’erreur yaml.YAMLError avec conseils concrets sur backslashes/quotes
    status: completed
  - id: normalize-patterns
    content: Implémenter la normalisation des patterns (\\ vers /) avant PathSpec
    status: completed
  - id: add-special-char-tests
    content: Ajouter tests et fixtures Unicode + chemins Windows + erreur YAML guidée
    status: completed
  - id: update-readme-config
    content: Documenter les bonnes pratiques YAML/patterns pour caractères spéciaux
    status: completed
  - id: publish-plan-aicontextcraft
    content: Publier la copie du plan validé dans docs/plans/<branch-name>/ du projet AIContextCraft
    status: in_progress
isProject: false
---

# Correction des chemins spéciaux (AIContextCraft)

## Objectif
Permettre l’usage fiable de noms de dossiers/fichiers contenant des caractères Unicode (emoji, accents, etc.) et de séparateurs Windows (`\\`) dans `include_patterns`, sans erreur de parsing ni mismatch de filtrage.

## Constat actuel
- Le chargement de configuration repose sur `yaml.safe_load` dans [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py).
- Une valeur comme `"🚀 Projets\🏰 Proxmox Homelab"` dans un scalaire YAML double-quoted échoue avant toute logique applicative (`unknown escape character`).
- Le moteur de matching compare des chemins normalisés en `/` côté scan, mais les patterns utilisateur ne sont pas normalisés symétriquement.

## Plan d’implémentation
1. **Sécuriser le chargement YAML avec message guidé**
   - Dans [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py), enrichir le bloc `except yaml.YAMLError` pour détecter les erreurs d’escape liées aux backslashes et afficher une aide claire :
     - préférer les slashs `/` dans les patterns,
     - ou utiliser des guillemets simples YAML,
     - ou doubler les backslashes (`\\\\`) si nécessaire.
   - Garder la sortie en erreur explicite (pas de fallback silencieux ambigu).

2. **Normaliser les patterns de chemins utilisateur**
   - Ajouter une normalisation centralisée des patterns dans [`/opt/AIContextCraft/aicc.py`](/opt/AIContextCraft/aicc.py) avant création des `PathSpec` :
     - transformer les séparateurs Windows `\\` en `/`,
     - conserver les caractères Unicode tels quels,
     - appliquer la normalisation à `include_patterns`, `common_filters`, `project_only_filters`, `tree_only_filters`.
   - Vérifier que la logique de matching existante (`relative_path.replace('\\', '/')`) reste cohérente avec cette normalisation.

3. **Ajouter des tests de non-régression ciblés**
   - Étendre [`/opt/AIContextCraft/tests/test_aicc.py`](/opt/AIContextCraft/tests/test_aicc.py) avec des cas dédiés :
     - config valide avec pattern contenant emoji + slash `/` => inclusion attendue,
     - config avec chemins style Windows (`\\`) => comportement identique après normalisation,
     - config YAML invalide (double-quoted + escape invalide) => message d’erreur guidé attendu.
   - Ajouter les fixtures de projet minimales sous [`/opt/AIContextCraft/tests/test_projects`](/opt/AIContextCraft/tests/test_projects) avec dossiers/fichiers Unicode.

4. **Documenter la syntaxe recommandée**
   - Mettre à jour la section config de [`/opt/AIContextCraft/README.md`](/opt/AIContextCraft/README.md) avec exemples sûrs pour chemins spéciaux :
     - usage recommandé des `/`,
     - exemples avec caractères Unicode,
     - rappel sur YAML (`'...'` ou `\\\\` en double-quoted).

5. **Valider et publier le plan dans AIContextCraft**
   - Exécuter les tests concernés.
   - Créer (si absent) `docs/plans/<branch-name>/` dans le projet `AIContextCraft`.
   - Copier le plan validé dans ce dossier en le renommant au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` (titre en kebab-case ASCII).

## Résultat attendu
- Plus de blocage pour les noms Unicode dès lors que la config YAML est correctement formée.
- Les patterns saisis avec séparateurs Windows fonctionnent de façon prévisible via normalisation.
- Les utilisateurs ont une documentation claire pour éviter les erreurs YAML liées aux backslashes.

---

## Compte rendu d'implementation

Implementation terminee, tous les to-dos du plan sont completes.

- Correctif applique dans AIContextCraft pour gerer les chemins speciaux/Unicode et les separateurs Windows dans les patterns.
- Message d'erreur YAML ameliore pour guider clairement les cas `\` invalides en double quotes.
- Normalisation centralisee des patterns (`\` -> `/`) avant creation des PathSpec.
- Tests de non-regression ajoutes (Unicode, backslashes, erreur YAML guidee).
- Documentation mise a jour avec exemples recommandes.
- Copie du plan publiee dans AIContextCraft a `docs/plans/main/2026_05_16_23:28_fix-special-char-paths.plan.md`.

### Fichiers modifies

- `aicc.py`
- `tests/test_aicc.py`
- `README.md`
- `tests/test_projects/special_chars_project/config_slash.yaml`
- `tests/test_projects/special_chars_project/config_backslash.yaml`
- `tests/test_projects/special_chars_project/🚀 Projets/🏰 Proxmox Homelab/context.txt`
- `tests/test_projects/special_chars_project/other/ignored.txt`
- `docs/plans/main/2026_05_16_23:28_fix-special-char-paths.plan.md`

### Validation

- Lints verifies sur fichiers edites: aucune erreur.
- Tests executes:
  - `cd /opt/AIContextCraft && .venv/bin/python -m pytest -q --confcutdir=/opt/AIContextCraft tests/test_aicc.py`
- Resultat: `4 passed`