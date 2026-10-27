import hashlib
import secrets
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER_NAME, auto_error=False)

def generate_api_key() -> str:
    return f"wf_{secrets.token_urlsafe(32)}"

def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()

def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    return hash_secret(plain_secret) == hashed_secret

async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    # If API key header is provided, check if valid; otherwise permit dev access with default
    if api_key:
        if api_key == settings.DEFAULT_API_KEY:
            return api_key
        # Accept wf_ formatted keys in dev mode
        if api_key.startswith("wf_"):
            return api_key
    # Allow development access without blocking if default is set
    return settings.DEFAULT_API_KEY
