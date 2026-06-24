import sqlite3

DB_NAME = "queuecure.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            name TEXT,
            status TEXT DEFAULT 'waiting'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            current_token INTEGER DEFAULT 0,
            avg_time INTEGER DEFAULT 10
        )
    """)

    cursor.execute("SELECT * FROM settings WHERE id=1")
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO settings (id, current_token, avg_time)
            VALUES (1, 0, 10)
        """)

    conn.commit()
    conn.close()