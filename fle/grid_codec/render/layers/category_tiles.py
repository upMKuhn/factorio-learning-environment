"""Machine-mode tiles: one category colour per tile, plus direction arrows."""

from __future__ import annotations

import numpy as np

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.layers.render_layer import RenderLayer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.palette import PALETTE, Palette
from fle.grid_codec.schema import ENTITY_REGISTRY


class CategoryTilesLayer(RenderLayer):
    """
    Each occupied tile in its entity's category colour, shaded by direction,
    with a white arrow on directional tiles. Works per tile, so it also shows
    malformed grids (e.g. model output) faithfully.
    """

    def __init__(self, palette: Palette = PALETTE):
        self.palette = palette

    def draw(self, canvas: Canvas, layout: Layout) -> None:
        grid, s = layout.grid, canvas.scale
        for gy, gx in zip(*np.nonzero(grid[:, :, 0])):
            type_id, direction = int(grid[gy, gx, 0]), int(grid[gy, gx, 1])
            x0, y0 = int(gx) * s, int(gy) * s
            canvas.draw.rectangle([x0, y0, x0 + s - 1, y0 + s - 1],
                                  fill=self._color(type_id, direction), outline=self.palette.grid_line)
            if direction:
                canvas.arrow((x0, y0, s, s), Direction.snap(direction), (255, 255, 255))

    def _color(self, type_id: int, direction: int) -> tuple[int, int, int]:
        if not ENTITY_REGISTRY.has_id(type_id):
            return self.palette.unknown
        base = self.palette.category_color(ENTITY_REGISTRY.from_id(type_id).category)
        shift = (direction // 4 % 4) * 10 - 15
        return tuple(max(0, min(255, c + shift)) for c in base)
