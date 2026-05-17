import argparse
import base64
import datetime
import json
import logging
import os
import sys
from pathlib import Path

import pathspec
import pyperclip
import yaml
from rich.console import Console
from rich.progress import track

from craft.file_processor import get_python_headers, strip_comments_from_code
from craft.filter_manager import normalize_glob_patterns
from craft.formatter import build_output
from craft.git_manager import get_git_diff
from craft.ignore_manager import IgnoreManager
from craft.tree_generator import format_extension_summary, generate_tree
from craft.utils import get_file_stats, setup_logging


def maybe_copy_to_clipboard(clipboard_enabled, content, console):
    if not clipboard_enabled:
        return

    try:
        pyperclip.copy(content)
        console.print("[green]Contenu copié dans le presse-papiers.[/green]")
    except (
        pyperclip.PyperclipException,
        getattr(pyperclip, "PyperclipWindowsException", pyperclip.PyperclipException),
    ):
        try:
            encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
            sys.stdout.write(f"\x1b]52;c;{encoded}\x07")
            sys.stdout.flush()
            console.print("[green]Contenu envoyé au presse-papiers via SSH (OSC 52).[/green]")
        except Exception as e:
            logging.warning(
                "Fallback OSC 52 indisponible pour la copie presse-papiers: %s",
                e,
            )


def should_copy_to_clipboard(args, content, console):
    if args.no_clipboard:
        logging.info("Copie presse-papiers désactivée via --no-clipboard.")
        return False

    content_size_bytes = len(content.encode(args.encoding))
    content_size_mb = content_size_bytes / (1024 * 1024)
    clipboard_limit_mb = args.clipboard_limit

    if content_size_mb > clipboard_limit_mb:
        console.print(
            (
                f"[yellow]⚠️ Le fichier généré ({content_size_mb:.2f} Mo) dépasse la limite "
                f"du presse-papiers ({clipboard_limit_mb:.2f} Mo). "
                "Copie annulée. Utilisez -cb <taille> pour forcer.[/yellow]"
            )
        )
        logging.info(
            "Copie presse-papiers annulée (%.2f Mo > %.2f Mo).",
            content_size_mb,
            clipboard_limit_mb,
        )
        return False

    return True


def print_config_resolution_status(console, config_path, config_source, explicit_config_path):
    if config_source == "explicit":
        console.print(f"[cyan]Configuration utilisée :[/cyan] explicite ({config_path.resolve()})")
    elif config_source == "auto":
        console.print(f"[cyan]Configuration utilisée :[/cyan] auto-détectée ({config_path.resolve()})")
    elif config_source == "explicit_missing":
        console.print(
            f"[yellow]Configuration :[/yellow] fichier explicite introuvable ({explicit_config_path}), fallback defaults."
        )
    else:
        console.print("[yellow]Configuration :[/yellow] aucun fichier trouvé, fallback defaults.")


def print_ignore_report(console, project_path, ignore_manager, disabled=False):
    ignore_report = ignore_manager.get_ignore_file_report()
    ignore_names = ", ".join(ignore_manager.IGNORE_FILENAMES)
    header = f"[cyan]Fichiers d'ignore détectés ({ignore_names}) :[/cyan]"
    if disabled:
        header += " [yellow](filtrage ignore désactivé via --no-ignore)[/yellow]"
    elif ignore_manager.disabled_ignore_types:
        disabled_types = ", ".join(sorted(ignore_manager.disabled_ignore_types))
        header += f" [yellow](types désactivés: {disabled_types})[/yellow]"
    console.print(header)

    if not ignore_report:
        console.print("  - (aucun)")
        return

    for item in ignore_report:
        ignore_path = item["path"]
        try:
            rel_path = ignore_path.relative_to(project_path).as_posix()
        except ValueError:
            rel_path = ignore_path.as_posix()

        if item["invalid"]:
            status = "trouve+erreur"
        elif item["used"] and item["active"]:
            status = "trouve+utilise"
        elif item["used"]:
            status = "trouve+utilise(vide)"
        elif disabled:
            status = "trouve+non_utilise(desactive)"
        elif (
            IgnoreManager.resolve_ignore_type(ignore_path.name)
            in ignore_manager.disabled_ignore_types
        ):
            status = "trouve+non_utilise(desactive_type)"
        else:
            status = "trouve+non_utilise"

        console.print(f"  - {rel_path} ({status})")


def parse_ignore_type_values(raw_value, parser, flag_name):
    if not raw_value:
        return set()

    values = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    if not values:
        return set()

    valid_types = set(IgnoreManager.IGNORE_TYPE_TO_FILENAME.keys())
    invalid = sorted({value for value in values if value not in valid_types})
    if invalid:
        parser.error(
            f"{flag_name}: type(s) invalide(s): {', '.join(invalid)}. "
            f"Valeurs autorisées: {', '.join(sorted(valid_types))}."
        )
    return set(values)


def build_execution_report(
    *,
    status,
    mode,
    output_format,
    output_destination,
    output_file,
    log_file,
    stats,
    dry_run,
    no_ignore,
    disabled_ignore_types,
):
    return {
        "status": status,
        "mode": mode,
        "output_format": output_format,
        "output_destination": output_destination,
        "output_file": str(output_file) if output_file else None,
        "log_file": str(log_file) if log_file else None,
        "stats": stats,
        "dry_run": dry_run,
        "ignore_files_disabled_globally": no_ignore,
        "ignore_file_types_disabled": sorted(disabled_ignore_types),
    }


def emit_json_report(report):
    sys.stdout.write(json.dumps(report, ensure_ascii=False) + "\n")


def main():
    console = Console()
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
    parser.add_argument(
        '--no-ignore',
        action='store_true',
        help=(
            "Désactive tous les ignore files hiérarchiques "
            "(.gitignore, .dockerignore, .cursorignore, .npmignore) "
            "(les règles de sécurité restent actives)."
        ),
    )
    parser.add_argument(
        '--skip-ignore-files',
        type=str,
        help=(
            "Désactive sélectivement certains types d'ignore files "
            "(valeurs: gitignore,dockerignore,cursorignore,npmignore)."
        ),
    )
    parser.add_argument(
        '--ignore-files',
        type=str,
        help=(
            "Active uniquement les types listés (valeurs: gitignore,dockerignore,cursorignore,npmignore). "
            "Alias inverse de --skip-ignore-files."
        ),
    )
    parser.add_argument('--git-diff', nargs=2, metavar=('REF_A', 'REF_B'), help="Mode spécial: génère un rapport Markdown du diff Git global entre deux révisions.")
    parser.add_argument('--format', choices=['text', 'xml', 'markdown'], default='xml', help="Format de sortie: xml (défaut), text ou markdown.")
    parser.add_argument(
        '--output-format',
        choices=['human', 'json'],
        default='human',
        help="Format des messages d'exécution: human (défaut) ou json (stdout structuré).",
    )
    parser.add_argument(
        '--output-destination',
        choices=['file', 'stdout', 'both', 'none'],
        default='file',
        help="Destination du contenu généré: file (défaut), stdout, both ou none.",
    )
    parser.add_argument('-cb', '--clipboard-limit', type=float, default=10.0, metavar='MB', help="Taille maximum en Mo pour la copie automatique dans le presse-papiers (défaut: 10.0).")
    parser.add_argument('--no-clipboard', action='store_true', help="Désactive totalement la copie automatique dans le presse-papiers.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Affiche des informations détaillées sur la console.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Réduit les logs console au strict minimum (erreurs).")
    args = parser.parse_args()

    DEFAULT_CONFIG = {
        'include_patterns': ['**/*'],
        'common_filters': ['__pycache__/', '*.pyc', '.git/', '.venv/', 'venv/', 'node_modules/', 'build/', 'dist/', '.idea/', '.vscode/'],
        'project_only_filters': [],
        'tree_only_filters': ['*.md', 'LICENSE', '.gitignore', 'config.yaml'],
        'full_body_filters': ['main', 'run_app', 'settings', 'configure_*'],
        'output_format': 'xml',
    }

    if args.clipboard_limit < 0:
        parser.error("--clipboard-limit doit être >= 0.")
    if args.verbose and args.quiet:
        parser.error("--verbose et --quiet sont incompatibles.")
    if args.skip_ignore_files and args.ignore_files:
        parser.error("--skip-ignore-files et --ignore-files sont incompatibles.")

    config = DEFAULT_CONFIG.copy()
    config_path = None
    config_source = "auto_missing"
    explicit_config_path = None
    if args.config:
        explicit_config_path = Path(args.config)
        if explicit_config_path.exists():
            config_path = explicit_config_path
            config_source = "explicit"
        else:
            config_source = "explicit_missing"
            logging.info(
                "Fichier de configuration explicite introuvable: '%s'. Mode Zero-Config activé.",
                explicit_config_path,
            )
    else:
        config_search_root = Path(args.project or '.').resolve()
        auto_config_candidates = ['.aicc.yaml', 'aicc.yaml', 'aicc.yml', 'config-concat-code.yaml']
        for candidate in auto_config_candidates:
            candidate_path = config_search_root / candidate
            if candidate_path.exists():
                config_path = candidate_path
                config_source = "auto"
                logging.info(f"Fichier de configuration trouvé automatiquement : '{candidate_path}'")
                break
        if config_path is None:
            config_source = "auto_missing"
            logging.info("Aucun fichier de configuration trouvé. Mode Zero-Config activé (basé sur les ignore files hiérarchiques).")

    if config_path is not None:
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
    content_format = args.format or config.get('output_format', 'xml')
    if content_format not in {'text', 'xml', 'markdown'}:
        logging.warning(f"Format de sortie inconnu '{content_format}' dans la configuration. Fallback vers 'xml'.")
        content_format = 'xml'

    output_path_str = args.output or config.get('output_path')
    if not output_path_str:
        default_extension_by_format = {
            'text': 'txt',
            'xml': 'xml',
            'markdown': 'md',
        }
        output_path_str = f"./build/aicc_context.{default_extension_by_format[content_format]}"
        logging.info("Aucun chemin de sortie fourni. Utilisation du chemin par défaut: '%s'", output_path_str)

    output_path = Path(output_path_str)
    if not args.no_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")

    write_log_file = args.output_format == "human" or args.output_destination in {"file", "both"}
    log_path = output_path.with_suffix('.log') if write_log_file else None
    setup_logging(log_path, args.verbose, quiet=args.quiet, enable_file_logging=write_log_file)

    if args.dry_run:
        console.print("[bold yellow]--- MODE DRY RUN ACTIVÉ : AUCUN FICHIER NE SERA ÉCRIT ---[/bold yellow]")
    if config_path is not None:
        logging.info(f"Configuration chargée et fusionnée depuis '{config_path}'")
    if args.output_format == "human" and not args.quiet:
        print_config_resolution_status(console, config_path, config_source, explicit_config_path)

    if args.git_diff:
        if content_format != 'markdown':
            logging.info(
                f"Mode --git-diff: le format '{content_format}' est ignoré, sortie Markdown forcée."
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

        if output_path.suffix.lower() != '.md':
            output_path = output_path.with_suffix('.md')
            log_path = output_path.with_suffix('.log')

        if args.output_format == "human" and args.output_destination in {"stdout", "both"}:
            sys.stdout.write(final_output_str)
            if not final_output_str.endswith("\n"):
                sys.stdout.write("\n")

        if not args.dry_run and args.output_destination in {"file", "both"}:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding=args.encoding) as f:
                f.write(final_output_str)
            if args.output_format == "human" and not args.quiet:
                console.print("\n[bold green]Opération terminée.[/bold green]")
                console.print(f"[cyan]Fichier de sortie généré :[/cyan] {output_path.resolve()}")
        elif args.dry_run and args.output_format == "human" and not args.quiet:
            console.print("\n[bold yellow]Opération (dry run) terminée.[/bold yellow]")
            console.print(f"[cyan]Le fichier de sortie aurait été :[/cyan] {output_path.resolve()}")

        if args.output_destination != "none":
            maybe_copy_to_clipboard(should_copy_to_clipboard(args, final_output_str, console), final_output_str, console)
        report = build_execution_report(
            status="success",
            mode="git_diff",
            output_format=content_format,
            output_destination=args.output_destination,
            output_file=output_path if args.output_destination in {"file", "both"} else None,
            log_file=log_path,
            stats=stats,
            dry_run=args.dry_run,
            no_ignore=args.no_ignore,
            disabled_ignore_types=set(),
        )
        if args.output_format == "json":
            emit_json_report(report)
        elif not args.quiet:
            if log_path is not None:
                console.print(f"[cyan]Fichier de log généré :[/cyan] {log_path.resolve()}")
            console.print(f"[magenta]Statistiques finales :[/magenta] {stats}")
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

    disabled_ignore_types = set()
    if args.skip_ignore_files:
        disabled_ignore_types = parse_ignore_type_values(
            args.skip_ignore_files, parser, "--skip-ignore-files"
        )
    elif args.ignore_files:
        enabled_types = parse_ignore_type_values(args.ignore_files, parser, "--ignore-files")
        all_types = set(IgnoreManager.IGNORE_TYPE_TO_FILENAME.keys())
        disabled_ignore_types = all_types - enabled_types

    if args.no_ignore:
        disabled_ignore_types = set(IgnoreManager.IGNORE_TYPE_TO_FILENAME.keys())

    ignore_manager = IgnoreManager(
        project_path,
        disabled=args.no_ignore,
        disabled_ignore_types=disabled_ignore_types,
        encoding=args.encoding,
    )
    if args.no_ignore:
        logging.info(
            "Bouclier natif : ignore files (%s) désactivés (--no-ignore), règles de sécurité actives.",
            ", ".join(ignore_manager.IGNORE_FILENAMES),
        )
    elif disabled_ignore_types:
        logging.info(
            "Bouclier natif : types d'ignore files désactivés: %s",
            ", ".join(sorted(disabled_ignore_types)),
        )
    else:
        logging.info(
            "Bouclier natif : ignore files hiérarchiques actifs (étage 1) : %s",
            ", ".join(ignore_manager.IGNORE_FILENAMES),
        )

    include_spec = pathspec.PathSpec.from_lines('gitwildmatch', include_patterns)
    project_exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', final_project_filters)
    tree_exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', final_tree_filters)

    logging.info("="*50)
    logging.info("CONFIGURATION FINALE DES FILTRES DE DÉBOGAGE")
    logging.info(f"  - PATTERNS D'INCLUSION: {include_patterns}")
    logging.info(f"  - FILTRES D'EXCLUSION (CONTENU): {final_project_filters}")
    logging.info(f"  - FILTRES D'EXCLUSION (ARBRE): {final_tree_filters}")
    logging.info("="*50)

    console.print("[bold]Concaténation des fichiers...[/bold]")
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
        file_iterator = track(
            final_file_list,
            description="Traitement des fichiers...",
            disable=not sys.stdout.isatty(),
        )
        for file_path in file_iterator:
            relative_path_str = str(file_path.relative_to(project_path)).replace('\\', '/')
            try:
                with open(file_path, 'r', encoding=args.encoding, errors='ignore') as f:
                    content = f.read()

                if args.headers_only and file_path.suffix == '.py':
                    content = get_python_headers(content, full_body_filters)
                elif args.strip_comments:
                    content = strip_comments_from_code(content, file_path)

                files_data.append((relative_path_str, content))
            except IOError as e:
                logging.error(f"  -> ERREUR: Impossible de lire {relative_path_str}. Erreur: {e}")

        logging.info("Assemblage du fichier de sortie...")
        full_body = build_output(
            content_format,
            project_tree,
            extension_summary,
            files_data,
            tree_only=False,
        )
        stats = get_file_stats(full_body, args.encoding)
    else:
        logging.info("Mode --tree-only activé : saut de la lecture du contenu des fichiers.")
        full_body = build_output(
            content_format,
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

    if args.output_format == "human" and args.output_destination in {"stdout", "both"}:
        sys.stdout.write(final_output_str)
        if not final_output_str.endswith("\n"):
            sys.stdout.write("\n")

    if not args.dry_run and args.output_destination in {"file", "both"}:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding=args.encoding) as f:
            f.write(final_output_str)
        if args.output_format == "human" and not args.quiet:
            console.print("\n[bold green]Opération terminée.[/bold green]")
            console.print(f"[cyan]Fichier de sortie généré :[/cyan] {output_path.resolve()}")
    elif args.dry_run and args.output_format == "human" and not args.quiet:
        console.print("\n[bold yellow]Opération (dry run) terminée.[/bold yellow]")
        console.print(f"[cyan]Le fichier de sortie aurait été :[/cyan] {output_path.resolve()}")

    if args.output_destination != "none":
        maybe_copy_to_clipboard(should_copy_to_clipboard(args, final_output_str, console), final_output_str, console)
    report = build_execution_report(
        status="success",
        mode="standard",
        output_format=content_format,
        output_destination=args.output_destination,
        output_file=output_path if args.output_destination in {"file", "both"} else None,
        log_file=log_path,
        stats=stats,
        dry_run=args.dry_run,
        no_ignore=args.no_ignore,
        disabled_ignore_types=disabled_ignore_types,
    )
    if args.output_format == "json":
        emit_json_report(report)
        return

    if not args.quiet:
        print_ignore_report(console, project_path, ignore_manager, disabled=args.no_ignore)
        if log_path is not None:
            console.print(f"[cyan]Fichier de log généré :[/cyan] {log_path.resolve()}")
        console.print(f"[magenta]Statistiques finales :[/magenta] {stats}")


if __name__ == '__main__':
    main()
