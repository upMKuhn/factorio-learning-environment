from __future__ import annotations

from dataclasses import dataclass, field

from fle.grid_codec.registry.footprint import Footprint
from fle.grid_codec.registry.meta import Meta


@dataclass(frozen=True)
class EntityInfo:
    """Static info about a placeable entity type."""
    id: int                # grid id, never reused or changed
    name: str              # prototype name, e.g. "stone-furnace"
    width: int             # tile width when facing north
    height: int            # tile height when facing north
    meta: Meta             # default metadata flags
    category: str          # resource, transport, production, power, logistics, combat, circuit, special
    off_grid: bool = False  # placed at arbitrary positions, not snapped to tiles (land mines)
    # Derived once; hot in encode/decode.
    is_multi_tile: bool = field(init=False, compare=False)
    is_underground_belt: bool = field(init=False, compare=False)
    carries_contents: bool = field(init=False, compare=False)

    def __post_init__(self):
        belt = bool(self.meta & Meta.IS_BELT)
        derived = {
            "is_multi_tile": self.width > 1 or self.height > 1,
            "is_underground_belt": belt and self.name.endswith("underground-belt"),
            # Belts and pipes: the only tiles whose contents grid channels 5-6 describe.
            "carries_contents": self.category == "transport" and (belt or self.name in ("pipe", "pipe-to-ground")),
        }
        for name, value in derived.items():
            object.__setattr__(self, name, value)

    def footprint(self, direction: int) -> Footprint:
        """Tiles covered when facing direction (0-15); east/west swap the north-facing size."""
        if direction % 8 == 4:
            return Footprint(self.height, self.width)
        return Footprint(self.width, self.height)
