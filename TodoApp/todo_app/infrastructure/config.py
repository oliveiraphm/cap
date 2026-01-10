from enum import Enum
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"

class Config:

    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"

    @classmethod
    def get_repository_type(cls) -> RepositoryType:

        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid repository type: {repo_type_str}")
        
    @classmethod
    def get_data_directory(cls) -> Path:

        data_dir = os.getenv("TODO_DATA_DIR", cls.DEFAULT_DATA_DIR)
        path = Path(data_dir)
        path.mkdor(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def get_sendgrid_api_key(cls) -> str:

        return os.getenv("TODO_SENDGRID_API_KEY", "")
    
    @classmethod
    def get_notification_email(cls) -> str:

        return os.getenv("TODO_NOTIFICATION_EMAIL", "")