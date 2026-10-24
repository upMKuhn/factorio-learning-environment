"""Transport belts: straight pieces and curves."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

N, E, S, W = Direction

# Rows of a belt animation set, as Factorio's default *_index values (1-based)
BELT_ROWS = {
    "east": 1, "west": 2, "north": 3, "south": 4,
    "east_to_north": 5, "north_to_east": 6, "west_to_north": 7, "north_to_west": 8,
    "south_to_east": 9, "east_to_south": 10, "south_to_west": 11, "west_to_south": 12,
    "starting_south": 13, "ending_south": 14, "starting_west": 15, "ending_west": 16,
    "starting_north": 17, "ending_north": 18, "starting_east": 19, "ending_east": 20,
}
CURVES = [f"{a.label}_to_{b.label}" for a in Direction for b in (a.left, a.right)]


class BeltExtractor(GraphicsExtractor):
    """Variants "north".."west" and "<from>_to_<to>" curves, named by travel direction."""

    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        return {name: [self.piece(proto, name)] for name in [d.label for d in Direction] + CURVES}

    @staticmethod
    def piece(proto: dict, name: str) -> SpriteLayer:
        """One frame of the belt animation row called name (e.g. "ending_east")."""
        belt_set = proto["belt_animation_set"]
        sheet = belt_set["animation_set"]
        row = belt_set.get(f"{name}_index", BELT_ROWS[name]) - 1
        size = sheet.get("size") or sheet["height"]
        return SpriteLayer.from_spec({**sheet, "line_length": 1, "y": sheet.get("y", 0) + row * size})
