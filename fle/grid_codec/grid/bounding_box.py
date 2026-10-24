from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field

from fle.grid_codec.grid.entity_spec import EntitySpec


class BoundingBox(BaseModel):
    """A world region in tiles: top-left corner and size."""
    model_config = ConfigDict(frozen=True)

    x: int
    y: int
    width: int = Field(ge=0)
    height: int = Field(ge=0)

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x=x, y=y, width=width, height=height)

    @classmethod
    def from_entities(cls, entities: Sequence[EntitySpec], padding: int = 1) -> BoundingBox:
        """Smallest box around the entities' rotated footprints, plus padding on every side."""
        if not entities:
            return cls(0, 0, 64, 64)
        footprints = [e.footprint for e in entities]
        min_x = min(e.x for e in entities)
        min_y = min(e.y for e in entities)
        max_x = max(e.x + f.width for e, f in zip(entities, footprints))
        max_y = max(e.y + f.height for e, f in zip(entities, footprints))
        return cls(min_x - padding, min_y - padding,
                   max_x - min_x + 2 * padding, max_y - min_y + 2 * padding)

    @property
    def shape(self) -> tuple[int, int]:
        """(height, width), numpy order."""
        return self.height, self.width
