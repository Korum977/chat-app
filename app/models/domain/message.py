from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .reply import ReplyInfo

@dataclass
class Message:
    id: int
    text: str
    user_id: str
    recipient_id: str
    username: str
    timestamp: datetime
    avatar_url: Optional[str] = None
    reply_to: Optional[ReplyInfo] = None
    is_mine: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        reply_to = None
        if data.get('reply_to_id'):
            reply_to = ReplyInfo(
                id=data['reply_to_id'],
                text=data['reply_text'],
                username=data['reply_username']
            )
            
        return cls(
            id=data['id'],
            text=data['text'],
            user_id=data['user_id'],
            recipient_id=data['recipient_id'],
            username=data['username'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            avatar_url=data.get('avatar_url'),
            reply_to=reply_to,
            is_mine=bool(data.get('is_mine', False))
        ) 