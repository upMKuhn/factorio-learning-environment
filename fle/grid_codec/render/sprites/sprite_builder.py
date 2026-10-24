"""Builds the sprite cache from a local Factorio install."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from fle.grid_codec.render.sprites.extractors import variants_for
from fle.grid_codec.render.sprites.game_files import GameFiles
from fle.grid_codec.render.sprites.paths import DEFAULT_DUMP, DEFAULT_GAME_DATA, SPRITE_DIR, TILE_PX
from fle.grid_codec.render.sprites.sprite_entry import SpriteEntry
from fle.grid_codec.render.sprites.sprite_index import SpriteIndex
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer
from fle.grid_codec.schema import ENTITY_REGISTRY


class SpriteBuilder:
    """
    Composes one PNG per registered entity and variant from `factorio --dump-data`
    output (script-output/data-raw-dump.json) and the game's PNGs, and writes
    <out>/<entity>/<variant>.png plus <out>/index.json. Shadows, glows and
    lights are left out.
    """

    def __init__(self, dump: Path = DEFAULT_DUMP, game_data: Path = DEFAULT_GAME_DATA, out: Path = SPRITE_DIR):
        self.dump, self.out = Path(dump), Path(out)
        self.files = GameFiles(Path(game_data))

    def build(self) -> dict[str, list[str]]:
        """Write the cache; returns entities or variants skipped, by reason."""
        raw = json.loads(self.dump.read_text())
        prototypes = {name: proto for protos in raw.values() for name, proto in protos.items()
                      if isinstance(proto, dict) and "collision_box" in proto}
        index = SpriteIndex(tile_px=TILE_PX)
        skipped: dict[str, list[str]] = {}

        for info in ENTITY_REGISTRY.all_entities():
            proto = prototypes.get(info.name)
            if proto is None:
                skipped.setdefault("no prototype", []).append(info.name)
                continue
            (self.out / info.name).mkdir(parents=True, exist_ok=True)
            for variant, layers in variants_for(proto).items():
                if not layers:
                    skipped.setdefault("no graphics", []).append(f"{info.name}/{variant}")
                    continue
                img, anchor = self.compose(layers)
                img.save(self.out / info.name / f"{variant}.png")
                index.sprites[f"{info.name}/{variant}"] = SpriteEntry(anchor=anchor)

        index.save(self.out / "index.json")
        return skipped

    def compose(self, layers: list[SpriteLayer]) -> tuple[Image.Image, tuple[int, int]]:
        """Draw layers around the entity centre; returns the image and the centre in it."""
        placed = []
        for layer in layers:
            img = self.files.open(layer.file).crop(
                (layer.x, layer.y, layer.x + layer.width, layer.y + layer.height))
            factor = TILE_PX * layer.scale / 32
            w, h = max(1, round(img.width * factor)), max(1, round(img.height * factor))
            if layer.length:
                h = max(1, round(TILE_PX * layer.length))
            img = img.resize((w, h), Image.LANCZOS)
            if layer.rotate:
                img = img.rotate(layer.rotate, expand=True, resample=Image.BICUBIC)
            cx, cy = layer.shift[0] * TILE_PX, layer.shift[1] * TILE_PX
            placed.append((img, cx - img.width / 2, cy - img.height / 2))

        x0 = min(p[1] for p in placed)
        y0 = min(p[2] for p in placed)
        x1 = max(p[1] + p[0].width for p in placed)
        y1 = max(p[2] + p[0].height for p in placed)
        canvas = Image.new("RGBA", (round(x1 - x0), round(y1 - y0)), (0, 0, 0, 0))
        for img, x, y in placed:
            canvas.alpha_composite(img, (round(x - x0), round(y - y0)))
        return self._strip_shadow(canvas), (round(-x0), round(-y0))

    @staticmethod
    def _strip_shadow(img: Image.Image) -> Image.Image:
        """Drop baked-in shadows: translucent near-black pixels."""
        px = np.array(img)
        shadow = (px[..., :3].max(axis=-1) < 24) & (px[..., 3] < 230)
        px[shadow, 3] = 0
        return Image.fromarray(px)
