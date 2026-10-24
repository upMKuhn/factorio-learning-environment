"""Grid encoding and decoding: Vocabulary, GridEncoder, GridDecoder."""

import numpy as np
import pytest

from fle.grid_codec.grid import (
    BoundingBox, Channel, EncodingError, EntitySpec, GridDecoder, GridEncoder, Vocabulary,
)
from fle.grid_codec.registry import ENTITY_REGISTRY, Meta

VOCAB = Vocabulary.from_names(recipes=["iron-gear-wheel", "copper-cable"], items=["iron-plate", "copper-cable"])


def roundtrip(entities, vocab=VOCAB):
    grid = GridEncoder(vocab).encode(entities, padding=0)
    bounds = BoundingBox.from_entities(entities, padding=0)
    return grid, GridDecoder(vocab).decode(grid, bounds)


# ── Vocabulary ────────────────────────────────────────────────────────────────

def test_vocabulary_ids_are_sorted_and_one_based():
    assert VOCAB.recipe_index == {"copper-cable": 1, "iron-gear-wheel": 2}
    assert VOCAB.recipe_id("iron-gear-wheel") == 2 and VOCAB.recipe_name(2) == "iron-gear-wheel"
    assert VOCAB.item_id("iron-plate") == 2 and VOCAB.item_name(1) == "copper-cable"


def test_vocabulary_unknown_names_raise():
    with pytest.raises(KeyError):
        VOCAB.recipe_id("rocket-part")
    assert not VOCAB.has_recipe("rocket-part") and VOCAB.has_item("iron-plate")


def test_vocabulary_round_trips_through_its_indices():
    again = Vocabulary(VOCAB.recipe_index, VOCAB.item_index)
    assert again == VOCAB


def test_vocabulary_rejects_zero_and_duplicate_ids():
    with pytest.raises(ValueError):
        Vocabulary({"a": 0}, {})
    with pytest.raises(ValueError):
        Vocabulary({"a": 1, "b": 1}, {})


# ── Encoding ──────────────────────────────────────────────────────────────────

def test_channels_layout():
    assert [c.name for c in Channel] == [
        "ENTITY", "DIRECTION", "META", "INSTANCE", "RECIPE", "ITEM_LEFT", "ITEM_RIGHT"]
    assert GridEncoder(VOCAB).encode([], BoundingBox(0, 0, 3, 2)).shape == (2, 3, 7)


def test_encode_fills_rotated_footprint():
    grid = GridEncoder(VOCAB).encode([EntitySpec("steam-engine", 0, 0, direction=4)], padding=0)
    engine = ENTITY_REGISTRY.from_name("steam-engine")
    assert grid.shape[:2] == (3, 5)
    assert np.all(grid[:, :, Channel.ENTITY] == engine.id)
    assert np.all(grid[:, :, Channel.DIRECTION] == 4)
    assert np.all(grid[:, :, Channel.INSTANCE] == 1)


def test_encode_writes_recipe_and_meta():
    grid = GridEncoder(VOCAB).encode([EntitySpec("assembling-machine-2", 1, 1, recipe="iron-gear-wheel")])
    assert grid.shape[:2] == (5, 5)  # 1 tile padding by default
    assert grid[1, 1, Channel.RECIPE] == VOCAB.recipe_id("iron-gear-wheel")
    assert grid[1, 1, Channel.META] == int(ENTITY_REGISTRY.from_name("assembling-machine-2").meta)
    assert grid[0, 0, Channel.ENTITY] == 0


def test_single_tile_entities_have_no_instance():
    grid = GridEncoder(VOCAB).encode([EntitySpec("transport-belt", 0, 0)], padding=0)
    assert grid[0, 0, Channel.INSTANCE] == 0


def test_underground_output_sets_meta_bit():
    grid = GridEncoder(VOCAB).encode([
        EntitySpec("underground-belt", 0, 0, 4, io_type="input"),
        EntitySpec("underground-belt", 3, 0, 4, io_type="output"),
    ], padding=0)
    assert not grid[0, 0, Channel.META] & Meta.UNDERGROUND_OUTPUT
    assert grid[0, 3, Channel.META] & Meta.UNDERGROUND_OUTPUT
    assert grid[0, 3, Channel.META] & Meta.IS_BELT


@pytest.mark.parametrize("entities, message", [
    ([EntitySpec("stone-furnace", 0, 0), EntitySpec("inserter", 1, 1)], "overlap"),
    ([EntitySpec("stone-furnace", 0, 0, recipe="unobtainium")], "recipe"),
    ([EntitySpec("straight-rail", 0, 0)], "entity"),
    ([EntitySpec("inserter", 0, 0, direction=16)], "direction"),
    ([EntitySpec("inserter", 0, 0, io_type="output")], "io_type"),
])
def test_strict_encoder_refuses_bad_input(entities, message):
    with pytest.raises(EncodingError, match=message):
        GridEncoder(VOCAB).encode(entities)


def test_strict_encoder_refuses_clipping():
    with pytest.raises(EncodingError, match="outside"):
        GridEncoder(VOCAB).encode([EntitySpec("stone-furnace", 3, 3)], BoundingBox(0, 0, 4, 4))


def test_lenient_encoder_clips_and_ignores_unknown_recipe():
    grid = GridEncoder(VOCAB, strict=False).encode(
        [EntitySpec("stone-furnace", 3, 3, recipe="unobtainium")], BoundingBox(0, 0, 4, 4))
    assert grid[3, 3, Channel.ENTITY] == ENTITY_REGISTRY.from_name("stone-furnace").id
    assert grid[3, 3, Channel.RECIPE] == 0


def test_stamp_carried_items():
    encoder = GridEncoder(VOCAB)
    grid = encoder.encode([EntitySpec("transport-belt", 0, 0), EntitySpec("transport-belt", 1, 0)], padding=0)
    encoder.stamp_carried_items(grid, {(0, 0): ("iron-plate", None), (1, 0): (None, "copper-cable")})
    assert grid[0, 0, Channel.ITEM_LEFT] == VOCAB.item_id("iron-plate") and grid[0, 0, Channel.ITEM_RIGHT] == 0
    assert grid[0, 1, Channel.ITEM_RIGHT] == VOCAB.item_id("copper-cable")
    with pytest.raises(EncodingError, match="item"):
        encoder.stamp_carried_items(grid, {(0, 0): ("unobtainium", None)})


# ── Decoding ──────────────────────────────────────────────────────────────────

def test_roundtrip_reproduces_every_field():
    entities = [
        EntitySpec("assembling-machine-2", 0, 0, direction=4, recipe="copper-cable"),
        EntitySpec("steam-engine", 3, 0, direction=12),
        EntitySpec("arithmetic-combinator", 8, 0, direction=4),
        EntitySpec("underground-belt", 0, 3, direction=4, io_type="input"),
        EntitySpec("underground-belt", 4, 3, direction=4, io_type="output"),
        EntitySpec("transport-belt", 5, 3, direction=8),
    ]
    _, decoded = roundtrip(entities)
    assert sorted(decoded, key=EntitySpec.sort_key) == sorted(entities, key=EntitySpec.sort_key)


def test_roundtrip_every_registered_entity_in_every_direction():
    for info in ENTITY_REGISTRY.all_entities():
        for direction in (0, 4, 8, 12):
            entities = [EntitySpec(info.name, 2, 3, direction)]
            assert roundtrip(entities)[1] == entities, (info.name, direction)


def test_adjacent_identical_multitile_entities_stay_separate():
    entities = [EntitySpec("stone-furnace", 0, 0), EntitySpec("stone-furnace", 2, 0), EntitySpec("stone-furnace", 0, 2)]
    _, decoded = roundtrip(entities)
    assert sorted(decoded, key=EntitySpec.sort_key) == sorted(entities, key=EntitySpec.sort_key)


def test_decoder_accepts_entity_channels_only():
    grid, _ = roundtrip([EntitySpec("stone-furnace", 0, 0, recipe="iron-gear-wheel")])
    assert GridDecoder().decode(grid[:, :, :4]) == [EntitySpec("stone-furnace", 0, 0)]


def test_decoder_without_vocabulary_cannot_name_recipes():
    grid, _ = roundtrip([EntitySpec("stone-furnace", 0, 0, recipe="iron-gear-wheel")])
    assert GridDecoder().decode(grid)[0].recipe is None


def test_strict_decoder_detects_damaged_footprint():
    grid, _ = roundtrip([EntitySpec("stone-furnace", 0, 0)])
    grid[1, 1] = 0
    with pytest.raises(EncodingError, match="footprint"):
        GridDecoder().decode(grid)


def test_strict_decoder_detects_unknown_entity_id():
    grid = np.zeros((1, 1, 7), dtype=np.uint16)
    grid[0, 0, Channel.ENTITY] = 255
    with pytest.raises(EncodingError, match="entity id"):
        GridDecoder().decode(grid)
    assert GridDecoder(strict=False).decode(grid) == []


def test_bounding_box_respects_rotation():
    box = BoundingBox.from_entities([EntitySpec("steam-engine", 2, 3, direction=4)], padding=1)
    assert box == BoundingBox(1, 2, 7, 5)
