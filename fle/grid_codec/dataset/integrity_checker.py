from __future__ import annotations

from typing import Sequence

from fle.grid_codec.dataset.carried_items_check import CarriedItemsCheck
from fle.grid_codec.dataset.encoded_sample import EncodedSample
from fle.grid_codec.dataset.grid_format_check import GridFormatCheck
from fle.grid_codec.dataset.integrity_check import IntegrityCheck
from fle.grid_codec.dataset.overlap_check import OverlapCheck
from fle.grid_codec.dataset.round_trip_check import RoundTripCheck
from fle.grid_codec.grid import GridDecoder


class IntegrityChecker:
    """Runs a pipeline of IntegrityChecks; by default format, overlap, strict round trip and belt contents."""

    def __init__(self, decoder: GridDecoder | None = None, checks: Sequence[IntegrityCheck] | None = None):
        if checks is None:
            if decoder is None:
                raise ValueError("The default checks need a decoder for the round trip")
            checks = [GridFormatCheck(), OverlapCheck(), RoundTripCheck(decoder), CarriedItemsCheck()]
        self.checks = list(checks)

    def check(self, sample: EncodedSample) -> list[str]:
        failures = []
        for check in self.checks:
            try:
                failures += check.check(sample)
            except Exception as e:  # a crashing check is a failed check, not a crashed build
                failures.append(f"{check.name} crashed: {e!r}")
        return failures

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.checks]
