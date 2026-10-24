"""Machine mode: category-coloured tiles with direction arrows."""

from __future__ import annotations

from fle.grid_codec.render.layered_renderer import LayeredRenderer
from fle.grid_codec.render.layers.category_tiles import CategoryTilesLayer


class MachineRenderer(LayeredRenderer):
    """Fast and dependency-free; for ML visualization and bulk prerendering."""

    def __init__(self, scale: int = 8):
        super().__init__(scale, [CategoryTilesLayer()])
