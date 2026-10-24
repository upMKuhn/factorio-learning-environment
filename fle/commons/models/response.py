import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from fle.commons.models.achievements import ProductionFlows
from fle.commons.models.task_response import TaskResponse


class Response(BaseModel):
    """Outcome of executing one program (one environment step)."""

    score: float
    automated_score: float = 0.0  # Score excluding harvested and manually crafted items
    achievements: Dict[Any, Any]
    flows: ProductionFlows
    task: TaskResponse
    step: int
    ticks: int
    code: str
    created_at: datetime.datetime
    response: str
    error: bool = False
    program_id: Optional[int] = None
