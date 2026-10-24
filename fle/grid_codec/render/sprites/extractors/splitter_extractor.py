"""Splitters: structure plus its patch (the belts underneath are drawn by the renderer)."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.spec import layers_of
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class SplitterExtractor(GraphicsExtractor):
    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        return {d.label: layers_of(proto["structure"], d) + layers_of(proto.get("structure_patch"), d)
                for d in Direction}
