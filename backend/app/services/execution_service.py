import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks

from app.models.workflow import Workflow
from app.models.execution import Execution, StepExecution, ExecutionLog
from app.engine.workflow_engine import WorkflowEngine
from app.db.database import SessionLocal
from app.core.logging_config import logger

class ExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Execution]:
        query = self.db.query(Execution)
        if workflow_id:
            query = query.filter(Execution.workflow_id == workflow_id)
        if status_filter:
            query = query.filter(Execution.status == status_filter)
        return query.order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()

    def get_execution(self, execution_id: str) -> Execution:
        execution = self.db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution '{execution_id}' not found")
        return execution

    def get_execution_logs(self, execution_id: str) -> List[ExecutionLog]:
        self.get_execution(execution_id)
        return self.db.query(ExecutionLog).filter(
            ExecutionLog.execution_id == execution_id
        ).order_by(ExecutionLog.timestamp.asc()).all()

    async def trigger_execution(
        self,
        workflow_id: str,
        trigger_payload: Optional[Dict[str, Any]] = None,
        trigger_source: str = "manual",
        run_async: bool = False,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Execution:
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found")

        execution = Execution(
            workflow_id=workflow.id,
            status="PENDING",
            trigger=trigger_source,
            trigger_payload=trigger_payload or {}
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        if run_async and background_tasks:
            # Dispatch background worker task
            background_tasks.add_task(self._run_async_worker, execution.id, workflow.id, trigger_payload)
            return execution
        else:
            # Run synchronously and await completion
            engine = WorkflowEngine(self.db)
            completed_execution = await engine.run_execution(execution.id, workflow, trigger_payload)
            return completed_execution

    @staticmethod
    def _run_async_worker(execution_id: str, workflow_id: str, trigger_payload: Optional[Dict[str, Any]]):
        """Background async task running in independent DB session."""
        db = SessionLocal()
        try:
            workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                return
            engine = WorkflowEngine(db)
            asyncio.run(engine.run_execution(execution_id, workflow, trigger_payload))
        except Exception as e:
            logger.error(f"Async worker failed for execution {execution_id}: {str(e)}")
        finally:
            db.close()

    def cancel_execution(self, execution_id: str) -> Execution:
        execution = self.get_execution(execution_id)
        if execution.status in ["COMPLETED", "FAILED", "CANCELLED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel execution in state '{execution.status}'")
        
        execution.status = "CANCELLED"
        execution.completed_at = datetime.utcnow()
        if execution.started_at:
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        self.db.commit()
        self.db.refresh(execution)
        return execution
