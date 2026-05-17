import ast
import fnmatch
import logging
from pathlib import Path


def strip_comments_from_code(content, file_path):
    """
    Supprime les commentaires et les docstrings d'un fichier de code.
    Utilise 'ast' pour une suppression robuste en Python.
    """
    file_ext = Path(file_path).suffix

    if file_ext == '.py':
        try:
            tree = ast.parse(content)

            class DocstringRemover(ast.NodeTransformer):
                def _remove_docstring(self, node):
                    if not node.body:
                        return
                    first_node = node.body[0]
                    if isinstance(first_node, ast.Expr):
                        if isinstance(getattr(first_node.value, 'value', None), str):
                            node.body = node.body[1:]
                        elif isinstance(first_node.value, ast.Str):
                            node.body = node.body[1:]

                def visit_Module(self, node):
                    self._remove_docstring(node)
                    self.generic_visit(node)
                    return node

                def visit_FunctionDef(self, node):
                    self._remove_docstring(node)
                    self.generic_visit(node)
                    return node

                visit_AsyncFunctionDef = visit_FunctionDef
                visit_ClassDef = visit_FunctionDef

            transformer = DocstringRemover()
            new_tree = transformer.visit(tree)
            ast.fix_missing_locations(new_tree)
            return ast.unparse(new_tree)

        except (SyntaxError, Exception):
            logging.warning(
                f"  -> AVERTISSEMENT: Impossible de parser/stripper les commentaires de {file_path}. "
                "Fichier inclus tel quel."
            )
            return content

    elif file_ext in ('.sh', '.bash') or 'Dockerfile' in Path(file_path).name:
        return "\n".join([line for line in content.splitlines() if not line.strip().startswith('#')])

    return content


def get_python_headers(content, full_body_filters_patterns):
    try:
        tree = ast.parse(content)
    except Exception as e:
        return f"# ERREUR: Impossible de parser le fichier Python: {e}\n{content}"
    output_lines = []

    def should_keep_full_body(name):
        return any(fnmatch.fnmatch(name, pattern) for pattern in full_body_filters_patterns)

    def format_signature(node, indent=""):
        lines = [f"{indent}@{ast.unparse(decorator)}" for decorator in getattr(node, 'decorator_list', [])]
        prefix = indent
        if isinstance(node, ast.AsyncFunctionDef):
            prefix += "async def"
        elif isinstance(node, ast.FunctionDef):
            prefix += "def"
        elif isinstance(node, ast.ClassDef):
            prefix += "class"
        name = node.name
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ast.unparse(node.args)
            return_annotation = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            lines.append(f"{prefix} {name}({args}){return_annotation}:")
        elif isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            keywords = [f"{k.arg}={ast.unparse(k.value)}" for k in node.keywords]
            lines.append(f"{prefix} {name}({', '.join(bases + keywords)}):")
        return "\n".join(lines)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if should_keep_full_body(node.name):
                output_lines.append(ast.get_source_segment(content, node))
                continue
            output_lines.append(format_signature(node))
            docstring = ast.get_docstring(node)
            if docstring:
                output_lines.append(f'    """{docstring}"""')
            if isinstance(node, ast.ClassDef):
                has_methods = False
                for method_node in node.body:
                    if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        has_methods = True
                        output_lines.append("\n" + format_signature(method_node, indent="    "))
                        method_docstring = ast.get_docstring(method_node)
                        if method_docstring:
                            output_lines.append(f'        """{method_docstring}"""')
                        output_lines.append("        pass")
                if not docstring and not has_methods:
                    output_lines.append("    pass")
            else:
                output_lines.append("    pass")
            output_lines.append("")
    return "\n".join(output_lines)
