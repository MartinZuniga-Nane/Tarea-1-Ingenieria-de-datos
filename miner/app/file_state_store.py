from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

logger = logging.getLogger(__name__)


class JsonFileStore:
    """Simple JSON file store with atomic writes."""

    def __init__(self, path: Path, default_value: Any):
        self.path = path
        self.default_value = default_value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.write(self.default_value)

    def read(self) -> Any:
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read %s (%s). Resetting to default.", self.path, exc)
            self.write(self.default_value)
            return self.default_value

    def write(self, data: Any) -> None:
        # atomic write: write to temp file in same directory and rename
        with NamedTemporaryFile("w", delete=False, dir=self.path.parent, encoding="utf-8") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            temp_name = tmp.name
        Path(temp_name).replace(self.path)
