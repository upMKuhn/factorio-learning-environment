"""A renderer built from a stack of layers."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from PIL import Image

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.layers.render_layer import RenderLayer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.palette import PALETTE
from fle.grid_codec.render.renderer import Renderer


class LayeredRenderer(Renderer):
    """
    Draws each layer on its own transparent sheet and composites the sheets
    bottom to top, so translucent overlays blend with what is underneath.
    """

    def __init__(self, scale: int, layers: Sequence[RenderLayer],
                 background: tuple[int, int, int] = PALETTE.empty):
        self.scale = scale
        self.layers = list(layers)
        self.background = background

    def with_overlays(self, overlays: Sequence[RenderLayer]) -> LayeredRenderer:
        """A renderer drawing this one's layers, then the overlays."""
        return LayeredRenderer(self.scale, [*self.layers, *overlays], self.background)

    def render(self, grid: np.ndarray) -> Image.Image:
        layout = Layout(grid)
        canvas = Canvas(layout.width, layout.height, self.scale, self.background)
        for layer in self.layers:
            sheet = canvas.sheet()
            layer.draw(sheet, layout)
            canvas.composite(sheet)
        return canvas.rgb()
