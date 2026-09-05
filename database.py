import sqlite3
from datetime import datetime


DATABASE_NAME = "orchestrator.db"


def get_connection():
    """Create and return a connection to the SQLite database."""

    connection = sqlite3.connect(DATABASE_NAME)

    # Enable foreign key support for this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Create the database tables if they do not already exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------
    # REQUESTS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_prompt TEXT NOT NULL,
            created_at TEXT NOT NULL,
            understanding_score INTEGER,
            needs_clarification INTEGER,
            prompt_score INTEGER,
            enhanced_prompt TEXT,
            status TEXT NOT NULL DEFAULT 'created'
        )
    """)

    # ---------------------------------
    # INTERACTIONS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (request_id)
                REFERENCES requests(id)
                ON DELETE CASCADE
        )
    """)

    # ---------------------------------
    # HANDLE EXISTING DATABASES
    # ---------------------------------

    cursor.execute("""
        PRAGMA table_info(requests)
    """)

    columns = cursor.fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "status" not in column_names:

        cursor.execute("""
            ALTER TABLE requests
            ADD COLUMN status TEXT
            DEFAULT 'created'
        """)

    connection.commit()
    connection.close()


def create_request(original_prompt):
    """
    Create a new request immediately.

    Returns:
        The ID of the newly created request.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO requests (
            original_prompt,
            created_at,
            status
        )

        VALUES (?, ?, ?)
    """, (
        original_prompt,
        datetime.now().isoformat(),
        "created"
    ))

    request_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return request_id


def save_interaction(
    request_id,
    interaction_type,
    content
):
    """
    Save an interaction related to a request.

    Examples of interaction types:

    - clarification_question
    - clarification_answer
    - cancellation
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interactions (
            request_id,
            interaction_type,
            content,
            created_at
        )

        VALUES (?, ?, ?, ?)
    """, (
        request_id,
        interaction_type,
        content,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def update_request(
    request_id,
    understanding_score=None,
    needs_clarification=None,
    prompt_score=None,
    enhanced_prompt=None,
    status=None
):
    """
    Update processing information for an existing request.
    """

    connection = get_connection()
    cursor = connection.cursor()

    fields = []
    values = []

    if understanding_score is not None:

        fields.append(
            "understanding_score = ?"
        )

        values.append(
            understanding_score
        )

    if needs_clarification is not None:

        fields.append(
            "needs_clarification = ?"
        )

        values.append(
            int(needs_clarification)
        )

    if prompt_score is not None:

        fields.append(
            "prompt_score = ?"
        )

        values.append(
            prompt_score
        )

    if enhanced_prompt is not None:

        fields.append(
            "enhanced_prompt = ?"
        )

        values.append(
            enhanced_prompt
        )

    if status is not None:

        fields.append(
            "status = ?"
        )

        values.append(
            status
        )

    # If nothing needs updating,
    # stop the function.

    if not fields:

        connection.close()

        return

    values.append(request_id)

    query = f"""
        UPDATE requests
        SET {", ".join(fields)}
        WHERE id = ?
    """

    cursor.execute(
        query,
        values
    )

    connection.commit()
    connection.close()


def get_request_interactions(request_id):
    """
    Return all interactions related
    to a specific request.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            request_id,
            interaction_type,
            content,
            created_at

        FROM interactions

        WHERE request_id = ?

        ORDER BY id
    """, (
        request_id,
    ))

    interactions = cursor.fetchall()

    connection.close()

    return interactions
