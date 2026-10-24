"""Hand-built Factorio blueprints for tests (independent of the code under test)."""

from __future__ import annotations

import base64
import json
import zlib
from pathlib import Path

V0_17 = (0 << 48) | (17 << 32) | (79 << 16)
V1_1 = (1 << 48) | (1 << 32) | (110 << 16)
V2_0 = (2 << 48) | (0 << 32) | (28 << 16)


def export_string(obj: dict) -> str:
    """Encode a blueprint/book dict the way the game exports it."""
    return "0" + base64.b64encode(zlib.compress(json.dumps(obj).encode())).decode()


def entity(name: str, x: float, y: float, direction: int = 0, **extra) -> dict:
    """A blueprint entity with its centre at (x, y)."""
    return {"name": name, "position": {"x": x, "y": y}, **({"direction": direction} if direction else {}), **extra}


def blueprint(entities: list[dict], label: str = "bp", version: int = V2_0) -> dict:
    return {"blueprint": {"label": label, "version": version, "entities": entities}}


def book(children: list[dict], label: str = "book", version: int = V2_0) -> dict:
    return {"blueprint_book": {"label": label, "version": version, "blueprints": children}}


def write_jsonl(path: Path, objs: list[dict], **row) -> Path:
    """One source row per object, in the format of blueprints_v2/blueprints.jsonl."""
    with open(path, "w") as f:
        for obj in objs:
            f.write(json.dumps({"blueprint_string": export_string(obj), "tags": ["t"], "favorites": 3,
                                "entities": [{"corrupt": True}], **row}) + "\n")
    return path
