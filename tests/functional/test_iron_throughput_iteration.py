"""
Parametrized throughput tests across ore types and layout scales.

Each test builds a drill→furnace layout, runs for 60 seconds at game speed 10,
and measures output throughput.

Ore types tested:
- iron-ore → iron-plate (furnace)
- copper-ore → copper-plate (furnace)
- stone → stone-brick (furnace, 2 stone per brick)
- coal → coal (raw mining, no furnace needed)
"""

import pytest
from fle.env.entities import Position
from fle.env.game_types import Prototype, Resource


MEASURE_SECONDS = 60

INVENTORY = {
    "coal": 500,
    "burner-mining-drill": 10,
    "electric-mining-drill": 10,
    "stone-furnace": 10,
    "burner-inserter": 20,
    "inserter": 20,
    "transport-belt": 200,
    "wooden-chest": 5,
    "iron-chest": 5,
    "boiler": 2,
    "offshore-pump": 2,
    "steam-engine": 2,
    "small-electric-pole": 50,
    "pipe": 20,
}

# (resource, output_item_name, needs_furnace)
ORE_CONFIGS = [
    pytest.param(Resource.IronOre, "iron-plate", True, id="iron"),
    pytest.param(Resource.CopperOre, "copper-plate", True, id="copper"),
    pytest.param(Resource.Stone, "stone-brick", True, id="stone"),
    pytest.param(Resource.Coal, "coal", False, id="coal"),
]


@pytest.fixture()
def game(configure_game):
    game = configure_game(inventory=INVENTORY)
    yield game


def measure_throughput(game, entity_name):
    """Run factory for MEASURE_SECONDS and return items/sec for entity_name."""
    pre_stats = game._get_production_stats()
    pre_count = pre_stats.get("output", {}).get(entity_name, 0)
    game.sleep(MEASURE_SECONDS)
    post_stats = game._get_production_stats()
    post_count = post_stats.get("output", {}).get(entity_name, 0)
    produced = post_count - pre_count
    rate = produced / MEASURE_SECONDS
    print(f"\n=== THROUGHPUT: {produced} {entity_name} in {MEASURE_SECONDS}s = {rate:.3f}/sec ===")
    return rate, produced


# ---------------------------------------------------------------------------
# Layout 1: Minimal — 1 drill → 1 furnace (direct drop) → inserter → chest
# For coal: 1 drill → inserter → chest (no furnace)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("resource,output_item,needs_furnace", ORE_CONFIGS)
def test_layout_1_minimal(game, resource, output_item, needs_furnace):
    """Single drill baseline throughput for each ore type."""
    from fle.env import DirectionInternal as Direction

    ore_pos = game.nearest(resource)
    game.move_to(ore_pos)

    drill = game.place_entity(
        Prototype.BurnerMiningDrill,
        direction=Direction.RIGHT,
        position=ore_pos,
    )
    game.insert_item(Prototype.Coal, drill, quantity=50)

    if needs_furnace:
        furnace = game.place_entity_next_to(
            Prototype.StoneFurnace,
            reference_position=drill.position,
            direction=Direction.RIGHT,
            spacing=0,
        )
        game.insert_item(Prototype.Coal, furnace, quantity=50)
        last_entity = furnace
    else:
        last_entity = drill

    # Inserter to pull output into chest
    inserter = game.place_entity_next_to(
        Prototype.BurnerInserter,
        reference_position=last_entity.position,
        direction=Direction.RIGHT,
        spacing=0,
    )
    game.insert_item(Prototype.Coal, inserter, quantity=10)

    chest = game.place_entity_next_to(
        Prototype.IronChest,
        reference_position=inserter.position,
        direction=Direction.RIGHT,
        spacing=0,
    )

    print(f"Layout 1 [{output_item}]: drill@{drill.position} → {'furnace → ' if needs_furnace else ''}chest@{chest.position}")

    rate, produced = measure_throughput(game, output_item)
    assert produced > 0, f"Should produce {output_item}"


# ---------------------------------------------------------------------------
# Layout 2: 3 drills → 3 furnaces (direct drop), output belt → chest
# For coal: 3 drills → belt → chest
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("resource,output_item,needs_furnace", ORE_CONFIGS)
def test_layout_2_triple(game, resource, output_item, needs_furnace):
    """Three drill pairs for each ore type."""
    from fle.env import DirectionInternal as Direction

    ore_pos = game.nearest(resource)
    game.move_to(ore_pos)

    output_inserters = []

    for i in range(3):
        drill_pos = Position(x=ore_pos.x + i * 4, y=ore_pos.y)
        game.move_to(drill_pos)
        drill = game.place_entity(
            Prototype.BurnerMiningDrill,
            direction=Direction.DOWN,
            position=drill_pos,
        )
        game.insert_item(Prototype.Coal, drill, quantity=50)

        if needs_furnace:
            furnace = game.place_entity_next_to(
                Prototype.StoneFurnace,
                reference_position=drill.position,
                direction=Direction.DOWN,
                spacing=0,
            )
            game.insert_item(Prototype.Coal, furnace, quantity=50)
            output_ref = furnace.position
        else:
            output_ref = drill.drop_position

        # Output inserter
        out_ins = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=output_ref,
            direction=Direction.DOWN,
            spacing=0,
        )
        game.insert_item(Prototype.Coal, out_ins, quantity=10)
        output_inserters.append(out_ins)

    # Belt connecting all output drops → chest
    first_drop = output_inserters[0].drop_position
    last_drop = output_inserters[-1].drop_position
    game.connect_entities(first_drop, last_drop, Prototype.TransportBelt)

    chest = game.place_entity_next_to(
        Prototype.IronChest,
        reference_position=last_drop,
        direction=Direction.RIGHT,
        spacing=1,
    )
    belt_to_chest = game.place_entity(
        Prototype.BurnerInserter,
        direction=Direction.RIGHT,
        position=chest.position.left(),
    )
    game.insert_item(Prototype.Coal, belt_to_chest, quantity=10)

    print(f"Layout 2 [{output_item}]: 3x drill{'→furnace' if needs_furnace else ''} → belt → chest@{chest.position}")

    rate, produced = measure_throughput(game, output_item)
    assert produced > 0, f"Should produce {output_item}"


# ---------------------------------------------------------------------------
# Layout 3: 3 electric drills + steam power → furnaces → chest
# For coal: 3 electric drills → belt → chest
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("resource,output_item,needs_furnace", ORE_CONFIGS)
def test_layout_3_electric(game, resource, output_item, needs_furnace):
    """Electric drills with steam power for each ore type."""
    from fle.env import DirectionInternal as Direction

    # Set up power: offshore pump → boiler → steam engine
    water_pos = game.nearest(Resource.Water)
    game.move_to(water_pos)
    pump = game.place_entity(Prototype.OffshorePump, position=water_pos)

    boiler = game.place_entity_next_to(
        Prototype.Boiler,
        reference_position=pump.position,
        direction=Direction.RIGHT,
        spacing=1,
    )
    game.insert_item(Prototype.Coal, boiler, quantity=50)
    game.connect_entities(pump, boiler, Prototype.Pipe)

    engine = game.place_entity_next_to(
        Prototype.SteamEngine,
        reference_position=boiler.position,
        direction=Direction.RIGHT,
        spacing=1,
    )
    game.connect_entities(boiler, engine, Prototype.Pipe)

    # Place electric drills on ore
    ore_pos = game.nearest(resource)
    game.move_to(ore_pos)

    drills = []
    furnaces = []
    for i in range(3):
        drill_pos = Position(x=ore_pos.x + i * 4, y=ore_pos.y)
        game.move_to(drill_pos)
        drill = game.place_entity(
            Prototype.ElectricMiningDrill,
            direction=Direction.DOWN,
            position=drill_pos,
        )
        drills.append(drill)

        if needs_furnace:
            furnace = game.place_entity(
                Prototype.StoneFurnace,
                position=drill.drop_position,
            )
            game.insert_item(Prototype.Coal, furnace, quantity=50)
            furnaces.append(furnace)

    # Connect power from engine to drills
    game.connect_entities(engine, drills[0], connection_type=Prototype.SmallElectricPole)
    for i in range(len(drills) - 1):
        game.connect_entities(drills[i], drills[i + 1], connection_type=Prototype.SmallElectricPole)

    # Output inserters → belt → chest
    inserter_drops = []
    output_refs = furnaces if needs_furnace else drills
    for ref in output_refs:
        ins = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=ref.position,
            direction=Direction.DOWN,
            spacing=0,
        )
        game.insert_item(Prototype.Coal, ins, quantity=10)
        inserter_drops.append(ins.drop_position)

    game.connect_entities(inserter_drops[0], inserter_drops[-1], Prototype.TransportBelt)

    chest = game.place_entity_next_to(
        Prototype.IronChest,
        reference_position=inserter_drops[-1],
        direction=Direction.RIGHT,
        spacing=1,
    )
    belt_ins = game.place_entity(
        Prototype.BurnerInserter,
        direction=Direction.RIGHT,
        position=chest.position.left(),
    )
    game.insert_item(Prototype.Coal, belt_ins, quantity=10)

    print(f"Layout 3 [{output_item}]: 3x electric drill{'→furnace' if needs_furnace else ''} → belt → chest@{chest.position}")

    rate, produced = measure_throughput(game, output_item)
    assert produced > 0, f"Should produce {output_item}"
