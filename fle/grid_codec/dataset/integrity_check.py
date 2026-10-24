from __future__ import annotations

from abc import ABC, abstractmethod

from fle.grid_codec.dataset.encoded_sample import EncodedSample


class IntegrityCheck(ABC):
    """One property every written sample must have; returns human-readable failures, none if it holds."""

    @abstractmethod
    def check(self, sample: EncodedSample) -> list[str]:
        ...

    @property
    def name(self) -> str:
        return type(self).__name__
