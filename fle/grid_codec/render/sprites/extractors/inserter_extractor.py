"""Inserters: platform plus an arm reaching toward the drop side."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import layers_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

# Degrees counter-clockwise that turn a north-pointing hand toward each direction
_ROTATION = {Direction.NORTH: 0, Direction.EAST: 270, Direction.SOUTH: 180, Direction.WEST: 90}


class InserterExtractor(GraphicsExtractor):
    """
    Variants are keyed by the grid direction, which points at the pickup side;
    the arm is drawn toward the drop side. The arm is kept short (hand inside
    the tile) so the sprite reads at tile size; long-handed ones reach further.
    """

    REACH = 0.3        # tiles from centre to hand
    LONG_REACH = 0.42

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        return {d.label: self.layers(proto, d) for d in Direction}

    def layers(self, proto: dict, pickup: Direction) -> list[SpriteLayer]:
        platform = layers_of(proto["platform_picture"], pickup)
        reach = self.LONG_REACH if "long" in proto["name"] else self.REACH
        drop = pickup.opposite
        dx, dy = drop.delta
        base = SpriteLayer.from_spec(proto["hand_base_picture"])
        hand = SpriteLayer.from_spec(proto["hand_open_picture"])
        base.shift = (dx * reach / 2, dy * reach / 2)
        hand.shift = (dx * reach, dy * reach)
        base.rotate = hand.rotate = _ROTATION[drop]
        base.length = reach
        return platform + [base, hand]
