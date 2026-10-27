from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ExecutionLogResponse(BaseModel):
    id: str
    execution_id: str
    step_execution_id: Optional[str] = None
    node_id: Optional[str] = None
    level: str
    message: str
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class StepExecutionResponse(BaseModel):
    id: str
    execution_id: str
    node_id: str
    node_type: str
    node_name: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = 0.0
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    error: Optional[str] = None

    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger: str
    trigger_payload: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    step_executions: Optional[List[StepExecutionResponse]] = Field(default_factory=list)
    logs: Optional[List[ExecutionLogResponse]] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ExecutionSummaryResponse(BaseModel):
    id: str
    workflow_id: str
    workflow_name: Optional[str] = None
    status: str
    trigger: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = 0.0
    total_steps: int = 0
    completed_steps: int = 0
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
