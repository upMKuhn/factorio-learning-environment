from __future__ import annotations

from enum import IntEnum


class Channel(IntEnum):
    """Channels of an encoded (H, W, 7) uint16 grid."""
    ENTITY = 0      # entity type id, 0 = empty
    DIRECTION = 1   # 0-15: 0=N, 4=E, 8=S, 12=W
    META = 2        # Meta flags
    INSTANCE = 3    # shared by the tiles of one multi-tile entity, 0 for single-tile ones
    RECIPE = 4      # Vocabulary recipe id, 0 = none
    ITEM_LEFT = 5   # Vocabulary item id carried on the belt's left lane, 0 = none
    ITEM_RIGHT = 6  # ... right lane

    @classmethod
    def count(cls) -> int:
        return len(cls)
