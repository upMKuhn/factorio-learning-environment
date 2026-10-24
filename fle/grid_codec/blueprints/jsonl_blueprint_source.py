from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from fle.grid_codec.blueprints.blueprint_source import BlueprintSource
from fle.grid_codec.blueprints.blueprint_string import BlueprintString
from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint

_STRING_KEY = '"blueprint_string": "'


class JsonlBlueprintSource(BlueprintSource):
    """
    Community blueprints, one JSON row per export: {"blueprint_string", "tags", "favorites", ...}.

    Books are exploded and repeated export strings read once. The rows' own
    "entities" lists are not used: they are truncated, uncentred and missing
    pre-2.0 names.
    """

    def __init__(self, path: str | Path, min_entities: int = 0, max_entities: int | None = None):
        super().__init__(min_entities, max_entities)
        self.path = Path(path)

    def _read(self) -> Iterator[SourceBlueprint]:
        seen: set[str] = set()
        with open(self.path) as f:
            for line in f:
                self.stats["source rows"] += 1
                if self._peek_string(line) in seen:
                    self.stats["duplicate export strings"] += 1
                    continue
                row = json.loads(line)
                text = row["blueprint_string"]
                if text in seen:
                    self.stats["duplicate export strings"] += 1
                    continue
                seen.add(text)
                self.stats["distinct export strings"] += 1
                yield from BlueprintString(text).blueprints(row.get("tags", ()), row.get("favorites", 0))

    @staticmethod
    def _peek_string(line: str) -> str | None:
        """The row's export string without parsing the (large) row, or None if it is JSON-escaped."""
        start = line.find(_STRING_KEY)
        if start < 0:
            return None
        start += len(_STRING_KEY)
        text = line[start:line.find('"', start)]
        return None if "\\" in text else text

    def __repr__(self) -> str:
        return f"JsonlBlueprintSource({str(self.path)!r})"
