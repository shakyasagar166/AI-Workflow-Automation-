import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Workflow Automation System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise-Grade Autonomous AI Workflow Automation and Orchestration Platform"
    
    # Database
    DATABASE_URL: str = "sqlite:///./workflow_automation.db"
    
    # Security
    SECRET_KEY: str = "super-secret-system-key-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    API_KEY_HEADER_NAME: str = "X-API-KEY"
    DEFAULT_API_KEY: str = "ai-wf-key-default-admin-2026"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini, openai, mock
    DEFAULT_LLM_MODEL: str = "gemini-1.5-pro"
    MOCK_LLM_MODE: bool = True
    
    # Integrations
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "automations@example.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@ai-workflow.internal"
    
    # Workflow Execution Settings
    MAX_CONCURRENT_STEPS: int = 5
    DEFAULT_STEP_TIMEOUT_SECONDS: int = 120
    MAX_STEP_RETRIES: int = 3
    RETRY_BACKOFF_BASE_SECONDS: float = 1.5
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
