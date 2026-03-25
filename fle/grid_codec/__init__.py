"""Factorio grid codec — encode/decode game state as 2D grid images."""

from fle.grid_codec.schema import EntityID, ENTITY_REGISTRY
from fle.grid_codec.encoder import encode, EntitySpec, BoundingBox
from fle.grid_codec.decoder import decode

__all__ = ["EntityID", "ENTITY_REGISTRY", "encode", "decode", "EntitySpec", "BoundingBox"]
