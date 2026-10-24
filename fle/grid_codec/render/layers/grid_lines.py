"""Tile grid lines."""

from __future__ import annotations

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.layers.render_layer import RenderLayer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.palette import PALETTE


class GridLinesLayer(RenderLayer):
    def __init__(self, color: tuple[int, int, int] = PALETTE.grid_line):
        self.color = color

    def draw(self, canvas: Canvas, layout: Layout) -> None:
        s, w, h = canvas.scale, layout.width, layout.height
        for gy in range(h + 1):
            canvas.draw.line([(0, gy * s), (w * s, gy * s)], fill=self.color)
        for gx in range(w + 1):
            canvas.draw.line([(gx * s, 0), (gx * s, h * s)], fill=self.color)
