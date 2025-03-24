"""
Logging configuration for Project Leela.
"""
import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..config import get_config

# Get configuration
config = get_config()
system_config = config["system"]
log_level_str = system_config["log_level"]
log_level = getattr(logging, log_level_str.upper(), logging.INFO)

# Set up log directory
base_dir = Path(config["paths"]["base_dir"])
log_dir = base_dir / "logs"
log_dir.mkdir(exist_ok=True, parents=True)

# Configure logging
class LeelaLogger:
    """
    Configurable logger for Project Leela.
    """
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, file_logging: bool = True) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name
            file_logging: Whether to log to file
            
        Returns:
            logging.Logger: Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if file_logging:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = log_dir / f"{name}_{timestamp}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Store logger
        cls._loggers[name] = logger
        
        return logger
    
    @classmethod
    def set_level(cls, level: str):
        """
        Set the log level for all loggers.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        for logger in cls._loggers.values():
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)

# Create main loggers
main_logger = LeelaLogger.get_logger("leela")
api_logger = LeelaLogger.get_logger("leela.api")
claude_logger = LeelaLogger.get_logger("leela.claude")
engine_logger = LeelaLogger.get_logger("leela.engine")
db_logger = LeelaLogger.get_logger("leela.db")