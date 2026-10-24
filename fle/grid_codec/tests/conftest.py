from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
BLUEPRINTS_JSONL = REPO / "blueprints_v2" / "blueprints.jsonl"
RECIPE_DATA = REPO / "data" / "spa" / "data.json"
PROTOTYPE_DUMP = Path.home() / "Library/Application Support/factorio/script-output/data-raw-dump.json"


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: reads the full 2.8 GB blueprint source")


@pytest.fixture(scope="session")
def recipe_data():
    from fle.grid_codec.blueprints import RecipeData
    if not RECIPE_DATA.exists():
        pytest.skip(f"{RECIPE_DATA} missing")
    return RecipeData.load(RECIPE_DATA)
