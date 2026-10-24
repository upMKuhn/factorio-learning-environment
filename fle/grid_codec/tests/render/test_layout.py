from fle.grid_codec.render import Direction, Layout
from fle.grid_codec.tests.render.helpers import E, make_grid


def test_groups_multi_tile_entities_by_instance():
    layout = Layout(make_grid(6, 6, [("assembling-machine-1", 1, 1), ("inserter", 4, 2, E)]))
    names = sorted(e.name for e in layout.entities)
    assert names == ["assembling-machine-1", "inserter"]
    am = layout.at(3, 3)
    assert (am.x, am.y, am.w, am.h) == (1, 1, 3, 3)
    assert layout.at(0, 0) is None


def test_rotated_footprint_comes_from_the_grid():
    layout = Layout(make_grid(4, 6, [("steam-engine", 0, 0, E)]))
    engine = layout.entities[0]
    assert (engine.w, engine.h) == (5, 3)
    assert engine.direction is Direction.EAST


def test_recipe_and_lane_channels():
    grid = make_grid(3, 3, [("assembling-machine-1", 0, 0, 0, 7)])
    layout = Layout(grid)
    assert layout.entities[0].recipe_id == 7
    grid4 = make_grid(3, 3, [("assembling-machine-1", 0, 0, 0)], channels=4)
    assert Layout(grid4).entities[0].recipe_id == 0


def test_inserter_faces_its_drop_side():
    layout = Layout(make_grid(1, 1, [("inserter", 0, 0, E)]))
    ins = layout.entities[0]
    assert ins.pickup_side is Direction.EAST
    assert ins.facing is Direction.WEST


def test_unknown_type_ids_are_skipped():
    grid = make_grid(2, 2, [("wooden-chest", 0, 0)])
    grid[1, 1, 0] = 254
    assert [e.name for e in Layout(grid).entities] == ["wooden-chest"]
