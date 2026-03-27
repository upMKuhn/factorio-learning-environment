"""
Decode Factorio blueprint strings and convert to EntitySpec.

Blueprint string format: "0" + base64(zlib(json))

The JSON contains entities with name, position, direction — maps directly to EntitySpec.
"""

from __future__ import annotations

import base64
import json
import zlib
from dataclasses import dataclass, field

from fle.grid_codec.encoder import EntitySpec


@dataclass
class Blueprint:
    """A decoded Factorio blueprint with metadata."""
    label: str
    description: str
    entities: list[EntitySpec]
    tags: list[str] = field(default_factory=list)
    source_key: str = ""              # factorioprints key e.g. "-KnQ865j-qQ21WoUPbd3"
    favorites: int = 0

    @property
    def entity_count(self) -> int:
        return len(self.entities)


def decode_blueprint_string(bp_string: str) -> list[dict]:
    """
    Decode a Factorio blueprint string to raw entity dicts.

    Returns list of {"name": str, "position": {"x": float, "y": float}, "direction": int, ...}
    """
    raw = base64.b64decode(bp_string[1:])  # strip version byte "0"
    data = json.loads(zlib.decompress(raw))

    if "blueprint" in data:
        return data["blueprint"].get("entities", [])
    return []


def decode_blueprint_book(bp_string: str) -> list[tuple[dict, list[dict]]]:
    """
    Decode a blueprint book string.

    Returns list of (blueprint_metadata, entities) tuples.
    """
    raw = base64.b64decode(bp_string[1:])
    data = json.loads(zlib.decompress(raw))

    results = []
    if "blueprint_book" in data:
        for entry in data["blueprint_book"].get("blueprints", []):
            bp = entry.get("blueprint", {})
            entities = bp.get("entities", [])
            results.append((bp, entities))
    elif "blueprint" in data:
        bp = data["blueprint"]
        results.append((bp, bp.get("entities", [])))

    return results


def raw_entities_to_specs(raw_entities: list[dict]) -> list[EntitySpec]:
    """
    Convert raw blueprint entity dicts to EntitySpec list.

    Factorio blueprints use center-based positions for multi-tile entities.
    We convert to top-left tile coordinates.
    """
    from fle.grid_codec.schema import ENTITY_REGISTRY

    specs = []
    for ent in raw_entities:
        name = ent.get("name", "")
        if not ENTITY_REGISTRY.has_name(name):
            continue

        info = ENTITY_REGISTRY.from_name(name)
        pos = ent.get("position", {})

        # Blueprint positions are center-based — convert to top-left integer tile
        cx = pos.get("x", 0)
        cy = pos.get("y", 0)
        x = int(cx - info.width / 2 + 0.5)
        y = int(cy - info.height / 2 + 0.5)

        # Direction: Factorio uses 0,2,4,6 in blueprints (N,E,S,W)
        # but FLE uses 0,4,8,12 — multiply by 2
        raw_dir = ent.get("direction", 0)
        direction = raw_dir * 2 if raw_dir <= 7 else raw_dir

        recipe = ent.get("recipe")
        specs.append(EntitySpec(name=name, x=x, y=y, direction=direction, recipe=recipe))

    return specs


def from_blueprint_string(
    bp_string: str,
    label: str = "",
    description: str = "",
    tags: list[str] | None = None,
    source_key: str = "",
    favorites: int = 0,
) -> Blueprint:
    """Decode a blueprint string into a Blueprint object."""
    raw_entities = decode_blueprint_string(bp_string)
    specs = raw_entities_to_specs(raw_entities)

    return Blueprint(
        label=label,
        description=description,
        entities=specs,
        tags=tags or [],
        source_key=source_key,
        favorites=favorites,
    )


def from_cdn_json(cdn_data: dict, source_key: str = "") -> list[Blueprint]:
    """
    Convert a full CDN blueprint JSON (as fetched from factorioprints CDN) into Blueprint(s).

    Handles both single blueprints and blueprint books.
    """
    bp_string = cdn_data.get("blueprintString", "")
    if not bp_string:
        return []

    title = cdn_data.get("title", "")
    description = cdn_data.get("descriptionMarkdown", "")
    tags = cdn_data.get("tags", [])
    if isinstance(tags, dict):
        tags = list(tags.keys())
    favorites = cdn_data.get("numberOfFavorites", 0)

    # Try as book first, then as single
    decoded = decode_blueprint_book(bp_string)

    blueprints = []
    for bp_meta, raw_entities in decoded:
        specs = raw_entities_to_specs(raw_entities)
        if not specs:
            continue

        bp_label = bp_meta.get("label", title)
        bp_desc = bp_meta.get("description", description)

        blueprints.append(Blueprint(
            label=bp_label or title,
            description=bp_desc or description,
            entities=specs,
            tags=tags if isinstance(tags, list) else [],
            source_key=source_key,
            favorites=favorites,
        ))

    return blueprints
