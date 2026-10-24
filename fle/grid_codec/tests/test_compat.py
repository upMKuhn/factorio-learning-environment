"""Old import paths and functions keep working while callers migrate."""

import numpy as np

from fle.grid_codec.tests.fixtures import V1_1, blueprint, book, entity, write_jsonl


def test_schema_module_reexports():
    from fle.grid_codec import schema
    from fle.grid_codec.registry import ENTITY_REGISTRY, EntityInfo, EntityRegistry, Meta
    assert schema.ENTITY_REGISTRY is ENTITY_REGISTRY
    assert schema.EntityInfo is EntityInfo and schema.Meta is Meta
    assert schema.EntityID is EntityRegistry


def test_encoder_and_decoder_modules():
    from fle.grid_codec import BoundingBox as B0, EntitySpec as S0, decode as d0, encode as e0
    from fle.grid_codec.decoder import decode
    from fle.grid_codec.encoder import BoundingBox, EntitySpec, encode, stamp_carried_items
    assert (B0, S0, d0, e0) == (BoundingBox, EntitySpec, decode, encode)

    entities = [EntitySpec("stone-furnace", 0, 0), EntitySpec("transport-belt", 2, 0, 8)]
    grid = encode(entities, bounds=BoundingBox(0, 0, 4, 4))
    assert grid.shape == (4, 4, 7) and grid.dtype == np.uint16
    assert decode(grid) == entities
    assert decode(grid[:, :, :4]) == entities

    stamp_carried_items(grid, {(2, 0): ("iron-plate", None)}, {"iron-plate": 3})
    assert grid[0, 2, 5] == 3


def test_legacy_encode_clips_like_before():
    from fle.grid_codec.encoder import BoundingBox, EntitySpec, encode
    grid = encode([EntitySpec("stone-furnace", 3, 3)], bounds=BoundingBox(0, 0, 4, 4))
    assert grid[3, 3, 0] > 0


def test_blueprint_functions(tmp_path, recipe_data):
    from fle.grid_codec.blueprints import blueprint_entities, encode_entities, find_blueprint, iter_blueprints
    path = write_jsonl(tmp_path / "s.jsonl", [book([
        blueprint([entity("stone-furnace", 1, 1), entity("stack-inserter", 2.5, 0.5, 2)], label="Inserters", version=V1_1),
        blueprint([entity("straight-rail", 1, 1)], label="rails"),
    ])])
    assert [bp["label"] for bp in iter_blueprints(path)] == ["Inserters", "rails"]

    bp = find_blueprint(path, "Inserters")
    assert bp["entity_count"] == 2 and bp["label"] == "Inserters"

    entities = blueprint_entities(bp, recipe_data.recipes)
    assert entities == [
        {"name": "stone-furnace", "x": 0, "y": 0, "direction": 0},
        {"name": "bulk-inserter", "x": 2, "y": 0, "direction": 4},
    ]
    stats = {}
    from collections import Counter
    stats = Counter()
    assert blueprint_entities(find_blueprint(path, "rails"), recipe_data.recipes, stats) is None
    assert stats["dropped blueprint, unknown entity: straight-rail"] == 1

    grid, in_grid = encode_entities(entities, recipe_data)
    assert grid.shape == (4, 5, 7)
    assert in_grid[0] == {"name": "stone-furnace", "x": 1, "y": 1, "direction": 0}


def test_recipe_data_exposes_vocabulary(recipe_data):
    vocab = recipe_data.vocabulary
    assert vocab.recipe_index == recipe_data.recipe_index
    assert vocab.item_index == recipe_data.item_index
    assert recipe_data.recipe_index["iron-gear-wheel"] > 0
    assert recipe_data.recipe_times["iron-gear-wheel"] > 0
    assert "iron-plate" in recipe_data.recipes["iron-gear-wheel"]["in_"]
