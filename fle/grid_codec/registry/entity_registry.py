from __future__ import annotations

from typing import Iterable

from fle.grid_codec.registry.entity_info import EntityInfo


class EntityRegistry:
    """Bidirectional entity name ↔ grid id lookup."""
    EMPTY = 0

    def __init__(self, entities: Iterable[EntityInfo]):
        self._by_name: dict[str, EntityInfo] = {}
        self._by_id: dict[int, EntityInfo] = {}
        for info in entities:
            if info.id == self.EMPTY or info.id in self._by_id or info.name in self._by_name:
                raise ValueError(f"Duplicate or reserved registry entry: {info}")
            self._by_name[info.name] = info
            self._by_id[info.id] = info

    def from_name(self, name: str) -> EntityInfo:
        return self._by_name[name]

    def from_id(self, id_: int) -> EntityInfo:
        return self._by_id[id_]

    def get(self, name: str) -> EntityInfo | None:
        return self._by_name.get(name)

    def has_name(self, name: str) -> bool:
        return name in self._by_name

    def has_id(self, id_: int) -> bool:
        return id_ in self._by_id

    def __contains__(self, name: str) -> bool:
        return name in self._by_name

    def all_entities(self) -> list[EntityInfo]:
        """All registered entities sorted by id."""
        return sorted(self._by_id.values(), key=lambda e: e.id)

    def names(self) -> list[str]:
        return list(self._by_name)

    def ids(self) -> list[int]:
        return sorted(self._by_id)
