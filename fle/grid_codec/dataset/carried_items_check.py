from __future__ import annotations

import numpy as np

from fle.grid_codec.dataset.encoded_sample import EncodedSample
from fle.grid_codec.dataset.integrity_check import IntegrityCheck
from fle.grid_codec.grid import Channel
from fle.grid_codec.registry import ENTITY_REGISTRY

_CONDUIT_IDS = np.array([e.id for e in ENTITY_REGISTRY.all_entities() if e.carries_contents])


class CarriedItemsCheck(IntegrityCheck):
    """Contents (channels 5-6) only on belt and pipe tiles."""

    def check(self, sample: EncodedSample) -> list[str]:
        grid = sample.grid
        if grid.shape[2] <= Channel.ITEM_RIGHT:
            return []
        carrying = (grid[:, :, Channel.ITEM_LEFT] > 0) | (grid[:, :, Channel.ITEM_RIGHT] > 0)
        elsewhere = carrying & ~np.isin(grid[:, :, Channel.ENTITY], _CONDUIT_IDS)
        n = int(np.count_nonzero(elsewhere))
        return [f"items on {n} non-belt, non-pipe tiles"] if n else []
