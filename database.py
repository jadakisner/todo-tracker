import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT,
            creation_time TEXT NOT NULL,
            due_date TEXT,
            is_completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)
