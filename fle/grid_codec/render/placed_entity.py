"""One entity as it sits on the grid."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, SkipValidation

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.schema import EntityInfo, Meta


class PlacedEntity(BaseModel):
    """An entity on the grid: its type, footprint (top-left tile, size in tiles) and settings."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    info: SkipValidation[EntityInfo]   # owned by the schema registry; passed through as is
    x: int
    y: int
    w: int
    h: int
    raw_direction: int     # grid channel 1, 16-way
    meta: int              # grid channel 2
    recipe_id: int = 0     # grid channel 4, 0 if absent

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def direction(self) -> Direction:
        return Direction.snap(self.raw_direction)

    @property
    def is_inserter(self) -> bool:
        return bool(self.info.meta & Meta.IS_INSERTER)

    @property
    def is_transport_belt(self) -> bool:
        return self.name.endswith("transport-belt")

    @property
    def is_underground(self) -> bool:
        return self.name.endswith("underground-belt")

    @property
    def is_splitter(self) -> bool:
        return self.name.endswith("splitter")

    @property
    def is_belt(self) -> bool:
        """Anything that carries items on lanes: belts, undergrounds, splitters."""
        return self.is_transport_belt or self.is_underground or self.is_splitter

    @property
    def is_fluid(self) -> bool:
        return bool(self.meta & Meta.IS_FLUID)

    @property
    def has_recipe_slot(self) -> bool:
        return bool(self.info.meta & Meta.HAS_RECIPE)

    @property
    def is_directional(self) -> bool:
        """Whether its direction matters visually even when it is north (0)."""
        return self.raw_direction != 0 or self.is_inserter or self.is_belt

    @property
    def pickup_side(self) -> Direction:
        """Inserters' grid direction points at the tile they pick up from."""
        return self.direction

    @property
    def facing(self) -> Direction:
        """Where the entity visibly points: belt flow, or the drop side for inserters."""
        return self.direction.opposite if self.is_inserter else self.direction

    def tiles(self) -> list[tuple[int, int]]:
        return [(self.x + dx, self.y + dy) for dy in range(self.h) for dx in range(self.w)]

    def pixel_box(self, scale: int) -> tuple[int, int, int, int]:
        """(x0, y0, width, height) in pixels."""
        return self.x * scale, self.y * scale, self.w * scale, self.h * scale
