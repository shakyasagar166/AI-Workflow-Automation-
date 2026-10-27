from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.workflow import Workflow, WorkflowSchedule
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.engine.dependency_resolver import DependencyResolver
from app.core.logging_config import logger

class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def list_workflows(self, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None) -> List[Workflow]:
        query = self.db.query(Workflow)
        if status_filter:
            query = query.filter(Workflow.status == status_filter)
        return query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit).all()

    def get_workflow(self, workflow_id: str) -> Workflow:
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow '{workflow_id}' not found")
        return workflow

    def create_workflow(self, data: WorkflowCreate) -> Workflow:
        # Validate DAG structure
        nodes_dict = [n.model_dump() for n in data.nodes]
        edges_dict = [e.model_dump() for e in data.edges]
        is_valid, err = DependencyResolver.validate_dag(nodes_dict, edges_dict)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        workflow = Workflow(
            name=data.name,
            description=data.description,
            status=data.status,
            trigger_type=data.trigger_type,
            nodes=nodes_dict,
            edges=edges_dict,
            metadata_json=data.metadata_json or {}
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        logger.info(f"Created workflow '{workflow.name}' with id: {workflow.id}")
        return workflow

    def update_workflow(self, workflow_id: str, data: WorkflowUpdate) -> Workflow:
        workflow = self.get_workflow(workflow_id)

        update_dict = data.model_dump(exclude_unset=True)
        nodes_dict = [n.model_dump() if hasattr(n, "model_dump") else n for n in update_dict.get("nodes", workflow.nodes or [])]
        edges_dict = [e.model_dump() if hasattr(e, "model_dump") else e for e in update_dict.get("edges", workflow.edges or [])]

        is_valid, err = DependencyResolver.validate_dag(nodes_dict, edges_dict)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

        for k, v in update_dict.items():
            if k == "nodes":
                setattr(workflow, k, nodes_dict)
            elif k == "edges":
                setattr(workflow, k, edges_dict)
            else:
                setattr(workflow, k, v)

        self.db.commit()
        self.db.refresh(workflow)
        logger.info(f"Updated workflow '{workflow.name}' (id: {workflow.id})")
        return workflow

    def delete_workflow(self, workflow_id: str) -> bool:
        workflow = self.get_workflow(workflow_id)
        self.db.delete(workflow)
        self.db.commit()
        logger.info(f"Deleted workflow '{workflow_id}'")
        return True

    def import_workflow(self, payload: Dict[str, Any]) -> Workflow:
        wf_create = WorkflowCreate(
            name=payload.get("name", "Imported Workflow"),
            description=payload.get("description", "Imported via template JSON"),
            status=payload.get("status", "active"),
            trigger_type=payload.get("trigger_type", "manual"),
            nodes=payload.get("nodes", []),
            edges=payload.get("edges", []),
            metadata_json=payload.get("metadata_json", {})
        )
        return self.create_workflow(wf_create)
