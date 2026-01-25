from logging.config import dictConfig
from pathlib import Path
import json
import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from todo_app.infrastructure.logging.trace import get_trace_id

class JsonLogEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Exception):
            return str(o)
        
        return super().default(o)
    
class JsonFormatter(logging.Formatter):
    def __init__(self, app_context: str):
        super().__init__()
        self.app_context = app_context
        self.encoder = JsonLogEncoder()

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_context": self.app_context,
            "trace_id": get_trace_id(),
        }
        context = {}
        for key, value in record.__dict__.items():
            if key == "context":
                context = value
                break

        if context:
            log_data["context"] = context

        return self.encoder.encode(log_data)
    
def configure_logging(app_context: Literal["CLI", "WEB"]) -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    config = {
        "version": 1,
        "formatters": {
            "json": {"()": JsonFormatter, "app_context": app_context},
            "standard": {
                "format": "%(asctime)s [%(trace_id)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {

            "standard_console": {"class": "logging.StreamHandler", "formatter": "standard"},

            "json_console": {"class": "logging.StreamHandler", "formatter": "json"},

            "app_file": {
                "class": "logging.FileHandler",
                "filename": log_dir / "app.log",
                "formatter": "json",
            },
            "access_file": {
                "class": "logging.FileHandler",
                "filename": log_dir / "access.log",
                "formatter": "standard",
            },
        },
        "loggers": {

            "todo_app": {
                "handlers": ["app_file"] if app_context == "CLI" else ["json_console", "app_file"],
                "level": "INFO",
            },

            "werkzeug": {
                "handlers": ["standard_console", "access_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    dictConfig(config)