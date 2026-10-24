"""Synthetic grids and pixel checks for renderer tests."""

from __future__ import annotations

import numpy as np
from PIL import Image

from fle.grid_codec.schema import ENTITY_REGISTRY

N, E, S, W = 0, 4, 8, 12


def make_grid(h: int, w: int, entities: list[tuple], channels: int = 7) -> np.ndarray:
    """
    Stamp entities onto an empty grid.

    Each entity is (name, x, y[, direction[, recipe_id]]) with (x, y) its top-left tile.
    """
    grid = np.zeros((h, w, channels), dtype=np.uint16)
    for instance, (name, x, y, *rest) in enumerate(entities, start=1):
        direction = rest[0] if rest else 0
        recipe = rest[1] if len(rest) > 1 else 0
        info = ENTITY_REGISTRY.from_name(name)
        fw, fh = info.footprint(direction)
        grid[y:y + fh, x:x + fw, 0] = info.id
        grid[y:y + fh, x:x + fw, 1] = direction
        grid[y:y + fh, x:x + fw, 2] = int(info.meta)
        grid[y:y + fh, x:x + fw, 3] = instance
        if channels > 4:
            grid[y:y + fh, x:x + fw, 4] = recipe
    return grid


# Distinct opaque colours so tests can tell what was drawn where
SPRITE_RED = (200, 30, 30, 255)
ICON_COLORS = {
    "iron-gear-wheel": (10, 200, 10, 255),
    "wooden-chest": (10, 10, 200, 255),
    "inserter": (200, 200, 200, 255),
    "iron-plate": (90, 90, 250, 255),
    "copper-plate": (250, 120, 40, 255),
}


def pixels(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB")).astype(int)


def has_color(region: np.ndarray, color: tuple, tol: int = 12) -> bool:
    return bool((np.abs(region - np.array(color[:3])).max(axis=-1) <= tol).any())
