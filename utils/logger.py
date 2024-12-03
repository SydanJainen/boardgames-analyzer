# utils/logger.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union, List

class ProjectLogger:
    def __init__(
        self, 
        name: str = 'BoardGameAnalyzer', 
        log_dir: Union[str, Path] = 'logs',
        log_level: int = logging.INFO,
        max_log_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        # Ensure log directory exists
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Clear any existing handlers to prevent duplicate logs
        self.logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        self.logger.addHandler(console_handler)

        # File Handler with rotation
        log_file_path = self.log_dir / f'{name.lower().replace(" ", "_")}.log'
        file_handler = RotatingFileHandler(
            log_file_path, 
            maxBytes=max_log_size, 
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        self.logger.addHandler(file_handler)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a child logger with optional name
        
        Args:
            name (Optional[str]): Name of the child logger
        
        Returns:
            logging.Logger: Configured logger
        """
        return logging.getLogger(name) if name else self.logger

    @classmethod
    def create_logger(
        cls, 
        name: str = 'BoardGameAnalyzer', 
        log_dir: Union[str, Path] = 'logs',
        log_level: int = logging.INFO
    ) -> logging.Logger:
        """
        Class method to create and return a logger directly
        
        Args:
            name (str): Name of the logger
            log_dir (Union[str, Path]): Directory for log files
            log_level (int): Logging level
        
        Returns:
            logging.Logger: Configured logger
        """
        return cls(name, log_dir, log_level).logger

def log_method(logger: Optional[logging.Logger] = None, level: int = logging.INFO):
    """
    Decorator to log method calls, arguments, and execution time
    
    Args:
        logger (Optional[logging.Logger]): Logger to use
        level (int): Logging level
    
    Returns:
        Callable: Decorated method
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided logger or get a default one
            method_logger = logger or logging.getLogger(func.__module__)
            
            # Log method entry
            method_logger.log(
                level, 
                f"Calling {func.__name__} "
                f"with args: {args}, kwargs: {kwargs}"
            )
            
            # Track execution time
            start_time = time.time()
            try:
                # Execute the actual method
                result = func(*args, **kwargs)
                
                # Log successful execution
                method_logger.log(
                    level,
                    f"{func.__name__} completed in "
                    f"{time.time() - start_time:.4f} seconds"
                )
                return result
            
            except Exception as e:
                # Log any exceptions
                method_logger.exception(
                    f"Exception in {func.__name__}: {str(e)}"
                )
                raise
        return wrapper
    return decorator

# Example Usage
def example_usage():
    # Create a project-wide logger
    project_logger = ProjectLogger(
        name='BoardGameAnalyzer', 
        log_dir='logs', 
        log_level=logging.DEBUG
    )

    # Get a logger for a specific module
    logger = project_logger.get_logger('DataCollection')

    # Use the decorator
    @log_method(logger)
    def example_method(x, y):
        """
        An example method to demonstrate logging
        """
        return x + y

    # Demonstrate logging
    logger.info("Starting data collection")
    try:
        result = example_method(5, 3)
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    example_usage()