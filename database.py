import sqlite3
from datetime import datetime


DATABASE_NAME = "orchestrator.db"


def get_connection():
    """Create and return a connection to the SQLite database."""

    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    """Create the requests table if it does not already exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_prompt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            understanding_score INTEGER,
            needs_clarification INTEGER,
            prompt_score INTEGER,
            enhanced_prompt TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_request(
    original_prompt,
    understanding_score,
    needs_clarification,
    prompt_score=None,
    enhanced_prompt=None
):
    """Save a user request and its processing results."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO requests (
            original_prompt,
            created_at,
            understanding_score,
            needs_clarification,
            prompt_score,
            enhanced_prompt
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        original_prompt,
        datetime.now().isoformat(),
        understanding_score,
        int(needs_clarification),
        prompt_score,
        enhanced_prompt
    ))

    connection.commit()
    connection.close()
