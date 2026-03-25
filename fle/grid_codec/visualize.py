"""
Render a grid in two modes:

  - **machine**: category-colored tiles with direction arrows (fast, no external data)
  - **human**:  actual Factorio icons from the spritesheet (requires icons.webp + data.json)
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from fle.grid_codec.schema import ENTITY_REGISTRY

# ── Color palette for machine mode ────────────────────────────────────────────

CATEGORY_COLORS: dict[str, tuple[int, int, int]] = {
    "resource":   (180, 140,  60),   # gold
    "transport":  ( 60, 160, 220),   # blue
    "production": (220, 100,  50),   # orange
    "power":      (240, 220,  50),   # yellow
    "logistics":  (100, 200, 100),   # green
    "combat":     (200,  50,  50),   # red
    "circuit":    (160,  80, 200),   # purple
    "special":    (128, 128, 128),   # gray
}

EMPTY_COLOR = (30, 30, 30)
GRID_LINE_COLOR = (50, 50, 50)

# ── Icon atlas ────────────────────────────────────────────────────────────────

ICON_SIZE = 66  # pixels per icon in the spritesheet


@lru_cache(maxsize=1)
def _load_icon_atlas(data_dir: str) -> tuple[Image.Image, dict[str, tuple[int, int]]]:
    """
    Load the icon spritesheet and build a name → (px_x, px_y) lookup.

    Returns:
        (spritesheet PIL image, {prototype_name: (crop_x, crop_y)})
    """
    data_path = Path(data_dir)
    sheet = Image.open(data_path / "icons.webp").convert("RGBA")

    with open(data_path / "data.json") as f:
        data = json.load(f)

    positions: dict[str, tuple[int, int]] = {}
    for icon in data.get("icons", []):
        # position format: "-132px -198px"
        parts = icon["position"].replace("px", "").split()
        px_x = abs(int(parts[0]))
        px_y = abs(int(parts[1]))
        positions[icon["id"]] = (px_x, px_y)

    return sheet, positions


def _get_icon(name: str, data_dir: str, size: int) -> Image.Image | None:
    """Crop and resize a single icon from the spritesheet."""
    sheet, positions = _load_icon_atlas(data_dir)
    if name not in positions:
        return None

    px_x, px_y = positions[name]
    icon = sheet.crop((px_x, px_y, px_x + ICON_SIZE, px_y + ICON_SIZE))
    if size != ICON_SIZE:
        icon = icon.resize((size, size), Image.LANCZOS)
    return icon


# ── Direction arrows ──────────────────────────────────────────────────────────

# FLE directions: 0=UP, 4=RIGHT, 8=DOWN, 12=LEFT
_ARROW_DELTAS = {0: (0, -1), 4: (1, 0), 8: (0, 1), 12: (-1, 0)}


def _draw_direction_arrow(draw: ImageDraw.Draw, x0: int, y0: int, scale: int, direction: int,
                          color: tuple[int, int, int, int] | tuple[int, int, int] = (255, 255, 255),
                          filled: bool = True) -> None:
    """Draw a triangular arrow inside a tile cell pointing in the given direction."""
    if direction == 0:
        return
    cx = x0 + scale // 2
    cy = y0 + scale // 2
    r = scale // 3

    nearest = min(_ARROW_DELTAS.keys(), key=lambda d: abs(d - direction))
    dx, dy = _ARROW_DELTAS[nearest]

    # Triangle tip + two base corners perpendicular to direction
    tip = (cx + dx * r, cy + dy * r)
    # Perpendicular vector
    px, py = -dy, dx
    base_half = r * 0.6
    base1 = (cx - dx * r // 3 + px * base_half, cy - dy * r // 3 + py * base_half)
    base2 = (cx - dx * r // 3 - px * base_half, cy - dy * r // 3 - py * base_half)

    if filled:
        draw.polygon([tip, base1, base2], fill=color)
    else:
        draw.polygon([tip, base1, base2], outline=color, width=max(1, scale // 12))


# ── Machine mode ──────────────────────────────────────────────────────────────

def grid_to_machine(grid: np.ndarray, scale: int = 8) -> Image.Image:
    """
    Render grid as category-colored tiles with direction arrows.
    Fast, no external data needed. Suitable for ML training visualization.
    """
    h, w = grid.shape[:2]
    img = Image.new("RGB", (w * scale, h * scale), EMPTY_COLOR)
    draw = ImageDraw.Draw(img)

    for gy in range(h):
        for gx in range(w):
            type_id = int(grid[gy, gx, 0])
            if type_id == 0:
                continue

            if not ENTITY_REGISTRY.has_id(type_id):
                color = (255, 0, 255)  # magenta = unknown
            else:
                info = ENTITY_REGISTRY.from_id(type_id)
                base = CATEGORY_COLORS.get(info.category, (128, 128, 128))
                direction = int(grid[gy, gx, 1])
                shift = (direction % 4) * 10 - 15
                color = tuple(max(0, min(255, c + shift)) for c in base)

            x0 = gx * scale
            y0 = gy * scale
            draw.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1],
                           fill=color, outline=GRID_LINE_COLOR)

            _draw_direction_arrow(draw, x0, y0, scale, int(grid[gy, gx, 1]))

    return img


# ── Human mode ────────────────────────────────────────────────────────────────

def grid_to_human(
    grid: np.ndarray,
    data_dir: str = "data/2.0",
    scale: int = 48,
) -> Image.Image:
    """
    Render grid using actual Factorio icons from the spritesheet.
    Multi-tile entities get a single icon centered on their bounding box.

    Args:
        grid: (H, W, 4) uint8 array.
        data_dir: Path to data directory containing icons.webp + data.json.
        scale: Pixels per tile.
    """
    h, w = grid.shape[:2]
    img = Image.new("RGBA", (w * scale, h * scale), (*EMPTY_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    for gy in range(h + 1):
        draw.line([(0, gy * scale), (w * scale, gy * scale)], fill=GRID_LINE_COLOR, width=1)
    for gx in range(w + 1):
        draw.line([(gx * scale, 0), (gx * scale, h * scale)], fill=GRID_LINE_COLOR, width=1)

    # Track which instance IDs we've already drawn (for multi-tile)
    drawn_instances: set[int] = set()

    for gy in range(h):
        for gx in range(w):
            type_id = int(grid[gy, gx, 0])
            if type_id == 0:
                continue

            instance_id = int(grid[gy, gx, 3])

            # Multi-tile: only draw icon once per instance
            if instance_id > 0:
                if instance_id in drawn_instances:
                    continue
                drawn_instances.add(instance_id)

            if not ENTITY_REGISTRY.has_id(type_id):
                continue

            info = ENTITY_REGISTRY.from_id(type_id)
            direction = int(grid[gy, gx, 1])

            # Icon size = entity size in tiles * scale
            icon_w = info.width * scale
            icon_h = info.height * scale
            icon_size = min(icon_w, icon_h)

            icon = _get_icon(info.name, data_dir, icon_size)

            x0 = gx * scale
            y0 = gy * scale

            if icon is not None:
                # Rotate icon by direction
                rotation = {0: 0, 4: -90, 8: 180, 12: 90}
                nearest_dir = min(rotation.keys(), key=lambda d: abs(d - direction))
                if rotation[nearest_dir] != 0:
                    icon = icon.rotate(rotation[nearest_dir], expand=False, resample=Image.BICUBIC)

                # Center icon in the entity's bounding box
                paste_x = x0 + (icon_w - icon.width) // 2
                paste_y = y0 + (icon_h - icon.height) // 2
                img.paste(icon, (paste_x, paste_y), icon)
            else:
                # Fallback: colored rectangle with name
                base = CATEGORY_COLORS.get(info.category, (128, 128, 128))
                draw.rectangle([x0 + 2, y0 + 2, x0 + icon_w - 3, y0 + icon_h - 3],
                               fill=(*base, 180), outline=(255, 255, 255, 100))
                label = info.name.split("-")[-1][:8]
                draw.text((x0 + 4, y0 + 4), label, fill=(255, 255, 255, 220))

            # Direction arrow overlay
            if direction > 0:
                if info.width == 1 and info.height == 1:
                    _draw_direction_arrow(draw, x0, y0, scale, direction, color=(255, 220, 0, 200))
                else:
                    arrow_size = min(icon_w, icon_h) // 2
                    arrow_x = x0 + (icon_w - arrow_size) // 2
                    arrow_y = y0 + (icon_h - arrow_size) // 2
                    _draw_direction_arrow(draw, arrow_x, arrow_y, arrow_size, direction,
                                          color=(255, 220, 0, 180))

    return img.convert("RGB")


# ── Convenience aliases ───────────────────────────────────────────────────────

# Keep backward compat
grid_to_rgb = grid_to_machine


def render_to_file(grid: np.ndarray, path: str | Path, mode: str = "machine", **kwargs) -> None:
    """
    Render grid and save as PNG.

    Args:
        mode: "machine" or "human"
    """
    if mode == "human":
        img = grid_to_human(grid, **kwargs)
    else:
        img = grid_to_machine(grid, **kwargs)
    img.save(str(path))


def render_legend(path: str | Path, scale: int = 16) -> None:
    """Render a color legend showing category → color mapping."""
    categories = list(CATEGORY_COLORS.items())
    h = len(categories) * (scale + 4) + 8
    w = 200
    img = Image.new("RGB", (w, h), (20, 20, 20))
    draw = ImageDraw.Draw(img)

    for i, (cat, color) in enumerate(categories):
        y = 4 + i * (scale + 4)
        draw.rectangle([4, y, 4 + scale, y + scale], fill=color)
        draw.text((4 + scale + 8, y), cat, fill=(220, 220, 220))

    img.save(str(path))
