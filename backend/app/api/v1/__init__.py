from fastapi import APIRouter
from app.api.v1.workflows import router as workflows_router
from app.api.v1.executions import router as executions_router
from app.api.v1.integrations import router as integrations_router

api_v1_router = APIRouter()
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(executions_router)
api_v1_router.include_router(integrations_router)

__all__ = ["api_v1_router"]
