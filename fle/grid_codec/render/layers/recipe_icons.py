"""Recipe icons over production buildings."""

from __future__ import annotations

from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.icon_atlas import IconAtlas
from fle.grid_codec.render.layers.render_layer import RenderLayer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.palette import PALETTE, Palette


class RecipeIconsLayer(RenderLayer):
    """
    The recipe's icon, semi-transparent, in the middle of each building that has
    one set, on a dark disc (as in Factorio's alt-mode) so it reads as an icon.
    """

    def __init__(self, icons: IconAtlas, recipe_index: dict[str, int], palette: Palette = PALETTE):
        self.icons = icons
        self.palette = palette
        self.recipes = {v: k for k, v in recipe_index.items()}

    def draw(self, canvas: Canvas, layout: Layout) -> None:
        for e in layout.entities:
            recipe = self.recipes.get(e.recipe_id) if e.has_recipe_slot else None
            if not recipe:
                continue
            p = self.palette
            size = round(min(min(e.w, e.h) * p.recipe_icon_size, p.recipe_icon_max_tiles) * canvas.scale)
            icon = self.icons.icon(recipe, size)
            if icon is None:
                continue
            icon = icon.copy()
            icon.putalpha(icon.getchannel("A").point(lambda a: round(a * p.recipe_icon_alpha)))
            x0, y0, bw, bh = e.pixel_box(canvas.scale)
            cx, cy = x0 + bw // 2, y0 + bh // 2
            r = round(size * p.recipe_backdrop_radius)
            canvas.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=p.recipe_backdrop)
            canvas.image.alpha_composite(icon, (cx - size // 2, cy - size // 2))
