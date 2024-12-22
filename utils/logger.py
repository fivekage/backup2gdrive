import logging
from logging import Logger
import os
from logging.handlers import RotatingFileHandler

# Singleton instance for the logger
_logger_instance: Logger | None = None


def setup_logger(
    name: str = "app_logger",
    log_file: str = "logs/app.log",
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> Logger:
    """
    Sets up and returns a singleton logger instance.

    Args:
        name (str): Name of the logger.
        log_file (str): File path for the log file.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        max_bytes (int): Maximum file size in bytes before rotation.
        backup_count (int): Number of backup files to keep after rotation.

    Returns:
        logging.Logger: Configured logger instance.
    """
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance  # Return existing logger if already created

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create and configure the logger
    logger: Logger = logging.getLogger(name)
    logger.setLevel(level)

    # Formatter for log messages
    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler: RotatingFileHandler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Avoid adding handlers multiple times
    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    _logger_instance = logger  # Cache the logger instance
    return logger


def get_logger(name: str = "app_logger") -> Logger:
    """
    Returns the configured logger instance.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
