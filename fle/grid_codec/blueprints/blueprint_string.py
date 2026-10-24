from __future__ import annotations

import base64
import json
import zlib
from typing import Iterator, Sequence

from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint


class BlueprintString:
    """An exported blueprint or blueprint book: a format version byte, then base64 of zlib-compressed JSON."""
    FORMAT_VERSION = "0"

    def __init__(self, text: str):
        self.text = text.strip()

    @classmethod
    def from_json(cls, obj: dict) -> BlueprintString:
        return cls(cls.FORMAT_VERSION + base64.b64encode(zlib.compress(json.dumps(obj).encode())).decode())

    def decode(self) -> dict:
        if not self.text.startswith(self.FORMAT_VERSION):
            raise ValueError(f"Unsupported blueprint string version {self.text[:1]!r}")
        return json.loads(zlib.decompress(base64.b64decode(self.text[1:])))

    def blueprints(self, tags: Sequence[str] = (), favorites: int = 0) -> Iterator[SourceBlueprint]:
        """Every blueprint in the string; books are exploded recursively and lend their version and label."""
        yield from self._explode(self.decode(), None, (), tuple(tags), favorites)

    def _explode(self, obj: dict, version: int | None, book: tuple[str, ...],
                 tags: tuple[str, ...], favorites: int) -> Iterator[SourceBlueprint]:
        if "blueprint" in obj:
            bp = obj["blueprint"]
            yield SourceBlueprint(
                label=bp.get("label", ""), entities=bp.get("entities", []),
                version=bp.get("version", version), book=" / ".join(b for b in book if b),
                tags=tags, favorites=favorites,
            )
        elif "blueprint_book" in obj:
            b = obj["blueprint_book"]
            for child in b.get("blueprints", []):
                yield from self._explode(child, b.get("version", version), (*book, b.get("label", "")), tags, favorites)
        # upgrade/deconstruction planners hold no entities
