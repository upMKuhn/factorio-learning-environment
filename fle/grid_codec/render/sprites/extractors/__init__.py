"""One graphics extractor per prototype type."""

from __future__ import annotations

from fle.grid_codec.render.sprites.extractors.belt_extractor import BeltExtractor
from fle.grid_codec.render.sprites.extractors.directional_extractor import DirectionalExtractor
from fle.grid_codec.render.sprites.extractors.gate_extractor import GateExtractor
from fle.grid_codec.render.sprites.extractors.graphics_extractor import GraphicsExtractor
from fle.grid_codec.render.sprites.extractors.inserter_extractor import InserterExtractor
from fle.grid_codec.render.sprites.extractors.pipe_extractor import PipeExtractor
from fle.grid_codec.render.sprites.extractors.rail_signal_extractor import RailSignalExtractor
from fle.grid_codec.render.sprites.extractors.splitter_extractor import SplitterExtractor
from fle.grid_codec.render.sprites.extractors.underground_extractor import UndergroundExtractor
from fle.grid_codec.render.sprites.sprite_layer import SpriteLayer

EXTRACTORS: dict[str, GraphicsExtractor] = {
    "transport-belt": BeltExtractor(),
    "underground-belt": UndergroundExtractor(),
    "splitter": SplitterExtractor(),
    "inserter": InserterExtractor(),
    "pipe": PipeExtractor(),
    "gate": GateExtractor(),
    "rail-signal": RailSignalExtractor(),
    "rail-chain-signal": RailSignalExtractor(),
}
DEFAULT_EXTRACTOR = DirectionalExtractor()


def variants_for(proto: dict) -> dict[str, list[SpriteLayer]]:
    """Sprite variants of a prototype, read by the extractor for its type."""
    return EXTRACTORS.get(proto["type"], DEFAULT_EXTRACTOR).variants(proto)


__all__ = [
    "BeltExtractor", "DirectionalExtractor", "EXTRACTORS", "GateExtractor", "GraphicsExtractor",
    "InserterExtractor", "PipeExtractor", "RailSignalExtractor", "SplitterExtractor",
    "UndergroundExtractor", "variants_for",
]
