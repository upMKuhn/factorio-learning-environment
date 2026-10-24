"""Human mode: in-game sprites, as a Factorio player would see the layout."""

from __future__ import annotations

from fle.grid_codec.render.drawers import (
    BeltDrawer, IconFallbackDrawer, PipeDrawer, SplitterDrawer, SpriteDrawer, UndergroundDrawer,
)
from fle.grid_codec.render.icon_atlas import IconAtlas
from fle.grid_codec.render.layered_renderer import LayeredRenderer
from fle.grid_codec.render.layers import EntitiesLayer, GridLinesLayer, RecipeIconsLayer
from fle.grid_codec.render.sprites.paths import SPRITE_DIR
from fle.grid_codec.render.sprites.sprite_cache import SpriteCache


class HumanRenderer(LayeredRenderer):
    """
    Grid lines, entity sprites fitted inside their footprints (see
    fle.grid_codec.render.sprites), and recipe icons over production buildings.
    Entities without a cached sprite fall back to their item icon plus an arrow.

    Args:
        data_dir: directory with icons.webp + data.json.
        scale: pixels per tile.
        sprite_dir: sprite cache (default: FLE's .fle/sprites/entities).
        recipe_index: recipe name → grid id (channel 4); without it no recipe icons.
    """

    def __init__(self, data_dir: str = "data/2.0", scale: int = 48, sprite_dir: str | None = None,
                 recipe_index: dict[str, int] | None = None):
        icons = IconAtlas.shared(str(data_dir))
        sprites = SpriteCache.shared(str(sprite_dir or SPRITE_DIR))
        layers = [
            GridLinesLayer(),
            EntitiesLayer([
                BeltDrawer(sprites), UndergroundDrawer(sprites), SplitterDrawer(sprites),
                PipeDrawer(sprites), SpriteDrawer(sprites), IconFallbackDrawer(icons),
            ]),
        ]
        if recipe_index:
            layers.append(RecipeIconsLayer(icons, recipe_index))
        super().__init__(scale, layers)
