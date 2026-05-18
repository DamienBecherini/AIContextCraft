import argparse
import base64
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any

import pyperclip
import yaml
from rich.console import Console

from craft.context_builder import ContextBuilder
from craft.filter_manager import FilterManager
from craft.formatter import build_output
from craft.git_manager import get_git_diff
from craft.ignore_manager import IgnoreManager
from craft.utils import get_file_stats, setup_logging


def maybe_copy_to_clipboard(clipboard_enabled: bool, content: str, console: Console) -> None:
    if not clipboard_enabled:
        return

    try:
        pyperclip.copy(content)
        console.print("[green]Content copied to clipboard.[/green]")
    except (
        pyperclip.PyperclipException,
        getattr(pyperclip, "PyperclipWindowsException", pyperclip.PyperclipException),
    ):
        try:
            encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
            sys.stdout.write(f"\x1b]52;c;{encoded}\x07")
            sys.stdout.flush()
            console.print("[green]Content sent to clipboard via SSH (OSC 52).[/green]")
        except Exception as e:
            logging.warning(
                "OSC 52 fallback unavailable for clipboard copy: %s",
                e,
            )


def should_copy_to_clipboard(args: argparse.Namespace, content: str, console: Console) -> bool:
    if args.no_clipboard:
        logging.info("Clipboard copy disabled via --no-clipboard.")
        return False

    content_size_bytes = len(content.encode(args.encoding))
    content_size_mb = content_size_bytes / (1024 * 1024)
    clipboard_limit_mb = args.clipboard_limit

    if content_size_mb > clipboard_limit_mb:
        console.print(
            (
                f"[yellow]⚠️ Generated output ({content_size_mb:.2f} MB) exceeds the "
                f"clipboard limit ({clipboard_limit_mb:.2f} MB). "
                "Copy skipped. Use -cb <size> to raise the limit.[/yellow]"
            )
        )
        logging.info(
            "Clipboard copy skipped (%.2f MB > %.2f MB).",
            content_size_mb,
            clipboard_limit_mb,
        )
        return False

    return True


def print_config_resolution_status(
    console: Console,
    config_path: Path | None,
    config_source: str,
    explicit_config_path: Path | None,
) -> None:
    if config_source == "explicit":
        console.print(f"[cyan]Configuration used:[/cyan] explicit ({config_path.resolve()})")
    elif config_source == "auto":
        console.print(f"[cyan]Configuration used:[/cyan] auto-detected ({config_path.resolve()})")
    elif config_source == "explicit_missing":
        console.print(
            f"[yellow]Configuration:[/yellow] explicit file not found ({explicit_config_path}), using defaults."
        )
    else:
        console.print("[yellow]Configuration:[/yellow] no config file found, using defaults.")


def print_ignore_report(
    console: Console,
    project_path: Path,
    ignore_manager: IgnoreManager,
    disabled: bool = False,
) -> None:
    ignore_report = ignore_manager.get_ignore_file_report()
    ignore_names = ", ".join(ignore_manager.IGNORE_FILENAMES)
    header = f"[cyan]Ignore files detected ({ignore_names}):[/cyan]"
    if disabled:
        header += " [yellow](ignore filtering disabled via --no-ignore)[/yellow]"
    elif ignore_manager.disabled_ignore_types:
        disabled_types = ", ".join(sorted(ignore_manager.disabled_ignore_types))
        header += f" [yellow](disabled types: {disabled_types})[/yellow]"
    console.print(header)

    if not ignore_report:
        console.print("  - (none)")
        return

    for item in ignore_report:
        ignore_path = item["path"]
        try:
            rel_path = ignore_path.relative_to(project_path).as_posix()
        except ValueError:
            rel_path = ignore_path.as_posix()

        if item["invalid"]:
            status = "found+error"
        elif item["used"] and item["active"]:
            status = "found+used"
        elif item["used"]:
            status = "found+used(empty)"
        elif disabled:
            status = "found+unused(disabled)"
        elif (
            IgnoreManager.resolve_ignore_type(ignore_path.name)
            in ignore_manager.disabled_ignore_types
        ):
            status = "found+unused(disabled_type)"
        else:
            status = "found+unused"

        console.print(f"  - {rel_path} ({status})")


def parse_ignore_type_values(raw_value: str | None, parser: argparse.ArgumentParser, flag_name: str) -> set[str]:
    if not raw_value:
        return set()

    values = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    if not values:
        return set()

    valid_types = set(IgnoreManager.IGNORE_TYPE_TO_FILENAME.keys())
    invalid = sorted({value for value in values if value not in valid_types})
    if invalid:
        parser.error(
            f"{flag_name}: invalid type(s): {', '.join(invalid)}. "
            f"Allowed values: {', '.join(sorted(valid_types))}."
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
) -> dict[str, Any]:
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


def emit_json_report(report: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(report, ensure_ascii=False) + "\n")


def main():
    console = Console(stderr=True)
    parser = argparse.ArgumentParser(description="Aggregate project files into a single output file for LLM context.")
    parser.add_argument('-c', '--config', type=str, help="Path to the YAML configuration file.")
    parser.add_argument('-p', '--project', type=str, help="Path to the target project.")
    parser.add_argument('-o', '--output', type=str, help="Path to the output file.")
    parser.add_argument('--no-timestamp', action='store_true', help="Do not append a timestamp to the output filename.")
    parser.add_argument('--strip-comments', action='store_true', help="Strip comments from source files.")
    parser.add_argument('--headers-only', action='store_true', help="Keep only function/method signatures.")
    parser.add_argument('--tree-only', action='store_true', help="Generate only the project tree (sizes, extensions) without file contents.")
    parser.add_argument('--dry-run', action='store_true', help="Simulate the run without writing a file.")
    parser.add_argument('--encoding', type=str, default='utf-8', help="File encoding (default: utf-8).")
    parser.add_argument(
        '--no-ignore',
        action='store_true',
        help=(
            "Disable all hierarchical ignore files "
            "(.gitignore, .dockerignore, .cursorignore, .npmignore) "
            "(security rules remain active)."
        ),
    )
    parser.add_argument(
        '--skip-ignore-files',
        type=str,
        help=(
            "Selectively disable ignore file types "
            "(values: gitignore,dockerignore,cursorignore,npmignore)."
        ),
    )
    parser.add_argument(
        '--ignore-files',
        type=str,
        help=(
            "Enable only the listed types (values: gitignore,dockerignore,cursorignore,npmignore). "
            "Inverse alias of --skip-ignore-files."
        ),
    )
    parser.add_argument('--git-diff', nargs=2, metavar=('REF_A', 'REF_B'), help="Special mode: generate a Markdown report of the global Git diff between two revisions.")
    parser.add_argument('--format', choices=['text', 'xml', 'markdown'], default='xml', help="Output format: xml (default), text, or markdown.")
    parser.add_argument(
        '--output-format',
        choices=['human', 'json'],
        default='human',
        help="Execution message format: human (default) or json (structured stdout).",
    )
    parser.add_argument(
        '--output-destination',
        choices=['file', 'stdout', 'both', 'none'],
        default='file',
        help="Generated content destination: file (default), stdout, both, or none.",
    )
    parser.add_argument('-cb', '--clipboard-limit', type=float, default=10.0, metavar='MB', help="Max size in MB for automatic clipboard copy (default: 10.0).")
    parser.add_argument('--no-clipboard', action='store_true', help="Disable automatic clipboard copy entirely.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Show detailed information on the console.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Reduce console logs to errors only.")
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
        parser.error("--clipboard-limit must be >= 0.")
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet are incompatible.")
    if args.skip_ignore_files and args.ignore_files:
        parser.error("--skip-ignore-files and --ignore-files are incompatible.")

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
                "Explicit configuration file not found: '%s'. Zero-Config mode enabled.",
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
                logging.info(f"Configuration file auto-detected: '{candidate_path}'")
                break
        if config_path is None:
            config_source = "auto_missing"
            logging.info("No configuration file found. Zero-Config mode enabled (hierarchical ignore files).")

    if config_path is not None:
        try:
            with open(config_path, 'r', encoding=args.encoding) as f:
                config.update(yaml.safe_load(f) or {})
        except yaml.YAMLError as e:
            error_help = (
                "\nYAML tips for paths with special characters:\n"
                "  - Prefer '/' instead of '\\' in patterns.\n"
                "  - In double-quoted YAML, '\\' is an escape character.\n"
                "  - Use single quotes ('...') or double backslashes ('\\\\\\\\')."
            )
            sys.exit(f"ERROR: Unable to parse configuration file '{config_path}': {e}{error_help}")

    project_path = Path(args.project or config.get('project_path', '.')).resolve()
    content_format = args.format or config.get('output_format', 'xml')
    if content_format not in {'text', 'xml', 'markdown'}:
        logging.warning(f"Unknown output format '{content_format}' in configuration. Falling back to 'xml'.")
        content_format = 'xml'

    output_path_str = args.output or config.get('output_path')
    if not output_path_str:
        default_extension_by_format = {
            'text': 'txt',
            'xml': 'xml',
            'markdown': 'md',
        }
        output_path_str = f"./build/aicc_context.{default_extension_by_format[content_format]}"
        logging.info("No output path provided. Using default path: '%s'", output_path_str)

    output_path = Path(output_path_str)
    if not args.no_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")

    write_log_file = args.output_format == "human" or args.output_destination in {"file", "both"}
    log_path = output_path.with_suffix('.log') if write_log_file else None
    setup_logging(log_path, args.verbose, quiet=args.quiet, enable_file_logging=write_log_file)

    if args.dry_run and args.output_format != "json":
        console.print("[bold yellow]--- DRY RUN MODE: NO FILE WILL BE WRITTEN ---[/bold yellow]")
    if config_path is not None:
        logging.info(f"Configuration loaded and merged from '{config_path}'")
    if args.output_format == "human" and not args.quiet:
        print_config_resolution_status(console, config_path, config_source, explicit_config_path)

    if args.git_diff:
        if content_format != 'markdown':
            logging.info(
                f"--git-diff mode: format '{content_format}' is ignored; Markdown output forced."
            )
        ref_a, ref_b = args.git_diff
        logging.info(f"--git-diff mode enabled: computing diff between '{ref_a}' and '{ref_b}'")
        try:
            diff_content = get_git_diff(project_path, ref_a, ref_b)
        except RuntimeError as e:
            logging.error(str(e))
            sys.exit(str(e))

        if not diff_content.strip():
            diff_content = "No differences detected between these revisions.\n"

        full_body = (
            f"# Diff Git: {ref_a} -> {ref_b}\n\n"
            "```diff\n"
            f"{diff_content}"
            "```\n"
        )
        stats = get_file_stats(full_body, args.encoding)
        final_output_str = "".join([
            "This file is a Git diff report generated by AI Context Craft.\n",
            f"Generation date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"Content statistics: {stats}\n\n",
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
                console.print("\n[bold green]Done.[/bold green]")
                console.print(f"[cyan]Output file:[/cyan] {output_path.resolve()}")
        elif args.dry_run and args.output_format == "human" and not args.quiet:
            console.print("\n[bold yellow]Dry run complete.[/bold yellow]")
            console.print(f"[cyan]Output file would be:[/cyan] {output_path.resolve()}")

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
                console.print(f"[cyan]Log file:[/cyan] {log_path.resolve()}")
            console.print(f"[magenta]Final statistics:[/magenta] {stats}")
        return

    logging.info("Assembling filters...")
    filter_manager = FilterManager(config, output_path)
    full_body_filters = config.get('full_body_filters') or []

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
            "Native shield: ignore files (%s) disabled (--no-ignore); security rules active.",
            ", ".join(ignore_manager.IGNORE_FILENAMES),
        )
    elif disabled_ignore_types:
        logging.info(
            "Native shield: disabled ignore file types: %s",
            ", ".join(sorted(disabled_ignore_types)),
        )
    else:
        logging.info(
            "Native shield: hierarchical ignore files active (stage 1): %s",
            ", ".join(ignore_manager.IGNORE_FILENAMES),
        )

    logging.info("="*50)
    logging.info("FINAL FILTER DEBUG CONFIGURATION")
    logging.info(f"  - INCLUDE PATTERNS: {filter_manager.include_patterns}")
    logging.info(f"  - EXCLUSION FILTERS (CONTENT): {filter_manager.project_filters}")
    logging.info(f"  - EXCLUSION FILTERS (TREE): {filter_manager.tree_filters}")
    logging.info("="*50)

    if args.output_format != "json" and not args.quiet:
        console.print("[bold]Concatenating files...[/bold]")
    builder = ContextBuilder(
        project_path=project_path,
        filter_manager=filter_manager,
        ignore_manager=ignore_manager,
        encoding=args.encoding,
        args=args,
        full_body_filters=full_body_filters,
        console=console,
    )
    project_tree, extension_summary, files_data = builder.build()

    if not args.tree_only:
        logging.info("Assembling output file...")
        full_body = build_output(
            content_format,
            project_tree,
            extension_summary,
            files_data,
            tree_only=False,
        )
        stats = get_file_stats(full_body, args.encoding)
    else:
        logging.info("--tree-only mode enabled: skipping file content reads.")
        full_body = build_output(
            content_format,
            project_tree,
            extension_summary,
            files_data,
            tree_only=True,
        )
        stats = "N/A (tree-only mode)"

    final_output_str = "".join([
        "This file is a concatenation of several source files from a project.\n",
        f"Generation date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"Content statistics: {stats}\n\n",
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
            console.print("\n[bold green]Done.[/bold green]")
            console.print(f"[cyan]Output file:[/cyan] {output_path.resolve()}")
    elif args.dry_run and args.output_format == "human" and not args.quiet:
        console.print("\n[bold yellow]Dry run complete.[/bold yellow]")
        console.print(f"[cyan]Output file would be:[/cyan] {output_path.resolve()}")

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
            console.print(f"[cyan]Log file:[/cyan] {log_path.resolve()}")
        console.print(f"[magenta]Final statistics:[/magenta] {stats}")


if __name__ == '__main__':
    main()
