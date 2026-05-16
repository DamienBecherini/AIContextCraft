---
name: report-save-prompt-rule
overview: Ajouter une consigne Cursor toujours active dans chaque dépôt pour demander, en fin d’implémentation, si le compte rendu affiché dans le chat doit être sauvegardé à la fin du plan, puis dupliquer/harmoniser les règles entre les deux projets.
todos:
  - id: update-wp-rule
    content: Étendre la règle plan-publication-policy.mdc dans wp-manager avec la consigne de sauvegarde du compte rendu
    status: completed
  - id: sync-rule-to-aicc
    content: Créer .cursor/rules dans AIContextCraft et y dupliquer la règle harmonisée
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
Mettre en place, dans chaque dépôt (`wp-manager` et `AIContextCraft`), une règle Cursor toujours active qui impose en fin d’implémentation :
- demander explicitement si le compte rendu d’implémentation affiché dans le chat doit être sauvegardé,
- si l’utilisateur répond oui, l’ajouter à la fin du fichier de plan avec un séparateur clair entre plan et compte rendu.

## Fichiers ciblés
- Règle existante à enrichir dans [`/opt/wp-manager/.cursor/rules/plan-publication-policy.mdc`](/opt/wp-manager/.cursor/rules/plan-publication-policy.mdc)
- Nouvelle règle miroir dans [`/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc)

## Plan d’implémentation
1. **Étendre la règle de `wp-manager`**
   - Conserver la politique actuelle (publication du plan + procédure de tests).
   - Ajouter une section “Post-implementation report persistence” qui impose :
     - en fin d’exécution, afficher le compte rendu dans le chat,
     - demander à l’utilisateur s’il faut le sauvegarder,
     - en cas de réponse positive, l’append en fin de plan avec séparateur explicite (par ex. `---` puis titre `## Compte rendu d’implémentation`).

2. **Dupliquer/harmoniser la règle dans `AIContextCraft`**
   - Créer le dossier `.cursor/rules` si absent dans `AIContextCraft`.
   - Copier la règle mise à jour depuis `wp-manager` vers `AIContextCraft` pour assurer la même consigne dans chaque dépôt.

3. **Validation rapide des règles**
   - Vérifier le frontmatter `.mdc` (`description`, `alwaysApply: true`) et la lisibilité.
   - Vérifier que la formulation est non ambiguë sur le flux : question utilisateur obligatoire avant toute sauvegarde du compte rendu.

4. **Publication du plan (demandée)**
   - Ajouter une étape de publication dans l’exécution :
     - créer `docs/plans/<branch-name>/` si nécessaire,
     - copier le plan validé,
     - renommer en `YYYY_MM_DD_HH:MM_<plan-title>.plan.md` (kebab-case ASCII).

## Résultat attendu
- Les deux dépôts possèdent une règle Cursor alignée qui force la question de sauvegarde du compte rendu de fin d’implémentation.
- Si l’utilisateur confirme, le compte rendu est ajouté en fin du plan avec séparation claire.
- Le plan de travail est également publié sous `docs/plans/<branch-name>/` avec nom horodaté.