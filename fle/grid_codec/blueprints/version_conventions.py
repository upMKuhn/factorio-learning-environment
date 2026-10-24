from __future__ import annotations

from abc import ABC, abstractmethod


class VersionConventions(ABC):
    """How one game version writes blueprints: direction scheme and entity/recipe names."""

    @classmethod
    def for_version(cls, version: int | None) -> VersionConventions:
        """Conventions for a packed game version (major in the top 16 bits); None means 2.x."""
        from fle.grid_codec.blueprints.pre20_conventions import Pre20Conventions
        from fle.grid_codec.blueprints.v20_conventions import V20Conventions

        major = 2 if version is None else version >> 48
        return Pre20Conventions() if major < 2 else V20Conventions()

    @abstractmethod
    def direction(self, raw: int) -> int:
        """Blueprint direction → 16-way direction (0=N, 4=E, 8=S, 12=W)."""

    @abstractmethod
    def entity_name(self, name: str) -> str:
        """Blueprint entity name → 2.0 prototype name."""

    @abstractmethod
    def recipe_name(self, name: str) -> str:
        """Blueprint recipe name → 2.0 recipe name."""
