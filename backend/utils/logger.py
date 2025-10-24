"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from loguru import logger as loguru_logger

from .config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure loguru
    loguru_logger.remove()  # Remove default handler
    
    # Console handler
    loguru_logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )
    
    # File handler
    loguru_logger.add(
        settings.LOG_FILE,
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.LOG_LEVEL
    )
    
    # Create a standard logger that uses loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = loguru_logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            loguru_logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Setup intercept handler for standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    return logging.getLogger(name)
