"""Benchmark task registry: works without the LLM harness and without a game server."""

from fle.commons.models.task_response import TaskResponse
from fle.eval.tasks import TaskABC, ThroughputTask, UnboundedThroughputTask
from fle.eval.tasks.task_definitions.unbounded.unbounded_tasks import (
    IRON_GEAR_WHEEL_THROUGHPUT_UNBOUNDED,
)
from fle.eval.tasks.task_definitions.task_registry import (
    create_task,
    get_task_info,
    list_all_tasks,
    list_tasks_by_category,
)


def test_throughput_tasks_are_registered():
    tasks = list_all_tasks()
    assert "iron_plate_throughput" in tasks
    assert "automation_science_pack_throughput" in tasks


def test_multiagent_dialogue_tasks_are_gone():
    assert not [key for key in list_all_tasks() if "multiagent" in key]
    assert set(list_tasks_by_category()) == {"throughput", "unbounded"}


def test_create_throughput_task():
    task = create_task("iron_plate_throughput")
    assert isinstance(task, ThroughputTask)
    assert isinstance(task, TaskABC)
    assert task.task_key == "iron_plate_throughput"


def test_create_unbounded_throughput_task():
    task = create_task(IRON_GEAR_WHEEL_THROUGHPUT_UNBOUNDED)
    assert isinstance(task, UnboundedThroughputTask)


def test_task_info_is_single_agent():
    info = get_task_info("iron_plate_throughput")
    assert info["num_agents"] == 1
    assert info["task_type"] == "throughput"


def test_default_enhance_response_passes_through():
    task = create_task("iron_plate_throughput")
    response = TaskResponse(success=False, meta={})
    assert isinstance(task.enhance_response_with_task_output("out", response), str)


def test_every_registered_task_can_be_created():
    """No config may exist that only the removed LLM harness could run."""
    for key in list_all_tasks():
        assert isinstance(create_task(key), TaskABC), key
