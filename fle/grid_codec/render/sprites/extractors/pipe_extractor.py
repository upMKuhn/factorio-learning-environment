"""Pipes: one variant per set of connected sides."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import layers_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

# Pipe picture per connection mask (N, E, S, W)
SHAPES = {
    "0000": "straight_vertical_single",
    "1000": "ending_up", "0100": "ending_right", "0010": "ending_down", "0001": "ending_left",
    "1010": "straight_vertical", "0101": "straight_horizontal",
    "1100": "corner_up_right", "1001": "corner_up_left",
    "0110": "corner_down_right", "0011": "corner_down_left",
    "1101": "t_up", "0111": "t_down", "1110": "t_right", "1011": "t_left",
    "1111": "cross",
}


class PipeExtractor(GraphicsExtractor):
    """Variants "NESW" masks, e.g. "1010" for a vertical pipe."""

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        return {mask: layers_of(proto["pictures"][shape], Direction.NORTH) for mask, shape in SHAPES.items()}
