#!/usr/bin/env python3
"""Configure logging for all services"""

import logging
import logging.config
from pathlib import Path

import yaml

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name: str, level=logging.INFO):
    """
    Create logger for a service

    Args:
        name: Name of the service (e.g., 'backend', 'rag', 'latex')
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler
    log_file = LOG_DIR / f"{name}.log"
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)

    # Console handler (only warnings and above)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh.setFormatter(detailed_formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def load_config_logging():
    """
    Load logging configuration from config/app.yaml

    Returns:
        Configured logger based on app.yaml settings
    """
    config_file = Path("config/app.yaml")

    if not config_file.exists():
        print(f"Warning: {config_file} not found, using default logging")
        return setup_logger("app")

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        logging_config = config.get("logging")
        if logging_config:
            # Ensure log directory exists
            LOG_DIR.mkdir(exist_ok=True)

            # Apply logging configuration
            logging.config.dictConfig(logging_config)
            return logging.getLogger()
        else:
            return setup_logger("app")

    except Exception as e:
        print(f"Warning: Could not load logging config: {e}")
        return setup_logger("app")


def get_logger(name: str = None):
    """
    Get a logger instance

    Args:
        name: Optional logger name. If None, returns root logger

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


# Example usage
if __name__ == "__main__":
    # Test basic setup
    logger = setup_logger("test", logging.DEBUG)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    print(f"\nLog file created at: {LOG_DIR / 'test.log'}")
    print("\nTo use in your code:")
    print("  from ops.scripts.setup_logging import setup_logger")
    print("  logger = setup_logger('your_service_name')")
    print("  logger.info('Your message here')")
