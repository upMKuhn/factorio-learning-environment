"""Factorio grid codec — encode/decode game state as 2D grid images."""

from fle.grid_codec.decoder import decode
from fle.grid_codec.encoder import encode
from fle.grid_codec.grid import BoundingBox, Channel, EntitySpec, GridDecoder, GridEncoder, Vocabulary
from fle.grid_codec.registry import ENTITY_REGISTRY, EntityRegistry
from fle.grid_codec.schema import EntityID

__all__ = [
    "ENTITY_REGISTRY", "EntityID", "EntityRegistry", "BoundingBox", "Channel", "EntitySpec",
    "GridDecoder", "GridEncoder", "Vocabulary", "encode", "decode",
]
