from dataclasses import dataclass
from typing import Optional

@dataclass
class ReplyInfo:
    id: int
    text: str
    username: str
    
    @classmethod
    def from_dict(cls, data: dict) -> Optional['ReplyInfo']:
        if not data.get('reply_to_id'):
            return None
        return cls(
            id=data['reply_to_id'],
            text=data['reply_text'],
            username=data['reply_username']
        ) 