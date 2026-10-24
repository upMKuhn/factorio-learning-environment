"""Fixtures: synthetic sprite caches and icon atlases."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from fle.grid_codec.tests.render.helpers import ICON_COLORS, SPRITE_RED


@pytest.fixture
def sprite_dir(tmp_path: Path) -> Path:
    """
    A sprite cache with an oversized red assembler (5×5 tiles at 64 px for a
    3×3 entity) and nothing else.
    """
    out = tmp_path / "sprites"
    (out / "assembling-machine-1").mkdir(parents=True)
    index = {}
    for variant in ("north", "east", "south", "west"):
        Image.new("RGBA", (320, 320), SPRITE_RED).save(out / "assembling-machine-1" / f"{variant}.png")
        index[f"assembling-machine-1/{variant}"] = {"anchor": [160, 160]}
    (out / "index.json").write_text(json.dumps({"tile_px": 64, "sprites": index}))
    return out


@pytest.fixture
def empty_sprite_dir(tmp_path: Path) -> Path:
    out = tmp_path / "no-sprites"
    out.mkdir()
    return out


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """An icon atlas (icons.webp + data.json) with one solid colour per icon."""
    out = tmp_path / "data"
    out.mkdir()
    sheet = Image.new("RGBA", (66 * len(ICON_COLORS), 66), (0, 0, 0, 0))
    icons = []
    for i, (name, color) in enumerate(ICON_COLORS.items()):
        sheet.paste(Image.new("RGBA", (66, 66), color), (i * 66, 0))
        icons.append({"id": name, "position": f"-{i * 66}px 0px"})
    sheet.save(out / "icons.webp", lossless=True)
    (out / "data.json").write_text(json.dumps({"icons": icons}))
    return out
