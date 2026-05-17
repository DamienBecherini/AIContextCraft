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
    """First-stage filter: security patterns and hierarchical .gitignore files."""

    def __init__(self, project_root: Path, *, disabled: bool = False, encoding: str = "utf-8"):
        self.project_root = project_root.resolve()
        self.disabled = disabled
        self.encoding = encoding
        self.security_spec = pathspec.PathSpec.from_lines("gitwildmatch", SECURITY_PATTERNS)
        self._spec_cache: dict[Path, pathspec.PathSpec | None] = {}

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

    def _load_gitignore_spec(self, directory: Path) -> pathspec.PathSpec | None:
        directory = directory.resolve()
        if directory in self._spec_cache:
            return self._spec_cache[directory]

        gitignore_path = directory / ".gitignore"
        if not gitignore_path.is_file():
            self._spec_cache[directory] = None
            return None

        with open(gitignore_path, "r", encoding=self.encoding) as f:
            patterns = _parse_ignore_lines(f.readlines())

        spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns) if patterns else None
        self._spec_cache[directory] = spec
        return spec

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
            spec = self._load_gitignore_spec(directory)
            if spec is None:
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
            if self._matches_spec(spec, rel_from_dir, is_dir):
                return True

        return False
