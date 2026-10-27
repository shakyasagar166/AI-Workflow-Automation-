import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.logging_config import logger
from app.db.database import init_db, get_db, SessionLocal
from app.api.v1 import api_v1_router
from app.models.workflow import Workflow
from app.models.execution import Execution

def seed_sample_workflows():
    """Seeds sample workflows if the database is newly initialized."""
    db: Session = SessionLocal()
    try:
        count = db.query(Workflow).count()
        if count == 0:
            logger.info("Database is empty. Seeding pre-configured production workflow templates...")
            
            # Workflow 1: Email Automation
            email_wf = Workflow(
                name="Autonomous Email Triage & Response",
                description="Ingests incoming customer emails, performs AI sentiment & intent classification, verifies draft response quality, and dispatches reply.",
                status="active",
                trigger_type="webhook",
                nodes=[
                    {
                        "id": "node_trigger",
                        "type": "trigger",
                        "name": "Incoming Email Webhook",
                        "config": {
                            "default_payload": {
                                "from_email": "jane.doe@enterprise.com",
                                "subject": "Urgent inquiry regarding API latency spikes",
                                "body": "Hello support team, we noticed elevated latency in the APAC region over the last hour. Is there an active incident?"
                            }
                        },
                        "position": {"x": 100, "y": 150}
                    },
                    {
                        "id": "node_planner",
                        "type": "agent_planner",
                        "name": "AI Triage Planner",
                        "config": {
                            "goal": "Analyze customer email, categorize priority, and draft resolution plan",
                            "inputs": "{{steps.node_trigger.output.payload}}"
                        },
                        "position": {"x": 350, "y": 150}
                    },
                    {
                        "id": "node_executor",
                        "type": "agent_executor",
                        "name": "Response Synthesis Agent",
                        "config": {
                            "instruction": "Draft a personalized, professional customer support reply resolving the inquiry.",
                            "inputs": "{{steps.node_planner.output.plan}}",
                            "system_role": "Senior Enterprise Customer Success Engineer"
                        },
                        "position": {"x": 620, "y": 150}
                    },
                    {
                        "id": "node_verifier",
                        "type": "agent_verifier",
                        "name": "Quality & Policy Verifier",
                        "config": {
                            "candidate_output": "{{steps.node_executor.output.output}}",
                            "criteria": ["Response is polite and professional", "Contains no internal secrets", "Addresses latency topic directly"],
                            "minimum_confidence": 0.85
                        },
                        "position": {"x": 900, "y": 150}
                    },
                    {
                        "id": "node_email_dispatch",
                        "type": "integration_email",
                        "name": "Dispatch Verified Email",
                        "config": {
                            "to_email": "{{steps.node_trigger.output.payload.from_email}}",
                            "subject": "Re: {{steps.node_trigger.output.payload.subject}} [Ticket Auto-Resolved]",
                            "body": "{{steps.node_executor.output.output.response_draft}}"
                        },
                        "position": {"x": 1180, "y": 150}
                    }
                ],
                edges=[
                    {"id": "e1", "source": "node_trigger", "target": "node_planner"},
                    {"id": "e2", "source": "node_planner", "target": "node_executor"},
                    {"id": "e3", "source": "node_executor", "target": "node_verifier"},
                    {"id": "e4", "source": "node_verifier", "target": "node_email_dispatch"}
                ]
            )

            # Workflow 2: Report Generation
            report_wf = Workflow(
                name="Executive KPI & Incident Digest",
                description="Aggregates telemetry metrics, synthesizes executive briefing via AI reasoning agent, validates report accuracy, and sends alert webhook.",
                status="active",
                trigger_type="schedule",
                nodes=[
                    {
                        "id": "trig_schedule",
                        "type": "trigger",
                        "name": "Scheduled Daily Cron",
                        "config": {"default_payload": {"period": "24h", "target_audience": "Leadership"}},
                        "position": {"x": 100, "y": 250}
                    },
                    {
                        "id": "agent_analytics",
                        "type": "agent_executor",
                        "name": "Data Synthesis Agent",
                        "config": {
                            "instruction": "Compile daily performance audit report with latency metrics and throughput figures.",
                            "inputs": {"period": "24h"}
                        },
                        "position": {"x": 380, "y": 250}
                    },
                    {
                        "id": "agent_guardrail",
                        "type": "agent_verifier",
                        "name": "Executive Guardrail Verifier",
                        "config": {
                            "candidate_output": "{{steps.agent_analytics.output.output}}",
                            "criteria": ["Metrics are well-formatted", "Actionable recommendations provided"],
                            "minimum_confidence": 0.9
                        },
                        "position": {"x": 680, "y": 250}
                    },
                    {
                        "id": "webhook_slack",
                        "type": "integration_webhook",
                        "name": "Broadcast to Webhook",
                        "config": {
                            "url": "https://api.example.com/webhook/kpi-digest",
                            "method": "POST",
                            "payload": "{{steps.agent_analytics.output.output}}"
                        },
                        "position": {"x": 980, "y": 250}
                    }
                ],
                edges=[
                    {"id": "er1", "source": "trig_schedule", "target": "agent_analytics"},
                    {"id": "er2", "source": "agent_analytics", "target": "agent_guardrail"},
                    {"id": "er3", "source": "agent_guardrail", "target": "webhook_slack"}
                ]
            )

            db.add(email_wf)
            db.add(report_wf)
            db.commit()
            logger.info("Successfully seeded default sample workflows.")
    except Exception as e:
        logger.error(f"Error seeding workflows: {str(e)}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}...")
    init_db()
    seed_sample_workflows()
    yield
    # Shutdown
    logger.info("Shutting down AI Workflow Automation Engine...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mock_llm_mode": settings.MOCK_LLM_MODE
    }

@app.get("/api/v1/stats", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Aggregate dashboard metrics for UI presentation."""
    total_workflows = db.query(Workflow).count()
    active_workflows = db.query(Workflow).filter(Workflow.status == "active").count()
    total_executions = db.query(Execution).count()
    completed_executions = db.query(Execution).filter(Execution.status == "COMPLETED").count()
    failed_executions = db.query(Execution).filter(Execution.status == "FAILED").count()
    running_executions = db.query(Execution).filter(Execution.status == "RUNNING").count()

    success_rate = 0.0
    if total_executions > 0:
        success_rate = round((completed_executions / total_executions) * 100, 1)

    avg_duration = db.query(func.avg(Execution.duration_seconds)).filter(Execution.status == "COMPLETED").scalar() or 0.0

    return {
        "total_workflows": total_workflows,
        "active_workflows": active_workflows,
        "total_executions": total_executions,
        "completed_executions": completed_executions,
        "failed_executions": failed_executions,
        "running_executions": running_executions,
        "success_rate_percent": success_rate,
        "average_duration_seconds": round(float(avg_duration), 2)
    }
