"""Game PNGs addressed as "__mod__/path"."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image


class GameFiles:
    def __init__(self, game_data: Path):
        self.game_data = Path(game_data)

    @lru_cache(maxsize=None)
    def open(self, file: str) -> Image.Image:
        mod, rest = file.split("/", 1)
        return Image.open(self.game_data / mod.strip("_") / rest).convert("RGBA")
