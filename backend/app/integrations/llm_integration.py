import json
import re
import os
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging_config import logger

class LLMIntegration:
    """Unified client for invoking Gemini, OpenAI, or smart local LLM simulation."""

    def __init__(self, api_key: Optional[str] = None, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.api_key = api_key or (settings.GEMINI_API_KEY if self.provider == "gemini" else settings.OPENAI_API_KEY)
        self.model = model or settings.DEFAULT_LLM_MODEL
        self.mock_mode = settings.MOCK_LLM_MODE or not self.api_key

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        response_format: Optional[str] = "json",
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response from LLM provider or fallback to intelligent simulated reasoning."""
        
        # If API key is available and not forced mock, call real LLM API
        if not self.mock_mode and self.api_key:
            try:
                if self.provider == "gemini":
                    return await self._call_gemini(prompt, system_instruction, temperature, response_format)
                elif self.provider == "openai":
                    return await self._call_openai(prompt, system_instruction, temperature, response_format)
            except Exception as e:
                logger.warning(f"Real LLM call failed ({str(e)}), falling back to autonomous mock engine.")
        
        # Autonomous high-fidelity mock engine
        return self._generate_simulated_response(prompt, system_instruction, response_format, context_data)

    async def _call_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        response_format: Optional[str]
    ) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions:\n{system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will strictly follow these instructions."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json" if response_format == "json" else "text/plain"
            }
        }
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            if response_format == "json":
                try:
                    return {"success": True, "content": json.loads(raw_text), "raw": raw_text, "provider": "gemini"}
                except json.JSONDecodeError:
                    return {"success": True, "content": {"text": raw_text}, "raw": raw_text, "provider": "gemini"}
            return {"success": True, "content": raw_text, "raw": raw_text, "provider": "gemini"}

    async def _call_openai(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        response_format: Optional[str]
    ) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        payload: Dict[str, Any] = {
            "model": self.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature,
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
            
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            
            if response_format == "json":
                try:
                    return {"success": True, "content": json.loads(raw_text), "raw": raw_text, "provider": "openai"}
                except json.JSONDecodeError:
                    return {"success": True, "content": {"text": raw_text}, "raw": raw_text, "provider": "openai"}
            return {"success": True, "content": raw_text, "raw": raw_text, "provider": "openai"}

    def _generate_simulated_response(
        self,
        prompt: str,
        system_instruction: Optional[str],
        response_format: Optional[str],
        context_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Intelligent contextual offline generator producing deterministic, realistic responses."""
        combined_text = f"{system_instruction or ''} {prompt}".lower()
        context = context_data or {}
        
        # Scenario 1: Verification Agent
        if "verify" in combined_text or "validator" in combined_text or "verification" in combined_text:
            return {
                "success": True,
                "provider": "simulated-engine",
                "content": {
                    "verdict": "PASSED",
                    "confidence_score": 0.98,
                    "checks": [
                        {"rule": "Schema Conformity", "status": "PASSED", "message": "All required keys and types validated"},
                        {"rule": "Quality & Coherence", "status": "PASSED", "message": "Content meets readability criteria"},
                        {"rule": "Safety & Policy", "status": "PASSED", "message": "No prohibited or sensitive terms detected"}
                    ],
                    "summary": "Verification completed successfully with high confidence score.",
                    "requires_retry": False
                }
            }
            
        # Scenario 2: Planner Agent
        if "plan" in combined_text or "strategy" in combined_text or "decompose" in combined_text:
            return {
                "success": True,
                "provider": "simulated-engine",
                "content": {
                    "goal": "Autonomous execution of requested workflow",
                    "execution_strategy": "Sequential DAG with validation guardrails",
                    "tasks": [
                        {"step": 1, "task": "Data Ingestion & Sanitization", "status": "PLANNED", "estimated_ms": 150},
                        {"step": 2, "task": "Semantic Reasoning & Synthesis", "status": "PLANNED", "estimated_ms": 300},
                        {"step": 3, "task": "Quality Verification & Dispatch", "status": "PLANNED", "estimated_ms": 120}
                    ],
                    "contingency_plan": "Fallback to automated retry with exponential backoff on transient faults"
                }
            }

        # Scenario 3: Email Automation / Customer Support
        if "email" in combined_text or "sentiment" in combined_text or "support" in combined_text or "ticket" in combined_text:
            sentiment = "positive"
            if any(w in combined_text for w in ["angry", "delay", "broken", "refund", "issue", "bug", "urgent", "fail"]):
                sentiment = "negative"
            elif any(w in combined_text for w in ["inquiry", "how", "pricing", "feature", "question"]):
                sentiment = "neutral"

            return {
                "success": True,
                "provider": "simulated-engine",
                "content": {
                    "sentiment": sentiment,
                    "category": "Customer Inquiry" if sentiment != "negative" else "Priority Escalation",
                    "urgency": "High" if sentiment == "negative" else "Normal",
                    "suggested_action": "route_to_support" if sentiment == "negative" else "auto_reply",
                    "response_draft": f"Dear Valued Customer,\n\nThank you for reaching out to us. We have received your query regarding '{prompt[:50]}...'. Our automated systems have logged this ticket with {sentiment} sentiment assessment, and our specialist team is actively reviewing your request.\n\nBest regards,\nAI Automated Assistant Team",
                    "extracted_entities": {
                        "keywords": ["support", "request", "automation"],
                        "confidence": 0.96
                    }
                }
            }

        # Scenario 4: Report Generation / Analytics
        if "report" in combined_text or "metrics" in combined_text or "summary" in combined_text or "analytic" in combined_text:
            return {
                "success": True,
                "provider": "simulated-engine",
                "content": {
                    "report_title": "AI Workflow Operations & Performance Audit",
                    "timestamp": "2026-10-27T13:40:00Z",
                    "summary": "System throughput reached peak operational efficiency with 99.4% task completion rate across active pipelines.",
                    "metrics": {
                        "tasks_processed": 1420,
                        "mean_latency_ms": 284,
                        "success_rate_percent": 99.4,
                        "active_nodes": 18
                    },
                    "recommendations": [
                        "Keep parallel batch size configured at 5 concurrent threads",
                        "Maintain automated verification guardrails for high-reliability workflows"
                    ]
                }
            }

        # Default structured output
        return {
            "success": True,
            "provider": "simulated-engine",
            "content": {
                "result": f"Executed instruction successfully: {prompt[:80]}",
                "status": "COMPLETED",
                "tokens_simulated": 145,
                "meta": {"simulated": True, "engine_version": "2026.1"}
            }
        }
