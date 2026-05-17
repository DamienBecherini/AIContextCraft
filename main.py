import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

import pathspec
import yaml

from craft.file_processor import get_python_headers, strip_comments_from_code
from craft.filter_manager import normalize_glob_patterns
from craft.formatter import build_output
from craft.git_manager import get_git_diff
from craft.ignore_manager import IgnoreManager
from craft.tree_generator import format_extension_summary, generate_tree
from craft.utils import get_file_stats, setup_logging


def main():
    parser = argparse.ArgumentParser(description="Agrège les fichiers d'un projet en un seul fichier texte pour une IA.")
    parser.add_argument('-c', '--config', type=str, help="Chemin vers le fichier de configuration YAML.")
    parser.add_argument('-p', '--project', type=str, help="Chemin vers le projet cible.")
    parser.add_argument('-o', '--output', type=str, help="Chemin vers le fichier de sortie.")
    parser.add_argument('--no-timestamp', action='store_true', help="Ne pas ajouter de timestamp au nom du fichier de sortie.")
    parser.add_argument('--strip-comments', action='store_true', help="Supprimer les commentaires des fichiers.")
    parser.add_argument('--headers-only', action='store_true', help="Ne conserver que les signatures de fonctions/méthodes.")
    parser.add_argument('--tree-only', action='store_true', help="Génère uniquement l'arbre du projet (tailles, extensions) sans le contenu des fichiers.")
    parser.add_argument('--dry-run', action='store_true', help="Simule l'opération sans écrire de fichier.")
    parser.add_argument('--encoding', type=str, default='utf-8', help="Encodage des fichiers (défaut: utf-8).")
    parser.add_argument('--no-ignore', action='store_true', help="Désactive les .gitignore hiérarchiques (les règles de sécurité restent actives).")
    parser.add_argument('--git-diff', nargs=2, metavar=('REF_A', 'REF_B'), help="Mode spécial: génère un rapport Markdown du diff Git global entre deux révisions.")
    parser.add_argument('--format', choices=['text', 'xml', 'markdown'], help="Format de sortie: text (défaut), xml ou markdown.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Affiche des informations détaillées sur la console.")
    args = parser.parse_args()

    DEFAULT_CONFIG = {
        'output_path': './build/project_context.txt',
        'include_patterns': ['**/*'],
        'common_filters': ['__pycache__/', '*.pyc', '.git/', '.venv/', 'venv/', 'node_modules/', 'build/', 'dist/', '.idea/', '.vscode/'],
        'project_only_filters': [],
        'tree_only_filters': ['*.md', 'LICENSE', '.gitignore', 'config.yaml'],
        'full_body_filters': ['main', 'run_app', 'settings', 'configure_*'],
        'output_format': 'text',
    }

    config = DEFAULT_CONFIG.copy()
    script_dir = Path(__file__).resolve().parent
    config_path = Path(args.config or script_dir / 'config.yaml')

    if config_path.exists():
        try:
            with open(config_path, 'r', encoding=args.encoding) as f:
                config.update(yaml.safe_load(f) or {})
        except yaml.YAMLError as e:
            error_help = (
                "\nConseils YAML pour les chemins avec caractères spéciaux :\n"
                "  - Préférez '/' au lieu de '\\' dans les patterns.\n"
                "  - En YAML double-quoted, '\\' est un caractère d'échappement.\n"
                "  - Utilisez des quotes simples ('...') ou doublez les backslashes ('\\\\\\\\')."
            )
            sys.exit(f"ERREUR: Impossible de parser le fichier de configuration '{config_path}': {e}{error_help}")

    project_path = Path(args.project or config.get('project_path', '.')).resolve()
    output_path_str = args.output or config.get('output_path')
    output_format = args.format or config.get('output_format', 'text')
    if output_format not in {'text', 'xml', 'markdown'}:
        logging.warning(f"Format de sortie inconnu '{output_format}' dans la configuration. Fallback vers 'text'.")
        output_format = 'text'

    output_path = Path(output_path_str)
    if not args.no_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")

    log_path = output_path.with_suffix('.log')
    setup_logging(log_path, args.verbose)

    if args.dry_run:
        print("--- MODE DRY RUN ACTIVÉ : AUCUN FICHIER NE SERA ÉCRIT ---")
    if not config_path.exists():
        with open(config_path, 'w', encoding=args.encoding) as f:
            yaml.dump(DEFAULT_CONFIG, f, sort_keys=False, allow_unicode=True)
        logging.info(f"Fichier de configuration par défaut créé à '{config_path}'")
    else:
        logging.info(f"Configuration chargée et fusionnée depuis '{config_path}'")

    if args.git_diff:
        if output_format != 'markdown':
            logging.info(
                f"Mode --git-diff: le format '{output_format}' est ignoré, sortie Markdown forcée."
            )
        ref_a, ref_b = args.git_diff
        logging.info(f"Mode --git-diff activé: calcul du diff entre '{ref_a}' et '{ref_b}'")
        try:
            diff_content = get_git_diff(project_path, ref_a, ref_b)
        except RuntimeError as e:
            logging.error(str(e))
            sys.exit(str(e))

        if not diff_content.strip():
            diff_content = "Aucune différence détectée entre ces révisions.\n"

        full_body = (
            f"# Diff Git: {ref_a} -> {ref_b}\n\n"
            "```diff\n"
            f"{diff_content}"
            "```\n"
        )
        stats = get_file_stats(full_body, args.encoding)
        final_output_str = "".join([
            "Ce fichier est un rapport de diff Git généré par AI Context Craft.\n",
            f"Date de génération : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"Statistiques du contenu : {stats}\n\n",
            full_body
        ])

        if output_path.suffix.lower() == '.txt':
            output_path = output_path.with_suffix('.md')
            log_path = output_path.with_suffix('.log')

        if not args.dry_run:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding=args.encoding) as f:
                f.write(final_output_str)
            print("\nOpération terminée.")
            print(f"Fichier de sortie généré : {output_path.resolve()}")
        else:
            print("\nOpération (dry run) terminée.")
            print(f"Le fichier de sortie aurait été : {output_path.resolve()}")

        print(f"Fichier de log généré : {log_path.resolve()}")
        print(f"Statistiques finales : {stats}")
        return

    logging.info("Assemblage des filtres...")

    def clean_patterns(patterns):
        if not patterns:
            return []
        return [p for p in patterns if p and p.strip()]

    include_patterns = normalize_glob_patterns(clean_patterns(config.get('include_patterns') or ['**/*']))
    common_filters = normalize_glob_patterns(clean_patterns(config.get('common_filters') or []))
    project_only_filters = normalize_glob_patterns(clean_patterns(config.get('project_only_filters') or []))
    tree_only_filters = normalize_glob_patterns(clean_patterns(config.get('tree_only_filters') or []))
    full_body_filters = config.get('full_body_filters') or []

    final_project_filters = common_filters + project_only_filters
    final_tree_filters = common_filters + tree_only_filters

    output_path_base = Path(output_path_str).stem
    auto_exclude_pattern = f'{output_path_base}*'
    final_project_filters.append(auto_exclude_pattern)
    final_tree_filters.append(auto_exclude_pattern)

    ignore_manager = IgnoreManager(
        project_path, disabled=args.no_ignore, encoding=args.encoding
    )
    if args.no_ignore:
        logging.info("Bouclier natif : .gitignore désactivés (--no-ignore), règles de sécurité actives.")
    else:
        logging.info("Bouclier natif : .gitignore hiérarchiques actifs (étage 1).")

    include_spec = pathspec.PathSpec.from_lines('gitwildmatch', include_patterns)
    project_exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', final_project_filters)
    tree_exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', final_tree_filters)

    logging.info("="*50)
    logging.info("CONFIGURATION FINALE DES FILTRES DE DÉBOGAGE")
    logging.info(f"  - PATTERNS D'INCLUSION: {include_patterns}")
    logging.info(f"  - FILTRES D'EXCLUSION (CONTENU): {final_project_filters}")
    logging.info(f"  - FILTRES D'EXCLUSION (ARBRE): {final_tree_filters}")
    logging.info("="*50)

    print("Concaténation des fichiers...")
    files_data = []

    logging.info("Recherche optimisée des fichiers (avec élagage des dossiers exclus)...")
    final_file_list = []
    for root, dirs, files in os.walk(project_path, topdown=True):
        excluded_dirs = []
        for d in dirs:
            dir_path = Path(root) / d
            dir_path_str = str(dir_path.relative_to(project_path)).replace('\\', '/')
            if ignore_manager.is_ignored(dir_path):
                excluded_dirs.append(d)
            elif project_exclude_spec.match_file(dir_path_str) or project_exclude_spec.match_file(dir_path_str + '/'):
                excluded_dirs.append(d)

        for d in excluded_dirs:
            dirs.remove(d)

        for filename in files:
            file_path = Path(root) / filename
            relative_path_str = str(file_path.relative_to(project_path)).replace('\\', '/')

            if ignore_manager.is_ignored(file_path):
                continue
            if include_spec.match_file(relative_path_str) and not project_exclude_spec.match_file(relative_path_str):
                final_file_list.append(file_path)

    final_file_list.sort()
    concatenated_paths = set(final_file_list)

    logging.info("Génération de l'arbre du projet...")
    project_tree, tree_paths = generate_tree(
        project_path, include_spec, tree_exclude_spec, concatenated_paths,
        ignore_manager=ignore_manager,
    )
    tree_file_paths = {p for p in tree_paths if p.is_file()}
    extension_summary = format_extension_summary(tree_file_paths, concatenated_paths)
    logging.info(f"{len(final_file_list)} fichiers finaux trouvés après filtrage optimisé.")
    logging.info("--- LISTE DES FICHIERS À TRAITER ---")
    for p in final_file_list:
        logging.info(f"  [INCLUS] {str(p.relative_to(project_path)).replace('\\', '/')}")
    logging.info("--- FIN DE LA LISTE ---")

    if not args.tree_only:
        for file_path in final_file_list:
            relative_path_str = str(file_path.relative_to(project_path)).replace('\\', '/')
            try:
                with open(file_path, 'r', encoding=args.encoding, errors='ignore') as f:
                    content = f.read()
                logging.info(f"  -> Traitement de : {relative_path_str}")

                if args.headers_only and file_path.suffix == '.py':
                    content = get_python_headers(content, full_body_filters)
                elif args.strip_comments:
                    content = strip_comments_from_code(content, file_path)

                files_data.append((relative_path_str, content))
            except IOError as e:
                logging.error(f"  -> ERREUR: Impossible de lire {relative_path_str}. Erreur: {e}")

        logging.info("Assemblage du fichier de sortie...")
        full_body = build_output(
            output_format,
            project_tree,
            extension_summary,
            files_data,
            tree_only=False,
        )
        stats = get_file_stats(full_body, args.encoding)
    else:
        logging.info("Mode --tree-only activé : saut de la lecture du contenu des fichiers.")
        full_body = build_output(
            output_format,
            project_tree,
            extension_summary,
            files_data,
            tree_only=True,
        )
        stats = "N/A (Mode arbre uniquement)"

    final_output_str = "".join([
        "Ce fichier est une concaténation de plusieurs fichiers sources d'un projet.\n",
        f"Date de génération : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"Statistiques du contenu : {stats}\n\n",
        full_body
    ])

    if not args.dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding=args.encoding) as f:
            f.write(final_output_str)
        print("\nOpération terminée.")
        print(f"Fichier de sortie généré : {output_path.resolve()}")
    else:
        print("\nOpération (dry run) terminée.")
        print(f"Le fichier de sortie aurait été : {output_path.resolve()}")

    print(f"Fichier de log généré : {log_path.resolve()}")
    print(f"Statistiques finales : {stats}")


if __name__ == '__main__':
    main()
