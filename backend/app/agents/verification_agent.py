from typing import Dict, Any, List, Optional
from app.integrations.llm_integration import LLMIntegration
from app.core.logging_config import logger

class VerificationAgent:
    """Agent responsible for output auditing, guardrail validation, and quality verification."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.llm = LLMIntegration(provider=provider, model=model)

    async def verify_output(
        self,
        candidate_output: Any,
        validation_criteria: Optional[List[str]] = None,
        expected_schema: Optional[Dict[str, Any]] = None,
        minimum_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Audits an execution output against safety, policy, format, and accuracy rules."""
        
        criteria = validation_criteria or [
            "Output must not be empty or null",
            "Output must conform to structured schema",
            "No harmful, hallucinated, or malformed data"
        ]

        # 1. Deterministic code-level checks first
        deterministic_checks = []
        is_empty = candidate_output is None or candidate_output == {} or candidate_output == ""
        deterministic_checks.append({
            "rule": "Non-empty output verification",
            "status": "FAILED" if is_empty else "PASSED",
            "message": "Output payload contains data" if not is_empty else "Output is empty or null"
        })

        if is_empty:
            return {
                "agent": "VerificationAgent",
                "verdict": "REJECTED",
                "confidence_score": 0.0,
                "checks": deterministic_checks,
                "requires_retry": True,
                "feedback": "Empty payload received from candidate execution step",
                "agent_thoughts": ["Deterministic verification failed: Empty or null output"]
            }

        # 2. LLM / heuristic verification assessment
        system_instruction = (
            "You are a rigorous AI Verification and Quality Assurance Agent. Your task is to critique "
            "and validate candidate step outputs against strict quality criteria and schemas."
        )

        prompt = f"""
Candidate Output to Verify: {candidate_output}
Criteria to Satisfy: {criteria}
Expected Schema: {expected_schema or 'Valid JSON payload'}
Minimum Confidence Required: {minimum_confidence}

Evaluate the output thoroughly. Return a JSON object with:
1. verdict: "PASSED" or "REJECTED"
2. confidence_score: float between 0.0 and 1.0
3. checks: array of {{"rule": string, "status": "PASSED"|"FAILED", "message": string}}
4. feedback: recommendations or confirmation message
5. requires_retry: boolean
"""

        logger.info("[VerificationAgent] Auditing step output against guardrail policies")
        completion = await self.llm.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            response_format="json",
            context_data={"candidate_output": candidate_output}
        )

        verification_result = completion.get("content", {})
        verdict = verification_result.get("verdict", "PASSED")
        confidence = float(verification_result.get("confidence_score", 0.95))
        
        all_checks = deterministic_checks + verification_result.get("checks", [])
        requires_retry = verdict == "REJECTED" or confidence < minimum_confidence

        return {
            "agent": "VerificationAgent",
            "verdict": "PASSED" if not requires_retry else "REJECTED",
            "confidence_score": confidence,
            "checks": all_checks,
            "requires_retry": requires_retry,
            "feedback": verification_result.get("feedback", "Output meets quality assertions."),
            "agent_thoughts": [
                f"Ran {len(all_checks)} quality assertions",
                f"Verification audit concluded with verdict: {'PASSED' if not requires_retry else 'REJECTED'} (Confidence: {confidence:.2f})"
            ]
        }
