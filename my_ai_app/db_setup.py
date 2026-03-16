import sqlite3
import os

DB_PATH = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for saved papers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            summary TEXT,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for saved repositories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT,
            description TEXT,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for general tracking (e.g. HN posts or articles)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            type TEXT,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
