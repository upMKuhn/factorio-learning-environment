"""Which belts feed which tiles, and where belts curve."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.placed_entity import PlacedEntity

if TYPE_CHECKING:
    from fle.grid_codec.render.layout import Layout
    from fle.grid_codec.render.underground_pairing import UndergroundPairing


class BeltConnections:
    """Belt-to-belt item flow between neighbouring tiles."""

    def __init__(self, layout: Layout, pairing: UndergroundPairing):
        self._layout = layout
        self._pairing = pairing

    def feeds(self, source: PlacedEntity | None, x: int, y: int) -> bool:
        """Whether source puts items onto tile (x, y) from a neighbouring tile."""
        if source is None or not source.is_belt:
            return False
        if source.is_underground and not self._pairing.is_exit(source):
            return False  # entrances send items underground
        dx, dy = source.direction.delta
        return any((tx + dx, ty + dy) == (x, y) for tx, ty in source.tiles())

    def curve(self, belt: PlacedEntity) -> Direction | None:
        """
        Travel direction a transport belt turns from, or None if it runs straight.

        A belt curves when nothing feeds it from behind and exactly one belt
        feeds it from a side.
        """
        if not belt.is_transport_belt:
            return None
        d = belt.direction
        if self.feeds(self._layout.step(belt.x, belt.y, d.opposite), belt.x, belt.y):
            return None
        inputs = [side for side in (d.left, d.right)
                  if self.feeds(self._layout.step(belt.x, belt.y, side), belt.x, belt.y)]
        return inputs[0].opposite if len(inputs) == 1 else None
