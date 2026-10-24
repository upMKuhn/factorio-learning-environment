"""The prototype-graphics extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer


class GraphicsExtractor(ABC):
    """Reads one prototype type's graphics into sprite variants."""

    @abstractmethod
    def variants(self, proto: dict) -> dict[str, list[SpriteLayer]]:
        """Every variant the renderer may ask for (e.g. "north", "east_to_north"), mapped to its layers."""
