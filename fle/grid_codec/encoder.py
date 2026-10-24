"""
Compatibility path; encoding lives in fle.grid_codec.grid (GridEncoder, Channel).

encode() keeps the old lenient behaviour (clips, overwrites, no recipe ids).
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from fle.grid_codec.grid import BoundingBox, EntitySpec, GridEncoder, Vocabulary

__all__ = ["BoundingBox", "EntitySpec", "encode", "stamp_carried_items"]


def encode(entities: list[EntitySpec], bounds: BoundingBox | None = None,
           grid_size: tuple[int, int] | None = None) -> np.ndarray:
    """(H, W, 7) uint16 grid over bounds (default: entities' bounding box with 1 tile padding)."""
    return GridEncoder(strict=False).encode(entities, bounds, grid_size=grid_size)


def stamp_carried_items(grid: np.ndarray, carries: Mapping[tuple[int, int], tuple],
                        item_index: Mapping[str, int]) -> None:
    """Write belt contents into channels 5-6; item_index maps item name → id."""
    GridEncoder(Vocabulary({}, item_index), strict=False).stamp_carried_items(grid, carries)
