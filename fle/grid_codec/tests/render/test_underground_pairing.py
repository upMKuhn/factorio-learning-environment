import pytest

from fle.grid_codec.render import Layout, UndergroundPairing
from fle.grid_codec.tests.render.helpers import E, N, W, make_grid


def _pairing(entities, w=16, h=3):
    layout = Layout(make_grid(h, w, entities))
    return layout, UndergroundPairing(layout)


def test_entrance_pairs_with_next_underground_along_flow():
    layout, pairing = _pairing([("underground-belt", 2, 1, E), ("underground-belt", 6, 1, E)])
    entrance, exit_ = layout.at(2, 1), layout.at(6, 1)
    assert not pairing.is_exit(entrance)
    assert pairing.is_exit(exit_)
    assert pairing.partner(entrance) is exit_


def test_westward_flow_walks_right_to_left():
    layout, pairing = _pairing([("underground-belt", 2, 1, W), ("underground-belt", 6, 1, W)])
    assert pairing.is_exit(layout.at(2, 1))
    assert not pairing.is_exit(layout.at(6, 1))


@pytest.mark.parametrize("name, reach", [
    ("underground-belt", 5), ("fast-underground-belt", 7),
    ("express-underground-belt", 9), ("turbo-underground-belt", 11),
])
def test_reach_per_tier(name, reach):
    layout, pairing = _pairing([(name, 0, 1, E), (name, reach, 1, E)], w=24)
    assert pairing.partner(layout.at(0, 1)) is layout.at(reach, 1)
    layout, pairing = _pairing([(name, 0, 1, E), (name, reach + 1, 1, E)], w=24)
    assert pairing.partner(layout.at(0, 1)) is None


def test_tiers_and_lines_do_not_mix():
    layout, pairing = _pairing([
        ("underground-belt", 0, 0, E), ("fast-underground-belt", 3, 0, E),
        ("underground-belt", 0, 1, E), ("underground-belt", 3, 2, E),
    ])
    assert all(pairing.partner(e) is None for e in layout.entities)


def test_two_pairs_on_one_line():
    layout, pairing = _pairing([("underground-belt", x, 1, E) for x in (0, 3, 5, 9)])
    assert [pairing.is_exit(layout.at(x, 1)) for x in (0, 3, 5, 9)] == [False, True, False, True]


def test_lone_exit_fed_from_nothing_but_feeding_a_belt():
    # The entrance lies outside the blueprint: the first underground only outputs
    layout, pairing = _pairing([
        ("underground-belt", 1, 1, E), ("transport-belt", 2, 1, E),
        ("transport-belt", 4, 1, E), ("underground-belt", 5, 1, E), ("underground-belt", 8, 1, E),
    ])
    assert pairing.is_exit(layout.at(1, 1))
    assert not pairing.is_exit(layout.at(5, 1))
    assert pairing.is_exit(layout.at(8, 1))


def test_metadata_flag_wins_over_inference():
    grid = make_grid(1, 8, [("underground-belt", 0, 0, E), ("underground-belt", 3, 0, E)])
    flag = 1 << 12
    grid[0, 0, 2] |= flag  # the first one is the exit according to the encoder
    layout = Layout(grid)
    pairing = UndergroundPairing(layout, exit_flag=flag)
    assert pairing.is_exit(layout.at(0, 0))
    assert not pairing.is_exit(layout.at(3, 0))


def test_vertical_lines():
    layout, pairing = _pairing([("underground-belt", 1, 7, N), ("underground-belt", 1, 2, N)], w=3, h=10)
    assert not pairing.is_exit(layout.at(1, 7))
    assert pairing.is_exit(layout.at(1, 2))
