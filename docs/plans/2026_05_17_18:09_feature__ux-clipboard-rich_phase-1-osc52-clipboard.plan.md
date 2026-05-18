---
name: phase-1-osc52-clipboard
overview: Ajouter un fallback OSC 52 dans la copie presse-papiers pour supporter les exécutions SSH/headless sans casser le flux console existant.
todos:
  - id: update-clipboard-function
    content: Mettre à jour `maybe_copy_to_clipboard` dans `main.py` pour fallback de `pyperclip` vers OSC 52.
    status: completed
  - id: add-safe-logging-path
    content: Conserver les messages utilisateur `rich` et la journalisation warning uniquement quand OSC 52 échoue.
    status: completed
  - id: validate-behavior
    content: Valider manuellement les 3 scénarios (clipboard local OK, fallback OSC 52, échec OSC 52).
    status: completed
  - id: publish-plan-copy
    content: Copier le plan validé dans `docs/plans/<branch-name>/` en `YYYY_MM_DD_HH:MM_phase-1-osc52-clipboard.plan.md`.
    status: in_progress
  - id: save-report
    content: Demander si le compte-rendu d’implémentation doit être sauvegardé dans le plan, puis agir selon la réponse.
    status: pending
isProject: false
---

# Plan d’implémentation — Support OSC 52 (SSH/headless)

## Objectif
Rendre `--clipboard` fiable en environnement distant/headless en conservant d’abord la copie locale via `pyperclip`, puis en basculant vers OSC 52 si le backend système est indisponible.

## Fichiers concernés
- [main.py](/opt/AIContextCraft/main.py)
- [docs/plans/<branch-name>/YYYY_MM_DD_HH:MM_phase-1-osc52-clipboard.plan.md](/opt/AIContextCraft/docs/plans)

## Changements à réaliser
1. Dans [main.py](/opt/AIContextCraft/main.py), compléter les imports avec `base64` (et garder `sys` déjà présent).
2. Modifier `maybe_copy_to_clipboard(clipboard_enabled, content, console)` pour appliquer ce flux:
   - **Étape A (locale)**: tenter `pyperclip.copy(content)` puis afficher le succès local actuel.
   - **Étape B (fallback OSC 52)**: uniquement si exception `pyperclip.PyperclipException` ou `pyperclip.PyperclipWindowsException`:
     - encoder `content` en base64 UTF-8,
     - écrire `\x1b]52;c;{encoded}\x07` sur `stdout`,
     - forcer `flush()`,
     - afficher `[green]Contenu envoyé au presse-papiers via SSH (OSC 52).[/green]`.
   - **Étape C (erreur fallback)**: encapsuler l’étape B dans un `try/except Exception` pour conserver un warning propre en log, sans interrompre le programme.
3. Préserver l’ergonomie console:
   - ne pas altérer les messages `rich` existants hors du périmètre presse-papiers,
   - garder une exécution non bloquante si clipboard local et OSC 52 échouent.

## Vérification
1. **Cas local GUI**: vérifier que le message “Contenu copié dans le presse-papiers.” apparaît et que le contenu est collable.
2. **Cas SSH/headless sans backend clipboard**: simuler/observer une `PyperclipException`, vérifier l’émission OSC 52 et le message de succès OSC 52.
3. **Cas erreur OSC 52**: forcer une erreur sur l’écriture stdout pour confirmer qu’un warning est loggé sans crash.

## Publication du plan (demandée)
Après validation du plan, ajouter une étape d’exécution qui:
1. crée `docs/plans/<branch-name>/` si nécessaire,
2. copie le plan validé dans ce dossier,
3. renomme le fichier en `YYYY_MM_DD_HH:MM_phase-1-osc52-clipboard.plan.md`.

---
## Compte rendu d'implementation

- Changement principal: ajout d'un fallback OSC 52 dans `maybe_copy_to_clipboard` après échec de `pyperclip`.
- Comportement:
  - tentative locale conservée via `pyperclip.copy(content)`,
  - fallback OSC 52 sur exceptions `PyperclipException`/`PyperclipWindowsException`,
  - message utilisateur Rich de succès OSC 52,
  - warning non bloquant uniquement si l'étape OSC 52 échoue.
- Fichiers modifiés:
  - `main.py`
  - `docs/plans/feature/ux-clipboard-rich/2026_05_17_18:09_phase-1-osc52-clipboard.plan.md` (append du compte-rendu)
- Validation:
  - lint: aucun problème sur `main.py`,
  - tests: `21 passed`, `54 warnings`,
  - collecte: `21` tests.