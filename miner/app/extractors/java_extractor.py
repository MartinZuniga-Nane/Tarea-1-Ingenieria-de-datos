from __future__ import annotations

from typing import List

from tree_sitter import Language, Node, Parser
import tree_sitter_java as tsjava


class JavaExtractor:
    """Extract method names from Java code via tree-sitter parser."""

    def __init__(self) -> None:
        self.parser = Parser()
        language = Language(tsjava.language())
        # Support tree-sitter versions that use either property assignment or set_language.
        if hasattr(self.parser, "language"):
            self.parser.language = language
        else:
            self.parser.set_language(language)

    def extract_method_names(self, source_code: str) -> List[str]:
        tree = self.parser.parse(source_code.encode("utf-8", errors="ignore"))
        names: list[str] = []

        def visit(node: Node) -> None:
            if node.type == "method_declaration":
                for child in node.children:
                    if child.type == "identifier":
                        text = source_code[child.start_byte : child.end_byte]
                        names.append(text)
                        break
            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return names
