from fle.grid_codec.render import IconAtlas
from fle.grid_codec.tests.render.helpers import ICON_COLORS, pixels


def test_icon_lookup_and_resize(data_dir):
    atlas = IconAtlas.shared(str(data_dir))
    icon = atlas.icon("iron-plate", 20)
    assert icon.size == (20, 20)
    assert tuple(pixels(icon)[10, 10]) == ICON_COLORS["iron-plate"][:3]
    assert atlas.icon("no-such-item", 20) is None
    assert "wooden-chest" in atlas


def test_load_is_cached(data_dir):
    assert IconAtlas.shared(str(data_dir)) is IconAtlas.shared(str(data_dir))


def test_fit_is_square_and_may_upscale(data_dir):
    atlas = IconAtlas.shared(str(data_dir))
    assert atlas.fit("iron-plate", (200, 120), tile_px=32).size == (120, 120)
    assert atlas.fit("nope", (10, 10), tile_px=32) is None
