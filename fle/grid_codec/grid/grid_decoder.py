from __future__ import annotations

import numpy as np

from fle.grid_codec.grid.bounding_box import BoundingBox
from fle.grid_codec.grid.channel import Channel
from fle.grid_codec.grid.encoding_error import EncodingError
from fle.grid_codec.grid.entity_spec import EntitySpec
from fle.grid_codec.grid.vocabulary import Vocabulary
from fle.grid_codec.registry import ENTITY_REGISTRY, Meta


class GridDecoder:
    """
    (H, W, ≥4) grid → entities, ordered by top-left tile (row-major).

    Recipes are named only with a vocabulary and a recipe channel. Strict (the
    default) raises on anything an encoder could not have written: unknown ids,
    multi-tile entities whose tiles do not form their exact footprint.
    """

    def __init__(self, vocabulary: Vocabulary | None = None, strict: bool = True):
        self.vocabulary = vocabulary
        self.strict = strict

    def decode(self, grid: np.ndarray, bounds: BoundingBox | None = None) -> list[EntitySpec]:
        if grid.ndim != 3 or grid.shape[2] < 4:
            raise EncodingError(f"Expected an (H, W, C≥4) grid, got {grid.shape}")
        ox, oy = (bounds.x, bounds.y) if bounds else (0, 0)
        ys, xs = np.nonzero(grid[:, :, Channel.ENTITY])
        instances = grid[ys, xs, Channel.INSTANCE]

        anchors = [(y, x) for y, x, i in zip(ys, xs, instances) if i == 0]
        ids, first, counts = np.unique(instances, return_index=True, return_counts=True)
        anchors += [(ys[f], xs[f]) for i, f in zip(ids, first) if i != 0]
        tile_counts = {int(i): int(c) for i, c in zip(ids, counts)}

        entities = []
        for y, x in sorted(anchors):
            entity = self._entity(grid, int(y), int(x), tile_counts)
            if entity is not None:
                entity.x += ox
                entity.y += oy
                entities.append(entity)
        return entities

    def _entity(self, grid: np.ndarray, y: int, x: int, tile_counts: dict[int, int]) -> EntitySpec | None:
        type_id, direction, meta, instance = (int(v) for v in grid[y, x, :4])
        if not ENTITY_REGISTRY.has_id(type_id):
            if self.strict:
                raise EncodingError(f"unknown entity id {type_id} at ({x}, {y})")
            return None
        info = ENTITY_REGISTRY.from_id(type_id)
        if self.strict:
            self._check_footprint(grid, y, x, info, direction, instance, tile_counts)
        return EntitySpec(
            info.name, x, y, direction,
            recipe=self._recipe(grid, y, x),
            io_type=("output" if meta & Meta.UNDERGROUND_OUTPUT else "input") if info.is_underground_belt else None,
        )

    @staticmethod
    def _check_footprint(grid, y, x, info, direction, instance, tile_counts) -> None:
        w, h = info.footprint(direction)
        if (instance == 0) == info.is_multi_tile:
            raise EncodingError(f"{info.name} at ({x}, {y}): instance id {instance} contradicts its footprint")
        if instance == 0:
            return
        block = grid[y:y + h, x:x + w, :4]
        complete = (block.shape[:2] == (h, w) and tile_counts[instance] == w * h
                    and np.all(block[:, :, Channel.INSTANCE] == instance)
                    and np.all(block[:, :, Channel.ENTITY] == info.id)
                    and np.all(block[:, :, Channel.DIRECTION] == direction))
        if not complete:
            raise EncodingError(f"{info.name} at ({x}, {y}): tiles do not form its {w}x{h} footprint")

    def _recipe(self, grid: np.ndarray, y: int, x: int) -> str | None:
        if self.vocabulary is None or grid.shape[2] <= Channel.RECIPE:
            return None
        recipe_id = int(grid[y, x, Channel.RECIPE])
        if recipe_id == 0:
            return None
        try:
            return self.vocabulary.recipe_name(recipe_id)
        except KeyError:
            if self.strict:
                raise EncodingError(f"unknown recipe id {recipe_id} at ({x}, {y})") from None
            return None
