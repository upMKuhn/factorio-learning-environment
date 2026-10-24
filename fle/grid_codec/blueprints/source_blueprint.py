from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceBlueprint:
    """One blueprint as read from a source, entities still in Factorio's (or synthetic grid) form."""
    label: str
    entities: list[dict]
    version: int | None = None     # packed game version; None for synthetic data, treated as 2.x
    book: str = ""                 # enclosing book labels, "outer / inner"
    tags: tuple[str, ...] = field(default=())
    favorites: int = 0

    @property
    def major_version(self) -> int:
        """Factorio packs major.minor.patch.build into 16 bits each."""
        return 2 if self.version is None else self.version >> 48

    @property
    def entity_count(self) -> int:
        return len(self.entities)

    def content_key(self) -> str:
        """Identity of the raw placement (ignores order, entity numbers, wires, labels)."""
        rows = sorted(
            (e["name"], *self._position(e), e.get("direction", 0), e.get("recipe") or "", e.get("type") or "")
            for e in self.entities
        )
        return hashlib.sha1(json.dumps(rows).encode()).hexdigest()

    @staticmethod
    def _position(e: dict) -> tuple:
        return (e["position"]["x"], e["position"]["y"]) if "position" in e else (e["x"], e["y"])

    @classmethod
    def from_dict(cls, d: dict) -> SourceBlueprint:
        """From the legacy dict form ({label, entities, version?, book?, tags?, favorites?})."""
        return cls(label=d.get("label", ""), entities=d.get("entities", []), version=d.get("version"),
                   book=d.get("book", ""), tags=tuple(d.get("tags", ())), favorites=d.get("favorites", 0))

    def to_dict(self) -> dict:
        return {"label": self.label, "book": self.book, "tags": list(self.tags), "favorites": self.favorites,
                "version": self.version, "entity_count": self.entity_count, "entities": self.entities}
