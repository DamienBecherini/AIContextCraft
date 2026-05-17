import os
from pathlib import Path


def generate_tree(directory, include_spec, exclude_spec, show_sizes=False):
    tree_lines = [f"Arbre du projet : {directory.resolve()}"]

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

    paths = sorted(list(final_paths_for_tree))

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
            tree_lines.append(f"{indent}{connector}{path.name}/")
        else:
            if show_sizes:
                try:
                    size_kb = path.stat().st_size / 1024.0
                    tree_lines.append(f"{indent}{connector}{path.name} ({size_kb:.2f} KB)")
                except OSError:
                    tree_lines.append(f"{indent}{connector}{path.name} (taille inconnue)")
            else:
                tree_lines.append(f"{indent}{connector}{path.name}")

    return "\n".join(tree_lines)
