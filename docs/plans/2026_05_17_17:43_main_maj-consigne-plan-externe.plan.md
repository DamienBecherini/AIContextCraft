---
name: Maj consigne plan externe
overview: Mettre à jour la règle Cursor de AIContextCraft pour imposer une vérification d’un plan collé depuis une autre IA, puis la génération d’un plan autoporté amélioré avant toute demande d’enregistrement, en précisant que la proposition de commit vient seulement après la réponse à la question d’append du rapport.
todos:
  - id: read-existing-rule
    content: Confirmer la structure actuelle de la règle AIContextCraft pour préserver toutes les consignes existantes
    status: pending
  - id: draft-external-plan-section
    content: Rédiger la nouvelle section imposant vérification et réécriture autoportée d’un plan externe
    status: pending
  - id: merge-with-existing-policy
    content: Intégrer la section sans altérer les sections existantes (publication, report persistence, commit proposal, tests)
    status: pending
  - id: validate-final-rule
    content: Relire et vérifier la cohérence du flux complet avant demande d’enregistrement
    status: pending
  - id: publish-plan-copy-step
    content: Inclure dans l’exécution la copie du plan dans docs/plans/<branch-name>/ avec nom horodaté normalisé
    status: pending
isProject: false
---

# Mise à jour des consignes de traitement des plans externes

## Objectif

Ajouter une section de règle qui force l’agent à:

- analyser un plan collé depuis une autre IA,
- vérifier sa cohérence/complétude,
- générer un plan **autoporté** corrigé/amélioré si nécessaire (sans référence au plan source),
- conserver les consignes existantes, avec un ordre explicite: d’abord la question d’append du rapport, puis la proposition de message de commit.

La règle existante est conservée et enrichie dans `[/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc)`.

## Modifications prévues

- Ajouter une nouvelle section (ex: `## External Plan Intake and Self-Contained Rewrite`) dans `[/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc)`.
- Définir explicitement le flux obligatoire:
  1. détecter qu’un plan externe est fourni/collé,
  2. valider qualité/risques/lacunes,
  3. produire un nouveau plan autoporté (sans mention du plan d’origine),
  4. intégrer les corrections/améliorations pertinentes,
  5. poser la question d’enregistrement/publication du plan si applicable,
  6. après implémentation, poser la question d’append du compte rendu au plan,
  7. seulement après la réponse utilisateur à cette question, proposer le message de commit.
- Préciser les critères de validation minimum (clarté, faisabilité, ordre d’exécution, tests/validation, risques, dépendances).
- Garantir la compatibilité avec les règles déjà présentes (question de publication, persistance du compte rendu, proposition de commit message, procédure de tests Python), en verrouillant l’ordre “question d’append -> réponse utilisateur -> proposition commit”.

## Vérification

- Relire la règle modifiée pour confirmer qu’aucune consigne existante n’a été supprimée.
- Vérifier que la séquence “réécriture autoportée avant demande d’enregistrement” est non ambiguë et prioritaire quand un plan externe est collé.
- Vérifier que la proposition de commit n’apparaît jamais avant la réponse utilisateur à la question d’append du rapport.

## Publication du plan (demandée)

- Créer `docs/plans/<branch-name>/` si nécessaire.
- Copier le plan validé dans ce dossier.
- Renommer en `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` avec `<plan-title>` en kebab-case ASCII.

---
## Compte rendu d'implementation

### Changements realises

- Ajout d'une section `## External Plan Intake and Self-Contained Rewrite` dans `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`.
- Cette section impose l'analyse d'un plan externe, sa reecriture en plan autoporte, sans reference au plan source, et son amelioration/correction si pertinent.
- La section commit a ete renforcee pour exiger l'ordre strict: question d'append du rapport -> reponse utilisateur -> proposition de message de commit.

### Fichiers modifies

- `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`
- `/opt/AIContextCraft/docs/plans/main/2026_05_17_17:43_maj-consigne-plan-externe.plan.md`

### Validation

- Relecture complete de la regle pour verifier que les consignes existantes sont conservees.
- Verification de coherence du flux "plan externe -> plan autoporte -> confirmation".
- Verification explicite de la contrainte d'ordre pour la proposition du commit.
- Verification linter via `ReadLints`: aucune erreur.
