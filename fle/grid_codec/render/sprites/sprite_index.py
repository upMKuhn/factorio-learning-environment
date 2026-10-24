"""The sprite cache's index.json."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from fle.grid_codec.render.sprites.paths import TILE_PX
from fle.grid_codec.render.sprites.sprite_entry import SpriteEntry


class SpriteIndex(BaseModel):
    tile_px: int = TILE_PX                                  # cache pixels per tile
    sprites: dict[str, SpriteEntry] = Field(default_factory=dict)  # "<entity>/<variant>" → entry

    @classmethod
    def load(cls, path: Path) -> SpriteIndex:
        """The index at path; empty if there is none."""
        path = Path(path)
        return cls.model_validate_json(path.read_text()) if path.exists() else cls()

    def save(self, path: Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=1))
