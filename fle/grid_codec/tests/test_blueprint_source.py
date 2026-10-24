"""Reading the source: BlueprintString, SourceBlueprint, JsonlBlueprintSource, VersionConventions."""

import pytest

from fle.grid_codec.blueprints import (
    BlueprintString, JsonlBlueprintSource, Pre20Conventions, SourceBlueprint, SyntheticBlueprintSource,
    V20Conventions, VersionConventions,
)
from fle.grid_codec.tests.fixtures import V0_17, V1_1, V2_0, blueprint, book, entity, export_string, write_jsonl

BELT = entity("transport-belt", 0.5, 0.5)
FURNACE = entity("stone-furnace", 2, 1)


# ── BlueprintString ───────────────────────────────────────────────────────────

def test_decodes_exported_string():
    obj = blueprint([BELT], label="one belt")
    assert BlueprintString(export_string(obj)).decode() == obj


def test_export_then_decode_is_identity():
    obj = book([blueprint([BELT])])
    assert BlueprintString.from_json(obj).decode() == obj


def test_rejects_unknown_format_version():
    with pytest.raises(ValueError, match="version"):
        BlueprintString("1" + export_string(blueprint([BELT]))[1:]).decode()


def test_single_blueprint_yields_itself():
    [bp] = BlueprintString(export_string(blueprint([BELT], label="x", version=V1_1))).blueprints()
    assert (bp.label, bp.book, bp.version, bp.major_version) == ("x", "", V1_1, 1)
    assert bp.entities == [BELT]


def test_books_explode_recursively_with_labels_and_inherited_version():
    inner = {"blueprint_book": {"label": "inner", "blueprints": [
        {"blueprint": {"label": "deep", "entities": [FURNACE]}}]}}
    obj = book([blueprint([BELT], label="top", version=V2_0), inner, {"upgrade_planner": {}}],
               label="outer", version=V0_17)
    bps = list(BlueprintString(export_string(obj)).blueprints())
    assert [(b.label, b.book, b.major_version) for b in bps] == [("top", "outer", 2), ("deep", "outer / inner", 0)]


def test_source_metadata_is_attached():
    [bp] = BlueprintString(export_string(blueprint([BELT]))).blueprints(tags=["a"], favorites=7)
    assert bp.tags == ("a",) and bp.favorites == 7


def test_content_key_ignores_entity_order_and_metadata():
    a = SourceBlueprint(label="a", entities=[BELT, FURNACE], version=V2_0)
    b = SourceBlueprint(label="b", entities=[FURNACE, {**BELT, "entity_number": 9}], version=V1_1)
    assert a.content_key() == b.content_key()


def test_content_key_sees_recipes_and_underground_type():
    plain = SourceBlueprint(label="a", entities=[entity("assembling-machine-1", 1.5, 1.5)])
    crafting = SourceBlueprint(label="a", entities=[entity("assembling-machine-1", 1.5, 1.5, recipe="pipe")])
    ug_in = SourceBlueprint(label="a", entities=[entity("underground-belt", 0.5, 0.5, type="input")])
    ug_out = SourceBlueprint(label="a", entities=[entity("underground-belt", 0.5, 0.5, type="output")])
    assert plain.content_key() != crafting.content_key()
    assert ug_in.content_key() != ug_out.content_key()


def test_synthetic_blueprints_without_version_are_2_0():
    bp = SourceBlueprint.from_dict({"label": "s", "entities": [{"name": "inserter", "x": 0, "y": 0}]})
    assert bp.major_version == 2 and bp.entity_count == 1


# ── JsonlBlueprintSource ──────────────────────────────────────────────

@pytest.fixture
def source(tmp_path):
    a = blueprint([BELT, FURNACE], label="A")
    b = blueprint([FURNACE], label="B bigger")
    crafted = blueprint([BELT, entity("assembling-machine-1", 4.5, 1.5, recipe="pipe")], label="A crafting")
    objs = [
        book([a, book([b], label="inner")], label="outer"),
        book([a, book([b], label="inner")], label="outer"),   # same export string again
        book([blueprint([FURNACE, BELT], label="A again")], label="other"),  # same content, other book
        crafted,
        blueprint([], label="empty"),
    ]
    return write_jsonl(tmp_path / "source.jsonl", objs)


def test_jsonl_source_dedupes_strings_and_content(source):
    reader = JsonlBlueprintSource(source)
    assert [bp.label for bp in reader] == ["A", "B bigger", "A crafting"]
    assert reader.stats["source rows"] == 5
    assert reader.stats["duplicate export strings"] == 1
    assert reader.stats["duplicate blueprints"] == 1
    assert reader.stats["empty blueprints"] == 1
    assert reader.stats["unique blueprints"] == 3


def test_jsonl_source_reads_row_metadata_not_row_entities(source):
    first = next(iter(JsonlBlueprintSource(source)))
    assert first.tags == ("t",) and first.favorites == 3
    assert first.entities == [BELT, FURNACE]
    assert first.book == "outer"


def test_jsonl_source_size_filter(source):
    reader = JsonlBlueprintSource(source, min_entities=2, max_entities=2)
    assert [bp.label for bp in reader] == ["A", "A crafting"]
    assert reader.stats["outside entity range"] == 1


def test_find_prefers_exact_label(source):
    reader = JsonlBlueprintSource(source)
    assert reader.find("A crafting").label == "A crafting"
    assert reader.find("bigger").label == "B bigger"
    with pytest.raises(KeyError):
        reader.find("nope")


# ── VersionConventions ───────────────────────────────────────────────────────

def test_conventions_are_chosen_by_major_version():
    assert isinstance(VersionConventions.for_version(V0_17), Pre20Conventions)
    assert isinstance(VersionConventions.for_version(V1_1), Pre20Conventions)
    assert isinstance(VersionConventions.for_version(V2_0), V20Conventions)
    assert isinstance(VersionConventions.for_version(None), V20Conventions)  # synthetic data


def test_directions():
    assert [Pre20Conventions().direction(d) for d in (0, 2, 4, 6)] == [0, 4, 8, 12]
    assert [V20Conventions().direction(d) for d in (0, 4, 8, 12)] == [0, 4, 8, 12]


@pytest.mark.parametrize("old, new", [
    ("logistic-chest-requester", "requester-chest"),
    ("logistic-chest-passive-provider", "passive-provider-chest"),
    ("filter-inserter", "fast-inserter"),
    ("stack-filter-inserter", "bulk-inserter"),
    ("stack-inserter", "bulk-inserter"),
    ("transport-belt", "transport-belt"),
    ("straight-rail", "straight-rail"),         # unknown stays unknown
])
def test_pre_2_0_entity_names(old, new):
    assert Pre20Conventions().entity_name(old) == new


@pytest.mark.parametrize("old, new", [
    ("science-pack-1", "automation-science-pack"),
    ("high-tech-science-pack", "utility-science-pack"),
    ("fill-water-barrel", "water-barrel"),
    ("empty-barrel", "barrel"),
    ("stack-inserter", "bulk-inserter"),
    ("logistic-chest-buffer", "buffer-chest"),
    ("iron-gear-wheel", "iron-gear-wheel"),
])
def test_pre_2_0_recipe_names(old, new):
    assert Pre20Conventions().recipe_name(old) == new


def test_2_0_names_are_never_migrated():
    v2 = V20Conventions()
    assert v2.entity_name("stack-inserter") == "stack-inserter"   # Space Age's own stack inserter
    assert v2.entity_name("filter-inserter") == "filter-inserter"
    assert v2.recipe_name("empty-barrel") == "empty-barrel"


# ── SyntheticBlueprintSource ──────────────────────────────────────────────────

def test_synthetic_source_is_seeded_and_tagged():
    first = [(bp.label, len(bp.entities)) for bp in SyntheticBlueprintSource(seed=3)]
    again = [(bp.label, len(bp.entities)) for bp in SyntheticBlueprintSource(seed=3)]
    assert first == again and len(first) > 10
    bp = next(iter(SyntheticBlueprintSource(seed=3)))
    assert bp.tags == ("synthetic",) and bp.major_version == 2 and "x" in bp.entities[0]


def test_sources_share_the_size_filter():
    small = list(SyntheticBlueprintSource(seed=0, max_entities=7))
    assert small and all(bp.entity_count <= 7 for bp in small)
