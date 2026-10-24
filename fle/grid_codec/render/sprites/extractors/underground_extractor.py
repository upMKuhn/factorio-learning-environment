"""Underground belts: entrance and exit hoods over a belt end."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.belt_extractor import BeltExtractor
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import layers_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class UndergroundExtractor(GraphicsExtractor):
    """
    "<direction>-in" and "<direction>-out", keyed by travel direction: half a
    straight belt on the open side (behind an entrance, ahead of an exit) under
    the hood. The game indexes exit hoods by the old-style direction (facing
    back toward the entrance), so exits use the opposite frame and a pair's
    hoods face each other.
    """

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        structure = proto["structure"]
        out = {}
        for d in Direction:
            out[f"{d.label}-in"] = self._half_belt(proto, d, d.opposite) \
                + layers_of(structure["direction_in"], d)
            out[f"{d.label}-out"] = self._half_belt(proto, d, d) \
                + layers_of(structure["direction_out"], d.opposite)
        return out

    @staticmethod
    def _half_belt(proto: dict, travel: Direction, side: Direction) -> list[SpriteLayer]:
        """The half of a straight belt piece (travelling travel) on the given side of the tile."""
        if "belt_animation_set" not in proto:
            return []
        piece = BeltExtractor.piece(proto, travel.label)
        dx, dy = side.delta
        if dx:
            piece.width //= 2
            piece.x += piece.width if dx > 0 else 0
        else:
            piece.height //= 2
            piece.y += piece.height if dy > 0 else 0
        piece.shift = (dx / 4, dy / 4)
        return [piece]
