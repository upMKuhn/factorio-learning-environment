from __future__ import annotations

from fle.grid_codec.dataset.encoded_sample import EncodedSample
from fle.grid_codec.dataset.integrity_check import IntegrityCheck


class OverlapCheck(IntegrityCheck):
    """No tile is claimed by two entities."""

    def check(self, sample: EncodedSample) -> list[str]:
        tiles = sample.layout.overlapping_tiles()
        if not tiles:
            return []
        names = sorted({e.name for e in sample.layout.entities_on(tiles)})
        return [f"overlap: {len(tiles)} tiles shared by {', '.join(names)}"]
