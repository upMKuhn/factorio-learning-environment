from fle.grid_codec.render.sprites import SpriteCache
from fle.grid_codec.tests.render.helpers import SPRITE_RED


def test_load_scales_to_tile_px(sprite_dir):
    cache = SpriteCache(str(sprite_dir))
    img, anchor = cache.load("assembling-machine-1/north", 32)
    assert img.size == (160, 160) and anchor == (80, 80)
    assert cache.load("nope/north", 32) is None


def test_fit_scales_to_tile_px_then_never_exceeds_the_box(sprite_dir):
    cache = SpriteCache(str(sprite_dir))
    img = cache.fit("assembling-machine-1/east", (60, 45), tile_px=32)
    assert img.size == (45, 45)
    assert cache.fit("assembling-machine-1/east", (400, 400), tile_px=32).size == (160, 160)
    assert cache.fit("nope/north", (10, 10), tile_px=32) is None
    assert img.getpixel((20, 20)) == SPRITE_RED


def test_available(sprite_dir, empty_sprite_dir):
    assert SpriteCache(str(sprite_dir)).available
    assert not SpriteCache(str(empty_sprite_dir)).available
