from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.integrations.email_integration import EmailIntegration
from app.integrations.webhook_integration import WebhookIntegration
from app.integrations.llm_integration import LLMIntegration
from app.core.security import get_api_key

router = APIRouter(prefix="/integrations", tags=["Integrations"])

class TestEmailRequest(BaseModel):
    to_email: str
    subject: str = "Test Workflow Dispatch"
    body: str = "This is a verification test dispatch from AI Workflow Automation Engine."
    is_html: bool = False

class TestWebhookRequest(BaseModel):
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = None
    payload: Optional[Dict[str, Any]] = None

class TestLLMRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    system_instruction: Optional[str] = None

@router.post("/test-email")
async def test_email(
    payload: TestEmailRequest,
    _: str = Depends(get_api_key)
):
    """Test email integration dispatch."""
    email_client = EmailIntegration()
    result = await email_client.send_email(
        to_email=payload.to_email,
        subject=payload.subject,
        body=payload.body,
        is_html=payload.is_html
    )
    return result

@router.get("/email-outbox")
def get_email_outbox(
    limit: int = 50,
    _: str = Depends(get_api_key)
):
    """Inspect simulated email dispatch history."""
    return {"outbox": EmailIntegration.get_outbox(limit=limit)}

@router.post("/test-webhook")
async def test_webhook(
    payload: TestWebhookRequest,
    _: str = Depends(get_api_key)
):
    """Test outbound webhook dispatch."""
    result = await WebhookIntegration.dispatch_webhook(
        url=payload.url,
        method=payload.method,
        headers=payload.headers,
        payload=payload.payload
    )
    return result

@router.post("/test-llm")
async def test_llm(
    payload: TestLLMRequest,
    _: str = Depends(get_api_key)
):
    """Test LLM completion and cognitive agent reasoning."""
    llm_client = LLMIntegration(provider=payload.provider, model=payload.model)
    result = await llm_client.generate_completion(
        prompt=payload.prompt,
        system_instruction=payload.system_instruction,
        response_format="json"
    )
    return result
