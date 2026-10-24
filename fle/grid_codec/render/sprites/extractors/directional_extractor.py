"""Default extractor: one variant per direction."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import graphics_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class DirectionalExtractor(GraphicsExtractor):
    """
    The prototype's main graphics for each direction. Symmetric entities
    define only some directions; the game reuses the opposite one.
    """

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        by_dir = {d: self.layers(proto, d) for d in Direction}
        return {d.label: by_dir[d] or by_dir[d.opposite] or by_dir[Direction.NORTH] for d in Direction}

    def layers(self, proto: dict, direction: Direction) -> list[SpriteLayer]:
        return graphics_of(proto, direction)
