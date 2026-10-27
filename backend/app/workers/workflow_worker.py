import time
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.workflow import Workflow, WorkflowSchedule
from app.models.execution import Execution
from app.engine.workflow_engine import WorkflowEngine
from app.core.logging_config import logger

class WorkflowWorker:
    """Independent background worker for processing queued workflow runs and scheduled triggers."""

    def __init__(self, poll_interval_seconds: float = 3.0):
        self.poll_interval = poll_interval_seconds
        self.is_running = False

    async def run_loop(self):
        """Main worker loop."""
        self.is_running = True
        logger.info("[WorkflowWorker] Background worker loop started.")

        while self.is_running:
            try:
                await self._process_pending_executions()
            except Exception as e:
                logger.error(f"[WorkflowWorker] Worker iteration encountered error: {str(e)}")
            await asyncio.sleep(self.poll_interval)

    async def _process_pending_executions(self):
        db: Session = SessionLocal()
        try:
            pending_exec = db.query(Execution).filter(
                Execution.status == "PENDING"
            ).order_by(Execution.created_at.asc()).first()

            if pending_exec:
                wf = db.query(Workflow).filter(Workflow.id == pending_exec.workflow_id).first()
                if wf:
                    logger.info(f"[WorkflowWorker] Claimed pending execution {pending_exec.id} for workflow '{wf.name}'")
                    engine = WorkflowEngine(db)
                    await engine.run_execution(
                        execution_id=pending_exec.id,
                        workflow=wf,
                        trigger_payload=pending_exec.trigger_payload
                    )
        finally:
            db.close()

    def stop(self):
        self.is_running = False
        logger.info("[WorkflowWorker] Background worker stopping.")

if __name__ == "__main__":
    worker = WorkflowWorker()
    try:
        asyncio.run(worker.run_loop())
    except KeyboardInterrupt:
        worker.stop()
