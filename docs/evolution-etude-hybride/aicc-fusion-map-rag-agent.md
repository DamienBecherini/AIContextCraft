# AIContextCraft - Etude d'evolution hybride (Map + RAG + Agent)

## 1) Contexte et objectif

Ce document formalise l'etude d'evolution de AIContextCraft (AICC) en fusionnant deux approches:

- l'approche actuelle AICC: filtrage robuste + concatenation optimisee pour LLM;
- l'approche **POC Atlas**: orchestration IA (adapters, pipeline RAG, fallback, logique asynchrone).

Objectif produit:
passer d'un "generateur de contexte" statique a un "moteur d'investigation de code" capable de selectionner intelligemment les bons fichiers selon une intention utilisateur, sous contrainte de cout/latence/tokens.


## 2) Etat actuel confirme

### Cote AICC

- Pipeline solide de collecte/filtrage via `ContextBuilder`, `FilterManager`, `IgnoreManager`.
- Formats de sortie adaptes LLM (`xml`, `markdown`, `text`) et stats de taille/tokens.
- Fonctions Python-only pour optimisation de contenu:
  - `--strip-comments` (AST Python),
  - `--headers-only` (signatures Python).
- Roadmap deja alignee avec l'evolution:
  - Phase 2: Tree-sitter multi-langages,
  - Phase 3: focus intelligent.

### Cote POC Atlas

- Pattern Ports/Adapters propre pour brancher des providers LLM.
- `JobOrchestrator` pour centraliser la logique metier (retries, fallback, validation schema).
- `RagPipeline` + `InMemoryVectorStore` demonstrant le flux retrieval -> prompt.


## 3) Conclusion strategique

La logique "base vectorielle + chunking classique" seule n'est pas suffisante pour le code.
La meilleure direction est un pipeline hybride:

1. structure du repo (map/squelette),
2. retrieval lexical + semantique,
3. expansion des dependances,
4. assemblage contextuel sous budget tokens,
5. boucle de demande de contexte manquant.

En bref: **Map-and-Select + Parent-Document RAG + Expansion de graphe + Boucle agentique**.


## 4) Architecture cible recommandee

## 4.1 Pipeline global

1. **Candidate generation (local, sans LLM):**
   - signaux lexicaux (grep/BM25),
   - signaux git (fichiers modifies),
   - heuristiques de chemin/symboles.
2. **Reranking semantique (embeddings):**
   - retrieval au niveau chunk, remonte au document parent.
3. **Expansion structurelle (Tree-sitter):**
   - imports/exports, interfaces/types, tests associes.
4. **Arbitrage budget (policy engine):**
   - top fichiers en contenu complet,
   - dependances en mode headers-only,
   - arret sur plafond tokens.
5. **Prompt final + boucle de correction:**
   - si contexte insuffisant, le modele demande explicitement des fichiers manquants.

## 4.2 Modele de selection (multi-signaux)

Score final par fichier = combinaison ponderee de:

- score lexical,
- score semantique,
- proximite graphe (dependances),
- signal git (recence/changements),
- priorites configurables projet.

Ce ranking multi-signaux est plus fiable qu'un RAG pur.


## 5) Pourquoi c'est coherent avec les briques existantes

### Reutilisation directe AICC

- `ContextBuilder` devient assembleur final sur une liste ciblee de fichiers.
- `Formatter` conserve son role de sortie XML/Markdown optimisee.
- `IgnoreManager` et `FilterManager` restent la couche "Shield + Scalpel".

### Reutilisation directe POC

- Le pattern `LlmAdapter` est transferable vers AICC pour:
  - routeur low-cost,
  - modele principal,
  - fallback cloud/local.
- La logique orchestrateur sert a piloter la boucle d'investigation.
- Le pipeline RAG mock peut etre remplace progressivement par embeddings reels.


## 6) Recommandations techniques concretes

## 6.1 Choix d'architecture

- **Ne pas** demarrer par une infra lourde (cluster vector DB).
- Commencer par un index local incrementel (`.aicc_cache/`) avec invalidation par hash fichier.
- Ajouter Tree-sitter en priorite pour sortir du Python-only.

## 6.2 RAG code-friendly

- Utiliser le RAG pour trouver des **documents parents**, pas pour envoyer des chunks bruts au LLM final.
- Conserver metadonnees chunk -> fichier -> symboles pour recomposition contextuelle.

## 6.3 Boucle "fichiers manquants"

- Preferer un protocole structure (JSON/tool-calling) au lieu d'une simple consigne textuelle.
- Exemple de contrat de sortie:
  - `action: "answer"` avec reponse finale,
  - `action: "need_files"` avec liste de chemins.

## 6.4 Politique de budget tokens

- Definir un budget dur (ex: 40k-80k tokens selon modele).
- Prioriser:
  1) fichier principal complet,
  2) fichiers coeurs complets,
  3) dependances en headers-only,
  4) couper le reste.


## 7) Plan d'implementation propose (avec l'existant)

## Etape A - MVP fiable (sans routeur LLM)

Objectif: premiere valeur utile avec faible risque.

1. Ajouter un mode focus hybride lexical + semantique (local).
2. Retourner liste de fichiers classes par score.
3. Integrer expansion dependances 1-hop (Tree-sitter si dispo, fallback regex import).
4. Generer contexte final:
   - top N full content,
   - dependances en headers-only.

Livrable:
- nouvelle commande type `--focus "requete"` (ou enrichissement de celle planifiee).

## Etape B - Universalisation syntaxique

1. Integrer Tree-sitter (comment stripping + headers-only multi-langages).
2. Ajouter resolveur d'imports progressif (Python/TS/JS en premier).

Livrable:
- repo map multi-langages stable.

## Etape C - Routeur low-cost

1. Injecter `LlmAdapter` dans AICC.
2. Demander au routeur de choisir "full vs headers" et de prioriser les candidats.
3. Conserver mode offline/no-LLM en fallback.

Livrable:
- `--focus-ai "requete"` avec cout borne.

## Etape D - Boucle agentique

1. Ajouter protocole de demande de fichiers manquants.
2. Reboucler automatiquement 1 a 2 fois max.
3. Retourner rapport final (fichiers utilises, budget, raisons d'exclusion).

Livrable:
- investigation iterative quasi autonome.


## 8) Risques majeurs et garde-fous

1. **Explosion cout/latence**
   - garde-fou: budget tokens + limite appels + caching index/embeddings.
2. **Index obsolete**
   - garde-fou: hash de fichier + refresh incrementel.
3. **Dependances mal resolues (aliases/imports dynamiques)**
   - garde-fou: resolveur tolerant + fallback lexical + demande explicite de fichiers manquants.
4. **Contexte trop gros**
   - garde-fou: downgrade automatique en headers-only.
5. **Hallucinations par manque de pieces**
   - garde-fou: protocole strict "need_files" + schema valide.


## 9) Metriques de pilotage (obligatoires)

Pour eviter les decisions "au ressenti", mesurer:

- `Recall@K` des fichiers reellement necessaires,
- precision du top-N,
- tokens envoyes/requete,
- latence p50/p95,
- cout estime/requete,
- taux de reponse "need_files" au 1er tour,
- taux de succes en 1 tour vs 2 tours.

Mettre en place un mini corpus d'evaluation (30-50 taches realistes) pour comparer chaque iteration.


## 10) Decision framework (quand utiliser quoi)

- Petit repo / tache precise:
  - lexical + git + map peut suffire.
- Repo moyen:
  - ajouter reranking semantique.
- Gros monorepo:
  - pre-filtrage fort + routeur low-cost + budget agressif.
- Contrainte privacy/offline:
  - embeddings locaux + routeur local (ou mode no-LLM).


## 11) Proposition de backlog immediat

Backlog recommande court terme:

1. Ajouter couche de ranking multi-signaux (lexical + semantique + git).
2. Sortir un rapport explicatif des choix de fichiers (transparence).
3. Integrer Tree-sitter (au moins JS/TS/Python) pour map universelle.
4. Ajouter mode "assembly policy" (full/header/skip par seuil score).
5. Ajouter protocole `need_files` structure.


## 12) Open questions a trancher

1. Priorite UX:
   - mode 100% local d'abord, ou routeur low-cost d'abord?
2. Formats:
   - XML unique garde comme format principal, ou sortie duale (XML + JSON meta)?
3. Cible perf:
   - latence max acceptable pour une commande `--focus`?
4. Gouvernance cout:
   - budget API par execution / par jour?
5. Experience dev:
   - interaction one-shot (copier-coller), ou mode agent continu?


## 13) Resume executif

La fusion des deux idees est pertinente et moderne.
Le meilleur chemin n'est pas "RAG pur", mais une architecture hybride orientee code:

- map structurelle du repo,
- retrieval multi-signaux,
- expansion de dependances,
- assemblage budgete,
- boucle de contexte manquant.

AICC possede deja la fondation ideale (filtrage, assemblage, formats, robustesse).
Le POC apporte la couche orchestration/adapters.
L'etape critique pour debloquer la suite est Tree-sitter + ranking evalue par metriques.
