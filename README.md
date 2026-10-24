# Factorio Learning Environment (slim fork)

A fork of the [Factorio Learning Environment](https://github.com/JackHopkins/factorio-learning-environment)
([paper](https://arxiv.org/abs/2503.09617)) cut down to one job: **interfacing with Factorio and its benchmarks**.
The upstream LLM-agent harness (agents, Inspect/MCP/A2A integrations, eval runners, plots, docs site) has been removed.

## What is here

| Path | Purpose |
|------|---------|
| `fle/env` | `FactorioInstance` (RCON connection, Lua tool loading, Python namespace), entities and game types, agent/admin tools, Lua mods |
| `fle/env/gym_env` | Gym interface (`FactorioGymEnv`) and a registry that exposes every benchmark task via `gym.make()` |
| `fle/eval/tasks` | Benchmark task definitions: throughput (lab play) and unbounded tasks, plus their registry |
| `fle/cluster` | Docker headless servers, scenarios, server config |
| `fle/commons` | Shared pydantic/data models (game state, research state, production flows, step and task results) |

## Usage

Requires Docker and Python 3.10+.

```bash
uv sync
fle cluster start -n 1        # start headless Factorio server(s)
fle sprites                   # optional: sprites for the render tool / gym vision
```

```python
from fle.env import FactorioInstance

instance = FactorioInstance(address="localhost", tcp_port=27000, fast=True)
namespace = instance.namespace
```

```python
import gym
import fle.env.gym_env.registry  # registers all benchmark tasks

env = gym.make("iron_plate_throughput", run_idx=0)
```

## Tests

Most tests drive a live server (`fle cluster start`). Unit tests that need no server run with:

```bash
pytest tests/test_package_imports.py tests/test_cli.py tests/commons tests/tasks \
       tests/gym_env/test_registry_offline.py tests/gym_env/test_observation_formatter.py \
       tests/render/test_sprite_pipeline.py tests/test_rcon_utils.py
```
