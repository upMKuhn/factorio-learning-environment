from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterator

from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint


class BlueprintSource(ABC):
    """
    Somewhere blueprints come from. Iterating yields each blueprint within the
    entity range once (identical content is kept once) and fills `stats` with
    what was skipped and why.
    """

    def __init__(self, min_entities: int = 0, max_entities: int | None = None):
        self.min_entities = min_entities
        self.max_entities = max_entities
        self.stats: Counter = Counter()

    @abstractmethod
    def _read(self) -> Iterator[SourceBlueprint]:
        """Every blueprint the source holds, before filtering."""

    def __iter__(self) -> Iterator[SourceBlueprint]:
        self.stats = Counter()
        seen: set[str] = set()
        for bp in self._read():
            self.stats["blueprints in source"] += 1
            if not bp.entities:
                self.stats["empty blueprints"] += 1
            elif bp.entity_count < self.min_entities or (
                    self.max_entities is not None and bp.entity_count > self.max_entities):
                self.stats["outside entity range"] += 1
            elif (key := bp.content_key()) in seen:
                self.stats["duplicate blueprints"] += 1
            else:
                seen.add(key)
                self.stats["unique blueprints"] += 1
                yield bp

    def find(self, label: str) -> SourceBlueprint:
        """First blueprint labelled exactly label, else the first whose label contains it."""
        partial = None
        for bp in self:
            if bp.label == label:
                return bp
            if partial is None and label in bp.label:
                partial = bp
        if partial is None:
            raise KeyError(f"No blueprint labelled {label!r} in {self}")
        return partial
