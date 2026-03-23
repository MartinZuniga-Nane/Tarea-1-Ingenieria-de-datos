from __future__ import annotations

import ast
from typing import List


class PythonExtractor:
    """Extract function names using Python AST (includes class methods and async defs)."""

    def extract_function_names(self, source_code: str) -> List[str]:
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return []

        names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.append(node.name)
        return names
