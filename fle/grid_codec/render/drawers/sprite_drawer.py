"""Entities drawn with their in-game sprite."""

from __future__ import annotations

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.drawers.entity_drawer import EntityDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.placed_entity import PlacedEntity
from fle.grid_codec.render.sprite_source import SpriteSource


class SpriteDrawer(EntityDrawer):
    """
    The entity's cached sprite for its direction, fitted inside its footprint so
    it never spills onto neighbours. Subclasses pick other variants.
    Anchored drawers (ground pieces such as belts) keep the sprite's alignment
    with the tile grid and clip it to the footprint instead.
    """

    anchored = False

    def __init__(self, sprites: SpriteSource):
        self.sprites = sprites

    def applies(self, e: PlacedEntity) -> bool:
        return True

    def key(self, e: PlacedEntity, layout: Layout) -> str:
        return f"{e.name}/{e.direction.label}"

    def draw(self, canvas: Canvas, e: PlacedEntity, layout: Layout) -> bool:
        return self.paste(canvas, self.key(e, layout), e.pixel_box(canvas.scale))

    def paste(self, canvas: Canvas, key: str, box: tuple[int, int, int, int], anchored: bool | None = None) -> bool:
        if self.anchored if anchored is None else anchored:
            sprite = self.sprites.load(key, canvas.scale)
            if sprite is None:
                return False
            canvas.paste_anchored(*sprite, box)
            return True
        img = self.sprites.fit(key, box[2:], canvas.scale)
        if img is None:
            return False
        canvas.paste_fitted(img, box)
        return True
