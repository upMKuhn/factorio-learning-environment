"""A grid parsed into placed entities."""

from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.placed_entity import PlacedEntity
from fle.grid_codec.schema import ENTITY_REGISTRY

if TYPE_CHECKING:
    from fle.grid_codec.render.belt_connections import BeltConnections
    from fle.grid_codec.render.underground_pairing import UndergroundPairing


class Layout:
    """
    The entities of a (H, W, C) grid with tile lookup.

    Tiles of one multi-tile entity share an instance id (channel 3); tiles with
    instance 0 are single-tile entities. Unknown type ids are skipped.
    """

    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape[:2]
        self.entities: list[PlacedEntity] = self._parse(grid)
        self._at = {tile: e for e in self.entities for tile in e.tiles()}

    @staticmethod
    def _parse(grid: np.ndarray) -> list[PlacedEntity]:
        groups: dict[tuple, list[tuple[int, int]]] = defaultdict(list)
        for y, x in zip(*np.nonzero(grid[:, :, 0])):
            instance = int(grid[y, x, 3])
            groups[("i", instance) if instance else ("t", x, y)].append((int(x), int(y)))

        entities = []
        for cells in groups.values():
            x0, y0 = min(c[0] for c in cells), min(c[1] for c in cells)
            x1, y1 = max(c[0] for c in cells), max(c[1] for c in cells)
            cx, cy = cells[0]
            type_id = int(grid[cy, cx, 0])
            if not ENTITY_REGISTRY.has_id(type_id):
                continue
            entities.append(PlacedEntity(
                info=ENTITY_REGISTRY.from_id(type_id),
                x=x0, y=y0, w=x1 - x0 + 1, h=y1 - y0 + 1,
                raw_direction=int(grid[cy, cx, 1]),
                meta=int(grid[cy, cx, 2]),
                recipe_id=int(grid[cy, cx, 4]) if grid.shape[2] > 4 else 0,
            ))
        entities.sort(key=lambda e: (e.y, e.x))
        return entities

    @cached_property
    def pairing(self) -> UndergroundPairing:
        from fle.grid_codec.render.underground_pairing import UndergroundPairing
        return UndergroundPairing(self)

    @cached_property
    def belts(self) -> BeltConnections:
        from fle.grid_codec.render.belt_connections import BeltConnections
        return BeltConnections(self, self.pairing)

    def at(self, x: int, y: int) -> PlacedEntity | None:
        return self._at.get((x, y))

    def step(self, x: int, y: int, direction: Direction) -> PlacedEntity | None:
        """The entity one tile from (x, y) in direction."""
        dx, dy = direction.delta
        return self._at.get((x + dx, y + dy))

    def lane_items(self, x: int, y: int) -> tuple[int, int]:
        """Item ids on the left and right belt lane of a tile (channels 5-6), 0 if none."""
        if self.grid.shape[2] < 7:
            return 0, 0
        return int(self.grid[y, x, 5]), int(self.grid[y, x, 6])
