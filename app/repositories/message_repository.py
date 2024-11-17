from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from app.models.domain.message import Message

class MessageRepository(BaseRepository):
    def init_table(self):
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                text TEXT NOT NULL,
                reply_to_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id),
                FOREIGN KEY (reply_to_id) REFERENCES messages (id)
            )
        ''')

    def create(self, text: str, user_id: str, recipient_id: str, reply_to_id: Optional[int] = None) -> int:
        return self.execute_query(
            'INSERT INTO messages (text, user_id, recipient_id, reply_to_id, timestamp) VALUES (?, ?, ?, ?, ?)',
            (text, user_id, recipient_id, reply_to_id, datetime.now().isoformat())
        )

    def get_conversation(self, user_id: str, other_user_id: str, limit: int = 100) -> List[Message]:
        messages_data = self.execute_query('''
            WITH conversation AS (
                SELECT 
                    m.id,
                    m.text,
                    m.user_id,
                    m.recipient_id,
                    m.reply_to_id,
                    m.timestamp,
                    u.username,
                    u.avatar_url,
                    CASE 
                        WHEN m.user_id = ? THEN 1 
                        ELSE 0 
                    END as is_mine
                FROM messages m 
                JOIN users u ON m.user_id = u.id 
                WHERE (m.user_id = ? AND m.recipient_id = ?) 
                   OR (m.user_id = ? AND m.recipient_id = ?)
                ORDER BY m.timestamp ASC
                LIMIT ?
            )
            SELECT 
                c.*,
                r.text as reply_text,
                ru.username as reply_username,
                r.id as reply_to_id
            FROM conversation c
            LEFT JOIN messages r ON c.reply_to_id = r.id
            LEFT JOIN users ru ON r.user_id = ru.id
            ORDER BY c.timestamp ASC
        ''', (user_id, user_id, other_user_id, other_user_id, user_id, limit), fetch_all=True)
        
        return [Message.from_dict(msg) for msg in messages_data]

    def get_by_id(self, message_id: int) -> Optional[Message]:
        messages = self.execute_query('''
            SELECT 
                m.*,
                u.username,
                u.avatar_url,
                r.text as reply_text,
                ru.username as reply_username
            FROM messages m
            JOIN users u ON m.user_id = u.id
            LEFT JOIN messages r ON m.reply_to_id = r.id
            LEFT JOIN users ru ON r.user_id = ru.id
            WHERE m.id = ?
        ''', (message_id,), fetch_all=True)
        return Message.from_dict(messages[0]) if messages else None

    def delete(self, message_id: int) -> bool:
        return self.execute_query(
            'DELETE FROM messages WHERE id = ?',
            (message_id,)
        ) > 0 