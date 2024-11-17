from typing import Optional, List
import hashlib
import uuid
from datetime import datetime
from .base_repository import BaseRepository
from app.models.domain.user import User

class UserRepository(BaseRepository):
    def init_table(self):
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                username TEXT NOT NULL,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create(self, email: str, password: str, username: str) -> Optional[str]:
        try:
            user_id = str(uuid.uuid4())
            hashed_password = self.hash_password(password)
            
            self.execute_query(
                'INSERT INTO users (id, email, password, username) VALUES (?, ?, ?, ?)',
                (user_id, email, hashed_password, username)
            )
            
            return user_id
        except Exception:
            return None

    def verify(self, email: str, password: str) -> Optional[User]:
        hashed_password = self.hash_password(password)
        
        users = self.execute_query(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hashed_password),
            fetch_all=True
        )
        
        return User.from_dict(users[0]) if users else None

    def get_all(self) -> List[User]:
        users_data = self.execute_query(
            'SELECT id, email, username, avatar_url, created_at FROM users ORDER BY username',
            fetch_all=True
        )
        return [User.from_dict(user) for user in users_data]

    def update_avatar(self, user_id: str, avatar_url: Optional[str]) -> None:
        self.execute_query(
            'UPDATE users SET avatar_url = ? WHERE id = ?',
            (avatar_url, user_id)
        ) 