#!/usr/bin/env bash

# ================================================================= #
# AI Context Craft test project generator script                    #
#                                                                   #
# Usage:                                                            #
#   1. ./setup_tests.sh              : Create/reset test projects.    #
#   2. ./setup_tests.sh --golden-files : Create projects AND generate #
#                                      "expected_output.txt" files.   #
# ================================================================= #

# Exit immediately if a command fails
set -e

# --- Configuration and colors ---
# Run from the script directory so relative paths work
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
TEST_PROJECTS_ROOT="$SCRIPT_DIR/test_projects"
AICC_SCRIPT="$PROJECT_ROOT/main.py"

# Colors for clearer output
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m' # No Color

# --- Test project creation functions ---

# Scenario 1: simple project for basic concatenation
create_basic_project() {
    local project_dir="$TEST_PROJECTS_ROOT/basic_project"
    echo -e "${COLOR_BLUE}--> Creating test project: 'basic_project'${COLOR_NC}"
    
    # Remove previous project if it exists
    rm -rf "$project_dir"
    mkdir -p "$project_dir/app"

    # Create files via here documents
    cat << 'EOF' > "$project_dir/config.yaml"
# Simple configuration for this test
include_patterns:
  - '**/*'
common_filters:
  - ".git/"
  - "build/"
  - "expected_output.txt"
  - "*.log"
tree_only_filters: []
EOF

    cat << 'EOF' > "$project_dir/.gitignore"
# File to ignore
ignored_file.txt
__pycache__/
EOF

    cat << 'EOF' > "$project_dir/app/main.py"
# main.py
import utils

def main():
    """This is the main function."""
    print("Hello, World!")
    utils.helper()
EOF

    cat << 'EOF' > "$project_dir/utils.py"
# utils.py
def helper():
    # A utility function
    print("Helper function.")
EOF
    echo "    Test project 'basic_project' created."
}

# Scenario 2: project for --strip-comments
create_strip_comments_project() {
    local project_dir="$TEST_PROJECTS_ROOT/strip_comments_project"
    echo -e "${COLOR_BLUE}--> Creating test project: 'strip_comments_project'${COLOR_NC}"

    rm -rf "$project_dir"
    mkdir -p "$project_dir"

    # Python file rich in comments and docstrings
    cat << 'EOF' > "$project_dir/code_with_comments.py"
# This script is an example for the test.
# It contains various comment styles.

class MyClass:
    """
    This is a class docstring.
    It should be removed.
    """
    def __init__(self, name):
        self.name = name # Inline comment

    def greet(self):
        """Method docstring."""
        # Print a message
        print(f"Hello, {self.name}")

# Top-level function
def top_level_function():
    """Another docstring to remove."""
    return 1 + 1 # Simple calculation
EOF
    echo "    Test project 'strip_comments_project' created."
}

# Scenario 3: hierarchical .gitignore and security rules (Phase 1)
create_nested_ignore_project() {
    local project_dir="$TEST_PROJECTS_ROOT/nested_ignore_project"
    echo -e "${COLOR_BLUE}--> Creating test project: 'nested_ignore_project'${COLOR_NC}"

    rm -rf "$project_dir"
    mkdir -p "$project_dir/logs" "$project_dir/frontend/node_modules/pkg" "$project_dir/frontend/src"

    cat << 'EOF' > "$project_dir/config.yaml"
include_patterns:
  - '**/*'
common_filters:
  - ".git/"
project_only_filters: []
tree_only_filters: []
EOF

    echo 'logs/' > "$project_dir/.gitignore"
    echo 'node_modules/' > "$project_dir/frontend/.gitignore"
    echo 'SECRET=should-not-appear' > "$project_dir/logs/secret.log"
    echo 'module.exports = {};' > "$project_dir/frontend/node_modules/pkg/index.js"
    echo 'export const ok = true;' > "$project_dir/frontend/src/ok.js"
    echo 'FAKE_SECRET=do-not-leak' > "$project_dir/.env.local"

    echo "    Test project 'nested_ignore_project' created."
}

# --- Golden file generation (expected outputs) ---

generate_golden_files() {
    echo -e "\n${COLOR_YELLOW}--- Generating 'Golden' files (expected_output.txt) ---${COLOR_NC}"

    # 1. For 'basic_project'
    echo "  -> Generating for 'basic_project'..."
    local basic_project_dir="$TEST_PROJECTS_ROOT/basic_project"
    local temp_output_basic="/tmp/aicc_basic_output.txt"
    PYTHON="${AICC_PYTHON:-python3}"
    "$PYTHON" "$AICC_SCRIPT" \
        --project "$basic_project_dir" \
        --output "$temp_output_basic" \
        --no-timestamp \
        --config "$basic_project_dir/config.yaml"

    # Strip dynamic header for a stable reference file
    # Tree path differs per machine, so normalize it.
    # Skip the first 4 lines and add a simple stable header.
    {
        echo "This file is a concatenation of several source files from a project."
        echo ""
        tail -n +5 "$temp_output_basic" | sed "1s|Project tree:.*|Project tree: [NORMALIZED_PATH]|"
    } > "$basic_project_dir/expected_output.txt"
    rm "$temp_output_basic"
    echo -e "     ${COLOR_GREEN}File 'expected_output.txt' generated.${COLOR_NC}"


    # 2. For 'strip_comments_project'
    echo "  -> Generating for 'strip_comments_project' (with --strip-comments)..."
    local strip_project_dir="$TEST_PROJECTS_ROOT/strip_comments_project"
    local temp_output_strip="/tmp/aicc_strip_output.txt"
    PYTHON="${AICC_PYTHON:-python3}"
    "$PYTHON" "$AICC_SCRIPT" \
        --project "$strip_project_dir" \
        --output "$temp_output_strip" \
        --no-timestamp \
        --strip-comments
    
    {
        echo "This file is a concatenation of several source files from a project."
        echo ""
        tail -n +5 "$temp_output_strip" | sed "1s|Project tree:.*|Project tree: [NORMALIZED_PATH]|"
    } > "$strip_project_dir/expected_output.txt"
    rm "$temp_output_strip"
    echo -e "     ${COLOR_GREEN}File 'expected_output.txt' generated.${COLOR_NC}"

    echo -e "${COLOR_YELLOW}--- Generation complete ---${COLOR_NC}"
}


# --- Script entry point ---
main() {
    # Create the main test projects directory if missing
    mkdir -p "$TEST_PROJECTS_ROOT"

    echo -e "${COLOR_GREEN}Initializing test environment...${COLOR_NC}"
    
    # Create each test project
    create_basic_project
    create_strip_comments_project
    create_nested_ignore_project
    # Add calls here for future test projects
    # create_headers_only_project

    # Check for --golden-files argument
    if [[ "$1" == "--golden-files" ]]; then
        generate_golden_files
    else
        echo -e "\n${COLOR_YELLOW}To generate/update 'expected_output.txt' files, run: ./setup_tests.sh --golden-files${COLOR_NC}"
    fi

    echo -e "\n${COLOR_GREEN}✅ Test environment ready!${COLOR_NC}"
}

# Run main
main "$@"
