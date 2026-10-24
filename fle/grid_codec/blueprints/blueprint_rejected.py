from __future__ import annotations

from typing import Iterable


class BlueprintRejected(Exception):
    """A blueprint that cannot be encoded faithfully; reason is a stable category for counting."""

    def __init__(self, reason: str, details: Iterable[str] = ()):
        self.reason = reason
        self.details = tuple(details)
        super().__init__(f"{reason}: {self.detail}" if self.details else reason)

    @property
    def detail(self) -> str:
        return ", ".join(self.details)
