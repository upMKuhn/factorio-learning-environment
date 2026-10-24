from __future__ import annotations

from enum import IntFlag


class Meta(IntFlag):
    """Bitmask flags in grid channel 2: an entity type's defaults plus per-instance bits."""
    NONE = 0
    HAS_RECIPE = 1       # entity can have a recipe set
    IS_FLUID = 2         # entity handles fluids
    IS_ELECTRIC = 4      # entity uses electric power
    IS_BURNER = 8        # entity uses burner fuel
    IS_INSERTER = 16     # entity is an inserter
    IS_BELT = 32         # entity is a transport belt / underground / splitter
    IS_RESOURCE = 64     # tile contains a resource patch
    # Per instance: this underground belt is an exit (blueprint type "output"), not an entrance.
    UNDERGROUND_OUTPUT = 128

    @classmethod
    def instance_bits(cls) -> Meta:
        """Bits that describe one placed entity rather than its type."""
        return cls.UNDERGROUND_OUTPUT
