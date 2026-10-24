"""
In-game entity sprites for the human renderer.

Factorio's item icons don't show which way an entity faces, so the human
renderer draws the real entity graphics. They come from a local game install:
`factorio --dump-data` writes every prototype's sprite definitions to
script-output/data-raw-dump.json, and the PNGs live in the game's data folder.
SpriteBuilder composes one image per entity and variant into a cache folder
(gitignored: it holds game art); SpriteCache loads them.

    uv run python -m fle.grid_codec.sprites            # default Steam paths on macOS
"""

from fle.grid_codec.render.sprites.game_files import GameFiles
from fle.grid_codec.render.sprites.paths import DEFAULT_DUMP, DEFAULT_GAME_DATA, SPRITE_DIR, TILE_PX
from fle.grid_codec.render.sprites.sprite_builder import SpriteBuilder
from fle.grid_codec.render.sprites.sprite_cache import SpriteCache
from fle.grid_codec.render.sprites.sprite_entry import SpriteEntry
from fle.grid_codec.render.sprites.sprite_index import SpriteIndex
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

__all__ = [
    "DEFAULT_DUMP", "DEFAULT_GAME_DATA", "GameFiles", "SPRITE_DIR", "SpriteBuilder", "SpriteCache",
    "SpriteEntry", "SpriteIndex", "SpriteLayer", "TILE_PX",
]
