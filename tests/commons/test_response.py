"""Response (one environment step's outcome) lives in fle.commons.models."""

import datetime

import pytest
from pydantic import ValidationError

from fle.commons.models.achievements import ProductionFlows
from fle.commons.models.response import Response
from fle.commons.models.task_response import TaskResponse


def _flows() -> ProductionFlows:
    return ProductionFlows(input={}, output={"iron-plate": 3.0}, crafted=[], harvested={})


def _response(**overrides) -> Response:
    fields = dict(
        score=1.5,
        achievements={},
        flows=_flows(),
        task=TaskResponse(success=False),
        step=0,
        ticks=60,
        code="print(1)",
        created_at=datetime.datetime(2026, 1, 1),
        response="1",
    )
    fields.update(overrides)
    return Response(**fields)


def test_defaults():
    response = _response()
    assert response.automated_score == 0.0
    assert response.error is False
    assert response.program_id is None


def test_holds_flows_and_task():
    response = _response(task=TaskResponse(success=True, meta={"a": 1}))
    assert response.flows.output == {"iron-plate": 3.0}
    assert response.task.success is True
    assert response.task.meta == {"a": 1}


def test_score_is_required():
    fields = _response().model_dump()
    del fields["score"]
    with pytest.raises(ValidationError):
        Response(**fields)
