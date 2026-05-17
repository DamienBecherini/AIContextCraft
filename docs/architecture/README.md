# Architecture Diagrams

Ce dossier centralise les diagrammes d'architecture du projet en mode diagrams-as-code.

## Contenu

- `structurizr/workspace.dsl`: modele C4 de reference (system context + container + processing flow).
- `structurizr/out/`: exports generes par Structurizr CLI.
- `assets/`: images SVG versionnees pour la documentation.
- `sequences/run-standard-flow.md`: sequence du workflow standard (concat de contexte).
- `sequences/git-diff-flow.md`: sequence du workflow `--git-diff`.

## Commande unique de regeneration

Depuis la racine du repo:

```bash
./scripts/architecture/generate-all.sh
```

## Prerequis

- Option A: `structurizr` installe localement.
- Option B: `docker` disponible pour executer `structurizr/structurizr`.
- Pour les SVG:
  - `plantuml` local ou Docker (`plantuml/plantuml`)
  - `mmdc` local ou Docker (`minlag/mermaid-cli`)

## Scripts disponibles

- `scripts/architecture/render-structurizr.sh`
  - Exporte le modele Structurizr en PlantUML Structurizr dans `docs/architecture/structurizr/out`.
- `scripts/architecture/validate-mermaid.sh`
  - Extrait le premier bloc Mermaid de chaque fichier de `docs/architecture/sequences` puis valide le rendu.
- `scripts/architecture/render-diagram-assets.sh`
  - Convertit les diagrammes en SVG versionnes dans `docs/architecture/assets`.
- `scripts/architecture/generate-all.sh`
  - Lance export, validation et generation des assets en sequence.

## Regles de mise a jour

1. Modifier d'abord `structurizr/workspace.dsl` pour toute evolution de l'architecture statique.
2. Mettre a jour les sequences Mermaid lors de toute evolution du pipeline standard ou du mode `--git-diff`.
3. Regenerer les artefacts avec `./scripts/architecture/generate-all.sh`.
4. Verifier que les vues C4 SVG sont presentes dans `docs/architecture/assets/`:
   - `system-context.svg`
   - `container-view.svg`
   - `processing-flow-view.svg`
5. Verifier que les sequences SVG sont presentes:
   - `run-standard-flow.svg`
   - `git-diff-flow.svg`

## Apercu des diagrammes publies

### C4 - System Context
![System Context](./assets/system-context.svg)

### C4 - Container View
![Container View](./assets/container-view.svg)

### C4 - Processing Flow View
![Processing Flow View](./assets/processing-flow-view.svg)

### Sequence - Run Standard
![Run Standard Flow](./assets/run-standard-flow.svg)

### Sequence - Git Diff
![Git Diff Flow](./assets/git-diff-flow.svg)
