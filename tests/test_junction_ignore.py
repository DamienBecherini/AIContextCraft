from pathlib import Path

import pytest

from craft.ignore_manager import IgnoreManager


def test_resolved_path_outside_project_is_ignored(tmp_path, monkeypatch):
    project = tmp_path / "project"
    external = tmp_path / "external_vault"
    project.mkdir()
    external.mkdir()
    link = project / "content" / "docs"
    link.mkdir(parents=True)

    real_resolve = Path.resolve

    def patched_resolve(self, *args, **kwargs):
        if self == link:
            return external.resolve()
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", patched_resolve)

    manager = IgnoreManager(project)
    assert manager.is_ignored(link)
