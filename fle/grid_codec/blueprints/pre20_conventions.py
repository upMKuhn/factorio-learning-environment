from __future__ import annotations

from fle.grid_codec.blueprints.version_conventions import VersionConventions

_LOGISTIC_CHESTS = {
    f"logistic-chest-{kind}": f"{kind}-chest"
    for kind in ("active-provider", "passive-provider", "requester", "storage", "buffer")
}


class Pre20Conventions(VersionConventions):
    """0.x and 1.x: 8-way directions and the names 2.0 replaced."""

    ENTITY_RENAMES: dict[str, str] = {
        "filter-inserter": "fast-inserter",
        "stack-filter-inserter": "bulk-inserter",
        "stack-inserter": "bulk-inserter",  # 2.0's stack-inserter is Space Age's new one
        **_LOGISTIC_CHESTS,
    }
    RECIPE_RENAMES: dict[str, str] = {
        **ENTITY_RENAMES,
        "science-pack-1": "automation-science-pack",
        "science-pack-2": "logistic-science-pack",
        "science-pack-3": "chemical-science-pack",
        "high-tech-science-pack": "utility-science-pack",
        "effectivity-module": "efficiency-module",
        "effectivity-module-2": "efficiency-module-2",
        "effectivity-module-3": "efficiency-module-3",
        "empty-barrel": "barrel",
        **{f"fill-{fluid}-barrel": f"{fluid}-barrel" for fluid in (
            "crude-oil", "heavy-oil", "light-oil", "lubricant", "petroleum-gas", "sulfuric-acid", "water",
        )},
    }

    def direction(self, raw: int) -> int:
        return raw * 2

    def entity_name(self, name: str) -> str:
        return self.ENTITY_RENAMES.get(name, name)

    def recipe_name(self, name: str) -> str:
        return self.RECIPE_RENAMES.get(name, name)
