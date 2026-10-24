"""Entity registry: ids are frozen, sizes match the game's prototypes."""

import json
import math

import pytest
from pydantic import ValidationError

from fle.grid_codec.registry import ENTITY_REGISTRY, EntityInfo, EntityRegistry, Footprint, Meta
from fle.grid_codec.tests.conftest import PROTOTYPE_DUMP

# Existing datasets store these ids; this list may only ever grow.
FROZEN_IDS = {
    1: "burner-mining-drill", 2: "electric-mining-drill", 3: "pumpjack", 4: "offshore-pump",
    5: "asteroid-collector", 6: "big-mining-drill", 20: "transport-belt", 21: "fast-transport-belt",
    22: "express-transport-belt", 23: "underground-belt", 24: "fast-underground-belt",
    25: "express-underground-belt", 26: "splitter", 27: "fast-splitter", 28: "express-splitter",
    29: "turbo-transport-belt", 30: "inserter", 31: "burner-inserter", 32: "long-handed-inserter",
    33: "fast-inserter", 34: "bulk-inserter", 35: "stack-inserter", 40: "pipe", 41: "pipe-to-ground", 42: "pump",
    43: "storage-tank", 44: "turbo-underground-belt", 45: "turbo-splitter", 50: "stone-furnace", 51: "steel-furnace",
    52: "electric-furnace", 53: "recycler", 54: "foundry", 55: "assembling-machine-1",
    56: "assembling-machine-2", 57: "assembling-machine-3", 58: "centrifuge", 59: "crusher", 60: "oil-refinery",
    61: "chemical-plant", 62: "electromagnetic-plant", 63: "cryogenic-plant", 64: "biochamber", 65: "lab",
    66: "rocket-silo", 67: "beacon", 68: "biolab", 69: "agricultural-tower", 70: "captive-biter-spawner",
    100: "boiler", 101: "steam-engine", 102: "solar-panel", 103: "accumulator", 104: "small-electric-pole",
    105: "medium-electric-pole", 106: "big-electric-pole", 107: "substation", 108: "nuclear-reactor",
    109: "heat-exchanger", 110: "steam-turbine", 111: "heat-pipe", 112: "heating-tower", 113: "fusion-reactor",
    114: "fusion-generator", 115: "lightning-rod", 116: "lightning-collector", 117: "thruster",
    130: "wooden-chest", 131: "iron-chest", 132: "steel-chest", 133: "passive-provider-chest",
    134: "active-provider-chest", 135: "storage-chest", 136: "requester-chest", 137: "buffer-chest",
    140: "rail", 141: "train-stop", 142: "rail-signal", 143: "rail-chain-signal", 144: "roboport",
    145: "cargo-bay", 160: "stone-wall", 161: "gate", 162: "gun-turret", 163: "laser-turret",
    164: "flamethrower-turret", 165: "artillery-turret", 166: "land-mine", 167: "radar", 168: "small-lamp",
    169: "rocket-turret", 170: "railgun-turret", 171: "tesla-turret", 190: "arithmetic-combinator",
    191: "decider-combinator", 192: "constant-combinator", 193: "power-switch", 194: "selector-combinator",
    195: "display-panel", 196: "programmable-speaker", 240: "belt-group", 241: "pipe-group",
    242: "electricity-group",
}

# Entities whose tile footprint differs from their collision box (collision box is smaller).
FOOTPRINT_NOT_FROM_COLLISION_BOX = {"train-stop", "railgun-turret"}
NOT_IN_PROTOTYPES = {"rail", "belt-group", "pipe-group", "electricity-group"}


def test_ids_never_change():
    current = {e.id: e.name for e in ENTITY_REGISTRY.all_entities()}
    for id_, name in FROZEN_IDS.items():
        assert current.get(id_) == name, f"id {id_} must stay {name!r}"


def test_ids_and_names_are_unique():
    entities = ENTITY_REGISTRY.all_entities()
    assert len({e.id for e in entities}) == len(entities)
    assert len({e.name for e in entities}) == len(entities)
    assert all(0 < e.id < 2 ** 16 for e in entities)


def test_lookup_both_ways():
    info = ENTITY_REGISTRY.from_name("stone-furnace")
    assert ENTITY_REGISTRY.from_id(info.id) is info
    assert "stone-furnace" in ENTITY_REGISTRY
    assert ENTITY_REGISTRY.has_name("stone-furnace") and not ENTITY_REGISTRY.has_name("straight-rail")
    assert ENTITY_REGISTRY.has_id(50) and not ENTITY_REGISTRY.has_id(0)
    assert ENTITY_REGISTRY.get("straight-rail") is None
    with pytest.raises(KeyError):
        ENTITY_REGISTRY.from_name("straight-rail")


def test_registry_rejects_duplicate_ids():
    with pytest.raises(ValueError):
        EntityRegistry([
            EntityInfo(id=1, name="a", width=1, height=1, meta=Meta.NONE, category="special"),
            EntityInfo(id=1, name="b", width=1, height=1, meta=Meta.NONE, category="special"),
        ])


@pytest.mark.parametrize("name, direction, expected", [
    ("steam-engine", 0, (3, 5)), ("steam-engine", 8, (3, 5)),
    ("steam-engine", 4, (5, 3)), ("steam-engine", 12, (5, 3)),
    ("arithmetic-combinator", 0, (1, 2)), ("arithmetic-combinator", 4, (2, 1)),
    ("splitter", 0, (2, 1)), ("splitter", 12, (1, 2)),
    ("boiler", 4, (2, 3)), ("assembling-machine-2", 4, (3, 3)),
])
def test_footprint_rotates_with_direction(name, direction, expected):
    assert ENTITY_REGISTRY.from_name(name).footprint(direction) == Footprint(*expected)


def test_offshore_pump_is_one_tile():
    # 2.0 prototype: tile_width = tile_height = 1; blueprints anchor it on a single tile.
    assert ENTITY_REGISTRY.from_name("offshore-pump").footprint(0) == Footprint(1, 1)


def test_only_land_mine_is_placed_off_grid():
    assert {e.name for e in ENTITY_REGISTRY.all_entities() if e.off_grid} == {"land-mine"}


def test_underground_output_flag_is_free():
    defaults = 0
    for e in ENTITY_REGISTRY.all_entities():
        defaults |= int(e.meta)
    assert not defaults & Meta.UNDERGROUND_OUTPUT


@pytest.mark.skipif(not PROTOTYPE_DUMP.exists(), reason="needs the game's data-raw-dump.json")
def test_sizes_match_game_prototypes():
    dump = json.loads(PROTOTYPE_DUMP.read_text())
    prototypes = {}
    for group in dump.values():
        if isinstance(group, dict):
            for name, p in group.items():
                if isinstance(p, dict) and "collision_box" in p:
                    prototypes.setdefault(name, p)

    mismatches = []
    for e in ENTITY_REGISTRY.all_entities():
        if e.name in NOT_IN_PROTOTYPES:
            continue
        p = prototypes[e.name]
        (x0, y0), (x1, y1) = p["collision_box"]
        size = (p.get("tile_width") or math.ceil(x1 - x0 - 1e-9), p.get("tile_height") or math.ceil(y1 - y0 - 1e-9))
        if size != (e.width, e.height) and e.name not in FOOTPRINT_NOT_FROM_COLLISION_BOX:
            mismatches.append((e.name, (e.width, e.height), size))
        assert e.off_grid == ("placeable-off-grid" in p.get("flags", [])), e.name
    assert mismatches == []


def test_conduits_are_belts_and_pipes():
    conduits = {e.name for e in ENTITY_REGISTRY.all_entities() if e.carries_contents}
    assert {"transport-belt", "express-underground-belt", "turbo-splitter", "pipe", "pipe-to-ground"} <= conduits
    assert not conduits & {"chemical-plant", "inserter", "storage-tank", "pump", "belt-group", "pipe-group"}


# ── Models ────────────────────────────────────────────────────────────────────

def test_entity_info_is_frozen_and_hashable():
    info = ENTITY_REGISTRY.from_name("stone-furnace")
    with pytest.raises(ValidationError):
        info.width = 3
    assert hash(info) == hash(info.model_copy())
    assert info == info.model_copy() and info.is_multi_tile


@pytest.mark.parametrize("field, value", [
    ("width", 0), ("height", -1), ("id", -1), ("id", 2 ** 16), ("category", "unknown"),
])
def test_entity_info_validates_fields(field, value):
    fields = dict(id=1, name="a", width=1, height=1, meta=Meta.NONE, category="special")
    with pytest.raises(ValidationError):
        EntityInfo(**{**fields, field: value})


def test_footprint_unpacks_like_a_pair():
    w, h = ENTITY_REGISTRY.from_name("steam-engine").footprint(4)
    assert (w, h) == (5, 3)
    footprint = Footprint(2, 3)
    assert footprint.area == 6
    assert list(footprint.tiles(1, 1)) == [(1, 1), (2, 1), (1, 2), (2, 2), (1, 3), (2, 3)]


def test_footprint_is_frozen_and_validated():
    footprint = Footprint(width=2, height=1)
    with pytest.raises(ValidationError):
        footprint.width = 3
    assert hash(footprint) == hash(Footprint(2, 1))
    with pytest.raises(ValidationError):
        Footprint(0, 1)
