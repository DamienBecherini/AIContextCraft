import argparse
import logging
import os
import sys
from pathlib import Path

from rich.progress import track

from craft.file_processor import get_python_headers, strip_comments_from_code
from craft.filter_manager import FilterManager
from craft.ignore_manager import IgnoreManager
from craft.tree_generator import format_extension_summary, generate_tree
from craft.types import ProcessedFile
from craft.utils import read_file_with_fallback


class ContextBuilder:
    def __init__(
        self,
        project_path: Path,
        filter_manager: FilterManager,
        ignore_manager: IgnoreManager,
        encoding: str,
        args: argparse.Namespace,
        full_body_filters: list[str],
    ) -> None:
        self.project_path = project_path
        self.filter_manager = filter_manager
        self.ignore_manager = ignore_manager
        self.encoding = encoding
        self.args = args
        self.full_body_filters = full_body_filters

    def _gather_files(self) -> list[Path]:
        logging.info("Recherche optimisée des fichiers (avec élagage des dossiers exclus)...")
        final_file_list: list[Path] = []
        for root, dirs, files in os.walk(self.project_path, topdown=True):
            excluded_dirs = []
            for d in dirs:
                dir_path = Path(root) / d
                dir_path_str = str(dir_path.relative_to(self.project_path)).replace('\\', '/')
                if self.ignore_manager.is_ignored(dir_path):
                    excluded_dirs.append(d)
                elif self.filter_manager.is_project_excluded(dir_path_str, is_dir=True):
                    excluded_dirs.append(d)

            for d in excluded_dirs:
                dirs.remove(d)

            for filename in files:
                file_path = Path(root) / filename
                relative_path_str = str(file_path.relative_to(self.project_path)).replace('\\', '/')

                if self.ignore_manager.is_ignored(file_path):
                    continue
                if self.filter_manager.is_included(
                    relative_path_str
                ) and not self.filter_manager.is_project_excluded(relative_path_str):
                    final_file_list.append(file_path)

        final_file_list.sort()
        return final_file_list

    def _process_files(self, final_file_list: list[Path]) -> list[ProcessedFile]:
        files_data: list[ProcessedFile] = []
        file_iterator = track(
            final_file_list,
            description="Traitement des fichiers...",
            disable=not sys.stdout.isatty(),
        )
        for file_path in file_iterator:
            relative_path_str = str(file_path.relative_to(self.project_path)).replace('\\', '/')
            try:
                content = read_file_with_fallback(file_path, self.encoding)

                if self.args.headers_only and file_path.suffix == '.py':
                    content = get_python_headers(content, self.full_body_filters)
                elif self.args.strip_comments:
                    content = strip_comments_from_code(content, file_path)

                files_data.append(ProcessedFile(path=relative_path_str, content=content))
            except IOError as e:
                logging.error(f"  -> ERREUR: Impossible de lire {relative_path_str}. Erreur: {e}")
        return files_data

    def build(self) -> tuple[str, str, list[ProcessedFile]]:
        final_file_list = self._gather_files()
        concatenated_paths = set(final_file_list)

        logging.info("Génération de l'arbre du projet...")
        project_tree, tree_paths = generate_tree(
            self.project_path,
            self.filter_manager,
            concatenated_paths,
            ignore_manager=self.ignore_manager,
        )
        tree_file_paths = {p for p in tree_paths if p.is_file()}
        extension_summary = format_extension_summary(tree_file_paths, concatenated_paths)
        logging.info(f"{len(final_file_list)} fichiers finaux trouvés après filtrage optimisé.")
        logging.info("--- LISTE DES FICHIERS À TRAITER ---")
        for p in final_file_list:
            logging.info(f"  [INCLUS] {str(p.relative_to(self.project_path)).replace('\\', '/')}")
        logging.info("--- FIN DE LA LISTE ---")

        if self.args.tree_only:
            return project_tree, extension_summary, []

        files_data = self._process_files(final_file_list)
        return project_tree, extension_summary, files_data
