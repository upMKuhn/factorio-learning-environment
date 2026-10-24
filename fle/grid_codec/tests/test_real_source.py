"""The real community source: every normalized blueprint must survive a strict round trip."""

from collections import Counter

import pytest

from fle.grid_codec.blueprints import JsonlBlueprintSource, BlueprintNormalizer, BlueprintRejected
from fle.grid_codec.grid import GridDecoder, GridEncoder
from fle.grid_codec.dataset import EncodedSample, IntegrityChecker
from fle.grid_codec.tests.conftest import BLUEPRINTS_JSONL

pytestmark = [pytest.mark.slow, pytest.mark.skipif(not BLUEPRINTS_JSONL.exists(), reason="no blueprint source")]


def test_every_accepted_blueprint_round_trips(recipe_data):
    source = JsonlBlueprintSource(BLUEPRINTS_JSONL, max_entities=65535)  # instance ids are uint16
    normalizer = BlueprintNormalizer(recipe_data.recipes)
    encoder, checker = GridEncoder(recipe_data.vocabulary), IntegrityChecker(GridDecoder(recipe_data.vocabulary))
    rejected, accepted, failures = Counter(), 0, {}
    for bp in source:
        try:
            layout = normalizer.normalize(bp)
        except BlueprintRejected as r:
            rejected[r.reason] += 1
            continue
        if problems := checker.check(EncodedSample.encode(layout, encoder)):
            failures[bp.label] = problems
        accepted += 1

    assert source.stats["source rows"] == 5695
    assert source.stats["distinct export strings"] == 735
    assert failures == {}
    assert accepted > 3000
    assert rejected["unknown entity"] > 1500
