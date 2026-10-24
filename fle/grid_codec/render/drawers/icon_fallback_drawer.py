"""Entities without a sprite: upright icon plus a direction arrow."""

from __future__ import annotations

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.drawers.entity_drawer import EntityDrawer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.palette import PALETTE, Palette
from fle.grid_codec.render.placed_entity import PlacedEntity
from fle.grid_codec.render.sprite_source import SpriteSource


class IconFallbackDrawer(EntityDrawer):
    """
    The entity's item icon (or a labelled category box if it has none), with a
    yellow arrow showing where directional entities point. Icons are never
    rotated: an upright icon plus an arrow reads unambiguously.
    """

    def __init__(self, icons: SpriteSource, palette: Palette = PALETTE):
        self.icons = icons
        self.palette = palette

    def applies(self, e: PlacedEntity) -> bool:
        return True

    def draw(self, canvas: Canvas, e: PlacedEntity, layout: Layout) -> bool:
        box = e.pixel_box(canvas.scale)
        x0, y0, bw, bh = box
        icon = self.icons.fit(e.name, (bw, bh), canvas.scale)
        if icon is not None:
            canvas.paste_fitted(icon, box)
        else:
            color = self.palette.category_color(e.info.category)
            canvas.draw.rectangle([x0 + 2, y0 + 2, x0 + bw - 3, y0 + bh - 3],
                                  fill=(*color, 180), outline=(255, 255, 255, 100))
            canvas.draw.text((x0 + 4, y0 + 4), e.name.split("-")[-1][:8], fill=(255, 255, 255, 220))
        if e.is_directional:
            size = canvas.scale if e.w == e.h == 1 else min(bw, bh) // 2
            canvas.arrow((x0 + (bw - size) // 2, y0 + (bh - size) // 2, size, size), e.facing, self.palette.arrow)
        return True
