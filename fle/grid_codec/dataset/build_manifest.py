from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence


class BuildManifest:
    """What a dataset build read, wrote, dropped and why, and which integrity checks every sample passed."""

    def __init__(self, checks: Sequence[str] = ()):
        self.checks = list(checks)
        self.sources: dict[str, dict] = {}
        self.samples: Counter = Counter()
        self.rejected: Counter = Counter()
        self.rejected_detail: defaultdict[str, Counter] = defaultdict(Counter)
        self.duplicates = 0
        self.integrity_failures: dict[str, list[str]] = {}
        self.annotations: dict[str, dict] = {}

    def merge_source(self, name: str, stats: Mapping[str, int]) -> None:
        self.sources[name] = dict(stats)

    def accept(self, kind: str) -> None:
        self.samples[kind] += 1

    def reject(self, reason: str, *details: str) -> None:
        self.rejected[reason] += 1
        self.rejected_detail[reason].update(details)

    def annotate(self, section: str, stats: Mapping[str, int]) -> None:
        """Extra counts recorded under their own section, e.g. what flow inference discarded."""
        self.annotations[section] = dict(stats)

    def duplicate(self) -> None:
        self.duplicates += 1

    def fail_integrity(self, label: str, failures: list[str]) -> None:
        key, n = label, 1
        while key in self.integrity_failures:
            n += 1
            key = f"{label} #{n}"
        self.integrity_failures[key] = failures

    @property
    def ok(self) -> bool:
        return not self.integrity_failures

    def to_dict(self) -> dict:
        return {
            "samples": dict(self.samples),
            "sources": self.sources,
            "duplicate layouts": self.duplicates,
            "rejected": dict(self.rejected.most_common()),
            "rejected_detail": {r: dict(c.most_common()) for r, c in self.rejected_detail.items()},
            **self.annotations,
            "integrity": {"checks": self.checks, "passed": self.ok, "failures": self.integrity_failures},
        }

    def write(self, path: str | Path) -> Path:
        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path

    def summary(self) -> list[str]:
        lines = [f"samples: {sum(self.samples.values())} ({', '.join(f'{k} {v}' for k, v in self.samples.items())})"]
        for name, stats in self.sources.items():
            lines.append(f"source {name}: " + ", ".join(f"{k} {v}" for k, v in stats.items()))
        lines.append(f"duplicate layouts dropped: {self.duplicates}")
        for reason, n in self.rejected.most_common():
            top = ", ".join(f"{d} {c}" for d, c in self.rejected_detail[reason].most_common(5))
            lines.append(f"rejected {n:5d}  {reason}" + (f"  ({top})" if top else ""))
        for section, stats in self.annotations.items():
            lines.append(f"{section}: " + ", ".join(f"{k} {v}" for k, v in stats.items()))
        verdict = "passed" if self.ok else f"FAILED for {len(self.integrity_failures)} samples"
        lines.append(f"integrity ({', '.join(self.checks)}): {verdict}")
        return lines
