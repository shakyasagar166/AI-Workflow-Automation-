import asyncio
import random
from typing import Callable, Any, Dict, Optional
from app.core.config import settings
from app.core.logging_config import logger

class RetryHandler:
    """Manages resilient execution with exponential backoff and policy-based retries."""

    def __init__(
        self,
        max_retries: int = settings.MAX_STEP_RETRIES,
        base_backoff_seconds: float = settings.RETRY_BACKOFF_BASE_SECONDS
    ):
        self.max_retries = max_retries
        self.base_backoff = base_backoff_seconds

    def should_retry(self, attempt: int, error: Optional[Exception] = None, output: Optional[Dict[str, Any]] = None) -> bool:
        """Determines whether a failed or rejected step should be retried."""
        if attempt >= self.max_retries:
            return False

        # If agent output explicitly requested retry
        if isinstance(output, dict) and output.get("requires_retry") is True:
            return True

        if error:
            # Fatal validation errors shouldn't be retried indefinitely
            err_msg = str(error).lower()
            if "cycle detected" in err_msg or "schema invalid" in err_msg:
                return False
            return True

        return False

    async def sleep_backoff(self, attempt: int) -> float:
        """Calculates exponential delay with jitter and sleeps asynchronously."""
        # backoff = base * (2 ^ attempt) + random jitter (0 to 0.5s)
        delay = (self.base_backoff * (2 ** attempt)) + (random.uniform(0.1, 0.5))
        # Cap max sleep at 15 seconds for responsive execution
        delay = min(delay, 15.0)
        logger.info(f"Retrying step after backoff delay: {delay:.2f}s (attempt {attempt + 1})")
        await asyncio.sleep(delay)
        return delay
