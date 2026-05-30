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

# Scenario 4: Unicode folder names and Windows-style pattern separators
create_special_chars_project() {
    local project_dir="$TEST_PROJECTS_ROOT/special_chars_project"
    echo -e "${COLOR_BLUE}--> Creating test project: 'special_chars_project'${COLOR_NC}"

    rm -rf "$project_dir"
    mkdir -p "$project_dir/other" "$project_dir/🚀 Projects/🏰 Proxmox Homelab"

    cat << 'EOF' > "$project_dir/config_slash.yaml"
include_patterns:
  - "🚀 Projects/🏰 Proxmox Homelab/**"
common_filters:
  - ".git/"
  - "build/"
  - "*.log"
tree_only_filters: []
EOF

    cat << 'EOF' > "$project_dir/config_backslash.yaml"
include_patterns:
  - '🚀 Projects\🏰 Proxmox Homelab\**'
common_filters:
  - ".git/"
  - "build/"
  - "*.log"
tree_only_filters: []
EOF

    echo 'This file should not be included by focused include patterns.' > "$project_dir/other/ignored.txt"
    echo 'sample context for special-char path tests' > "$project_dir/🚀 Projects/🏰 Proxmox Homelab/context.txt"

    echo "    Test project 'special_chars_project' created."
}

# --- Golden file generation (expected outputs) ---

resolve_aicc_python() {
    if [[ -n "${AICC_PYTHON:-}" ]]; then
        echo "$AICC_PYTHON"
        return
    fi
    if [[ -x "$PROJECT_ROOT/.aicc_venv/Scripts/python.exe" ]]; then
        echo "$PROJECT_ROOT/.aicc_venv/Scripts/python.exe"
        return
    fi
    if [[ -x "$PROJECT_ROOT/.aicc_venv/bin/python" ]]; then
        echo "$PROJECT_ROOT/.aicc_venv/bin/python"
        return
    fi
    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return
    fi
    command -v python
}

generate_golden_files() {
    echo -e "\n${COLOR_YELLOW}--- Generating 'Golden' files (expected_output.txt) ---${COLOR_NC}"
    local PYTHON
    PYTHON="$(resolve_aicc_python)"
    # Run from repo root with a relative script path so Git Bash + Windows python agree on paths.
    (cd "$PROJECT_ROOT" && "$PYTHON" tests/generate_golden_output.py setup-tests)
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
    create_special_chars_project
    # Add calls here for future test projects
    # create_headers_only_project

    # Regenerate golden files when requested or when basic_project golden is missing
    local basic_golden="$TEST_PROJECTS_ROOT/basic_project/expected_output.txt"
    if [[ "$1" == "--golden-files" ]] || [[ ! -f "$basic_golden" ]]; then
        generate_golden_files
    else
        echo -e "\n${COLOR_YELLOW}To regenerate 'expected_output.txt' files, run: ./setup_tests.sh --golden-files${COLOR_NC}"
    fi

    echo -e "\n${COLOR_GREEN}✅ Test environment ready!${COLOR_NC}"
}

# Run main
main "$@"
