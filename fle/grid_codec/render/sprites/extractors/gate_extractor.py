"""Gates: vertical or horizontal by orientation."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import layers_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class GateExtractor(GraphicsExtractor):
    """North/south gates sit in a vertical wall, east/west ones in a horizontal wall."""

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        vertical = layers_of(proto["vertical_animation"], Direction.NORTH)
        horizontal = layers_of(proto["horizontal_animation"], Direction.EAST)
        return {d.label: vertical if d in (Direction.NORTH, Direction.SOUTH) else horizontal
                for d in Direction}
