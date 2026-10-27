from typing import Dict, Any, Optional
from app.integrations.email_integration import EmailIntegration
from app.integrations.webhook_integration import WebhookIntegration
from app.core.logging_config import logger

class NotificationService:
    """Service for system alerts and execution milestone notifications."""

    def __init__(self):
        self.email = EmailIntegration()
        self.webhook = WebhookIntegration()

    async def notify_execution_complete(
        self,
        execution_id: str,
        workflow_name: str,
        status: str,
        duration_seconds: float,
        recipient_email: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatches completion alert via configured notification channels."""
        subject = f"[{status}] Workflow '{workflow_name}' Finished"
        body = (
            f"Workflow Execution Notification:\n\n"
            f"Workflow: {workflow_name}\n"
            f"Execution ID: {execution_id}\n"
            f"Status: {status}\n"
            f"Duration: {duration_seconds:.2f}s\n"
        )

        results = {}
        if recipient_email:
            email_res = await self.email.send_email(to_email=recipient_email, subject=subject, body=body)
            results["email"] = email_res

        if webhook_url:
            webhook_res = await self.webhook.dispatch_webhook(
                url=webhook_url,
                payload={
                    "event": "workflow.execution_complete",
                    "execution_id": execution_id,
                    "workflow_name": workflow_name,
                    "status": status,
                    "duration_seconds": duration_seconds
                }
            )
            results["webhook"] = webhook_res

        logger.info(f"Notification sent for execution {execution_id} ({status})")
        return results
