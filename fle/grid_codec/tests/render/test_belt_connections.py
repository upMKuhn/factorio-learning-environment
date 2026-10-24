from fle.grid_codec.render import BeltConnections, Direction, Layout, UndergroundPairing
from fle.grid_codec.tests.render.helpers import E, N, S, W, make_grid


def _curve(entities, at, w=5, h=5):
    layout = Layout(make_grid(h, w, entities))
    return BeltConnections(layout, UndergroundPairing(layout)).curve(layout.at(*at))


def test_straight_belt_fed_from_behind():
    assert _curve([("transport-belt", 2, 3, N), ("transport-belt", 2, 2, N)], (2, 2)) is None


def test_single_side_input_curves():
    # Fed by an east-moving belt on its west side: it turns from east to north
    assert _curve([("transport-belt", 1, 2, E), ("transport-belt", 2, 2, N)], (2, 2)) is Direction.EAST


def test_side_input_with_rear_input_is_a_sideload():
    entities = [("transport-belt", 1, 2, E), ("transport-belt", 2, 3, N), ("transport-belt", 2, 2, N)]
    assert _curve(entities, (2, 2)) is None


def test_inputs_from_both_sides_stay_straight():
    entities = [("transport-belt", 1, 2, E), ("transport-belt", 3, 2, W), ("transport-belt", 2, 2, N)]
    assert _curve(entities, (2, 2)) is None


def test_side_belt_pointing_away_is_not_an_input():
    assert _curve([("transport-belt", 1, 2, W), ("transport-belt", 2, 2, N)], (2, 2)) is None


def test_underground_exit_feeds_like_a_belt():
    entities = [("underground-belt", 0, 1, S), ("underground-belt", 0, 3, S), ("transport-belt", 0, 4, E)]
    assert _curve(entities, (0, 4)) is Direction.SOUTH


def test_underground_entrance_does_not_feed():
    entities = [("transport-belt", 0, 0, S), ("underground-belt", 0, 1, S), ("transport-belt", 0, 2, E)]
    assert _curve(entities, (0, 2), w=3, h=3) is None


def test_splitter_feeds_from_each_tile():
    entities = [("splitter", 1, 0, S), ("transport-belt", 2, 1, W)]
    assert _curve(entities, (2, 1)) is Direction.SOUTH


def test_non_belts_have_no_curve():
    assert _curve([("wooden-chest", 1, 1)], (1, 1)) is None
