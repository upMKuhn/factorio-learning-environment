"""
Encode a list of entity specs into a 4-channel 2D grid (numpy array).

Grid shape: (H, W, 4) dtype uint8
  Channel 0 (R): entity type ID
  Channel 1 (G): direction (0-15)
  Channel 2 (B): metadata bitmask
  Channel 3 (A): instance ID for multi-tile grouping (0 = single-tile or empty)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fle.grid_codec.schema import ENTITY_REGISTRY, EntityInfo, Meta


@dataclass
class EntitySpec:
    """Lightweight entity placement descriptor."""
    name: str               # prototype name, e.g. "stone-furnace"
    x: int                  # top-left tile x (grid column)
    y: int                  # top-left tile y (grid row)
    direction: int = 0      # 0-15 (FLE Direction enum)
    meta_override: int | None = None  # override metadata byte, or None for default


@dataclass
class BoundingBox:
    """Grid bounds in tile coordinates."""
    x: int          # top-left x
    y: int          # top-left y
    width: int      # tiles wide
    height: int     # tiles tall

    @classmethod
    def from_entities(cls, entities: list[EntitySpec], padding: int = 1) -> BoundingBox:
        """Compute minimal bounding box around a set of entities."""
        if not entities:
            return cls(0, 0, 64, 64)

        min_x = min(e.x for e in entities)
        min_y = min(e.y for e in entities)
        max_x = max_y = 0

        for e in entities:
            info = ENTITY_REGISTRY.from_name(e.name)
            max_x = max(max_x, e.x + info.width)
            max_y = max(max_y, e.y + info.height)

        return cls(
            x=min_x - padding,
            y=min_y - padding,
            width=max_x - min_x + 2 * padding,
            height=max_y - min_y + 2 * padding,
        )


def encode(
    entities: list[EntitySpec],
    bounds: BoundingBox | None = None,
    grid_size: tuple[int, int] | None = None,
) -> np.ndarray:
    """
    Encode entities into a 4-channel grid.

    Args:
        entities: List of entity placements.
        bounds: Bounding box defining the world region to encode.
                If None, computed from entities.
        grid_size: Optional (height, width) to force output size.
                   If None, uses bounds dimensions.

    Returns:
        (H, W, 4) uint8 numpy array.
    """
    if bounds is None:
        bounds = BoundingBox.from_entities(entities)

    h = grid_size[0] if grid_size else bounds.height
    w = grid_size[1] if grid_size else bounds.width

    grid = np.zeros((h, w, 4), dtype=np.uint8)

    for instance_id, entity in enumerate(entities, start=1):
        info: EntityInfo = ENTITY_REGISTRY.from_name(entity.name)
        meta = entity.meta_override if entity.meta_override is not None else int(info.meta)

        # Clamp instance_id to uint8
        inst = min(instance_id, 255)

        # Fill all tiles occupied by this entity
        for dy in range(info.height):
            for dx in range(info.width):
                gx = entity.x + dx - bounds.x
                gy = entity.y + dy - bounds.y

                if 0 <= gx < w and 0 <= gy < h:
                    grid[gy, gx, 0] = info.id           # entity type
                    grid[gy, gx, 1] = entity.direction   # direction
                    grid[gy, gx, 2] = meta               # metadata
                    # Multi-tile: set instance ID so decoder can group tiles
                    grid[gy, gx, 3] = inst if (info.width > 1 or info.height > 1) else 0

    return grid
