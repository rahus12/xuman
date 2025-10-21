"""
Structured Logging Configuration for Service Marketplace API
Provides centralized logging setup with proper levels and formatting
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import structlog
from typing import Any, Dict

# Environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def setup_logging() -> None:
    """Setup structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error log file for errors and above
    error_log_file = str(log_path.parent / "error.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Access log for API requests
    access_log_file = str(log_path.parent / "access.log")
    access_handler = logging.handlers.RotatingFileHandler(
        access_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    access_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        '%(asctime)s - %(message)s'
    )
    access_handler.setFormatter(access_formatter)
    
    # Create access logger
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False
    
    # Database log for database operations
    db_log_file = str(log_path.parent / "database.log")
    db_handler = logging.handlers.RotatingFileHandler(
        db_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(file_formatter)
    
    # Create database logger
    db_logger = logging.getLogger("database")
    db_logger.setLevel(logging.INFO)
    db_logger.addHandler(db_handler)
    db_logger.propagate = False
    
    # Security log for authentication and authorization
    security_log_file = str(log_path.parent / "security.log")
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(file_formatter)
    
    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)
    security_logger.propagate = False

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

def log_api_request(method: str, path: str, status_code: int, user_id: str = None, **kwargs) -> None:
    """Log API request with structured data"""
    logger = get_logger("access")
    logger.info(
        "API Request",
        method=method,
        path=path,
        status_code=status_code,
        user_id=user_id,
        **kwargs
    )

def log_database_operation(operation: str, table: str, record_id: str = None, **kwargs) -> None:
    """Log database operation with structured data"""
    logger = get_logger("database")
    logger.info(
        "Database Operation",
        operation=operation,
        table=table,
        record_id=record_id,
        **kwargs
    )

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, **kwargs) -> None:
    """Log security event with structured data"""
    logger = get_logger("security")
    logger.info(
        "Security Event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        **kwargs
    )

def log_business_event(event_type: str, entity_type: str, entity_id: str = None, **kwargs) -> None:
    """Log business event with structured data"""
    logger = get_logger("business")
    logger.info(
        "Business Event",
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        **kwargs
    )

# Initialize logging when module is imported
setup_logging()
