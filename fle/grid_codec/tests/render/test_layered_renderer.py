from fle.grid_codec.render import Canvas, HumanRenderer, LayeredRenderer, Layout, MachineRenderer, Renderer
from fle.grid_codec.render.layers import RenderLayer
from fle.grid_codec.tests.render.helpers import make_grid, pixels


class Fill(RenderLayer):
    def __init__(self, color):
        self.color = color

    def draw(self, canvas: Canvas, layout: Layout) -> None:
        canvas.draw.rectangle([0, 0, canvas.image.width - 1, canvas.image.height // 2 - 1], fill=self.color)


def test_layers_are_drawn_in_order_on_translucent_sheets():
    renderer = LayeredRenderer(scale=4, layers=[Fill((255, 0, 0, 255)), Fill((0, 0, 255, 128))])
    px = pixels(renderer.render(make_grid(2, 2, [])))
    r, g, b = px[0, 0]
    assert 120 <= r <= 135 and 120 <= b <= 135  # blue at half alpha over red
    assert tuple(px[7, 0]) == (30, 30, 30)       # untouched background


def test_with_overlays_extends_a_renderer():
    base = MachineRenderer(scale=4)
    combined = base.with_overlays([Fill((0, 255, 0, 255))])
    assert isinstance(combined, Renderer)
    assert combined.layers[:-1] == base.layers
    assert tuple(pixels(combined.render(make_grid(2, 2, [])))[0, 0]) == (0, 255, 0)


def test_renderers_share_the_interface(data_dir, empty_sprite_dir):
    assert isinstance(MachineRenderer(scale=4), Renderer)
    assert isinstance(HumanRenderer(str(data_dir), 8, str(empty_sprite_dir)), Renderer)
