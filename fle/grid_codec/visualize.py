"""
Compatibility wrappers over fle.grid_codec.render.

  - **machine**: category-coloured tiles with direction arrows (MachineRenderer)
  - **human**:  in-game entity sprites, item icons as fallback (HumanRenderer)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from fle.grid_codec.render import HumanRenderer, IconAtlas, MachineRenderer
from fle.grid_codec.render.palette import CATEGORY_COLORS

ICON_SIZE = IconAtlas.ICON_SIZE

__all__ = [
    "CATEGORY_COLORS", "ICON_SIZE", "get_icon", "grid_to_human", "grid_to_machine", "grid_to_rgb",
    "render_legend", "render_to_file",
]


def _load_icon_atlas(data_dir: str) -> tuple[Image.Image, dict[str, tuple[int, int]]]:
    """The icon spritesheet and prototype name → (crop_x, crop_y)."""
    atlas = IconAtlas.shared(str(data_dir))
    return atlas.sheet, atlas.positions


def get_icon(name: str, data_dir: str, size: int) -> Image.Image | None:
    """The icon for a prototype or item, size×size, or None."""
    return IconAtlas.shared(str(data_dir)).icon(name, size)


def grid_to_machine(grid: np.ndarray, scale: int = 8) -> Image.Image:
    return MachineRenderer(scale).render(grid)


def grid_to_human(grid: np.ndarray, data_dir: str = "data/2.0", scale: int = 48,
                  sprite_dir: str | None = None, recipe_index: dict[str, int] | None = None) -> Image.Image:
    return HumanRenderer(data_dir, scale, sprite_dir, recipe_index).render(grid)


grid_to_rgb = grid_to_machine


def render_to_file(grid: np.ndarray, path: str | Path, mode: str = "machine", **kwargs) -> None:
    """Render grid in "machine" or "human" mode and save as PNG."""
    render = grid_to_human if mode == "human" else grid_to_machine
    render(grid, **kwargs).save(str(path))


def render_legend(path: str | Path, scale: int = 16) -> None:
    """Category → colour legend."""
    img = Image.new("RGB", (200, len(CATEGORY_COLORS) * (scale + 4) + 8), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    for i, (cat, color) in enumerate(CATEGORY_COLORS.items()):
        y = 4 + i * (scale + 4)
        draw.rectangle([4, y, 4 + scale, y + scale], fill=color)
        draw.text((4 + scale + 8, y), cat, fill=(220, 220, 220))
    img.save(str(path))
