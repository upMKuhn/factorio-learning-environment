from __future__ import annotations

from dataclasses import dataclass

from fle.grid_codec.registry import ENTITY_REGISTRY, EntityInfo, Footprint

IO_TYPES = ("input", "output")


@dataclass
class EntitySpec:
    """One placed entity: type, top-left tile, direction and per-instance settings."""
    name: str                          # prototype name, e.g. "stone-furnace"
    x: int                             # top-left tile x (grid column)
    y: int                             # top-left tile y (grid row)
    direction: int = 0                 # 0-15
    meta_override: int | None = None   # replaces the type's default Meta flags
    recipe: str | None = None          # recipe set on a machine
    io_type: str | None = None         # underground belts: "input" (entrance) or "output" (exit)

    def __post_init__(self):
        info = ENTITY_REGISTRY.get(self.name)
        if self.io_type is None and info is not None and info.is_underground_belt:
            self.io_type = "input"  # Factorio's default

    @property
    def info(self) -> EntityInfo:
        return ENTITY_REGISTRY.from_name(self.name)

    @property
    def footprint(self) -> Footprint:
        return self.info.footprint(self.direction)

    def tiles(self):
        return self.footprint.tiles(self.x, self.y)

    def sort_key(self) -> tuple:
        return self.y, self.x, self.name, self.direction, self.recipe or "", self.io_type or ""

    def to_dict(self) -> dict:
        """{name, x, y, direction, recipe?, type?}: the dict form flow inference and notebooks use."""
        return {
            "name": self.name, "x": self.x, "y": self.y, "direction": self.direction,
            **({"recipe": self.recipe} if self.recipe else {}),
            **({"type": self.io_type} if self.io_type else {}),
        }

    @classmethod
    def from_dict(cls, d: dict) -> EntitySpec:
        return cls(d["name"], d["x"], d["y"], d.get("direction", 0),
                   recipe=d.get("recipe"), io_type=d.get("type"))
