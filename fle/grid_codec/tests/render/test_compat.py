"""The pre-rewrite module paths keep working."""


from fle.grid_codec.tests.render.helpers import make_grid


def test_visualize_exports(data_dir, empty_sprite_dir):
    from fle.grid_codec.visualize import (
        CATEGORY_COLORS, ICON_SIZE, _load_icon_atlas, get_icon, grid_to_human, grid_to_machine,
        grid_to_rgb,
    )
    grid = make_grid(3, 3, [("wooden-chest", 1, 1)])
    assert grid_to_machine(grid, scale=4).size == (12, 12)
    assert grid_to_rgb is grid_to_machine
    img = grid_to_human(grid, str(data_dir), 10, sprite_dir=str(empty_sprite_dir), recipe_index={})
    assert img.mode == "RGB" and img.size == (30, 30)
    sheet, positions = _load_icon_atlas(str(data_dir))
    assert ICON_SIZE == 66 and "wooden-chest" in positions
    assert get_icon("wooden-chest", str(data_dir), 8).size == (8, 8)
    assert "transport" in CATEGORY_COLORS


def test_render_to_file_and_legend(tmp_path, data_dir, empty_sprite_dir):
    from fle.grid_codec.visualize import render_legend, render_to_file
    grid = make_grid(3, 3, [("wooden-chest", 1, 1)])
    render_to_file(grid, tmp_path / "m.png", mode="machine", scale=4)
    render_to_file(grid, tmp_path / "h.png", mode="human", data_dir=str(data_dir), scale=8,
                   sprite_dir=str(empty_sprite_dir))
    render_legend(tmp_path / "legend.png")
    assert all((tmp_path / f).exists() for f in ("m.png", "h.png", "legend.png"))


def test_sprites_exports(sprite_dir):
    from fle.grid_codec.sprites import SPRITE_DIR, build_sprites, load_sprite, sprites_available
    assert sprites_available(str(sprite_dir))
    img, anchor = load_sprite("assembling-machine-1/north", 64, str(sprite_dir))
    assert img.size == (320, 320)
    assert SPRITE_DIR.name == "entities" and callable(build_sprites)
