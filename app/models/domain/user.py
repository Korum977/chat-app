from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: str
    email: str
    username: str
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            id=data['id'],
            email=data['email'],
            username=data['username'],
            avatar_url=data.get('avatar_url'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        ) 