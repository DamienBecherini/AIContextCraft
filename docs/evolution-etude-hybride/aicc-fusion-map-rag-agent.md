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

### Reutilisation directe POC Atlas

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

### 7.1 Plan d'execution court terme (10 jours)

Jours 1-2:
- creer `tests/eval_harness/` avec cas pieges versionnes;
- definir oracles (must-have / must-not-have files) par prompt.

Jours 3-4:
- implementer baseline lexical + budget tokens;
- generer rapport de selection par fichier (score + raison).

Jours 5-6:
- ajouter score semantique local (embeddings);
- lancer ablation et comparer aux baselines.

Jours 7-8:
- ajouter expansion dependances 1-hop;
- appliquer policy `full/header/skip` sous budget.

Jours 9-10:
- stabiliser seuils/ponderations via eval;
- figer criteres d'acceptation V1 et publier bilan metriques.


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

### 9.1 Protocole d'ablation (obligatoire)

Objectif: mesurer l'apport reel de chaque composant, et eviter les decisions au ressenti.

Runs minimaux a comparer sur le meme corpus:

1. Lexical seul (baseline)
2. Semantique seul (embeddings)
3. Hybride lexical + semantique
4. Hybride + expansion dependances
5. Hybride + dependances + policy budget (full/header/skip)

Pour chaque run, mesurer:
- Recall@K
- precision top-N
- latence p50/p95
- tokens envoyes
- cout estime (ou cout equivalent en tokens)

Regle de validation:
- une etape n'est retenue que si elle ameliore au moins 1 metrique prioritaire
  (Recall@K ou precision top-N) sans degradation majeure de latence.


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

Backlog recommande court terme (ordre d'execution):

1. Construire l'eval harness (projets pieges + oracles + pytest).
2. Ajouter couche de ranking multi-signaux (lexical + semantique + git).
3. Sortir un rapport explicatif des choix de fichiers (transparence).
4. Integrer Tree-sitter (au moins JS/TS/Python) pour map universelle.
5. Ajouter mode "assembly policy" (full/header/skip par seuil score).
6. Ajouter protocole `need_files` structure.


## 12) Decisions tranchees (version courante)

Ces decisions sont des choix d'execution pour accelerer la phase MVP.
Elles pourront etre revisees apres les premiers cycles d'evaluation.

1. **Priorite UX**
   - Decision: mode 100% local d'abord (sans routeur LLM).
   - Raison: reduire la complexite, maitriser la perf, valider le ranking.

2. **Formats**
   - Decision: XML pour le contexte final LLM.
   - Decision: JSON meta pour l'orchestrateur/debug (scores, budget, raisons d'inclusion).
   - Raison: separer lisibilite LLM et pilotage technique.

3. **Cible de performance**
   - Decision: `--focus` local < 3 secondes (cible), p95 < 5 secondes.
   - Decision: boucle `need_files` < 15 secondes (cible) avec 1 rebouclage max en V1 agentique.
   - Raison: conserver une UX fluide et exploitable au quotidien.

4. **Gouvernance budget**
   - Decision: profils en tokens:
     - `fast` = 10k
     - `deep` = 50k
     - `max` = 100k
   - Raison: modele de cout universel (local ou API commerciale).

5. **Experience developpeur**
   - Decision: one-shot CLI en V1/V2.
   - Decision: mode agent interactif/TUI plus tard (V4+).
   - Raison: limiter la dette de complexite conversationnelle.

### 12.1 Infrastructure locale (guideline)

Objectif: iterer massivement sans cout API et sans fuite de code.

1. **Embeddings**
   - mode local CPU prioritaire (pas besoin GPU au demarrage);
   - preferer un modele oriente code des que possible.

2. **Routeur LLM local**
   - 8 Go RAM peut fonctionner pour tests de base, mais confort limite;
   - 12-16 Go VRAM recommande pour une iteration fluide.

3. **Securite reseau**
   - si serveur local sur LAN: auth + proxy + pas d'exposition brute;
   - le moteur de securite AICC reste prioritaire (ex: refus `.env`, cles, secrets).

4. **Fallback**
   - mode no-LLM obligatoire pour garantir robustesse hors infra GPU.

### 12.2 Criteres d'acceptation par phase

**V1 (ranking + budget, sans routeur LLM)**
- Recall@K et precision top-N > baseline lexical seule.
- budget tokens respecte dans 100% des runs eval.
- logs explicatifs disponibles (raison d'inclusion/exclusion par fichier).

**V2 (Tree-sitter multi-langages)**
- `headers-only` stable sur Python + JS/TS (minimum).
- expansion dependances 1-hop fonctionnelle sur cas eval cibles.

**V3 (boucle `need_files`)**
- schema JSON strict valide.
- 1 rebouclage max en mode standard.
- aucune regression des regles de securite (secrets toujours bloques).


## 13) Resume executif

La fusion des deux idees est pertinente et moderne.
Le meilleur chemin n'est pas "RAG pur", mais une architecture hybride orientee code:

- map structurelle du repo,
- retrieval multi-signaux,
- expansion de dependances,
- assemblage budgete,
- boucle de contexte manquant.

AICC possede deja la fondation ideale (filtrage, assemblage, formats, robustesse).
Le POC Atlas apporte la couche orchestration/adapters.

Priorite immediate: construire l'eval harness et valider le ranking hybride par ablation
avant d'introduire le routeur LLM. Les fondations (lexical, semantique, budget, policy
full/header/skip) peuvent etre developpees et testees sans GPU ni API payante.

L'etape critique pour debloquer la suite est: eval harness -> ranking mesure -> Tree-sitter.
