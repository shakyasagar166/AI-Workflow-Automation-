import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from app.agents.planner_agent import PlannerAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.verification_agent import VerificationAgent
from app.integrations.email_integration import EmailIntegration
from app.integrations.webhook_integration import WebhookIntegration
from app.engine.dependency_resolver import DependencyResolver
from app.core.logging_config import logger

class TaskExecutor:
    """Executes single workflow nodes based on type and configuration."""

    def __init__(self):
        self.planner_agent = PlannerAgent()
        self.execution_agent = ExecutionAgent()
        self.verification_agent = VerificationAgent()
        self.email_integration = EmailIntegration()
        self.webhook_integration = WebhookIntegration()

    async def execute_node(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatches node execution to specialized agent, integration, or control unit."""
        node_id = node.get("id")
        node_type = node.get("type", "unknown")
        config = node.get("config", {}) or {}
        
        # 1. Interpolate variables in node config using accumulated workflow execution context
        interpolated_config = DependencyResolver.interpolate_value(config, context)
        
        logger.info(f"[TaskExecutor] Executing node '{node_id}' ({node_type})")
        started_at = datetime.utcnow()

        output_data = {}
        logs = []

        try:
            if node_type == "trigger":
                # Returns the incoming trigger payload or default test inputs
                payload = interpolated_config.get("default_payload", {})
                if "trigger" in context and context["trigger"]:
                    payload = context["trigger"]
                output_data = {
                    "status": "TRIGGERED",
                    "payload": payload,
                    "timestamp": started_at.isoformat()
                }
                logs.append(f"Trigger activated with payload: {list(payload.keys())}")

            elif node_type == "agent_planner":
                goal = interpolated_config.get("goal", "Decompose workflow tasks")
                constraints = interpolated_config.get("constraints", [])
                plan_result = await self.planner_agent.create_plan(
                    goal=goal,
                    input_data=interpolated_config.get("inputs", context.get("trigger", {})),
                    constraints=constraints,
                    context=context
                )
                output_data = plan_result
                logs.extend(plan_result.get("agent_thoughts", []))

            elif node_type == "agent_executor":
                instruction = interpolated_config.get("instruction", "Process input data")
                inputs = interpolated_config.get("inputs", {})
                if not inputs and "trigger" in context:
                    inputs = context["trigger"]
                role = interpolated_config.get("system_role", "AI Automation Specialist")
                temp = float(interpolated_config.get("temperature", 0.5))
                
                exec_result = await self.execution_agent.execute_task(
                    task_instruction=instruction,
                    input_data=inputs,
                    system_role=role,
                    temperature=temp
                )
                output_data = exec_result
                logs.extend(exec_result.get("agent_thoughts", []))

            elif node_type == "agent_verifier":
                candidate = interpolated_config.get("candidate_output")
                if not candidate:
                    # Fallback to the latest completed step in context
                    steps = context.get("steps", {})
                    if steps:
                        last_step = list(steps.values())[-1]
                        candidate = last_step.get("output", {})
                criteria = interpolated_config.get("criteria", [])
                min_conf = float(interpolated_config.get("minimum_confidence", 0.8))

                verif_result = await self.verification_agent.verify_output(
                    candidate_output=candidate,
                    validation_criteria=criteria,
                    minimum_confidence=min_conf
                )
                output_data = verif_result
                logs.extend(verif_result.get("agent_thoughts", []))

            elif node_type == "integration_email":
                to_addr = interpolated_config.get("to_email", "user@example.com")
                subj = interpolated_config.get("subject", "AI Workflow Notification")
                body = interpolated_config.get("body", "Workflow step finished successfully.")
                is_html = bool(interpolated_config.get("is_html", False))

                send_result = await self.email_integration.send_email(
                    to_email=to_addr,
                    subject=subj,
                    body=body,
                    is_html=is_html
                )
                output_data = send_result
                logs.append(f"Email sent to {to_addr}: '{subj}'")

            elif node_type == "integration_webhook":
                url = interpolated_config.get("url", "https://api.example.com/webhook")
                method = interpolated_config.get("method", "POST")
                headers = interpolated_config.get("headers", {})
                payload = interpolated_config.get("payload", {})

                webhook_result = await self.webhook_integration.dispatch_webhook(
                    url=url,
                    method=method,
                    headers=headers,
                    payload=payload
                )
                output_data = webhook_result
                logs.append(f"Webhook {method} {url} returned status {webhook_result.get('status_code')}")

            elif node_type == "condition":
                condition_expr = interpolated_config.get("expression", "true")
                left = interpolated_config.get("left_value")
                operator = interpolated_config.get("operator", "==")
                right = interpolated_config.get("right_value")

                verdict = True
                if operator == "==":
                    verdict = str(left).lower() == str(right).lower()
                elif operator == "!=":
                    verdict = str(left).lower() != str(right).lower()
                elif operator == ">":
                    verdict = float(left) > float(right)
                elif operator == "<":
                    verdict = float(left) < float(right)
                elif operator == "contains":
                    verdict = str(right).lower() in str(left).lower()

                output_data = {
                    "evaluation": verdict,
                    "condition_result": "true" if verdict else "false",
                    "left_value": left,
                    "operator": operator,
                    "right_value": right
                }
                logs.append(f"Condition evaluated: {left} {operator} {right} -> {verdict}")

            elif node_type == "data_transform":
                # Transform or pick specific fields
                mappings = interpolated_config.get("mappings", {})
                transformed = {}
                for target_k, source_v in mappings.items():
                    transformed[target_k] = source_v
                output_data = {"transformed": transformed, "original_inputs": interpolated_config}
                logs.append(f"Transformed {len(mappings)} data attributes")

            elif node_type == "delay":
                seconds = float(interpolated_config.get("seconds", 1.0))
                # Cap simulated delay at 5s during tests to keep responsiveness
                clamped_delay = min(seconds, 5.0)
                await asyncio.sleep(clamped_delay)
                output_data = {"delayed_seconds": clamped_delay, "requested_seconds": seconds}
                logs.append(f"Execution delayed for {clamped_delay}s")

            else:
                output_data = {"status": "SUCCESS", "message": f"Generic pass-through for {node_type}"}
                logs.append(f"Completed execution of generic node type: {node_type}")

            duration_sec = (datetime.utcnow() - started_at).total_seconds()
            return {
                "success": True,
                "output": output_data,
                "duration_seconds": round(duration_sec, 3),
                "logs": logs,
                "requires_retry": output_data.get("requires_retry", False)
            }

        except Exception as e:
            duration_sec = (datetime.utcnow() - started_at).total_seconds()
            logger.error(f"[TaskExecutor] Error executing node {node_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": round(duration_sec, 3),
                "logs": [f"Execution failed with error: {str(e)}"],
                "requires_retry": True
            }
