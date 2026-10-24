"""The entity-drawing strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fle.grid_codec.render.canvas import Canvas
    from fle.grid_codec.render.layout import Layout
    from fle.grid_codec.render.placed_entity import PlacedEntity


class EntityDrawer(ABC):
    """How one kind of entity is drawn. Drawers are tried in order until one succeeds."""

    @abstractmethod
    def applies(self, e: PlacedEntity) -> bool: ...

    @abstractmethod
    def draw(self, canvas: Canvas, e: PlacedEntity, layout: Layout) -> bool:
        """Draw e inside its footprint; False if this drawer has nothing to draw."""
