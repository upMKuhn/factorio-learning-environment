"""One cached sprite's metadata."""

from pydantic import BaseModel


class SpriteEntry(BaseModel):
    anchor: tuple[int, int]  # entity centre in the sprite, in cache pixels
