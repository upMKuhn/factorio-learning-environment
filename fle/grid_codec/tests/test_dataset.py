"""Layout, IntegrityChecker and BuildManifest: what a dataset build proves about each sample."""

import json

import numpy as np
import pytest
from pydantic import ValidationError

from fle.grid_codec.blueprints import Layout, SourceBlueprint
from fle.grid_codec.dataset import (
    BuildManifest, CarriedItemsCheck, EncodedSample, GridFormatCheck, IntegrityChecker, OverlapCheck, RoundTripCheck,
)
from fle.grid_codec.grid import BoundingBox, Channel, EntitySpec, GridDecoder, GridEncoder, Vocabulary

VOCAB = Vocabulary.from_names(recipes=["copper-cable"], items=["copper-plate"])
LAYOUT = Layout((
    EntitySpec("assembling-machine-1", 0, 0, recipe="copper-cable"),
    EntitySpec("inserter", 3, 1, 4),
    EntitySpec("transport-belt", 4, 1, 8),
    EntitySpec("underground-belt", 4, 2, 8, io_type="input"),
    EntitySpec("underground-belt", 4, 5, 8, io_type="output"),
))


# ── Layout ────────────────────────────────────────────────────────────────────

def test_layout_overlaps():
    assert LAYOUT.overlapping_tiles() == set()
    clash = Layout((EntitySpec("stone-furnace", 0, 0), EntitySpec("steam-engine", 1, 1, 4)))
    assert clash.overlapping_tiles() == {(1, 1)}


def test_layout_content_key_is_translation_invariant_and_sees_recipes():
    moved = LAYOUT.translated(7, -3)
    assert moved.entities[0] == EntitySpec("assembling-machine-1", 7, -3, recipe="copper-cable")
    assert moved.content_key() == LAYOUT.content_key()
    plain = Layout(tuple(EntitySpec(e.name, e.x, e.y, e.direction, io_type=e.io_type) for e in LAYOUT.entities))
    assert plain.content_key() != LAYOUT.content_key()


def test_layout_dicts_for_flow_inference():
    dicts = LAYOUT.as_dicts()
    assert dicts[0] == {"name": "assembling-machine-1", "x": 0, "y": 0, "direction": 0, "recipe": "copper-cable"}
    assert dicts[4]["type"] == "output"


def test_layout_bounds():
    assert LAYOUT.bounds(padding=1) == BoundingBox(-1, -1, 7, 8)


def test_layout_is_frozen_and_ignores_its_source_in_equality():
    with pytest.raises(ValidationError):
        LAYOUT.entities = ()
    tagged = Layout(LAYOUT.entities, SourceBlueprint(label="x", entities=[]))
    assert tagged == LAYOUT and hash(tagged) == hash(LAYOUT)
    assert tagged.source.label == "x"


def test_layout_holds_entity_specs_only():
    with pytest.raises(ValidationError):
        Layout(("transport-belt",))


# ── IntegrityChecker ──────────────────────────────────────────────────────────

@pytest.fixture
def checker():
    return IntegrityChecker(GridDecoder(VOCAB))


def encoded(layout=LAYOUT) -> EncodedSample:
    return EncodedSample.encode(layout, GridEncoder(VOCAB))


def test_encoded_sample_keeps_grid_and_bounds():
    sample = encoded()
    assert sample.bounds == LAYOUT.bounds(padding=1)
    assert sample.grid.shape == (8, 7, 7)
    assert sample.entities_in_grid()[0] == EntitySpec("assembling-machine-1", 1, 1, recipe="copper-cable")


def test_encoded_sample_is_frozen_and_holds_an_array():
    sample = encoded()
    with pytest.raises(ValidationError):
        sample.bounds = BoundingBox(0, 0, 1, 1)
    with pytest.raises(ValidationError):
        EncodedSample(layout=LAYOUT, grid=[[0]], bounds=sample.bounds)


def test_default_pipeline_runs_every_check():
    kinds = {type(c) for c in IntegrityChecker(GridDecoder(VOCAB)).checks}
    assert kinds == {GridFormatCheck, OverlapCheck, RoundTripCheck, CarriedItemsCheck}


def test_pipeline_is_composable():
    checker = IntegrityChecker(checks=[OverlapCheck()])
    sample = encoded()
    sample.grid[:] = 0
    assert checker.check(sample) == []  # only overlaps are checked


def test_clean_sample_passes(checker):
    assert checker.check(encoded()) == []


def test_lost_entity_is_reported(checker):
    sample = encoded()
    sample.grid[2, 4] = 0  # the inserter
    failures = checker.check(sample)
    assert any("missing" in f and "inserter" in f for f in failures)


def test_changed_recipe_is_reported(checker):
    sample = encoded()
    sample.grid[1:4, 1:4, Channel.RECIPE] = 0
    assert any("assembling-machine-1" in f for f in checker.check(sample))


def test_damaged_footprint_is_reported(checker):
    sample = encoded()
    sample.grid[1, 1, Channel.INSTANCE] = 99
    assert any("decode" in f for f in checker.check(sample))


def test_overlapping_layout_is_reported(checker):
    clash = Layout((EntitySpec("stone-furnace", 0, 0), EntitySpec("inserter", 1, 1)))
    sample = EncodedSample.encode(clash, GridEncoder(VOCAB, strict=False))
    assert any("overlap" in f for f in checker.check(sample))


def test_fluids_in_pipes_are_fine(checker):
    layout = Layout((EntitySpec("pipe", 0, 0), EntitySpec("pipe-to-ground", 1, 0, 12)))
    sample = EncodedSample.encode(layout, GridEncoder(VOCAB))
    sample.grid[1, 1:3, Channel.ITEM_LEFT] = 1
    assert checker.check(sample) == []


def test_items_off_belts_are_reported(checker):
    sample = encoded()
    sample.grid[1, 1, Channel.ITEM_LEFT] = 1
    assert any("non-belt" in f for f in checker.check(sample))


def test_wrong_dtype_is_reported(checker):
    sample = encoded()
    sample = sample.model_copy(update={"grid": sample.grid.astype(np.int32)})
    assert any("dtype" in f for f in checker.check(sample))


# ── BuildManifest ─────────────────────────────────────────────────────────────

def test_manifest_counts_and_serializes(tmp_path):
    manifest = BuildManifest(checks=["OverlapCheck"])
    manifest.merge_source("community", {"source rows": 4, "unique blueprints": 3})
    manifest.duplicate()
    manifest.reject("unknown entity", "straight-rail")
    manifest.reject("unknown entity", "straight-rail")
    manifest.reject("unknown entity", "curved-rail")
    manifest.reject("overlapping tiles", "2 tiles")
    manifest.accept("community")
    manifest.accept("synthetic")
    assert manifest.ok
    manifest.fail_integrity("A", ["missing inserter"])
    assert not manifest.ok

    path = manifest.write(tmp_path / "manifest.json")
    data = json.loads(path.read_text())
    assert data["sources"]["community"]["unique blueprints"] == 3
    assert data["duplicate layouts"] == 1
    assert data["integrity"]["checks"] == ["OverlapCheck"]
    assert data["rejected"] == {"unknown entity": 3, "overlapping tiles": 1}
    assert data["rejected_detail"]["unknown entity"] == {"straight-rail": 2, "curved-rail": 1}
    assert data["samples"] == {"community": 1, "synthetic": 1}
    assert data["integrity"]["failures"] == {"A": ["missing inserter"]}
    assert data["integrity"]["passed"] is False
    assert any("unknown entity" in line for line in manifest.summary())


def test_manifest_annotations():
    manifest = BuildManifest()
    manifest.annotate("flow labels", {"mixed lanes left unlabelled": 2})
    assert manifest.to_dict()["flow labels"] == {"mixed lanes left unlabelled": 2}
