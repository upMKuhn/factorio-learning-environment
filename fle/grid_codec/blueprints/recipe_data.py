from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from fle.grid_codec.grid import Vocabulary


class RecipeData(BaseModel):
    """Recipes from a Factorio data export (e.g. data/spa/data.json) and the grid vocabulary built from them."""
    model_config = ConfigDict(frozen=True)

    recipes: dict[str, dict]        # recipe → {"in_": {item: n}, "out": {item: n}, "producers": [...]}
    recipe_times: dict[str, float]  # recipe → seconds per craft

    @classmethod
    def load(cls, path: str | Path) -> RecipeData:
        raw = json.loads(Path(path).read_text()).get("recipes", [])
        return cls(
            recipes={r["id"]: {"in_": r.get("in", {}), "out": r.get("out", {}), "producers": r.get("producers", [])}
                     for r in raw},
            recipe_times={r["id"]: r.get("energy", 0.5) for r in raw},
        )

    @cached_property
    def vocabulary(self) -> Vocabulary:
        """Recipe ids in sorted name order; item ids over every recipe ingredient and product."""
        items = {item for r in self.recipes.values() for item in (*r["in_"], *r["out"])}
        return Vocabulary.from_names(self.recipes, items)

    @property
    def recipe_index(self) -> dict[str, int]:
        return self.vocabulary.recipe_index

    @property
    def item_index(self) -> dict[str, int]:
        return self.vocabulary.item_index
