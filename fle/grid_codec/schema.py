"""Compatibility path; the registry lives in fle.grid_codec.registry."""

from fle.grid_codec.registry import ENTITY_REGISTRY, EntityInfo, EntityRegistry, Footprint, Meta

EntityID = EntityRegistry  # old name

__all__ = ["ENTITY_REGISTRY", "EntityID", "EntityInfo", "EntityRegistry", "Footprint", "Meta"]
