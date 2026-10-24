"""Default locations of the sprite cache and a local Factorio install (macOS Steam)."""

from pathlib import Path

TILE_PX = 64  # cache resolution; the game's high-res sprites are 64 px per tile at scale 0.5

SPRITE_DIR = Path(__file__).resolve().parents[4] / ".fle" / "sprites" / "entities"
DEFAULT_GAME_DATA = (Path.home() / "Library/Application Support/Steam/steamapps/common/Factorio"
                     / "factorio.app/Contents/data")
DEFAULT_DUMP = Path.home() / "Library/Application Support/factorio/script-output/data-raw-dump.json"
