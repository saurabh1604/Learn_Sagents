import sqlite3
from db_setup import DB_PATH

def add_xp(amount, source="system"):
    """Adds XP to the user profile and levels up if needed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT xp, level, papers_read, repos_explored FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    xp, level, papers, repos = row

    new_xp = xp + amount
    # Level up logic: every 100 XP is a new level
    new_level = max(1, (new_xp // 100) + 1)

    # Increment counters based on source
    papers_increment = 1 if source == "paper" else 0
    repos_increment = 1 if source == "repo" else 0

    cursor.execute("""
        UPDATE user_profile
        SET xp = ?, level = ?, papers_read = papers_read + ?, repos_explored = repos_explored + ?
        WHERE id = 1
    """, (new_xp, new_level, papers_increment, repos_increment))

    conn.commit()
    conn.close()

    return {"level_up": new_level > level, "new_level": new_level, "xp_gained": amount}

def get_user_stats():
    """Returns the current user profile stats."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT xp, level, papers_read, repos_explored, debates_won FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "xp": row[0],
            "level": row[1],
            "papers_read": row[2],
            "repos_explored": row[3],
            "debates_won": row[4]
        }
    return None

def mark_as_read(title, url, source):
    """Records an item as read to prevent duplicate XP farming."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if already read
    cursor.execute("SELECT id FROM reading_history WHERE url = ?", (url,))
    if cursor.fetchone():
        conn.close()
        return False # Already read

    cursor.execute("INSERT INTO reading_history (title, url, source) VALUES (?, ?, ?)", (title, url, source))
    conn.commit()
    conn.close()

    # Grant XP based on source
    xp_amount = 50 if source.lower() == "arxiv" else 30
    source_type = "paper" if source.lower() == "arxiv" else "repo"

    return add_xp(xp_amount, source=source_type)
