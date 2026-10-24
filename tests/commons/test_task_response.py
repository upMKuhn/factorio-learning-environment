"""TaskResponse lives in fle.commons.models (moved out of the deleted fle.agents)."""

import pytest
from pydantic import ValidationError

from fle.commons.models.task_response import TaskResponse


def test_success_is_required():
    with pytest.raises(ValidationError):
        TaskResponse()


def test_meta_defaults_to_empty_dict():
    response = TaskResponse(success=True)
    assert response.success is True
    assert response.meta == {}


def test_meta_default_is_not_shared_between_instances():
    first = TaskResponse(success=False)
    first.meta["key"] = "value"
    assert TaskResponse(success=False).meta == {}


def test_meta_round_trips():
    response = TaskResponse(success=False, meta={"throughput": 12.5})
    assert TaskResponse.model_validate(response.model_dump()) == response
