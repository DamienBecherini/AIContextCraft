---
name: phase-1-ux-clipboard
overview: Implémenter l’UX finale de la phase 1 avec Rich (console + progression) et copie presse-papiers robuste en environnement headless, sans polluer les logs fichiers.
todos:
  - id: branch-and-plan-file
    content: Créer `feature/ux-clipboard-rich` et enregistrer le plan dans `docs/plans/feature/ux-clipboard-rich/2026_05_17_17:40_phase-1-ux-clipboard.plan.md`.
    status: in_progress
  - id: deps-update
    content: Ajouter `rich` et `pyperclip` dans `requirements.txt`.
    status: pending
  - id: logging-rich-console-plain-file
    content: Adapter `setup_logging` pour Rich en console et texte brut en fichier log.
    status: pending
  - id: clipboard-cli
    content: Ajouter `--clipboard`/`-cb` et implémenter `pyperclip.copy` avec gestion d’erreur headless.
    status: pending
  - id: progress-ui
    content: Utiliser `rich.progress.track` dans la boucle de traitement des fichiers et retirer les logs info perturbateurs.
    status: pending
  - id: tests-hardening
    content: Ajuster/valider les tests de sortie console pour éviter les effets ANSI de Rich.
    status: pending
  - id: run-pytests-venv
    content: Exécuter les tests via `.aicc_venv/bin/python -m pytest tests` et reporter collected/pass-fail/warnings.
    status: pending
  - id: implementation-report-flow
    content: Présenter le compte-rendu, demander s’il faut l’enregistrer dans le plan, puis proposer un message de commit conventionnel.
    status: pending
  - id: publish-plan-copy
    content: Copier le plan validé dans `docs/plans/<branch-name>/` avec nom horodaté `YYYY_MM_DD_HH:MM_<plan-title>.plan.md`.
    status: pending
isProject: false
---

# Plan d'implémentation Phase 1 UX Clipboard + Rich

## Objectif
Ajouter une expérience CLI plus fluide avec:
- une option `--clipboard` robuste (sans crash en SSH/headless),
- une console enrichie via `rich`,
- une barre de progression pendant le traitement,
- des logs `.log` strictement en texte brut (sans ANSI).

## Fichiers ciblés
- [requirements.txt](/opt/AIContextCraft/requirements.txt)
- [craft/utils.py](/opt/AIContextCraft/craft/utils.py)
- [main.py](/opt/AIContextCraft/main.py)
- [tests/test_aicc.py](/opt/AIContextCraft/tests/test_aicc.py)
- [docs/plans/feature/ux-clipboard-rich/2026_05_17_17:40_phase-1-ux-clipboard.plan.md](/opt/AIContextCraft/docs/plans/feature/ux-clipboard-rich/2026_05_17_17:40_phase-1-ux-clipboard.plan.md)

## Étapes d'exécution
1. Créer la branche `feature/ux-clipboard-rich`.
2. Sauvegarder ce plan dans `docs/plans/feature/ux-clipboard-rich/2026_05_17_17:40_phase-1-ux-clipboard.plan.md`.
3. Ajouter `rich` et `pyperclip` à `requirements.txt`.
4. Moderniser `setup_logging` dans `craft/utils.py`:
   - console avec `rich.logging.RichHandler` (temps/chemin masqués),
   - fichier `.log` conservé via `logging.FileHandler` + formatter texte classique,
   - empêcher les séquences ANSI dans le fichier de log.
5. Mettre à jour `main.py`:
   - ajouter `-cb/--clipboard` dans l'argument parser,
   - remplacer les `print()` finaux par `Console().print(...)`,
   - intégrer la copie `pyperclip.copy(final_output_str)` en fin de run conditionnée par `args.clipboard`,
   - encapsuler la copie dans un `try/except pyperclip.PyperclipException` avec warning non bloquant.
6. Remplacer la boucle de traitement des fichiers par une progression `rich.progress.track(...)` et supprimer le log info par fichier (`Traitement de ...`) qui perturbe l'affichage, tout en conservant les logs d'erreur.
7. Stabiliser les tests de sortie console:
   - vérifier `tests/test_aicc.py`,
   - si nécessaire, désactiver la couleur Rich en contexte test (ex. `NO_COLOR`, `TERM=dumb` ou configuration Rich adaptée) pour éviter les caractères ANSI inattendus.
8. Exécuter les tests Python avec la procédure projet:
   - préparer/valider `.aicc_venv` (création + install dépendances si absent),
   - lancer `pytest` via l'interpréteur du venv,
   - reporter nombre de tests collectés, résultat pass/fail, warnings.
9. Produire le compte-rendu d'implémentation (changements, fichiers modifiés, validation), puis demander explicitement si ce compte-rendu doit être enregistré dans le plan.
10. Après la réponse sur la sauvegarde du compte-rendu, proposer un message de commit Conventional Commits incluant la référence du fichier de plan.
11. Publier une copie du plan validé dans `docs/plans/<branch-name>/` en le renommant au format `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` (titre normalisé en kebab-case ASCII).

## Critères de validation
- `--clipboard` fonctionne quand le presse-papiers OS est disponible.
- En environnement headless/SSH sans backend clipboard, le script ne crash pas et affiche un warning clair.
- L'affichage console est enrichi (Rich) sans dégrader la lisibilité.
- Les fichiers `.log` restent propres, sans codes couleur ANSI.
- La progression s'affiche pendant le traitement de `final_file_list`.
- Les tests passent avec la procédure `.aicc_venv` et les résultats sont reportés.

---
## Compte rendu d'implementation

- Branche créée : `feature/ux-clipboard-rich`.
- Plan sauvegardé : `docs/plans/feature/ux-clipboard-rich/2026_05_17_17:40_phase-1-ux-clipboard.plan.md`.
- Dépendances ajoutées dans `requirements.txt` : `rich`, `pyperclip`.
- Logging modernisé dans `craft/utils.py` :
  - console via `RichHandler` (`show_time=False`, `show_path=False`),
  - fichier `.log` conservé en `FileHandler` texte brut.
- UX CLI améliorée dans `main.py` :
  - option `-cb/--clipboard`,
  - copie finale via `pyperclip.copy(final_output_str)`,
  - gestion des environnements headless/SSH via `try/except pyperclip.PyperclipException` avec warning non bloquant,
  - messages de fin migrés vers `Console().print(...)`.
- Traitement des fichiers : remplacement de la boucle classique par `rich.progress.track(...)`.
- Nettoyage d'affichage : suppression du log info par fichier pendant la progression ; conservation des logs d'erreur.
- Durcissement tests sortie console dans `tests/test_aicc.py` avec `NO_COLOR=1` et `TERM=dumb` dans le subprocess.

### Validation

- Commande exécutée : `./.aicc_venv/bin/python -m pytest tests`
- Log généré : `logs/unit_tests_run_20260517_175908.log`
- Tests collectés : `21`
- Résultat : `21 passed`
- Warnings : `54` (dépréciations `pathspec` liées à `gitwildmatch`)
