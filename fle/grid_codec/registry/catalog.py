"""
The entity catalog: every placeable entity the grid can hold.

Sizes are (width, height) when facing north, as the game's prototypes define
their tile footprint (offshore-pump is 1x1 since 2.0; train-stop and
railgun-turret have collision boxes smaller than their footprint). IDs never
change once assigned; new entities take free slots in their category.
"""

from __future__ import annotations

from fle.grid_codec.registry.entity_info import EntityInfo
from fle.grid_codec.registry.entity_registry import EntityRegistry
from fle.grid_codec.registry.meta import Meta

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

_ENTRIES: list[tuple[int, str, int, int, Meta, str]] = [
    # ── Resource extraction ───────────────────────────────────────────────────
    (1,  "burner-mining-drill",     2, 2, Meta.IS_BURNER,                           "resource"),
    (2,  "electric-mining-drill",   3, 3, Meta.IS_ELECTRIC,                         "resource"),
    (3,  "pumpjack",                3, 3, Meta.IS_ELECTRIC | Meta.IS_FLUID,         "resource"),
    (4,  "offshore-pump",           1, 1, Meta.IS_FLUID,                            "resource"),
    (5,  "asteroid-collector",      3, 3, Meta.IS_ELECTRIC,                         "resource"),
    (6,  "big-mining-drill",        5, 5, Meta.IS_ELECTRIC,                         "resource"),

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
    (29, "turbo-transport-belt",    1, 1, Meta.IS_BELT,                             "transport"),
    (44, "turbo-underground-belt",  1, 1, Meta.IS_BELT,                             "transport"),
    (45, "turbo-splitter",          2, 1, Meta.IS_BELT,                             "transport"),

    # ── Transport: inserters ──────────────────────────────────────────────────
    (30, "inserter",                1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (31, "burner-inserter",         1, 1, Meta.IS_INSERTER | Meta.IS_BURNER,        "transport"),
    (32, "long-handed-inserter",    1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (33, "fast-inserter",           1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (34, "bulk-inserter",           1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),
    (35, "stack-inserter",          1, 1, Meta.IS_INSERTER | Meta.IS_ELECTRIC,      "transport"),

    # ── Transport: pipes ──────────────────────────────────────────────────────
    (40, "pipe",                    1, 1, Meta.IS_FLUID,                            "transport"),
    (41, "pipe-to-ground",          1, 1, Meta.IS_FLUID,                            "transport"),
    (42, "pump",                    1, 2, Meta.IS_FLUID | Meta.IS_ELECTRIC,         "transport"),
    (43, "storage-tank",            3, 3, Meta.IS_FLUID,                            "transport"),

    # ── Production: furnaces ──────────────────────────────────────────────────
    (50, "stone-furnace",           2, 2, Meta.HAS_RECIPE | Meta.IS_BURNER,         "production"),
    (51, "steel-furnace",           2, 2, Meta.HAS_RECIPE | Meta.IS_BURNER,         "production"),
    (52, "electric-furnace",        3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (53, "recycler",                2, 4, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (54, "foundry",                 5, 5, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),

    # ── Production: assemblers ────────────────────────────────────────────────
    (55, "assembling-machine-1",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (56, "assembling-machine-2",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (57, "assembling-machine-3",    3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (58, "centrifuge",              3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (59, "crusher",                 2, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),

    # ── Production: oil & chemistry ───────────────────────────────────────────
    (60, "oil-refinery",            5, 5, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),
    (61, "chemical-plant",          3, 3, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),
    (62, "electromagnetic-plant",   4, 4, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),
    (63, "cryogenic-plant",         5, 5, Meta.HAS_RECIPE | Meta.IS_ELECTRIC | Meta.IS_FLUID, "production"),
    (64, "biochamber",              3, 3, Meta.HAS_RECIPE | Meta.IS_BURNER | Meta.IS_FLUID,   "production"),

    # ── Production: other ─────────────────────────────────────────────────────
    (65, "lab",                     3, 3, Meta.IS_ELECTRIC,                         "production"),
    (66, "rocket-silo",            9, 9, Meta.HAS_RECIPE | Meta.IS_ELECTRIC,       "production"),
    (67, "beacon",                  3, 3, Meta.IS_ELECTRIC,                         "production"),
    (68, "biolab",                  5, 5, Meta.IS_ELECTRIC,                         "production"),
    (69, "agricultural-tower",      3, 3, Meta.IS_ELECTRIC,                         "production"),
    (70, "captive-biter-spawner",   5, 5, Meta.HAS_RECIPE | Meta.IS_BURNER,         "production"),

    # ── Power ─────────────────────────────────────────────────────────────────
    (100, "boiler",                 3, 2, Meta.IS_BURNER | Meta.IS_FLUID,           "power"),
    (101, "steam-engine",           3, 5, Meta.IS_FLUID,                            "power"),
    (102, "solar-panel",            3, 3, Meta.NONE,                                "power"),
    (103, "accumulator",            2, 2, Meta.IS_ELECTRIC,                         "power"),
    (104, "small-electric-pole",    1, 1, Meta.IS_ELECTRIC,                         "power"),
    (105, "medium-electric-pole",   1, 1, Meta.IS_ELECTRIC,                         "power"),
    (106, "big-electric-pole",      2, 2, Meta.IS_ELECTRIC,                         "power"),
    (107, "substation",             2, 2, Meta.IS_ELECTRIC,                         "power"),
    (108, "nuclear-reactor",        5, 5, Meta.IS_FLUID,                            "power"),
    (109, "heat-exchanger",         3, 2, Meta.IS_FLUID,                            "power"),
    (110, "steam-turbine",          3, 5, Meta.IS_FLUID,                            "power"),
    (111, "heat-pipe",              1, 1, Meta.NONE,                                "power"),
    (112, "heating-tower",          3, 3, Meta.IS_BURNER,                           "power"),
    (113, "fusion-reactor",         6, 6, Meta.IS_ELECTRIC | Meta.IS_FLUID,         "power"),
    (114, "fusion-generator",       3, 5, Meta.IS_ELECTRIC | Meta.IS_FLUID,         "power"),
    (115, "lightning-rod",          1, 1, Meta.IS_ELECTRIC,                         "power"),
    (116, "lightning-collector",    2, 2, Meta.IS_ELECTRIC,                         "power"),
    (117, "thruster",               4, 5, Meta.IS_FLUID,                            "power"),

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
    (145, "cargo-bay",              4, 4, Meta.NONE,                                "logistics"),

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
    (169, "rocket-turret",          3, 3, Meta.NONE,                                "combat"),
    (170, "railgun-turret",         5, 5, Meta.IS_ELECTRIC,                         "combat"),
    (171, "tesla-turret",           4, 4, Meta.IS_ELECTRIC,                         "combat"),

    # ── Circuit network ───────────────────────────────────────────────────────
    (190, "arithmetic-combinator",  1, 2, Meta.IS_ELECTRIC,                         "circuit"),
    (191, "decider-combinator",     1, 2, Meta.IS_ELECTRIC,                         "circuit"),
    (192, "constant-combinator",    1, 1, Meta.IS_ELECTRIC,                         "circuit"),
    (193, "power-switch",           2, 2, Meta.IS_ELECTRIC,                         "circuit"),
    (194, "selector-combinator",    1, 2, Meta.IS_ELECTRIC,                         "circuit"),
    (195, "display-panel",          1, 1, Meta.NONE,                                "circuit"),
    (196, "programmable-speaker",   1, 1, Meta.IS_ELECTRIC,                         "circuit"),

    # ── Special / group markers ───────────────────────────────────────────────
    (240, "belt-group",             1, 1, Meta.IS_BELT,                             "special"),
    (241, "pipe-group",             1, 1, Meta.IS_FLUID,                            "special"),
    (242, "electricity-group",      1, 1, Meta.IS_ELECTRIC,                         "special"),
]


# Prototypes flagged "placeable-off-grid".
OFF_GRID = {"land-mine"}

ENTITY_REGISTRY = EntityRegistry(
    EntityInfo(id=id_, name=name, width=w, height=h, meta=meta, category=cat, off_grid=name in OFF_GRID)
    for id_, name, w, h, meta, cat in _ENTRIES
)
