"""Every kept fle module imports, and the deleted LLM-agent harness stays deleted."""

import importlib
from pathlib import Path

import pytest

import fle


# Modules whose third-party dependency is optional (pyproject extras); skipped when absent.
OPTIONAL_DEPENDENCIES = {
    "fle.cluster.remote.factorio_server_login": "pyautogui",  # [cluster] extra
}

DELETED_MODULES = [
    "fle.agents",
    "fle.configs",
    "fle.env.a2a_instance",
    "fle.env.a2a_namespace",
    "fle.env.protocols",
    "fle.eval.algorithms",
    "fle.eval.analysis",
    "fle.eval.entrypoints",
    "fle.eval.infra",
    "fle.eval.inspect_integration",
    "fle.eval.open",
    "fle.server",
    "fle.overlay",
    "fle.overlay_mcp",
    "fle.mcp_dataloader",
]


def _kept_modules() -> list[str]:
    """Every .py file under fle/ (most directories are namespace packages, which pkgutil skips)."""
    root = Path(fle.__file__).parent
    names = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root.parent).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        name = ".".join(parts)
        if "__pycache__" in parts:
            continue
        names.append(name)
    return names


def test_walk_finds_core_modules():
    names = _kept_modules()
    for expected in ("fle.env.instance", "fle.env.namespace", "fle.eval.tasks", "fle.env.gym_env.environment"):
        assert expected in names


@pytest.mark.parametrize("name", _kept_modules())
def test_module_imports(name):
    if name in OPTIONAL_DEPENDENCIES:
        pytest.importorskip(OPTIONAL_DEPENDENCIES[name])
    importlib.import_module(name)


@pytest.mark.parametrize("name", DELETED_MODULES)
def test_deleted_module_is_gone(name):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(name)


def test_fle_bridge_imports():
    """The surface factorio-architect's fle_bridge.py relies on."""
    from fle.env import FactorioInstance
    from fle.env.entities import Direction, Position
    from fle.env.game_types import Prototype, Resource

    assert FactorioInstance.__init__
    assert Direction.UP and Position(x=1, y=2).x == 1
    assert Prototype.IronPlate and Resource.IronOre
