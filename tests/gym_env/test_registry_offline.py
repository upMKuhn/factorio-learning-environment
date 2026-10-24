"""Gym registry discovery works offline (no Docker, no A2A server)."""

from fle.env.gym_env.registry import get_environment_info, list_available_environments


def test_discovers_throughput_environments():
    assert "iron_plate_throughput" in list_available_environments()


def test_no_multiagent_environments():
    assert not [e for e in list_available_environments() if "multiagent" in e]


def test_environment_info():
    info = get_environment_info("iron_plate_throughput")
    assert info["num_agents"] == 1
    assert info["task_key"] == "iron_plate_throughput"
    assert get_environment_info("does_not_exist") is None
