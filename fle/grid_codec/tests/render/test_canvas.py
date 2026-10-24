from PIL import Image

from fle.grid_codec.render import Canvas, Direction
from fle.grid_codec.tests.render.helpers import has_color, pixels

RED = (200, 30, 30, 255)


def test_fitted_image_stays_inside_its_box_and_is_centred():
    canvas = Canvas(6, 6, scale=10)
    canvas.paste_fitted(Image.new("RGBA", (300, 100), RED), (10, 10, 30, 30))
    px = pixels(canvas.image)
    inside = px[10:40, 10:40]
    outside = px.copy()
    outside[10:40, 10:40] = 0
    assert has_color(inside, RED)
    assert not has_color(outside, RED)
    rows = (px[:, :, 0] == 200).any(axis=1).nonzero()[0]
    assert (rows.min(), rows.max()) == (20, 29)  # 30×10 after shrinking, centred vertically


def test_small_images_are_not_upscaled():
    canvas = Canvas(4, 4, scale=10)
    canvas.paste_fitted(Image.new("RGBA", (4, 4), RED), (0, 0, 40, 40))
    assert (pixels(canvas.image)[:, :, 0] == 200).sum() == 16


def test_transparent_margins_are_cropped_before_fitting():
    sprite = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    sprite.paste(Image.new("RGBA", (20, 20), RED), (0, 0))
    canvas = Canvas(2, 2, scale=10)
    canvas.paste_fitted(sprite, (0, 0, 20, 20))
    assert (pixels(canvas.image)[:, :, 0] == 200).sum() == 400


def test_arrow_points_along_direction():
    canvas = Canvas(1, 1, scale=30, background=(0, 0, 0))
    canvas.arrow((0, 0, 30, 30), Direction.EAST, (255, 255, 0))
    px = pixels(canvas.image)
    yellow = (px[:, :, 0] > 200) & (px[:, :, 1] > 200)
    cols = yellow.any(axis=0).nonzero()[0]
    # The tip is right of centre, the base only a little left of it
    assert cols.max() - 15 > 15 - cols.min()


def test_anchored_paste_keeps_alignment_and_clips_to_the_box():
    # 3×3-tile image whose content sits in its top-left tile; anchor at its centre
    img = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (10, 10), RED), (0, 0))
    canvas = Canvas(5, 5, scale=10, background=(0, 0, 0))
    canvas.paste_anchored(img, (15, 15), (20, 20, 10, 10))
    px = pixels(canvas.image)
    # Content is not re-centred: it would land on tile (1, 1), outside the box, so it is clipped
    assert not has_color(px, RED)
    canvas.paste_anchored(img, (5, 5), (20, 20, 10, 10))
    assert (px := pixels(canvas.image))[20:30, 20:30, 0].min() == 200
    assert (px[:, :, 0] == 200).sum() == 100
