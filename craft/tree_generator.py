import os
from pathlib import Path

from craft.utils import format_bytes

TREE_LEGEND = (
    "Légende : ● fichier concaténé dans le contenu ci-dessous ; "
    "○ fichier affiché à titre indicatif (exclu par project_only_filters). "
    "Les tailles des dossiers et de la section Extensions indiquent d'abord le total "
    "des fichiers ●, puis entre parenthèses le total réel de tous les fichiers visibles dans l'arbre."
)

SYMBOL_CONCATENATED = "●"
SYMBOL_INDICATIVE = "○"
NO_EXTENSION_LABEL = "(sans extension)"


def build_tree_legend():
    return TREE_LEGEND


def _file_size(path):
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _collect_tree_paths(directory, include_spec, exclude_spec):
    paths_for_tree = set()

    for root, dirs, files in os.walk(directory, topdown=True):
        root_path = Path(root)

        excluded_dirs = []
        for d in dirs:
            dir_path_str = str((root_path / d).relative_to(directory)).replace('\\', '/')
            if exclude_spec.match_file(dir_path_str) or exclude_spec.match_file(dir_path_str + '/'):
                excluded_dirs.append(d)

        for d in excluded_dirs:
            dirs.remove(d)

        for name in dirs + files:
            item_path = root_path / name
            relative_p_str = str(item_path.relative_to(directory)).replace('\\', '/')
            if include_spec.match_file(relative_p_str) and not exclude_spec.match_file(relative_p_str):
                paths_for_tree.add(item_path)

    final_paths_for_tree = set(paths_for_tree)
    for path in paths_for_tree:
        parent = path.parent
        while parent and parent != directory:
            final_paths_for_tree.add(parent)
            parent = parent.parent

    return final_paths_for_tree


def _aggregate_dir_sizes(directory, paths, concatenated_paths):
    file_metrics = {}
    dir_sizes = {p: [0, 0] for p in paths if p.is_dir()}

    for path in paths:
        if not path.is_file():
            continue
        real_size = _file_size(path)
        concat_size = real_size if path in concatenated_paths else 0
        file_metrics[path] = (concat_size, real_size)

        parent = path.parent
        while True:
            if parent in dir_sizes:
                dir_sizes[parent][0] += concat_size
                dir_sizes[parent][1] += real_size
            if parent == directory:
                break
            parent = parent.parent

    return file_metrics, {d: (v[0], v[1]) for d, v in dir_sizes.items()}


def _format_dir_suffix(concat_size, real_size):
    if concat_size == 0 and real_size == 0:
        return ""
    if concat_size == real_size:
        return f" — {format_bytes(concat_size)}"
    return f" — {format_bytes(concat_size)} (Total réel : {format_bytes(real_size)})"


def _extension_key(path):
    suffix = path.suffix
    return suffix if suffix else NO_EXTENSION_LABEL


def format_extension_summary(tree_file_paths, concatenated_paths):
    concat_by_ext = {}
    real_by_ext = {}

    for path in tree_file_paths:
        if not path.is_file():
            continue
        ext = _extension_key(path)
        size = _file_size(path)
        real_by_ext[ext] = real_by_ext.get(ext, 0) + size
        if path in concatenated_paths:
            concat_by_ext[ext] = concat_by_ext.get(ext, 0) + size

    if not concat_by_ext:
        return "Extensions (fichiers concaténés) :\n  (aucune)"

    lines = ["Extensions (fichiers concaténés) :"]
    for ext in sorted(concat_by_ext.keys(), key=lambda e: e.lower()):
        concat_size = concat_by_ext[ext]
        real_size = real_by_ext.get(ext, concat_size)
        if concat_size == real_size:
            lines.append(f"  {ext:<20} {format_bytes(concat_size)}")
        else:
            lines.append(
                f"  {ext:<20} {format_bytes(concat_size)} (Total réel : {format_bytes(real_size)})"
            )
    return "\n".join(lines)


def generate_tree(directory, include_spec, exclude_spec, concatenated_paths):
    concatenated_paths = set(concatenated_paths)
    final_paths_for_tree = _collect_tree_paths(directory, include_spec, exclude_spec)
    file_metrics, dir_sizes = _aggregate_dir_sizes(
        directory, final_paths_for_tree, concatenated_paths
    )

    tree_lines = [build_tree_legend(), f"Arbre du projet : {directory.resolve()}"]
    paths = sorted(final_paths_for_tree)

    last_in_level = {}
    for path in paths:
        if path == directory:
            continue
        relative_path = path.relative_to(directory)
        depth = len(relative_path.parts)

        try:
            siblings_in_tree = [p for p in sorted(path.parent.iterdir()) if p in final_paths_for_tree]
            is_last = (path == siblings_in_tree[-1]) if siblings_in_tree else True
        except (IndexError, FileNotFoundError):
            is_last = True

        last_in_level[depth - 1] = is_last

        indent = "".join(["    " if last_in_level.get(i) else "│   " for i in range(depth - 1)])
        connector = "└── " if is_last else "├── "

        if path.is_dir():
            concat_size, real_size = dir_sizes.get(path, (0, 0))
            suffix = _format_dir_suffix(concat_size, real_size)
            tree_lines.append(f"{indent}{connector}{path.name}/{suffix}")
        else:
            concat_size, real_size = file_metrics.get(path, (0, 0))
            if path in concatenated_paths:
                tree_lines.append(
                    f"{indent}{connector}{SYMBOL_CONCATENATED} {path.name} — {format_bytes(concat_size)}"
                )
            else:
                tree_lines.append(f"{indent}{connector}{SYMBOL_INDICATIVE} {path.name}")

    return "\n".join(tree_lines), final_paths_for_tree

