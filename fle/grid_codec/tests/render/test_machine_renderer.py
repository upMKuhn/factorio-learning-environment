from fle.grid_codec.render import MachineRenderer
from fle.grid_codec.render.palette import CATEGORY_COLORS
from fle.grid_codec.tests.render.helpers import make_grid, pixels


def test_size_and_category_colour():
    grid = make_grid(4, 5, [("wooden-chest", 1, 1)])
    img = MachineRenderer(scale=8).render(grid)
    assert img.size == (40, 32)
    # North-facing tiles are shaded slightly darker than the category colour
    assert (abs(pixels(img)[12, 12] - CATEGORY_COLORS["logistics"]) <= 15).all()


def test_unknown_ids_are_magenta():
    grid = make_grid(2, 2, [])
    grid[0, 0, 0] = 254
    assert tuple(pixels(MachineRenderer(scale=8).render(grid))[4, 4]) == (255, 0, 255)


def test_accepts_extra_channels():
    grid = make_grid(2, 2, [("transport-belt", 0, 0, 4)], channels=7)
    MachineRenderer(scale=8).render(grid)
