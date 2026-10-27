import asyncio
from datetime import datetime
from typing import Dict, Any, List, Set, Optional
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.models.execution import Execution, StepExecution, ExecutionLog
from app.engine.dependency_resolver import DependencyResolver
from app.engine.task_executor import TaskExecutor
from app.engine.retry_handler import RetryHandler
from app.core.logging_config import logger

class WorkflowEngine:
    """Asynchronous Orchestration Engine for Multi-Agent and Integration DAG Workflows."""

    def __init__(self, db: Session):
        self.db = db
        self.task_executor = TaskExecutor()
        self.retry_handler = RetryHandler()
        self._lock = None

    async def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def run_execution(
        self,
        execution_id: str,
        workflow: Workflow,
        trigger_payload: Optional[Dict[str, Any]] = None
    ) -> Execution:
        """Executes the workflow graph end-to-end with persistent step and log tracking."""
        self._lock = asyncio.Lock()
        execution = self.db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            raise ValueError(f"Execution record {execution_id} not found")

        execution.status = "RUNNING"
        execution.started_at = datetime.utcnow()
        self.db.commit()

        await self._add_log(execution_id, None, None, "INFO", f"Starting workflow '{workflow.name}' (ID: {workflow.id})")

        nodes = workflow.nodes or []
        edges = workflow.edges or []

        # 1. Validate DAG
        is_valid, validation_err = DependencyResolver.validate_dag(nodes, edges)
        if not is_valid:
            execution.status = "FAILED"
            execution.error = validation_err
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            await self._add_log(execution_id, None, None, "ERROR", f"DAG Validation Failed: {validation_err}")
            self.db.commit()
            return execution

        # 2. Setup execution context and tracking
        context: Dict[str, Any] = {
            "trigger": trigger_payload or {},
            "steps": {},
            "workflow": {"id": workflow.id, "name": workflow.name}
        }

        node_map = {n["id"]: n for n in nodes}
        dependencies = DependencyResolver.build_dependency_graph(nodes, edges)
        
        # Build edge adjacency for conditions: source -> list of (target, condition)
        out_edges: Dict[str, List[Dict[str, Any]]] = {n["id"]: [] for n in nodes}
        for edge in edges:
            src = edge.get("source")
            if src in out_edges:
                out_edges[src].append(edge)

        completed_nodes: Set[str] = set()
        skipped_nodes: Set[str] = set()
        failed_nodes: Set[str] = set()
        running_nodes: Set[str] = set()

        # Find initial ready nodes (dependencies empty)
        ready_nodes = [nid for nid, deps in dependencies.items() if len(deps) == 0]

        while ready_nodes or running_nodes:
            # Launch batch of ready nodes up to concurrency limit
            tasks_to_launch = []
            while ready_nodes:
                nid = ready_nodes.pop(0)
                running_nodes.add(nid)
                tasks_to_launch.append(self._execute_single_node_with_retry(
                    execution_id=execution_id,
                    node=node_map[nid],
                    context=context
                ))

            if not tasks_to_launch:
                await asyncio.sleep(0.05)
                continue

            results = await asyncio.gather(*tasks_to_launch, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    logger.error(f"Node execution raised unhandled exception: {str(res)}")
                    continue

                nid = res["node_id"]
                running_nodes.remove(nid)

                if res["success"]:
                    completed_nodes.add(nid)
                    context["steps"][nid] = {
                        "output": res.get("output", {}),
                        "duration_seconds": res.get("duration_seconds", 0.0)
                    }

                    # Determine downstream branch activation based on conditions
                    node_output = res.get("output", {})
                    cond_result = str(node_output.get("condition_result", "")).lower()

                    for edge in out_edges.get(nid, []):
                        target = edge.get("target")
                        edge_cond = edge.get("condition")

                        # If edge has a condition specified (e.g., "true" or "false")
                        if edge_cond is not None and edge_cond != "":
                            if str(edge_cond).lower() != cond_result:
                                # Skip branch
                                skipped_nodes.add(target)
                                await self._mark_step_skipped(execution_id, target, node_map.get(target, {}))
                                await self._add_log(execution_id, None, target, "INFO", f"Branch condition not met ({edge_cond} != {cond_result}). Node skipped.")
                else:
                    failed_nodes.add(nid)
                    # Node failed and retries exhausted
                    await self._add_log(execution_id, None, nid, "ERROR", f"Node '{nid}' execution failed: {res.get('error')}")

            # Check for new ready nodes
            for nid, deps in dependencies.items():
                if nid not in completed_nodes and nid not in running_nodes and nid not in failed_nodes and nid not in skipped_nodes and nid not in ready_nodes:
                    # All active prerequisites must be satisfied
                    unmet_deps = [d for d in deps if d not in completed_nodes]
                    # If any prereq was skipped or failed, this node cannot proceed
                    has_skipped_or_failed = any(d in skipped_nodes or d in failed_nodes for d in deps)
                    if has_skipped_or_failed:
                        skipped_nodes.add(nid)
                        await self._mark_step_skipped(execution_id, nid, node_map.get(nid, {}))
                    elif len(unmet_deps) == 0:
                        ready_nodes.append(nid)

            # If any non-recoverable failure occurred and no more nodes can run
            if failed_nodes and not running_nodes and not ready_nodes:
                break

        # 3. Finalize execution status
        execution.completed_at = datetime.utcnow()
        execution.duration_seconds = round((execution.completed_at - execution.started_at).total_seconds(), 3)

        if failed_nodes:
            execution.status = "FAILED"
            execution.error = f"Nodes failed: {', '.join(failed_nodes)}"
            await self._add_log(execution_id, None, None, "ERROR", f"Workflow execution completed with failure in nodes: {failed_nodes}")
        else:
            execution.status = "COMPLETED"
            execution.result = {
                "summary": "Workflow executed successfully",
                "completed_nodes": list(completed_nodes),
                "skipped_nodes": list(skipped_nodes),
                "steps": {nid: s.get("output") for nid, s in context["steps"].items()}
            }
            await self._add_log(execution_id, None, None, "INFO", f"Workflow execution finished successfully in {execution.duration_seconds}s")

        self.db.commit()
        return execution

    async def _execute_single_node_with_retry(
        self,
        execution_id: str,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs node with automated retry loop and records StepExecution in DB."""
        nid = node["id"]
        ntype = node.get("type", "unknown")
        nname = node.get("name") or node.get("label") or nid

        step_exec = StepExecution(
            execution_id=execution_id,
            node_id=nid,
            node_type=ntype,
            node_name=nname,
            status="RUNNING",
            started_at=datetime.utcnow(),
            input_data=node.get("config", {})
        )
        async with self._lock:
            self.db.add(step_exec)
            self.db.commit()

        await self._add_log(execution_id, step_exec.id, nid, "INFO", f"Starting node '{nname}' ({ntype})")

        attempt = 0
        last_result = None

        while True:
            result = await self.task_executor.execute_node(node, context)
            last_result = result
            
            # Log any agent thoughts or outputs
            for log_msg in result.get("logs", []):
                lvl = "AGENT_THOUGHT" if "Assessed" in log_msg or "Synthesized" in log_msg or "Ran" in log_msg else "INFO"
                await self._add_log(execution_id, step_exec.id, nid, lvl, log_msg)

            if result["success"] and not result.get("requires_retry"):
                async with self._lock:
                    step_exec.status = "COMPLETED"
                    step_exec.completed_at = datetime.utcnow()
                    step_exec.duration_seconds = result["duration_seconds"]
                    step_exec.output_data = result.get("output", {})
                    step_exec.retry_count = attempt
                    self.db.commit()
                return {"node_id": nid, "success": True, "output": result.get("output", {}), "duration_seconds": result["duration_seconds"]}

            # Step failed or verification requested retry
            attempt += 1
            if self.retry_handler.should_retry(attempt, output=result.get("output")):
                async with self._lock:
                    step_exec.status = "RETRYING"
                    step_exec.retry_count = attempt
                    self.db.commit()
                await self._add_log(execution_id, step_exec.id, nid, "WARN", f"Step '{nname}' triggered retry policy (attempt {attempt})")
                await self.retry_handler.sleep_backoff(attempt)
            else:
                # Retries exhausted or non-retryable
                async with self._lock:
                    step_exec.status = "FAILED"
                    step_exec.completed_at = datetime.utcnow()
                    step_exec.duration_seconds = result.get("duration_seconds", 0.0)
                    step_exec.error = result.get("error") or str(result.get("output", {}).get("feedback", "Step verification rejected"))
                    step_exec.retry_count = attempt
                    self.db.commit()
                return {"node_id": nid, "success": False, "error": step_exec.error}

    async def _mark_step_skipped(self, execution_id: str, node_id: str, node: Dict[str, Any]):
        nname = node.get("name") or node.get("label") or node_id
        step = StepExecution(
            execution_id=execution_id,
            node_id=node_id,
            node_type=node.get("type", "unknown"),
            node_name=nname,
            status="SKIPPED",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.0
        )
        async with self._lock:
            self.db.add(step)
            self.db.commit()

    async def _add_log(self, execution_id: str, step_id: Optional[str], node_id: Optional[str], level: str, message: str, meta: Optional[Dict[str, Any]] = None):
        log = ExecutionLog(
            execution_id=execution_id,
            step_execution_id=step_id,
            node_id=node_id,
            level=level,
            message=message,
            metadata_json=meta,
            timestamp=datetime.utcnow()
        )
        async with self._lock:
            self.db.add(log)
            self.db.commit()
