from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class NodePosition(BaseModel):
    x: float = 0.0
    y: float = 0.0

class NodeSchema(BaseModel):
    id: str
    type: str  # trigger, agent_planner, agent_executor, agent_verifier, integration_email, integration_webhook, condition, data_transform, delay
    name: str = ""
    label: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[NodePosition] = Field(default_factory=NodePosition)

class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    label: Optional[str] = None
    condition: Optional[str] = None  # e.g., "true", "false", "{{status}} == 'APPROVED'"

class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="active")
    trigger_type: str = Field(default="manual")
    nodes: List[NodeSchema] = Field(default_factory=list)
    edges: List[EdgeSchema] = Field(default_factory=list)
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    trigger_type: Optional[str] = None
    nodes: Optional[List[NodeSchema]] = None
    edges: Optional[List[EdgeSchema]] = None
    metadata_json: Optional[Dict[str, Any]] = None

class WorkflowResponse(WorkflowBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowExecuteRequest(BaseModel):
    trigger_payload: Optional[Dict[str, Any]] = Field(default_factory=dict)
    run_async: bool = False

class WorkflowScheduleCreate(BaseModel):
    cron_expression: str
    is_enabled: bool = True

class WorkflowScheduleResponse(BaseModel):
    id: str
    workflow_id: str
    cron_expression: str
    is_enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
