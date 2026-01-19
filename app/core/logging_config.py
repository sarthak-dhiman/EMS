import logging
import json
import os
from logging.handlers import RotatingFileHandler

# 1. Define the JSON Formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
            "path": getattr(record, "path", "N/A"),
            "method": getattr(record, "method", "N/A"),
        }
        # If there's an exception, add the stack trace
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# 2. Setup Function
def setup_logging():
    # Create a 'logs' directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Define the Logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    # --- Handler 1: Log Rotation (File) ---
    # Rotates when file reaches 5MB. Keeps last 3 backup files.
    file_handler = RotatingFileHandler(
        "logs/app.log", 
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3
    )
    file_handler.setFormatter(JsonFormatter())
    
    # --- Handler 2: Console (Stdout) ---
    # Useful for Docker/Kubernetes logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())

    # Also provide a simple console handler for uvicorn access logs
    # so HTTP status codes and request lines appear in the terminal.
    uvicorn_console = logging.StreamHandler()
    uvicorn_console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    uvicorn_console.setFormatter(uvicorn_console_formatter)

    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Attach uvicorn access logger to a simple console formatter (keeps access log format readable)
    uv_logger = logging.getLogger("uvicorn.access")
    uv_logger.setLevel(logging.INFO)
    if not uv_logger.handlers:
        uv_logger.addHandler(uvicorn_console)

    return logger

# Create a singleton instance
logger = setup_logging()