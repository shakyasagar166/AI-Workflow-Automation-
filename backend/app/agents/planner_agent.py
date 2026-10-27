from typing import Dict, Any, List, Optional
from app.integrations.llm_integration import LLMIntegration
from app.core.logging_config import logger

class PlannerAgent:
    """Agent responsible for task decomposition, resource planning, and strategy formulation."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.llm = LLMIntegration(provider=provider, model=model)

    async def create_plan(
        self,
        goal: str,
        input_data: Dict[str, Any],
        constraints: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyzes workflow goal and context to create a multi-step execution plan."""
        
        system_instruction = (
            "You are an expert AI Planner Agent in an enterprise workflow automation system. "
            "Your job is to analyze the operational goal and input parameters, break down the process into "
            "clear executable subtasks, define required data transformations, and identify risks or validation rules."
        )

        prompt = f"""
Goal: {goal}
Input Parameters: {input_data}
Constraints: {constraints or ['Enforce schema validity', 'Ensure idempotency']}
Context: {context or {}}

Generate a structured execution plan in JSON containing:
1. goal_summary: Brief statement of the target
2. execution_strategy: Strategy description
3. tasks: Array of ordered tasks, each with task_id, title, expected_inputs, expected_outputs, and timeout_ms
4. validation_criteria: Key verification rules needed
"""

        logger.info(f"[PlannerAgent] Planning for goal: '{goal}'")
        completion = await self.llm.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            response_format="json",
            context_data={"goal": goal, "input_data": input_data}
        )

        plan_content = completion.get("content", {})
        return {
            "agent": "PlannerAgent",
            "plan": plan_content,
            "provider": completion.get("provider", "simulated"),
            "agent_thoughts": [
                f"Assessed objective: {goal}",
                f"Generated execution strategy with {len(plan_content.get('tasks', []))} phased subtasks",
                "Assigned verification checkpoints and error-recovery policies"
            ]
        }
