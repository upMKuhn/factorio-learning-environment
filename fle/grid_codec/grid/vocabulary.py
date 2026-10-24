from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping


class Vocabulary:
    """Recipe and item names ↔ the ids stored in grid channels 4-6; id 0 means none."""

    def __init__(self, recipe_index: Mapping[str, int], item_index: Mapping[str, int]):
        self._recipe_ids = dict(recipe_index)
        self._item_ids = dict(item_index)
        self._recipe_names = self._invert(self._recipe_ids)
        self._item_names = self._invert(self._item_ids)

    @staticmethod
    def _invert(index: dict[str, int]) -> dict[int, str]:
        if any(i <= 0 for i in index.values()) or len(set(index.values())) != len(index):
            raise ValueError("Vocabulary ids must be unique and positive")
        return {i: name for name, i in index.items()}

    @classmethod
    def from_names(cls, recipes: Iterable[str], items: Iterable[str]) -> Vocabulary:
        """Ids 1..N in sorted name order."""
        return cls({n: i for i, n in enumerate(sorted(set(recipes)), 1)},
                   {n: i for i, n in enumerate(sorted(set(items)), 1)})

    @classmethod
    def empty(cls) -> Vocabulary:
        return cls({}, {})

    @classmethod
    def load(cls, directory: str | Path) -> Vocabulary:
        """Read recipe_index.json and item_index.json written next to a dataset."""
        d = Path(directory)
        return cls(json.loads((d / "recipe_index.json").read_text()), json.loads((d / "item_index.json").read_text()))

    def save(self, directory: str | Path) -> None:
        d = Path(directory)
        (d / "recipe_index.json").write_text(json.dumps(self._recipe_ids))
        (d / "item_index.json").write_text(json.dumps(self._item_ids))

    @property
    def recipe_index(self) -> dict[str, int]:
        return dict(self._recipe_ids)

    @property
    def item_index(self) -> dict[str, int]:
        return dict(self._item_ids)

    def recipe_id(self, name: str) -> int:
        return self._recipe_ids[name]

    def recipe_name(self, id_: int) -> str:
        return self._recipe_names[id_]

    def item_id(self, name: str) -> int:
        return self._item_ids[name]

    def item_name(self, id_: int) -> str:
        return self._item_names[id_]

    def has_recipe(self, name: str) -> bool:
        return name in self._recipe_ids

    def has_item(self, name: str) -> bool:
        return name in self._item_ids

    def __eq__(self, other) -> bool:
        return isinstance(other, Vocabulary) and (self._recipe_ids, self._item_ids) == (other._recipe_ids, other._item_ids)

    def __repr__(self) -> str:
        return f"Vocabulary({len(self._recipe_ids)} recipes, {len(self._item_ids)} items)"
