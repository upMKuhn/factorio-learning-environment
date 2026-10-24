from typing import Any, Dict

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    """Outcome of a benchmark task's verification step."""

    success: bool
    meta: Dict[str, Any] = Field(default_factory=dict)
