"""One image layer of an entity sprite, as defined in a prototype."""

from __future__ import annotations

from pydantic import BaseModel


class SpriteLayer(BaseModel):
    file: str                   # "__base__/graphics/..."
    x: int                      # crop origin in the file
    y: int
    width: int
    height: int
    scale: float                # 0.5 = 64 px per tile
    shift: tuple[float, float]  # sprite centre relative to the entity centre, in tiles
    rotate: int = 0               # degrees counter-clockwise, applied after scaling
    length: float | None = None   # stretch to this many tiles tall (inserter arms)

    @classmethod
    def from_spec(cls, spec: dict, frame: int = 0) -> SpriteLayer:
        """The given animation frame of a Sprite/Animation definition."""
        size = spec.get("size")
        w, h = (size, size) if isinstance(size, int) else (size or (spec["width"], spec["height"]))
        line_length = spec.get("line_length") or spec.get("frames") or spec.get("frame_count") or 1
        shift = spec.get("shift", (0, 0))
        return cls(
            file=spec["filename"] if "filename" in spec else spec["filenames"][0],
            x=spec.get("x", 0) + (frame % line_length) * w,
            y=spec.get("y", 0) + (frame // line_length) * h,
            width=w, height=h,
            scale=spec.get("scale", 1.0),
            shift=(float(shift[0]), float(shift[1])),
        )

    @staticmethod
    def is_drawn(spec: dict) -> bool:
        """False for shadows, glows, lights and masks, which the renderer leaves out."""
        return not (spec.get("draw_as_shadow") or spec.get("draw_as_glow") or spec.get("draw_as_light")
                    or spec.get("blend_mode") == "additive" or "mask" in spec.get("flags", [])
                    or "empty.png" in spec.get("filename", ""))
