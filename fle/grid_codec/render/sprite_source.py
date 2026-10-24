"""The sprite-source interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image


class SpriteSource(ABC):
    """Images looked up by name and sized to fit a box."""

    @abstractmethod
    def load(self, name: str, tile_px: int) -> tuple[Image.Image, tuple[int, int]] | None:
        """The image for name at tile_px pixels per tile, with the entity centre in it; None if unknown."""

    @abstractmethod
    def fit(self, name: str, box: tuple[int, int], tile_px: int) -> Image.Image | None:
        """
        The image for name, fitted inside box (width, height in pixels) with its
        aspect ratio kept, at tile_px pixels per tile; None if unknown.
        """
