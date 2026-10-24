"""Compatibility path; decoding lives in fle.grid_codec.grid (GridDecoder)."""

from __future__ import annotations

import numpy as np

from fle.grid_codec.grid import BoundingBox, EntitySpec, GridDecoder

__all__ = ["decode"]


def decode(grid: np.ndarray, bounds: BoundingBox | None = None) -> list[EntitySpec]:
    """Entities in an (H, W, ≥4) grid, skipping unknown ids; recipes are not named."""
    return GridDecoder(strict=False).decode(grid, bounds)
