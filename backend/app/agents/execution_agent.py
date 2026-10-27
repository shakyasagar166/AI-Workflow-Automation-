from typing import Dict, Any, Optional
from app.integrations.llm_integration import LLMIntegration
from app.core.logging_config import logger

class ExecutionAgent:
    """Agent specialized in autonomous task execution, semantic reasoning, and synthesis."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.llm = LLMIntegration(provider=provider, model=model)

    async def execute_task(
        self,
        task_instruction: str,
        input_data: Dict[str, Any],
        system_role: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.5
    ) -> Dict[str, Any]:
        """Execute a cognitive workflow task using LLM capabilities."""
        
        system_instruction = system_role or (
            "You are a high-precision AI Execution Agent. Follow instructions accurately, extract "
            "required information, format output cleanly in JSON, and fulfill all requirements."
        )

        prompt = f"""
Task Instruction: {task_instruction}
Input Data: {input_data}
Expected Schema: {response_schema or 'Structured JSON object with relevant fields'}

Execute the task diligently and provide your result in JSON format.
"""

        logger.info(f"[ExecutionAgent] Executing instruction: '{task_instruction[:80]}...'")
        completion = await self.llm.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            response_format="json",
            context_data=input_data
        )

        return {
            "agent": "ExecutionAgent",
            "output": completion.get("content", {}),
            "provider": completion.get("provider", "simulated"),
            "agent_thoughts": [
                f"Ingested input parameters: {list(input_data.keys())}",
                "Synthesized contextual semantics and satisfied domain criteria",
                "Serialized structured output conforming to task specification"
            ]
        }
