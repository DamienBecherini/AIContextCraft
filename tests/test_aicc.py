# tests/test_aicc.py

import subprocess
import sys
from pathlib import Path

# Définir les chemins de base pour une meilleure portabilité
# __file__ est le chemin de ce fichier de test
TESTS_DIR = Path(__file__).parent
# On remonte d'un niveau pour avoir la racine du projet
PROJECT_ROOT = TESTS_DIR.parent
# Chemin vers le script principal
AICC_SCRIPT = PROJECT_ROOT / 'aicc.py'

def run_aicc(args, cwd=PROJECT_ROOT):
    """Exécute le script aicc.py avec les arguments fournis via subprocess."""
    command = [sys.executable, str(AICC_SCRIPT)] + args
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=cwd
    )
    return result

def find_content_start(lines):
    """Trouve l'index de la ligne où le contenu réel commence."""
    for i, line in enumerate(lines):
        if line.strip().startswith("Arbre du projet :"):
            return i
    # Si on ne trouve pas l'arbre, on retourne 0 pour comparer tout le fichier (et probablement échouer)
    return 0

def compare_files_robust(generated_path, expected_path):
    """
    Compare deux fichiers de manière robuste.
    1. Ignore tout l'en-tête en trouvant la ligne "Arbre du projet".
    2. Normalise le chemin de l'arbre pour être indépendant de la machine.
    """
    with open(generated_path, 'r', encoding='utf-8') as f_gen, \
         open(expected_path, 'r', encoding='utf-8') as f_exp:
        
        lines_gen = f_gen.read().splitlines()
        lines_exp = f_exp.read().splitlines()

        # Trouver le début du contenu dans chaque fichier
        start_gen = find_content_start(lines_gen)
        start_exp = find_content_start(lines_exp)
        
        # Tronquer les listes pour ne garder que le contenu pertinent
        content_lines_gen = lines_gen[start_gen:]
        content_lines_exp = lines_exp[start_exp:]

        # Normaliser la première ligne (le chemin de l'arbre)
        if content_lines_gen:
            content_lines_gen[0] = "Arbre du projet : [CHEMIN_NORMALISÉ]"
        if content_lines_exp:
            content_lines_exp[0] = "Arbre du projet : [CHEMIN_NORMALISÉ]"

        # Joindre les lignes pour la comparaison finale
        final_content_gen = "\n".join(content_lines_gen)
        final_content_exp = "\n".join(content_lines_exp)
        
        assert final_content_gen == final_content_exp


def test_basic_concatenation(tmp_path):
    """
    Teste la fonctionnalité de base : concaténation simple d'un projet.
    `tmp_path` est une fixture pytest qui fournit un dossier temporaire unique.
    """
    # 1. Définir les chemins pour ce test
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'output.txt'
    expected_file = test_project_path / 'expected_output.txt'
    
    # 2. Construire la commande
    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml')
    ]
    
    # 3. Exécuter le script
    result = run_aicc(args)
    
    # 4. Vérifier les résultats
    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert output_file.exists(), "Le fichier de sortie n'a pas été créé."
    
    # 5. Comparer le contenu du fichier généré avec le fichier attendu
    compare_files_robust(output_file, expected_file)

def test_special_chars_pattern_with_slash(tmp_path):
    """Valide l'inclusion avec des caractères Unicode et des slashs '/'."""
    test_project_path = TESTS_DIR / 'test_projects' / 'special_chars_project'
    output_file = tmp_path / 'special_chars_slash_output.txt'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config_slash.yaml')
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert "--- FICHIER: 🚀 Projets/🏰 Proxmox Homelab/context.txt" in content
    assert "--- FICHIER: other/ignored.txt" not in content

def test_special_chars_pattern_with_backslashes(tmp_path):
    """Valide la normalisation des backslashes '\\' en '/' dans les patterns."""
    test_project_path = TESTS_DIR / 'test_projects' / 'special_chars_project'
    output_file = tmp_path / 'special_chars_backslash_output.txt'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config_backslash.yaml')
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert "--- FICHIER: 🚀 Projets/🏰 Proxmox Homelab/context.txt" in content
    assert "--- FICHIER: other/ignored.txt" not in content

def test_invalid_yaml_backslash_error_has_guidance(tmp_path):
    """Valide le message d'aide pour une config YAML invalide avec escapes."""
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'invalid_yaml_output.txt'
    invalid_config = tmp_path / 'invalid_config.yaml'
    invalid_config.write_text(
        'include_patterns:\n  - "🚀 Projets\\🏰 Proxmox Homelab"\n',
        encoding='utf-8'
    )

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(invalid_config)
    ]

    result = run_aicc(args)

    assert result.returncode != 0
    assert "Impossible de parser le fichier de configuration" in result.stderr
    assert "Préférez '/' au lieu de '\\'" in result.stderr
    assert "quotes simples" in result.stderr


def init_git_repo_with_two_commits(repo_path):
    """Initialise un dépôt Git temporaire avec deux commits et retourne leurs SHAs."""
    subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True, text=True)
    subprocess.run(['git', 'config', 'user.name', 'AIContextCraft Tests'], cwd=repo_path, check=True, capture_output=True, text=True)
    subprocess.run(['git', 'config', 'user.email', 'tests@aicc.local'], cwd=repo_path, check=True, capture_output=True, text=True)

    tracked_file = repo_path / 'sample.py'
    tracked_file.write_text("print('v1')\n", encoding='utf-8')
    subprocess.run(['git', 'add', 'sample.py'], cwd=repo_path, check=True, capture_output=True, text=True)
    subprocess.run(['git', 'commit', '-m', 'first'], cwd=repo_path, check=True, capture_output=True, text=True)
    first_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo_path, check=True, capture_output=True, text=True).stdout.strip()

    tracked_file.write_text("print('v2')\nprint('new line')\n", encoding='utf-8')
    subprocess.run(['git', 'add', 'sample.py'], cwd=repo_path, check=True, capture_output=True, text=True)
    subprocess.run(['git', 'commit', '-m', 'second'], cwd=repo_path, check=True, capture_output=True, text=True)
    second_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo_path, check=True, capture_output=True, text=True).stdout.strip()

    return first_sha, second_sha


def test_git_diff_mode_generates_markdown_output(tmp_path):
    """Valide que --git-diff génère un fichier Markdown contenant un bloc diff."""
    repo_path = tmp_path / 'repo'
    repo_path.mkdir()
    sha_a, sha_b = init_git_repo_with_two_commits(repo_path)
    output_file = tmp_path / 'git_diff_output.txt'

    args = [
        '--project', str(repo_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--git-diff', sha_a, sha_b
    ]

    result = run_aicc(args, cwd=repo_path)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    expected_output = output_file.with_suffix('.md')
    assert expected_output.exists(), "Le fichier de sortie Markdown n'a pas été créé."
    content = expected_output.read_text(encoding='utf-8')
    assert f"# Diff Git: {sha_a} -> {sha_b}" in content
    assert "```diff" in content
    assert "-print('v1')" in content
    assert "+print('v2')" in content


def test_git_diff_mode_with_invalid_ref_fails(tmp_path):
    """Valide qu'une référence Git invalide provoque une erreur claire."""
    repo_path = tmp_path / 'repo_invalid_ref'
    repo_path.mkdir()
    sha_a, _ = init_git_repo_with_two_commits(repo_path)
    output_file = tmp_path / 'git_diff_invalid_output.txt'

    args = [
        '--project', str(repo_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--git-diff', sha_a, 'not-a-valid-ref'
    ]

    result = run_aicc(args, cwd=repo_path)

    assert result.returncode != 0
    assert "not-a-valid-ref" in result.stderr
