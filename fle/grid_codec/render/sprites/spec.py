"""Reading Factorio sprite definitions (Sprite, Animation, Sprite4Way, layers...)."""

from __future__ import annotations

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

# Where prototypes keep their in-world graphics, in order of preference
GRAPHICS_KEYS = (
    "graphics_set", "structure", "pictures", "picture", "animation", "animations",
    "sprites", "sprite", "off_animation", "picture_off", "base", "chargable_graphics",
    "base_picture", "power_on_animation", "connection_sprites", "picture_safe",
    "robot_door", "base_day_sprite",
)
# Keys inside a graphics container that hold the sprite itself
NESTED_KEYS = (
    "animation", "idle_animation", "structure", "picture", "base_visualisation", "animation_list",
    "single", "straight_vertical_single", "sprites",
)


def layers_of(spec, direction: Direction) -> list[SpriteLayer]:
    """Flatten a sprite definition into drawable layers for one direction, frame 0."""
    if isinstance(spec, list):
        return [layer for s in spec for layer in layers_of(s, direction)]
    if not isinstance(spec, dict):
        return []
    for key in (direction.label, f"{direction.label}_graphics_set"):
        if key in spec:
            return layers_of(spec[key], direction)
    if "layers" in spec:
        return layers_of(spec["layers"], direction)
    if "sheet" in spec or "sheets" in spec:
        # Sprite4Way sheet: one frame per direction (or fewer, e.g. N/S and E/W)
        out = []
        for sheet in [spec["sheet"]] if "sheet" in spec else spec["sheets"]:
            if SpriteLayer.is_drawn(sheet):
                frames = sheet.get("frames", 4)
                out.append(SpriteLayer.from_spec({**sheet, "line_length": frames},
                                                 direction.value // 4 % frames))
        return out
    if "filename" in spec or "filenames" in spec:
        return [SpriteLayer.from_spec(spec)] if SpriteLayer.is_drawn(spec) else []
    for key in NESTED_KEYS:
        if key in spec:
            layers = layers_of(spec[key], direction)
            if layers:
                return layers
    return []


def graphics_of(proto: dict, direction: Direction) -> list[SpriteLayer]:
    """The first graphics definition of a prototype that yields layers."""
    for key in GRAPHICS_KEYS:
        if key in proto:
            layers = layers_of(proto[key], direction)
            if layers:
                return layers
    return []
