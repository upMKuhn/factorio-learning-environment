"""
Decode a 4-channel 2D grid back into a list of EntitySpec.

Handles multi-tile entities by grouping pixels with the same instance ID
(channel 3) and computing the top-left origin.
"""

from __future__ import annotations

import numpy as np

from fle.grid_codec.encoder import BoundingBox, EntitySpec
from fle.grid_codec.schema import ENTITY_REGISTRY


def decode(
    grid: np.ndarray,
    bounds: BoundingBox | None = None,
) -> list[EntitySpec]:
    """
    Decode a 4-channel grid into entity specs.

    Args:
        grid: (H, W, 4) uint8 numpy array.
        bounds: World-space offset. If None, grid coords = world coords with origin (0,0).

    Returns:
        List of EntitySpec with world-space positions.
    """
    if grid.ndim != 3 or grid.shape[2] != 4:
        raise ValueError(f"Expected (H, W, 4) grid, got {grid.shape}")

    ox = bounds.x if bounds else 0
    oy = bounds.y if bounds else 0

    h, w = grid.shape[:2]
    entities: list[EntitySpec] = []
    seen_instances: set[int] = set()

    for gy in range(h):
        for gx in range(w):
            type_id = int(grid[gy, gx, 0])
            if type_id == 0:
                continue

            instance_id = int(grid[gy, gx, 3])

            # Multi-tile: only process first pixel per instance
            if instance_id > 0:
                if instance_id in seen_instances:
                    continue
                seen_instances.add(instance_id)

            direction = int(grid[gy, gx, 1])

            if not ENTITY_REGISTRY.has_id(type_id):
                continue

            info = ENTITY_REGISTRY.from_id(type_id)

            # For multi-tile entities, this pixel is the top-left
            # (encoder fills top-to-bottom, left-to-right, and we scan the same way)
            world_x = gx + ox
            world_y = gy + oy

            entities.append(EntitySpec(
                name=info.name,
                x=world_x,
                y=world_y,
                direction=direction,
            ))

    return entities
