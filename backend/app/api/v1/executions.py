from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.execution import (
    ExecutionResponse,
    ExecutionSummaryResponse,
    ExecutionLogResponse
)
from app.services.execution_service import ExecutionService
from app.core.security import get_api_key

router = APIRouter(prefix="/executions", tags=["Executions"])

@router.get("", response_model=List[ExecutionResponse])
def list_executions(
    workflow_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Retrieve history of workflow executions."""
    service = ExecutionService(db)
    return service.list_executions(workflow_id=workflow_id, status_filter=status, skip=skip, limit=limit)

@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Get full details of a specific execution, including steps and logs."""
    service = ExecutionService(db)
    return service.get_execution(execution_id)

@router.get("/{execution_id}/logs", response_model=List[ExecutionLogResponse])
def get_execution_logs(
    execution_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Get chronological execution logs and agent reasoning traces."""
    service = ExecutionService(db)
    return service.get_execution_logs(execution_id)

@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
def cancel_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Cancel an active execution run."""
    service = ExecutionService(db)
    return service.cancel_execution(execution_id)

@router.post("/{execution_id}/retry", response_model=ExecutionResponse)
async def retry_execution(
    execution_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(get_api_key)
):
    """Rerun an execution with its original inputs and configuration."""
    service = ExecutionService(db)
    original = service.get_execution(execution_id)
    return await service.trigger_execution(
        workflow_id=original.workflow_id,
        trigger_payload=original.trigger_payload,
        trigger_source=f"retry_{original.id[:8]}",
        run_async=False,
        background_tasks=background_tasks
    )
