import os
from dataclasses import dataclass, field
from typing import Set

@dataclass
class Config:
    DB_NAME: str = field(default='chat.db')
    UPLOAD_FOLDER: str = field(default='static/uploads')
    ALLOWED_EXTENSIONS: Set[str] = field(
        default_factory=lambda: {'png', 'jpg', 'jpeg', 'gif'}
    )

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def get_upload_path(cls) -> str:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(root_dir, cls.get_instance().UPLOAD_FOLDER)