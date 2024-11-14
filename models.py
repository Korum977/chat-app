import sqlite3

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            username TEXT DEFAULT 'Аноним',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close() 