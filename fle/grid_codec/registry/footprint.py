from __future__ import annotations

from typing import Iterator, NamedTuple


class Footprint(NamedTuple):
    """Tiles an entity covers, as (width, height); unpacks like a plain tuple."""
    width: int
    height: int

    def tiles(self, x: int, y: int) -> Iterator[tuple[int, int]]:
        """Every (x, y) covered when the top-left tile is (x, y)."""
        for dy in range(self.height):
            for dx in range(self.width):
                yield x + dx, y + dy

    @property
    def area(self) -> int:
        return self.width * self.height
