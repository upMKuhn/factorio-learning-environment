from __future__ import annotations

import math
from collections import Counter
from typing import Collection

from fle.grid_codec.blueprints.blueprint_rejected import BlueprintRejected
from fle.grid_codec.blueprints.layout import Layout
from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint
from fle.grid_codec.blueprints.version_conventions import VersionConventions
from fle.grid_codec.grid import EntitySpec
from fle.grid_codec.grid.entity_spec import IO_TYPES
from fle.grid_codec.registry import ENTITY_REGISTRY, EntityRegistry

_EPS = 1e-6


class BlueprintNormalizer:
    """
    SourceBlueprint → Layout, or BlueprintRejected when it cannot be encoded faithfully.

    Factorio stores entity centres. A blueprint's entities share one grid
    phase (many 0.x exports sit half a tile off), so top-left tiles are taken
    relative to the most common phase; entities off that phase are an error,
    except prototypes placed off-grid (land mines), which take the tile under
    their centre. A blueprint is rejected whole for an unknown entity or recipe,
    a bad direction, misalignment or overlapping footprints — a partial
    factory is worse than none.
    """

    def __init__(self, recipes: Collection[str], registry: EntityRegistry = ENTITY_REGISTRY):
        self.recipes = recipes
        self.registry = registry

    def normalize(self, bp: SourceBlueprint) -> Layout:
        if not bp.entities:
            raise BlueprintRejected("no entities")
        conventions = VersionConventions.for_version(bp.version)
        resolved = self._resolve(bp.entities, conventions)
        placed = self._place(resolved)
        layout = Layout(tuple(placed), bp).at_origin()
        if overlap := layout.overlapping_tiles():
            names = sorted({e.name for e in layout.entities_on(overlap)})
            raise BlueprintRejected("overlapping tiles", names)
        return layout

    def _resolve(self, entities: list[dict], conventions: VersionConventions) -> list[tuple]:
        """(info, raw entity, direction, recipe, io_type) for each entity, or reject."""
        resolved, unknown_entities, unknown_recipes = [], set(), set()
        for e in entities:
            name = conventions.entity_name(e["name"])
            info = self.registry.get(name)
            if info is None:
                unknown_entities.add(name)
                continue
            direction = conventions.direction(e.get("direction", 0))
            if not 0 <= direction < 16:
                raise BlueprintRejected("invalid direction", [f"{name} {e.get('direction')}"])
            recipe = conventions.recipe_name(e["recipe"]) if e.get("recipe") else None
            if recipe and recipe not in self.recipes:
                unknown_recipes.add(recipe)
            io_type = e.get("type", "input") if info.is_underground_belt else None
            if io_type is not None and io_type not in IO_TYPES:
                raise BlueprintRejected("invalid underground type", [str(io_type)])
            resolved.append((info, e, direction, recipe, io_type))
        if unknown_entities:
            raise BlueprintRejected("unknown entity", sorted(unknown_entities))
        if unknown_recipes:
            raise BlueprintRejected("unknown recipe", sorted(unknown_recipes))
        return resolved

    def _place(self, resolved: list[tuple]) -> list[EntitySpec]:
        # Footprint corner in world units for centre-positioned entities; None for grid-form ones.
        corners = []
        for info, e, direction, _, _ in resolved:
            if "position" in e:
                w, h = info.footprint(direction)
                corners.append((e["position"]["x"] - w / 2, e["position"]["y"] - h / 2))
            else:
                corners.append(None)
        phases = Counter((self._frac(c[0]), self._frac(c[1]))
                         for (info, *_), c in zip(resolved, corners) if c and not info.off_grid)
        fx, fy = phases.most_common(1)[0][0] if phases else (0.0, 0.0)

        placed = []
        for (info, e, direction, recipe, io_type), corner in zip(resolved, corners):
            if corner:
                x, y = self._tile(corner[0] - fx, info), self._tile(corner[1] - fy, info)
            else:
                x, y = e["x"], e["y"]
            placed.append(EntitySpec(info.name, x, y, direction, recipe=recipe, io_type=io_type))
        return placed

    @staticmethod
    def _frac(v: float) -> float:
        return round(v % 1, 6) % 1

    @staticmethod
    def _tile(v: float, info) -> int:
        nearest = round(v)
        if abs(v - nearest) < _EPS:
            return int(nearest)
        if info.off_grid:
            return math.floor(v + 0.5)
        raise BlueprintRejected("misaligned entity", [info.name])
