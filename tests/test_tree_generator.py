from pathlib import Path

import pathspec

from craft.tree_generator import (
    NO_EXTENSION_LABEL,
    SYMBOL_CONCATENATED,
    SYMBOL_INDICATIVE,
    _aggregate_dir_sizes,
    _collect_tree_paths,
    build_tree_legend,
    format_extension_summary,
    generate_tree,
)

TESTS_DIR = Path(__file__).parent
TREE_STATS_PROJECT = TESTS_DIR / 'test_projects' / 'tree_stats_project'


def _specs_for_tree_stats():
    include = pathspec.PathSpec.from_lines('gitignore', ['**/*'])
    common = ['.git/', 'build/', 'expected_output.txt', '*.log']
    tree_exclude = pathspec.PathSpec.from_lines('gitignore', common)
    return include, tree_exclude


def test_build_tree_legend_contains_symbols():
    legend = build_tree_legend()
    assert '●' in legend
    assert '○' in legend
    assert 'project_only_filters' in legend


def test_aggregate_dir_sizes_sums_descendants():
    directory = TREE_STATS_PROJECT
    include, tree_exclude = _specs_for_tree_stats()
    paths = _collect_tree_paths(directory, include, tree_exclude)
    main_py = directory / 'app' / 'main.py'
    readme = directory / 'README.md'
    skipped = directory / 'mixed' / 'skipped.txt'
    included = directory / 'mixed' / 'included.txt'
    app_dir = directory / 'app'
    mixed_dir = directory / 'mixed'
    concatenated = {main_py, included}

    file_metrics, dir_sizes = _aggregate_dir_sizes(directory, paths, concatenated)

    assert file_metrics[main_py][0] == file_metrics[main_py][1]
    assert file_metrics[readme][0] == 0
    assert file_metrics[readme][1] > 0
    assert file_metrics[skipped][0] == 0
    assert file_metrics[skipped][1] > 0
    assert dir_sizes[app_dir][0] == file_metrics[main_py][0]
    assert dir_sizes[mixed_dir][0] == file_metrics[included][0]
    assert dir_sizes[mixed_dir][1] == file_metrics[included][1] + file_metrics[skipped][1]


def test_generate_tree_marks_concatenated_and_indicative():
    directory = TREE_STATS_PROJECT
    include, tree_exclude = _specs_for_tree_stats()
    main_py = directory / 'app' / 'main.py'
    included = directory / 'mixed' / 'included.txt'
    concatenated = {main_py, included}

    tree, _ = generate_tree(directory, include, tree_exclude, concatenated)

    assert f"{SYMBOL_CONCATENATED} main.py" in tree
    assert f"{SYMBOL_INDICATIVE} README.md" in tree
    assert "README.md —" not in tree
    assert "mixed/" in tree and "(Real total:" in tree


def test_format_extension_summary_dual_totals(tmp_path):
    included = tmp_path / 'a.py'
    indicative = tmp_path / 'b.py'
    included.write_text('x = 1\n', encoding='utf-8')
    indicative.write_text('y = 2\n', encoding='utf-8')
    tree_files = {included, indicative}
    concatenated = {included}

    summary = format_extension_summary(tree_files, concatenated)

    assert "Extensions (concatenated files)" in summary
    assert ".py" in summary
    assert "(Real total:" in summary


def test_format_extension_summary_no_extension_label(tmp_path):
    no_ext = tmp_path / 'Makefile'
    no_ext.write_text('all:\n', encoding='utf-8')
    paths = {no_ext}
    summary = format_extension_summary(paths, paths)
    assert NO_EXTENSION_LABEL in summary
