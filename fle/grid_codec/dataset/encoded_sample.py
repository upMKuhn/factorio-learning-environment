from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fle.grid_codec.blueprints import Layout
from fle.grid_codec.grid import BoundingBox, EntitySpec, GridEncoder


@dataclass(frozen=True)
class EncodedSample:
    """A layout, its grid and the world region the grid covers."""
    layout: Layout
    grid: np.ndarray
    bounds: BoundingBox

    @classmethod
    def encode(cls, layout: Layout, encoder: GridEncoder, padding: int = 1) -> EncodedSample:
        bounds = layout.bounds(padding=padding)
        return cls(layout, encoder.encode(list(layout.entities), bounds), bounds)

    def entities_in_grid(self) -> list[EntitySpec]:
        """The layout's entities in grid coordinates (column, row)."""
        return list(self.layout.translated(-self.bounds.x, -self.bounds.y).entities)
