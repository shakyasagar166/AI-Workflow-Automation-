import logging
import sys

def setup_logging():
    log_format = "%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logger = logging.getLogger("ai_workflow_system")
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()
