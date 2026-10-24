"""Splitters on top of the belts running through them."""

from __future__ import annotations

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.drawers.sprite_drawer import SpriteDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity


class SplitterDrawer(SpriteDrawer):
    def applies(self, e: PlacedEntity) -> bool:
        return e.is_splitter

    def belt_key(self, e: PlacedEntity) -> str:
        """Straight belt of the splitter's tier ("fast-splitter" → "fast-transport-belt")."""
        return f"{e.name.removesuffix('splitter')}transport-belt/{e.direction.label}"

    def draw(self, canvas: Canvas, e: PlacedEntity, layout: Layout) -> bool:
        box = e.pixel_box(canvas.scale)
        splitter = self.sprites.fit(self.key(e, layout), box[2:], canvas.scale)
        if splitter is None:
            return False
        for x, y in e.tiles():
            self.paste(canvas, self.belt_key(e), canvas.tile_box(x, y), anchored=True)
        canvas.paste_fitted(splitter, box)
        return True
