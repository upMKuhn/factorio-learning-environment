"""BlueprintNormalizer: Factorio blueprint → Layout of top-left tiles, or a counted rejection."""

import pytest

from fle.grid_codec.blueprints import BlueprintNormalizer, BlueprintRejected, Layout, SourceBlueprint
from fle.grid_codec.grid import EntitySpec
from fle.grid_codec.tests.fixtures import V0_17, V1_1, V2_0, entity

RECIPES = {"iron-gear-wheel", "automation-science-pack", "copper-cable"}
NORMALIZER = BlueprintNormalizer(RECIPES)


def normalize(entities, version=V2_0) -> list[EntitySpec]:
    layout = NORMALIZER.normalize(SourceBlueprint(label="t", entities=entities, version=version))
    assert isinstance(layout, Layout)
    return sorted(layout.entities, key=EntitySpec.sort_key)


def rejection(entities, version=V2_0) -> BlueprintRejected:
    with pytest.raises(BlueprintRejected) as info:
        NORMALIZER.normalize(SourceBlueprint(label="t", entities=entities, version=version))
    return info.value


def test_centres_become_top_left_tiles():
    assert normalize([
        entity("stone-furnace", 1, 1),          # 2x2 centred on a tile corner
        entity("transport-belt", 2.5, 0.5),
        entity("assembling-machine-2", 4.5, 1.5),
    ]) == [
        EntitySpec("stone-furnace", 0, 0),
        EntitySpec("transport-belt", 2, 0),
        EntitySpec("assembling-machine-2", 3, 0),
    ]


def test_origin_moves_to_zero():
    assert normalize([entity("transport-belt", -10.5, 7.5), entity("inserter", -9.5, 8.5)]) == [
        EntitySpec("transport-belt", 0, 0), EntitySpec("inserter", 1, 1)]


@pytest.mark.parametrize("direction, top_left_x, top_left_y", [(0, 1, 0), (4, 0, 1), (8, 1, 0), (12, 0, 1)])
def test_rotated_non_square_entity(direction, top_left_x, top_left_y):
    # steam engine is 3x5 north-facing, 5x3 east/west; centre (2.5, 2.5) in both cases.
    entities = normalize([entity("steam-engine", 2.5, 2.5, direction), entity("small-lamp", 0.5, 0.5)])
    assert entities[-1] == EntitySpec("steam-engine", top_left_x, top_left_y, direction)


def test_rotated_combinator():
    # 1x2 north-facing: east-facing at centre (1, 0.5) spans tiles (0,0)-(1,0).
    assert normalize([entity("decider-combinator", 1, 0.5, 4)]) == [EntitySpec("decider-combinator", 0, 0, 4)]


@pytest.mark.parametrize("version", [V0_17, V1_1])
def test_pre_2_0_directions_are_8_way(version):
    entities = normalize([entity("steam-engine", 2.5, 1.5, 2), entity("inserter", 0.5, 3.5, 6)], version)
    assert entities == [EntitySpec("steam-engine", 0, 0, 4), EntitySpec("inserter", 0, 3, 12)]


def test_2_0_directions_are_kept():
    assert normalize([entity("inserter", 0.5, 0.5, 12)]) == [EntitySpec("inserter", 0, 0, 12)]


def test_half_tile_phase_is_consistent():
    # Many 0.x blueprints put every entity half a tile off; relative placement must survive.
    shifted = normalize([entity("stone-furnace", 1.5, 1.5), entity("transport-belt", 3, 1)], V0_17)
    assert shifted == normalize([entity("stone-furnace", 1, 1), entity("transport-belt", 2.5, 0.5)], V0_17)


def test_off_grid_entities_take_the_tile_under_their_centre():
    assert normalize([entity("transport-belt", 0.5, 0.5), entity("land-mine", 3.02, 0.93)]) == [
        EntitySpec("transport-belt", 0, 0), EntitySpec("land-mine", 3, 0)]


def test_misaligned_entity_rejects_blueprint():
    err = rejection([entity("transport-belt", 0.5, 0.5), entity("transport-belt", 1.5, 0.5),
                     entity("stone-furnace", 3.5, 1)])
    assert err.reason == "misaligned entity" and err.detail == "stone-furnace"


def test_offshore_pump_is_anchored_on_one_tile():
    assert normalize([entity("offshore-pump", 0.5, 0.5), entity("pipe", 0.5, 1.5)]) == [
        EntitySpec("offshore-pump", 0, 0), EntitySpec("pipe", 0, 1)]


def test_renames_by_version():
    assert normalize([entity("stack-inserter", 0.5, 0.5), entity("logistic-chest-storage", 1.5, 0.5)], V1_1) == [
        EntitySpec("bulk-inserter", 0, 0), EntitySpec("storage-chest", 1, 0)]
    assert normalize([entity("stack-inserter", 0.5, 0.5)]) == [EntitySpec("stack-inserter", 0, 0)]


def test_recipes_are_migrated():
    [machine] = normalize([entity("assembling-machine-1", 1.5, 1.5, recipe="science-pack-1")], V0_17)
    assert machine.recipe == "automation-science-pack"


def test_unknown_entity_rejects_whole_blueprint():
    err = rejection([entity("transport-belt", 0.5, 0.5), entity("straight-rail", 3, 3)])
    assert (err.reason, err.detail) == ("unknown entity", "straight-rail")


def test_unknown_recipe_rejects_whole_blueprint():
    err = rejection([entity("assembling-machine-1", 1.5, 1.5, recipe="modded-thing")])
    assert (err.reason, err.detail) == ("unknown recipe", "modded-thing")


def test_overlap_rejects_blueprint():
    err = rejection([entity("stone-furnace", 1, 1), entity("inserter", 1.5, 1.5)])
    assert err.reason == "overlapping tiles"


def test_invalid_direction_rejects_blueprint():
    err = rejection([entity("inserter", 0.5, 0.5, 8)], V0_17)
    assert err.reason == "invalid direction"


def test_empty_blueprint_is_rejected():
    assert rejection([]).reason == "no entities"


def test_underground_type_is_kept_and_defaults_to_input():
    entities = normalize([
        entity("underground-belt", 0.5, 0.5, 4, type="input"),
        entity("underground-belt", 3.5, 0.5, 4, type="output"),
        entity("fast-underground-belt", 0.5, 1.5, 4),
    ])
    assert [e.io_type for e in entities] == ["input", "output", "input"]


def test_grid_form_entities_pass_through():
    layout = NORMALIZER.normalize(SourceBlueprint.from_dict({"label": "synthetic", "entities": [
        {"name": "stone-furnace", "x": 5, "y": 5}, {"name": "inserter", "x": 7, "y": 5, "direction": 4}]}))
    assert sorted(layout.entities, key=EntitySpec.sort_key) == [
        EntitySpec("stone-furnace", 0, 0), EntitySpec("inserter", 2, 0, 4)]
