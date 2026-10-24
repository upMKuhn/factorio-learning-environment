"""Sprites built by SpriteBuilder, loaded for rendering."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image

from fle.grid_codec.render.sprite_source import SpriteSource
from fle.grid_codec.render.sprites.paths import SPRITE_DIR
from fle.grid_codec.render.sprites.sprite_index import SpriteIndex


class SpriteCache(SpriteSource):
    """<dir>/<entity>/<variant>.png plus index.json (SpriteIndex)."""

    def __init__(self, sprite_dir: str | Path = SPRITE_DIR):
        self.dir = Path(sprite_dir)
        self.index = SpriteIndex.load(self.dir / "index.json")
        self._fitted: dict[tuple, Image.Image | None] = {}

    @staticmethod
    @lru_cache(maxsize=4)
    def shared(sprite_dir: str = str(SPRITE_DIR)) -> SpriteCache:
        """Shared cache per directory."""
        return SpriteCache(sprite_dir)

    @property
    def available(self) -> bool:
        return bool(self.index.sprites)

    def __contains__(self, key: str) -> bool:
        return key in self.index.sprites

    @lru_cache(maxsize=4096)
    def load(self, key: str, tile_px: int) -> tuple[Image.Image, tuple[int, int]] | None:
        """Sprite `<entity>/<variant>` scaled to tile_px, with the entity centre inside it."""
        entry = self.index.sprites.get(key)
        if entry is None:
            return None
        img = Image.open(self.dir / f"{key}.png").convert("RGBA")
        factor = tile_px / self.index.tile_px
        if factor != 1:
            img = img.resize((max(1, round(img.width * factor)), max(1, round(img.height * factor))),
                             Image.LANCZOS)
        ax, ay = entry.anchor
        return img, (round(ax * factor), round(ay * factor))

    def fit(self, name: str, box: tuple[int, int], tile_px: int) -> Image.Image | None:
        key = (name, box, tile_px)
        if key not in self._fitted:
            self._fitted[key] = self._fit(name, box, tile_px)
        return self._fitted[key]

    def _fit(self, name: str, box: tuple[int, int], tile_px: int) -> Image.Image | None:
        sprite = self.load(name, tile_px)
        if sprite is None:
            return None
        img = sprite[0]
        if (bbox := img.getbbox()) is not None:
            img = img.crop(bbox)
        factor = min(box[0] / img.width, box[1] / img.height, 1)
        if factor < 1:
            img = img.resize((max(1, round(img.width * factor)), max(1, round(img.height * factor))),
                             Image.LANCZOS)
        return img
