import logging
import os
from pathlib import Path

import pathspec

from craft.filter_manager import normalize_glob_patterns

SECURITY_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    ".git/",
]


def _parse_ignore_lines(lines):
    patterns = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        patterns.append(stripped)
    return normalize_glob_patterns(patterns)


class IgnoreManager:
    """First-stage filter: security patterns and hierarchical ignore files."""

    IGNORE_FILENAMES = (".gitignore", ".dockerignore", ".cursorignore", ".npmignore")
    IGNORE_TYPE_TO_FILENAME = {
        "gitignore": ".gitignore",
        "dockerignore": ".dockerignore",
        "cursorignore": ".cursorignore",
        "npmignore": ".npmignore",
    }
    FILENAME_TO_IGNORE_TYPE = {v: k for k, v in IGNORE_TYPE_TO_FILENAME.items()}

    def __init__(
        self,
        project_root: Path,
        *,
        disabled: bool = False,
        disabled_ignore_types: set[str] | None = None,
        encoding: str = "utf-8",
    ):
        self.project_root = project_root.resolve()
        self.disabled = disabled
        self.disabled_ignore_types = set(disabled_ignore_types or set())
        self.encoding = encoding
        self.security_spec = pathspec.PathSpec.from_lines("gitwildmatch", SECURITY_PATTERNS)
        self._spec_cache: dict[Path, list[pathspec.PathSpec]] = {}
        self._detected_ignore_files: set[Path] = set()
        self._used_ignore_files: set[Path] = set()
        self._active_ignore_files: set[Path] = set()
        self._invalid_ignore_files: set[Path] = set()
        self._scan_detected_ignore_files()

    @property
    def enabled_ignore_filenames(self) -> tuple[str, ...]:
        enabled = []
        for ignore_type, filename in self.IGNORE_TYPE_TO_FILENAME.items():
            if ignore_type not in self.disabled_ignore_types:
                enabled.append(filename)
        return tuple(enabled)

    @classmethod
    def resolve_ignore_type(cls, filename: str) -> str | None:
        return cls.FILENAME_TO_IGNORE_TYPE.get(filename)

    def _relative_posix(self, path: Path) -> str:
        resolved = path.resolve()
        rel = resolved.relative_to(self.project_root)
        return str(rel).replace("\\", "/")

    def _matches_spec(self, spec: pathspec.PathSpec, rel_from_dir: str, is_dir: bool) -> bool:
        if spec.match_file(rel_from_dir):
            return True
        if is_dir and spec.match_file(rel_from_dir + "/"):
            return True
        return False

    def _scan_detected_ignore_files(self) -> None:
        for root, _, files in os.walk(self.project_root):
            for filename in files:
                if filename in self.IGNORE_FILENAMES:
                    self._detected_ignore_files.add((Path(root) / filename).resolve())

    def _load_ignore_specs(self, directory: Path) -> list[pathspec.PathSpec]:
        directory = directory.resolve()
        if directory in self._spec_cache:
            return self._spec_cache[directory]

        specs: list[pathspec.PathSpec] = []
        for ignore_name in self.enabled_ignore_filenames:
            ignore_path = (directory / ignore_name).resolve()
            if not ignore_path.is_file():
                continue

            self._detected_ignore_files.add(ignore_path)
            self._used_ignore_files.add(ignore_path)

            try:
                with open(ignore_path, "r", encoding=self.encoding) as f:
                    patterns = _parse_ignore_lines(f.readlines())
            except (OSError, UnicodeError) as exc:
                self._invalid_ignore_files.add(ignore_path)
                logging.warning("Impossible de lire le fichier d'ignore '%s': %s", ignore_path, exc)
                continue

            if not patterns:
                continue

            try:
                spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
            except Exception as exc:  # pragma: no cover - protection supplémentaire
                self._invalid_ignore_files.add(ignore_path)
                logging.warning("Impossible de parser le fichier d'ignore '%s': %s", ignore_path, exc)
                continue

            specs.append(spec)
            self._active_ignore_files.add(ignore_path)

        self._spec_cache[directory] = specs
        return specs

    def _ancestor_directories(self, path: Path):
        resolved = path.resolve()
        if resolved == self.project_root:
            yield self.project_root
            return

        current = resolved if resolved.is_dir() else resolved.parent
        ancestors = []
        while True:
            ancestors.append(current)
            if current == self.project_root:
                break
            current = current.parent

        for directory in reversed(ancestors):
            yield directory

    def is_ignored(self, path: Path) -> bool:
        rel = self._relative_posix(path)
        is_dir = path.is_dir() or rel.endswith("/")

        if self._matches_spec(self.security_spec, rel, is_dir):
            return True

        if self.disabled:
            return False

        for directory in self._ancestor_directories(path):
            specs = self._load_ignore_specs(directory)
            if not specs:
                continue
            rel_from_dir = self._relative_posix(path)
            if directory != self.project_root:
                prefix = self._relative_posix(directory)
                if rel_from_dir == prefix:
                    rel_from_dir = "."
                elif rel_from_dir.startswith(prefix + "/"):
                    rel_from_dir = rel_from_dir[len(prefix) + 1 :]
                else:
                    continue
            for spec in specs:
                if self._matches_spec(spec, rel_from_dir, is_dir):
                    return True

        return False

    def get_ignore_file_report(self) -> list[dict[str, object]]:
        report = []
        for ignore_path in sorted(self._detected_ignore_files):
            report.append(
                {
                    "path": ignore_path,
                    "used": ignore_path in self._used_ignore_files,
                    "active": ignore_path in self._active_ignore_files,
                    "invalid": ignore_path in self._invalid_ignore_files,
                }
            )
        return report
