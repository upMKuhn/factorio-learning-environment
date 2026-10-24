from __future__ import annotations

import hashlib
import json
from collections import Counter
from functools import cached_property
from typing import Iterator

from pydantic import BaseModel, ConfigDict

from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint
from fle.grid_codec.grid import BoundingBox, EntitySpec


class Layout(BaseModel):
    """
    Normalized entities on integer tiles (top-left of each footprint), plus where they came from.

    Equality and hashing look at the entities only, not the source.
    """
    model_config = ConfigDict(frozen=True)

    entities: tuple[EntitySpec, ...]
    source: SourceBlueprint | None = None

    def __init__(self, entities: tuple[EntitySpec, ...] = (), source: SourceBlueprint | None = None):
        super().__init__(entities=entities, source=source)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Layout) and self.entities == other.entities

    def __hash__(self) -> int:
        return hash(self.entities)

    def __len__(self) -> int:
        return len(self.entities)

    def __iter__(self) -> Iterator[EntitySpec]:  # type: ignore[override]
        return iter(self.entities)

    def overlapping_tiles(self) -> set[tuple[int, int]]:
        """Tiles claimed by more than one entity."""
        claims = Counter(tile for e in self.entities for tile in e.tiles())
        return {tile for tile, n in claims.items() if n > 1}

    def entities_on(self, tiles: set[tuple[int, int]]) -> list[EntitySpec]:
        return [e for e in self.entities if tiles.intersection(e.tiles())]

    def bounds(self, padding: int = 1) -> BoundingBox:
        return BoundingBox.from_entities(self.entities, padding=padding)

    def translated(self, dx: int, dy: int) -> Layout:
        if dx == dy == 0:
            return self  # immutable, so no copy needed
        return Layout(tuple(EntitySpec(e.name, e.x + dx, e.y + dy, e.direction, e.meta_override, e.recipe, e.io_type)
                            for e in self.entities), self.source)

    def at_origin(self) -> Layout:
        """Shifted so the smallest x and y are 0."""
        if not self.entities:
            return self
        return self.translated(-min(e.x for e in self.entities), -min(e.y for e in self.entities))

    def content_key(self) -> str:
        """Identity of the placement, independent of position and entity order."""
        return self._content_key

    @cached_property
    def _content_key(self) -> str:
        rows = sorted(e.sort_key() for e in self.at_origin().entities)
        return hashlib.sha1(json.dumps(rows).encode()).hexdigest()

    def as_dicts(self) -> list[dict]:
        return [e.to_dict() for e in self.entities]
