import argparse

from rich.console import Console

from craft.context_builder import ContextBuilder
from craft.filter_manager import FilterManager
from craft.ignore_manager import IgnoreManager
from craft.utils import read_file_with_fallback


def _build_context_builder(project_path, encoding: str = "utf-8") -> ContextBuilder:
    filter_manager = FilterManager(
        config={
            "include_patterns": ["**/*"],
            "common_filters": [],
            "project_only_filters": [],
            "tree_only_filters": [],
        },
        output_path=project_path / "output.md",
    )
    ignore_manager = IgnoreManager(project_path)
    args = argparse.Namespace(
        headers_only=False,
        strip_comments=False,
        tree_only=False,
        output_format="human",
    )
    console = Console(stderr=True)
    return ContextBuilder(
        project_path=project_path,
        filter_manager=filter_manager,
        ignore_manager=ignore_manager,
        encoding=encoding,
        args=args,
        full_body_filters=[],
        console=console,
    )


def test_fallback_encoding_iso_8859_1(tmp_path):
    file_path = tmp_path / "latin1.txt"
    file_path.write_bytes("Voici un été français".encode("iso-8859-1"))

    content = read_file_with_fallback(file_path, "utf-8")

    assert "été français" in content


def test_fallback_replace_when_detection_fails(tmp_path, monkeypatch):
    file_path = tmp_path / "unknown.bin"
    file_path.write_bytes(b"\xff\xfe\xf8")

    class _NoMatch:
        @staticmethod
        def best():
            return None

    monkeypatch.setattr("charset_normalizer.from_path", lambda _: _NoMatch())

    content = read_file_with_fallback(file_path, "utf-8")

    assert "\ufffd" in content


def test_context_builder_process_files_preserves_accents(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    source_file = project / "notes.txt"
    source_file.write_bytes(
        "Voici un été français avec des accents: à, é, è, ç, ù.".encode("iso-8859-1")
    )

    builder = _build_context_builder(project, encoding="utf-8")
    files_data = builder._process_files([source_file])

    assert len(files_data) == 1
    assert files_data[0].path == "notes.txt"
    assert "été français" in files_data[0].content
