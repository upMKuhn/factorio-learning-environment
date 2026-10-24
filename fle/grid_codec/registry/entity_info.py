from __future__ import annotations

from functools import cached_property
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fle.grid_codec.registry.footprint import Footprint
from fle.grid_codec.registry.meta import Meta

Category = Literal["resource", "transport", "production", "power", "logistics", "combat", "circuit", "special"]


class EntityInfo(BaseModel):
    """Static info about a placeable entity type."""
    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=0, lt=2 ** 16)  # grid id, never reused or changed
    name: str                          # prototype name, e.g. "stone-furnace"
    width: int = Field(ge=1)           # tile width when facing north
    height: int = Field(ge=1)          # tile height when facing north
    meta: Meta                         # default metadata flags
    category: Category
    off_grid: bool = False             # placed at arbitrary positions, not snapped to tiles (land mines)

    # Derived once on first use; hot in encode/decode, so plain instance attributes afterwards.
    @cached_property
    def is_multi_tile(self) -> bool:
        return self.width > 1 or self.height > 1

    @cached_property
    def is_underground_belt(self) -> bool:
        return bool(self.meta & Meta.IS_BELT) and self.name.endswith("underground-belt")

    @cached_property
    def carries_contents(self) -> bool:
        """Belts and pipes: the only tiles whose contents grid channels 5-6 describe."""
        return self.category == "transport" and (bool(self.meta & Meta.IS_BELT)
                                                 or self.name in ("pipe", "pipe-to-ground"))

    @cached_property
    def _footprints(self) -> tuple[Footprint, Footprint]:
        return Footprint(self.width, self.height), Footprint(self.height, self.width)

    def footprint(self, direction: int) -> Footprint:
        """Tiles covered when facing direction (0-15); east/west swap the north-facing size."""
        return self._footprints[direction % 8 == 4]
