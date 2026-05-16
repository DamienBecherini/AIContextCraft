---
name: report-save-prompt-rule
overview: Ajouter une consigne Cursor toujours active dans AIContextCraft pour demander, en fin d’implémentation, si le compte rendu affiché dans le chat doit être sauvegardé à la fin du plan.
todos:
  - id: update-aicc-rule
    content: Étendre la règle plan-publication-policy.mdc dans AIContextCraft avec la consigne de sauvegarde du compte rendu
    status: completed
  - id: validate-rule-structure
    content: Vérifier le frontmatter et la clarté des instructions obligatoires
    status: completed
  - id: publish-generated-plan
    content: Publier le plan validé sous docs/plans/<branch-name>/ avec renommage horodaté
    status: in_progress
isProject: false
---

# Ajout de consigne de sauvegarde du compte rendu

## Objectif
Mettre en place, dans `AIContextCraft`, une règle Cursor toujours active qui impose en fin d’implémentation :
- demander explicitement si le compte rendu d’implémentation affiché dans le chat doit être sauvegardé,
- si l’utilisateur répond oui, l’ajouter à la fin du fichier de plan avec un séparateur clair entre plan et compte rendu.

## Fichiers ciblés
- Règle à enrichir dans [`/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc)

## Plan d’implémentation
1. **Étendre la règle de `AIContextCraft`**
   - Conserver la politique actuelle (publication du plan + procédure de tests).
   - Ajouter une section “Post-implementation report persistence” qui impose :
     - en fin d’exécution, afficher le compte rendu dans le chat,
     - demander à l’utilisateur s’il faut le sauvegarder,
     - en cas de réponse positive, l’append en fin de plan avec séparateur explicite (par ex. `---` puis titre `## Compte rendu d’implémentation`).

2. **Validation rapide de la règle**
   - Vérifier le frontmatter `.mdc` (`description`, `alwaysApply: true`) et la lisibilité.
   - Vérifier que la formulation est non ambiguë sur le flux : question utilisateur obligatoire avant toute sauvegarde du compte rendu.

3. **Publication du plan (demandée)**
   - Ajouter une étape de publication dans l’exécution :
     - créer `docs/plans/<branch-name>/` si nécessaire,
     - copier le plan validé,
     - renommer en `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` (kebab-case ASCII).

## Résultat attendu
- Le dépôt AIContextCraft possède une règle Cursor qui force la question de sauvegarde du compte rendu de fin d’implémentation.
- Si l’utilisateur confirme, le compte rendu est ajouté en fin du plan avec séparation claire.
- Le plan de travail est également publié sous `docs/plans/<branch-name>/` avec nom horodaté.

---

## Compte rendu d'implementation

Implementation terminee, tous les to-dos du plan sont completes pour AIContextCraft.

- Regle `plan-publication-policy.mdc` enrichie dans `AIContextCraft` avec la section `Post-Implementation Report Persistence`.
- Le flux impose maintenant : afficher le compte rendu en chat, demander confirmation, puis sauvegarder dans le plan uniquement si reponse positive.
- Format d'ajout precise dans la regle : separateur `---`, titre `## Compte rendu d'implementation`, puis contenu du rapport.

### Fichiers modifies

- `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`
- `/opt/AIContextCraft/docs/plans/main/2026_05_16_23:38_report-save-prompt-rule.plan.md`

### Validation

- Frontmatter de la regle verifie (`description`, `alwaysApply: true`).
- Contenu de la regle verifie pour un usage cible AIContextCraft.