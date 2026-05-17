from pathlib import Path
from typing import Any

import pathspec


def normalize_glob_patterns(patterns: list[str] | None) -> list[str]:
    """Normalise les patterns pour un matching cross-platform cohérent."""
    if not patterns:
        return []
    normalized: list[str] = []
    for pattern in patterns:
        if not pattern:
            continue
        cleaned = pattern.strip()
        if not cleaned:
            continue
        normalized.append(cleaned.replace('\\', '/'))
    return normalized


class FilterManager:
    def __init__(self, config: dict[str, Any], output_path: Path) -> None:
        include_patterns = normalize_glob_patterns(config.get("include_patterns") or ["**/*"])
        common_filters = normalize_glob_patterns(config.get("common_filters") or [])
        project_only_filters = normalize_glob_patterns(config.get("project_only_filters") or [])
        tree_only_filters = normalize_glob_patterns(config.get("tree_only_filters") or [])

        auto_exclude_pattern = f"{output_path.stem}*"
        final_project_filters = [*common_filters, *project_only_filters, auto_exclude_pattern]
        final_tree_filters = [*common_filters, *tree_only_filters, auto_exclude_pattern]

        self.include_patterns = include_patterns
        self.project_filters = final_project_filters
        self.tree_filters = final_tree_filters

        self._include_spec = pathspec.PathSpec.from_lines("gitwildmatch", include_patterns)
        self._project_exclude_spec = pathspec.PathSpec.from_lines(
            "gitwildmatch", final_project_filters
        )
        self._tree_exclude_spec = pathspec.PathSpec.from_lines("gitwildmatch", final_tree_filters)

    @staticmethod
    def _normalize_relative_path(relative_path: str, is_dir: bool = False) -> str:
        normalized = relative_path.replace("\\", "/")
        if is_dir:
            return normalized if normalized.endswith("/") else f"{normalized}/"
        return normalized

    def is_included(self, relative_path: str) -> bool:
        normalized = self._normalize_relative_path(relative_path)
        return self._include_spec.match_file(normalized)

    def is_project_excluded(self, relative_path: str, is_dir: bool = False) -> bool:
        normalized = self._normalize_relative_path(relative_path, is_dir=is_dir)
        return self._project_exclude_spec.match_file(normalized)

    def is_tree_excluded(self, relative_path: str, is_dir: bool = False) -> bool:
        normalized = self._normalize_relative_path(relative_path, is_dir=is_dir)
        return self._tree_exclude_spec.match_file(normalized)
