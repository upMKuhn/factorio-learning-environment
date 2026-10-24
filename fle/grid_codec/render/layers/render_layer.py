"""The layer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fle.grid_codec.render.canvas import Canvas
    from fle.grid_codec.render.layout import Layout


class RenderLayer(ABC):
    """One stratum of a rendered image (tiles, sprites, an overlay...)."""

    @abstractmethod
    def draw(self, canvas: Canvas, layout: Layout) -> None: ...
