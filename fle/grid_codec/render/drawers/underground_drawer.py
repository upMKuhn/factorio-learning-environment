"""Underground belts: entrance or exit hood, so pairs face each other."""

from __future__ import annotations

from fle.grid_codec.render.drawers.sprite_drawer import SpriteDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity


class UndergroundDrawer(SpriteDrawer):
    anchored = True

    def applies(self, e: PlacedEntity) -> bool:
        return e.is_underground

    def key(self, e: PlacedEntity, layout: Layout) -> str:
        end = "out" if layout.pairing.is_exit(e) else "in"
        return f"{super().key(e, layout)}-{end}"
