"""
Logging configuration for the backend application.
"""
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging():
    """
    Configures the logging for the application.
    - Logs to both console and a rotating file (`backend.log`).
    - Uses a consistent format for log messages.
    """
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = RotatingFileHandler(
        "backend.log", maxBytes=10*1024*1024, backupCount=5  # 10 MB per file, 5 backups
    )
    file_handler.setFormatter(log_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info("Logging configured successfully.")

