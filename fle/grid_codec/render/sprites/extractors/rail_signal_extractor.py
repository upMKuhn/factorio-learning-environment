"""Rail signals: one sheet row per 16-way direction."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class RailSignalExtractor(GraphicsExtractor):
    """The ground structure's first (green) frame in each cardinal direction."""

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        structure = proto["ground_picture_set"]["structure"]
        specs = structure.get("layers", [structure])
        return {d.label: [SpriteLayer.from_spec(s, d.value * s.get("frame_count", 1))
                          for s in specs if SpriteLayer.is_drawn(s)]
                for d in Direction}
