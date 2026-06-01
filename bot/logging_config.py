"""
Centralized logging configuration for the Binance Futures Testnet trading bot.
Provides rotating file logs and consistent formatting across all modules.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file_name: str = "trading.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Sets up a centralized logging system with rotating file and console handlers.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file_name: The name of the log file inside the logs/ directory.
        max_bytes: Maximum size of a single log file before rotation.
        backup_count: Number of historical log files to retain.
    """
    # Ensure the logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file_name

    # Define a consistent format for all log entries
    # Includes: Timestamp, Log Level, Module Name, and the Message
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 1. Rotating File Handler
    # Automatically manages log file size and history
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 2. Console (Stdout) Handler
    # For real-time monitoring during development/deployment
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Configure the root logger
    root_logger = logging.getLogger()
    
    # Remove any existing handlers to avoid duplicate logs if setup is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Default level for the application
    app_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(app_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Production Refinement: Suppress noisy third-party libraries
    # This ensures logs stay concise even if the application is in DEBUG mode
    suppressed_loggers = ["urllib3", "asyncio", "binance", "requests"]
    for logger_name in suppressed_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Ensure our application modules respect the log level
    logging.getLogger("bot").setLevel(app_level)
    logging.getLogger("__main__").setLevel(app_level)

    # Log initialization at INFO level regardless of DEBUG status
    logging.getLogger(__name__).info(
        "Logging initialized | Level: %s | File: %s", 
        log_level.upper(), 
        log_path
    )


def get_logger(name: str) -> logging.Logger:
    """
    Helper function to get a named logger instance.
    
    Args:
        name: The name of the module or component (usually __name__).
        
    Returns:
        A configured logging.Logger instance.
    """
    return logging.getLogger(name)
