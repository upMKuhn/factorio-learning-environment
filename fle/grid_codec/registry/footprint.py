from __future__ import annotations

from typing import Iterator

from pydantic import BaseModel, ConfigDict, Field


class Footprint(BaseModel):
    """Tiles an entity covers, as (width, height); unpacks like a pair: `w, h = footprint`."""
    model_config = ConfigDict(frozen=True)

    width: int = Field(ge=1)
    height: int = Field(ge=1)

    def __init__(self, width: int, height: int):
        super().__init__(width=width, height=height)

    def __iter__(self) -> Iterator[int]:  # type: ignore[override]
        yield self.width
        yield self.height

    def tiles(self, x: int, y: int) -> Iterator[tuple[int, int]]:
        """Every (x, y) covered when the top-left tile is (x, y)."""
        for dy in range(self.height):
            for dx in range(self.width):
                yield x + dx, y + dy

    @property
    def area(self) -> int:
        return self.width * self.height
