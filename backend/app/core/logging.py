import sys
from loguru import logger
from app.core.config import settings, DATA_DIR

def configure_logging():
    """
    Configures the loguru logger for the application.
    Removes the default handler, sets up console and rotating file handlers,
    and dynamically reads the log level from settings.
    
    This function is idempotent; it clears existing handlers before adding new ones.
    """
    # Remove all existing handlers (idempotent setup)
    logger.remove()
    
    # Define common format
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}"
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.log_level,
    )
    
    # Add file handler
    log_file = DATA_DIR / "logs" / "app.log"
    logger.add(
        str(log_file),
        format=log_format,
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

__all__ = ["logger", "configure_logging"]
