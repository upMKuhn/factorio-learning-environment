"""Entities drawn by the first drawer that can draw them."""

from __future__ import annotations

from typing import Sequence

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.drawers.entity_drawer import EntityDrawer
from fle.grid_codec.render.layers.render_layer import RenderLayer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity


class EntitiesLayer(RenderLayer):
    """Each entity drawn by the first applicable drawer that succeeds (chain of responsibility)."""

    def __init__(self, drawers: Sequence[EntityDrawer]):
        self.drawers = list(drawers)

    def draw(self, canvas: Canvas, layout: Layout) -> None:
        for e in sorted(layout.entities, key=self._draw_order):
            for drawer in self.drawers:
                if drawer.applies(e) and drawer.draw(canvas, e, layout):
                    break

    @staticmethod
    def _draw_order(e: PlacedEntity) -> tuple:
        """Belts lie on the ground; everything else back to front."""
        on_ground = e.is_transport_belt or e.is_underground
        return not on_ground, e.y + e.h, e.x
