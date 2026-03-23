from __future__ import annotations

import re

# Handles snake_case, camelCase, PascalCase, acronyms (XML), and suffixes like v2.
_TOKEN_PATTERN = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\d|$)|[A-Z]?[a-z]+\d*|\d+|[A-Z]+")



def split_identifier(identifier: str) -> list[str]:
    parts: list[str] = []
    for chunk in identifier.replace("-", "_").split("_"):
        if not chunk:
            continue
        parts.extend(m.group(0).lower() for m in _TOKEN_PATTERN.finditer(chunk))
    return parts
