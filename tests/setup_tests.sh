#!/usr/bin/env bash

# ================================================================= #
# Script de Génération des Projets de Test pour AI Context Craft    #
#                                                                   #
# Utilisation :                                                     #
#   1. ./setup_tests.sh              : Crée/réinitialise les projets de test.
#   2. ./setup_tests.sh --golden-files : Crée les projets ET génère les
#                                      fichiers "expected_output.txt".
# ================================================================= #

# Arrête le script immédiatement si une commande échoue
set -e

# --- Configuration et Couleurs ---
# Se positionne dans le répertoire du script pour que les chemins relatifs fonctionnent
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
TEST_PROJECTS_ROOT="$SCRIPT_DIR/test_projects"
AICC_SCRIPT="$PROJECT_ROOT/main.py"

# Couleurs pour un affichage plus clair
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m' # No Color

# --- Fonctions de création des projets ---

# Scénario 1 : Un projet simple pour tester la concaténation de base
create_basic_project() {
    local project_dir="$TEST_PROJECTS_ROOT/basic_project"
    echo -e "${COLOR_BLUE}--> Création du projet de test : 'basic_project'${COLOR_NC}"
    
    # Nettoyer l'ancien projet s'il existe
    rm -rf "$project_dir"
    mkdir -p "$project_dir/app"

    # Créer les fichiers avec leur contenu via "here documents"
    cat << 'EOF' > "$project_dir/config.yaml"
# Configuration simple pour le test
include_patterns:
  - '**/*'
common_filters:
  - ".git/"
  - "build/"
tree_only_filters: []
EOF

    cat << 'EOF' > "$project_dir/.gitignore"
# Fichier à ignorer
ignored_file.txt
__pycache__/
EOF

    cat << 'EOF' > "$project_dir/app/main.py"
# main.py
import utils

def main():
    """Ceci est la fonction principale."""
    print("Hello, World!")
    utils.helper()
EOF

    cat << 'EOF' > "$project_dir/utils.py"
# utils.py
def helper():
    # Une fonction utilitaire
    print("Helper function.")
EOF
    echo "    Projet 'basic_project' créé."
}

# Scénario 2 : Un projet pour tester la suppression des commentaires (--strip-comments)
create_strip_comments_project() {
    local project_dir="$TEST_PROJECTS_ROOT/strip_comments_project"
    echo -e "${COLOR_BLUE}--> Création du projet de test : 'strip_comments_project'${COLOR_NC}"

    rm -rf "$project_dir"
    mkdir -p "$project_dir"

    # Fichier Python riche en commentaires et docstrings
    cat << 'EOF' > "$project_dir/code_with_comments.py"
# Ce script est un exemple pour le test.
# Il contient divers types de commentaires.

class MyClass:
    """
    Ceci est une docstring de classe.
    Elle devrait être supprimée.
    """
    def __init__(self, name):
        self.name = name # Commentaire en ligne

    def greet(self):
        """Docstring de méthode."""
        # Affiche un message
        print(f"Hello, {self.name}")

# Fonction de premier niveau
def top_level_function():
    """Une autre docstring à supprimer."""
    return 1 + 1 # Calcul simple
EOF
    echo "    Projet 'strip_comments_project' créé."
}

# --- Fonction pour générer les fichiers "Golden" (attendus) ---

generate_golden_files() {
    echo -e "\n${COLOR_YELLOW}--- Génération des fichiers 'Golden' (expected_output.txt) ---${COLOR_NC}"

    # 1. Pour 'basic_project'
    echo "  -> Génération pour 'basic_project'..."
    local basic_project_dir="$TEST_PROJECTS_ROOT/basic_project"
    local temp_output_basic="/tmp/aicc_basic_output.txt"
    python3 "$AICC_SCRIPT" \
        --project "$basic_project_dir" \
        --output "$temp_output_basic" \
        --no-timestamp \
        --config "$basic_project_dir/config.yaml"

    # Supprime l'en-tête dynamique pour créer un fichier de référence stable
    # Le chemin dans l'arbre sera différent sur chaque machine, donc on le remplace.
    # On saute les 4 premières lignes et on ajoute un en-tête simple et stable.
    {
        echo "Ce fichier est une concaténation de plusieurs fichiers sources d'un projet."
        echo ""
        tail -n +5 "$temp_output_basic" | sed "1s|Arbre du projet :.*|Arbre du projet : [CHEMIN_NORMALISÉ]|"
    } > "$basic_project_dir/expected_output.txt"
    rm "$temp_output_basic"
    echo -e "     ${COLOR_GREEN}Fichier 'expected_output.txt' généré.${COLOR_NC}"


    # 2. Pour 'strip_comments_project'
    echo "  -> Génération pour 'strip_comments_project' (avec --strip-comments)..."
    local strip_project_dir="$TEST_PROJECTS_ROOT/strip_comments_project"
    local temp_output_strip="/tmp/aicc_strip_output.txt"
    python3 "$AICC_SCRIPT" \
        --project "$strip_project_dir" \
        --output "$temp_output_strip" \
        --no-timestamp \
        --strip-comments
    
    {
        echo "Ce fichier est une concaténation de plusieurs fichiers sources d'un projet."
        echo ""
        tail -n +5 "$temp_output_strip" | sed "1s|Arbre du projet :.*|Arbre du projet : [CHEMIN_NORMALISÉ]|"
    } > "$strip_project_dir/expected_output.txt"
    rm "$temp_output_strip"
    echo -e "     ${COLOR_GREEN}Fichier 'expected_output.txt' généré.${COLOR_NC}"

    echo -e "${COLOR_YELLOW}--- Génération terminée ---${COLOR_NC}"
}


# --- Point d'entrée du script ---
main() {
    # Créer le répertoire principal des projets de test s'il n'existe pas
    mkdir -p "$TEST_PROJECTS_ROOT"

    echo -e "${COLOR_GREEN}Initialisation de l'environnement de test...${COLOR_NC}"
    
    # Appeler les fonctions pour créer chaque projet
    create_basic_project
    create_strip_comments_project
    # Ajoutez ici les appels pour vos futurs projets de test
    # create_headers_only_project

    # Vérifier si l'argument --golden-files est passé
    if [[ "$1" == "--golden-files" ]]; then
        generate_golden_files
    else
        echo -e "\n${COLOR_YELLOW}Pour générer/mettre à jour les fichiers 'expected_output.txt', lancez : ./setup_tests.sh --golden-files${COLOR_NC}"
    fi

    echo -e "\n${COLOR_GREEN}✅ Environnement de test prêt !${COLOR_NC}"
}

# Exécuter la fonction principale
main "$@"