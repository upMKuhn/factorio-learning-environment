"""A pixel surface addressed in tiles."""

from __future__ import annotations

from PIL import Image, ImageDraw

from fle.grid_codec.render.direction import Direction

Box = tuple[int, int, int, int]  # x0, y0, width, height in pixels


class Canvas:
    """An RGBA image of width×height tiles at scale pixels per tile."""

    def __init__(self, width: int, height: int, scale: int,
                 background: tuple[int, ...] | None = (30, 30, 30)):
        self.width, self.height, self.scale = width, height, scale
        fill = (*background[:3], 255) if background else (0, 0, 0, 0)
        self.image = Image.new("RGBA", (width * scale, height * scale), fill)
        self.draw = ImageDraw.Draw(self.image)

    def sheet(self) -> Canvas:
        """A transparent canvas of the same size, to be composited back."""
        return Canvas(self.width, self.height, self.scale, background=None)

    def composite(self, other: Canvas) -> None:
        self.image.alpha_composite(other.image)

    def tile_box(self, x: int, y: int, w: int = 1, h: int = 1) -> Box:
        s = self.scale
        return x * s, y * s, w * s, h * s

    def paste_fitted(self, img: Image.Image, box: Box) -> None:
        """Paste img centred in box, cropped to its content and shrunk (never grown) to fit."""
        bbox = img.getbbox()
        if bbox is None:
            return
        img = img.crop(bbox)
        x0, y0, bw, bh = box
        factor = min(bw / img.width, bh / img.height, 1)
        if factor < 1:
            img = img.resize((max(1, round(img.width * factor)), max(1, round(img.height * factor))),
                             Image.LANCZOS)
        self.image.alpha_composite(img, (x0 + (bw - img.width) // 2, y0 + (bh - img.height) // 2))

    def paste_anchored(self, img: Image.Image, anchor: tuple[int, int], box: Box) -> None:
        """Paste img with its anchor on the centre of box, clipped to box (for tile-aligned sprites)."""
        x0, y0, bw, bh = box
        left, top = x0 + bw // 2 - anchor[0], y0 + bh // 2 - anchor[1]
        window = img.crop((x0 - left, y0 - top, x0 - left + bw, y0 - top + bh))
        self.image.alpha_composite(window, (x0, y0))

    def arrow(self, box: Box, direction: Direction, color: tuple[int, ...]) -> None:
        """A filled triangle in the middle of box, pointing along direction."""
        x0, y0, bw, bh = box
        size = min(bw, bh)
        dx, dy = direction.delta
        cx, cy = x0 + bw // 2, y0 + bh // 2
        r = size // 3
        px, py = -dy, dx
        back, half = r // 3, r * 0.6
        tip = (cx + dx * r, cy + dy * r)
        base1 = (cx - dx * back + px * half, cy - dy * back + py * half)
        base2 = (cx - dx * back - px * half, cy - dy * back - py * half)
        self.draw.polygon([tip, base1, base2], fill=color)

    def rgb(self) -> Image.Image:
        return self.image.convert("RGB")
