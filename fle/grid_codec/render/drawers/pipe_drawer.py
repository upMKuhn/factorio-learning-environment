"""Pipes, shaped by which neighbours they connect to."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.drawers.sprite_drawer import SpriteDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity


class PipeDrawer(SpriteDrawer):
    """
    Pipes and pipes-to-ground, tile-aligned so connections line up. A pipe's
    variant is "pipe/NESW" with a 1 for each connected side: it connects to any
    fluid-handling neighbour, except a pipe-to-ground, which only connects on
    the side it faces.
    """

    anchored = True

    def applies(self, e: PlacedEntity) -> bool:
        return e.name in ("pipe", "pipe-to-ground")

    def key(self, e: PlacedEntity, layout: Layout) -> str:
        if e.name != "pipe":
            return super().key(e, layout)
        mask = "".join("1" if self._connects(e, side, layout) else "0" for side in Direction)
        return f"{e.name}/{mask}"

    @staticmethod
    def _connects(e: PlacedEntity, side: Direction, layout: Layout) -> bool:
        other = layout.step(e.x, e.y, side)
        if other is None or not other.is_fluid:
            return False
        if other.name == "pipe-to-ground":
            return other.direction == side.opposite
        return True
