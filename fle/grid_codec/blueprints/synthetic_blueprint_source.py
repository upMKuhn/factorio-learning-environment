from __future__ import annotations

import random
from typing import Iterator

from fle.grid_codec.blueprints.blueprint_source import BlueprintSource
from fle.grid_codec.blueprints.source_blueprint import SourceBlueprint


class SyntheticBlueprintSource(BlueprintSource):
    """Generated patterns from factorio_architect.data.synthetic, already in grid form; reproducible per seed."""

    def __init__(self, seed: int = 0, variations_per_pattern: int = 5,
                 min_entities: int = 0, max_entities: int | None = None):
        super().__init__(min_entities, max_entities)
        self.seed = seed
        self.variations_per_pattern = variations_per_pattern

    def _read(self) -> Iterator[SourceBlueprint]:
        from factorio_architect.data.synthetic import generate_all

        state = random.getstate()
        random.seed(self.seed)  # generate_all draws from the global RNG
        try:
            generated = generate_all(variations_per_pattern=self.variations_per_pattern)
        finally:
            random.setstate(state)
        for s in generated:
            yield SourceBlueprint(label=s.get("label", ""), entities=s["entities"],
                                  tags=tuple(s.get("tags", ("synthetic",))), favorites=s.get("favorites", 0))

    def __repr__(self) -> str:
        return f"SyntheticBlueprintSource(seed={self.seed})"
