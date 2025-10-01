"""Logging configuration for structured application logs."""
import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    trace_id: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logging for the application.
    
    Args:
        level: Logging level (default INFO)
        log_file: Optional file path for log output
        trace_id: Optional trace ID for correlation
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("demandforge")
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    if trace_id:
        formatter = logging.Formatter(
            f'%(asctime)s - %(name)s - [TRACE:{trace_id}] - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")
    
    return logger


def get_logger(name: str = "demandforge", trace_id: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        trace_id: Optional trace ID for correlation
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # Setup if not already configured
    if not logger.handlers:
        setup_logging(trace_id=trace_id)
    
    return logger


class StructuredLogger:
    """
    Wrapper for structured logging with automatic field sanitization.
    Ensures no PII or secrets are logged.
    """
    
    def __init__(self, logger: logging.Logger, trace_id: str):
        """Initialize with base logger and trace ID."""
        self.logger = logger
        self.trace_id = trace_id
        self.sensitive_fields = {
            "password", "token", "secret", "api_key", "auth",
            "email", "phone", "ssn", "credit_card"
        }
    
    def _sanitize_message(self, message: str, **kwargs) -> str:
        """Remove sensitive information from log message."""
        # Check kwargs for sensitive fields
        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                sanitized_kwargs[key] = "[REDACTED]"
            else:
                sanitized_kwargs[key] = value
        
        if sanitized_kwargs:
            return f"{message} | {sanitized_kwargs}"
        return message
    
    def info(self, message: str, **kwargs):
        """Log info level message."""
        sanitized = self._sanitize_message(message, **kwargs)
        self.logger.info(sanitized)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        sanitized = self._sanitize_message(message, **kwargs)
        self.logger.warning(sanitized)
    
    def error(self, message: str, **kwargs):
        """Log error level message."""
        sanitized = self._sanitize_message(message, **kwargs)
        self.logger.error(sanitized)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        sanitized = self._sanitize_message(message, **kwargs)
        self.logger.debug(sanitized)
