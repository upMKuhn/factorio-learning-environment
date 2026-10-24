from fle.grid_codec.render import Direction


def test_snap_rounds_16_way_to_nearest_cardinal():
    assert Direction.snap(0) is Direction.NORTH
    assert Direction.snap(3) is Direction.EAST
    assert Direction.snap(9) is Direction.SOUTH
    assert Direction.snap(13) is Direction.WEST
    assert Direction.snap(15) is Direction.NORTH


def test_delta_points_along_grid_axes():
    assert Direction.NORTH.delta == (0, -1)
    assert Direction.EAST.delta == (1, 0)
    assert Direction.SOUTH.delta == (0, 1)
    assert Direction.WEST.delta == (-1, 0)


def test_opposite_and_label():
    assert Direction.EAST.opposite is Direction.WEST
    assert Direction.NORTH.opposite is Direction.SOUTH
    assert Direction.WEST.label == "west"


def test_left_and_right_relative_to_travel():
    assert Direction.NORTH.left is Direction.WEST
    assert Direction.NORTH.right is Direction.EAST
    assert Direction.EAST.left is Direction.NORTH
