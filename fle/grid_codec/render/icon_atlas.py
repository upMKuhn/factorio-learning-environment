"""Item and entity icons from the web spritesheet (icons.webp + data.json)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from PIL import Image

from fle.grid_codec.render.sprite_source import SpriteSource


class IconAtlas(SpriteSource):
    """Upright square icons keyed by prototype name."""

    ICON_SIZE = 66  # pixels per icon in the spritesheet

    def __init__(self, data_dir: str | Path):
        data_path = Path(data_dir)
        self.sheet = Image.open(data_path / "icons.webp").convert("RGBA")
        data = json.loads((data_path / "data.json").read_text())
        self.positions: dict[str, tuple[int, int]] = {}
        for icon in data.get("icons", []):
            x, y = icon["position"].replace("px", "").split()  # "-132px -198px"
            self.positions[icon["id"]] = (abs(int(x)), abs(int(y)))
        self._icons: dict[tuple[str, int], Image.Image] = {}

    @staticmethod
    @lru_cache(maxsize=4)
    def shared(data_dir: str) -> IconAtlas:
        """Shared atlas per data directory."""
        return IconAtlas(data_dir)

    def __contains__(self, name: str) -> bool:
        return name in self.positions

    def icon(self, name: str, size: int) -> Image.Image | None:
        """The icon resized to size×size, or None."""
        if name not in self.positions:
            return None
        key = (name, size)
        if key not in self._icons:
            x, y = self.positions[name]
            icon = self.sheet.crop((x, y, x + self.ICON_SIZE, y + self.ICON_SIZE))
            self._icons[key] = icon if size == self.ICON_SIZE else icon.resize((size, size), Image.LANCZOS)
        return self._icons[key]

    def load(self, name: str, tile_px: int) -> tuple[Image.Image, tuple[int, int]] | None:
        icon = self.icon(name, tile_px)
        return None if icon is None else (icon, (tile_px // 2, tile_px // 2))

    def fit(self, name: str, box: tuple[int, int], tile_px: int) -> Image.Image | None:
        return self.icon(name, max(1, min(box)))
