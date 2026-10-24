from __future__ import annotations

from fle.grid_codec.blueprints.version_conventions import VersionConventions


class V20Conventions(VersionConventions):
    """2.x (and Space Age): 16-way directions, names as they are."""

    def direction(self, raw: int) -> int:
        return raw

    def entity_name(self, name: str) -> str:
        return name

    def recipe_name(self, name: str) -> str:
        return name
