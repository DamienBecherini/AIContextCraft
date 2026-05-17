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


def test_additional_ignore_files_are_applied(tmp_path):
    project = tmp_path / "multi_ignore_project"
    project.mkdir()
    (project / ".dockerignore").write_text("docker-data/\n", encoding="utf-8")
    (project / ".cursorignore").write_text("drafts/\n", encoding="utf-8")
    (project / ".npmignore").write_text("package-lock.json\n", encoding="utf-8")
    (project / "docker-data").mkdir()
    (project / "docker-data" / "out.txt").write_text("hidden", encoding="utf-8")
    (project / "drafts").mkdir()
    (project / "drafts" / "notes.md").write_text("private", encoding="utf-8")
    (project / "package-lock.json").write_text("{}", encoding="utf-8")
    (project / "src").mkdir()
    (project / "src" / "ok.py").write_text("print('ok')\n", encoding="utf-8")

    manager = IgnoreManager(project)
    assert manager.is_ignored(project / "docker-data" / "out.txt")
    assert manager.is_ignored(project / "drafts" / "notes.md")
    assert manager.is_ignored(project / "package-lock.json")
    assert not manager.is_ignored(project / "src" / "ok.py")


def test_ignore_report_tracks_detected_and_used_files(tmp_path):
    project = tmp_path / "ignore_report_project"
    project.mkdir()
    (project / ".gitignore").write_text("*.log\n", encoding="utf-8")
    (project / ".dockerignore").write_text("cache/\n", encoding="utf-8")
    (project / ".npmignore").write_text("", encoding="utf-8")
    (project / "cache").mkdir()
    (project / "cache" / "tmp.txt").write_text("tmp", encoding="utf-8")
    (project / "events.log").write_text("entry", encoding="utf-8")

    manager = IgnoreManager(project)
    report_before = {item["path"].name: item for item in manager.get_ignore_file_report()}
    assert report_before[".gitignore"]["used"] is False
    assert report_before[".dockerignore"]["used"] is False
    assert report_before[".npmignore"]["used"] is False

    assert manager.is_ignored(project / "events.log")
    assert manager.is_ignored(project / "cache" / "tmp.txt")

    report_after = {item["path"].name: item for item in manager.get_ignore_file_report()}
    assert report_after[".gitignore"]["used"] is True
    assert report_after[".dockerignore"]["used"] is True
    assert report_after[".npmignore"]["used"] is True
    assert report_after[".npmignore"]["active"] is False
