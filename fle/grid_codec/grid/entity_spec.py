from __future__ import annotations

from typing import Iterator, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from fle.grid_codec.registry import ENTITY_REGISTRY, EntityInfo, Footprint

IoType = Literal["input", "output"]
IO_TYPES: tuple[str, ...] = get_args(IoType)


class EntitySpec(BaseModel):
    """One placed entity: type, top-left tile, direction and per-instance settings."""
    model_config = ConfigDict(frozen=True)

    name: str                                                # prototype name, e.g. "stone-furnace"; may be unknown
    x: int                                                   # top-left tile x (grid column)
    y: int                                                   # top-left tile y (grid row)
    direction: int = Field(0, ge=0, lt=16)                   # 16-way: 0=N, 4=E, 8=S, 12=W
    meta_override: int | None = Field(None, ge=0, lt=2 ** 16)  # replaces the type's default Meta flags
    recipe: str | None = None                                # recipe set on a machine
    io_type: IoType | None = Field(None, validate_default=True)  # underground belts: entrance or exit

    def __init__(self, name: str, x: int, y: int, direction: int = 0, meta_override: int | None = None,
                 recipe: str | None = None, io_type: IoType | None = None):
        super().__init__(name=name, x=x, y=y, direction=direction, meta_override=meta_override,
                         recipe=recipe, io_type=io_type)

    @field_validator("io_type")
    @classmethod
    def _underground_belts_default_to_input(cls, io_type: str | None, info: ValidationInfo) -> str | None:
        if io_type is None:
            entity = ENTITY_REGISTRY.get(info.data.get("name"))
            if entity is not None and entity.is_underground_belt:
                return "input"  # Factorio's default
        return io_type

    @property
    def info(self) -> EntityInfo:
        return ENTITY_REGISTRY.from_name(self.name)

    @property
    def footprint(self) -> Footprint:
        return self.info.footprint(self.direction)

    def tiles(self) -> Iterator[tuple[int, int]]:
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
