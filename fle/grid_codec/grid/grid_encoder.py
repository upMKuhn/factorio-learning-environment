from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

from fle.grid_codec.grid.bounding_box import BoundingBox
from fle.grid_codec.grid.channel import Channel
from fle.grid_codec.grid.encoding_error import EncodingError
from fle.grid_codec.grid.entity_spec import EntitySpec
from fle.grid_codec.grid.vocabulary import Vocabulary
from fle.grid_codec.registry import ENTITY_REGISTRY, Meta

MAX_INSTANCES = np.iinfo(np.uint16).max


class GridEncoder:
    """
    Entities → (H, W, 7) uint16 grid, see Channel.

    Strict (the default) refuses anything the grid could not reproduce: unknown
    entities, recipes or items, overlapping or clipped footprints, bad
    directions. Lenient mode clips, overwrites and maps unknown names to 0.
    """

    def __init__(self, vocabulary: Vocabulary | None = None, strict: bool = True):
        self.vocabulary = vocabulary or Vocabulary.empty()
        self.strict = strict

    def encode(self, entities: Sequence[EntitySpec], bounds: BoundingBox | None = None,
               padding: int = 1, grid_size: tuple[int, int] | None = None) -> np.ndarray:
        """Encode entities over bounds (default: their bounding box plus padding)."""
        unknown = [e.name for e in entities if e.name not in ENTITY_REGISTRY]
        if unknown:
            if self.strict:
                raise EncodingError(f"unknown entity {unknown[0]!r}")
            entities = [e for e in entities if e.name in ENTITY_REGISTRY]
        if bounds is None:
            bounds = BoundingBox.from_entities(entities, padding=padding)
        h, w = grid_size or bounds.shape
        grid = np.zeros((h, w, Channel.count()), dtype=np.uint16)
        if len(entities) > MAX_INSTANCES:
            raise EncodingError(f"{len(entities)} entities exceed the {MAX_INSTANCES} instance ids")

        for instance, entity in enumerate(entities, start=1):
            info = ENTITY_REGISTRY.from_name(entity.name)
            self._validate(entity, info)
            fw, fh = info.footprint(entity.direction)
            x0, y0 = entity.x - bounds.x, entity.y - bounds.y
            x1, y1 = x0 + fw, y0 + fh
            if not (0 <= x0 and 0 <= y0 and x1 <= w and y1 <= h):
                if self.strict:
                    raise EncodingError(f"{entity} lies outside the {w}x{h} grid at {bounds}")
                x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w), min(y1, h)
                if x0 >= x1 or y0 >= y1:
                    continue
            tiles = grid[y0:y1, x0:x1]
            if self.strict and tiles[:, :, Channel.ENTITY].any():
                raise EncodingError(f"{entity} would overlap another entity")
            tiles[:, :, Channel.ENTITY] = info.id
            tiles[:, :, Channel.DIRECTION] = entity.direction
            tiles[:, :, Channel.META] = self._meta(entity, info)
            tiles[:, :, Channel.INSTANCE] = instance if info.is_multi_tile else 0
            tiles[:, :, Channel.RECIPE] = self._recipe_id(entity.recipe)
        return grid

    def stamp_carried_items(self, grid: np.ndarray, carries: Mapping[tuple[int, int], tuple]) -> None:
        """Write belt contents {(x, y) in grid coords: (left item, right item)} into channels 5-6."""
        for (x, y), lanes in carries.items():
            if not (0 <= y < grid.shape[0] and 0 <= x < grid.shape[1]):
                if self.strict:
                    raise EncodingError(f"carried item at ({x}, {y}) lies outside the grid")
                continue
            for channel, item in zip((Channel.ITEM_LEFT, Channel.ITEM_RIGHT), lanes):
                if item:
                    grid[y, x, channel] = self._item_id(item)

    def _validate(self, entity: EntitySpec, info) -> None:
        # EntitySpec itself guarantees a 16-way direction and a known io_type value.
        if self.strict and info.is_underground_belt != (entity.io_type is not None):
            raise EncodingError(f"invalid io_type in {entity}")

    @staticmethod
    def _meta(entity: EntitySpec, info) -> int:
        if entity.meta_override is not None:
            return entity.meta_override
        return int(info.meta | (Meta.UNDERGROUND_OUTPUT if entity.io_type == "output" else 0))

    def _recipe_id(self, recipe: str | None) -> int:
        if not recipe:
            return 0
        if self.vocabulary.has_recipe(recipe):
            return self.vocabulary.recipe_id(recipe)
        if self.strict:
            raise EncodingError(f"recipe {recipe!r} is not in the vocabulary")
        return 0

    def _item_id(self, item: str) -> int:
        if self.vocabulary.has_item(item):
            return self.vocabulary.item_id(item)
        if self.strict:
            raise EncodingError(f"item {item!r} is not in the vocabulary")
        return 0
