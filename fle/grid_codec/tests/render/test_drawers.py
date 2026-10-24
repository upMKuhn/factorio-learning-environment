"""Which sprite variant each kind of entity resolves to."""

import pytest

from fle.grid_codec.render import Layout
from fle.grid_codec.render.drawers import (
    BeltDrawer, IconFallbackDrawer, PipeDrawer, SplitterDrawer, SpriteDrawer, UndergroundDrawer,
)
from fle.grid_codec.render.sprites import SpriteCache
from fle.grid_codec.tests.render.helpers import E, N, W, make_grid


@pytest.fixture
def sprites(empty_sprite_dir):
    return SpriteCache(str(empty_sprite_dir))


def _layout(entities, w=6, h=6):
    return Layout(make_grid(h, w, entities))


def test_generic_key_is_entity_and_direction(sprites):
    layout = _layout([("assembling-machine-2", 0, 0, E)])
    assert SpriteDrawer(sprites).key(layout.at(0, 0), layout) == "assembling-machine-2/east"


def test_inserter_key_uses_its_grid_direction(sprites):
    # The sprite builder draws the arm toward the drop side for each pickup direction
    layout = _layout([("inserter", 0, 0, N)])
    assert SpriteDrawer(sprites).key(layout.at(0, 0), layout) == "inserter/north"


def test_16_way_direction_is_snapped(sprites):
    layout = _layout([("rail-signal", 0, 0, 3)])
    assert SpriteDrawer(sprites).key(layout.at(0, 0), layout) == "rail-signal/east"


def test_underground_entrance_and_exit(sprites):
    layout = _layout([("underground-belt", 0, 1, E), ("underground-belt", 4, 1, E)])
    drawer = UndergroundDrawer(sprites)
    assert drawer.applies(layout.at(0, 1))
    assert drawer.key(layout.at(0, 1), layout) == "underground-belt/east-in"
    assert drawer.key(layout.at(4, 1), layout) == "underground-belt/east-out"


def test_belt_curve_key(sprites):
    layout = _layout([("transport-belt", 1, 2, E), ("transport-belt", 2, 2, N)])
    drawer = BeltDrawer(sprites)
    assert drawer.key(layout.at(2, 2), layout) == "transport-belt/east_to_north"
    assert drawer.key(layout.at(1, 2), layout) == "transport-belt/east"
    assert not drawer.applies(_layout([("splitter", 0, 0)]).at(0, 0))


def test_pipe_mask_is_north_east_south_west(sprites):
    layout = _layout([("pipe", 1, 1), ("pipe", 1, 0), ("pipe", 2, 1), ("wooden-chest", 0, 1)])
    drawer = PipeDrawer(sprites)
    assert drawer.key(layout.at(1, 1), layout) == "pipe/1100"
    assert drawer.key(layout.at(1, 0), layout) == "pipe/0010"
    assert drawer.key(layout.at(2, 1), layout) == "pipe/0001"


def test_pipe_connects_to_fluid_machines(sprites):
    layout = _layout([("pipe", 3, 1), ("chemical-plant", 0, 0)])
    assert PipeDrawer(sprites).key(layout.at(3, 1), layout) == "pipe/0001"


def test_pipe_to_ground_connects_only_on_its_open_side(sprites):
    layout = _layout([("pipe", 1, 1), ("pipe-to-ground", 1, 2, N), ("pipe-to-ground", 2, 1, N)])
    assert PipeDrawer(sprites).key(layout.at(1, 1), layout) == "pipe/0010"


def test_pipe_to_ground_key_is_directional(sprites):
    layout = _layout([("pipe-to-ground", 0, 0, W)])
    assert PipeDrawer(sprites).applies(layout.at(0, 0))
    assert PipeDrawer(sprites).key(layout.at(0, 0), layout) == "pipe-to-ground/west"


def test_ground_pieces_are_anchored(sprites):
    assert BeltDrawer.anchored and UndergroundDrawer.anchored and PipeDrawer.anchored
    assert not SpriteDrawer.anchored and not SplitterDrawer.anchored


def test_splitter_draws_belts_underneath(sprites):
    layout = _layout([("fast-splitter", 0, 0, N)])
    drawer = SplitterDrawer(sprites)
    assert drawer.applies(layout.at(0, 0))
    assert drawer.belt_key(layout.at(0, 0)) == "fast-transport-belt/north"


def test_sprite_drawer_declines_without_sprite(sprites):
    from fle.grid_codec.render import Canvas
    layout = _layout([("wooden-chest", 0, 0)])
    assert SpriteDrawer(sprites).draw(Canvas(6, 6, 10), layout.at(0, 0), layout) is False


def test_fallback_drawer_applies_to_everything(data_dir):
    from fle.grid_codec.render import IconAtlas
    layout = _layout([("wooden-chest", 0, 0)])
    assert IconFallbackDrawer(IconAtlas.shared(str(data_dir))).applies(layout.at(0, 0))
