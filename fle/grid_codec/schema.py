"""
Entity ID registry and grid channel encoding spec.

Maps Factorio prototype names to uint8 IDs for grid encoding.
Only placeable entities (those with an entity class in FLE) get IDs.

Grid format: (H, W, 4) uint8 numpy array
  Channel 0 (R): entity type ID (0 = empty, 1-255 = entity)
  Channel 1 (G): direction (0-15, matches FLE Direction enum)
  Channel 2 (B): metadata bitmask
  Channel 3 (A): instance ID for multi-tile entity grouping
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag


# ── Metadata bitmask (channel 2) ──────────────────────────────────────────────

class Meta(IntFlag):
    """Bitmask flags stored in the blue channel."""
    NONE = 0
    HAS_RECIPE = 1       # entity can have a recipe set
    IS_FLUID = 2         # entity handles fluids
    IS_ELECTRIC = 4      # entity uses electric power
    IS_BURNER = 8        # entity uses burner fuel
    IS_INSERTER = 16     # entity is an inserter
    IS_BELT = 32         # entity is a transport belt / underground / splitter
    IS_RESOURCE = 64     # tile contains a resource patch


# ── Entity size lookup ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EntityInfo:
    """Static info about a placeable entity type."""
    id: int                # uint8 grid ID (1-255)
    name: str              # FLE prototype name, e.g. "stone-furnace"
    width: int             # tile width
    height: int            # tile height
    meta: Meta             # default metadata flags
    category: str          # grouping: resource, transport, production, power, logistics, combat, circuit


# ── Registry ──────────────────────────────────────────────────────────────────
# Manually curated from FLE Prototype enum (game_types.py) + entity dimensions
# (entities.py). Only placeable entities — items (entity_class=None) excluded.
#
# IDs are grouped by category for readability:
#   1-19:   resource extraction
#   20-49:  transport (belts, pipes, pumps)
#   50-99:  production (furnaces, assemblers, refineries)
#   100-129: power
#   130-159: logistics (chests, robots, trains)
#   160-189: combat
#   190-219: circuit network
#   220-239: reserved
#   240-255: special (groups, markers)

_ENTITIES: list[tuple[int, str, int, int, Meta, str]] = [
    # ── Resource extraction ───────────────────────────────────────────────────
    (1,  "burner-mining-drill",     2, 2, Meta.IS_BURNER,                           "resource"),
    (2,  "electric-mining-drill",   3, 3, Meta.IS_ELECTRIC,                         "resource"),
    (3,  "pumpjack",                3, 3, Meta.IS_ELECTRIC | Meta.IS_FLUID,         "resource"),
    (4,  "offshore-pump",           1, 2, Meta.IS_FLUID,                            "resource"),

    # ── Transport: belts ──────────────────────────────────────────────────────
    (20, "transport-belt",          1, 1, Meta.IS_BELT,                             "transport"),
    (21, "fast-transport-belt",     1, 1, Meta.IS_BELT,                             "transport"),
    (22, "express-transport-belt",  1, 1, Meta.IS_BELT,                             "transport"),
    (23, "underground-belt",        1, 1, Meta.IS_BELT,                             "transport"),
    (24, "fast-underground-belt",   1, 1, Meta.IS_BELT,                             "transport"),
    (25, "express-underground-belt",1, 1, Meta.IS_BELT,                             "transport"),
    (26, "splitter",                2, 1, Meta.IS_BELT,                             "transport"),
    (27, "fast-splitter",           2, 1, Meta.IS_BELT,                             "transport"),
    (28, "express-splitter",        2, 1, Meta.IS_BELT,                             "transport"),

    # ── Transport: inserters ──────────────────────────────────────────────────
    (30, "inserter",                1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (31, "burner-inserter",         1, 1, Meta.IS_INSERTER | Meta.IS_BURNER,        "transport"),
    (32, "long-handed-inserter",    1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (33, "fast-inserter",           1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (34, "bulk-inserter",           1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),

    # ── Transport: pipes ──────────────────────────────────────────────────────
    (40, "pipe",                    1, 1, Meta.IS_FLUID,                            "transport"),
    (41, "pipe-to-ground",          1, 1, Meta.IS_FLUID,                            "transport"),
    (42, "pump",                    1, 2, Meta.IS_FLUID | Meta.IS_ELECTRIC,         "transport"),
    (43, "storage-tank",            3, 3, Meta.IS_FLUID,                            "transport"),

    # ── Production: furnaces ──────────────────────────────────────────────────
    (50, "stone-furnace",           2, 2, Meta.HAS_RECIPE | Meta.IS_BURNER,         "production"),
    (51, "steel-furnace",           2, 2, Meta.HAS_RECIPE | Meta.IS_BURNER,         "production"),
    (52, "electric-furnace",        3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),

    # ── Production: assemblers ────────────────────────────────────────────────
    (55, "assembling-machine-1",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (56, "assembling-machine-2",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (57, "assembling-machine-3",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (58, "centrifuge",              3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),

    # ── Production: oil & chemistry ───────────────────────────────────────────
    (60, "oil-refinery",            5, 5, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),
    (61, "chemical-plant",          3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),

    # ── Production: other ─────────────────────────────────────────────────────
    (65, "lab",                     3, 3, Meta.IS_ELECTRIC,                         "production"),
    (66, "rocket-silo",            9, 9, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (67, "beacon",                  3, 3, Meta.IS_ELECTRIC,                         "production"),

    # ── Power ─────────────────────────────────────────────────────────────────
    (100, "boiler",                 3, 2, Meta.IS_BURNER | Meta.IS_FLUID,           "power"),
    (101, "steam-engine",           5, 3, Meta.IS_FLUID,                            "power"),
    (102, "solar-panel",            3, 3, Meta.NONE,                                "power"),
    (103, "accumulator",            2, 2, Meta.IS_ELECTRIC,                         "power"),
    (104, "small-electric-pole",    1, 1, Meta.IS_ELECTRIC,                         "power"),
    (105, "medium-electric-pole",   1, 1, Meta.IS_ELECTRIC,                         "power"),
    (106, "big-electric-pole",      2, 2, Meta.IS_ELECTRIC,                         "power"),
    (107, "substation",             2, 2, Meta.IS_ELECTRIC,                         "power"),
    (108, "nuclear-reactor",        5, 5, Meta.IS_FLUID,                            "power"),
    (109, "heat-exchanger",         3, 2, Meta.IS_FLUID,                            "power"),
    (110, "steam-turbine",          5, 3, Meta.IS_FLUID,                            "power"),
    (111, "heat-pipe",              1, 1, Meta.NONE,                                "power"),

    # ── Logistics: chests ─────────────────────────────────────────────────────
    (130, "wooden-chest",           1, 1, Meta.NONE,                                "logistics"),
    (131, "iron-chest",             1, 1, Meta.NONE,                                "logistics"),
    (132, "steel-chest",            1, 1, Meta.NONE,                                "logistics"),
    (133, "passive-provider-chest", 1, 1, Meta.NONE,                                "logistics"),
    (134, "active-provider-chest",  1, 1, Meta.NONE,                                "logistics"),
    (135, "storage-chest",          1, 1, Meta.NONE,                                "logistics"),
    (136, "requester-chest",        1, 1, Meta.NONE,                                "logistics"),
    (137, "buffer-chest",           1, 1, Meta.NONE,                                "logistics"),

    # ── Logistics: trains ─────────────────────────────────────────────────────
    (140, "rail",                   2, 2, Meta.NONE,                                "logistics"),
    (141, "train-stop",             2, 2, Meta.IS_ELECTRIC,                         "logistics"),
    (142, "rail-signal",            1, 1, Meta.NONE,                                "logistics"),
    (143, "rail-chain-signal",      1, 1, Meta.NONE,                                "logistics"),
    (144, "roboport",               4, 4, Meta.IS_ELECTRIC,                         "logistics"),

    # ── Combat ────────────────────────────────────────────────────────────────
    (160, "stone-wall",             1, 1, Meta.NONE,                                "combat"),
    (161, "gate",                   1, 1, Meta.NONE,                                "combat"),
    (162, "gun-turret",             2, 2, Meta.NONE,                                "combat"),
    (163, "laser-turret",           2, 2, Meta.IS_ELECTRIC,                         "combat"),
    (164, "flamethrower-turret",    2, 3, Meta.IS_FLUID,                            "combat"),
    (165, "artillery-turret",       3, 3, Meta.IS_ELECTRIC,                         "combat"),
    (166, "land-mine",              1, 1, Meta.NONE,                                "combat"),
    (167, "radar",                  3, 3, Meta.IS_ELECTRIC,                         "combat"),
    (168, "small-lamp",             1, 1, Meta.IS_ELECTRIC,                         "combat"),

    # ── Circuit network ───────────────────────────────────────────────────────
    (190, "arithmetic-combinator",  2, 1, Meta.IS_ELECTRIC,                         "circuit"),
    (191, "decider-combinator",     2, 1, Meta.IS_ELECTRIC,                         "circuit"),
    (192, "constant-combinator",    1, 1, Meta.IS_ELECTRIC,                         "circuit"),
    (193, "power-switch",           2, 2, Meta.IS_ELECTRIC,                         "circuit"),

    # ── Special / group markers ───────────────────────────────────────────────
    (240, "belt-group",             1, 1, Meta.IS_BELT,                             "special"),
    (241, "pipe-group",             1, 1, Meta.IS_FLUID,                            "special"),
    (242, "electricity-group",      1, 1, Meta.IS_ELECTRIC,                         "special"),
]


# ── Build registry ────────────────────────────────────────────────────────────

class EntityID:
    """Bidirectional entity name ↔ uint8 ID mapping."""
    EMPTY = 0

    def __init__(self, entries: list[tuple[int, str, int, int, Meta, str]]):
        self._by_name: dict[str, EntityInfo] = {}
        self._by_id: dict[int, EntityInfo] = {}

        for id_, name, w, h, meta, cat in entries:
            info = EntityInfo(id=id_, name=name, width=w, height=h, meta=meta, category=cat)
            self._by_name[name] = info
            self._by_id[id_] = info

    def from_name(self, name: str) -> EntityInfo:
        """Look up entity info by prototype name."""
        return self._by_name[name]

    def from_id(self, id_: int) -> EntityInfo:
        """Look up entity info by grid ID."""
        return self._by_id[id_]

    def has_name(self, name: str) -> bool:
        return name in self._by_name

    def has_id(self, id_: int) -> bool:
        return id_ in self._by_id

    def all_entities(self) -> list[EntityInfo]:
        """All registered entities sorted by ID."""
        return sorted(self._by_id.values(), key=lambda e: e.id)

    def names(self) -> list[str]:
        return list(self._by_name.keys())

    def ids(self) -> list[int]:
        return sorted(self._by_id.keys())


# Singleton registry
ENTITY_REGISTRY = EntityID(_ENTITIES)
