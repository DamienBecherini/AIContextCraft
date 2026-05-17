# tests/test_aicc.py

import os
import json
import subprocess
import sys
from pathlib import Path

# Définir les chemins de base pour une meilleure portabilité
# __file__ est le chemin de ce fichier de test
TESTS_DIR = Path(__file__).parent
# On remonte d'un niveau pour avoir la racine du projet
PROJECT_ROOT = TESTS_DIR.parent
# Chemin vers le script principal
AICC_SCRIPT = PROJECT_ROOT / 'main.py'

def run_aicc(args, cwd=PROJECT_ROOT):
    """Exécute le script main.py avec les arguments fournis via subprocess."""
    command = [sys.executable, str(AICC_SCRIPT)] + args
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    env.setdefault("TERM", "dumb")
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=cwd,
        env=env,
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
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'text',
        '--no-clipboard',
    ]
    
    # 3. Exécuter le script
    result = run_aicc(args)
    
    # 4. Vérifier les résultats
    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert output_file.exists(), "Le fichier de sortie n'a pas été créé."
    
    # 5. Comparer le contenu du fichier généré avec le fichier attendu
    compare_files_robust(output_file, expected_file)

def test_tree_stats_project_indicators(tmp_path):
    """Valide les symboles ●/○, les tailles et le résumé par extension."""
    test_project_path = TESTS_DIR / 'test_projects' / 'tree_stats_project'
    output_file = tmp_path / 'tree_stats_output.txt'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'text',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')

    assert '● main.py' in content
    assert '○ README.md' in content
    assert 'README.md —' not in content
    assert 'Extensions (fichiers concaténés)' in content
    assert 'mixed/' in content and '(Total réel :' in content
    assert '--- FICHIER: app/main.py' in content
    assert '--- FICHIER: mixed/included.txt' in content
    assert '--- FICHIER: README.md' not in content
    assert '--- FICHIER: mixed/skipped.txt' not in content


def test_special_chars_pattern_with_slash(tmp_path):
    """Valide l'inclusion avec des caractères Unicode et des slashs '/'."""
    test_project_path = TESTS_DIR / 'test_projects' / 'special_chars_project'
    output_file = tmp_path / 'special_chars_slash_output.txt'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config_slash.yaml'),
        '--format', 'text',
        '--no-clipboard',
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
        '--config', str(test_project_path / 'config_backslash.yaml'),
        '--format', 'text',
        '--no-clipboard',
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
        '--config', str(invalid_config),
        '--no-clipboard',
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
        '--git-diff', sha_a, sha_b,
        '--no-clipboard',
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


def test_nested_gitignore_and_security_patterns(tmp_path):
    """Valide le Bouclier : .gitignore hiérarchiques et règles de sécurité."""
    test_project_path = TESTS_DIR / 'test_projects' / 'nested_ignore_project'
    output_file = tmp_path / 'nested_ignore_output.txt'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'text',
        '--no-clipboard',
    ]

    result = run_aicc(args)
    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '--- FICHIER: frontend/src/ok.js' in content
    assert '--- FICHIER: logs/' not in content
    assert '--- FICHIER: logs/secret.log' not in content
    assert '--- FICHIER: frontend/node_modules/' not in content
    assert '--- FICHIER: .env.local' not in content
    assert 'FAKE_SECRET' not in content

    output_no_ignore = tmp_path / 'nested_ignore_no_ignore_output.txt'
    args_no_ignore = [
        '--project', str(test_project_path),
        '--output', str(output_no_ignore),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'text',
        '--no-ignore',
        '--no-clipboard',
    ]
    result_no_ignore = run_aicc(args_no_ignore)
    assert result_no_ignore.returncode == 0, (
        f"Le script a échoué avec le code {result_no_ignore.returncode}.\n"
        f"Stderr: {result_no_ignore.stderr}"
    )
    content_no_ignore = output_no_ignore.read_text(encoding='utf-8')
    assert '--- FICHIER: logs/secret.log' in content_no_ignore
    assert '--- FICHIER: frontend/node_modules/pkg/index.js' in content_no_ignore
    assert '--- FICHIER: .env.local' not in content_no_ignore
    assert 'FAKE_SECRET' not in content_no_ignore


def test_skip_ignore_files_disables_only_selected_types(tmp_path):
    project_path = tmp_path / 'skip_ignore_types_project'
    project_path.mkdir()
    (project_path / '.gitignore').write_text('*.log\n', encoding='utf-8')
    (project_path / '.dockerignore').write_text('cache/\n', encoding='utf-8')
    (project_path / 'events.log').write_text('entry\n', encoding='utf-8')
    (project_path / 'cache').mkdir()
    (project_path / 'cache' / 'tmp.txt').write_text('tmp\n', encoding='utf-8')
    (project_path / 'keep.py').write_text("print('ok')\n", encoding='utf-8')

    output_file = tmp_path / 'skip_ignore_types_output.xml'
    result = run_aicc(
        [
            '--project', str(project_path),
            '--output', str(output_file),
            '--no-timestamp',
            '--format', 'xml',
            '--skip-ignore-files', 'gitignore',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '<file path="events.log">' in content
    assert '<file path="cache/tmp.txt">' not in content


def test_ignore_files_keeps_only_listed_types(tmp_path):
    project_path = tmp_path / 'keep_only_ignore_types_project'
    project_path.mkdir()
    (project_path / '.gitignore').write_text('*.log\n', encoding='utf-8')
    (project_path / '.dockerignore').write_text('cache/\n', encoding='utf-8')
    (project_path / 'events.log').write_text('entry\n', encoding='utf-8')
    (project_path / 'cache').mkdir()
    (project_path / 'cache' / 'tmp.txt').write_text('tmp\n', encoding='utf-8')
    (project_path / 'keep.py').write_text("print('ok')\n", encoding='utf-8')

    output_file = tmp_path / 'keep_only_ignore_types_output.xml'
    result = run_aicc(
        [
            '--project', str(project_path),
            '--output', str(output_file),
            '--no-timestamp',
            '--format', 'xml',
            '--ignore-files', 'dockerignore',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '<file path="events.log">' in content
    assert '<file path="cache/tmp.txt">' not in content


def test_output_json_stdout_without_file_creation(tmp_path):
    project_path = tmp_path / 'json_stdout_project'
    project_path.mkdir()
    (project_path / 'keep.py').write_text("print('ok')\n", encoding='utf-8')

    output_file = tmp_path / 'json_stdout_output.xml'
    result = run_aicc(
        [
            '--project', str(project_path),
            '--output', str(output_file),
            '--no-timestamp',
            '--format', 'xml',
            '--output-format', 'json',
            '--output-destination', 'stdout',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert not output_file.exists(), "Le fichier de sortie ne doit pas être créé en mode stdout."
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload['status'] == 'success'
    assert payload['output_destination'] == 'stdout'
    assert payload['output_file'] is None


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
        '--git-diff', sha_a, 'not-a-valid-ref',
        '--no-clipboard',
    ]

    result = run_aicc(args, cwd=repo_path)

    assert result.returncode != 0
    assert "not-a-valid-ref" in result.stderr


def test_xml_format_output_structure(tmp_path):
    """Valide la structure de sortie XML en mode concaténation standard."""
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'output.xml'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'xml',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '<repository>' in content
    assert '<directory_structure>' in content
    assert '<files>' in content
    assert '<file path="app/main.py">' in content
    assert '</repository>' in content


def test_markdown_format_output_structure(tmp_path):
    """Valide la structure de sortie Markdown en mode concaténation standard."""
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'output.md'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'markdown',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '# Project Context' in content
    assert '## Directory Structure' in content
    assert '## Files' in content
    assert '### File: `app/main.py`' in content
    assert '```python' in content


def test_tree_only_xml_omits_files_section(tmp_path):
    """Valide que --tree-only en XML ne génère pas la section <files>."""
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'tree_only.xml'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'xml',
        '--tree-only',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '<repository>' in content
    assert '<directory_structure>' in content
    assert '<files>' not in content


def test_tree_only_markdown_omits_files_section(tmp_path):
    """Valide que --tree-only en Markdown ne génère pas la section fichiers."""
    test_project_path = TESTS_DIR / 'test_projects' / 'basic_project'
    output_file = tmp_path / 'tree_only.md'

    args = [
        '--project', str(test_project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--config', str(test_project_path / 'config.yaml'),
        '--format', 'markdown',
        '--tree-only',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '# Project Context' in content
    assert '## Directory Structure' in content
    assert '## Files' not in content
    assert '### File:' not in content


def test_xml_format_escapes_file_content(tmp_path):
    """Valide l'échappement XML du contenu des fichiers concaténés."""
    project_path = tmp_path / 'xml_escape_project'
    project_path.mkdir()
    target_file = project_path / 'snippet.txt'
    target_file.write_text('<tag>&value</tag>\n', encoding='utf-8')

    output_file = tmp_path / 'escaped_output.xml'
    args = [
        '--project', str(project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--format', 'xml',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '&lt;tag&gt;&amp;value&lt;/tag&gt;' in content
    assert '<tag>&value</tag>' not in content


def test_clipboard_limit_skips_copy_when_output_is_too_large(tmp_path):
    """Valide que la copie est annulée si la sortie dépasse --clipboard-limit."""
    project_path = tmp_path / 'clipboard_limit_project'
    project_path.mkdir()
    (project_path / 'big.txt').write_text("A" * 3000, encoding='utf-8')

    output_file = tmp_path / 'clipboard_limit_output.xml'
    args = [
        '--project', str(project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--format', 'xml',
        '--clipboard-limit', '0.001',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert "dépasse la limite du presse-papiers" in result.stderr
    assert "Contenu copié dans le presse-papiers." not in result.stdout
    assert "Contenu envoyé au presse-papiers via SSH (OSC 52)." not in result.stdout


def test_no_clipboard_disables_automatic_copy(tmp_path):
    """Valide que --no-clipboard empêche toute tentative de copie."""
    project_path = tmp_path / 'no_clipboard_project'
    project_path.mkdir()
    (project_path / 'small.txt').write_text("hello\n", encoding='utf-8')

    output_file = tmp_path / 'no_clipboard_output.xml'
    args = [
        '--project', str(project_path),
        '--output', str(output_file),
        '--no-timestamp',
        '--format', 'xml',
        '--no-clipboard',
    ]

    result = run_aicc(args)

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert "Contenu copié dans le presse-papiers." not in result.stdout
    assert "Contenu envoyé au presse-papiers via SSH (OSC 52)." not in result.stdout


def test_default_output_path_uses_build_and_format_extension(tmp_path):
    """Valide le fallback output vers build/aicc_context.<ext> si non fourni."""
    project_path = tmp_path / 'default_output_project'
    project_path.mkdir()
    (project_path / 'snippet.py').write_text("print('ok')\n", encoding='utf-8')

    result = run_aicc(
        [
            '--project', str(project_path),
            '--no-timestamp',
            '--format', 'xml',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    generated_file = tmp_path / 'build' / 'aicc_context.xml'
    assert generated_file.exists(), "Le fichier build/aicc_context.xml n'a pas été généré."


def test_zero_config_auto_detects_aicc_yaml(tmp_path):
    """Valide la détection automatique de .aicc.yaml sans --config."""
    project_path = tmp_path / 'auto_config_project'
    project_path.mkdir()
    (project_path / 'keep.py').write_text("print('keep')\n", encoding='utf-8')
    (project_path / 'skip.txt').write_text("skip\n", encoding='utf-8')
    (project_path / '.aicc.yaml').write_text(
        "include_patterns:\n"
        "  - '*.py'\n"
        "common_filters: []\n"
        "project_only_filters: []\n"
        "tree_only_filters: []\n",
        encoding='utf-8',
    )

    output_file = tmp_path / 'auto_config_output.xml'
    result = run_aicc(
        [
            '--project', str(project_path),
            '--output', str(output_file),
            '--no-timestamp',
            '--format', 'xml',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    content = output_file.read_text(encoding='utf-8')
    assert '<file path="keep.py">' in content
    assert '<file path="skip.txt">' not in content


def test_zero_config_does_not_create_config_file(tmp_path):
    """Valide qu'aucun config.yaml n'est créé si aucun fichier n'est trouvé."""
    project_path = tmp_path / 'no_config_project'
    project_path.mkdir()
    (project_path / 'main.py').write_text("print('hi')\n", encoding='utf-8')

    result = run_aicc(
        [
            '--project', str(project_path),
            '--no-timestamp',
            '--format', 'xml',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert not (project_path / 'config.yaml').exists()


def test_console_reports_config_and_ignore_usage(tmp_path):
    """Valide l'affichage console du mode config et des ignore files détectés/utilisés."""
    project_path = tmp_path / 'console_report_project'
    project_path.mkdir()
    (project_path / '.aicc.yaml').write_text(
        "include_patterns:\n"
        "  - '**/*'\n"
        "common_filters: []\n"
        "project_only_filters: []\n"
        "tree_only_filters: []\n",
        encoding='utf-8',
    )
    (project_path / '.gitignore').write_text("*.log\n", encoding='utf-8')
    (project_path / '.dockerignore').write_text("cache/\n", encoding='utf-8')
    (project_path / '.npmignore').write_text("", encoding='utf-8')
    (project_path / 'cache').mkdir()
    (project_path / 'cache' / 'tmp.txt').write_text("tmp", encoding='utf-8')
    (project_path / 'events.log').write_text("entry", encoding='utf-8')
    (project_path / 'keep.py').write_text("print('ok')\n", encoding='utf-8')

    output_file = tmp_path / 'console_report_output.xml'
    result = run_aicc(
        [
            '--project', str(project_path),
            '--output', str(output_file),
            '--no-timestamp',
            '--format', 'xml',
            '--no-clipboard',
        ],
        cwd=tmp_path,
    )

    assert result.returncode == 0, f"Le script a échoué avec le code {result.returncode}.\nStderr: {result.stderr}"
    assert "Configuration utilisée :" in result.stderr
    assert "auto-détectée" in result.stderr
    assert "Fichiers d'ignore détectés" in result.stderr
    assert ".gitignore (trouve+utilise)" in result.stderr
    assert ".dockerignore (trouve+utilise)" in result.stderr
    assert ".npmignore (trouve+utilise(vide))" in result.stderr
