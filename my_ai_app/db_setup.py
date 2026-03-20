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

    # Table for User Profile & Gamification Stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            username TEXT DEFAULT 'Neural Explorer',
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            papers_read INTEGER DEFAULT 0,
            repos_explored INTEGER DEFAULT 0,
            debates_won INTEGER DEFAULT 0
        )
    ''')

    # Initialize a default user if none exists
    cursor.execute('SELECT COUNT(*) FROM user_profile')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO user_profile (id, xp, level) VALUES (1, 0, 1)')

    # Table for reading history/completed items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reading_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            source TEXT,
            date_completed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
