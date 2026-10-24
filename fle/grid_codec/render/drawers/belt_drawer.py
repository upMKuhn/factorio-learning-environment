"""Transport belts, curved where they turn."""

from __future__ import annotations

from fle.grid_codec.render.drawers.sprite_drawer import SpriteDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity


class BeltDrawer(SpriteDrawer):
    anchored = True

    def applies(self, e: PlacedEntity) -> bool:
        return e.is_transport_belt

    def key(self, e: PlacedEntity, layout: Layout) -> str:
        turn_from = layout.belts.curve(e)
        if turn_from is None:
            return super().key(e, layout)
        return f"{e.name}/{turn_from.label}_to_{e.direction.label}"
