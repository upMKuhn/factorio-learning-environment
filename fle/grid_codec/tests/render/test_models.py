"""Value objects are pydantic models."""

import pydantic
import pytest

from fle.grid_codec.render import Layout, PlacedEntity
from fle.grid_codec.render.palette import PALETTE, Palette
from fle.grid_codec.render.sprites import SpriteEntry, SpriteIndex, SpriteLayer
from fle.grid_codec.tests.render.helpers import make_grid


def test_placed_entity_is_frozen():
    e = Layout(make_grid(1, 1, [("wooden-chest", 0, 0)])).entities[0]
    assert isinstance(e, pydantic.BaseModel) and isinstance(e, PlacedEntity)
    with pytest.raises(pydantic.ValidationError):
        e.x = 3


def test_sprite_index_round_trip(tmp_path):
    index = SpriteIndex(tile_px=64, sprites={"pipe/1010": SpriteEntry(anchor=(32, 40))})
    path = tmp_path / "index.json"
    index.save(path)
    loaded = SpriteIndex.load(path)
    assert loaded.sprites["pipe/1010"].anchor == (32, 40) and loaded.tile_px == 64


def test_sprite_index_rejects_malformed_files(tmp_path):
    path = tmp_path / "index.json"
    path.write_text('{"tile_px": 64, "sprites": {"pipe/1010": {"anchor": "middle"}}}')
    with pytest.raises(pydantic.ValidationError):
        SpriteIndex.load(path)


def test_missing_index_is_empty(tmp_path):
    assert SpriteIndex.load(tmp_path / "nope.json").sprites == {}


def test_sprite_layer_is_a_model():
    layer = SpriteLayer.from_spec({"filename": "f.png", "size": 64, "scale": 0.5})
    assert isinstance(layer, pydantic.BaseModel)
    assert layer.model_copy(update={"rotate": 90}).rotate == 90


def test_palette_defaults_and_overrides():
    assert PALETTE.category_colors["transport"] == (60, 160, 220)
    dark = Palette(empty=(0, 0, 0))
    assert dark.empty == (0, 0, 0) and dark.category_colors == PALETTE.category_colors
    with pytest.raises(pydantic.ValidationError):
        PALETTE.empty = (1, 1, 1)
