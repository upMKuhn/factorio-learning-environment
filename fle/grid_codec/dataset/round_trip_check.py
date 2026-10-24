from __future__ import annotations

from collections import Counter

from fle.grid_codec.dataset.encoded_sample import EncodedSample
from fle.grid_codec.dataset.integrity_check import IntegrityCheck
from fle.grid_codec.grid import EncodingError, GridDecoder


class RoundTripCheck(IntegrityCheck):
    """Strictly decoding the grid gives back exactly the layout's entities: type, tile, direction, recipe, io type."""

    def __init__(self, decoder: GridDecoder):
        self.decoder = decoder

    def check(self, sample: EncodedSample) -> list[str]:
        try:
            decoded = self.decoder.decode(sample.grid)
        except EncodingError as e:
            return [f"decode failed: {e}"]
        expected = Counter(e.sort_key() for e in sample.entities_in_grid())
        actual = Counter(e.sort_key() for e in decoded)
        return ([f"missing after decode: {self._describe(k)}" for k in sorted(expected - actual)]
                + [f"unexpected after decode: {self._describe(k)}" for k in sorted(actual - expected)])

    @staticmethod
    def _describe(key: tuple) -> str:
        y, x, name, direction, recipe, io_type = key
        extra = "".join(f" {v}" for v in (recipe, io_type) if v)
        return f"{name} at ({x}, {y}) dir {direction}{extra}"
