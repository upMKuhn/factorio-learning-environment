"""Cardinal directions in FLE's 16-way encoding."""

from __future__ import annotations

from enum import IntEnum


class Direction(IntEnum):
    """A cardinal direction; values match grid channel 1 (0=N, 4=E, 8=S, 12=W)."""
    NORTH = 0
    EAST = 4
    SOUTH = 8
    WEST = 12

    @classmethod
    def snap(cls, value: int) -> Direction:
        """Nearest cardinal direction to a 16-way value."""
        return cls(round(int(value) / 4) % 4 * 4)

    @property
    def delta(self) -> tuple[int, int]:
        """One step in this direction as (dx, dy); y grows southward."""
        return {0: (0, -1), 4: (1, 0), 8: (0, 1), 12: (-1, 0)}[self.value]

    @property
    def opposite(self) -> Direction:
        return Direction((self.value + 8) % 16)

    @property
    def left(self) -> Direction:
        """Left-hand side when travelling this way."""
        return Direction((self.value + 12) % 16)

    @property
    def right(self) -> Direction:
        return Direction((self.value + 4) % 16)

    @property
    def label(self) -> str:
        """Factorio's lowercase name, as used in sprite variants."""
        return self.name.lower()
