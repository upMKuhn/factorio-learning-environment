import numpy as np

from fle.grid_codec.render import HumanRenderer
from fle.grid_codec.render.palette import ARROW_COLOR, EMPTY_COLOR
from fle.grid_codec.tests.render.helpers import ICON_COLORS, SPRITE_RED, E, has_color, make_grid, pixels

S = 20  # px per tile
RECIPES = {"iron-gear-wheel": 3}


def _render(grid, data_dir, sprite_dir, recipe_index=None):
    return pixels(HumanRenderer(str(data_dir), S, str(sprite_dir), recipe_index).render(grid))


def test_sprite_is_fitted_inside_its_footprint(data_dir, sprite_dir):
    px = _render(make_grid(7, 7, [("assembling-machine-1", 2, 2)]), data_dir, sprite_dir)
    box = px[2 * S:5 * S, 2 * S:5 * S]
    assert has_color(box, SPRITE_RED)
    outside = px.copy()
    outside[2 * S:5 * S, 2 * S:5 * S] = 0
    assert not has_color(outside, SPRITE_RED)


def test_recipe_icon_over_production_buildings(data_dir, sprite_dir):
    grid = make_grid(5, 5, [("assembling-machine-1", 1, 1, 0, 3)])
    px = _render(grid, data_dir, sprite_dir, RECIPES)
    gear = ICON_COLORS["iron-gear-wheel"]
    centre = px[2 * S:3 * S, 2 * S:3 * S]
    # Drawn semi-transparently: a blend of the sprite and the icon, never the pure icon
    assert not has_color(centre, gear, tol=4)
    assert (np.abs(centre[S // 2, S // 2] - np.array(SPRITE_RED[:3])) > 30).any()
    without = _render(make_grid(5, 5, [("assembling-machine-1", 1, 1)]), data_dir, sprite_dir, RECIPES)
    assert has_color(without[2 * S:3 * S, 2 * S:3 * S], SPRITE_RED, tol=2)


def test_no_recipe_icon_on_entities_without_recipes(data_dir, empty_sprite_dir):
    # A stray recipe id on a chest is ignored
    grid = make_grid(3, 3, [("wooden-chest", 1, 1, 0, 3)])
    px = _render(grid, data_dir, empty_sprite_dir, RECIPES)
    assert not has_color(px, ICON_COLORS["iron-gear-wheel"], tol=40)


def test_fallback_to_icon_without_sprite_cache(data_dir, empty_sprite_dir):
    px = _render(make_grid(3, 3, [("wooden-chest", 1, 1)]), data_dir, empty_sprite_dir)
    tile = px[S:2 * S, S:2 * S]
    assert has_color(tile, ICON_COLORS["wooden-chest"])
    assert not has_color(px, ARROW_COLOR)  # chests have no direction


def test_fallback_arrow_for_directional_entities(data_dir, empty_sprite_dir):
    px = _render(make_grid(3, 3, [("inserter", 1, 1, E)]), data_dir, empty_sprite_dir)
    tile = px[S:2 * S, S:2 * S]
    assert has_color(tile, ICON_COLORS["inserter"])
    arrow = (np.abs(tile - np.array(ARROW_COLOR[:3])).max(axis=-1) < 40)
    cols = arrow.any(axis=0).nonzero()[0]
    # Inserter picks up east, drops west: the arrow points west
    assert cols.min() < S // 2 - 2 and S // 2 - cols.min() > cols.max() - S // 2


def test_unknown_entities_without_icon_get_a_labelled_box(data_dir, empty_sprite_dir):
    px = _render(make_grid(3, 3, [("pipe", 1, 1)]), data_dir, empty_sprite_dir)
    assert not (px[S:2 * S, S:2 * S] == EMPTY_COLOR).all()


def test_empty_grid_renders_background(data_dir, sprite_dir):
    px = _render(make_grid(2, 3, []), data_dir, sprite_dir)
    assert px.shape == (2 * S, 3 * S, 3)


def test_belts_are_tile_aligned_not_recentred(data_dir, tmp_path):
    """A curve sprite whose content fills only one corner stays in that corner."""
    import json
    from PIL import Image
    out = tmp_path / "belt-sprites"
    (out / "transport-belt").mkdir(parents=True)
    index = {}
    for name in ("north", "east", "south", "west", "east_to_north"):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        img.paste(Image.new("RGBA", (32, 32), SPRITE_RED), (0, 0))  # top-left quarter
        img.save(out / "transport-belt" / f"{name}.png")
        index[f"transport-belt/{name}"] = {"anchor": [32, 32]}
    (out / "index.json").write_text(json.dumps({"tile_px": 64, "sprites": index}))
    grid = make_grid(3, 3, [("transport-belt", 0, 1, E), ("transport-belt", 1, 1, 0)])
    px = _render(grid, data_dir, out)
    tile = px[S:2 * S, S:2 * S]
    assert has_color(tile[:S // 2, :S // 2], SPRITE_RED)
    assert not has_color(tile[S // 2 + 1:, S // 2 + 1:], SPRITE_RED)


def test_recipe_icon_sits_on_a_dark_backdrop(data_dir, sprite_dir):
    """Like Factorio's alt-mode, so an item icon never reads as part of the building."""
    grid = make_grid(5, 5, [("assembling-machine-1", 1, 1, 0, 3)])
    px = _render(grid, data_dir, sprite_dir, RECIPES)
    centre = int(2.5 * S)
    below_icon = px[centre + int(0.6 * 3 * S) // 2 + 2, centre]
    assert below_icon[0] < SPRITE_RED[0] - 60
    corner = px[S + 2, S + 2]
    assert tuple(corner) == SPRITE_RED[:3]


def test_recipe_icon_size_is_capped_on_big_buildings(data_dir, empty_sprite_dir):
    grid = make_grid(5, 5, [("oil-refinery", 0, 0, 0, 3)])
    px = _render(grid, data_dir, empty_sprite_dir, RECIPES)
    gear = (np.abs(px - np.array(ICON_COLORS["iron-gear-wheel"][:3])).max(axis=-1) < 60)
    rows = gear.any(axis=1).nonzero()[0]
    assert rows.max() - rows.min() + 1 <= round(1.8 * S)
