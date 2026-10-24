"""Colours and proportions shared by the renderers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


class Palette(BaseModel):
    model_config = ConfigDict(frozen=True)

    category_colors: dict[str, RGB] = Field(default_factory=lambda: {
        "resource":   (180, 140,  60),   # gold
        "transport":  ( 60, 160, 220),   # blue
        "production": (220, 100,  50),   # orange
        "power":      (240, 220,  50),   # yellow
        "logistics":  (100, 200, 100),   # green
        "combat":     (200,  50,  50),   # red
        "circuit":    (160,  80, 200),   # purple
        "special":    (128, 128, 128),   # gray
    })
    default_category: RGB = (128, 128, 128)
    empty: RGB = (30, 30, 30)
    grid_line: RGB = (50, 50, 50)
    unknown: RGB = (255, 0, 255)
    arrow: RGBA = (255, 220, 0, 230)
    recipe_icon_size: float = 0.6        # fraction of the building's shorter side
    recipe_icon_max_tiles: float = 1.8
    recipe_icon_alpha: float = 0.75      # recipe icon opacity over buildings
    recipe_backdrop: RGBA = (0, 0, 0, 150)
    recipe_backdrop_radius: float = 0.7  # fraction of the icon size

    def category_color(self, category: str) -> RGB:
        return self.category_colors.get(category, self.default_category)


PALETTE = Palette()

# Module-level names kept for existing imports
CATEGORY_COLORS = PALETTE.category_colors
EMPTY_COLOR = PALETTE.empty
ARROW_COLOR = PALETTE.arrow
