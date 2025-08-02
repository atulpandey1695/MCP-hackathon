import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'chatbot_context.db')

class ChatContextDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context_json TEXT
        )''')
        self.conn.commit()

    def load_context(self):
        c = self.conn.cursor()
        c.execute('SELECT context_json FROM chat_context ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        if row:
            try:
                return json.loads(row[0])
            except Exception:
                return []
        return []

    def save_context(self, context):
        c = self.conn.cursor()
        c.execute('INSERT INTO chat_context (context_json) VALUES (?)', (json.dumps(context),))
        self.conn.commit()
