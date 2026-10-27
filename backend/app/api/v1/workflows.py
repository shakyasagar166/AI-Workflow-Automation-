from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowExecuteRequest
)
from app.schemas.execution import ExecutionResponse
from app.services.workflow_service import WorkflowService
from app.services.execution_service import ExecutionService
from app.core.security import get_api_key

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Retrieve all defined workflows with optional status filtering."""
    service = WorkflowService(db)
    return service.list_workflows(skip=skip, limit=limit, status_filter=status)

@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_in: WorkflowCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Create a new workflow with DAG validation."""
    service = WorkflowService(db)
    return service.create_workflow(workflow_in)

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Get single workflow by ID."""
    service = WorkflowService(db)
    return service.get_workflow(workflow_id)

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: str,
    workflow_in: WorkflowUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Update workflow structure, nodes, or metadata."""
    service = WorkflowService(db)
    return service.update_workflow(workflow_id, workflow_in)

@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Delete a workflow and its associated executions."""
    service = WorkflowService(db)
    service.delete_workflow(workflow_id)
    return None

@router.post("/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    exec_req: WorkflowExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Trigger execution of a workflow."""
    exec_service = ExecutionService(db)
    execution = await exec_service.trigger_execution(
        workflow_id=workflow_id,
        trigger_payload=exec_req.trigger_payload,
        trigger_source="manual",
        run_async=exec_req.run_async,
        background_tasks=background_tasks
    )
    return execution

@router.post("/import", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def import_workflow(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Import a workflow from a JSON template definition."""
    service = WorkflowService(db)
    return service.import_workflow(payload)

@router.get("/{workflow_id}/export")
def export_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Export workflow graph definition as portable JSON."""
    service = WorkflowService(db)
    wf = service.get_workflow(workflow_id)
    return {
        "name": wf.name,
        "description": wf.description,
        "status": wf.status,
        "trigger_type": wf.trigger_type,
        "nodes": wf.nodes,
        "edges": wf.edges,
        "metadata_json": wf.metadata_json,
        "exported_at": wf.updated_at.isoformat()
    }
