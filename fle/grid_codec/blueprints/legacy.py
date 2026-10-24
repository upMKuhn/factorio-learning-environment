"""Dict-based functions from before the object model; kept until callers move to the classes."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Collection, Iterator

import numpy as np

from fle.grid_codec.blueprints.blueprint_normalizer import BlueprintNormalizer
from fle.grid_codec.blueprints.blueprint_rejected import BlueprintRejected
from fle.grid_codec.blueprints.blueprint_string import BlueprintString
from fle.grid_codec.blueprints.jsonl_blueprint_source import JsonlBlueprintSource
from fle.grid_codec.blueprints.recipe_data import RecipeData
from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint
from fle.grid_codec.grid import BoundingBox, EntitySpec, GridEncoder


def decode_blueprint_string(s: str) -> dict:
    return BlueprintString(s).decode()


def iter_blueprints(path: str | Path, min_entities: int = 0, max_entities: int | None = None) -> Iterator[dict]:
    for bp in JsonlBlueprintSource(path, min_entities, max_entities):
        yield bp.to_dict()


def find_blueprint(path: str | Path, label: str) -> dict:
    return JsonlBlueprintSource(path).find(label).to_dict()


def blueprint_entities(bp: dict, recipes: Collection[str], stats: Counter | None = None) -> list[dict] | None:
    """Normalized entities as dicts at the origin, or None (reasons counted in stats) if rejected."""
    try:
        return BlueprintNormalizer(recipes).normalize(SourceBlueprint.from_dict(bp)).as_dicts()
    except BlueprintRejected as rejected:
        if stats is not None:
            for detail in rejected.details or ("",):
                stats[f"dropped blueprint, {rejected.reason}: {detail}"] += 1
        return None


def encode_entities(entities: list[dict], data: RecipeData) -> tuple[np.ndarray, list[dict]]:
    """Strictly encode with 1 tile padding; returns the grid and the entities in grid coordinates."""
    specs = [EntitySpec.from_dict(e) for e in entities]
    bounds = BoundingBox.from_entities(specs, padding=1)
    grid = GridEncoder(data.vocabulary).encode(specs, bounds)
    return grid, [{**e, "x": e["x"] - bounds.x, "y": e["y"] - bounds.y} for e in entities]
