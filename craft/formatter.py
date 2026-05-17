from html import escape
from pathlib import Path


def _markdown_language_for_path(relative_path):
    suffix = Path(relative_path).suffix.lower()
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.html': 'html',
        '.css': 'css',
        '.xml': 'xml',
        '.sql': 'sql',
        '.toml': 'toml',
        '.txt': 'text',
    }
    return mapping.get(suffix, 'text')


def _build_text_output(project_tree, extension_summary, files_data, tree_only=False):
    if tree_only:
        return project_tree + "\n\n" + extension_summary

    all_files_content = []
    for relative_path, content in files_data:
        header = f"\n{'='*80}\n--- FICHIER: {relative_path}\n{'='*80}\n\n"
        all_files_content.append(header + content)

    body_content_str = "".join(all_files_content)
    return (
        project_tree + "\n\n" + extension_summary + "\n\n"
        + "-" * 80 + "\nCONTENU DES FICHIERS\n" + "-" * 80 + "\n\n" + body_content_str
    )


def _build_xml_output(project_tree, extension_summary, files_data, tree_only=False):
    directory_block = f"{project_tree}\n\n{extension_summary}"
    parts = [
        "<repository>",
        "<directory_structure>",
        escape(directory_block),
        "</directory_structure>",
    ]

    if not tree_only:
        parts.append("<files>")
        for relative_path, content in files_data:
            parts.append(f'<file path="{escape(relative_path, quote=True)}">')
            parts.append(escape(content))
            parts.append("</file>")
        parts.append("</files>")

    parts.append("</repository>")
    return "\n".join(parts)


def _build_markdown_output(project_tree, extension_summary, files_data, tree_only=False):
    parts = [
        "# Project Context",
        "",
        "## Directory Structure",
        "```text",
        project_tree,
        "",
        extension_summary,
        "```",
    ]

    if not tree_only:
        parts.extend(["", "## Files", ""])
        for relative_path, content in files_data:
            language = _markdown_language_for_path(relative_path)
            parts.extend(
                [
                    f"### File: `{relative_path}`",
                    f"```{language}",
                    content,
                    "```",
                    "",
                ]
            )

    return "\n".join(parts).rstrip() + "\n"


def build_output(format_type, project_tree, extension_summary, files_data, tree_only=False):
    if format_type == 'text':
        return _build_text_output(project_tree, extension_summary, files_data, tree_only=tree_only)
    if format_type == 'xml':
        return _build_xml_output(project_tree, extension_summary, files_data, tree_only=tree_only)
    if format_type == 'markdown':
        return _build_markdown_output(project_tree, extension_summary, files_data, tree_only=tree_only)
    raise ValueError(f"Unsupported output format: {format_type}")
