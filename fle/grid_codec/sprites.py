"""
Compatibility wrappers over fle.grid_codec.render.sprites; also the cache-building CLI.

    uv run python -m fle.grid_codec.sprites            # default Steam paths on macOS
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from fle.grid_codec.render.sprites import (
    DEFAULT_DUMP, DEFAULT_GAME_DATA, SPRITE_DIR, TILE_PX, SpriteBuilder, SpriteCache,
)

DIRECTIONS = {0: "north", 4: "east", 8: "south", 12: "west"}

__all__ = ["DIRECTIONS", "SPRITE_DIR", "TILE_PX", "build_sprites", "load_sprite", "sprites_available"]


def build_sprites(dump: Path = DEFAULT_DUMP, game_data: Path = DEFAULT_GAME_DATA,
                  out: Path = SPRITE_DIR) -> dict[str, list[str]]:
    skipped = SpriteBuilder(dump, game_data, out).build()
    SpriteCache.shared.cache_clear()
    return skipped


def load_sprite(key: str, tile_px: int, sprite_dir: str = str(SPRITE_DIR)
                ) -> tuple[Image.Image, tuple[int, int]] | None:
    """Sprite `<entity>/<variant>` scaled to tile_px, with the entity centre inside it."""
    return SpriteCache.shared(str(sprite_dir)).load(key, tile_px)


def sprites_available(sprite_dir: str = str(SPRITE_DIR)) -> bool:
    return SpriteCache.shared(str(sprite_dir)).available


def main():
    parser = argparse.ArgumentParser(description="Build the entity sprite cache from a local Factorio install")
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP,
                        help="data-raw-dump.json from `factorio --dump-data`")
    parser.add_argument("--game-data", type=Path, default=DEFAULT_GAME_DATA,
                        help="the game's data folder (contains base/, core/, space-age/)")
    parser.add_argument("--out", type=Path, default=SPRITE_DIR)
    args = parser.parse_args()

    skipped = build_sprites(args.dump, args.game_data, args.out)
    print(f"Wrote {len(SpriteCache(args.out).index.sprites)} sprites to {args.out}")
    for reason, names in skipped.items():
        print(f"  skipped ({reason}): {', '.join(names)}")


if __name__ == "__main__":
    main()
