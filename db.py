import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import uuid
import time

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_db()

    def get_connection(self, max_attempts=5):
        """Создает соединение с базой данных с повторными попытками"""
        attempt = 0
        while attempt < max_attempts:
            try:
                conn = sqlite3.connect(self.db_name, timeout=20)
                conn.row_factory = sqlite3.Row
                return conn
            except sqlite3.OperationalError as e:
                attempt += 1
                if attempt == max_attempts:
                    raise e
                time.sleep(0.1)  # Ждем 100ms перед следующей попыткой

    def execute_query(self, query, params=(), fetch_all=False):
        """Выполняет запрос с обработкой ошибок и автоматическим закрытием соединения"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
            else:
                result = cursor.lastrowid
                conn.commit()
            
            return result
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def init_db(self):
        """Инициализирует базу данных"""
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (recipient_id) REFERENCES users (id)
            )
        ''')

    def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, password: str, username: str) -> Optional[str]:
        """Создает нового пользователя"""
        try:
            user_id = str(uuid.uuid4())
            hashed_password = self.hash_password(password)
            
            self.execute_query(
                'INSERT INTO users (id, email, password, username) VALUES (?, ?, ?, ?)',
                (user_id, email, hashed_password, username)
            )
            
            return user_id
        except sqlite3.IntegrityError:
            return None

    def verify_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Проверяет учетные данные пользователя"""
        hashed_password = self.hash_password(password)
        
        users = self.execute_query(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hashed_password),
            fetch_all=True
        )
        
        return dict(users[0]) if users else None

    def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает последние сообщения с информацией о пользователях"""
        return self.execute_query('''
            SELECT m.*, u.username 
            FROM messages m 
            JOIN users u ON m.user_id = u.id 
            ORDER BY m.timestamp DESC 
            LIMIT ?
        ''', (limit,), fetch_all=True)

    def add_message(self, text: str, user_id: str, recipient_id: str) -> int:
        """Добавляет новое сообщение"""
        return self.execute_query(
            'INSERT INTO messages (text, user_id, recipient_id, timestamp) VALUES (?, ?, ?, ?)',
            (text, user_id, recipient_id, datetime.now().isoformat())
        )

    def clear_messages(self):
        """Очищает все сообщения"""
        self.execute_query('DELETE FROM messages')

    def get_message_by_id(self, message_id: int) -> Dict[str, Any]:
        """Получает сообщение по ID"""
        return self.execute_query(
            'SELECT * FROM messages WHERE id = ?',
            (message_id,),
            fetch_all=True
        )[0] if self.execute_query(
            'SELECT * FROM messages WHERE id = ?',
            (message_id,),
            fetch_all=True
        ) else None

    def delete_message(self, message_id: int) -> bool:
        """Удаляет сообщение по ID"""
        return self.execute_query(
            'DELETE FROM messages WHERE id = ?',
            (message_id,)
        ) > 0

    def get_users(self) -> List[Dict[str, Any]]:
        """Получает список всех пользователей"""
        return self.execute_query(
            'SELECT id, email, username, created_at FROM users ORDER BY username',
            fetch_all=True
        )

    def get_messages_with_user(self, user_id: str, other_user_id: str) -> List[Dict[str, Any]]:
        """Получает сообщения между двумя пользователями"""
        return self.execute_query('''
            SELECT 
                m.*,
                u.username,
                CASE 
                    WHEN m.user_id = ? THEN 1 
                    ELSE 0 
                END as is_mine
            FROM messages m 
            JOIN users u ON m.user_id = u.id 
            WHERE (m.user_id = ? AND m.recipient_id = ?) 
               OR (m.user_id = ? AND m.recipient_id = ?)
            ORDER BY m.timestamp ASC
            LIMIT 100
        ''', (user_id, user_id, other_user_id, other_user_id, user_id), fetch_all=True)