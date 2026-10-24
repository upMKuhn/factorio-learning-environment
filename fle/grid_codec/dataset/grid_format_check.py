from __future__ import annotations

import numpy as np

from fle.grid_codec.dataset.encoded_sample import EncodedSample
from fle.grid_codec.dataset.integrity_check import IntegrityCheck
from fle.grid_codec.grid import Channel


class GridFormatCheck(IntegrityCheck):
    """(H, W, 7) uint16 covering exactly the sample's bounds."""

    def check(self, sample: EncodedSample) -> list[str]:
        grid, failures = sample.grid, []
        if grid.dtype != np.uint16:
            failures.append(f"dtype {grid.dtype}, expected uint16")
        if grid.shape != (*sample.bounds.shape, Channel.count()):
            failures.append(f"shape {grid.shape}, expected {(*sample.bounds.shape, Channel.count())}")
        return failures
