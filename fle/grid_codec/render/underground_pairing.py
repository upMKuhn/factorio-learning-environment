"""Which underground belts are entrances and which are exits."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from fle.grid_codec.render.placed_entity import PlacedEntity
from fle.grid_codec.schema import Meta

if TYPE_CHECKING:
    from fle.grid_codec.render.layout import Layout


def _exit_flag() -> int:
    """The encoder's underground-exit bit, if the schema defines one."""
    for flag in Meta:
        if "UNDERGROUND" in flag.name and ("OUT" in flag.name or "EXIT" in flag.name):
            return int(flag)
    return 0


class UndergroundPairing:
    """
    Entrance/exit roles and partners of the underground belts in a layout.

    When the grid carries an exit flag (channel 2) it is used as is. Otherwise
    the roles are inferred the way Factorio pairs them: undergrounds of one tier
    and direction on one line, walked along the flow, each entrance linking to
    the next one within reach. An underground with no belt feeding it from
    behind but a belt taking from it ahead starts as an exit (its entrance lies
    outside the layout).
    """

    # Max entrance→exit offset in tiles (prototype max_distance)
    REACH = {
        "underground-belt": 5,
        "fast-underground-belt": 7,
        "express-underground-belt": 9,
        "turbo-underground-belt": 11,
    }

    def __init__(self, layout: Layout, exit_flag: int | None = None):
        self._layout = layout
        self._flag = _exit_flag() if exit_flag is None else exit_flag
        self._exits: set[int] = set()
        self._partner: dict[int, PlacedEntity] = {}
        undergrounds = [e for e in layout.entities if e.is_underground]
        if self._flag and any(e.meta & self._flag for e in undergrounds):
            self._exits = {id(e) for e in undergrounds if e.meta & self._flag}
            for line in self._lines(undergrounds):
                self._pair_flagged(line)
        else:
            for line in self._lines(undergrounds):
                self._pair_inferred(line)

    def is_exit(self, e: PlacedEntity) -> bool:
        return id(e) in self._exits

    def partner(self, e: PlacedEntity) -> PlacedEntity | None:
        return self._partner.get(id(e))

    @staticmethod
    def _lines(undergrounds: list[PlacedEntity]) -> list[list[PlacedEntity]]:
        """Undergrounds grouped by tier, direction and line, sorted along the flow."""
        lines: dict[tuple, list[PlacedEntity]] = defaultdict(list)
        for e in undergrounds:
            dx, dy = e.direction.delta
            lines[(e.name, e.direction, e.y if dx else e.x)].append(e)
        for line in lines.values():
            dx, dy = line[0].direction.delta
            line.sort(key=lambda e: e.x * dx + e.y * dy)
        return list(lines.values())

    def _in_reach(self, a: PlacedEntity, b: PlacedEntity) -> bool:
        return abs(b.x - a.x) + abs(b.y - a.y) <= self.REACH.get(a.name, 5)

    def _link(self, entrance: PlacedEntity, exit_: PlacedEntity) -> None:
        self._partner[id(entrance)] = exit_
        self._partner[id(exit_)] = entrance

    def _pair_flagged(self, line: list[PlacedEntity]) -> None:
        for a, b in zip(line, line[1:]):
            if not self.is_exit(a) and self.is_exit(b) and self._in_reach(a, b):
                self._link(a, b)

    def _pair_inferred(self, line: list[PlacedEntity]) -> None:
        i = 0
        while i < len(line):
            a = line[i]
            if self._looks_like_exit(a):
                self._exits.add(id(a))
                i += 1
            elif i + 1 < len(line) and self._in_reach(a, line[i + 1]):
                self._exits.add(id(line[i + 1]))
                self._link(a, line[i + 1])
                i += 2
            else:
                i += 1

    def _looks_like_exit(self, e: PlacedEntity) -> bool:
        behind = self._layout.step(e.x, e.y, e.direction.opposite)
        ahead = self._layout.step(e.x, e.y, e.direction)
        fed = behind is not None and behind.is_belt and behind.direction == e.direction
        feeds = ahead is not None and ahead.is_belt and ahead.direction != e.direction.opposite
        return feeds and not fed
