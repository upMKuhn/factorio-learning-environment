from __future__ import annotations

from functools import cached_property

import numpy as np
from pydantic import BaseModel, ConfigDict

from fle.grid_codec.blueprints import Layout
from fle.grid_codec.grid import BoundingBox, EntitySpec, GridEncoder


class EncodedSample(BaseModel):
    """A layout, its grid and the world region the grid covers; the grid array itself stays writable."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    layout: Layout
    grid: np.ndarray
    bounds: BoundingBox

    @classmethod
    def encode(cls, layout: Layout, encoder: GridEncoder, padding: int = 1) -> EncodedSample:
        bounds = layout.bounds(padding=padding)
        return cls(layout=layout, grid=encoder.encode(list(layout.entities), bounds), bounds=bounds)

    def entities_in_grid(self) -> list[EntitySpec]:
        """The layout's entities in grid coordinates (column, row)."""
        return list(self._entities_in_grid)

    @cached_property
    def _entities_in_grid(self) -> tuple[EntitySpec, ...]:
        # Layout and bounds are frozen, so this is computed once per sample (flow inference and checks share it).
        return self.layout.translated(-self.bounds.x, -self.bounds.y).entities
