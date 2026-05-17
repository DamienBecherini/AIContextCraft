from pathlib import Path

import pytest

from craft.ignore_manager import IgnoreManager

TESTS_DIR = Path(__file__).parent
NESTED_PROJECT = TESTS_DIR / "test_projects" / "nested_ignore_project"


@pytest.fixture
def nested_project():
    return NESTED_PROJECT.resolve()


def test_security_blocks_env_local(nested_project):
    manager = IgnoreManager(nested_project)
    assert manager.is_ignored(nested_project / ".env.local")


def test_nested_gitignore_logs_and_node_modules(nested_project):
    manager = IgnoreManager(nested_project)
    assert manager.is_ignored(nested_project / "logs" / "secret.log")
    assert manager.is_ignored(nested_project / "frontend" / "node_modules" / "pkg" / "index.js")
    assert not manager.is_ignored(nested_project / "frontend" / "src" / "ok.js")


def test_no_ignore_skips_gitignore_but_not_security(nested_project):
    manager = IgnoreManager(nested_project, disabled=True)
    assert not manager.is_ignored(nested_project / "logs" / "secret.log")
    assert not manager.is_ignored(nested_project / "frontend" / "node_modules" / "pkg" / "index.js")
    assert manager.is_ignored(nested_project / ".env.local")
