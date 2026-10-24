"""
Community and synthetic blueprints → normalized layouts.

Sources (JsonlBlueprintSource, SyntheticBlueprintSource) yield SourceBlueprints;
BlueprintNormalizer turns each into a Layout of top-left tiles with 16-way
directions and 2.0 names (VersionConventions), or rejects it with a counted
reason.
"""

from fle.grid_codec.blueprints.blueprint_normalizer import BlueprintNormalizer
from fle.grid_codec.blueprints.blueprint_rejected import BlueprintRejected
from fle.grid_codec.blueprints.blueprint_source import BlueprintSource
from fle.grid_codec.blueprints.blueprint_string import BlueprintString
from fle.grid_codec.blueprints.jsonl_blueprint_source import JsonlBlueprintSource
from fle.grid_codec.blueprints.layout import Layout
from fle.grid_codec.blueprints.legacy import (
    blueprint_entities, decode_blueprint_string, encode_entities, find_blueprint, iter_blueprints,
)
from fle.grid_codec.blueprints.pre20_conventions import Pre20Conventions
from fle.grid_codec.blueprints.recipe_data import RecipeData
from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint
from fle.grid_codec.blueprints.synthetic_blueprint_source import SyntheticBlueprintSource
from fle.grid_codec.blueprints.v20_conventions import V20Conventions
from fle.grid_codec.blueprints.version_conventions import VersionConventions

__all__ = [
    "BlueprintNormalizer", "BlueprintRejected", "BlueprintSource", "BlueprintString", "JsonlBlueprintSource",
    "Layout", "Pre20Conventions", "RecipeData", "SourceBlueprint", "SyntheticBlueprintSource",
    "V20Conventions", "VersionConventions",
    # legacy dict API
    "blueprint_entities", "decode_blueprint_string", "encode_entities", "find_blueprint", "iter_blueprints",
]
