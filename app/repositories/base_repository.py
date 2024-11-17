from typing import Optional, List, Any
import sqlite3
import time

class BaseRepository:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_connection(self, max_attempts=5):
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
                time.sleep(0.1)

    def execute_query(self, query: str, params: tuple = (), fetch_all: bool = False) -> Any:
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