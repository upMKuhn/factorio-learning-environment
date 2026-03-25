"""Round-trip tests: encode → decode should be lossless."""

import numpy as np
import pytest

from fle.grid_codec.encoder import BoundingBox, EntitySpec, encode
from fle.grid_codec.decoder import decode
from fle.grid_codec.schema import ENTITY_REGISTRY


def _roundtrip(entities: list[EntitySpec], bounds: BoundingBox | None = None):
    """Encode then decode and return the result."""
    if bounds is None:
        bounds = BoundingBox.from_entities(entities)
    grid = encode(entities, bounds=bounds)
    return decode(grid, bounds=bounds)


class TestEmptyGrid:
    def test_empty_produces_no_entities(self):
        result = _roundtrip([])
        assert result == []

    def test_empty_grid_is_all_zeros(self):
        grid = encode([], bounds=BoundingBox(0, 0, 8, 8))
        assert grid.shape == (8, 8, 4)
        assert np.all(grid == 0)


class TestSingleTileEntities:
    def test_single_belt(self):
        entities = [EntitySpec("transport-belt", x=3, y=3, direction=8)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "transport-belt"
        assert result[0].x == 3
        assert result[0].y == 3
        assert result[0].direction == 8

    def test_single_inserter(self):
        entities = [EntitySpec("inserter", x=5, y=5, direction=4)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "inserter"
        assert result[0].direction == 4

    def test_multiple_single_tile(self):
        entities = [
            EntitySpec("transport-belt", x=0, y=0, direction=8),
            EntitySpec("inserter", x=1, y=0, direction=4),
            EntitySpec("transport-belt", x=2, y=0, direction=8),
        ]
        result = _roundtrip(entities)
        assert len(result) == 3
        names = [e.name for e in result]
        assert "transport-belt" in names
        assert "inserter" in names


class TestMultiTileEntities:
    def test_stone_furnace_2x2(self):
        """Stone furnace is 2x2 — should produce single entity after roundtrip."""
        entities = [EntitySpec("stone-furnace", x=4, y=4, direction=0)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "stone-furnace"
        assert result[0].x == 4
        assert result[0].y == 4

    def test_assembler_3x3(self):
        entities = [EntitySpec("assembling-machine-1", x=2, y=2, direction=0)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "assembling-machine-1"

    def test_oil_refinery_5x5(self):
        entities = [EntitySpec("oil-refinery", x=0, y=0, direction=0)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "oil-refinery"

    def test_rocket_silo_9x9(self):
        entities = [EntitySpec("rocket-silo", x=0, y=0, direction=0)]
        result = _roundtrip(entities)
        assert len(result) == 1
        assert result[0].name == "rocket-silo"


class TestMultiTileGrid:
    def test_furnace_occupies_correct_tiles(self):
        """Verify 2x2 furnace fills exactly 4 tiles."""
        entities = [EntitySpec("stone-furnace", x=0, y=0, direction=0)]
        grid = encode(entities, bounds=BoundingBox(0, 0, 4, 4))
        furnace_id = ENTITY_REGISTRY.from_name("stone-furnace").id

        assert grid[0, 0, 0] == furnace_id
        assert grid[0, 1, 0] == furnace_id
        assert grid[1, 0, 0] == furnace_id
        assert grid[1, 1, 0] == furnace_id
        assert grid[0, 2, 0] == 0  # outside furnace
        assert grid[2, 0, 0] == 0


class TestRealisticBlueprint:
    def test_minimal_smelting(self):
        """Drill → inserter → furnace → belt."""
        entities = [
            EntitySpec("burner-mining-drill", x=0, y=0, direction=8),   # 2x2
            EntitySpec("burner-inserter", x=2, y=0, direction=4),       # 1x1
            EntitySpec("stone-furnace", x=3, y=0, direction=0),         # 2x2
            EntitySpec("transport-belt", x=5, y=0, direction=8),        # 1x1
            EntitySpec("transport-belt", x=5, y=1, direction=8),        # 1x1
        ]
        result = _roundtrip(entities)
        assert len(result) == 5
        names = sorted(e.name for e in result)
        assert names == [
            "burner-inserter",
            "burner-mining-drill",
            "stone-furnace",
            "transport-belt",
            "transport-belt",
        ]

    def test_position_preservation(self):
        """Positions should survive roundtrip exactly."""
        entities = [
            EntitySpec("stone-furnace", x=10, y=20, direction=0),
            EntitySpec("inserter", x=12, y=20, direction=4),
        ]
        bounds = BoundingBox(9, 19, 8, 8)
        result = _roundtrip(entities, bounds=bounds)
        assert len(result) == 2
        furnace = next(e for e in result if e.name == "stone-furnace")
        inserter = next(e for e in result if e.name == "inserter")
        assert furnace.x == 10
        assert furnace.y == 20
        assert inserter.x == 12
        assert inserter.y == 20


class TestAllRegisteredEntities:
    def test_every_entity_survives_roundtrip(self):
        """Each registered entity should encode and decode correctly."""
        for info in ENTITY_REGISTRY.all_entities():
            entities = [EntitySpec(info.name, x=0, y=0, direction=0)]
            result = _roundtrip(entities)
            assert len(result) == 1, f"Failed for {info.name}"
            assert result[0].name == info.name, f"Name mismatch for {info.name}"
