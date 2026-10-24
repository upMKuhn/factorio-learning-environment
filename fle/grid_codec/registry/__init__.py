"""Entity types the grid can hold: ids, footprints, metadata flags."""

from fle.grid_codec.registry.catalog import ENTITY_REGISTRY
from fle.grid_codec.registry.entity_info import EntityInfo
from fle.grid_codec.registry.entity_registry import EntityRegistry
from fle.grid_codec.registry.footprint import Footprint
from fle.grid_codec.registry.meta import Meta

__all__ = ["ENTITY_REGISTRY", "EntityInfo", "EntityRegistry", "Footprint", "Meta"]
