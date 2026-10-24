"""
Grid rendering.

    MachineRenderer(scale).render(grid)                       category colours + arrows
    HumanRenderer(data_dir, scale, sprite_dir, recipe_index)  in-game sprites

Renderers are LayeredRenderers: stacks of RenderLayers (fle.grid_codec.render.layers)
drawn over a Layout, the grid parsed into PlacedEntities. The human renderer's
entity layer hands each entity to the first EntityDrawer strategy that can draw it
(fle.grid_codec.render.drawers); sprites come from a SpriteSource — the sprite
cache (fle.grid_codec.render.sprites) or the icon atlas.
"""

from fle.grid_codec.render.belt_connections import BeltConnections
from fle.grid_codec.render.canvas import Canvas
from fle.grid_codec.render.direction import Direction
from fle.grid_codec.render.human_renderer import HumanRenderer
from fle.grid_codec.render.icon_atlas import IconAtlas
from fle.grid_codec.render.layered_renderer import LayeredRenderer
from fle.grid_codec.render.layout import Layout
from fle.grid_codec.render.machine_renderer import MachineRenderer
from fle.grid_codec.render.placed_entity import PlacedEntity
from fle.grid_codec.render.renderer import Renderer
from fle.grid_codec.render.sprite_source import SpriteSource
from fle.grid_codec.render.underground_pairing import UndergroundPairing

__all__ = [
    "BeltConnections", "Canvas", "Direction", "HumanRenderer", "IconAtlas", "LayeredRenderer",
    "Layout", "MachineRenderer", "PlacedEntity", "Renderer", "SpriteSource", "UndergroundPairing",
]
