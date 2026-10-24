"""Prototype definitions (as in data-raw-dump.json) → sprite layers per variant."""

from fle.grid_codec.render.sprites import SpriteLayer
from fle.grid_codec.render.sprites.extractors import variants_for


def _sheet(file, **kw):
    return {"filename": file, "width": 64, "height": 64, "scale": 0.5, **kw}


BELT = {
    "type": "transport-belt", "name": "transport-belt",
    "belt_animation_set": {"animation_set": {"filename": "belt.png", "size": 128, "scale": 0.5,
                                             "frame_count": 16, "direction_count": 20}},
}


def test_belt_rows_follow_factorio_default_indices():
    variants = variants_for(BELT)
    row = {k: v[0].y // 128 for k, v in variants.items()}
    assert row["east"] == 0 and row["west"] == 1 and row["north"] == 2 and row["south"] == 3
    assert row["east_to_north"] == 4 and row["north_to_east"] == 5
    assert row["west_to_north"] == 6 and row["north_to_west"] == 7
    assert row["south_to_east"] == 8 and row["east_to_south"] == 9
    assert row["south_to_west"] == 10 and row["west_to_south"] == 11


def test_underground_has_in_and_out_per_direction_on_a_belt_end():
    proto = {
        "type": "underground-belt", "name": "underground-belt",
        "belt_animation_set": BELT["belt_animation_set"],
        "structure": {"direction_in": {"sheet": _sheet("ug.png")},
                      "direction_out": {"sheet": _sheet("ug.png", y=64)}},
    }
    variants = variants_for(proto)
    assert set(variants) == {f"{d}-{end}" for d in ("north", "east", "south", "west") for end in ("in", "out")}
    # Half a straight belt on the open side, under the hood: behind for entrances, ahead for exits
    belt_in, belt_out = variants["east-in"][0], variants["east-out"][0]
    assert belt_in.file == belt_out.file == "belt.png"
    assert belt_in.y == belt_out.y == 0  # the straight "east" row
    assert (belt_in.width, belt_in.height) == (64, 128)
    assert belt_in.x == 0 and belt_in.shift == (-0.25, 0.0)
    assert belt_out.x == 64 and belt_out.shift == (0.25, 0.0)
    north_in = variants["north-in"][0]
    assert (north_in.y, north_in.height, north_in.shift) == (2 * 128 + 64, 64, (0.0, 0.25))
    assert variants["east-in"][-1].file == "ug.png"


def test_shadows_and_glows_are_dropped():
    proto = {"type": "container", "name": "x", "picture": {"layers": [
        _sheet("a.png"), _sheet("shadow.png", draw_as_shadow=True), _sheet("glow.png", draw_as_glow=True)]}}
    assert [l.file for l in variants_for(proto)["north"]] == ["a.png"]


def test_logistic_chest_uses_robot_door_animation():
    proto = {"type": "logistic-container", "name": "passive-provider-chest",
             "robot_door": {"animation": {"layers": [_sheet("chest.png", frame_count=7)]}}}
    assert variants_for(proto)["north"][0].file == "chest.png"


def test_machine_idle_animation():
    proto = {"type": "assembling-machine", "name": "centrifuge",
             "graphics_set": {"idle_animation": {"layers": [_sheet("c.png")]}}}
    assert variants_for(proto)["east"][0].file == "c.png"


def test_per_direction_graphics_sets():
    proto = {"type": "fusion-generator", "name": "fusion-generator", "graphics_set": {
        f"{d}_graphics_set": {"animation": {"layers": [_sheet(f"{d}.png")]}}
        for d in ("north", "east", "south", "west")}}
    variants = variants_for(proto)
    assert variants["west"][0].file == "west.png" and variants["north"][0].file == "north.png"


def test_gate_orientation():
    proto = {"type": "gate", "name": "gate",
             "vertical_animation": {"layers": [_sheet("v.png")]},
             "horizontal_animation": {"layers": [_sheet("h.png")]}}
    variants = variants_for(proto)
    assert variants["north"][0].file == "v.png" and variants["east"][0].file == "h.png"


def test_rail_signal_row_per_direction():
    proto = {"type": "rail-signal", "name": "rail-signal", "ground_picture_set": {"structure": {"layers": [
        {"filename": "rs.png", "width": 128, "height": 128, "frame_count": 3, "direction_count": 16,
         "line_length": 3, "scale": 0.5}]}}}
    variants = variants_for(proto)
    assert variants["north"][0].y == 0 and variants["east"][0].y == 4 * 128


def test_pipe_shapes_by_mask():
    pictures = {k: _sheet(f"{k}.png") for k in (
        "straight_vertical_single", "ending_up", "ending_right", "ending_down", "ending_left",
        "straight_vertical", "straight_horizontal", "corner_up_right", "corner_up_left",
        "corner_down_right", "corner_down_left", "t_up", "t_down", "t_right", "t_left", "cross")}
    variants = variants_for({"type": "pipe", "name": "pipe", "pictures": pictures})
    assert variants["1100"][0].file == "corner_up_right.png"
    assert variants["0101"][0].file == "straight_horizontal.png"
    assert len(variants) == 16


def test_inserter_arm_points_to_drop_side():
    proto = {"type": "inserter", "name": "inserter",
             "platform_picture": {"sheet": _sheet("platform.png")},
             "hand_base_picture": _sheet("base.png"), "hand_open_picture": _sheet("hand.png")}
    variants = variants_for(proto)
    hand = variants["east"][-1]  # picks up east, drops west
    assert hand.file == "hand.png" and hand.shift[0] < 0 and hand.shift[1] == 0
    hand = variants["north"][-1]
    assert hand.shift[1] > 0


def test_layer_from_spec_frame_offsets():
    layer = SpriteLayer.from_spec({"filename": "f.png", "width": 10, "height": 20, "line_length": 4}, frame=5)
    assert (layer.x, layer.y) == (10, 20)
